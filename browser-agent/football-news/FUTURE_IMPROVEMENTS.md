# Future Improvements — Skipped

> Documented: 2026-04-27
> Reason: Low value / High complexity

These improvements were evaluated but deemed not worth implementing now. Documented here for future consideration if needs change.

---

## 1. Topic-Scoped Credibility

**Proposal:** Track per-source credibility by topic (transfer, injury, contract).

```yaml
# In Fabrizio-Romano.md
credibility_transfer: 91.2
credibility_injury: 68.4
credibility_contract: 88.0
```

**Why Skip:**
- Adds significant complexity to `credibility.py`
- Requires tagging every news file with topic type
- Marginal benefit: you'd still trust the overall score

**When to Revisit:**
- If you notice a specific source is reliable for transfers but not injuries
- If you want to weight sources differently per topic

---

## 2. Credibility Decay Over Time

**Proposal:** Weight recent resolutions (last 12 months) at 2x vs older ones.

```python
# Recent = 2x weight
if months_old < 12:
    weight = 2.0
else:
    weight = 1.0
```

**Why Skip:**
- Adds noise: a source's *overall* accuracy matters more than recency
- Would require storing resolution dates, add complexity
- Wilson score already handles small-sample dampening

**When to Revisit:**
- If a source was great in 2023 but terrible in 2025
- If you notice patterns of "going cold"

---

## 3. Score History

**Proposal:** Track how a file's score changes over time.

```yaml
# score-history.yaml
file.md:
  - date: 2026-04-26
    score: 65
  - date: 2026-04-27
    score: 72  # Upgraded after corroboration
```

**Why Skip:**
- Requires tracking mtime changes
- Useful for retrospectives but not core workflow
- Incremental scoring addresses the main performance concern

**When to Revisit:**
- If you want to analyze "which stories upgraded after being corroborated"

---

## 4. Personal Interest Weighting

**Proposal:** Boost scores for clubs/leagues you care about.

```yaml
personal_interest:
  clubs: ["Manchester-City", "Arsenal-FC"]
  leagues: ["Premier-League", "Champions-League"]
  interest_multiplier: 1.3
```

**Why Skip:**
- Adds complexity for marginal gain
- You can manually sort/filter by entities you care about
- Can add later as simple filter

**When to Revisit:**
- If you want automatic sorting by "your teams"

---

## 5. Smooth Time Decay (Bucket → Continuous)

**Current:** Bucket-based (today=10, yesterday=8, 2-3 days=6, 4+ days=2)

**Proposed:** Continuous decay `score = 10 * (0.85 ** days_old)`

**Why Skip:**
- Already implemented in v4 as continuous decay
- Bucket is simpler and sufficient

**Status:** ✓ Already done in score.py v4

---

## 6. Incremental Scoring

**Proposal:** Only re-score files modified since last run.

**Why Skip:**
- Already implemented in v4 with mtime cache
- At 50+/day you'll hit 1000 in ~20 days

**Status:** ✓ Already done in score.py v4

---

## Priority Decision Framework

Before adding any improvement, evaluate:

| Factor | Score |
|--------|-------|
| Value added | High/Medium/Low |
| Complexity | Low/Medium/High |
| Dependencies | What else needs to change? |

**Rule:**
- DO if value=High and complexity=Low
- CONSIDER if value=High and complexity=Medium
- SKIP if complexity=High regardless of value (unless blocking another DO)
- LATER if value=Medium, complexity=Low

---

## Implemented Instead

| Feature | File | Version |
|---------|------|---------|
| Story threading | Frontmatter `story_id`, `story_stage` | v4 |
| Multi-source corroboration | `score.py` | v4 |
| Incremental scoring | mtime cache | v4 |
| Alias normalization | `ALIASES` dict | v4 |
| Templater template | `Knowledgebase/tpl-football-news.md` | — |
| Entity heat tracking | `entity_heat.py` | — |
| Wilson credibility | `credibility.py` | — |