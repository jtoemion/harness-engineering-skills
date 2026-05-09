# WhoScored - Navigation Recipes

## Scrape Match Stats

```markdown
## whoscored-match-stats

1. [goto] https://www.whoscored.com/Matches
2. [wait] 3 seconds
3. [extract] links matching a[href*="/Matches/"]
4. [filter] remove pagination links (/Matches?page=)
5. [scrape] for each match, extract date, teams, score, competition
6. [filter] apply match_signals.yaml
7. [save] to Assets/Matches with wiki-links
```

## Scrape Player Ratings

```markdown
## whoscored-player-ratings

1. [goto] https://www.whoscored.com/Players
2. [wait] 3 seconds
3. [extract] links matching a[href*="/Players/"]
4. [filter] remove player search links (/Players?search=)
5. [scrape] for each player, extract name, team, position, rating
6. [filter] apply player_signals.yaml
7. [save] to Assets/Players with wiki-links
```

## Scrape Match Details

```markdown
## whoscored-match-details

1. [goto] https://www.whoscored.com/Matches/{match-id}/{slug}
2. [wait] 4 seconds
3. [scrape] match centre: possession, shots, passes, tackles, ratings
4. [extract] player stats table
5. [save] to Assets/Matches/{match-id} with wiki-links
```

## URL Patterns
- Article: `https://www.whoscored.com/Articles/{slug}`
- Match: `https://www.whoscored.com/Matches/{match-id}/{slug}`
- Player: `https://www.whoscored.com/Players/{player-id}/{slug}`
- Team: `https://www.whoscored.com/Teams/{team-id}/{slug}`
- League: `https://www.whoscored.com/{league}/Standings`