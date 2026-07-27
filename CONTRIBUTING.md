# Contributing

Thanks for your interest in improving this tool! It is part of the
[Pangolinfo open-source ecosystem](related-projects.md).

## Ways to help

- 🐛 **Report bugs** — open an issue with the exact command, your `keywords.json` /
  `targets.json` / `niches.json` / `reviews.json` (ASINs redacted), and the error.
- 💡 **Suggest features** — ideas we love: alert webhooks (Slack/Telegram/Discord),
  chart generation, multi-ASIN dashboards, more marketplaces, CSV/JSON exports.
- 🔧 **Send a PR** — keep it small and single-purpose.

## Local development

This project is **Python standard library only** — there is nothing to install.

```bash
git clone https://github.com/pangolinfoapi/<this-repo>.git
cd <this-repo>
export PANGOLIN_TOKEN="your-free-key-from-tool.pangolinfo.com"
python <tool>.py run
```

## Guidelines

1. Run the tool end-to-end locally before opening a PR.
2. Keep dependencies at zero (stdlib only) unless there is a strong reason.
3. Update the README / `related-projects.md` if you change links or the ecosystem map.
4. Be respectful — we follow a standard code of conduct (be kind, assume good intent).

## License

By contributing, you agree your contributions are released under the
[MIT License](LICENSE).
