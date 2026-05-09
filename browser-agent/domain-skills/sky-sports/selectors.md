# Sky Sports - Domain Skill

## Source
- **URL:** https://www.skysports.com/football
- **Source Type:** Sports news outlet
- **Category:** Football news

## Article Selectors

### Primary (working)
```css
.news-list__link, .news-block a, h2 a[href*="/football/"], h3 a[href*="/football/"]
```

### Fallback
```css
.sdc-news-item a, a[href*="/football/"]
```

### Content Container
```css
.article, .news-article, .sdc-news-article, .article-body
```

## Navigation

### Homepage
1. Go to `https://www.skysports.com/football`
2. Wait for page load (3s)
3. Select articles using primary selector
4. Filter: only grab links containing `/football/` and not navigation

## Filter Notes

### Sky-Specific Patterns (OUT)
- Navigation links (team names like "Arsenal", "Liverpool")
- Score widgets
- Betting tips

### Sky Sports Article URL Pattern
```
https://www.skysports.com/football/{slug}
```

## Content Extraction

### Title
```css
h1, .news-title
```

### Author
```css
.author, .byline, [rel="author"]
```

### Date
```css
time, .date-published, .timestamp
```

### Body
```css
article p, .news-article p, .article-content p
```

## Status
- **Tested:** 2026-04-24
- **Working:** Yes (needs selector refinement for nav links)
- **Last Updated:** 2026-04-24