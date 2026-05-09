"""
Image Extractor - Save images from articles for manual download

Usage:
    python extract_images.py <article_url> <output_filename>

Example:
    python extract_images.py "https://espn.com/article" "ucl-semifinal"
"""

import sys
import subprocess
import json
import time
import os

OPENCODE = r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"
OUTPUT_DIR = r"C:\Users\jtoem\Assets\News\football\tweets\images"

def extract_images(url, prefix):
    print(f"Opening: {url}")

    # Navigate to page
    r = subprocess.run(["node", OPENCODE, "tool", "browser_navigate", json.dumps({"url": url})],
                       capture_output=True, text=True)
    time.sleep(5)

    # Get page HTML to find images
    r = subprocess.run(["node", OPENCODE, "tool", "browser_evaluate",
                        json.dumps({"function": "() => { return document.images.length; }"})],
                       capture_output=True, text=True)

    # Take screenshot of the article for reference
    screenshot_path = f"{OUTPUT_DIR}/{prefix}_screenshot.png"
    r = subprocess.run(["node", OPENCODE, "tool", "browser_screenshot", json.dumps({"path": screenshot_path})],
                       capture_output=True, text=True)
    print(f"Screenshot saved: {screenshot_path}")

    print("Note: Full image extraction requires additional setup.")
    print("For now, screenshot of article is saved for manual reference.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_images.py <url> <prefix>")
        sys.exit(1)

    url = sys.argv[1]
    prefix = sys.argv[2]
    extract_images(url, prefix)