# ESPN Soccer - Domain Skill

## Source
- **URL:** https://www.espn.com/soccer
- **Source Type:** Sports news outlet
- **Category:** Football/Soccer news

## Article Selectors

### Primary (working)
```css
a[href*="/soccer/story/"], a[href*="/football/story/"]
```

### Fallback
```css
article a, .headline a, h2 a[href*="/soccer/"]
```

### Content Container
```css
article, .article-content, .story-body, .main-content
```

## Navigation

### Homepage
1. Go to `https://www.espn.com/soccer`
2. Wait for page load (3s)
3. Select articles using primary selector
4. Filter: only grab links containing `/soccer/story/`

## Filter Notes

### ESPN-Specific Patterns (OUT)
- Mixed sports (NFL, NBA, MLB) - use `/soccer/` filter
- Trackers: `/tracker/` in URL
- Rankings: `/rankings/`
- NFL content: `/nfl/` in URL

### ESPN Article URL Pattern
```
https://www.espn.com/soccer/story/_/id/{id}/{slug}
```

## Content Extraction

### Title
```css
h1, .article-headline
```

### Author
```css
.author-name, .byline, [rel="author"]
```

### Date
```css
time, .article-date, .timestamp
```

### Body
```css
article p, .article-content p, .story-body p
```

## Status
- **Tested:** 2026-04-24
- **Working:** Yes
- **Note:** Mixed sports homepage - need soccer-specific filter
- **Last Updated:** 2026-04-24