# StatsBomb - Navigation Recipes

## Scrape Player Statistics

```markdown
## statsbomb-player-stats

1. [goto] https://statsbomb.com/players
2. [wait] 3 seconds
3. [scrape] player cards with name, position, team, competition
4. [extract] player IDs and profile URLs
5. [save] to Assets/Football/players with wiki-links
```

## Scrape Match Data

```markdown
## statsbomb-match

1. [goto] https://statsbomb.com/matches
2. [wait] 3 seconds
3. [extract] match links and event data
4. [scrape] events, shots, passes, tackles
5. [save] to Assets/Football/matches with wiki-links
```

## URL Patterns
- Player: `https://statsbomb.com/players/{id}`
- Team: `https://statsbomb.com/teams/{id}`
- Match: `https://statsbomb.com/matches/{id}`
- Competition: `https://statsbomb.com/competitions/{id}`
