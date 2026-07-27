# Amazon Keyword Rank Tracker — Free & Open Source

Track where your products rank on Amazon for any keyword, every day, for free.
Built in Python on top of the [Pangolinfo Scrape API](https://www.pangolinfo.com) — the
[Amazon data API](https://www.pangolinfo.com) that handles anti-bot, IP rotation and
page-structure changes for you.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![Data: Pangolinfo Scrape API](https://img.shields.io/badge/data-Pangolinfo%20Scrape%20API-orange.svg)](https://www.pangolinfo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why track Amazon keyword rankings?

For Amazon sellers, **organic keyword ranking decides sales**. If your ASIN is not on
page 1 for your main keywords, shoppers never see it. Rank tracking tells you:

- whether your listing optimization (title, bullets, backend keywords) actually worked
- when a competitor overtakes you — and on which keyword
- whether ad spend is cannibalizing or supporting your organic positions

Commercial rank trackers cost $50–100/month. This repo gives you the same core
capability for free: your own data, your own database, no lock-in.

## Features

- 🔎 **Keyword ranking lookup** — find your ASIN's exact position in Amazon search results (absolute + organic-only position, sponsored slots detected)
- 📈 **Daily monitoring** — SQLite history, trend report with day-over-day changes, 30-day best/worst
- 🤖 **Free automation** — included GitHub Actions workflow runs the check daily and commits reports back to your repo
- 🌍 **Multi-marketplace** — any Amazon domain (`www.amazon.com`, `.co.uk`, `.de`, `.co.jp`…), with ZIP-code-level localization
- 📄 **Multi-page scanning** — optionally scan page 2+ for deep rankings
- 🧩 **Zero infrastructure** — one Python file + SQLite; data stays in your repo

## Quickstart

### 1. Get a free API key

Sign up at [tool.pangolinfo.com](https://tool.pangolinfo.com) — open-source users get
**200 free API calls** (enough for weeks of daily tracking of a few keywords).

### 2. Install

```bash
git clone https://github.com/pangolinfoapi/amazon-keyword-rank-tracker.git
cd amazon-keyword-rank-tracker
pip install -r requirements.txt
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

## Automated daily tracking with GitHub Actions

This repo ships with [`.github/workflows/track.yml`](.github/workflows/track.yml):

1. Fork / push this repo to your GitHub account
2. Repo **Settings → Secrets and variables → Actions → New repository secret** →
   name `PANGOLIN_TOKEN`, value = your API key
3. Done — the workflow runs every day at 01:00 UTC and commits fresh
   `data/ranks.csv` + `reports/YYYY-MM-DD.md` back to the repo

Your ranking history becomes a public, versioned dataset you can chart anywhere.

## Use cases for Amazon sellers

- **Listing SEO validation** — did rewriting your title move the needle? Watch the 7-day trend instead of guessing
- **Launch monitoring** — track your target keywords daily during a product launch
- **Competitor watchdog** — track a competitor's ASIN the same way; get alerted when they climb
- **Ad efficiency** — if your sponsored rank is high but organic is stuck on page 3, you know ads are masking an SEO problem
- **Agency reporting** — `reports/latest.md` is a client-ready ranking table

## How it works

1. For every keyword, the tracker calls the
   [Pangolinfo Scrape API](https://www.pangolinfo.com) (`amzKeywordSearch` parser),
   which returns real, localized Amazon search result pages as structured JSON
2. Your ASIN is located in the ordered results → absolute position, organic-only
   position, page number, sponsored flag
3. Every check is appended to a local SQLite database; reports diff the latest
   run against the previous one

No selectors to maintain, no proxies to manage — the API handles Amazon's
anti-bot defenses and page-layout changes.

## FAQ

### Is there a free Amazon keyword rank tracker?

Yes — this repo. You bring a free [Pangolinfo API key](https://tool.pangolinfo.com)
(200 free calls), the code and automation here are MIT-licensed. 200 calls ≈
daily tracking of 6 keywords for a month.

### How do I track Amazon keyword ranking for free without a browser extension?

Browser extensions only see your own searches, which are personalized. This
tracker fetches neutral, localized results (you can set any US ZIP code), so the
positions reflect what a real new customer would see.

### What is the difference between "position" and "organic position"?

`position` is the absolute slot on the page (ads included). `organic_position`
counts only non-sponsored results — that is the number Amazon SEO work moves.

### Can I track keywords on Amazon UK / DE / JP?

Yes — set `"domain": "www.amazon.co.uk"` (or `.de`, `.co.jp`, …) in `targets.json`.

### Where does the data come from?

From the [Pangolinfo Scrape API](https://www.pangolinfo.com), a commercial
Amazon/Walmart/eBay data API with a free tier. See the
[API documentation](https://docs.pangolinfo.com) for all available parsers
(product detail, reviews, Best Sellers, category lists…).

## Related open-source tools

- [pangolinfo-amazon-scraper](https://pypi.org/project/pangolinfo-amazon-scraper/) — the Python SDK this tracker uses (product detail, reviews, search, Best Sellers)
- [pangolinfo-mcp](https://pypi.org/project/pangolinfo-mcp/) — use the same data from Claude/Cursor/any MCP client, no code needed

## Contributing

Issues and PRs welcome — ideas: alert webhooks (Telegram/Slack), chart
generation, more marketplaces, multi-ASIN dashboards.

## License

MIT © pangolinfo. Data provided by [Pangolinfo](https://www.pangolinfo.com);
this project is not affiliated with or endorsed by Amazon.com, Inc.
