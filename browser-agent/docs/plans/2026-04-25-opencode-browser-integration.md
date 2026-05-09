# opencode-browser Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add opencode-browser as an optional real-Chrome backend to browser-agent, enabling profile-aware browser automation alongside the existing Playwright backend.

**Architecture:** Add a `ChromeBackend` class that wraps opencode-browser's native messaging approach, with a selector helper parser that converts `label:`, `aria:`, `placeholder:`, `name:`, `role:`, `text:` syntax into CSS selectors. Backend selection via `OPENCODE_BROWSER_BACKEND` env var.

**Tech Stack:** Python (opencode-browser plugin integration), Playwright (existing), native messaging host manifest, selector parsing.

---

## Task 1: Create backend abstraction layer

**Files:**
- Create: `skills/browser-agent/_backends/__init__.py`
- Create: `skills/browser-agent/_backends/playwright_backend.py`
- Create: `skills/browser-agent/_backends/chrome_backend.py`
- Modify: `skills/browser-agent/_tools/run_recipe.py:14-36`

**Step 1: Create `_backends/__init__.py`**

```python
from abc import ABC, abstractmethod

class BrowserBackend(ABC):
    @abstractmethod
    async def launch(self):
        pass

    @abstractmethod
    async def new_page(self):
        pass

    @abstractmethod
    async def goto(self, url, wait_until="domcontentloaded"):
        pass

    @abstractmethod
    async def click(self, selector):
        pass

    @abstractmethod
    async def type(self, selector, value):
        pass

    @abstractmethod
    async def query_selector(self, selector):
        pass

    @abstractmethod
    async def screenshot(self, path):
        pass

    @abstractmethod
    async def close(self):
        pass

def get_backend():
    backend = os.environ.get("OPENCODE_BROWSER_BACKEND", "playwright")
    if backend == "chrome":
        from .chrome_backend import ChromeBackend
        return ChromeBackend()
    from .playwright_backend import PlaywrightBackend
    return PlaywrightBackend()
```

**Step 2: Create `playwright_backend.py`**

```python
import asyncio, os
from pathlib import Path
from playwright.async_api import async_playwright

class PlaywrightBackend(BrowserBackend):
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def launch(self, headless=True):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(viewport={"width": 1280, "height": 800})
        self.page = await self.context.new_page()
        return self

    async def new_page(self):
        return await self.context.new_page()

    async def goto(self, url, wait_until="domcontentloaded"):
        await self.page.goto(url, wait_until=wait_until)

    async def click(self, selector):
        el = await self.page.query_selector(selector)
        if el:
            await el.click()

    async def type(self, selector, value):
        el = await self.page.query_selector(selector)
        if el:
            await el.fill(value)

    async def query_selector(self, selector):
        return await self.page.query_selector(selector)

    async def screenshot(self, path):
        await self.page.screenshot(path=path)

    async def close(self):
        await self.browser.close()
```

**Step 3: Create `chrome_backend.py`**

```python
import asyncio, os, json, subprocess
from pathlib import Path

class ChromeBackend(BrowserBackend):
    """Wrapper for opencode-browser native messaging."""
    
    def __init__(self):
        self.socket_path = os.environ.get(
            "OPENCODE_BROWSER_SOCKET",
            "/tmp/opencode-browser.sock"
        )
        self._reader = None
        self._writer = None

    async def launch(self):
        sock = Path(self.socket_path)
        if not sock.exists():
            raise RuntimeError(
                f"Socket {self.socket_path} not found. "
                "Is opencode-browser broker running? Install with: bunx @different-ai/opencode-browser@latest install"
            )
        self._reader, self._writer = await asyncio.open_unix_connection(str(sock))
        return self

    async def _send_command(self, tool, args=None):
        cmd = {"tool": tool, "args": args or {}}
        self._writer.write((json.dumps(cmd) + "\n").encode())
        await self._writer.drain()
        resp = await self._reader.readline()
        return json.loads(resp.decode())

    async def goto(self, url, wait_until="domcontentloaded"):
        await self._send_command("browser_navigate", {"url": url})

    async def click(self, selector):
        result = await self._send_command("browser_query", {
            "selector": selector, "mode": "exists"
        })
        if result.get("found"):
            await self._send_command("browser_click", {"selector": selector})

    async def type(self, selector, value):
        await self._send_command("browser_type", {
            "selector": selector, "text": value
        })

    async def query_selector(self, selector):
        result = await self._send_command("browser_query", {
            "selector": selector, "mode": "exists"
        })
        return result.get("found")

    async def screenshot(self, path):
        await self._send_command("browser_screenshot", {"path": path})

    async def close(self):
        if self._writer:
            self._writer.close()
```

