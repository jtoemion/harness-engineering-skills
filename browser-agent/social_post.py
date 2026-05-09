import asyncio
from _backends.chrome_backend import ChromeBackend
import subprocess
import json
import time

TWEET = """🔥 FOOTBALL RED LININGS — April 30

🔴 BIG CLUBS, BIG CHANGES
• Liverpool: Salah, Robertson leaving FREE + Curtis Jones may go
• Man City: Stones, Ake, Bernardo exiting - mass exodus
• Chelsea: Rosenior sacked, squad overhaul incoming

🔴 UCL THRILLER
• PSG 5-4 Bayern - 9 GOALS, record-breaking semifinal
• Arsenal vs Atletico (Wednesday)
• Final: May 30, Budapest

🔴 TRANSFER MARKET
• Barcelona want Julian Álvarez (€95m) - financial issues
• Man Utd: €50-60m for Leao, Ederson talks
• Gordon to Chelsea? Arsenal too - €92m battle

#PL #UCL #Transfer"""

OPENCODE_BROWSER_CLI = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"

def run_cli(tool, args):
    json_args = json.dumps(args)
    result = subprocess.run(
        ["node", OPENCODE_BROWSER_CLI, "tool", tool, json_args],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.stdout, result.stderr

async def main():
    # First navigate to x.com home
    print("Navigating to x.com...")
    stdout, stderr = run_cli("browser_navigate", {"url": "https://x.com"})
    print(f"Navigate: {stdout[:100]}")
    time.sleep(5)

    # Open compose
    print("Clicking compose...")
    stdout, stderr = run_cli("browser_click", {"selector": "a[href=\"/compose/post\"]"})
    print(f"Click: {stdout[:100]}")
    time.sleep(3)

    # Type tweet
    print("Typing tweet...")
    stdout, stderr = run_cli("browser_type", {
        "selector": "[contenteditable=\"true\"]",
        "text": TWEET
    })
    print(f"Type: {stdout[:100]}")
    time.sleep(2)

    # Press Enter
    print("Posting...")
    stdout, stderr = run_cli("browser_press", {
        "selector": "[contenteditable=\"true\"]",
        "key": "Enter"
    })
    print(f"Press: {stdout[:100]}")

    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())