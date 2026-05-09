# Sofascore - Navigation Recipes

## Live Scores

```markdown
## sofascore-live-scores

1. [goto] https://www.sofascore.com/
2. [wait] 3 seconds
3. [scrape] all live matches with scores, teams, time
```

## Match Details

```markdown
## sofascore-match

1. [goto] https://www.sofascore.com/football/match/{match_id}
2. [wait] 2 seconds
3. [scrape] match events, stats, lineups, score
```

## Player Profile

```markdown
## sofascore-player

1. [goto] https://www.sofascore.com/football/player/{player_slug}/{player_id}
2. [wait] 2 seconds
3. [scrape] player statistics, career info, current team
```

## Team Profile

```markdown
## sofascore-team

1. [goto] https://www.sofascore.com/football/team/{team_slug}/{team_id}
2. [wait] 2 seconds
3. [scrape] squad, statistics, fixtures
```

## Competition (League/Cup)

```markdown
## sofascore-competition

1. [goto] https://www.sofascore.com/football/competition/{competition_id}
2. [wait] 2 seconds
3. [scrape] standings, fixtures, top scorers
```

## URL Patterns
- Live Scores: `https://www.sofascore.com/`
- Match: `https://www.sofascore.com/football/match/{match_id}`
- Player: `https://www.sofascore.com/football/player/{player_slug}/{player_id}`
- Team: `https://www.sofascore.com/football/team/{team_slug}/{team_id}`
- Competition: `https://www.sofascore.com/football/competition/{competition_id}`