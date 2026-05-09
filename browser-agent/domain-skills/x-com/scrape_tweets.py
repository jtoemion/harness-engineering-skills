"""
x.com Tweet Scraper with mandatory failure-retry loop.

Every failure triggers:
1. Write to failures.md
2. Read failures.md immediately
3. Extract fix
4. Retry (up to 3×)
"""
import asyncio
import json
import os
import re
import sys
from datetime import datetime

_BROWSER_AGENT_ROOT = r"C:\Users\jtoem\.config\opencode\skills\browser-agent"
sys.path.insert(0, _BROWSER_AGENT_ROOT)
from _backends.chrome_backend import ChromeBackend, check_broker_status
from entities.entity_manager import wikilink_text, auto_discover_and_create, load_registry

ACCOUNTS = [
    ("FabrizioRomano", "https://x.com/FabrizioRomano"),
    ("David_Ornstein", "https://x.com/David_Ornstein"),
    ("TheAthleticFC", "https://x.com/TheAthleticFC"),
    ("SkyFootball", "https://x.com/SkyFootball"),
    ("OptaJoe", "https://x.com/OptaJoe"),
    ("Zonal_Marking", "https://x.com/Zonal_Marking"),
    ("StatsBomb", "https://x.com/StatsBomb"),
    ("jonathanliew", "https://x.com/jonathanliew"),
    ("GaryLineker", "https://x.com/GaryLineker"),
    ("henrywinter", "https://x.com/henrywinter"),
]

OUTPUT_DIR = r"C:\Users\jtoem\Assets\News\football\entities\news"
VAULT_ROOT = r"C:\Users\jtoem\Assets\News\football"
FAILURES_FILE = os.path.dirname(os.path.abspath(__file__)) + "/failures.md"

