# Reuters Sports - Navigation Recipes

## Scrape Sports News

```markdown
## reuters-sports-news

1. [goto] https://www.reuters.com/sports
2. [wait] 3 seconds
3. [extract] all links matching article[data-id]
4. [scrape] for each link, extract title, content, timestamp, author
5. [filter] apply news_signals.yaml
6. [save] to Assets/News/sports with wiki-links
```

## URL Patterns
- Article: `https://www.reuters.com/sports/{sport}/{slug}`
- Section: `https://www.reuters.com/sports/{sport}`
- Homepage: `https://www.reuters.com/sports`

## Sport Sections
- football
- tennis
- basketball
- motorsport
- golf
- boxing
- athletics