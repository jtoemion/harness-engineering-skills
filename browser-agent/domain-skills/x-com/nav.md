# x.com Navigation Recipes

## Daily Tweet Scraping

### Scrape tweets from configured accounts

```bash
cd C:\Users\jtoem\.config\opencode\skills\browser-agent\domain-skills\x-com
python scrape_tweets.py
```

### Output

Tweets saved to: `C:\Users\jtoem\Assets\News\football\entities\news\`
- `{account_name}-YYYY-MM-DD.md` - One file per account
- Each file contains 2-5 tweets with dates and sources

### Configure accounts

Edit `scrape_tweets.py` ACCOUNTS list:
```python
ACCOUNTS = [
    ("AccountHandle", "https://x.com/AccountHandle"),
    # ...
]
```

### Requirements

- opencode-browser broker running (`node cli.js tool browser_status`)
- Chrome with opencode-browser extension
- `backend: chrome` in `_meta.yaml` (uses real Chrome, not Playwright)

## Manual Navigation

1. Open Chrome with opencode-browser extension
2. Navigate to `https://x.com/<handle>`
3. Wait for page to fully load
4. Use `browser_query` with `article` selector to extract posts