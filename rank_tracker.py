#!/usr/bin/env python3
"""Amazon Keyword Rank Tracker — track where your ASINs rank for target keywords.

Uses the Pangolinfo MCP endpoint (https://mcp.pangolinfo.com/mcp) — the same
Model Context Protocol server that AI assistants use — to fetch real Amazon
search result pages, locates your ASIN in the ranked results, and stores
daily positions in SQLite so you can see ranking trends over time.

Zero dependencies: Python 3.10+ standard library only.

Commands:
    init      Create targets.json from the example file
    run       Check rankings for all targets and store results
    history   Print ranking history (optionally filtered)
    report    Generate Markdown reports into reports/

Get a free API key (200 free calls) at https://tool.pangolinfo.com
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS_FILE = ROOT / "targets.json"
EXAMPLE_FILE = ROOT / "targets.example.json"
DB_FILE = ROOT / "data" / "ranks.db"
CSV_FILE = ROOT / "data" / "ranks.csv"
REPORTS_DIR = ROOT / "reports"

MCP_URL = os.environ.get("PANGOLIN_MCP_URL", "https://mcp.pangolinfo.com/mcp")
MCP_PROTOCOL_VERSION = "2024-11-05"

# The MCP endpoint sits behind Cloudflare, which blocks default library
# signatures (python-urllib gets Error 1010). Present a browser UA.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checked_at TEXT NOT NULL,
  asin TEXT NOT NULL,
  keyword TEXT NOT NULL,
  domain TEXT NOT NULL,
  zipcode TEXT,
  position INTEGER,
  organic_position INTEGER,
  page INTEGER,
  sponsored INTEGER DEFAULT 0,
  title TEXT,
  price TEXT,
  rating TEXT,
  pages_scanned INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_checks_asin_kw ON checks(asin, keyword, checked_at);
"""


# --------------------------------------------------------------------------- #
# Minimal MCP (streamable-HTTP) client — stdlib only
# --------------------------------------------------------------------------- #

class McpError(RuntimeError):
    pass


