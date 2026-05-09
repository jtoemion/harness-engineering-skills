# UEFA - Navigation Recipes

## Scrape Latest News

```markdown
## uefa-news

1. [goto] https://www.uefa.com
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/news/"]
4. [filter] remove section links (tickets, login, video)
5. [scrape] for each article, extract title, summary, date, category
6. [save] to Assets/News/uefa with wiki-links
```

## Scrape Competition News

```markdown
## uefa-competition-news

1. [goto] https://www.uefa.com/{competition}/news
2. [wait] 3 seconds
3. [scrape] articles by competition (champions-league, euro, nations-league)
4. [filter] apply news_signals.yaml
5. [save] to Assets/News/uefa with wiki-links
```

## Scrape Match Results

```markdown
## uefa-match-results

1. [goto] https://www.uefa.com/{competition}/matches
2. [wait] 3 seconds
3. [scrape] match data: date, teams, score, venue
4. [extract] match detail links
5. [scrape] goal scorers, cards, stats
6. [save] to Assets/Football/matches with wiki-links
```

## Scrape Player Profiles

```markdown
## uefa-player-profile

1. [goto] https://www.uefa.com/players
2. [wait] 3 seconds
3. [search] player by name
4. [scrape] profile: nationality, club, statistics
5. [save] to Assets/Football/players with wiki-links
```

## Scrape Team Information

```markdown
## uefa-team-profile

1. [goto] https://www.uefa.com/teams
2. [wait] 2 seconds
3. [scrape] team squad: players, positions, nationality
4. [save] to Assets/Football/teams with wiki-links
```

## URL Patterns
- Home: `https://www.uefa.com`
- Competition: `https://www.uefa.com/{competition}`
- Match: `https://www.uefa.com/{competition}/match/{id}`
- Player: `https://www.uefa.com/players/{id}/{slug}`
- Team: `https://www.uefa.com/teams/{id}/{slug}`
- News: `https://www.uefa.com/news`
- Results: `https://www.uefa.com/{competition}/matches`