import subprocess
import json
import time

TWEET = """🔥 FOOTBALL RED LININGS — 30 April 2026

🔴 BIG CLUBS IN CHAOS
• Liverpool: Salah & Robertson leave FREE. Rebuilding!
• Man City: Stones, Ake, Bernardo exiting. Mass exodus
• Chelsea: Rosenior SACKED, squad overhaul incoming
• Man Utd: £120m for Anderson TOO HIGH -转向 Tonali, Baleba

🔴 UCL SEMI-FINALS
• PSG 5-4 Bayern - 9 GOALS record-breaking!
• Arsenal vs Atletico (Wed)
• Final: May 30, Budapest

🔴 TRANSFER MARKET
• Morgan Rogers: Man Utd, Arsenal, Chelsea, PSG - £86m battle
• Rafael Leao: Man Utd considering swap + €50-60m
• Kvaratskhelia: "Not leaving PSG" - Arsenal blow
• Barcelona want Julian Álvarez - financial issues

🔴 TITLE RACE
• Man City beat Arsenal 2-1 - Haaland winner
• City go top with game in hand

#PL #UCL #Transfer"""

OPENCODE = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

print("=== Posting to x.com ===")

# Try direct compose URL
print("1. Going to compose...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_navigate", json.dumps({"url": "https://x.com/compose/post"})], capture_output=True, text=True)
print(f"   Navigate: {r.stdout[:100] if r.stdout else r.stderr[:100]}")
time.sleep(5)

# Type
print("2. Typing...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_type", json.dumps({"selector": "div[contenteditable]", "text": TWEET})], capture_output=True, text=True)
print(f"   Type result: {r.stdout[:100] if r.stdout else r.stderr[:100]}")
time.sleep(2)

# Try posting
print("3. Posting...")
r = subprocess.run(["node", OPENCODE, "tool", "browser_press", json.dumps({"selector": "div[contenteditable]", "key": "Enter"})], capture_output=True, text=True)
print(f"   Press: {r.stdout[:100] if r.stdout else r.stderr[:100]}")

time.sleep(3)

print("=== DONE ===")