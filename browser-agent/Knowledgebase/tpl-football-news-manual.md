# Football News Note Template

Use this template when creating new news files. For Templater automation, see `tpl-football-news.md`.

## Quick Start

1. Copy this template to new file: `YYYY-MM-DD-{topic}-{source}.md`
2. Fill in frontmatter (required fields)
3. Write summary (required)
4. Add to Obsidian vault

## Template

```yaml
---
type: news
date: YYYY-MM-DD
source: SOURCE_NAME
url: https://example.com/article
processed: true|false
entities:
  - "[[Entity1]]"
  - "[[Entity2]]"
tags: [tag1, tag2, tag3]
story_id: entity-entity-YYYY-MM-DD  # optional: groups related stories
story_stage: rumor|interest|talks|offer|confirmed|collapsed  # optional: for transfers
rumor_id: entity-entity-YYYY-MM-DD  # optional: for rumor-type files
resolution_status: pending|confirmed|false|expired  # for rumors only
resolution:  # for confirmed/denied rumors: confirmed|false|expired
resolved_date: YYYY-MM-DD  # optional
resolved_by: [[ConfirmationFile]]  # optional: link to confirmation article
---

# {Source} — {Date}

## Summary

{Wikilink every entity mentioned: clubs, players, managers, competitions}

## Background

{Optional: context, history, quotes}

## Key Details

| Field | Value |
|-------|-------|
| Source | {source} |
| Date | {date} |
| Story Stage | {stage} |

## Dataview Queries

### Timeline for this story
```dataview
TABLE date, source, story_stage, resolution
FROM "entities/news"
WHERE story_id = "ENTITY-ENTITY-YYYY-MM-DD"
SORT date ASC
```

### Pending rumors
```dataview
LIST
FROM "entities/news"
WHERE resolution_status = "pending"
SORT date DESC
```

### By source
```dataview
LIST
FROM "entities/news"
WHERE source = "SOURCE_NAME"
SORT date DESC
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `news` |
| `date` | string | `YYYY-MM-DD` |
| `source` | string | Journalist/source name |
| `url` | string | Full URL to article |
| `processed` | string | `true` after processed |
| `entities` | array | Wikilinked entities |
| `tags` | array | Tags |

## Optional Fields

| Field | Use | Description |
|-------|-----|-------------|
| `story_id` | Transfers | Groups related stories: `player-club-YYYY-MM-DD` |
| `story_stage` | Transfers | Stage: rumor→interest→talks→offer→confirmed→collapsed |
| `rumor_id` | Rumors | Unique ID: `player-club-YYYY-MM-DD` |
| `resolution_status` | Rumors | pending/confirmed/false/expired |
| `resolution` | Rumors | Final status |
| `resolved_date` | Rumors | When resolved |
| `resolved_by` | Rumors | Link to confirmation article |

## Story Stage Flow

```
rumor → interest → talks → offer → confirmed
                               ↓
                            collapsed (deal fell through)
```

## Entity Wikilinking

Every named entity MUST be wikilinked:

- Clubs: `[[Manchester-City]]`, `[[Arsenal-FC]]`
- Players: `[[Erling-Haaland]]`, `[[Bukayo-Saka]]`
- Managers: `[[Pep-Guardiola]]`, `[[Mikel-Arteta]]`
- Competitions: `[[Premier-League]]`, `[[Champions-League]]`
- Concepts: `[[Title-Race]]`, `[[Relegation-Battle]]`

## File Naming

Format: `YYYY-MM-DD-{topic}-{source}.md`

Examples:
- `2026-04-26-haaland-city-renew.md`
- `2026-04-26-arsenal-top-pl.md`
- `2026-04-26-bayern-real-madrid-ucl.md`
- `2026-04-26-mbappe-real-confirmed.md`