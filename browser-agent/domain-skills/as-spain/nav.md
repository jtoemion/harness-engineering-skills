# AS (Spain) - Navigation Recipes

## Scrape Football News

```markdown
## as-football-news

1. [goto] https://www.as.com/futbol/
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/futbol/"]
4. [filter] remove section links (resultados, clasificaciones)
5. [scrape] for each link, extract title, content, author, date
6. [save] to Assets/News/football with wiki-links
```

## URL Patterns
- Article: `https://www.as.com/futbol/{slug}`
- Section: `https://www.as.com/futbol/`