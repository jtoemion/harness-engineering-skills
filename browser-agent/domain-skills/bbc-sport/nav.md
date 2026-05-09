# BBC Sport - Navigation Recipes

## Scrape Football News

```markdown
## bbc-football-news

1. [goto] https://www.bbc.com/sport/football
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/sport/football/articles/"]
4. [filter] remove section links (scores-fixtures, tables, scorers)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml (96 OUT patterns, 84 IN signals)
7. [save] to Assets/News/football with wiki-links
```

## URL Patterns
- Article: `https://www.bbc.com/sport/football/articles/{slug}`
- Section: `https://www.bbc.com/sport/football/{section-name}`