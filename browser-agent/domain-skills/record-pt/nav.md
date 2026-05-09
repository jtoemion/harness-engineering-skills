# Record (Portugal) - Navigation Recipes

## Recipes

### football-news
Navigate to football section and extract article links.

```
1. [goto] https://www.record.pt/futebol/
2. [wait] 3 seconds
3. [extract] article links
```

### article-content
Navigate to specific article and extract content.

```
1. [goto] {url}
2. [wait] 2 seconds
3. [scrape] article title, body, metadata
```

## Navigation Patterns

- Main football: `https://www.record.pt/futebol/`
- Article: `https://www.record.pt/futebol/{slug}`
- Match center: `https://www.record.pt/futebol/{competition}/{match-id}`