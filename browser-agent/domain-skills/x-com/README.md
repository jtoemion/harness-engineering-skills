# x.com Domain Skill

**URL:** https://x.com
**Backend:** opencode-browser (chrome) - NOT Playwright
**Mapped:** 2026-04-25

## ⚠️ MANDATORY: Backend = Chrome

x.com has `backend: chrome` in `_meta.yaml`. **Always** use opencode-browser via `chrome_backend.py`. Never Playwright or CDP.

## Structure

```
x-com/
├── _meta.yaml          # backend: chrome
├── accounts.md         # List of football accounts to scrape
├── nav.md              # Navigation recipes
├── failures.md         # Known issues & fixes
├── scrape_tweets.py    # Main scraping script
└── credentials.md      # Login credentials (HarukawaShin)
```

## Daily Tweet Scraping

```bash
cd C:\Users\jtoem\.config\opencode\skills\browser-agent\domain-skills\x-com
python scrape_tweets.py
```

**Output:** `C:\Users\jtoem\Assets\News\football\entities\news\{account}-YYYY-MM-DD.md`

**Accounts:** Edit `scrape_tweets.py` ACCOUNTS list to configure.

## Requirements

1. opencode-browser broker running:
   ```bash
   node "C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js" tool browser_status
   ```
   Should return `{"broker":true,"hostConnected":true,...}`

2. Chrome with opencode-browser extension
3. Extension activated on x.com tabs (click extension icon if "permission not granted")

## Known Issues

See `failures.md` for current issues:
- "No matches for selectors: article" - tab not fully loaded
- "Site access permission not granted" - activate extension on tab