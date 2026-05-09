# Agent-callable tools for football news scraping
# Per-article operations only, no scan-all, lightweight per-operation

import json, yaml, re
from datetime import datetime, timedelta
from pathlib import Path
from math import sqrt
from difflib import SequenceMatcher

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
TRACKER_FILE = SKILL_ROOT / "football-news" / "news-tracker.json"
SCORE_CACHE_FILE = SKILL_ROOT / "football-news" / "score-cache.yaml"
REGISTRY_FILE = SKILL_ROOT / "entities" / "registry.yaml"

VAULT = Path("C:/Users/jtoem/Assets/News/football")
PERSONS = VAULT / "entities" / "Persons"
NEWS = VAULT / "entities" / "news"
HEAT_FILE = SKILL_ROOT / "football-news" / "entity-heat.json"


def _load_registry():
    """Load entity aliases from registry.yaml."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        data = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8")) or {}
        aliases = {}
        for section in ["_clubs", "_players", "_managers", "_competitions", "_nations"]:
            if section in data:
                for display, wikilink in data[section].items():
                    aliases[display.lower()] = wikilink
                    aliases[wikilink.lower()] = wikilink
        return aliases
    except:
        return {}


ALIASES = _load_registry()

ALIASES.update({
    "man city": "Manchester-City", "man-city": "Manchester-City", "mcity": "Manchester-City",
    "man united": "Manchester-United", "man-united": "Manchester-United", "munited": "Manchester-United",
    "arsenal": "Arsenal-FC", "tottenham": "Tottenham-Hotspur",
    "liverpool": "Liverpool-FC", "chelsea": "Chelsea-FC",
    "haaland": "Erling-Haaland", "erling": "Erling-Haaland",
    "saka": "Bukayo-Saka", "bukayo": "Bukayo-Saka",
    "mbappe": "Kylian-Mbappe", "kylian": "Kylian-Mbappe",
    "modric": "Luka-Modric", "vini": "Vinicius-Jr",
    "pep": "Pep-Guardiola", "guardiola": "Pep-Guardiola",
    "arteta": "Mikel-Arteta", "mikel": "Mikel-Arteta",
    "pl": "Premier-League", "premier league": "Premier-League",
    "ucl": "Champions-League", "champions league": "Champions-League",
})


def is_duplicate(article_url: str, article_title: str = "", article_date: str = "") -> bool:
    """Check if article already scraped."""
    if not article_url and not article_title:
        return False

    p = Path(TRACKER_FILE)
    if p.exists():
        try:
            tracker = json.loads(p.read_text())
        except:
            tracker = {"news": []}
    else:
        tracker = {"news": []}

    if article_url:
        for n in tracker["news"]:
            if n.get("url") == article_url:
                return True

    if article_title and article_date:
        for n in tracker["news"]:
            if n.get("title") == article_title and n.get("date") == article_date:
                return True

        entities_key = f"{article_title[:30]}_{article_date}"
        for n in tracker["news"]:
            if n.get("key") == entities_key:
                return True

    return False


def _normalize_entity(entity: str) -> str:
    """Normalize single entity to canonical wikilink."""
    if not entity:
        return entity
    clean = str(entity).lower().strip().replace("[[", "").replace("]]", "").strip()
    return ALIASES.get(clean, entity)


def normalize_entities(entities: list) -> list:
    """Normalize entity names to canonical wikilinks using aliases."""
    if not entities:
        return []
    return [_normalize_entity(e) for e in entities]


def _get_source_tier(source: str) -> int:
    """Get source tier (1, 2, or 3)."""
    if not source:
        return 3
    TIER1 = {"fabrizio-romano", "david-ornstein", "bbc", "sky", "the-athletic"}
    TIER2 = {"marca", "goal", "teamtalk", "caughtoffside"}
    s = source.lower().replace("-", "").replace(" ", "")
    if s in TIER1:
        return 1
    if s in TIER2:
        return 2
    return 3


def _get_reliability(source: str) -> int:
    """Get reliability score (0-30)."""
    return _get_source_tier(source) * 10


def _get_recency(date_str: str) -> int:
    """Continuous decay: 10 * 0.85^days_old."""
    if not date_str:
        return 0
    try:
        days = (datetime.now() - datetime.strptime(date_str[:10], "%Y-%m-%d")).days
        return int(10 * (0.85 ** days))
    except:
        return 0


def _get_news_type(content: str, tags: list) -> tuple:
    """Get news type score."""
    NEWS_TYPES = {
        "breaking": 25, "confirmed": 22, "transfer": 20,
        "result": 18, "update": 15, "analysis": 12,
        "opinion": 8, "rumor": 3, "gossip": 2,
    }
    content_lower = (content or "").lower()
    tags_lower = [t.lower() for t in (tags or [])]
    for t in tags_lower:
        if t in NEWS_TYPES:
            return NEWS_TYPES[t], t
    for kw, sc in [("breaking", 25), ("here we go", 25), ("confirmed", 22), ("transfer", 20),
                   ("result", 18), ("win", 18), ("update", 15), ("injury", 15), ("analysis", 12),
                   ("rumor", 3), ("interested", 3), ("gossip", 2)]:
        if kw in content_lower:
            return sc, kw
    return 5, "regular"


def _calc_corroboration(date: str, entities: list, source: str) -> int:
    """Calculate multi-source corroboration bonus."""
    if not date or not entities or not NEWS.exists():
        return 0

    try:
        file_date = datetime.strptime(date[:10], "%Y-%m-%d")
    except:
        return 0

    dates_to_check = [
        file_date.strftime("%Y-%m-%d"),
        (file_date - timedelta(days=1)).strftime("%Y-%m-%d"),
        (file_date + timedelta(days=1)).strftime("%Y-%m-%d"),
    ]

    tier_counts = {1: 0, 2: 0}
    for f in NEWS.glob("*.md"):
        if f.name.startswith("."):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1]) or {}
        except:
            continue
        if fm.get("date", "") not in dates_to_check:
            continue
        if fm.get("source") == source:
            continue
        file_ents = [_normalize_entity(e) for e in fm.get("entities", [])]
        if set(entities) & set(file_ents):
            tier = _get_source_tier(fm.get("source", ""))
            if tier in tier_counts:
                tier_counts[tier] += 1

    t1, t2 = tier_counts[1], tier_counts[2]
    if t1 >= 2:
        return 15
    if t1 >= 1 and t2 >= 1:
        return 8
    if t2 >= 2:
        return 5
    if t2 >= 1 and _get_source_tier(source) == 1:
        return 3
    return 0


def _get_story_bonus(story_id: str) -> int:
    """Bonus if part of active story."""
    if not story_id or not NEWS.exists():
        return 0
    for f in NEWS.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1]) or {}
            if fm.get("story_id") == story_id:
                stage = fm.get("story_stage", "")
                if stage in ("talks", "offer", "confirmed"):
                    return 3
                if stage == "interest":
                    return 2
        except:
            pass
    return 0


def score_article(article_content: str, source: str, date: str, entities: list, tags: list) -> dict:
    """Score a single article. Returns {score, grade, components, corroboration, recency}."""
    rel = _get_reliability(source)
    typ, reason = _get_news_type(article_content, tags or [])
    rec = _get_recency(date)
    norm_entities = normalize_entities(entities) if entities else []
    corroboration = _calc_corroboration(date, norm_entities, source)
    story_bonus = 0

    total = rel + typ + rec + 10 + corroboration + story_bonus
    grade = "A+" if total >= 90 else "A" if total >= 80 else "B+" if total >= 70 else "B" if total >= 60 else "C" if total >= 40 else "D" if total >= 20 else "F"

    return {
        "score": total,
        "grade": grade,
        "components": {
            "reliability": rel,
            "type": typ,
            "recency": rec,
            "uniqueness": 10,
            "corroboration": corroboration,
            "story": story_bonus,
        },
        "reason": reason,
        "corroboration": corroboration,
        "recency": rec,
    }


def _read_frontmatter(path: Path) -> dict:
    """Read YAML frontmatter from a markdown file."""
    if not path.exists():
        return {}
    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return yaml.safe_load(parts[1]) or {}
    except Exception:
        pass
    return {}


def _write_frontmatter(path: Path, fm: dict, body: str = None):
    """Write YAML frontmatter to a markdown file."""
    try:
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        if body is None:
            if content.startswith("---"):
                parts = content.split("---", 2)
                body = parts[2] if len(parts) >= 3 else ""
            else:
                body = content
        fm_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        path.write_text(f"---\n{fm_yaml}---\n{body}", encoding="utf-8")
    except Exception as e:
        raise e


def _slugify(text: str) -> str:
    """Create URL-safe slug."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def save_news_file(article_content: str, source: str, date: str, entities: list,
                   tags: list, url: str, score_data: dict, story_id: str = None,
                   story_stage: str = None, rumor_id: str = None, resolution_status: str = "pending") -> str:
    """Save article to vault with proper frontmatter. Returns file path."""
    if not NEWS.exists():
        NEWS.mkdir(parents=True, exist_ok=True)

    norm_entities = normalize_entities(entities) if entities else []

    if story_id:
        filename_base = _slugify(story_id)
    else:
        topic = url.split("/")[-1].split("?")[0][:30] if url else f"news-{date}"
        filename_base = f"{date}-{topic}"

    filename = f"{date}-{filename_base}.md"
    filepath = NEWS / filename

    counter = 1
    while filepath.exists():
        filename = f"{date}-{filename_base}-{counter}.md"
        filepath = NEWS / filename
        counter += 1

    wikilinked_entities = [f"[[{e}]]" for e in norm_entities]

    body = f"# {source} — {date}\n\n## Summary\n\n{article_content}\n\n## Key Details\n\n| Field | Value |\n|-------|-------|\n| Source | {source} |\n| Date | {date} |\n| Entities | {', '.join(wikilinked_entities)} |\n"

    fm = {
        "type": "news",
        "date": date,
        "source": source,
        "url": url,
        "processed": "true",
        "entities": wikilinked_entities,
        "tags": tags or [],
    }

    if story_id:
        fm["story_id"] = story_id
    if story_stage:
        fm["story_stage"] = story_stage
    if rumor_id:
        fm["rumor_id"] = rumor_id
        fm["resolution_status"] = resolution_status
    if score_data:
        fm["score"] = score_data.get("score", 0)
        fm["grade"] = score_data.get("grade", "")

    _write_frontmatter(filepath, fm, body)

    tracker = {"news": []}
    if TRACKER_FILE.exists():
        try:
            tracker = json.loads(TRACKER_FILE.read_text())
        except:
            pass
    key = url or f"{source}-{date}"
    tracker["news"].append({
        "key": key,
        "title": f"{source} — {date}",
        "date": date,
        "source": source,
        "entities": norm_entities,
        "added": datetime.now().isoformat()
    })
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(json.dumps(tracker, indent=2))

    return str(filepath)


