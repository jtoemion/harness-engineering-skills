# A Bola (Portugal) - Navigation Recipes

## Scrape Football News

```markdown
## abola-football-news

1. [goto] https://www.abola.pt/
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/nn/"]
4. [filter] remove internal nav links
5. [scrape] for each link, extract title, summary, date, category
6. [save] to Assets/News/football with wiki-links
```

## Get Match Results

```markdown
## abola-match-results

1. [goto] https://www.abola.pt/nn/liga/resultados
2. [wait] 2 seconds
3. [extract] match data: teams, score, time, competition
4. [save] to Assets/Stats/matches with date grouping
```

## Scrape Football Section

```markdown
## abola-football-section

1. [goto] https://www.abola.pt/nn/futebol/
2. [wait] 3 seconds
3. [extract] article cards: title, link, summary, timestamp
4. [scrape] open each article for full content
5. [save] to Assets/News/abola with wiki-links
```

## URL Patterns
- Homepage: `https://www.abola.pt/`
- Football: `https://www.abola.pt/nn/futebol/`
- Results: `https://www.abola.pt/nn/liga/resultados`