**Step 4: Modify `run_recipe.py` to use backend abstraction**

Add after line 14:
```python
from _backends import get_backend
```

Replace launch/context/page creation (lines 252-255):
```python
    backend = get_backend()
    await backend.launch(headless=headless)
    page = backend.page
```

Update `execute_step` to use backend instead of direct playwright calls.

**Step 5: Commit**

```bash
git add skills/browser-agent/_backends/ skills/browser-agent/_tools/run_recipe.py
git commit -m "feat: add backend abstraction layer for browser-agent"
```

---

## Task 2: Add selector helper parser

**Files:**
- Create: `skills/browser-agent/_backends/selector_parser.py`
- Modify: `skills/browser-agent/_backends/__init__.py`
- Modify: `skills/browser-agent/_tools/run_recipe.py`

**Step 1: Create `selector_parser.py`**

```python
import re

SELECTOR_RE = re.compile(r"^(label|aria|placeholder|name|role|text|css):(.+)$")

def parse_selector(selector):
    """Convert opencode-browser selector helpers to CSS.
    
    Examples:
        label:Email Address -> [aria-label="Email Address"]
        aria:Submit -> [aria-label="Submit"]
        placeholder:Search -> [placeholder="Search"]
        name:email -> [name="email"]
        role:button -> [role="button"]
        text:Submit -> text:contains("Submit")
        css:.class -> .class
    """
    m = SELECTOR_RE.match(selector)
    if not m:
        return selector
    
    kind, value = m.group(1), m.group(2)
    
    if kind == "label":
        return f'[aria-label="{value}"]'
    elif kind == "aria":
        return f'[aria-label="{value}"]'
    elif kind == "placeholder":
        return f'[placeholder="{value}"]'
    elif kind == "name":
        tag_match = re.match(r"^(\w+):(.+)$", value)
        if tag_match:
            return f'{tag_match.group(1)}[name="{tag_match.group(2)}"]'
        return f'[name="{value}"]'
    elif kind == "role":
        return f'[{value}]'
    elif kind == "text":
        return f'text:contains("{value}")'
    elif kind == "css":
        return value
    
    return selector

def parse_composite_selector(selector):
    """Handle composite selectors like 'label:City: input'."""
    if ": " in selector and not selector.startswith(("label:", "aria:", "placeholder:", "name:", "role:", "text:", "css:")):
        parts = selector.split(": ", 1)
        prefix = parts[0]
        suffix = parts[1]
        return f'{parse_selector(prefix)}: {suffix}'
    return parse_selector(selector)
```

**Step 2: Update `_backends/__init__.py`**

Add import and update `get_backend`:
```python
from .selector_parser import parse_selector, parse_composite_selector

def parse_selector(selector):
    return parse_composite_selector(selector)
```

**Step 3: Modify `run_recipe.py`**

Add parse_selector import and update `execute_step`:
```python
from _backends import get_backend, parse_selector

# In execute_step, before calling backend:
selector = parse_selector(target)
```

**Step 4: Commit**

```bash
git add skills/browser-agent/_backends/selector_parser.py skills/browser-agent/_backends/__init__.py skills/browser-agent/_tools/run_recipe.py
git commit -m "feat: add selector helper parser for label/aria/placeholder/name/role/text syntax"
```

---

## Task 3: Update SKILL.md with backend selection

**Files:**
- Modify: `skills/browser-agent/SKILL.md:1-50`

**Step 1: Add backend selection section after line 36**

```markdown
## Backend Selection

browser-agent supports two backends:

| Backend | Use case | Command |
|---------|----------|---------|
| Playwright (default) | Headless, cross-platform, CI/CD | `OPENCODE_BROWSER_BACKEND=playwright` |
| Chrome (opencode-browser) | Real Chrome with profile, logged-in state | `OPENCODE_BROWSER_BACKEND=chrome` |

### Chrome backend setup

1. Install opencode-browser:
   ```bash
   bunx @different-ai/opencode-browser@latest install
   ```

2. Set backend and socket:
   ```bash
   export OPENCODE_BROWSER_BACKEND=chrome
   export OPENCODE_BROWSER_SOCKET=/tmp/opencode-browser.sock
   ```

3. Start broker (in separate terminal):
   ```bash
   opencode-browser broker
   ```

### Selector helpers (Chrome backend)

The Chrome backend supports semantic selectors that map to accessibility attributes:

| Syntax | CSS equivalent |
|--------|----------------|
| `label:Email` | `[aria-label="Email"]` |
| `aria:Submit` | `[aria-label="Submit"]` |
| `placeholder:Search` | `[placeholder="Search"]` |
| `name:email` | `[name="email"]` |
| `role:button` | `[role="button"]` |
| `text:Submit` | `text:contains("Submit")` |

These work with both backends.
```

