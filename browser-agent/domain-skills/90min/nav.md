# 90min - Navigation Recipes

## Scrape Football News

```markdown
## 90min-football-news

1. [goto] https://www.90min.com
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/posts/"]
4. [filter] remove promotional/partner content
5. [scrape] for each link, extract title, excerpt, author, date, category
6. [filter] apply news_signals.yaml (96 OUT patterns, 84 IN signals)
7. [save] to Assets/News/football with wiki-links
```

## Scrape Latest News

```markdown
## 90min-latest-news

1. [goto] https://www.90min.com/posts
2. [wait] 3 seconds
3. [scrape] article titles, excerpts, authors, dates, categories
4. [save] to Assets/News/latest with wiki-links
```

## Scrape By Category

```markdown
## 90min-category-news

1. [goto] https://www.90min.com/categories/{category}
2. [wait] 3 seconds
3. [extract] article links matching /posts/
4. [scrape] for each, extract title, author, date, category
5. [save] to Assets/News/{category} with wiki-links
```

## URL Patterns
- Article: `https://www.90min.com/posts/{slug}`
- Section: `https://www.90min.com/categories/{category}`
- User: `https://www.90min.com/users/{username}`