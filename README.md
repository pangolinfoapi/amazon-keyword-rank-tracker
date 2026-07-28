# Amazon Keyword Rank Tracker — Free & Open Source

[![Track](https://github.com/pangolinfoapi/amazon-keyword-rank-tracker/actions/workflows/track.yml/badge.svg)](https://github.com/pangolinfoapi/amazon-keyword-rank-tracker/actions/workflows/track.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![Built with Pangolinfo](https://img.shields.io/badge/built%20with-Pangolinfo-blue)](https://www.pangolinfo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Track where your products rank on Amazon for any keyword, every day, for free.**
> Built in Python on top of [Pangolinfo](https://www.pangolinfo.com) — the
> [Amazon data API](https://www.pangolinfo.com) that handles anti-bot, IP rotation and
> page-structure changes for you.

Part of the [Pangolinfo open-source ecosystem](related-projects.md) — a family of free
tools built on the [Pangolinfo MCP server](https://mcp.pangolinfo.com/mcp).

---

## Table of contents

- [Why track Amazon keyword rankings?](#why-track-amazon-keyword-rankings)
- [Features](#features)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Automated daily tracking (GitHub Actions)](#automated-daily-tracking-github-actions)
- [Use cases for Amazon sellers](#use-cases-for-amazon-sellers)
- [How it works](#how-it-works)
- [🌐 Pangolinfo ecosystem](#-pangolinfo-ecosystem)
- [FAQ](#faq)
- [Roadmap](#roadmap)

---

## Why track Amazon keyword rankings?

For Amazon sellers, **organic keyword ranking decides sales**. If your ASIN is not on
page 1 for your main keywords, shoppers never see it. Rank tracking tells you:

- whether your listing optimization (title, bullets, backend keywords) actually worked
- when a competitor overtakes you — and on which keyword
- whether ad spend is cannibalizing or supporting your organic positions

Commercial rank trackers cost **$50–100/month**. This repo gives you the same core
capability for free: your own data, your own database, no lock-in.

---

## Features

- 🔎 **Keyword ranking lookup** — find your ASIN's exact position in Amazon search
  results (absolute + organic-only position, sponsored slots detected)
- 📈 **Daily monitoring** — SQLite history, trend report with day-over-day changes,
  30-day best/worst
- 🤖 **Free automation** — included GitHub Actions workflow runs the check daily and
  commits reports back to your repo
- 🌍 **Multi-marketplace** — any Amazon domain (`www.amazon.com`, `.co.uk`, `.de`,
  `.co.jp`…), with ZIP-code-level localization
- 📄 **Multi-page scanning** — optionally scan page 2+ for deep rankings
- 🧩 **Zero infrastructure** — one Python file + SQLite; data stays in your repo

---

## Architecture

```
        ┌─────────────────────────────────────────────┐
        │  amazon-keyword-rank-tracker (this repo)     │
        │  rank_tracker.py  ·  SQLite (data/ranks.db)  │
        └───────────────────┬─────────────────────────┘
                            │  streamable-HTTP (MCP)
                            │  tools/call → search_amazon
                            ▼
        ┌─────────────────────────────────────────────┐
        │   Pangolinfo MCP server                       │
        │   mcp.pangolinfo.com/mcp  (Bearer JWT)        │
        └───────────────────┬─────────────────────────┘
                            │  proxy → Amazon search
                            ▼
                  Amazon search results (JSON)
```

No selectors to maintain, no proxies to manage — the API handles Amazon's anti-bot
defenses and page-layout changes.

---

## Quickstart

### 1. Get a free API key

Sign up at [tool.pangolinfo.com](https://tool.pangolinfo.com) — open-source users get
**200 free API calls** (enough for weeks of daily tracking of a few keywords).

### 2. Install

```bash
git clone https://github.com/pangolinfoapi/amazon-keyword-rank-tracker.git
cd amazon-keyword-rank-tracker
pip install -r requirements.txt   # optional; stdlib-only by default
```

### 3. Configure your products

```bash
python rank_tracker.py init     # creates targets.json
```

Edit `targets.json` — one entry per ASIN:

```json
[
  {
    "asin": "B0DYTF8L2W",
    "keywords": ["wireless earbuds", "bluetooth earbuds"],
    "domain": "www.amazon.com",
    "zipcode": "10041",
    "pages": 2
  }
]
```

### 4. Run

```bash
export PANGOLIN_TOKEN="your-token"
python rank_tracker.py run       # check all ASIN × keyword pairs
python rank_tracker.py history   # browse stored positions
python rank_tracker.py report    # generate reports/latest.md + data/ranks.csv
```

Example output:

```
  ✓ B0DYTF8L2W @ 'wireless earbuds': position 14 (page 1)
  · B0DYTF8L2W @ 'bluetooth earbuds': not in first 2 page(s)

Done: 1/2 keywords ranked. Stored in data/ranks.db
```

---

## Automated daily tracking (GitHub Actions)

This repo ships with [`.github/workflows/track.yml`](.github/workflows/track.yml):

1. Fork / push this repo to your GitHub account
2. Repo **Settings → Secrets and variables → Actions → New repository secret** →
   name `PANGOLIN_TOKEN`, value = your API key
3. Done — the workflow runs every day at 01:00 UTC and commits fresh
   `data/ranks.csv` + `reports/YYYY-MM-DD.md` back to the repo

Your ranking history becomes a public, versioned dataset you can chart anywhere. See
[docs/SETUP.md](docs/SETUP.md) for the full walkthrough and troubleshooting.

---

## Use cases for Amazon sellers

- **Listing SEO validation** — did rewriting your title move the needle? Watch the
  7-day trend instead of guessing
- **Launch monitoring** — track your target keywords daily during a product launch
- **Competitor watchdog** — track a competitor's ASIN the same way; get alerted when
  they climb
- **Ad efficiency** — if your sponsored rank is high but organic is stuck on page 3,
  you know ads are masking an SEO problem
- **Agency reporting** — `reports/latest.md` is a client-ready ranking table

---

## How it works

1. For every keyword, the tracker calls the
   [Pangolinfo MCP server](https://mcp.pangolinfo.com/mcp) (`search_amazon` tool),
   which returns real, localized Amazon search result pages as structured JSON
2. Your ASIN is located in the ordered results → absolute position, organic-only
   position, page number, sponsored flag
3. Every check is appended to a local SQLite database; reports diff the latest
   run against the previous one

> Prefer no code? Connect Claude / Cursor / Windsurf / ChatGPT to
> `https://mcp.pangolinfo.com/mcp` and call `search_amazon` directly.

---

## 🌐 Pangolinfo ecosystem

This tool is one of several free tools in the **Pangolinfo open-source ecosystem**.

### 🛰️ More free tools by [@pangolinfoapi](https://github.com/pangolinfoapi)

🏠 **Hub:** [All tools, landing pages & tutorials](https://pangolinfoapi.github.io/)

- [amazon-niche-finder](https://pangolinfoapi.github.io/amazon-niche-finder/) —
  discover blue-ocean Amazon niches (low competition, high demand)
- [google-trends-tracker](https://pangolinfoapi.github.io/google-trends-tracker/) —
  monitor keyword interest with Google Trends, daily
- [amazon-review-analyzer](https://pangolinfoapi.github.io/amazon-review-analyzer/) —
  Amazon review sentiment + complaint/praise theme mining

### 🏗️ Built on the official Pangolinfo projects ([by @Pangolin-spg](https://github.com/Pangolin-spg))

- [pangolinfo-amazon-scraper](https://github.com/Pangolin-spg/pangolinfo-amazon-scraper)
  — the official Python SDK for the Pangolinfo Scrape API (this tool's data source)
- [amazon-walmart-shopify-scrape-api](https://github.com/Pangolin-spg/amazon-walmart-shopify-scrape-api)
  ⭐ 56 — the underlying Scrape API for Amazon, Walmart, Shopify, Shopee, eBay
- [pangolinfo-amazon-scraper-cli](https://github.com/Pangolin-spg/pangolinfo-amazon-scraper-cli)
  ⭐ 8 — Agent/AI-friendly CLI for Amazon data collection
- [clawdbot-competitor-monitor](https://github.com/Pangolin-spg/clawdbot-competitor-monitor)
  ⭐ 3 — automate Amazon competitor analysis

> See [related-projects.md](related-projects.md) for the full map of official
> Pangolinfo projects, skills and the live MCP endpoint.

---

## FAQ

### Is there a free Amazon keyword rank tracker?

Yes — this repo. You bring a free [Pangolinfo API key](https://tool.pangolinfo.com)
(200 free calls), the code and automation here are MIT-licensed. 200 calls ≈
daily tracking of 6 keywords for a month.

### How do I track Amazon keyword ranking for free without a browser extension?

Browser extensions only see your own searches, which are personalized. This tracker
fetches neutral, localized results (you can set any US ZIP code), so the positions
reflect what a real new customer would see.

### What is the difference between "position" and "organic position"?

`position` is the absolute slot on the page (ads included). `organic_position` counts
only non-sponsored results — that is the number Amazon SEO work moves.

### Can I track keywords on Amazon UK / DE / JP?

Yes — set `"domain": "www.amazon.co.uk"` (or `.de`, `.co.jp`, …) in `targets.json`.

### Where does the data come from?

From the [Pangolinfo Scrape API](https://www.pangolinfo.com), a commercial
Amazon/Walmart/eBay data API with a free tier. See the
[API documentation](https://docs.pangolinfo.com) for all available parsers
(product detail, reviews, Best Sellers, category lists…).

---

## Roadmap

- [ ] Alert webhooks (Telegram / Slack / Discord) on rank drops
- [ ] Chart generation (SVG / HTML trend charts)
- [ ] Multi-ASIN dashboards
- [ ] More marketplaces (Walmart, eBay) via the Pangolinfo API

---

## Contributing

Ideas and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). The bigger ecosystem
map lives in [related-projects.md](related-projects.md).

## License

MIT © pangolinfo. Data provided by [Pangolinfo](https://www.pangolinfo.com);
this project is not affiliated with or endorsed by Amazon.com, Inc.
