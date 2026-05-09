# Sport Bild (Germany) - Navigation Recipes

## Scrape Football News

```markdown
## sportbild-football-news

1. [goto] https://www.sportbild.de/fussball/
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/fussball/"]
4. [filter] remove section links (ergebnisse, tabellen)
5. [scrape] for each link, extract title, content, author, date
6. [save] to Assets/News/football with wiki-links
```

## Scrape Bundesliga

```markdown
## sportbild-bundesliga

1. [goto] https://www.sportbild.de/fussball/bundesliga/
2. [wait] 3 seconds
3. [extract] all article links
4. [scrape] for each link, extract title, content, date
5. [save] to Assets/News/bundesliga with wiki-links
```

## URL Patterns
- Article: `https://www.sportbild.de/fussball/{slug}`
- Section: `https://www.sportbild.de/fussball/`
- Bundesliga: `https://www.sportbild.de/fussball/bundesliga/`