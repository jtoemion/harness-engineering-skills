"""
run_recipe.py — Execute deterministic recipes from domain-skills.

Usage:
    python -m _tools.run_recipe students.ezralms.com login
    # or
    from _tools.run_recipe import run_recipe
    run_recipe("students.ezralms.com", "login")
"""

import asyncio, os, re, sys, yaml
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from _backends import get_backend

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"
ENV_FILE = SKILL_ROOT / ".env"
SELECTORS_FILE = "selectors.md"
META_FILE = "_meta.yaml"
MAX_FALLBACK_LOG_ENTRIES = 20

STEP_RE = re.compile(r"^\d+\.\s*\[(\w+)\]\s*(.+)$")
STEP_SEP = " -> "


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()


def _sub_env(value):
    if not value:
        return value
    for k, v in os.environ.items():
        value = value.replace(f"{{{k}}}", v)
    return value


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def _get_element_key(target):
    if not target:
        return None
    match = re.search(r'[\'"]([^\'"]+)[\'"]', target)
    if match:
        return match.group(1)
    return target


def parse_step(line):
    m = STEP_RE.match(line.strip())
    if not m:
        return None
    action, rest = m.group(1), m.group(2).strip()
    if STEP_SEP in rest:
        target, value = rest.split(STEP_SEP, 1)
        return action, target.strip(), value.strip()
    return action, rest, None


def load_recipe(site, recipe_name):
    folder = DOMAIN_SKILLS / slugify(site)
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if not fpath.exists():
            continue
        content = fpath.read_text()
        sections = re.split(r"^##\s+", content, flags=re.M)
        for section in sections:
            if section.strip().startswith(recipe_name):
                return content
    raise FileNotFoundError(f"Recipe '{recipe_name}' not found for {site} (checked nav.md, forms.md)")


def load_selectors(folder):
    selectors_path = folder / SELECTORS_FILE
    if not selectors_path.exists():
        return {}

    fallback_map = {}
    content = selectors_path.read_text()
    current_page = None

    for line in content.splitlines():
        page_match = re.match(r"^##\s+Page:\s+.+?\s*—\s*(/.+)$", line)
        if page_match:
            current_page = page_match.group(1)
            fallback_map[current_page] = {}
            continue

        if current_page and line.startswith("|") and not line.startswith("| Element"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                element = parts[0]
                primary = parts[1]
                fallback = parts[2] if len(parts) > 2 and parts[2] != "..." else None
                if element and primary:
                    fallbacks = []
                    if primary not in (element, "..."):
                        fallbacks.append(primary)
                    if fallback and fallback not in (element, "...", primary):
                        fallbacks.append(fallback)
                    if fallbacks:
                        fallback_map[current_page][element] = fallbacks

    return fallback_map


def log_fallback_usage(folder, site, page_url, element, primary_failed, fallback_used):
    meta_path = folder / META_FILE
    meta = {}
    if meta_path.exists():
        try:
            meta = yaml.safe_load(meta_path.read_text()) or {}
        except Exception:
            pass

    fallback_log = meta.get("fallback_log", [])
    fallback_log.append({
        "timestamp": datetime.now().isoformat(),
        "site": site,
        "page": page_url,
        "element": element,
        "primary_failed": primary_failed,
        "fallback_worked": fallback_used
    })

    if len(fallback_log) > MAX_FALLBACK_LOG_ENTRIES:
        fallback_log = fallback_log[-MAX_FALLBACK_LOG_ENTRIES:]

    meta["fallback_log"] = fallback_log
    meta["last_fallback_update"] = datetime.now().isoformat()

    try:
        meta_path.write_text(yaml.dump(meta, default_flow_style=False))
    except Exception:
        pass


async def _execute_with_selector(page, action, selector, value):
    if action == "wait":
        for _ in range(30):
            try:
                el = await page.query_selector(selector)
                if el:
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.3)
        return False
    elif action == "type":
        el = await page.query_selector(selector)
        if not el:
            return False
        await el.fill(value)
        return True
    elif action == "click":
        el = await page.query_selector(selector)
        if not el:
            return False
        await el.click()
        return True
    elif action == "press_enter":
        await page.press(selector, "Enter")
        return True
    elif action == "submit":
        form = await page.query_selector(selector)
        if form:
            await form.evaluate("f => f.submit()")
            return True
        return False
    elif action == "verify":
        result = await page.evaluate(selector)
        return value in str(result) if result else False
    return False


async def execute_step(page, action, target, value, fallback_map=None, site=None, folder=None, current_url=None):
    value = _sub_env(value) if value else None

    if action == "goto":
        await page.goto(target, wait_until="domcontentloaded")
        return True
    elif action == "wait_url":
        for _ in range(30):
            if target in page.url:
                return True
            await asyncio.sleep(0.5)
        return False
    elif action == "screenshot":
        await page.screenshot(path=value)
        return True

    result = await _execute_with_selector(page, action, target, value)
    if result:
        return True

    if fallback_map and current_url and site and folder:
        element_key = _get_element_key(target)
        page_fallbacks = fallback_map.get(current_url, {})
        fallbacks = page_fallbacks.get(element_key, [])

        for fallback_selector in fallbacks:
            if fallback_selector == target:
                continue
            result = await _execute_with_selector(page, action, fallback_selector, value)
            if result:
                log_fallback_usage(folder, site, current_url, element_key, target, fallback_selector)
                return True

    return False


async def run_recipe(site, recipe_name, headless=False, max_retries=2):
    folder = DOMAIN_SKILLS / slugify(site)
    if not folder.exists():
        raise FileNotFoundError(f"Site {site} not mapped. Run map_site first.")

    try:
        content = load_recipe(site, recipe_name)
    except FileNotFoundError:
        raise

    fallback_map = load_selectors(folder)

    in_section = False
    steps = []
    for line in content.splitlines():
        if line.strip() == f"## {recipe_name}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            parsed = parse_step(line)
            if parsed:
                steps.append(parsed)

    if not steps:
        raise ValueError(f"No steps found for recipe '{recipe_name}' in domain-skills")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        failure = None
        for i, (action, target, value) in enumerate(steps):
            print(f"Step {i+1}: [{action}] {target}" + (f" -> {value}" if value else ""))
            current_url = page.url if page.url else None
            ok = await execute_step(page, action, target, value, fallback_map=fallback_map, site=site, folder=folder, current_url=current_url)
            if not ok:
                failure = {"step": i+1, "action": action, "target": target, "value": value}
                break

        if failure:
            print(f"Step {failure['step']} failed: [{failure['action']}] {failure['target']}")
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from heal import heal
            healed = await heal(site, recipe_name, failure, page, max_retries)
            await browser.close()
            return healed

        await browser.close()
        return True


if __name__ == "__main__":
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "students.ezralms.com"
    recipe = sys.argv[2] if len(sys.argv) > 2 else "login"
    asyncio.run(run_recipe(site, recipe))