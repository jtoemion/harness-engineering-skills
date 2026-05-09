# Transfermarkt - Navigation Recipes

## Scrape Football News and Transfers

```markdown
## transfermarkt-football-news

1. [goto] https://www.transfermarkt.com
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/news/"], a[href*="/transfermarkt"]
4. [filter] remove section links (cookies, login, register)
5. [scrape] for each link, extract title, content, author, date
6. [filter] apply news_signals.yaml
7. [save] to Assets/News/football with wiki-links
```

## Scrape Transfer News

```markdown
## transfermarkt-transfers

1. [goto] https://www.transfermarkt.com/transfers/transfermarkt-filter/ansicht/ajax
2. [wait] 3 seconds
3. [scrape] transfer listings, player names, clubs, fees
4. [save] to Assets/Transfers with wiki-links
```

## Scrape Player Transfers

```markdown
## transfermarkt-player-transfers

1. [goto] https://www.transfermarkt.com/{player-name}/leistungsdaten/verein/{club-id}
2. [wait] 3 seconds
3. [scrape] transfer history, dates, clubs, fees
4. [save] to Assets/Transfers with wiki-links
```

## URL Patterns
- Article: `https://www.transfermarkt.com/{slug}`
- Section: `https://www.transfermarkt.com/{section}`
- Player Profile: `https://www.transfermarkt.com/{player-name}/profile/{id}`
- Club Profile: `https://www.transfermarkt.com/{club-name}/startseite/verein/{id}`
- Transfers: `https://www.transfermarkt.com/transfers/transfermarkt-filter/ansicht/ajax`