def _load_heat() -> dict:
    """Load entity heat data."""
    if HEAT_FILE.exists():
        try:
            return json.loads(HEAT_FILE.read_text())
        except:
            pass
    return {}


def _save_heat(heat: dict):
    """Save entity heat data."""
    HEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEAT_FILE.write_text(json.dumps(heat, indent=2))


def update_entity_heat(entities: list) -> None:
    """Update mention counts for entities (lightweight, incremental)."""
    if not entities:
        return
    heat = _load_heat()
    norm = normalize_entities(entities)
    for e in norm:
        heat[e] = heat.get(e, 0) + 1
    _save_heat(heat)


def update_source_credibility(source_name: str) -> dict:
    """Update credibility for a source after scraping."""
    possible_names = [source_name]
    if " " in source_name:
        possible_names.append(source_name.replace(" ", "-"))
    if "-" in source_name:
        possible_names.append(source_name.replace("-", " "))

    person_file = None
    for name in possible_names:
        p = PERSONS / f"{name}.md"
        if p.exists():
            person_file = p
            break

    if not person_file:
        return {"error": f"Source not found: {source_name}"}

    fm = _read_frontmatter(person_file)

    confirmed = false = expired = pending = 0

    resolved_by_id = {}
    if NEWS.exists():
        for f in NEWS.glob("*.md"):
            if f.name.startswith("."):
                continue
            ffm = _read_frontmatter(f)
            if ffm.get("resolves"):
                resolved_by_id[ffm.get("resolves")] = f

    if NEWS.exists():
        source_norm = source_name.lower().replace(" ", "").replace("-", "")
        for f in NEWS.glob("*.md"):
            if f.name.startswith("."):
                continue
            ffm = _read_frontmatter(f)
            source_key = ffm.get("source", "")
            if source_key.lower().replace(" ", "").replace("-", "") != source_norm:
                continue
            if not ffm.get("rumor_id"):
                continue
            res_status = ffm.get("resolution_status", "pending")
            if res_status == "confirmed":
                confirmed += 1
            elif res_status == "false":
                false += 1
            elif res_status == "expired":
                expired += 1
            else:
                date_str = ffm.get("date", "")
                if date_str:
                    try:
                        art_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                        if (datetime.now() - art_date).days > 90:
                            expired += 1
                            ffm["resolution_status"] = "expired"
                            ffm["resolution"] = "expired"
                            ffm["resolved_date"] = datetime.now().strftime("%Y-%m-%d")
                            _write_frontmatter(f, ffm)
                        else:
                            pending += 1
                    except:
                        pending += 1
                else:
                    pending += 1

    resolved = confirmed + false
    if resolved == 0:
        credibility = 50.0
    else:
        p = confirmed / resolved
        z = 1.96
        n = resolved
        denominator = 1 + (z**2 / n)
        numerator = p + (z**2 / (2*n)) - z * sqrt((p * (1-p) / n) + (z**2 / (4 * n**2)))
        lower = numerator / denominator
        if pending > 0:
            pending_ratio = pending / (resolved + pending)
            pending_discount = 1 - (pending_ratio * 0.2)
        else:
            pending_discount = 1.0
        credibility = round(lower * pending_discount * 100, 1)

    fm["rumors_total"] = confirmed + false + expired + pending
    fm["rumors_confirmed"] = confirmed
    fm["rumors_false"] = false
    fm["rumors_expired"] = expired
    fm["rumors_pending"] = pending
    fm["credibility_score"] = credibility
    fm["credibility_updated"] = datetime.now().strftime("%Y-%m-%d")

    _write_frontmatter(person_file, fm)

    tier = fm.get("base_tier", 3)
    tier_label = f"T{tier}"

    return {
        "source": source_name,
        "tier": tier,
        "tier_label": tier_label,
        "score": credibility,
        "confirmed": confirmed,
        "false": false,
        "expired": expired,
        "pending": pending,
        "total": confirmed + false + expired + pending,
    }


