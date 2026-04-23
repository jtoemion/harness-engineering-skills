"""
heal.py — Autorepair: detect failure, LLM diagnose, write fix, retry.

Called automatically by run-recipe.py on step failure.
"""

import sys, time, json, yaml
from pathlib import Path

HARNESS = Path("C:/Users/jtoem/Repo/browser-harness")
sys.path.insert(0, str(HARNESS))
from helpers import (
    page_info, screenshot, js, wait, wait_for_load
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"
GLOBAL_FAILURES = SKILL_ROOT / "_global-failures.yaml"


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def capture_failure_context(site, recipe_name, failure):
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
    prompt = f"""A recipe step failed on {site}.

Recipe: {context['recipe']}
Failed step: {context['failed_step']}
Current URL: {context['url']}
Page title: {context['title']}
DOM snippet: {context['dom_snippet'][:500] if context['dom_snippet'] else 'N/A'}

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
    print(f"[heal] Would ask LLM: {prompt[:200]}...")
    return {
        "symptom": "Unknown",
        "fix": "Unknown — LLM not wired up yet",
        "confidence": "low",
        "is_cross_site": False,
        "cross_site_notes": ""
    }


def append_fix_to_failures_md(site, recipe_name, failure, diagnosis):
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
    data = yaml.safe_load(GLOBAL_FAILURES.read_text()) if GLOBAL_FAILURES.exists() else {"version": "1.0", "failures": []}
    new_entry = {
        "id": diagnosis["symptom"][:30].replace(" ", "-").lower(),
        "symptom": diagnosis["symptom"],
        "fix": diagnosis["fix"],
        "confidence": diagnosis["confidence"],
        "sites": [],
        "first_seen": time.strftime("%Y-%m-%d"),
        "last_verified": time.strftime("%Y-%m-%d")
    }
    data["failures"].append(new_entry)
    GLOBAL_FAILURES.write_text(yaml.dump(data))


def retry_step(site, recipe_name, failure):
    from run_recipe import execute_step
    action, target, value = failure["action"], failure["target"], failure.get("value")
    return execute_step(action, target, value)


def heal(site, recipe_name, failure, max_retries=2):
    print(f"[heal] Diagnosing failure for {site}/{recipe_name}")
    context = capture_failure_context(site, recipe_name, failure)
    domain_skill_excerpt = ""
    folder = DOMAIN_SKILLS / slugify(site)
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if fpath.exists():
            domain_skill_excerpt = fpath.read_text()
            break
    diagnosis = query_llm_for_fix(site, context, domain_skill_excerpt)
    append_fix_to_failures_md(site, recipe_name, failure, diagnosis)
    if diagnosis.get("is_cross_site"):
        append_global_failure(diagnosis)
    if diagnosis["confidence"] == "low":
        print(f"[heal] Low confidence — escalating to user")
        return False
    for attempt in range(max_retries):
        print(f"[heal] Retry {attempt + 1}/{max_retries}")
        ok = retry_step(site, recipe_name, failure)
        if ok:
            print(f"[heal] Retry {attempt + 1} succeeded")
            return True
    print(f"[heal] All retries exhausted — escalating to user")
    return False