# Sky Sports - Navigation Recipes

## Scrape Football News

```markdown
## sky-football-news

1. [goto] https://www.skysports.com/football
2. [wait] 3 seconds
3. [extract] all links matching .news-list__link, h2 a[href*="/football/"]
4. [filter] remove navigation team links (short titles, no article pattern)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml
7. [save] to Assets/News/football with wiki-links
```

## URL Patterns
- Article: `https://www.skysports.com/football/{slug}`
- Section: `https://www.skysports.com/football/{section}`