# browser-agent + opencode-browser Integration

**Date:** 2026-04-25
**Status:** Working ✓
**End-to-end verified:** Fetched 5 posts from x.com/TheAthleticFC ✓

---

## What We Built

Python `ChromeBackend` that wraps opencode-browser CLI, auto-launches personal Chrome when needed, and handles multi-line JSON parsing from the CLI output.

---

## Architecture

```
browser-agent (Python)
  ├── ChromeBackend (auto-launches Chrome + wraps CLI)
  │     └── opencode-browser CLI → broker (named pipe) → Chrome Extension → Real Chrome
  └── PlaywrightBackend (headless CDP, default for most sites)

get_backend(site)  ← site-specific backend selection
  ├── domain-skills/<site>/_meta.yaml → backend: chrome|playwright
  ├── BROWSER_BACKEND env var
  └── Default: playwright
```

---

## Quick Start

### 1. Install opencode-browser

```bash
bunx @different-ai/opencode-browser@latest install
```

Follow the installer prompts (load unpacked extension, register native host).

### 2. Verify installation

```bash
node "C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js" tool browser_status
```

Should return `{"broker":true,"hostConnected":true,...}` once Chrome is open with the extension.

### 3. Add to opencode.json (for OpenWork recognition)

Global config: `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": [
    "opencode-scheduler",
    "@different-ai/opencode-browser"
  ],
  "skills": [
    "browser-agent"
  ]
}
```

### 4. Configure site backend

In `domain-skills/<site>/_meta.yaml`:

```yaml
backend: chrome    # Use opencode-browser (real Chrome with profile)
# or
backend: playwright  # Use headless Playwright (default)
```

---

## chrome_backend.py — Key Design Decisions

### 1. Auto-Launch (ensure_chrome_running)

```python
def ensure_chrome_running():
    if check_broker_status():
        return True
    # Launch personal Chrome with Default profile
    subprocess.Popen([
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--new-window", "https://x.com",
        "--profile-directory=Default"
    ])
    # Poll for 30s until hostConnected=true
```

Every `ChromeBackend` method (`launch`, `new_page`, `goto`, `_run_tool`) calls `ensure_chrome_running()` first. Chrome is auto-launched on first use — no manual preparation needed.

Configurable via env vars:
- `CHROME_PATH` — Chrome executable path
- `CHROME_PROFILE` — Profile directory name (default: `Default`)

### 2. CLI Invocation — No `--args` Flag

**CRITICAL:** The `--args` flag does NOT work. Use positional JSON.

```python
# WRONG — CLI getFlagValue splits on spaces, mangles JSON
subprocess.run(["node", CLI, "tool", toolName, "--args", json_args])

# CORRECT — positional JSON as argv[4]
subprocess.run(["node", CLI, "tool", toolName, json_args])
```

Why `--args` fails:
1. **PowerShell mangles JSON** — `{"url":"https://example.com"}` becomes `{url:https://example.com}` (quotes stripped)
2. **CLI getFlagValue bug** — splits on spaces, can't handle JSON with unescaped spaces

### 3. Multi-Line JSON Parsing

opencode-browser CLI outputs formatted multi-line JSON with ANSI color codes:

```
[36m[1mOpenCode Browser v4[0m[0m
[36mBrowser automation plugin...[0m

{
  "ok": true,
  "selectorUsed": "article",
  "value": {
    "count": 3,
    "items": [...]
  }
}
```

`_parse_cli_json()` handles this:
1. Strip ANSI escape sequences
2. Try single-line JSON (starts with `{` or `[`)
3. Fall back to multi-line: find `{` or `[`, then count braces/brackets to find the end

```python
def _parse_cli_json(stdout):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    cleaned = ansi_escape.sub('', stdout)
    lines = cleaned.split("\n")

    # Single-line JSON
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                continue

    # Multi-line JSON — find start, count braces/brackets to find end
    start = None
    start_char = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "{":
            start, start_char = i, "{"
            break
        if stripped == "[":
            start, start_char = i, "["
            break

    if start is not None:
        brace_count = 0
        json_lines = []
        for i in range(start, len(lines)):
            for ch in lines[i]:
                brace_count += 1 if ch in '{[' else -1 if ch in '}]' else 0
            json_lines.append(lines[i])
            if brace_count == 0 and i > start:
                break
        return json.loads("\n".join(json_lines).strip())

    return None
```

### 4. Text Response Fallback

Some tools (`browser_navigate`, `browser_click`, `browser_type`) return plain text instead of JSON:
- "Navigated to https://..."
- "Clicked element"
- "Typed text"

`_run_tool` checks for these after JSON parsing fails:

```python
for line in output.split("\n"):
    stripped = line.strip()
    if stripped.startswith("Navigated"):
        return {"ok": True}
    if stripped.startswith("Clicked"):
        return {"ok": True}
    if stripped.startswith("Typed"):
        return {"ok": True}
```

---

## Available Tools (via CLI)

```bash
node cli.js tools   # List all tools

# No args needed:
browser_status              → {"broker":true,"hostConnected":true,...}
browser_open_tab            → {"tabId":1234567890,"url":"","active":true}
browser_list_claims         → {"claims":[]}

# JSON positional arg (NOT --args):
browser_navigate '{"url":"https://x.com"}'
browser_query '{"selector":"article","mode":"list"}'
browser_click '{"selector":"text:Log in"}'
browser_type '{"selector":"input[name=email]","text":"user@example.com"}'
browser_close_tab '{"tabId":1234567890}'
```

### browser_query modes

| Mode | Returns |
|------|---------|
| `page_text` | All text on page |
| `list` | All matching elements (for `article`, `button`, etc.) |
| `exists` | Boolean — does selector match anything? |

