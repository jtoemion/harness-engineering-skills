"""
run_recipe.py — Execute deterministic recipes from domain-skills.

Usage:
    python -m _tools.run_recipe students.ezralms.com login
    # or
    from _tools.run_recipe import run_recipe
    run_recipe("students.ezralms.com", "login")
"""

import asyncio, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"

STEP_RE = re.compile(r"^\d+\.\s*\[(\w+)\]\s*(.+)$")


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def parse_step(line):
    m = STEP_RE.match(line.strip())
    if not m:
        return None
    action, rest = m.group(1), m.group(2).strip()
    if " → " in rest:
        target, value = rest.split(" → ", 1)
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
    raise FileNotFoundError(f"Recipe '{recipe_name}' not found for {site}")


async def execute_step(page, action, target, value):
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
    elif action == "verify":
        result = await page.evaluate(target)
        return value in str(result) if result else False
    elif action == "wait_url":
        for _ in range(30):
            if value in page.url:
                return True
            await asyncio.sleep(0.5)
        return False
    return False


async def run_recipe(site, recipe_name, headless=True, max_retries=2):
    folder = DOMAIN_SKILLS / slugify(site)
    if not folder.exists():
        raise FileNotFoundError(f"Site {site} not mapped. Run map_site first.")
    
    recipe_file = None
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if fpath.exists():
            recipe_file = fpath
            break
    if not recipe_file:
        raise FileNotFoundError(f"No recipe file found for {site}")
    
    content = recipe_file.read_text()
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
        raise ValueError(f"No steps found for recipe '{recipe_name}' in {recipe_file}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        failure = None
        for i, (action, target, value) in enumerate(steps):
            print(f"Step {i+1}: [{action}] {target}" + (f" → {value}" if value else ""))
            ok = await execute_step(page, action, target, value)
            if not ok:
                failure = {"step": i+1, "action": action, "target": target, "value": value}
                break
        
        if failure:
            print(f"Step {failure['step']} failed: [{failure['action']}] {failure['target']}")
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