def track_rumor_resolution(rumor_id: str, status: str, resolved_by: str = None) -> bool:
    """Mark rumor as confirmed/false/expired."""
    if status not in ["confirmed", "false", "expired"]:
        return False

    if not NEWS.exists():
        return False

    found = None
    source = None
    for f in NEWS.glob("*.md"):
        if f.name.startswith("."):
            continue
        fm = _read_frontmatter(f)
        if fm.get("rumor_id") == rumor_id:
            found = f
            source = fm.get("source", "")
            break

    if not found:
        return False

    fm = _read_frontmatter(found)
    fm["resolution_status"] = status
    fm["resolution"] = status
    fm["resolved_date"] = datetime.now().strftime("%Y-%m-%d")
    if resolved_by:
        fm["resolved_by"] = resolved_by
    _write_frontmatter(found, fm)

    if source:
        update_source_credibility(source)

    return True


def get_story_timeline(story_id: str) -> list:
    """Get all articles in a story arc. Returns list of {file, date, stage, source}."""
    if not story_id or not NEWS.exists():
        return []

    timeline = []
    for f in NEWS.glob("*.md"):
        if f.name.startswith("."):
            continue
        try:
            fm = _read_frontmatter(f)
            if fm.get("story_id") == story_id:
                timeline.append({
                    "file": f.name,
                    "date": fm.get("date", ""),
                    "stage": fm.get("story_stage", ""),
                    "source": fm.get("source", ""),
                    "resolution_status": fm.get("resolution_status", ""),
                })
        except:
            pass

    timeline.sort(key=lambda x: x["date"])
    return timeline