def write_failure(error, tool, url, context, fix_applied="None"):
    """Write failure to failures.md"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""
## {timestamp}

**Error:** {error}
**Tool:** {tool}
**URL:** {url}
**Context:** {context}
**Fix Applied:** {fix_applied}
**Status:** RETRYING
"""
    with open(FAILURES_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

def read_last_failure():
    """Read last failure entry from failures.md"""
    if not os.path.exists(FAILURES_FILE):
        return None
    with open(FAILURES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    entries = content.split("## ")
    if len(entries) < 2:
        return None
    last_entry = entries[-1].strip()
    failure = {}
    for line in last_entry.split("\n"):
        if "**Error:**" in line:
            failure["error"] = line.split("**Error:**")[1].strip()
        elif "**Tool:**" in line:
            failure["tool"] = line.split("**Tool:**")[1].strip()
        elif "**URL:**" in line:
            failure["url"] = line.split("**URL:**")[1].strip()
        elif "**Fix Applied:**" in line:
            failure["fix_applied"] = line.split("**Fix Applied:**")[1].strip()
        elif "**Status:**" in line:
            failure["status"] = line.split("**Status:**")[1].strip()
    return failure

def extract_fix_from_failure(failure):
    """Extract mitigation from failure - returns tuple (selector_tried, alternative_selector)"""
    error = failure.get("error", "")
    if "No matches for selectors: article" in error:
        return ("article", ["article[role='article']", "div[data-testid='tweet']", "div.tweet"])
    if "Site access permission not granted" in error:
        return ("permission", ["REQUIRES_USER_ACTIVATION"])
    return (None, None)

def mark_failure_resolved(timestamp=None):
    """Mark last failure as RESOLVED"""
    if not os.path.exists(FAILURES_FILE):
        return
    with open(FAILURES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    if timestamp:
        content = content.replace(f"{timestamp}\n**Status:** RETRYING", f"{timestamp}\n**Status:** RESOLVED")
    else:
        content = content.replace("**Status:** RETRYING", "**Status:** RESOLVED")
    with open(FAILURES_FILE, "w", encoding="utf-8") as f:
        f.write(content)

class TweetScraper:
    def __init__(self):
        self.backend = ChromeBackend()
        self.date_today = datetime.now().strftime("%Y-%m-%d")
        self.current_account = None
        self.retry_count = 0
        self.max_retries = 3
        self.registry = load_registry()
        print(f"Loaded {len(self.registry)} entities from registry")

    async def scrape_account(self, account_name, url, max_tweets=5):
        print(f"\n{'='*50}")
        print(f"Scraping: @{account_name}")
        print(f"URL: {url}")

        self.current_account = account_name
        self.retry_count = 0

        return await self._scrape_with_retry(account_name, url, max_tweets)

    async def _scrape_with_retry(self, account_name, url, max_tweets=5):
        """Retry loop: write failure → read → extract fix → retry"""
        while self.retry_count < self.max_retries:
            try:
                tweets = await self._do_scrape(account_name, url, max_tweets)
                if tweets:
                    if self.retry_count > 0:
                        mark_failure_resolved()
                    return tweets
                else:
                    raise Exception("No tweets extracted")
            except Exception as e:
                self.retry_count += 1
                error_str = str(e)
                tool_str = "browser_query"
                context_str = f"Attempt {self.retry_count}/{self.max_retries} for @{account_name}"

                print(f"  ❌ Attempt {self.retry_count} failed: {error_str[:100]}")

                write_failure(error_str, tool_str, url, context_str)
                failure = read_last_failure()
                fix_type, alternatives = extract_fix_from_failure(failure)

                if fix_type == "article" and alternatives:
                    print(f"  🔧 Trying alternative selectors: {alternatives}")
                elif fix_type == "permission":
                    print(f"  ⚠️ User activation required - try clicking extension icon")

                if self.retry_count >= self.max_retries:
                    print(f"  ❌ Max retries reached for @{account_name}")
                    return []

                await asyncio.sleep(2)

        return []

    async def _do_scrape(self, account_name, url, max_tweets=5):
        """Actual scraping logic"""
        await self.backend.goto(url)
        await asyncio.sleep(4)

        tabs_result = await self.backend._run_tool("browser_get_tabs", {})

        tab_id = None
        if isinstance(tabs_result, list):
            for tab in tabs_result:
                tab_url = tab.get('url', '')
                if f"x.com/{account_name}" in tab_url or account_name in tab_url:
                    tab_id = tab.get('id')
                    print(f"  Found matching tab: {tab_id}")
                    break

        if tab_id is None and len(tabs_result) > 0:
            tab_id = tabs_result[0].get('id')
            print(f"  Using first tab: {tab_id}")

        await self.backend._run_tool("browser_claim_tab", {"tabId": tab_id})
        await asyncio.sleep(1)

        selectors_to_try = ["article", "article[role='article']", "div[data-testid='tweet']"]
        tweets = []

        for selector in selectors_to_try:
            try:
                result = await self.backend._run_tool("browser_query", {
                    "tabId": tab_id,
                    "selector": selector,
                    "mode": "list"
                })

                if isinstance(result, dict) and "value" in result and "items" in result["value"]:
                    for item in result["value"]["items"][:max_tweets]:
                        tweets.append({
                            'text': item.get('text', ''),
                            'time': item.get('time', ''),
                            'link': item.get('href', '')
                        })
                    if tweets:
                        print(f"  ✅ Extracted {len(tweets)} tweets with selector: {selector}")
                        break
            except Exception as e:
                print(f"  Selector '{selector}' failed: {str(e)[:80]}")

        if tweets:
            filename = f"{account_name}-{self.date_today}.md"
            filepath = os.path.join(OUTPUT_DIR, filename)
            self._save_tweets(account_name, tweets, filepath)
            print(f"  Saved {len(tweets)} tweets to {filename}")

        return tweets

    def _save_tweets(self, account_name, tweets, filepath):
        content = f"""---
type: tweets
date: {self.date_today}
source: x.com/@{account_name}
account: @{account_name}
count: {len(tweets)}
entities: []
tags: []
---

# @{account_name} - Tweets

"""

        all_entities = set()
        new_entities_created = []
        for i, tweet in enumerate(tweets, 1):
            date_str = tweet['time'][:10] if tweet['time'] else self.date_today
            text = tweet['text'].encode('utf-8', errors='replace').decode('utf-8')
            linked_text, entities = self._wikilink_text(text)
            all_entities.update(entities)

            created = self._auto_create_unknown(text)
            new_entities_created.extend(created)

            content += f"""## Tweet {i} ({date_str})

**Source:** {tweet['link']}

{linked_text}

---
"""

        entity_list = sorted(list(all_entities))
        content = content.replace("entities: []", f"entities:\n  - " + "\n  - ".join(f"[[{e}]]" for e in entity_list))

        if new_entities_created:
            tags_line = f"auto_created: {', '.join(e[0] for e in new_entities_created)}"
            content = content.replace("tags: []", f"tags: []\n{tags_line}")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        if new_entities_created:
            print(f"  Auto-created {len(new_entities_created)} new entities: {new_entities_created}")

    def _wikilink_text(self, text):
        """Find entities in text and replace with wikilinks using registry. Returns (linked_text, entity_list)."""
        return wikilink_text(text, self.registry)

    def _auto_create_unknown(self, text):
        """Find unknown entities (2+ word names only) and auto-create notes. Returns list of newly created."""
        if " " not in text:
            return []
        return auto_discover_and_create(text, self.registry, VAULT_ROOT)

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Broker status: {check_broker_status()}")
    sys.stdout.flush()

    scraper = TweetScraper()
    print("Scraper created")
    sys.stdout.flush()

    for account_name, url in ACCOUNTS:
        print(f"Processing @{account_name}...")
        sys.stdout.flush()
        try:
            tweets = await scraper.scrape_account(account_name, url, max_tweets=5)
            if not tweets:
                print(f"⚠️ No tweets scraped for @{account_name}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error scraping @{account_name}: {e}")

    print("\n=== DONE ===")
    print(f"Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())