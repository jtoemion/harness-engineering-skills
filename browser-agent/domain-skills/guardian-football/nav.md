# Guardian Football - Navigation Recipes

## Scrape Football News

```markdown
## guardian-football-news

1. [goto] https://www.theguardian.com/football
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/football/"]
4. [filter] remove section links (tables, fixtures, results)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml (96 OUT patterns, 84 IN signals)
7. [save] to Assets/News/football with wiki-links
```

## Scrape Live Blog

```markdown
## guardian-live-blog

1. [goto] https://www.theguardian.com/football/live/{slug}
2. [wait] 2 seconds
3. [scrape] extract headline, timestamp, content blocks, score
4. [save] to Assets/News/live-blogs with wiki-links
```

## Scrape Match Report

```markdown
## guardian-match-report

1. [goto] https://www.theguardian.com/football/match/{id}
2. [wait] 3 seconds
3. [scrape] extract teams, score, timeline, key-events
4. [save] to Assets/News/match-reports with wiki-links
```

## URL Patterns
- Article: `https://www.theguardian.com/football/{slug}`
- Section: `https://www.theguardian.com/football`
- Live Blog: `https://www.theguardian.com/football/live/{slug}`
- Match: `https://www.theguardian.com/football/match/{id}`