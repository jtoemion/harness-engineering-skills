# News tracker - persists across sessions to detect duplicates

from pathlib import Path
from datetime import datetime
import json

TRACKER_FILE = "C:/Users/jtoem/.config/opencode/skills/browser-agent/football-news/news-tracker.json"

def load_tracker():
    """Load tracker from file"""
    p = Path(TRACKER_FILE)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except:
            return {"news": [], "last_updated": None}
    return {"news": [], "last_updated": None}

def save_tracker(data):
    """Save tracker to file"""
    data["last_updated"] = datetime.now().isoformat()
    Path(TRACKER_FILE).write_text(json.dumps(data, indent=2))

def add_news(news_items):
    """Add new news to tracker"""
    tracker = load_tracker()
    
    for item in news_items:
        # Create unique key from url or title+date
        key = item.get("url") or f"{item.get('title')}_{item.get('date')}"
        
        # Skip if already exists
        if any(n.get("key") == key for n in tracker["news"]):
            continue
        
        tracker["news"].append({
            "key": key,
            "title": item.get("title", ""),
            "date": item.get("date", ""),
            "source": item.get("source", ""),
            "entities": item.get("entities", []),
            "added": datetime.now().isoformat()
        })
    
    save_tracker(tracker)
    return tracker

def is_duplicate(new_item):
    """Check if news already scraped"""
    tracker = load_tracker()
    
    # Check by URL
    if new_item.get("url"):
        for n in tracker["news"]:
            if n.get("url") == new_item.get("url"):
                return True
    
    # Check by title + date
    title = new_item.get("title", "")
    date = new_item.get("date", "")
    if title and date:
        for n in tracker["news"]:
            if n.get("title") == title and n.get("date") == date:
                return True
    
    # Check by key entities + topic (e.g., "player X to club Y")
    entities = new_item.get("entities", [])
    if len(entities) >= 2:
        for n in tracker["news"]:
            n_entities = n.get("entities", [])
            # If same 2+ entities and recent date, likely dupe
            if set(entities[:3]) & set(n_entities[:3]):
                if n.get("date") == date:
                    return True
    
    return False

def get_stats():
    """Get tracker stats"""
    tracker = load_tracker()
    return {
        "total": len(tracker["news"]),
        "last_updated": tracker.get("last_updated"),
        "sources": list(set(n.get("source") for n in tracker["news"]))
    }

if __name__ == "__main__":
    # CLI for testing
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            s = get_stats()
            print(f"Tracked: {s['total']} news items")
            print(f"Updated: {s['last_updated']}")
        elif sys.argv[1] == "check":
            # Check if URL exists
            result = is_duplicate({"url": sys.argv[2], "title": sys.argv[3]})
            print(f"Duplicate: {result}")
    else:
        print("Usage: python news-tracker.py stats | check <url> <title>")