# Fotbollskanalen - Navigation Recipes

## Scrape Swedish Football News

```markdown
## fotbollskanalen-news

1. [goto] https://www.fotbollskanalen.se/
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/artikel/"]
4. [scrape] for each link, extract title, date, author, content
5. [save] to Assets/News/fotbollskanalen with wiki-links
```

## Scrape Allsvenskan News

```markdown
## fotbollskanalen-allsvenskan

1. [goto] https://www.fotbollskanalen.se/allsvenskan
2. [wait] 3 seconds
3. [extract] all article links
4. [scrape] for each link, extract title, date, author, content
5. [save] to Assets/News/fotbollskanalen/allsvenskan with wiki-links
```

## Scrape Damallsvenskan News

```markdown
## fotbollskanalen-damallsvenskan

1. [goto] https://www.fotbollskanalen.se/damallsvenskan
2. [wait] 3 seconds
3. [extract] all article links
4. [scrape] for each link, extract title, date, author, content
5. [save] to Assets/News/fotbollskanalen/damallsvenskan with wiki-links
```

## Scrape European Leagues

```markdown
## fotbollskanalen-europa

1. [goto] https://www.fotbollskanalen.se/europa
2. [wait] 3 seconds
3. [extract] all article links
4. [scrape] for each link, extract title, date, author, content
5. [save] to Assets/News/fotbollskanalen/europa with wiki-links
```

## Scrape Videos

```markdown
## fotbollskanalen-video

1. [goto] https://www.fotbollskanalen.se/video
2. [wait] 3 seconds
3. [extract] all links matching a[href*="/video/"]
4. [scrape] for each link, extract title, date, duration, description
5. [save] to Assets/News/fotbollskanalen/video with wiki-links
```

## URL Patterns
- Homepage: `https://www.fotbollskanalen.se/`
- Article: `https://www.fotbollskanalen.se/artikel/{slug}`
- Section (Nyheter): `https://www.fotbollskanalen.se/nyheter`
- Section (Allsvenskan): `https://www.fotbollskanalen.se/allsvenskan`
- Section (Damallsvenskan): `https://www.fotbollskanalen.se/damallsvenskan`
- Section (Euro ligor): `https://www.fotbollskanalen.se/europa`
- Video: `https://www.fotbollskanalen.se/video/{slug}`