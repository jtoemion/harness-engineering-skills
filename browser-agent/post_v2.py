import subprocess
import json
import time

TWEET = """🔥 FOOTBALL RED LININGS — April 30, 2026

🔴 BIG CLUBS IN CHAOS
• Liverpool: Salah & Robertson leave FREE + Curtis Jones may go
• Man City: Stones, Ake, Bernardo Silva exiting - mass exodus
• Chelsea: Rosenior sacked, squad overhaul incoming

🔴 UCL SEMI-FINALS  
• PSG 5-4 Bayern - 9 GOALS record-breaking!
• Arsenal vs Atletico (2nd leg Wed)
• Final: May 30, Budapest

🔴 TRANSFER MARKET
• Morgan Rogers: Man Utd, Arsenal, Chelsea, PSG - £86m battle
• Rafael Leao: Man Utd swap + €50-60m
• Kvaratskhelia: "Not leaving PSG" - Arsenal blow

#PL #UCL #Transfer"""

OPENCODE = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

print("=== START ===")

# Step 1: Open a new tab
print("1. Opening new tab...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_open_tab", json.dumps({"active": True})], capture_output=True, text=True)
print(f"   {r.stdout[:200]}")
time.sleep(2)

# Step 2: Navigate to x.com home
print("2. Navigate to x.com...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_navigate", json.dumps({"url": "https://x.com"})], capture_output=True, text=True)
print(f"   {r.stdout[:200]}")
time.sleep(5)

# Step 3: Try to find and click the post button using text
print("3. Click post...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": "text:Post"})], capture_output=True, text=True)
print(f"   {r.stdout[:200]}")
time.sleep(3)

# Step 4: Type the tweet
print("4. Type...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_type", json.dumps({"selector": "text:What is happening?", "text": TWEET})], capture_output=True, text=True)
print(f"   {r.stdout[:200]}")
time.sleep(2)

# Step 5: Click post button  
print("5. Click post button...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_click", json.dumps({"selector": "text:Post"})], capture_output=True, text=True)
print(f"   {r.stdout[:200]}")

print("=== END ===")