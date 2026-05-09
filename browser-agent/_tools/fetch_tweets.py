"""
opencode-browser tweet fetcher.
Fetches latest tweets from any x.com account.

Usage:
    python fetch_tweets.py TheAthleticFC
    python fetch_tweets.py elonmusk --count 10
"""
import asyncio, sys, os, time, re, json
from subprocess import run

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _backends.chrome_backend import ChromeBackend, check_broker_status

CLI_PATH = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

def parse_browser_json(stdout):
    """Extract JSON from opencode-browser CLI output."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    cleaned = ansi_escape.sub('', stdout)

    for line in cleaned.split("\n"):
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                continue

    start = None
    for i, line in enumerate(cleaned.split("\n")):
        if line.strip() == "{":
            start = i
            break

    if start is not None:
        brace_count = 0
        json_lines = []
        for i in range(start, len(cleaned.split("\n"))):
            for ch in cleaned.split("\n")[i]:
                brace_count += 1 if ch in '{[' else -1 if ch in '}]' else 0
            json_lines.append(cleaned.split("\n")[i])
            if brace_count == 0 and i > start:
                break
        try:
            return json.loads("\n".join(json_lines).strip())
        except json.JSONDecodeError:
            pass
    return None


def parse_tweet_text(raw_text):
    """Parse tweet text and extract metadata."""
    lines = raw_text.split("\n")

    is_pinned = "Pinned" in lines[0]
    is_repost = "reposted" in raw_text

    author_line = lines[1] if len(lines) > 1 else ""
    time_line = lines[2] if len(lines) > 2 else ""

    content_lines = []
    for line in lines[3:]:
        if re.match(r'^\d+\s+\d+\s+\d+$', line.strip()):
            break
        content_lines.append(line)

    text = " ".join(content_lines).strip()

    engagement = None
    for line in lines:
        match = re.findall(r'\d+', line)
        if match and len(match) >= 3:
            try:
                engagement = {
                    "replies": int(match[0]),
                    "reposts": int(match[1]),
                    "likes": int(match[2])
                }
            except:
                pass

    return {
        "pinned": is_pinned,
        "repost": is_repost,
        "author": author_line,
        "time": time_line,
        "text": text,
        "engagement": engagement
    }


async def fetch_tweets(account, count=5):
    print(f"Fetching @{account} tweets...")

    backend = ChromeBackend()
    page = await backend.new_page()
    print(f"  Tab opened: {page._tab_id}")

    url = f"https://x.com/{account}"
    await backend.goto(url)
    print(f"  Navigated to {url}")

    print("  Waiting 5s for page to load...")
    time.sleep(5)

    result = run([
        "node", CLI_PATH, "tool", "browser_query",
        json.dumps({"selector": "article", "mode": "list", "tabId": page._tab_id})
    ], capture_output=True, text=True)

    data = parse_browser_json(result.stdout)

    if not data or "value" not in data or "items" not in data["value"]:
        print(f"  No tweets found.")
        await backend.close()
        return

    items = data["value"]["items"][:count]

    print(f"\n--- Latest {len(items)} tweets from @{account} ---\n")

    for i, item in enumerate(items, 1):
        tweet = parse_tweet_text(item.get("text", ""))
        print(f"Tweet {i}:")
        if tweet["pinned"]:
            print(f"  [PINNED]")
        if tweet["repost"]:
            print(f"  [REPOST]")
        print(f"  Author: {tweet['author']}")
        print(f"  Time: {tweet['time']}")
        print(f"  Text: {tweet['text'][:300]}{'...' if len(tweet['text']) > 300 else ''}")
        if tweet["engagement"]:
            e = tweet["engagement"]
            print(f"  📊 {e['replies']} replies · {e['reposts']} reposts · {e['likes']} likes")
        print()

    await backend.close()
    print("Done.")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "TheAthleticFC"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    asyncio.run(fetch_tweets(account, count))