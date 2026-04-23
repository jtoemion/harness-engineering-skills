"""
heal.py — Autorepair: detect failure, LLM diagnose, write fix, retry.

Called automatically by run_recipe.py on step failure.
"""

import asyncio, json, os, time, yaml
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"
GLOBAL_FAILURES = SKILL_ROOT / "_global-failures.yaml"
ENV_FILE = SKILL_ROOT / ".env"


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


async def capture_failure_context(page, site, recipe_name, failure):
    try:
        await page.screenshot(path=str(SKILL_ROOT / f"_debug_{int(time.time())}.png"))
    except Exception:
        pass
    try:
        dom_snippet = await page.evaluate("document.body.innerHTML[:1000]")
    except Exception:
        dom_snippet = ""
    return {
        "url": page.url,
        "title": await page.title() if page else "",
        "dom_snippet": dom_snippet,
        "recipe": recipe_name,
        "failed_step": failure
    }


def _build_prompt(site, context, domain_skill_excerpt):
    return f"""A recipe step failed on {site}.

Recipe: {context['recipe']}
Failed step: {context['failed_step']}
Current URL: {context['url']}
Page title: {context['title']}
DOM snippet: {context['dom_snippet'][:500] if context['dom_snippet'] else 'N/A'}

Domain skill excerpt:
{domain_skill_excerpt[:1000] if domain_skill_excerpt else 'No domain skill found.'}

Suggest a fix for the failed step. Return ONLY valid JSON:
{{"symptom": "...", "fix": "...", "confidence": "high|medium|low", "is_cross_site": true|false, "cross_site_notes": "..."}}
"""


def _call_openrouter(prompt):
    import urllib.request, urllib.error
    data = json.dumps({
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://browser-agent.local",
            "X-Title": "browser-agent"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def _call_gemini(prompt):
    import urllib.request, urllib.error
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["candidates"][0]["content"]["parts"][0]["text"]


def _parse_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def query_llm_for_fix(site, context, domain_skill_excerpt=""):
    prompt = _build_prompt(site, context, domain_skill_excerpt)

    if OPENROUTER_API_KEY:
        try:
            raw = _call_openrouter(prompt)
            return _parse_json_response(raw)
        except Exception as e:
            print(f"[heal] OpenRouter failed: {e}")

    if GEMINI_API_KEY:
        try:
            raw = _call_gemini(prompt)
            return _parse_json_response(raw)
        except Exception as e:
            print(f"[heal] Gemini fallback failed: {e}")

    return {
        "symptom": "Unknown",
        "fix": "Unknown — no API keys configured",
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


async def retry_step(page, failure):
    from run_recipe import execute_step
    action, target, value = failure["action"], failure["target"], failure.get("value")
    return await execute_step(page, action, target, value)


async def heal(site, recipe_name, failure, page=None, max_retries=2):
    print(f"[heal] Diagnosing failure for {site}/{recipe_name}")

    context = await capture_failure_context(page, site, recipe_name, failure)

    domain_skill_excerpt = ""
    folder = DOMAIN_SKILLS / slugify(site)
    for fname in ["nav.md", "forms.md"]:
        fpath = folder / fname
        if fpath.exists():
            domain_skill_excerpt = fpath.read_text()
            break

    diagnosis = await asyncio.get_event_loop().run_in_executor(
        None, query_llm_for_fix, site, context, domain_skill_excerpt
    )
    append_fix_to_failures_md(site, recipe_name, failure, diagnosis)

    if diagnosis.get("is_cross_site"):
        append_global_failure(diagnosis)

    if diagnosis["confidence"] == "low":
        print(f"[heal] Low confidence — escalating to user")
        return False

    for attempt in range(max_retries):
        print(f"[heal] Retry {attempt + 1}/{max_retries}")
        ok = await retry_step(page, failure)
        if ok:
            print(f"[heal] Retry {attempt + 1} succeeded")
            return True

    print(f"[heal] All retries exhausted — escalating to user")
    return False