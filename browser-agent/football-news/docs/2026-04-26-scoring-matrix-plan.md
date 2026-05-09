# Football News Scoring Matrix Implementation Plan

> **For the next session: Use executing-plans to implement this plan task-by-task.**

**Goal:** Create a weighted scoring system for football news that rates each news item on multiple dimensions. The system should output a score (0-100) for each news file and help prioritize content quality.

**Architecture:** Python script that reads all news files in the vault, analyzes each against weighted metrics, outputs scored results. Uses YAML frontmatter + content analysis.

**Tech Stack:** Python, PyYAML, basic NLP (no external AI - rule-based scoring)

---

## Background: Why Scoring Matters

Current state: 51 news files scraped in one session with no quality differentiation.

Problems:
1. Some news is BREAKING (high value), some is OLD/GOSSIP (low value)
2. No way to filter by IMPORTANCE vs NOISE
3. Can't identify DUPPLICATES reliably
4. No way to prioritize what to READ vs SKIP

Need scoring to:
- Help user find HIGH VALUE news quickly
- Filter out low-quality gossip/rumors
- Enable "show me top 10 news" queries
- Track news TRENDING over time

---

## Task 1: Define Scoring Metrics (Weight Research)

### Core Metrics with Weights

| # | Metric | Weight | Rationale |
|---|-------|-------|----------|
| 1 | **Source Authority** | 25% | Fabrizio Romano > random blog |
| 2 | **Entity Impact** | 20% | Big clubs > small leagues |
| 3 | **News Type** | 15% | Breaking > Rumor > Opinion |
| 4 | **Recency** | 10% | Today > Yesterday > Old |
| 5 | **Engagement Signal** | 10% | Multiple sources = validated |
| 6 | **Content Depth** | 10% | Full article > Headline only |
| 7 | **Uniqueness** | 5% | Original > Reposted |
| 8 | **Wikilink Density** | 5% | More entities = richer |

**Total: 100%**

### Detailed Metric Definitions

#### 1. Source Authority (25 points max)
```yaml
- Tier 1 (25): Fabrizio Romano, David Ornstein, The Athletic, BBC, Sky Sports
- Tier 2 (20): Teamtalk, CaughtOffside, FootballInsider, Molodo
- Tier 3 (15): Standard blogs (90min, Goal, ESPN)
- Tier 4 (10): Smaller aggregators
- Tier 5 (5): Unknown/unverified sources
```

#### 2. Entity Impact (20 points max)
```yaml
# Based on entity prominence
- Champions League/Major League (20): Real Madrid, Man City, Bayern, PSG, Arsenal
- Top Premier League (18): Man United, Liverpool, Chelsea, Newcastle
- Mid-tier European (15): Juventus, Atletico, Napoli, Dortmund
- Other European (10): Lille, Lyon, Roma
- Smaller leagues (5): MLS, J-League, Saudi League
```

#### 3. News Type (15 points max)
```yaml
- Breaking/Confirmed (15): Official, "Here we go", Medical update
- Transfer Update (12): Active negotiation, bid accepted
- Match Result (10): Final score, major incident
- Opinion/Analysis (8): Tactical breakdown
- Rumor/Gossip (3): "could sign", "interested"
- Opinion Only (2): Pundit takes
```

#### 4. Recency (10 points max)
```yaml
# Based on date in frontmatter vs current date
- Today (10)
- Yesterday (8)
- 2 days ago (6)
- This week (4)
- Older (2)
- Unknown (0)
```

#### 5. Engagement Signal (10 points max)
```yaml
# Multiple independent sources reporting same news
- 3+ sources (10)
- 2 sources (7)
- 1 source (4)
- Not applicable (5)  # For match results
```

#### 6. Content Depth (10 points max)
```yaml
- Full article with quotes (10): Multiple paragraphs + quotes
- Substantial (7): Multiple paragraphs, no quotes
- Brief (4): Single paragraph summary
- Headline only (1): Just title
```

#### 7. Uniqueness (5 points max)
```yaml
# Check if same topic already in vault
- No duplicate found (5)
- Similar topic, different angle (3)
- Duplicate content (0)
```

#### 8. Wikilink Density (5 points max)
```yaml
# Count wikilinks in content / total entities mentioned
- 5+ valid wikilinks (5)
- 3-4 wikilinks (4)
- 1-2 wikilinks (2)
- No wikilinks (0)
```

---

## Task 2: Create Scoring Script Architecture

### File Structure
```
football-news/
├── SKILL.md                    # Updated with scoring reference
├── score_news.py               # Main scoring script
├── scorer/
│   ├── __init__.py
│   ├── weights.py            # Weight configuration
│   ├── source_tiers.py       # Source authority mapping
│   ├── entity_impacts.py     # Entity impact scores
│   ├── news_analyzer.py    # Core analysis logic
│   └── output_formatter.py # Results output
├── tests/
│   └── test_scorer.py    # Tests
└── docs/
    └── SCORING_LOGIC.md  # This document
```

