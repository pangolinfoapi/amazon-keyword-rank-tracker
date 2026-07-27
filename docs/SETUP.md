# Setup & Deployment Guide

A deeper walkthrough for running and automating this tool. For the one-minute version,
see the project `README.md`.

## 1. Get a free Pangolinfo API key

All tools in the [Pangolinfo open-source ecosystem](related-projects.md) are powered by
the [Pangolinfo Scrape / Data APIs](https://www.pangolinfo.com) (or the
[MCP server](https://mcp.pangolinfo.com/mcp)). You need a single API key:

1. Sign up at **[tool.pangolinfo.com](https://tool.pangolinfo.com)** — free, no credit card.
2. Open **Dashboard → API Keys** and copy your **Bearer token** (a long `eyJ…` JWT).
3. This token is your `PANGOLIN_TOKEN`.

> Free tier = **200 API calls**. Each daily run makes ~1 call per tracked item, so the
> free tier lasts a long time for a small watchlist.

## 2. Run locally

```bash
git clone https://github.com/pangolinfoapi/<repo>.git
cd <repo>

# 2a. Provide the key (never commit it)
export PANGOLIN_TOKEN="paste-your-token-here"

# 2b. (optional) create your config from the example
python <tool>.py init

# 2c. run
python <tool>.py run
python <tool>.py report
python <tool>.py history
```

## 3. Automate with GitHub Actions (free, daily)

The repo ships with `.github/workflows/track.yml`. To enable it:

1. **Fork** this repo to your own GitHub account (or push it to one you own).
2. Go to **Settings → Secrets and variables → Actions → New repository secret**.
3. Name: `PANGOLIN_TOKEN` · Value: your token from step 1.
4. Done — the workflow runs daily (default 01:00 UTC) and commits fresh data + reports
   back to the repo.

### Where the data lives

- `data/*.db` — a local SQLite database (your versioned history).
- `reports/latest.md`, `data/*.csv` — human + machine-readable snapshots.

These are committed by the workflow so the repo doubles as a public, self-updating
dataset you can chart anywhere.

## 4. Connect from an AI assistant (no code)

Prefer to ask an AI instead of running cron jobs? Connect any MCP client
(Claude, Cursor, Windsurf, ChatGPT desktop) to:

```
https://mcp.pangolinfo.com/mcp
```

…and call the same tools these scripts use (`search_amazon`, `filter_niches`,
`keyword_trends`, `get_amazon_reviews`). See the
[official Pangolinfo projects](related-projects.md#-official-pangolinfo-projects--bypangolin-spg)
for the SDKs and skills.

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `401` / `403` from the API | Bad or missing `PANGOLIN_TOKEN` | Re-copy the token; ensure it is set as the env var / secret exactly |
| Workflow run fails instantly | Secret not set | Add `PANGOLIN_TOKEN` repo secret (see step 3) |
| Empty report | Token valid but no data returned | Check your `*.json` config (ASINs/keywords/marketplace) |
| `5xx` from `mcp.pangolinfo.com` | Pangolinfo backend temporary outage | Retry later; the daily cron will self-heal on the next run |

## 6. Security notes

- Your token is **never** written to the repo. Locally it lives in your shell env;
  on GitHub it lives only in encrypted Actions secrets.
- Rotate your token at [tool.pangolinfo.com](https://tool.pangolinfo.com) if it ever leaks.
- This is an independent open-source tool and is **not affiliated with Amazon.com, Inc.**
