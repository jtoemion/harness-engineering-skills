import json
from pathlib import Path
import yaml

news_dir = Path('C:/Users/jtoem/Assets/News/football/entities/news')
tracker = {'news': []}

for f in news_dir.glob('*.md'):
    if f.name.startswith('.'):
        continue
    try:
        content = f.read_text(encoding='utf-8')
    except:
        continue
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
            except:
                fm = {}
        else:
            fm = {}
    else:
        fm = {}
    
    key = fm.get('url', '')
    if not key:
        key = f"{fm.get('title', f.stem)}_{fm.get('date', '')}"
    
    tracker['news'].append({
        'key': key,
        'title': str(fm.get('title', f.stem)),
        'date': str(fm.get('date', '')),
        'source': str(fm.get('source', '')),
        'entities': [str(e) for e in fm.get('entities', [])]
    })

output = Path('C:/Users/jtoem/.config/opencode/skills/browser-agent/football-news/news-tracker.json')
output.write_text(json.dumps(tracker, indent=2))
print(f'Initialized tracker with {len(tracker["news"])} items')