# BBC Sport - Domain Skill

## Source
- **URL:** https://www.bbc.com/sport/football
- **Source Type:** News aggregator
- **Category:** Football news

## Article Selectors

### Primary (working)
```css
a[href*="/sport/football/articles/"]
```

### Fallback
```css
a[href*="/sport/football/"]
```

### Content Container
```css
article, .article-body, .story-body, [data-component="article-body"]
```

## Navigation

### Homepage
1. Go to `https://www.bbc.com/sport/football`
2. Wait for page load (3s)
3. Select articles using primary selector

### Pagination
- BBC uses infinite scroll - no pagination needed
- First 15 links usually contain quality articles

## Filter Notes

### BBC-Specific Patterns (OUT)
- `/scores-fixtures` - scores page
- `/tables` - league tables
- `/scorers` - top scorers

### BBC Article URL Pattern
```
https://www.bbc.com/sport/football/articles/{slug}
```

## Content Extraction

### Title
```css
h1
```

### Author
```css
[rel="author"], .author-name
```

### Date
```css
time[datetime], .published
```

### Body
```css
article p, .article-body p, .story-body p
```

## Status
- **Tested:** 2026-04-24
- **Working:** Yes
- **Last Updated:** 2026-04-24