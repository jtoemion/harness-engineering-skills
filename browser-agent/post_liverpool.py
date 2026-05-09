import subprocess, json, time
OPENCODE = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

TWEET = """🚨 Liverpool leading race to sign next Mo Salah!

PSG's Ibrahim Mbaye (18) emerging as top target to replace departing Salah.

The Senegalese winger valued at $33m - already has 50 senior games for PSG.

Michael Edwards and Liverpool moving fast for the next big thing? 🇸🇳

#LFC #Liverpool #Transfer #PSG"""

TAB_ID = 1061583463

print("=== POSTING ===")

# Navigate
r = subprocess.run(["node", OPENCODE, "tool", "browser_navigate", json.dumps({"url": "https://x.com/home", "tabId": TAB_ID})], capture_output=True, text=True)
time.sleep(4)

# Open compose
r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": "a[href='/compose/post']", "tabId": TAB_ID})], capture_output=True, text=True)
time.sleep(3)

# Type
r = subprocess.run(["node", OPENCODE, "tool", "browser_type", json.dumps({"selector": "[contenteditable='true'][role='textbox']", "text": TWEET, "tabId": TAB_ID})], capture_output=True, text=True)
time.sleep(2)

# Post
r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": "div[data-testid='tweetButton']", "tabId": TAB_ID})], capture_output=True, text=True)
time.sleep(3)

print("=== DONE ===")