# Browser-Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a browser-agent skill that auto-discovers site structure, executes deterministic recipes, and autonomously repairs failures with LLM fallback after 2 retries.

**Architecture:** Skill sits at `~/.config/opencode/skills/browser-agent/`, uses `C:\Users\jtoem\Repo\browser-harness\helpers.py` for CDP, writes per-site domain skills to `domain-skills/<site>/`.

**Tech Stack:** Python + CDP (via browser-harness helpers) + LLM for diagnosis

---

## Prerequisite: Read Design

Before any task, read `C:\Users\jtoem\.config\opencode\skills\browser-agent\DESIGN.md` in full.

---

## Task 1: Create Skill Skeleton + SKILL.md

**Files:**
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\SKILL.md`
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\_global-failures.yaml`
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools\__init__.py`
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\domain-skills\.gitkeep`

**Step 1: Create _global-failures.yaml**

```yaml
# Cross-site failure index
# Add entries when a fix applies to 2+ sites
version: "1.0"
updated: "2026-04-23"
failures: []
```

**Step 2: Create _tools/__init__.py**

```python
"""Browser-agent tools."""
```

**Step 3: Create SKILL.md**

```markdown
---
name: browser-agent
description: Browser automation with auto-discovery, deterministic recipes, and autonomous repair. Use when automating web tasks, mapping sites, or need browser-based workflows.
---

# browser-agent

Browser automation skill that discovers site structure, executes deterministic recipes, and repairs failures autonomously.

## Quick Start

```bash
# Map a new site
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
from map_site import map_site
map_site("students.ezralms.com")
PY

# Run a recipe
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
from run_recipe import run_recipe
run_recipe("students.ezralms.com", "login")
PY
```

## Structure

```
browser-agent/
├── _global-failures.yaml    # Cross-site fix index
├── _tools/
│   ├── map-site.py          # Auto-discover site structure
│   ├── run-recipe.py        # Execute deterministic recipe
│   └── heal.py              # Autorepair with LLM + 2 retries
└── domain-skills/           # Per-site knowledge (auto-created)
    └── <site>/
        ├── README.md        # Site overview
        ├── nav.md           # Navigation recipes
        ├── forms.md         # Form recipes
        ├── apis.md          # Discovered endpoints
        ├── failures.md      # Site-specific failures
        └── _meta.yaml       # Auto-generated metadata
```

## Key Principles

1. **Screenshots first** — understand page before acting
2. **Coordinate clicks default** — bypasses React/framework complexity
3. **DOM as fallback** — only when coordinates won't work
4. **LLM only on failure** — deterministic execution is the happy path
5. **Fix once, reuse** — failures go to domain-skills + global index

## Autorepair Flow

```
Failure detected → Capture context (URL, screenshot, DOM) →
LLM diagnose → Write fix → Retry × 2 → Still fail → Ask user
```

## Commands

| Action | Tool |
|--------|------|
| Map a site | `map-site.py` |
| Run a recipe | `run-recipe.py` |
| Repair after failure | `heal.py` (called automatically) |

## Reference

- Design: `DESIGN.md`
- Browser harness helpers: `C:\Users\jtoem\Repo\browser-harness\helpers.py`
```

**Step 4: Commit**

```bash
git add browser-agent/
git commit -m "feat: add browser-agent skill skeleton"
```

---

## Task 2: Build `map-site.py` — Auto-discovery

**Files:**
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools\map-site.py`
- Reference: `C:\Users\jtoem\Repo\browser-harness\helpers.py`

**Step 1: Write test stub**

```python
# TBD — map-site test (coordinate with site structure)

def test_map_site_creates_folder():
    import os, shutil
    site = "test-site.example"
    site_path = f"C:/Users/jtoem/.config/opencode/skills/browser-agent/domain-skills/{site}"
    if os.path.exists(site_path):
        shutil.rmtree(site_path)
    # map_site(site, "https://test-site.example")
    # assert os.path.exists(site_path + "/README.md")
```

**Step 2: Write map-site.py**

Core implementation:

```python
"""
map-site.py — Auto-discover site structure and document it.

Usage:
    from map_site import map_site
    map_site("students.ezralms.com")
    # or
    map_site("students.ezralms.com", "https://students.ezralms.com")
"""

