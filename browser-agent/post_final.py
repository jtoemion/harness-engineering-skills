import asyncio
from _backends.chrome_backend import ChromeBackend

TWEET = """🔥 FOOTBALL RED LININGS — April 30, 2026

🔴 BIG CLUBS REBUILDING
• Liverpool: Salah, Robertson leave FREE
• Man City: Stones, Ake, Bernardo leaving
• Chelsea: Rosenior sacked

🔴 UCL SEMI-FINALS
• PSG 5-4 Bayern (9 goals!)
• Arsenal vs Atletico Wed
• Final May 30 Budapest

🔴 TRANSFERS
• Morgan Rogers: £86m battle
• Leao: Man Utd swap deal

#PL #UCL #Transfer"""

async def post():
    backend = ChromeBackend()
    await backend.launch()

    await backend.goto("https://x.com")
    await asyncio.sleep(6)

    # Open compose
    print("Opening compose...")
    await backend._run_tool("browser_click", {"selector": "text:Post"})
    await asyncio.sleep(4)

    # Find and fill textarea - try multiple approaches
    print("Finding textarea...")

    # Try type tool first
    try:
        await backend._run_tool("browser_type", {
            "selector": "[contenteditable='true']",
            "text": TWEET
        })
        print("Typed via browser_type")
    except Exception as e:
        print(f"browser_type failed: {e}")
        # Try click then type via evaluate
        try:
            await backend._run_tool("browser_click", {"selector": "[contenteditable='true'][role='textbox']"})
            await asyncio.sleep(1)
            await backend._run_tool("browser_type", {
                "selector": "[contenteditable='true']",
                "text": TWEET
            })
            print("Typed after clicking textarea")
        except Exception as e2:
            print(f"Second try failed: {e2}")

    await asyncio.sleep(3)

    # Post
    print("Posting...")
    try:
        await backend._run_tool("browser_click", {"selector": "text:Post"})
        print("Clicked Post button")
    except Exception as e:
        print(f"Post click failed: {e}")

    await asyncio.sleep(5)
    print("Done - check x.com!")

asyncio.run(post())