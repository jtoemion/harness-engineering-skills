"""
self_test.py — Smoke test for browser-agent tools.
Run with: python -m _tools.self_test
"""

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

def test_imports():
    from _tools import heal, map_site, run_recipe
    from _backends import get_backend, parse_selector
    assert heal is not None
    assert map_site is not None
    assert run_recipe is not None

def test_slugify():
    from _tools.run_recipe import slugify
    assert slugify("students.ezralms.com") == "students-ezralms-com"
    assert slugify("api.example.com:8080") == "api-example-com-8080"

def test_parse_step():
    from _tools.run_recipe import parse_step
    result = parse_step("1. [goto] https://site.com/login")
    assert result == ("goto", "https://site.com/login", None)

    result = parse_step("3. [type] #username -> testuser")
    assert result == ("type", "#username", "testuser")

    result = parse_step("5. [click] button[type=submit]")
    assert result == ("click", "button[type=submit]", None)

def test_step_regex():
    from _tools.run_recipe import STEP_RE
    assert STEP_RE.match("1. [goto] https://site.com/login")
    assert STEP_RE.match("10. [click] #submit-btn")
    assert not STEP_RE.match("not a step")

def test_load_env():
    from _tools.run_recipe import _load_env
    _load_env()

def test_heal_query_llm_signature():
    from _tools.heal import query_llm_for_fix
    result = query_llm_for_fix("test.site", {"recipe": "test", "failed_step": "click #btn", "url": "http://x.com", "title": "X", "dom_snippet": "..."}, "")
    assert isinstance(result, dict)
    assert "symptom" in result
    assert "fix" in result

def test_capture_failure_context():
    import asyncio
    from _tools.heal import capture_failure_context
    async def dummy():
        class MockPage:
            url = "http://test.com"
            async def screenshot(self, path): pass
            async def title(self): return "Test"
            async def evaluate(self, s): return "html"
        result = await capture_failure_context(MockPage(), "test.site", "login", "click #btn")
        assert result["url"] == "http://test.com"
        assert result["recipe"] == "login"
        assert result["failed_step"] == "click #btn"
    asyncio.run(dummy())

def test_selector_parser():
    from _backends.selector_parser import parse_selector
    assert parse_selector("label:Email") == '[aria-label="Email"]'
    assert parse_selector("placeholder:Search") == '[placeholder="Search"]'

def test_backend_get():
    from _backends import get_backend
    backend = get_backend()
    assert backend is not None

def test_heal_slugify():
    from _tools.heal import slugify
    assert slugify("example.com") == "example-com"

def test_map_site_slugify():
    from _tools.map_site import slugify
    assert slugify("example.com") == "example-com"

if __name__ == "__main__":
    tests = [
        test_imports,
        test_slugify,
        test_parse_step,
        test_step_regex,
        test_load_env,
        test_heal_query_llm_signature,
        test_capture_failure_context,
        test_selector_parser,
        test_backend_get,
        test_heal_slugify,
        test_map_site_slugify,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
        except Exception as e:
            print(f"  FAIL: {t.__name__} — {e}")
            failed += 1

    if failed:
        print(f"\n{failed} test(s) failed")
        sys.exit(1)
    else:
        print("\nAll tests passed")
        sys.exit(0)