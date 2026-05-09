import subprocess, json, time
OPENCODE = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

TWEET = "FOOTBALL RED LININGS April 30: Liverpool rebuilding (Salah, Robertson leave FREE). Man City mass exodus. Chelsea Rosenior sacked. UCL: PSG 5-4 Bayern. Transfers: Morgan Rogers 86m battle. #PL #UCL"

TAB_ID = 1061583463

print("=== START ===")

# 1. Navigate to home
print("1. Navigate to x.com...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_navigate", json.dumps({"url": "https://x.com/home", "tabId": TAB_ID})], capture_output=True, text=True)
print(f"   Navigated")
time.sleep(4)

# 2. Click Post button - using aria-label
print("2. Click Post...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": "a[href='/compose/post']", "tabId": TAB_ID})], capture_output=True, text=True)
print(f"   {r.stdout[:100]}")
time.sleep(3)

# 3. Type tweet
print("3. Type...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_type", json.dumps({"selector": "[contenteditable='true'][role='textbox']", "text": TWEET, "tabId": TAB_ID})], capture_output=True, text=True)
print(f"   Typed")
time.sleep(2)

# 4. Submit - try multiple selectors
print("4. Submit - trying selectors...")

selectors = [
    "div[data-testid='tweetButton']",
    "div[data-testid='tweetButtonInline']",
    "button:has-text('Post')",
    "text:Post"
]

for sel in selectors:
    print(f"   Trying: {sel}")
    r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": sel, "tabId": TAB_ID})], capture_output=True, text=True)
    if "error" not in r.stdout.lower() and "fail" not in r.stdout.lower():
        print(f"   SUCCESS: {sel}")
        break
    time.sleep(1)

print("=== DONE ===")