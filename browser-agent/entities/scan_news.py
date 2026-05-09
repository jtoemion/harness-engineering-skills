import os
import re
import yaml
from collections import Counter

NEWS_DIR = r"C:\Users\jtoem\Assets\News\football\entities\news"
REGISTRY_PATH = r"C:\Users\jtoem\.config\opencode\skills\browser-agent\entities\registry.yaml"

def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def extract_entities_from_files():
    entities = Counter()
    for filename in os.listdir(NEWS_DIR):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(NEWS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        for word in words:
            if len(word) > 3 and word not in ['The', 'This', 'That', 'They', 'There', 'Here', 'What', 'When', 'Where', 'Premier', 'Champions', 'League', 'Manchester', 'Real', 'Paris', 'BBC', 'Sky']:
                entities[word] += 1

    return entities

def main():
    registry = load_registry()
    all_entities = {**registry.get('_clubs', {}), **registry.get('_players', {}),
                     **registry.get('_managers', {}), **registry.get('_competitions', {}),
                     **registry.get('_nations', {})}

    found_entities = extract_entities_from_files()

    print("Entities found in news files that are NOT in registry:")
    print("-" * 60)

    missing = []
    for entity, count in found_entities.most_common(200):
        if entity not in all_entities and count >= 2:
            missing.append((entity, count))

    for entity, count in missing[:50]:
        print(f"{count:3d}x {entity}")

    print()
    print(f"Total missing (count >= 2): {len(missing)}")
    print(f"Current registry size: {len(all_entities)}")

if __name__ == "__main__":
    main()