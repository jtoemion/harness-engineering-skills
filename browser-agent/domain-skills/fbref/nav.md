# FBref - Navigation Recipes

## Scrape Player Statistics

```markdown
## fbref-player-stats

1. [goto] https://fbref.com/en/players
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/en/players/"]
4. [scrape] for each player, extract name, position, age, apps, minutes
5. [save] to Assets/Football/players with wiki-links
```

## URL Patterns
- Article: `https://fbref.com/en/players/{id}/{slug}`
- Stats: `https://fbref.com/en/players/{id}/{slug}/stats`
- Match: `https://fbref.com/en/matches/{id}/{slug}`