# Pangolinfo Open-Source Ecosystem

This project is part of the **Pangolinfo open-source family** — a collection of free,
single-purpose tools built on the [Pangolinfo](https://www.pangolinfo.com) data APIs and
the [Model Context Protocol server](https://mcp.pangolinfo.com/mcp) (`mcp.pangolinfo.com/mcp`).

Everything here is free to fork, run, and automate with GitHub Actions. Data is sourced
from Pangolinfo; you only need a free API key
([tool.pangolinfo.com](https://tool.pangolinfo.com), **200 free calls**, no credit card).

---

## 🛰️ Satellite tools — by [@pangolinfoapi](https://github.com/pangolinfoapi)

Free, daily-automated, single-purpose tools you can fork and run in GitHub Actions:

| Tool | What it does |
|---|---|
| [amazon-keyword-rank-tracker](https://github.com/pangolinfoapi/amazon-keyword-rank-tracker) | Daily Amazon keyword ranking for your ASINs (absolute + organic position, sponsored detection) |
| [amazon-niche-finder](https://github.com/pangolinfoapi/amazon-niche-finder) | Blue-ocean Amazon niche discovery (search volume ÷ brand count scoring) |
| [google-trends-tracker](https://github.com/pangolinfoapi/google-trends-tracker) | Daily Google Trends monitoring with rising/falling detection + sparklines |
| [amazon-review-analyzer](https://github.com/pangolinfoapi/amazon-review-analyzer) | Amazon review sentiment scoring + complaint/praise theme mining |

---

## 🏗️ Official Pangolinfo projects — by [@Pangolin-spg](https://github.com/Pangolin-spg)

The upstream SDKs, CLIs, skills and API references these tools are built on:

| Project | ★ | Description |
|---|---|---|
| [amazon-walmart-shopify-scrape-api](https://github.com/Pangolin-spg/amazon-walmart-shopify-scrape-api) | 56 | Powerful Scrape API for Amazon, Walmart, Shopify, Shopee, eBay — product details, rankings, HTML/JSON/Markdown |
| [pangolinfo-amazon-scraper-cli](https://github.com/Pangolin-spg/pangolinfo-amazon-scraper-cli) | 8 | 亚马逊爬虫与数据采集 CLI — Agent/AI-friendly JSON & Markdown output, Skill integration |
| [openclaw-skill-pangolinfo](https://github.com/Pangolin-spg/openclaw-skill-pangolinfo) | 8 | Real-time Web Scraper Skill for OpenClaw & AI Agents (Google, Amazon, Walmart) |
| [openclaw-skills](https://github.com/Pangolin-spg/openclaw-skills) | 3 | OpenClaw skills by Pangolinfo — AI SERP (Google SERP + AI Overviews) & Amazon Scraper |
| [clawdbot-competitor-monitor](https://github.com/Pangolin-spg/clawdbot-competitor-monitor) | 3 | Automate Amazon competitor analysis using Clawdbot + Pangolinfo API |
| [pangolinfo-amazon-scraper](https://github.com/Pangolin-spg/pangolinfo-amazon-scraper) | 1 | Official Python SDK for the Pangolinfo Scrape API (product/reviews/search/Best Sellers) |
| [amazon-follow-seller-scraper-api](https://github.com/Pangolin-spg/amazon-follow-seller-scraper-api) | 1 | Amazon Follow Seller Scraper API for OpenClaw — bypass CAPTCHAs/anti-bot |
| [amazon-scrape-api](https://github.com/Pangolin-spg/amazon-scrape-api) | 1 | E-commerce Scraping API (Amazon/Walmart/Shopify/eBay), auto-adapts to page changes |
| [Pangolin-spg.github.io](https://github.com/Pangolin-spg/Pangolin-spg.github.io) | 1 | E-commerce data scraping docs & technical blog |

---

## 🔌 Use the same data from your AI assistant

Prefer no code? Connect any MCP client (Claude, Cursor, Windsurf, ChatGPT) to
[`mcp.pangolinfo.com/mcp`](https://mcp.pangolinfo.com/mcp) and call the same tools
(`search_amazon`, `filter_niches`, `keyword_trends`, `get_amazon_reviews`, …) directly.

- Official MCP server & docs: [pangolinfo-mcp](https://github.com/Pangolin-spg/pangolinfo-amazon-scraper) (Python SDK)
- Live MCP endpoint: `https://mcp.pangolinfo.com/mcp`

---

## 🆓 Get a free API key

1. Sign up at [tool.pangolinfo.com](https://tool.pangolinfo.com) — free, no credit card.
2. Copy your **Bearer token** (JWT).
3. Use it as the `PANGOLIN_TOKEN` environment variable / GitHub Actions secret.

Every tool ships with a free tier of **200 API calls** — enough for weeks of daily
tracking across a handful of keywords or ASINs.

---

*Maintained as part of the Pangolinfo open-source ecosystem. MIT licensed.*
