# AFP Sport - Navigation Recipes

## Scrape Sports News

```markdown
## afp-sports-news

1. [goto] https://www.afp.com/en/sports
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/en/sports/news/"]
4. [scrape] for each link, extract title, content, author, date
5. [save] to Assets/News/sports with wiki-links
```

## URL Patterns
- Article: `https://www.afp.com/en/sports/news/{slug}`
- Section: `https://www.afp.com/en/sports`