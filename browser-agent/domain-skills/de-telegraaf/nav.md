# De Telegraaf - Navigation Recipes

## Scrape Sport Homepage

```markdown
## telegraaf-sport-home

1. [goto] https://www.telegraaf.nl/sport/
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/sport/"]
4. [scrape] for each link, extract title, summary, sport category
5. [filter] apply news_signals.yaml
6. [save] to Assets/News/telegraaf-sport with wiki-links
```

## Scrape Football News

```markdown
## telegraaf-football

1. [goto] https://www.telegraaf.nl/sport/voetbal/
2. [wait] 3 seconds
3. [extract] article links matching a[href*="/sport/voetbal/"]
4. [extract] title, summary, author, publication date
5. [scrape] full article content for key stories
6. [filter] apply news_signals.yaml
7. [save] to Assets/News/telegraaf-football with wiki-links
```

## Scrape Eredivisie

```markdown
## telegraaf-eredivisie

1. [goto] https://www.telegraaf.nl/sport/voetbal/eredivisie/
2. [wait] 3 seconds
3. [extract] match results and standings
4. [scrape] clubs (Ajax, Feyenoord, PSV, etc.)
5. [scrape] transfer news
6. [save] to Assets/Football/telegraaf-eredivisie
```

## URL Patterns
- Sport: `https://www.telegraaf.nl/sport/`
- Football: `https://www.telegraaf.nl/sport/voetbal/`
- Eredivisie: `https://www.telegraaf.nl/sport/voetbal/eredivisie/`
- Article: `https://www.telegraaf.nl/sport/{category}/{slug}`