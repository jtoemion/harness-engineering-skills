# SportsMole - Navigation Recipes

## Scrape Football News

```markdown
## sportsmole-football-news

1. [goto] https://www.sportsmole.co.uk/football
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/football/"]
4. [filter] remove section links (transfers, fixtures, results)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml
7. [save] to Assets/News/football with wiki-links
```

## URL Patterns
- Article: `https://www.sportsmole.co.uk/football/{slug}`
- Section: `https://www.sportsmole.co.uk/football/{section-name}`