class McpClient:
    """Talks JSON-RPC to the Pangolinfo MCP server over streamable-HTTP."""

    def __init__(self, token: str, url: str = MCP_URL, timeout: int = 90) -> None:
        self.token = token
        self.url = url
        self.timeout = timeout
        self.session_id: str | None = None
        self._next_id = 0
        self._initialized = False

    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Authorization", f"Bearer {self.token}")
        if self.session_id:
            req.add_header("mcp-session-id", self.session_id)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                sid = resp.headers.get("mcp-session-id")
                if sid:
                    self.session_id = sid
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            raise McpError(f"HTTP {exc.code} from MCP server: {exc.read()[:200]!r}") from exc
        except urllib.error.URLError as exc:
            raise McpError(f"MCP server unreachable: {exc}") from exc
        # Responses are SSE frames ("data: {...}") or occasionally plain JSON.
        # Notifications (no id) legitimately get an empty body.
        if not raw.strip():
            return {}
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        return json.loads(raw)

    def initialize(self) -> None:
        self._next_id += 1
        self._post({
            "jsonrpc": "2.0", "id": self._next_id, "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "amazon-keyword-rank-tracker", "version": "1.0.0"},
            },
        })
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        self._initialized = True

    def call_tool(self, name: str, arguments: dict) -> dict:
        if not self._initialized:
            self.initialize()
        self._next_id += 1
        resp = self._post({
            "jsonrpc": "2.0", "id": self._next_id, "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        if "error" in resp:
            raise McpError(f"JSON-RPC error: {resp['error']}")
        result = resp.get("result", {})
        texts = [c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"]
        if result.get("isError"):
            raise McpError("tool error: " + (" ".join(texts)[:300] or "unknown"))
        for text in texts:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                continue
        return {}


def search_amazon_page(client: McpClient, keyword: str, page: int) -> tuple[list[dict], dict]:
    """Call search_amazon for one SERP page; return (items, container)."""
    payload = client.call_tool("search_amazon", {"keyword": keyword, "page": page})
    container = _find_results_container(payload)
    if not container:
        return [], {}
    return container["results"], container


def _find_results_container(node, depth: int = 0) -> dict | None:
    """Recursively locate the dict holding the ASIN `results` list."""
    if depth > 6:
        return None
    if isinstance(node, dict):
        results = node.get("results")
        if isinstance(results, list) and results and isinstance(results[0], dict) and "asin" in results[0]:
            return node
        for value in node.values():
            found = _find_results_container(value, depth + 1)
            if found:
                return found
    if isinstance(node, list):
        for value in node:
            found = _find_results_container(value, depth + 1)
            if found:
                return found
    return None


# --------------------------------------------------------------------------- #
# Ranking helpers
# --------------------------------------------------------------------------- #

def item_rank(item: dict, fallback: int) -> int:
    try:
        return int(item.get("rank"))
    except (TypeError, ValueError):
        return fallback


def item_sponsored(item: dict) -> bool:
    for key in ("sponsored", "is_sponsored", "isSponsored", "ad", "is_ad"):
        if item.get(key) in (True, 1, "1", "true", "True"):
            return True
    badge = str(item.get("badge", "") or item.get("label", "")).lower()
    return "sponsored" in badge


def item_text(item: dict, *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def locate_asin(items: list[dict], target_asin: str) -> dict | None:
    """Find target ASIN in one page of items; return rank details."""
    organic_counter = 0
    for index, item in enumerate(items, start=1):
        sponsored = item_sponsored(item)
        if not sponsored:
            organic_counter += 1
        if str(item.get("asin", "")).upper() == target_asin.upper():
            return {
                "position": item_rank(item, index),
                "organic_position": None if sponsored else organic_counter,
                "sponsored": 1 if sponsored else 0,
                "title": item_text(item, "title", "name"),
                "price": item_text(item, "price", "price_text", "display_price"),
                "rating": item_text(item, "rating", "star", "stars", "score"),
            }
    return None


# --------------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------------- #

def db_connect() -> sqlite3.Connection:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.executescript(SCHEMA)
    return conn


def save_check(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """INSERT INTO checks
           (checked_at, asin, keyword, domain, zipcode, position, organic_position,
            page, sponsored, title, price, rating, pages_scanned)
           VALUES (:checked_at, :asin, :keyword, :domain, :zipcode, :position,
                   :organic_position, :page, :sponsored, :title, :price, :rating, :pages_scanned)""",
        row,
    )
    conn.commit()


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_init() -> None:
    if TARGETS_FILE.exists():
        sys.exit("targets.json already exists — edit it directly.")
    TARGETS_FILE.write_text(EXAMPLE_FILE.read_text(), encoding="utf-8")
    print(f"Created {TARGETS_FILE.name} — replace the example ASIN/keywords with yours.")


def cmd_run(args) -> None:
    if not TARGETS_FILE.exists():
        sys.exit("targets.json not found. Run: python rank_tracker.py init")
    targets = json.loads(TARGETS_FILE.read_text(encoding="utf-8"))
    token = os.environ.get("PANGOLIN_TOKEN") or os.environ.get("PANGOLINFO_API_KEY")
    if not token:
        sys.exit("Set PANGOLIN_TOKEN env var (free key: https://tool.pangolinfo.com)")

    conn = db_connect()
    client = McpClient(token=token)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    total, found = 0, 0

    for target in targets:
        asin = target["asin"].strip().upper()
        domain = target.get("domain", "www.amazon.com")
        zipcode = target.get("zipcode")
        pages = int(target.get("pages", 1))
        for keyword in target["keywords"]:
            total += 1
            hit = None
            hit_page = None
            scanned = 0
            for page in range(1, pages + 1):
                try:
                    items, _container = search_amazon_page(client, keyword, page)
                except McpError as exc:
                    # one retry for transient backend errors, then move on
                    time.sleep(5)
                    try:
                        items, _container = search_amazon_page(client, keyword, page)
                    except McpError as exc2:
                        print(f"  ! {asin} / '{keyword}' page {page}: {exc2}")
                        break
                scanned = page
                if items:
                    hit = locate_asin(items, asin)
                    if hit:
                        hit_page = page
                        break
                if page < pages:
                    time.sleep(args.delay)

            row = {
                "checked_at": now,
                "asin": asin,
                "keyword": keyword,
                "domain": domain,
                "zipcode": zipcode,
                "position": hit["position"] if hit else None,
                "organic_position": hit["organic_position"] if hit else None,
                "page": hit_page,
                "sponsored": hit["sponsored"] if hit else 0,
                "title": hit["title"] if hit else None,
                "price": hit["price"] if hit else None,
                "rating": hit["rating"] if hit else None,
                "pages_scanned": scanned,
            }
            save_check(conn, row)
            if hit:
                found += 1
                print(f"  ✓ {asin} @ '{keyword}': position {hit['position']} (page {hit_page})")
            else:
                print(f"  · {asin} @ '{keyword}': not in first {scanned} page(s)")
            time.sleep(args.delay)

    print(f"\nDone: {found}/{total} keywords ranked. Stored in {DB_FILE.relative_to(ROOT)}")


def cmd_history(args) -> None:
    conn = db_connect()
    query = "SELECT checked_at, asin, keyword, position, organic_position, page FROM checks"
    clauses, params = [], []
    if args.asin:
        clauses.append("asin = ?")
        params.append(args.asin.upper())
    if args.keyword:
        clauses.append("keyword = ?")
        params.append(args.keyword)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY asin, keyword, checked_at DESC LIMIT ?"
    params.append(args.limit)

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No data yet. Run: python rank_tracker.py run")
        return
    print(f"{'checked_at':<20} {'asin':<12} {'keyword':<28} {'pos':>5} {'organic':>8} {'page':>5}")
    print("-" * 84)
    for checked_at, asin, keyword, pos, organic, page in rows:
        print(f"{checked_at:<20} {asin:<12} {keyword[:27]:<28} "
              f"{pos if pos is not None else '-':>5} {organic if organic is not None else '-':>8} "
              f"{page if page is not None else '-':>5}")


def cmd_report(_args) -> None:
    conn = db_connect()
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()

    pairs = conn.execute(
        "SELECT DISTINCT asin, keyword FROM checks ORDER BY asin, keyword"
    ).fetchall()
    if not pairs:
        print("No data yet. Run: python rank_tracker.py run")
        return

    lines = [
        f"# Amazon Keyword Rank Report — {today}",
        "",
        "Tracked with [amazon-keyword-rank-tracker](https://github.com/pangolinfoapi/amazon-keyword-rank-tracker) "
        "using the [Pangolinfo Scrape API](https://www.pangolinfo.com).",
        "",
        "## Latest vs previous",
        "",
        "| ASIN | Keyword | Latest | Previous | Δ | Best (30d) | Worst (30d) |",
        "|---|---|---|---|---|---|---|",
    ]
    for asin, keyword in pairs:
        history = conn.execute(
            """SELECT position, checked_at FROM checks
               WHERE asin = ? AND keyword = ? AND position IS NOT NULL
               ORDER BY checked_at DESC LIMIT 30""",
            (asin, keyword),
        ).fetchall()
        latest = history[0][0] if history else None
        previous = history[1][0] if len(history) > 1 else None
        positions = [p for p, _ in history]
        delta = ""
        if latest is not None and previous is not None:
            diff = previous - latest  # lower position = better
            delta = f"▲ +{diff}" if diff > 0 else (f"▼ {diff}" if diff < 0 else "—")
        best = min(positions) if positions else None
        worst = max(positions) if positions else None
        fmt = lambda v: v if v is not None else "—"
        lines.append(f"| {asin} | {keyword} | {fmt(latest)} | {fmt(previous)} | {delta} | {fmt(best)} | {fmt(worst)} |")

    lines += [
        "",
        "## Full history (latest 200 rows)",
        "",
        "| checked_at (UTC) | ASIN | keyword | position | organic | page |",
        "|---|---|---|---|---|---|",
    ]
    for checked_at, asin, keyword, pos, organic, page in conn.execute(
        """SELECT checked_at, asin, keyword, position, organic_position, page
           FROM checks ORDER BY checked_at DESC LIMIT 200"""
    ):
        fmt = lambda v: v if v is not None else "—"
        lines.append(f"| {checked_at} | {asin} | {keyword} | {fmt(pos)} | {fmt(organic)} | {fmt(page)} |")

    report = "\n".join(lines) + "\n"
    (REPORTS_DIR / f"{today}.md").write_text(report, encoding="utf-8")
    (REPORTS_DIR / "latest.md").write_text(report, encoding="utf-8")

    # CSV export for easy diffing in git
    CSV_FILE.parent.mkdir(exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["checked_at", "asin", "keyword", "domain", "position",
                         "organic_position", "page", "sponsored", "title", "price", "rating"])
        writer.writerows(conn.execute(
            """SELECT checked_at, asin, keyword, domain, position, organic_position,
                      page, sponsored, title, price, rating
               FROM checks ORDER BY checked_at"""
        ))
    print(f"Reports written: reports/{today}.md, reports/latest.md, data/ranks.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Amazon Keyword Rank Tracker (powered by Pangolinfo)")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between API calls (default: 2)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Create targets.json from the example")
    sub.add_parser("run", help="Check rankings for all targets")
    hist = sub.add_parser("history", help="Show ranking history")
    hist.add_argument("--asin")
    hist.add_argument("--keyword")
    hist.add_argument("--limit", type=int, default=50)
    sub.add_parser("report", help="Generate Markdown + CSV reports")

    args = parser.parse_args()
    {"init": cmd_init, "run": cmd_run, "history": cmd_history, "report": cmd_report}[args.command](args) \
        if args.command != "init" else cmd_init()


if __name__ == "__main__":
    main()
