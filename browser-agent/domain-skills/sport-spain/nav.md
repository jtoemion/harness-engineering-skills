# Sport (Spain) - Navigation Recipes

## Scrape Football News

```markdown
## sport-football-news

1. [goto] https://www.sport.es/futbol/
2. [wait] 3 seconds
3. [extract] all links matching article a[href*="/futbol/"]
4. [scrape] for each article, extract title, date, summary
5. [save] to Assets/Football/news/sport-es with wiki-links
```

## La Liga Section

```markdown
## sport-la-liga

1. [goto] https://www.sport.es/futbol/liga/
2. [wait] 3 seconds
3. [extract] standings, match results, news
```

## URL Patterns
- Football: `https://www.sport.es/futbol/`
- Article: `https://www.sport.es/futbol/{slug}`
- La Liga: `https://www.sport.es/futbol/liga/`
- Results: `https://www.sport.es/futbol/resultados/`