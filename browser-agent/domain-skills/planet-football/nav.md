# Planet Football - Navigation Recipes

## Scrape Football News

```markdown
## planet-football-news

1. [goto] https://www.planetfootball.net
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/2025/"], a[href*="/2024/"]
4. [filter] remove section links (cookies, login, register)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml
7. [save] to Assets/News/football with wiki-links
```

## Scrape Latest Articles

```markdown
## planet-football-latest

1. [goto] https://www.planetfootball.net/latest
2. [wait] 3 seconds
3. [scrape] article listings, titles, excerpts, dates
4. [save] to Assets/News/football with wiki-links
```

## Scrape Category

```markdown
## planet-football-category

1. [goto] https://www.planetfootball.net/category/{category}
2. [wait] 3 seconds
3. [scrape] category articles, titles, dates
4. [save] to Assets/News/football with wiki-links
```

## URL Patterns
- Homepage: `https://www.planetfootball.net`
- Article: `https://www.planetfootball.net/{slug}`
- Section: `https://www.planetfootball.net/{section}`
- Category: `https://www.planetfootball.net/category/{category}`
- Latest: `https://www.planetfootball.net/latest`