### Scoring Workflow

```
Input: News vault directory
  ↓
1. Scan all .md files in entities/news/
  ↓
2. Parse frontmatter (date, source, url, entities, tags)
  ↓
3. Parse content for depth + wikilinks
  ↓
4. For each metric:
   - Extract value
   - Apply weight
   - Add to score
  ↓
5. Calculate total (0-100)
  ↓
6. Output results:
   - Individual file scores
   - Top 10 highest scored
   - Score distribution
   - Quality flags (score < 30 = low)
```

---

## Task 3: Implementation Details

### scorer/weights.py
```python
WEIGHTS = {
    "source_authority": 0.25,
    "entity_impact": 0.20,
    "news_type": 0.15,
    "recency": 0.10,
    "engagement": 0.10,
    "content_depth": 0.10,
    "uniqueness": 0.05,
    "wikilink_density": 0.05,
}

MAX_SCORES = {
    "source_authority": 25,
    "entity_impact": 20,
    "news_type": 15,
    "recency": 10,
    "engagement": 10,
    "content_depth": 10,
    "uniqueness": 5,
    "wikilink_density": 5,
}
```

### scorer/source_tiers.py
```python
# Map source names (lowercase) to tier
SOURCE_TIERS = {
    # Tier 1 (25) - Top tier journalists and outlets
    "fabrizio-romano": 25, "david-ornstein": 25,
    "the-athletic": 25, "bbc": 25, "bbc-sport": 25,
    "sky-sports": 25, "sky-football": 25,
    
    # Tier 2 (20) - Reliable football news
    "teamtalk": 20, "caughtoffside": 20,
    "football-insider": 20, "molodo": 20,
    
    # Tier 3 (15) - Standard sports media
    "marca": 15, "as": 15, "lequipe": 15,
    "espn": 15, "goal": 15, "90min": 15,
    
    # Tier 4 (10) - Smaller/aggregators
    "yahoo-sports": 10, "sports-yahoo": 10,
    "one-football": 10,
    
    # Default for unknown (5)
    "unknown": 5,
}

def get_source_score(source_name: str) -> int:
    """Get tier score for a source name."""
    normalized = source_name.lower().strip()
    return SOURCE_TIERS.get(normalized, SOURCE_TIERS["unknown"])
```

### scorer/entity_impacts.py
```python
# Static tier mapping + dynamic fallback (vault appearances)
TIER_1_CHAMPIONS = {
    "real-madrid", "man-city", "bayern-munich", "psg", "arsenal",
    "chelsea", "man-united", "liverpool", "barcelona",
}

TIER_2_TOP = {
    "newcastle", "tottenham", "atletico-madrid", "juventus",
    "napoli", "dortmund", "inter-milan", "milan",
}

TIER_3_MID = {
    "roma", "lazio", "fiorentina", "marseille", "lyon",
    "lille", "monaco", "leverkusen", "RB-leipzig",
}

# Fallback: Count vault appearances for unknown entities
ENTITY_VAULT_COUNT = {}  # Populated at runtime

def get_entity_score(entity: str) -> int:
    """Get impact score for an entity."""
    normalized = entity.lower().strip().replace(" ", "-")
    
    # Check static tiers first
    if normalized in TIER_1_CHAMPONS:
        return 20
    if normalized in TIER_2_TOP:
        return 18
    if normalized in TIER_3_MID:
        return 15
    
    # Dynamic fallback: vault appearances
    appearances = ENTITY_VAULT_COUNT.get(normalized, 0)
    if appearances >= 10:
        return 12
    elif appearances >= 5:
        return 8
    else:
        return 5  # Default for unknown

def set_vault_counts(counts: dict):
    """Set vault appearance counts from scan."""
    global ENTITY_VAULT_COUNT
    ENTITY_VAULT_COUNT = counts
```

### scorer/news_analyzer.py
Core analysis:
- Parse frontmatter with yaml.safe_load
- Count wikilinks with regex `\[\[([^\]]+)\]\]`
- Calculate content depth by paragraph count
- Check uniqueness by title match (normalized)

