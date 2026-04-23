"""
run_recipe.py — Execute deterministic recipes from domain-skills.

Usage:
    python -m _tools.run_recipe students.ezralms.com login
    # or
    from _tools.run_recipe import run_recipe
    run_recipe("students.ezralms.com", "login")
"""

import asyncio, os, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"
ENV_FILE = SKILL_ROOT / ".env"

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


async def execute_step(page, action, target, value):
    value = _sub_env(value) if value else None

    if action == "goto":
        await page.goto(target, wait_until="domcontentloaded")
        return True
    elif action == "wait":
        for _ in range(30):
            try:
                el = await page.query_selector(target)
                if el:
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.3)
        return False
    elif action == "type":
        el = await page.query_selector(target)
        if not el:
            return False
        await el.fill(value)
        return True
    elif action == "click":
        el = await page.query_selector(target)
        if not el:
            return False
        await el.click()
        return True
    elif action == "press_enter":
        await page.press(target, "Enter")
        return True
    elif action == "submit":
        form = await page.query_selector(target)
        if form:
            await form.evaluate("f => f.submit()")
            return True
        return False
    elif action == "verify":
        result = await page.evaluate(target)
        return value in str(result) if result else False
    elif action == "wait_url":
        for _ in range(30):
            if target in page.url:
                return True
            await asyncio.sleep(0.5)
        return False
    elif action == "screenshot":
        await page.screenshot(path=value)
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
            ok = await execute_step(page, action, target, value)
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