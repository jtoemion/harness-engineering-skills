# FIFA.com - Navigation Recipes

## URL Patterns
- Article: `https://www.fifa.com/{slug}`
- News: `https://www.fifa.com/news`
- Tournaments: `https://www.fifa.com/tournaments`
- Rankings: `https://www.fifa.com/world-rankings`

## Available Recipes
## fifa-news

1. [goto] https://www.fifa.com/news
2. [wait] 3 seconds
3. [extract] article links

## fifa-rankings

1. [goto] https://www.fifa.com/world-rankings
2. [wait] 3 seconds
3. [scrape] rankings table

## fifa-tournaments

1. [goto] https://www.fifa.com/tournaments
2. [wait] 3 seconds
3. [extract] tournament cards