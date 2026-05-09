# Agent Workflow — Football News Scraping

## Tool Order

When scraping a news article:

1. **is_duplicate()** → Check if already scraped
2. **score_article()** → Get importance score before saving
3. **normalize_entities()** → Ensure consistent wikilinks
4. **save_news_file()** → Write to vault
5. **update_entity_heat()** → Increment mention counts

## Rumor Resolution Flow

When a rumor is confirmed/denied:

1. **track_rumor_resolution()** → Mark original rumor as resolved
2. **update_source_credibility()** → Recalculate source credibility

## Story Tracking

When scraping transfer stories:

1. **get_story_timeline()** → See existing articles in story
2. Use same `story_id` for all related articles
3. Update `story_stage` as story progresses: rumor → interest → talks → offer → confirmed/collapsed

## Examples

```python
# Scraping a new article
entities = normalize_entities(["Man City", "Haaland"])
if is_duplicate(url):
    return "already scraped"
score = score_article(content, source, date, entities, tags)
path = save_news_file(content, source, date, entities, tags, url, score, story_id="haaland-city-2026")
update_entity_heat(entities)

# Resolving a rumor
track_rumor_resolution("haaland-city-2026-04-26", "confirmed", resolved_by="2026-04-27-haaland-city-renew.md")
update_source_credibility("FabrizioRomano")
```

## Story Stages

| Stage | Meaning |
|-------|---------|
| rumor | Initial speculation |
| interest | Club actively interested |
| talks | Negotiations started |
| offer | Formal offer made |
| confirmed | Deal completed |
| collapsed | Deal fell through |

## Key Fields

### News File Frontmatter
- `type`: Always `news`
- `date`: `YYYY-MM-DD`
- `source`: Journalist/source name
- `url`: Full article URL
- `entities`: Wikilinked entities `[[Entity-Name]]`
- `tags`: Array of tags
- `story_id`: Groups related transfer stories
- `story_stage`: Current stage of transfer story
- `rumor_id`: Unique rumor identifier
- `resolution_status`: pending/confirmed/false/expired

## Entity Normalization

Entities are normalized using `registry.yaml` aliases:
- "Man City" → `[[Manchester-City]]`
- "Haaland" → `[[Erling-Haaland]]`
- "PL" → `[[Premier-League]]`

Always use `normalize_entities()` before saving to ensure consistent wikilinks.

## Source Tiers

| Tier | Sources |
|------|---------|
| T1 | FabrizioRomano, DavidOrnstein, BBC, Sky, TheAthletic |
| T2 | Marca, Goal, Teamtalk, CaughtOffside |
| T3 | All others |
