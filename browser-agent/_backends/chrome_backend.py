import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

OPENCODE_BROWSER_CLI = os.environ.get(
    "OPENCODE_BROWSER_CLI",
    r"C:\Users\jtoem\.bun\install\cache\@different-ai\opencode-browser@4.6.1@@@1\bin\cli.js"
)

CHROME_PATH = os.environ.get(
    "CHROME_PATH",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

DEFAULT_PROFILE = os.environ.get("CHROME_PROFILE", "Default")


def _parse_cli_json(stdout):
    """Extract JSON from opencode-browser CLI output, skipping ANSI and progress lines."""
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    cleaned = ansi_escape.sub('', stdout)
    lines = cleaned.split("\n")

    # Single-line JSON: try to find any line that starts with '{' or '[' (arrays or objects)
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                continue

    # Multi-line formatted JSON: find line with just "{" or "["
    start = None
    start_char = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "{":
            start = i
            start_char = "{"
            break
        if stripped == "[":
            start = i
            start_char = "["
            break

    if start is not None:
        brace_count = 0
        json_lines = []
        for i in range(start, len(lines)):
            line = lines[i]
            for ch in line:
                if ch == '{' or ch == '[':
                    brace_count += 1
                elif ch == '}' or ch == ']':
                    brace_count -= 1
            json_lines.append(line)
            if brace_count == 0 and i > start:
                break

        json_str = "\n".join(json_lines).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return None


def _run_cli_sync(tool, args=None):
    """Run CLI tool synchronously and return parsed JSON or None."""
    args = args or {}
    json_args = json.dumps(args)
    r = subprocess.run(
        ["node", OPENCODE_BROWSER_CLI, "tool", tool, json_args],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        shell=False
    )
    stdout = r.stdout or ""
    result = _parse_cli_json(stdout)
    if result is not None:
        return result

    output = r.stdout.strip()
    for line in output.split("\n"):
        stripped = line.strip()
        if stripped.startswith("Navigated"):
            return {"ok": True}
        if stripped.startswith("Clicked"):
            return {"ok": True}
        if stripped.startswith("Typed"):
            return {"ok": True}

    err = r.stderr.strip() if r.stderr else ""
    raise RuntimeError(f"Tool {tool} failed: {err or output[:200]}")


def check_broker_status():
    """Check if opencode-browser broker is running."""
    result = _run_cli_sync("browser_status")
    if result and result.get("broker"):
        return True
    return False


def ensure_chrome_running():
    """Ensure opencode-browser broker is running. Extension connection optional."""
    if check_broker_status():
        return True

    print("opencode-browser: Broker not running. Please start it with: opencode-browser broker")
    raise RuntimeError("opencode-browser: Broker not available")


class ChromeBackend:
    """Backend using opencode-browser CLI via native messaging broker."""

    def __init__(self):
        self._tab_id = None
        self._url = None

    async def launch(self, headless=False):
        ensure_chrome_running()
        result = await self._run_tool("browser_open_tab", {})
        self._tab_id = result.get("tabId")
        return self

    async def new_page(self):
        ensure_chrome_running()
        result = await self._run_tool("browser_open_tab", {"active": True})
        self._tab_id = result.get("tabId")
        return ChromePage(self)

    async def goto(self, url, wait_until="domcontentloaded"):
        ensure_chrome_running()
        args = {"url": url}
        if self._tab_id is not None:
            args["tabId"] = self._tab_id
        result = await self._run_tool("browser_navigate", args)
        self._url = url
        return self

    async def close(self):
        if self._tab_id is not None:
            try:
                await self._run_tool("browser_close_tab", {"tabId": self._tab_id})
            except Exception:
                pass

    async def _run_tool(self, tool, args):
        ensure_chrome_running()
        json_args = json.dumps(args)
        r = subprocess.run(
            ["node", OPENCODE_BROWSER_CLI, "tool", tool, json_args],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=False
        )
        stdout = r.stdout or ""
        result = _parse_cli_json(stdout)
        if result is not None:
            return result

        output = r.stdout.strip()
        for line in output.split("\n"):
            stripped = line.strip()
            if stripped.startswith("Navigated"):
                return {"ok": True}
            if stripped.startswith("Clicked"):
                return {"ok": True}
            if stripped.startswith("Typed"):
                return {"ok": True}

        err = r.stderr.strip() if r.stderr else ""
        raise RuntimeError(f"Tool {tool} failed: {err or output[:200]}")

    @property
    def url(self):
        return self._url


class ChromePage:
    def __init__(self, backend):
        self._backend = backend

    @property
    def _tab_id(self):
        return self._backend._tab_id

    async def query_selector(self, selector):
        args = {"selector": selector, "mode": "exists"}
        if self._tab_id is not None:
            args["tabId"] = self._tab_id
        result = await self._backend._run_tool("browser_query", args)
        return ChromeElement(self, selector) if result and result.get("found") else None

    async def click(self, selector):
        args = {"selector": selector}
        if self._tab_id is not None:
            args["tabId"] = self._tab_id
        await self._backend._run_tool("browser_click", args)
        return True

    async def fill(self, selector, value):
        args = {"selector": selector, "text": value}
        if self._tab_id is not None:
            args["tabId"] = self._tab_id
        await self._backend._run_tool("browser_type", args)
        return True

    async def screenshot(self, path):
        args = {"path": path}
        if self._tab_id is not None:
            args["tabId"] = self._tab_id
        await self._backend._run_tool("browser_screenshot", args)
        return True

    @property
    def url(self):
        return self._backend.url


class ChromeElement:
    def __init__(self, page, selector):
        self._page = page
        self._selector = selector

    async def click(self):
        await self._page.click(self._selector)

    async def fill(self, value):
        await self._page.fill(self._selector, value)