def get_pending_rumors(source: str = None) -> list:
    """Get pending rumors, optionally filtered by source."""
    if not NEWS.exists():
        return []

    pending = []
    cutoff = datetime.now() - timedelta(days=90)

    for f in NEWS.glob("*.md"):
        if f.name.startswith("."):
            continue
        fm = _read_frontmatter(f)
        if not fm.get("rumor_id"):
            continue
        if fm.get("resolution_status", "pending") != "pending":
            continue
        if source:
            src = fm.get("source", "")
            if src.lower().replace(" ", "").replace("-", "") != source.lower().replace(" ", "").replace("-", ""):
                continue

        date_str = fm.get("date", "")
        is_stale = False
        if date_str:
            try:
                art_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if art_date < cutoff:
                    is_stale = True
            except:
                pass

        pending.append({
            "file": f.name,
            "rumor_id": fm.get("rumor_id"),
            "source": fm.get("source", ""),
            "date": date_str,
            "entities": fm.get("entities", []),
            "stale": is_stale,
        })

    pending.sort(key=lambda x: x["date"], reverse=True)
    return pending


def get_leaderboard() -> list:
    """Get source credibility leaderboard. Returns list of {source, tier, score, confirmed, false, pending}."""
    if not PERSONS.exists():
        return []

    leaderboard = []
    for f in PERSONS.glob("*.md"):
        if f.name.startswith("."):
            continue
        fm = _read_frontmatter(f)
        if fm.get("base_tier") is None and not fm.get("credibility_score"):
            continue
        leaderboard.append({
            "source": fm.get("name", f.stem.replace("-", " ")),
            "outlet": fm.get("outlet", ""),
            "tier": fm.get("base_tier", 3),
            "score": fm.get("credibility_score", 50.0),
            "confirmed": fm.get("rumors_confirmed", 0),
            "false": fm.get("rumors_false", 0),
            "pending": fm.get("rumors_pending", 0),
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard
