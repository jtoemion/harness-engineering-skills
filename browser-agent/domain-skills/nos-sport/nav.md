# NOS Sport - Navigation Recipes

## Scrape Match Center

```markdown
## nos-match-center

1. [goto] https://nos.nl/wedstrijd/{match_id}
2. [wait] 3 seconds
3. [extract] match header (teams, score, competition, time)
4. [extract] live stats (possession, shots, corners)
5. [extract] timeline events (goals, cards, substitutions)
6. [scrape] match summary and key moments
```

## Scrape Sport News

```markdown
## nos-sport-news

1. [goto] https://nos.nl/sport
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/artikel/"]
4. [scrape] for each link, extract title, summary, date, sport
5. [filter] apply news_signals.yaml
6. [save] to Assets/News/nos-sport with wiki-links
```

## URL Patterns
- Match: `https://nos.nl/wedstrijd/{id}`
- Article: `https://nos.nl/artikel/{slug}`
- Sport Section: `https://nos.nl/sport/{category}`