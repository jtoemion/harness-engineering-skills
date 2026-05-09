import subprocess
import json
import time
import asyncio
from _backends.chrome_backend import ChromeBackend

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

#PL #UCL #Transfer"""

async def post_tweet():
    backend = ChromeBackend()
    await backend.launch()
    print("Browser launched")

    # Navigate to x.com home
    await backend.goto("https://x.com")
    print("Navigated to x.com")
    await asyncio.sleep(5)

    # Get the tab ID for operations
    tab_id = backend._tab_id
    print(f"Tab ID: {tab_id}")

    # Try clicking using text selector
    try:
        result = await backend._run_tool("browser_click", {
            "selector": "text:Post",
            "tabId": tab_id
        })
        print(f"Click result: {result}")
    except Exception as e:
        print(f"Click error: {e}")

    await asyncio.sleep(3)

    # Try typing in the textarea
    try:
        result = await backend._run_tool("browser_type", {
            "selector": "text:What is happening?",
            "text": TWEET,
            "tabId": tab_id
        })
        print(f"Type result: {result}")
    except Exception as e:
        print(f"Type error: {e}")

    await asyncio.sleep(2)

    # Try clicking Post button
    try:
        result = await backend._run_tool("browser_click", {
            "selector": "text:Post",
            "tabId": tab_id
        })
        print(f"Post result: {result}")
    except Exception as e:
        print(f"Post error: {e}")

    print("Done!")

asyncio.run(post_tweet())