```python
import re
import yaml
from datetime import datetime
from pathlib import Path

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from file content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def get_wikilink_count(content: str) -> int:
    """Count wikilinks in content."""
    return len(re.findall(r'\[\[([^\]]+)\]\]', content))

def get_content_depth(content: str) -> int:
    """Score content depth by paragraph count."""
    # Remove frontmatter for pure content
    if content.startswith("---"):
        parts = content.split("---", 2)
        content = parts[2] if len(parts) >= 3 else ""
    
    # Count non-empty paragraphs (separated by blank lines)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    if len(paragraphs) >= 5:
        return 10
    elif len(paragraphs) >= 3:
        return 7
    elif len(paragraphs) >= 1:
        return 4
    else:
        return 1

def get_recency_score(date_str: str) -> int:
    """Score recency based on date vs today."""
    if not date_str:
        return 0
    
    try:
        # Parse date (supports YYYY-MM-DD)
        news_date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
        today = datetime.now()
        delta = (today - news_date).days
        
        if delta <= 0:
            return 10
        elif delta == 1:
            return 8
        elif delta <= 2:
            return 6
        elif delta <= 7:
            return 4
        else:
            return 2
    except:
        return 0

def check_duplicate(new_title: str, existing_titles: list) -> int:
    """Check duplicate by normalized title match."""
    # Normalize: lowercase, remove dates, remove punctuation
    normalized = re.sub(r'[\d-]', '', new_title.lower())
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = ' '.join(normalized.split())
    
    for existing in existing_titles:
        existing_norm = re.sub(r'[\d-]', '', existing.lower())
        existing_norm = re.sub(r'[^\w\s]', '', existing_norm)
        existing_norm = ' '.join(existing_norm.split())
        
        # Simple fuzzy match: if >70% similar
        if len(normalized) >= 10:
            matching = sum(1 for a, b in zip(normalized, existing_norm) if a == b)
            similarity = matching / max(len(normalized), len(existing_norm))
            if similarity > 0.7:
                return 0  # Duplicate
    
    return 5  # No duplicate
```
$ python score_news.py --vault C:/Users/jtoem/Assets/News/football

=================================================================
FOOTBALL NEWS SCORING REPORT
=================================================================
Files Scanned: 51
Date: 2026-04-26

TOP 10 HIGHEST SCORED NEWS:
------------------------------------------------------
#1 | 94 | [P1] Arsenal top PL | arsenal-top-pl
#2 | 92 | [P1] Bayern beat Real UCL | bayern-real-ucl
#3 | 89 | [P1] Barcelona title | barcelona-la-liga
...

SCORE DISTRIBUTION:
------------------------------------------------------
90-100: ████ 12
80-89:  ██████ 18
70-79:  ██████████ 22
60-69:  ███ 6
50-59:  █ 1
<50:    ██ 2

LOW QUALITY FLAGS (score < 30):
------------------------------------------------------
28 | Rumor: Newcastle Rashford | rashford-newcastle
25 | Old: PL Standings | pl-standings
```

### JSON Output (for programmatic use)
```json
{
  "scan_date": "2026-04-26",
  "files_scanned": 51,
  "results": [
    {
      "filename": "2026-04-26-arsenal-top-pl.md",
      "total_score": 94,
      "metrics": {
        "source_authority": 25,
        "entity_impact": 18,
        ...
      },
      "grade": "A+",
      "quality_flag": null
    }
  ],
  "summary": {
    "average_score": 78.3,
    "median_score": 82,
    "top_10": [...]
  }
}
```

---

## Task 5: Integration with Skill

Update SKILL.md to include scoring reference:

```markdown
## Optional: Scoring System

Run the scorer to prioritize news:

    python score_news.py --vault C:/Users/jtoem/Assets/News/football

Output shows:
- Individual scores (0-100)
- Top 10 highest scored
- Quality flags (<30 = low)
```

---

## Execution Plan

### Task 1: Create scorer directory structure
- Create: `scorer/__init__.py`
- Create: `scorer/weights.py`
- Create: `scorer/source_tiers.py`
- Create: `scorer/entity_impacts.py`
- Create: `scorer/news_analyzer.py`
- Create: `scorer/output_formatter.py`

### Task 2: Create main script
- Create: `score_news.py`

### Task 3: Create tests
- Create: `tests/test_scorer.py`

### Task 4: Run and verify
- Run scorer on vault
- Review scores for sanity
- Adjust weights if needed

### Task 5: Update SKILL.md
- Add scoring reference to football-news skill

---

## Self-Review Checklist (Before Implementation)

- [ ] Weights add up to 100%? YES (25+20+15+10+10+10+5+5 = 100)
- [ ] Each metric has clear scoring criteria? YES
- [ ] No circular dependencies? YES (only frontmatter/content parsing)
- [ ] Easy to adjust weights? YES (all in weights.py)
- [ ] Output useful for user? YES (top 10, quality flags)
- [ ] Handles edge cases? (no date, unknown source, empty content)

## Edge Cases to Handle (Updated)

1. Missing frontmatter → DEFAULT scores with INCOMPLETE flag (warnings in output)
2. Unknown source → TIER_4 default (5 pts)
3. No wikilinks → 0 for that metric
4. Future date → treat as today
5. Missing date in frontmatter → recency = 0, flag as UNDATED
6. Empty content → content_depth = 1 (minimum)
7. Title-only content → get_content_depth detects 1 paragraph → score 4

## Grade Boundaries (Adjustable)
- A+: 90-100
- A: 85-89
- B+: 80-84
- B: 70-79
- C: 50-69
- D: 30-49
- F: <30 (FLAG AS LOW QUALITY)

---

## Success Criteria

1. All 51 news files get scored (0-100)
2. Top news makes sense (Fabrizio sources rank high)
3. Runs in <10 seconds
4. Output is actionable (top 10 + quality flags)
5. Easy to modify weights if needed