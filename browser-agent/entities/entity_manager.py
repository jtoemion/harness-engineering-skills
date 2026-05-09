"""
Entity Manager - Central registry + auto-creation for football entities.
"""
import os
import yaml
from datetime import datetime

SKILL_ROOT = r"C:\Users\jtoem\.config\opencode\skills\browser-agent"
REGISTRY_PATH = os.path.join(SKILL_ROOT, "entities", "registry.yaml")

VAULT_ROOT = r"C:\Users\jtoem\Assets\News\football"
ENTITY_FOLDERS = {
    "clubs": "entities/clubs",
    "players": "entities/players",
    "persons": "entities/persons",
    "leagues": "entities/leagues",
    "competitions": "entities/competitions",
    "nations": "entities/nations",
}

def load_registry():
    """Load entity registry from YAML."""
    if not os.path.exists(REGISTRY_PATH):
        return {}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    all_entities = {}
    for category in ["_clubs", "_players", "_managers", "_competitions", "_nations"]:
        if category in registry:
            all_entities.update(registry[category])

    return all_entities

def get_all_patterns_sorted(registry):
    """Return all entity patterns sorted by length (longest first) to prevent partial matches."""
    patterns = []
    for display_name, wikilink in registry.items():
        patterns.append((display_name, wikilink))
    patterns.sort(key=lambda x: len(x[0]), reverse=True)
    return patterns

def wikilink_text(text, registry=None):
    """
    Replace all known entities in text with wikilinks.
    Returns: (linked_text, list_of_entities_found)
    """
    if registry is None:
        registry = load_registry()

    entities_found = []
    sorted_patterns = get_all_patterns_sorted(registry)

    for display_name, wikilink in sorted_patterns:
        if display_name in text:
            text = text.replace(display_name, f"[[{wikilink}]]")
            entities_found.append(wikilink)

    return text, list(set(entities_found))

def create_entity_note(entity_name, entity_type, vault_root=VAULT_ROOT):
    """
    Auto-create an entity note in the appropriate folder.

    entity_type: clubs | players | persons | leagues | competitions | nations
    """
    if entity_type not in ENTITY_FOLDERS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    folder = os.path.join(vault_root, ENTITY_FOLDERS[entity_type])
    os.makedirs(folder, exist_ok=True)

    filename = f"{entity_name}.md"
    filepath = os.path.join(folder, filename)

    if os.path.exists(filepath):
        return filepath, False

    date = datetime.now().strftime("%Y-%m-%d")

    templates = {
        "clubs": f"""---
type: club
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [club, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
        "players": f"""---
type: player
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [player, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
        "persons": f"""---
type: person
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [person, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
        "leagues": f"""---
type: league
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [league, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
        "competitions": f"""---
type: competition
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [competition, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
        "nations": f"""---
type: nation
name: {entity_name.replace('-', ' ')}
created: {date}
source: auto-created
tags: [nation, auto-created]
---

# {entity_name.replace('-', ' ')}

Auto-created entity note.
""",
    }

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(templates[entity_type])

    return filepath, True

def get_entity_type_from_name(name):
    """
    Guess entity type from name patterns.
    Returns: clubs | players | persons | nations
    """
    name_lower = name.lower()

    if name_lower in ["premier league", "la liga", "bundesliga", "serie a", "ligue 1",
                      "champions league", "europa league", "fa cup", "world cup"]:
        return "competitions"

    nations = ["england", "spain", "france", "germany", "italy", "portugal", "brazil",
               "argentina", "netherlands", "belgium", "croatia", "denmark", "norway",
               "wales", "scotland", "ukraine", "poland"]
    if name_lower in nations:
        return "nations"

    managers_suffixes = ["manager", "coach", "manager says", "on", "confirms", "appointed"]
    if any(s in name_lower for s in managers_suffixes):
        return "persons"

    return "players"

def clean_tweet_text(text):
    """Remove noise from tweet text before entity extraction."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Pinned'):
            continue
        if line.startswith('@'):
            continue
        if line.startswith('#'):
            continue
        if line.startswith('·'):
            continue
        if line.replace('.','').replace(',','').replace(' ','').isdigit():
            continue
        if any(char in line for char in ['@', '#', '·', 'K', 'M']) and len(line) < 20:
            continue
        if '·' in line and len(line) < 30:
            continue
        cleaned_lines.append(line)
    return ' '.join(cleaned_lines)

def auto_discover_and_create(text, registry=None, vault_root=VAULT_ROOT):
    """
    Find unknown entities in text and auto-create notes for them.
    Returns: list of newly created entities

    Strategy:
    1. Build n-grams (2-3 words) from consecutive title-case words
    2. Filter out: short words, numbers, social media artifacts
    3. Check against registry
    4. If unknown and substantial, create note
    """
    text = clean_tweet_text(text)
    if not text or len(text) < 15:
        return []

    if registry is None:
        registry = load_registry()

    common_words = {
        "january", "february", "march", "april", "may", "june", "july", "august",
        "september", "october", "november", "december",
        "pinned", "breaking", "live", "new",
        "something", "everything",
        "signs", "signing", "appointed", "becomes",
        "hotspur", "athletic", "football", "league", "cup", "premier", "world",
        "afc", "cfc", "efc", "lfc", "mufc", "ffc", "utc", "nffc"
    }

    words = text.split()
    potential_ngrams = []

    i = 0
    while i < len(words):
        word = words[i].strip(".,!?:;\"'()[]{}")
        if not word or len(word) < 3:
            i += 1
            continue
        if word.lower() in common_words:
            i += 1
            continue
        if word[0].islower():
            i += 1
            continue
        if any(c in word for c in '@#·0123456789'):
            i += 1
            continue

        ngram = word
        j = i + 1
        valid = True
        while j < min(i + 3, len(words)):
            next_word = words[j].strip(".,!?:;\"'()[]{}")
            if not next_word or len(next_word) < 2:
                break
            if next_word[0].islower():
                break
            if next_word.lower() in common_words:
                break
            if any(c in next_word for c in '@#·0123456789'):
                break
            if len(next_word) < 3:
                break
            ngram += " " + next_word
            j += 1

        if len(ngram) < 6 or ngram in registry:
            i += 1
            continue

        if ngram not in [p[0] for p in potential_ngrams]:
            potential_ngrams.append(ngram)
        i = j

    created = []
    for ngram in potential_ngrams:
        if len(ngram) < 6:
            continue
        wikilink = ngram.replace(" ", "-")
        entity_type = get_entity_type_from_name(ngram)
        try:
            filepath, is_new = create_entity_note(wikilink, entity_type, vault_root)
            if is_new:
                created.append((wikilink, entity_type))
        except:
            pass

    return created

if __name__ == "__main__":
    registry = load_registry()
    print(f"Loaded {len(registry)} entities from registry")

    test_text = "Manchester City will let Pep Guardiola decide what he wants to do with his future."
    linked, entities = wikilink_text(test_text, registry)
    print(f"Input: {test_text}")
    print(f"Output: {linked}")
    print(f"Entities: {entities}")