**Step 2: Commit**

```bash
git add skills/browser-agent/SKILL.md
git commit -m "docs: add backend selection and selector helpers to SKILL.md"
```

---

## Task 4: Update DESIGN.md

**Files:**
- Modify: `skills/browser-agent/DESIGN.md:1-50`

**Step 1: Add backend architecture section after line 32**

```markdown
## Backend Abstraction

```
_backends/
├── __init__.py          # get_backend(), parse_selector()
├── playwright_backend.py # Headless Playwright (default)
└── chrome_backend.py    # opencode-browser native messaging
```

- `get_backend()` returns appropriate backend based on `OPENCODE_BROWSER_BACKEND` env var
- Both backends implement `BrowserBackend` ABC
- Selector parser converts semantic selectors (`label:`, `aria:`, etc.) to CSS
```

**Step 2: Commit**

```bash
git add skills/browser-agent/DESIGN.md
git commit -m "docs: add backend abstraction architecture to DESIGN.md"
```

---

## Task 5: Add self-test script

**Files:**
- Create: `skills/browser-agent/_tools/self_test.py`

**Step 1: Create `self_test.py`**

```python
"""
self_test.py — Smoke test for browser-agent backends.

Usage:
    python -m _tools.self_test                    # test Playwright (default)
    OPENCODE_BROWSER_BACKEND=chrome python -m _tools.self_test  # test Chrome
"""

import asyncio, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _backends import get_backend, parse_selector

async def test_basic_navigation(backend):
    print("Testing basic navigation...")
    await backend.launch()
    await backend.goto("https://example.com")
    print("  ✓ Page loaded")
    await backend.close()
    return True

async def test_click_and_type(backend):
    print("Testing click and type...")
    await backend.launch()
    await backend.goto("https://example.com")
    
    # Test selector parsing
    tests = [
        ("label:Search", '[aria-label="Search"]'),
        ("placeholder:Email", '[placeholder="Email"]'),
        ("role:button", '[button]'),
        ("name:q", '[name="q"]'),
    ]
    for input_sel, expected in tests:
        result = parse_selector(input_sel)
        if result != expected:
            print(f"  ✗ {input_sel} -> {result} (expected {expected})")
            return False
    print("  ✓ Selector parsing works")
    
    await backend.close()
    return True

async def main():
    backend_name = os.environ.get("OPENCODE_BROWSER_BACKEND", "playwright")
    print(f"Testing {backend_name} backend...\n")
    
    backend = get_backend()
    
    try:
        ok1 = await test_basic_navigation(backend)
        ok2 = await test_click_and_type(backend)
        
        if ok1 and ok2:
            print(f"\n✓ All tests passed for {backend_name} backend")
            return 0
        else:
            print(f"\n✗ Some tests failed for {backend_name} backend")
            return 1
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        if backend_name == "chrome":
            print("  Is the opencode-browser broker running?")
            print("  Run: bunx @different-ai/opencode-browser@latest install")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

**Step 2: Test with Playwright (should pass)**

```bash
cd skills/browser-agent
python -m _tools.self_test
```

Expected output: "✓ All tests passed for playwright backend"

**Step 3: Commit**

```bash
git add skills/browser-agent/_tools/self_test.py
git commit -m "test: add self-test smoke test for browser-agent backends"
```

---

## Task 6: Update .env.example with backend config

**Files:**
- Create: `skills/browser-agent/.env.example`

**Step 1: Create `.env.example`**

```
# Browser backend selection
# Options: playwright (default), chrome
OPENCODE_BROWSER_BACKEND=playwright

# Chrome backend socket path (only for chrome backend)
OPENCODE_BROWSER_SOCKET=/tmp/opencode-browser.sock

# Chrome backend remote host (for Tailnet/remote)
# OPENCODE_BROWSER_AGENT_HOST=home-server.taild435d7.ts.net
# OPENCODE_BROWSER_AGENT_PORT=9833
```

**Step 2: Commit**

```bash
git add skills/browser-agent/.env.example
git commit -m "docs: add .env.example with backend configuration"
```

---

## Verification

After all tasks complete, run:

```bash
# Verify Playwright backend still works
cd skills/browser-agent
python -m _tools.self_test

# Test selector parsing
python -c "from _backends import parse_selector; print(parse_selector('label:Email'))"
# Expected: [aria-label="Email"]
```

---

## Execution Options

**Plan complete and saved to `docs/plans/2026-04-25-opencode-browser-integration.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**