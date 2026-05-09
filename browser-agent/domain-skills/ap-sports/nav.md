# AP Sports - Navigation Recipes

## Scrape Sports News

```markdown
## ap-sports-news

1. [goto] https://apnews.com/sports
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/sports/"]
4. [filter] remove section links (videos, photos, indexes)
5. [scrape] for each link, extract title, content, author, date
6. [save] to Assets/News/sports with wiki-links
```

## Scrape Article

```markdown
## ap-article

1. [goto] https://apnews.com/sports/{slug}
2. [wait] 2 seconds
3. [scrape] extract headline, timestamp, content blocks, byline
4. [save] to Assets/News/articles with wiki-links
```

## URL Patterns
- Article: `https://apnews.com/sports/{slug}`
- Section: `https://apnews.com/sports`
- Author: `https://apnews.com/author/{author-slug}`