---

## Selector Syntax (opencode-browser native)

| Syntax | Maps to |
|--------|---------|
| `label:Email` | `[aria-label="Email"]` |
| `aria:Submit` | `[aria-label="Submit"]` |
| `placeholder:Search` | `[placeholder="Search"]` |
| `name:email` | `[name="email"]` |
| `role:button` | `[role="button"]` |
| `text:Log in` | text containing "Log in" |
| `article` | `<article>` DOM tag |

---

## Backend Selection Flow

```python
def get_backend(site=None):
    # 1. Check site meta
    if site:
        meta = _load_site_meta(site)  # reads domain-skills/<site>/_meta.yaml
        backend = meta.get("backend", "").lower()
        if backend == "chrome":
            return ChromeBackend()
        if backend == "playwright":
            return PlaywrightBackend()

    # 2. Check env var
    env = os.environ.get("BROWSER_BACKEND", "playwright").lower()
    if env in ("chrome", "opencode-browser"):
        return ChromeBackend()

    # 3. Default
    return PlaywrightBackend()
```

Example `domain-skills/x-com/_meta.yaml`:
```yaml
backend: chrome
```

---

## End-to-End Demo

`python _tools/demo_chrome_backend.py`:

```
1. Checking broker status...
   hostConnected=True

2. Launching Chrome backend...
   tab_id=1061582581

3. Navigating to x.com/TheAthleticFC...
   Waiting 5s for page to load...

4. Fetching latest 5 posts (selector: article)...

   Post 1: Pinned The Athletic | Football @TheAthleticFC · 22h Sources connected to senior Chelsea players...

   Post 2: The Athletic | Football @TheAthleticFC · 2m It's semi-final weekend in the men's FA Cup...

   Post 3: The Athletic | Football @TheAthleticFC · 33m After scoring against Arsenal, Alex Scott...
```

---

## Mapping / Recipe Cost Reduction

The explore-then-cache workflow works with both backends:

| Phase | Playwright | Chrome (opencode-browser) |
|-------|-----------|---------------------------|
| `map_site` — explore site structure | ✓ Default | Use `BROWSER_BACKEND=chrome` if login wall |
| `run_recipe` — execute stored steps | ✓ Default | Site with `backend: chrome` in `_meta.yaml` |
| `heal` — autorepair failures | ✓ Default | Falls back to Chrome if needed |

Cached selectors in `domain-skills/<site>/selectors.md` mean repeat runs don't need snapshots — just execute recipe steps with stored selectors.

When to use Chrome (opencode-browser):
- Login walls / bot detection (Cloudflare, DataDome)
- Sites that fingerprint headless browsers (x.com, banking)
- Need real cookies/session from your personal Chrome profile

When to use Playwright (default):
- Public pages, no login
- Exploration / mapping (cheap, fast)
- CI/CD environments

---

## File Map

```
browser-agent/
├── SKILL.md                          # Updated with backend selection docs
├── _backends/
│   ├── __init__.py                   # BrowserBackend ABC + get_backend(site)
│   ├── chrome_backend.py              # ChromeBackend + ensure_chrome_running()
│   ├── playwright_backend.py          # PlaywrightBackend (unchanged)
│   ├── selector_parser.py            # Selector helper parser
│   └── CHROME_BACKEND.md             # This doc
├── _tools/
│   ├── self_test.py                  # 11 tests, all pass
│   ├── demo_chrome_backend.py        # End-to-end demo
│   ├── map_site.py                   # Site mapping (Playwright)
│   ├── run_recipe.py                 # Recipe execution (uses get_backend)
│   └── heal.py                       # Autorepair
├── domain-skills/
│   └── x-com/
│       ├── _meta.yaml                # backend: chrome
│       ├── README.md                 # Site overview
│       └── credentials.md            # Stored credentials
└── _global-failures.yaml             # Documented failures
```

---

## opencode-browser Components (Windows)

| Component | Status | Path |
|-----------|--------|------|
| Extension (Chrome 147 compat) | ⚠ Partial | `C:\Users\jtoem\.opencode-browser\extension` |
| Broker (named pipe) | ✓ Working | `\\.\pipe\opencode-browser-jtoem` |
| CLI tools | ✓ Working | `C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js` |
| Native host manifest | ✓ Registered | `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.opencode.browser_automation` |

**Note on extension:** Extension 4.6.1 shows `hostConnected=false` in Chrome 147 due to compatibility issue. CLI and broker still work correctly — the extension is not required for CLI-based automation. Tabs are owned by the CLI session, not the extension.

---

## Known Issues

1. **Extension hostConnected=false** — Extension 4.6.1 incompatible with Chrome 147. CLI/broker still work. Not blocking.
2. **Text responses instead of JSON** — `browser_navigate` returns "Navigated to..." handled by fallback in `_run_tool`.
3. **Per-tab ownership** — Tabs expire after 5 min inactivity. Create new tab via `browser_open_tab` for long sessions.
4. **Windows Task Scheduler** — Simple schedules only (daily, weekly, every N hours). Complex cron not reliable.
5. **No-overlap for scheduled jobs** — Only on Linux/macOS. Windows has no supervisor for this.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BROWSER_BACKEND` | `playwright` | Backend selection: `playwright` or `chrome` |
| `OPENCODE_BROWSER_CLI` | (install path) | Override CLI path |
| `CHROME_PATH` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | Chrome executable |
| `CHROME_PROFILE` | `Default` | Chrome profile directory |
| `CHROME_PROFILE_DIR` | (auto-detected) | Full profile directory path |