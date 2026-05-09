"""
Demo: chrome_backend auto-launches personal Chrome and fetches @TheAthleticFC posts.
"""
import asyncio, sys, os, time, re, json
from subprocess import run

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _backends.chrome_backend import ChromeBackend, check_broker_status

CLI_PATH = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

def parse_browser_json(stdout):
    """Extract JSON from opencode-browser CLI output, skipping ANSI and progress lines."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    cleaned = ansi_escape.sub('', stdout)
    lines = cleaned.split("\n")

    # Find JSON object start (line containing just "{")
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "{":
            start = i
            break

    if start is None:
        return None

    # Find JSON object end (line containing just "}")
    # Collect from start onwards
    json_lines = []
    brace_count = 0
    for i in range(start, len(lines)):
        line = lines[i]
        # Count braces on this line
        for ch in line:
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
        json_lines.append(line)
        if brace_count == 0 and i > start:
            break

    json_str = "\n".join(json_lines).strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

async def main():
    print("1. Checking broker status...")
    connected = check_broker_status()
    print(f"   hostConnected={connected}")

    print("\n2. Launching Chrome backend...")
    backend = ChromeBackend()
    page = await backend.new_page()
    print(f"   tab_id={page._tab_id}")

    print("\n3. Navigating to x.com/TheAthleticFC...")
    await backend.goto("https://x.com/TheAthleticFC")
    print("   Waiting 5s for page to load...")
    time.sleep(5)

    print("\n4. Fetching latest 5 posts (selector: article)...")
    result = run([
        "node", CLI_PATH, "tool", "browser_query",
        json.dumps({"selector": "article", "mode": "list", "tabId": page._tab_id})
    ], capture_output=True, text=True)

    data = parse_browser_json(result.stdout)
    if data and "value" in data and "items" in data["value"]:
        for i, item in enumerate(data["value"]["items"][:5], 1):
            text = item.get("text", "").replace("\n", " ")[:200]
            print(f"\n   Post {i}: {text}...")
    else:
        print("   No posts found. Raw:\n" + result.stdout[:500])

    print("\nDone!")
    await backend.close()

if __name__ == "__main__":
    asyncio.run(main())