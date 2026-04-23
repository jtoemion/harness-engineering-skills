"""
run-recipe.py — Execute deterministic recipes from domain-skills.

Usage:
    from run_recipe import run_recipe
    run_recipe("students.ezralms.com", "login")
"""

import sys, re
from pathlib import Path

HARNESS = Path("C:/Users/jtoem/Repo/browser-harness")
sys.path.insert(0, str(HARNESS))
from helpers import (
    goto, page_info, screenshot, js, wait, wait_for_load,
    click, type_text, press_key
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


STEP_RE = re.compile(r"^\d+\.\s*\[(\w+)\]\s*(.+)$")


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


def execute_step(action, target, value):
    if action == "goto":
        goto(target)
        wait_for_load()
        return True
    elif action == "wait":
        for _ in range(30):
            if js(f"!!document.querySelector('{target}')"):
                return True
            wait(0.3)
        return False
    elif action == "type":
        el = js(f"document.querySelector('{target}')")
        if not el:
            return False
        type_text(value)
        return True
    elif action == "click":
        box = js(f"(()=>{{const e=document.querySelector('{target}');if(!e)return null;const r=e.getBoundingClientRect();return {{x:r.left+r.width/2,y:r.top+r.height/2}}}})()")
        if not box:
            return False
        click(box["x"], box["y"])
        return True
    elif action == "verify":
        result = js(target)
        return value in str(result) if result else False
    elif action == "wait_url":
        for _ in range(30):
            info = page_info()
            if value in info.get("url", ""):
                return True
            wait(0.5)
        return False
    return False


def run_recipe(site, recipe_name, max_retries=2):
    folder = DOMAIN_SKILLS / slugify(site)
    if not folder.exists():
        raise FileNotFoundError(f"Site {site} not mapped. Run map-site first.")
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
    failure = None
    for i, (action, target, value) in enumerate(steps):
        print(f"Step {i+1}: [{action}] {target}" + (f" → {value}" if value else ""))
        ok = execute_step(action, target, value)
        if not ok:
            failure = {"step": i+1, "action": action, "target": target, "value": value}
            break
    if failure:
        print(f"Step {failure['step']} failed: [{failure['action']}] {failure['target']}")
        from heal import heal
        healed = heal(site, recipe_name, failure, max_retries)
        return healed
    return True