import sys, os, json, time, re
from pathlib import Path

# Add browser-harness helpers to path
HARNESS = Path("C:/Users/jtoem/Repo/browser-harness")
sys.path.insert(0, str(HARNESS))
from helpers import (
    goto, page_info, screenshot, js, wait, wait_for_load,
    http_get, cdp, new_tab, list_tabs, switch_tab
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"


def slugify(hostname):
    """Convert hostname to folder-safe name."""
    return hostname.replace(".", "-").replace(":", "-")


def ensure_site_folder(site):
    """Create domain-skills/<site>/ folder with all required files."""
    folder = DOMAIN_SKILLS / slugify(site)
    folder.mkdir(parents=True, exist_ok=True)
    for fname in ["README.md", "nav.md", "forms.md", "apis.md", "failures.md"]:
        fpath = folder / fname
        if not fpath.exists():
            fpath.write_text("")
    meta = folder / "_meta.yaml"
    if not meta.exists():
        meta.write_text(f"mapped: \npages: 0\nendpoints: 0\n")
    return folder


def write_frontmatter(path, site, url, **kwargs):
    """Append YAML frontmatter to a markdown file."""
    fm = ["---", f"site: {site}", f"url: {url}"]
    for k, v in kwargs.items():
        fm.append(f"{k}: {v}")
    fm.append("---\n")
    content = path.read_text() if path.exists() else ""
    path.write_text("\n".join(fm) + "\n" + content)


def crawl_site(root_url, max_pages=20):
    """Crawl same-origin links, return list of (url, title, forms, links)."""
    visited = set()
    to_visit = [root_url]
    results = []
    seen_urls = set()

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            goto(url)
            wait_for_load()
            wait(0.5)

            info = page_info()
            title = info.get("title", "")

            # Collect links
            links_raw = js("""
                Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith(window.location.origin))
                    .filter(h => !h.includes('#'))
                    .slice(0, 50)
            """) or []

            # Collect forms
            forms = js("""
                Array.from(document.forms).map(f => ({
                    action: f.action,
                    method: f.method,
                    id: f.id,
                    name: f.name,
                    inputs: Array.from(f.elements).map(e => ({
                        tag: e.tagName,
                        type: e.type,
                        name: e.name,
                        id: e.id,
                        ariaLabel: e.getAttribute('aria-label')
                    }))
                }))
            """) or []

            results.append({
                "url": url,
                "title": title,
                "forms": forms,
                "links": [l for l in links_raw if l not in seen_urls][:20]
            })
            seen_urls.update(links_raw[:20])

            for link in links_raw[:10]:
                if link not in visited:
                    to_visit.append(link)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

        wait(0.3)

    return results


def intercept_endpoints(root_url, pages):
    """Navigate pages and capture XHR/fetch endpoints."""
    endpoints = []
    seen = set()

    for page in pages[:5]:
        try:
            goto(page["url"])
            wait_for_load()
            wait(1)

            # Get network requests via CDP
            # Note: requires Network.enable — check helpers for capability
            # Fallback: extract from DOM (data-* attributes, fetch calls)
            fetch_calls = js("""
                Array.from(document.querySelectorAll('[data-fetch], [data-api], [data-src]'))
                    .map(el => ({
                        tag: el.tagName,
                        attr: el.getAttribute('data-fetch') || el.getAttribute('data-api') || el.getAttribute('data-src'),
                        id: el.id
                    }))
            """) or []

            for call in fetch_calls:
                key = call.get("attr", "")
                if key and key not in seen:
                    seen.add(key)
                    endpoints.append({"url": key, "source": "dom", "page": page["url"]})

        except Exception as e:
            print(f"Error intercepting {page['url']}: {e}")

    return endpoints


def write_nav_md(folder, pages):
    """Write nav.md with discovered routes."""
    lines = ["# Navigation\n"]
    for p in pages:
        lines.append(f"## {p['title'] or 'Untitled'}\nURL: {p['url']}\n")
        if p["links"]:
            lines.append("Links found:")
            for link in p["links"][:10]:
                lines.append(f"  - {link}")
        lines.append("")
    (folder / "nav.md").write_text("\n".join(lines))


def write_forms_md(folder, pages):
    """Write forms.md with discovered form structures."""
    lines = ["# Forms\n"]
    for p in pages:
        if not p["forms"]:
            continue
        lines.append(f"## {p['url']}\n")
        for form in p["forms"]:
            lines.append(f"### Form: {form.get('id') or form.get('name') or 'unnamed'}")
            lines.append(f"- action: {form.get('action')}")
            lines.append(f"- method: {form.get('method')}")
            lines.append("- inputs:")
            for inp in form.get("inputs", []):
                inp_desc = f"{inp['tag']}"
                if inp.get("type"):
                    inp_desc += f"[{inp['type']}]"
                if inp.get("name"):
                    inp_desc += f" name={inp['name']}"
                if inp.get("id"):
                    inp_desc += f" id={inp['id']}"
                if inp.get("ariaLabel"):
                    inp_desc += f' aria-label="{inp["ariaLabel"]}"'
                lines.append(f"  - {inp_desc}")
            lines.append("")
    (folder / "forms.md").write_text("\n".join(lines))


def write_apis_md(folder, endpoints):
    """Write apis.md with discovered endpoints."""
    lines = ["# Discovered APIs\n"]
    for ep in endpoints:
        lines.append(f"- {ep['url']} (source: {ep.get('source', 'unknown')})")
    (folder / "apis.md").write_text("\n".join(lines))


def write_readme_md(folder, site, root_url, pages, endpoints):
    """Write README.md with site overview."""
    framework = js("""
        (document.querySelector('[data-framework], [data-react-hydrate]') || 
         document.querySelector('script[src*="react"], script[src*="vue"], script[src*="angular"]') ||
         document.querySelector('meta[name="generator"]'))
        ?.content || 'Unknown'
    """) or "Unknown"

    lines = [
        f"# {site}\n",
        f"**URL:** {root_url}\n",
        f"**Framework:** {framework}\n",
        f"**Mapped:** {time.strftime('%Y-%m-%d')}\n",
        f"**Pages discovered:** {len(pages)}\n",
        f"**Endpoints discovered:** {len(endpoints)}\n",
        "\n## Entry Points\n",
    ]
    for p in pages[:5]:
        lines.append(f"- [{p['title'] or 'Untitled'}]({p['url']})")

    (folder / "README.md").write_text("\n".join(lines))


def write_meta_yaml(folder, pages, endpoints):
    """Write _meta.yaml with metadata."""
    import yaml
    meta = {
        "mapped": time.strftime("%Y-%m-%d"),
        "pages": len(pages),
        "endpoints": len(endpoints),
        "last_updated": time.strftime("%Y-%m-%d %H:%M")
    }
    (folder / "_meta.yaml").write_text(yaml.dump(meta))


def map_site(site, root_url=None):
    """
    Auto-discover site structure and write domain-skills/<site>/.

    Args:
        site: Hostname or friendly name (e.g., "students.ezralms.com")
        root_url: Full URL if different from https://<site>
    """
    if not root_url:
        root_url = f"https://{site}"

    print(f"Mapping {site} from {root_url}...")

    # Ensure folder structure exists
    folder = ensure_site_folder(site)

    # Crawl site
    print("Crawling pages...")
    pages = crawl_site(root_url)
    print(f"  Found {len(pages)} pages")

    # Intercept endpoints
    print("Intercepting endpoints...")
    endpoints = intercept_endpoints(root_url, pages)
    print(f"  Found {len(endpoints)} endpoints")

    # Write docs
    print("Writing domain skills...")
    write_nav_md(folder, pages)
    write_forms_md(folder, pages)
    write_apis_md(folder, endpoints)
    write_readme_md(folder, site, root_url, pages, endpoints)
    write_meta_yaml(folder, pages, endpoints)

    # Update _meta.yaml frontmatter
    import yaml
    meta = yaml.safe_load((folder / "_meta.yaml").read_text())
    fm_data = {
        "site": site,
        "url": root_url,
        "mapped": meta.get("mapped", time.strftime("%Y-%m-%d")),
        "pages": len(pages),
        "endpoints": len(endpoints)
    }
    write_frontmatter(folder / "README.md", **fm_data)

    print(f"Done. Mapped {len(pages)} pages, {len(endpoints)} endpoints.")
    print(f"Output: {folder}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: map_site.py <site> [root_url]")
    else:
        site = sys.argv[1]
        url = sys.argv[2] if len(sys.argv) > 2 else None
        map_site(site, url)
```

**Step 3: Run manual test**

```bash
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
# Note: map-site needs full browser session — test via browser-harness
PY
```

**Step 4: Commit**

```bash
git add browser-agent/_tools/map-site.py
git commit -m "feat: add map-site.py auto-discovery"
```

---

## Task 3: Build `run-recipe.py` — Recipe Execution

**Files:**
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools\run-recipe.py`

**Step 1: Write step parser + executor**

```python
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
    click, type_text, press_key, http_get
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


STEP_RE = re.compile(r"^\d+\.\s*\[(\w+)\]\s*(.+)$")


def parse_step(line):
    """Parse '1. [action] target → value' line."""
    m = STEP_RE.match(line.strip())
    if not m:
        return None
    action, rest = m.group(1), m.group(2).strip()
    if " → " in rest:
        target, value = rest.split(" → ", 1)
        return action, target.strip(), value.strip()
    return action, rest, None


def load_recipe(site, recipe_name):
    """Load nav.md or forms.md and extract named recipe."""
    folder = DOMAIN_SKILLS / slugify(site)
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if not fpath.exists():
            continue
        content = fpath.read_text()
        # Find section ## RecipeName
        sections = re.split(r"^##\s+", content, flags=re.M)
        for section in sections:
            if section.strip().startswith(recipe_name):
                return content  # Return full file, let caller find section
    raise FileNotFoundError(f"Recipe '{recipe_name}' not found for {site}")


def execute_step(action, target, value):
    """Execute a single recipe step."""
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
        # Use coordinate click via helpers.click(x, y)
        box = js(f"(()=>{{const e=document.querySelector('{target}');if(!e)return null;const r=e.getBoundingClientRect();return {{x:r.left+r.width/2,y:r.top+r.height/2}}}})()")
        if not box:
            return False
        click(box["x"], box["y"])
        return True

    elif action == "verify":
        result = js(target)  # target is a JS expression
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
    """
    Execute a named recipe for a site.

    Args:
        site: Hostname
        recipe_name: Name of recipe section in nav.md/forms.md
        max_retries: Number of retries before escalation (default 2)

    Returns:
        True if successful, False if failed after retries
    """
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

    # Find the recipe section
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

    # Execute steps
    failure = None
    for i, (action, target, value) in enumerate(steps):
        print(f"Step {i+1}: [{action}] {target}" + (f" → {value}" if value else ""))
        ok = execute_step(action, target, value)
        if not ok:
            failure = {"step": i+1, "action": action, "target": target, "value": value}
            break

    if failure:
        print(f"Step {failure['step']} failed: [{failure['action']}] {failure['target']}")
        # Trigger heal
        from heal import heal
        healed = heal(site, recipe_name, failure, max_retries)
        return healed

    return True
```

**Step 2: Commit**

```bash
git add browser-agent/_tools/run-recipe.py
git commit -m "feat: add run-recipe.py deterministic executor"
```

---

## Task 4: Build `heal.py` — Autorepair

**Files:**
- Create: `C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools\heal.py`

**Step 1: Write heal.py**

```python
"""
heal.py — Autorepair: detect failure, LLM diagnose, write fix, retry.

Called automatically by run-recipe.py on step failure.
"""

import sys, time, json
from pathlib import Path

HARNESS = Path("C:/Users/jtoem/Repo/browser-harness")
sys.path.insert(0, str(HARNESS))
from helpers import (
    page_info, screenshot, js, wait, wait_for_load, http_get
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"
GLOBAL_FAILURES = SKILL_ROOT / "_global-failures.yaml"


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def capture_failure_context(site, recipe_name, failure):
    """Capture screenshot, DOM snapshot, URL for LLM diagnosis."""
    info = page_info()
    shot_path = f"C:/Users/jtoem/.config/opencode/skills/browser-agent/_debug_{int(time.time())}.png"
    try:
        screenshot(shot_path)
    except Exception:
        shot_path = None

    dom_snippet = js("document.body.innerHTML[:1000]") or ""

    return {
        "url": info.get("url", ""),
        "title": info.get("title", ""),
        "screenshot": shot_path,
        "dom_snippet": dom_snippet,
        "recipe": recipe_name,
        "failed_step": failure
    }


def query_llm_for_fix(site, context, domain_skill_excerpt=""):
    """
    Ask LLM to diagnose failure and propose fix.

    Returns:
        dict with keys: symptom, fix, confidence, is_cross_site
    """
    prompt = f"""A recipe step failed on {site}.

Recipe: {context['recipe']}
Failed step: {context['failed_step']}
Current URL: {context['url']}
Page title: {context['title']}
DOM snippet: {context['dom_snippet'][:500]}

Domain skill excerpt:
{domain_skill_excerpt[:1000] if domain_skill_excerpt else 'No domain skill found.'}

Suggest a fix. Return JSON:
{{
  "symptom": "what went wrong",
  "fix": "concrete action to take",
  "confidence": "high|medium|low",
  "is_cross_site": true|false,
  "cross_site_notes": "if cross_site=true, what sites does this apply to"
}}
"""

    # TODO: wire up to actual LLM (claude-code, openai, etc.)
    # For now, return low-confidence placeholder
    # This will be replaced with actual LLM call
    print(f"[heal] Would ask LLM: {prompt[:200]}...")
    return {
        "symptom": "Unknown",
        "fix": "Unknown — LLM not wired up yet",
        "confidence": "low",
        "is_cross_site": False,
        "cross_site_notes": ""
    }


def append_fix_to_failures_md(site, recipe_name, failure, diagnosis):
    """Append fix entry to domain-skills/<site>/failures.md."""
    folder = DOMAIN_SKILLS / slugify(site)
    fpath = folder / "failures.md"
    entry = [
        f"## {site}: {diagnosis['symptom'][:50]}",
        "",
        f"### First seen",
        f"{time.strftime('%Y-%m-%d')}",
        "",
        f"### Recipe",
        f"{recipe_name}",
        "",
        f"### Failed step",
        f"{failure}",
        "",
        f"### Symptom",
        f"{diagnosis['symptom']}",
        "",
        f"### Fix",
        f"{diagnosis['fix']}",
        "",
        f"### Confidence",
        f"{diagnosis['confidence']}",
        "",
        f"### Status",
        f"Auto-repair not yet verified",
        ""
    ]
    existing = fpath.read_text() if fpath.exists() else ""
    fpath.write_text(existing + "\n".join(entry) + "\n")


def append_global_failure(diagnosis):
    """Add cross-site fix to _global-failures.yaml."""
    import yaml
    data = yaml.safe_load(GLOBAL_FAILURES.read_text()) if GLOBAL_FAILURES.exists() else {"version": "1.0", "failures": []}
    new_entry = {
        "id": diagnosis["symptom"][:30].replace(" ", "-").lower(),
        "symptom": diagnosis["symptom"],
        "fix": diagnosis["fix"],
        "confidence": diagnosis["confidence"],
        "sites": [],  # populated from diagnosis
        "first_seen": time.strftime("%Y-%m-%d"),
        "last_verified": time.strftime("%Y-%m-%d")
    }
    data["failures"].append(new_entry)
    GLOBAL_FAILURES.write_text(yaml.dump(data))


def retry_step(site, recipe_name, failure):
    """Re-execute the failed step after fix has been written."""
    from run_recipe import execute_step
    action, target, value = failure["action"], failure["target"], failure.get("value")
    return execute_step(action, target, value)


def heal(site, recipe_name, failure, max_retries=2):
    """
    Main autorepair entry point.

    1. Capture context
    2. Get domain skill excerpt
    3. Query LLM
    4. Write fix to failures.md (+ global if cross-site)
    5. Retry step
    6. If retry fails and retries remain, retry again
    7. If all retries exhausted, return False (escalate to user)
    """
    print(f"[heal] Diagnosing failure for {site}/{recipe_name}")

    # Step 1: Capture context
    context = capture_failure_context(site, recipe_name, failure)

    # Step 2: Get domain skill excerpt
    domain_skill_excerpt = ""
    folder = DOMAIN_SKILLS / slugify(site)
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if fpath.exists():
            domain_skill_excerpt = fpath.read_text()
            break

    # Step 3: Query LLM
    diagnosis = query_llm_for_fix(site, context, domain_skill_excerpt)

    # Step 4: Write fix
    append_fix_to_failures_md(site, recipe_name, failure, diagnosis)
    if diagnosis.get("is_cross_site"):
        append_global_failure(diagnosis)

    if diagnosis["confidence"] == "low":
        print(f"[heal] Low confidence — escalating to user")
        return False

    # Step 5: Retry
    for attempt in range(max_retries):
        print(f"[heal] Retry {attempt + 1}/{max_retries}")
        ok = retry_step(site, recipe_name, failure)
        if ok:
            print(f"[heal] Retry {attempt + 1} succeeded")
            return True

    print(f"[heal] All retries exhausted — escalating to user")
    return False
```

**Step 2: Commit**

```bash
git add browser-agent/_tools/heal.py
git commit -m "feat: add heal.py autorepair with LLM diagnosis"
```

---

## Task 5: Update SKILL.md with full docs

**Files:**
- Modify: `C:\Users\jtoem\.config\opencode\skills\browser-agent\SKILL.md`

Expand SKILL.md to include:
- Full command reference
- Example session
- How to add a recipe manually
- How failures are logged

**Step 1: Update SKILL.md**

(replace content of SKILL.md with expanded version)

**Step 2: Commit**

```bash
git add browser-agent/SKILL.md
git commit -m "docs: expand browser-agent SKILL.md"
```

---

## Task 6: Add browser-agent to skill router

**Files:**
- Modify: `C:\Users\jtoem\.config\opencode\skills\skill-router.yaml`
- Modify: `C:\Users\jtoem\.config\opencode\skills\SKILLS.yaml`

**Step 1: Add to skill-router.yaml**

Add routing entry:

```yaml
  - id: "browser-agent"
    condition: "browser automation, automate browser, map site, browser agent, autorepair"
    skill_path: "browser-agent/SKILL.md"
    mode_required: "any"
    weight: 35
```

**Step 2: Add to SKILLS.yaml**

```yaml
  browser-agent:
    path: "{SKILLS_ROOT}\\browser-agent\\SKILL.md"
    type: "core"
    category: "automation"
```

**Step 3: Commit**

```bash
git add skill-router.yaml SKILLS.yaml
git commit -m "feat: route browser-agent skill"
```

---

## Task 7: First site mapping — test end-to-end

**Files:**
- Map: `students.ezralms.com` (from existing exploration)

**Step 1: Run mapping**

```bash
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
from map_site import map_site
map_site("students.ezralms.com")
PY
```

**Step 2: Verify output**

```bash
ls "C:\Users\jtoem\.config\opencode\skills\browser-agent\domain-skills\students-ezralms-com"
```

Expected files: README.md, nav.md, forms.md, apis.md, failures.md, _meta.yaml

**Step 3: Review generated docs**

Open each file and verify content is reasonable

**Step 4: Commit**

```bash
git add browser-agent/domain-skills/
git commit -m "feat: add domain-skills for students.ezralms.com"
```

---

## Verification Checklist

After all tasks:

- [ ] `browser-agent/SKILL.md` exists and loads
- [ ] `browser-agent/_global-failures.yaml` exists and is valid YAML
- [ ] `browser-agent/_tools/map-site.py` — maps a site to domain-skills/
- [ ] `browser-agent/_tools/run-recipe.py` — executes named recipes
- [ ] `browser-agent/_tools/heal.py` — catches failures, queries LLM, retries
- [ ] `skill-router.yaml` routes browser-agent conditions
- [ ] `students.ezralms.com` mapped and committed
- [ ] All files committed

---

## Execution Options

**1. Subagent-Driven (this session)** — I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** — Open new session with executing-plans, batch execution with checkpoints

Which approach?
