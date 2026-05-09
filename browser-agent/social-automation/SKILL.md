---
name: social-automation
description: Use when automating social media posting (Twitter/X, Bluesky) via browser automation.
---

# social-automation — Browser Automation for Social Media

## MANDATORY ENFORCEMENT

**Violating the letter of these rules is violating the spirit of these rules.**

Social media automation MUST use opencode-browser. This is NOT optional, negotiable, or bypassable.

### STRICTLY FORBIDDEN

**NEVER use these tools under ANY circumstances:**
- ❌ `playwright_browser_*` (Playwright MCP)
- ❌ `chrome-devtools_*` (CDP protocol)
- ❌ `stagehand_*` (Stagehand)
- ❌ Any other browser automation tool

Using ANY of these tools is a DIRECT VIOLATION. It does not matter if:
- The broker is not running
- You're in a hurry
- You think it "might work"
- The user didn't specify

**If opencode-browser is unavailable, report it as a blocker.** Do NOT substitute with forbidden tools.

## Core Principle

```
opencode-browser → map workflow → execute → handle failures
```

## opencode-browser Setup

```bash
# Install (once)
bunx @different-ai/opencode-browser@latest install

# Start broker (keep running)
opencode-browser broker

# Use via browser-agent skill's chrome_backend
```

Key components:
| Component | Purpose |
|-----------|---------|
| Broker | WebSocket server for automation |
| DOM snapshot | Page structure via accessibility tree |
| Click/Type/Hover | Actions on elements |

## Workflow Map

```
Start → Launch browser → Navigate to site
    ↓
Auth check → Logged in? → Yes → Go to post form
    ↓                           ↓
No → Login flow ← Post tweet ← Success
    ↓                    ↓
Capture failure ← Retry 2× ← Fail → Report
```

### Node Map (Twitter Posting)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  x.com/home │ ──→ │ login form  │ ──→ │ home feed  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                                     │
        ↓                                     ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ post form   │ ──→ │ tweet popup │ ──→ │ confirmation│
└─────────────┘     └─────────────┘     └─────────────┘
```

### Iframe Detection

Twitter uses iframes for tweet composer:
- Iframe containing textarea with placeholder "What is happening?!"
- Outer container has role="dialog"
- Nested iframe for media attachments

Detected via accessibility snapshot:
```
[role="dialog"]
  → iframe#id (composer)
    → [contenteditable="true"]
```

## Required: Backend Selection

When automating social media, you MUST use opencode-browser. This is NOT OPTIONAL.

| Site | Backend | Why |
|------|---------|-----|
| x.com | opencode-browser | Login walls, bot detection |
| bluesky.social | opencode-browser | Auth required |
| twitter.com | opencode-browser | Same as x.com |

### How to Access opencode-browser

opencode-browser is accessed via browser-agent's `chrome_backend.py`:

```python
# CORRECT - Use browser-agent's chrome_backend
from _backends.chrome_backend import ChromeBackend

backend = ChromeBackend()
await backend.launch()
await backend.goto(url)
```

### STRICTLY FORBIDDEN

**NEVER use these tools:**
- ❌ `playwright_browser_*` (Playwright MCP)
- ❌ `chrome-devtools_*` (CDP protocol)
- ❌ `stagehand_*` (Stagehand)

This is violation even if the opencode-browser broker is not running. If broker is down, report it as a blocker.

## Login Flow

```python
# 1. Navigate to login
goto("https://x.com/i/flow/login")

# 2. Wait for username field
wait_for("label:Phone, email, or username")

# 3. Enter credentials
type("label:Phone, email, or username", USERNAME)
click("text:Next")

# 4. Wait for password field  
wait_for("label:Password")
type("label:Password", PASSWORD)
click("text:Log in")

# 5. Verify auth
wait_for("main timeline")
verify_url("x.com/home")
```

## Posting Flow

```python
# 1. Ensure at home/timeline
goto("https://x.com/home")

# 2. Click post button
wait_for("[aria-label='Post']")
click("[aria-label='Post']")

# 3. Wait for composer dialog
wait_for("role=dialog")

# 4. Type tweet
wait_for("[contenteditable='true']")
type("[contenteditable='true']", TWEET_TEXT)

# 5. Click post
click("text:Post")

# 6. Verify success
wait_for("text:Post", state="hidden")  # Dialog closed
```

## Failure-Retry Loop

**MANDATORY** — Every failure triggers retry:

```
Failure → Log to failures.md → Read last failure
    ↓
Apply fix → Retry → Succeed? → Done
    ↓
Fail again → Log new failure → Retry × 2
    ↓
Still failing → Report to user
```

Required fields in failures.md:
```markdown
## YYYY-MM-DD HH:MM

**Error:** <exact error>
**URL:** <page URL>
**Action:** <what failed>
**Fix:** <proposed fix>
**Status:** RETRYING|PERSOLVED|PERSISTENT
```

## Quick Reference

| Action | Command |
|--------|---------|
| Navigate | `goto("URL")` |
| Click element | `click("selector")` |
| Type text | `type("selector", "text")` |
| Wait for | `wait_for("selector")` |
| Snapshot | `snapshot()` |
| Screenshot | `screenshot()` |

Selectors: `aria:Label`, `text:Content`, `role:Type`, `[attribute=value]`

## Red Flags — STOP

If you find yourself doing any of these, STOP and start over:
- Using `playwright_browser_*` for social media → Delete all and start over
- Using `chrome-devtools_*` for social media → Delete all and start over
- Asking user for credentials without attempting auth flow → Use the login flow above
- Skipping the failure retry loop → Implement retry loop immediately

## Entities (if scraping)

Track entities using wikilinks:
```yaml
entities:
  - "[[Manchester-City]]"
  - "[[Erling-Haaland]]"
```