"""
map_site.py — Auto-discover site structure and document it.

Usage (from browser-agent skill dir):
    python -m _tools.map_site students.ezralms.com
    # or
    from _tools.map_site import map_site
    map_site("students.ezralms.com")
"""

import asyncio, sys, time, yaml, re
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"

CRITICAL_PAGES = [
    "/login",
    "/tutor-dashboard",
    "/class/",
    "/lessons/builder",
    "/lessons/",
]


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def ensure_site_folder(site):
    folder = DOMAIN_SKILLS / slugify(site)
    folder.mkdir(parents=True, exist_ok=True)
    for fname in ["README.md", "nav.md", "forms.md", "apis.md", "troubleshooting.md", "selectors.md"]:
        fpath = folder / fname
        if not fpath.exists():
            fpath.write_text("")
    meta = folder / "_meta.yaml"
    if not meta.exists():
        meta.write_text("mapped: \npages: 0\nendpoints: 0\n")
    return folder


def write_frontmatter(path, site, url, **kwargs):
    fm = ["---", f"site: {site}", f"url: {url}"]
    for k, v in kwargs.items():
        fm.append(f"{k}: {v}")
    fm.append("---\n")
    content = path.read_text() if path.exists() else ""
    path.write_text("\n".join(fm) + "\n" + content)


async def crawl_site(page, root_url, max_pages=20):
    visited, to_visit, results, seen_urls = set(), [root_url], [], set()
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)
            title = await page.title()
            
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith(window.location.origin))
                    .filter(h => !h.includes('#'))
                    .slice(0, 50);
            }""") or []
            
            forms_info = await page.evaluate("""() => {
                return Array.from(document.forms).map(f => ({
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
                }));
            }""") or []
            
            iframes_info = await detect_iframes(page)
            
            results.append({
                "url": url,
                "title": title,
                "forms": forms_info,
                "links": [l for l in links if l not in seen_urls][:20],
                "iframes": iframes_info
            })
            seen_urls.update(links[:20])
            for link in links[:10]:
                if link not in visited:
                    to_visit.append(link)
        except Exception as e:
            print(f"Error crawling {url}: {e}")
        await asyncio.sleep(0.3)
    return results


async def intercept_endpoints(page, pages):
    endpoints, seen = [], set()
    for p in pages[:5]:
        try:
            await page.goto(p["url"], wait_until="domcontentloaded")
            await asyncio.sleep(1)
            calls = await page.evaluate("""() => {
                const els = document.querySelectorAll('[data-fetch], [data-api], [data-src]');
                return Array.from(els).map(el => ({
                    tag: el.tagName,
                    attr: el.getAttribute('data-fetch') || el.getAttribute('data-api') || el.getAttribute('data-src'),
                    id: el.id
                }));
            }""") or []
            for c in calls:
                key = c.get("attr", "")
                if key and key not in seen:
                    seen.add(key)
                    endpoints.append({"url": key, "source": "dom", "page": p["url"]})
        except Exception as e:
            print(f"Error intercepting {p['url']}: {e}")
    return endpoints


def write_nav_md(folder, pages):
    lines = ["# Navigation\n"]
    for p in pages:
        lines.append(f"## {p['title'] or 'Untitled'}\nURL: {p['url']}\n")
        iframes = p.get("iframes", [])
        if iframes:
            lines.append("Iframes:")
            for iframe in iframes:
                lines.append(f"  - {iframe.get('name', 'unnamed')} (src: {iframe.get('src', '')[:50]})")
        if p["links"]:
            lines.append("Links found:")
            for link in p["links"][:10]:
                lines.append(f"  - {link}")
        lines.append("")
    (folder / "nav.md").write_text("\n".join(lines))


def write_forms_md(folder, pages):
    lines = ["# Forms\n"]
    for p in pages:
        if not p["forms"]:
            continue
        lines.append(f"## {p['url']}\n")
        for form in p["forms"]:
            fname = form.get("id") or form.get("name") or "unnamed"
            lines.append(f"### Form: {fname}")
            lines.append(f"- action: {form.get('action')}")
            lines.append(f"- method: {form.get('method')}")
            lines.append("- inputs:")
            for inp in form.get("inputs", []):
                d = inp["tag"]
                if inp.get("type"):
                    d += f"[{inp['type']}]"
                if inp.get("name"):
                    d += f" name={inp['name']}"
                if inp.get("id"):
                    d += f" id={inp['id']}"
                if inp.get("ariaLabel"):
                    d += f' aria-label="{inp["ariaLabel"]}"'
                lines.append(f"  - {d}")
            lines.append("")
    (folder / "forms.md").write_text("\n".join(lines))


def write_apis_md(folder, endpoints):
    lines = ["# Discovered APIs\n"]
    for ep in endpoints:
        lines.append(f"- {ep['url']} (source: {ep.get('source', 'unknown')})")
    (folder / "apis.md").write_text("\n".join(lines))


async def detect_iframes(page):
    """Detect all iframes on the current page."""
    iframe_info = await page.evaluate("""() => {
        const iframes = document.querySelectorAll('iframe');
        return Array.from(iframes).map(frame => ({
            src: frame.src || '',
            name: frame.name || '',
            id: frame.id || '',
            sandbox: frame.sandbox?.value || '',
            width: frame.width,
            height: frame.height,
            locatableBy: buildLocator(frame)
        }));
        
        function buildLocator(frame) {
            const locators = [];
            if (frame.id) locators.push(`id="${frame.id}"`);
            if (frame.name) locators.push(`name="${frame.name}"`);
            if (frame.src) {
                const srcMatch = frame.src.match(/\\/([^/]+)\\/?$/);
                if (srcMatch) locators.push(`src containing "${srcMatch[1]}"`);
            }
            return locators.join(', ') || 'src';
        }
    }""")
    return iframe_info


async def detect_stable_selectors(page, url):
    """Reload page and test which selectors survive."""
    await page.goto(url, wait_until="domcontentloaded")
    await asyncio.sleep(1)
    
    elements = await page.evaluate("""() => {
        const result = [];
        const interactives = document.querySelectorAll('button, input, select, textarea, a, [role], [data-testid], [data-id]');
        interactives.forEach(el => {
            const info = {
                tag: el.tagName,
                text: el.textContent?.trim().slice(0, 50),
                role: el.getAttribute('role'),
                id: el.id,
                dataTestid: el.getAttribute('data-testid'),
                dataId: el.getAttribute('data-id'),
                ariaLabel: el.getAttribute('aria-label'),
                name: el.getAttribute('name'),
                type: el.type,
                placeholder: el.placeholder
            };
            result.push(info);
        });
        return result;
    }""")
    
    return elements


def build_selector_candidates(element):
    """Build multiple selector paths for an element."""
    candidates = []
    tag = element.get("tag", "").lower()
    
    if element.get("id"):
        candidates.append(("id", f'#{element["id"]}'))
    if element.get("dataTestid"):
        candidates.append(("data-testid", f'[data-testid="{element["dataTestid"]}"]'))
    if element.get("dataId"):
        candidates.append(("data-id", f'[data-id="{element["dataId"]}"]'))
    if element.get("role"):
        candidates.append(("role", f'[{element["role"]}]'))
    if element.get("ariaLabel"):
        candidates.append(("aria-label", f'[aria-label="{element["ariaLabel"]}"]'))
    if element.get("name"):
        candidates.append(("name", f'{tag}[name="{element["name"]}"]'))
    if element.get("type") and tag == "input":
        candidates.append(("type", f'input[type="{element["type"]}"]'))
    if element.get("placeholder"):
        candidates.append(("placeholder", f'input[placeholder="{element["placeholder"]}"]'))
    if element.get("text"):
        candidates.append(("text", f'{tag}:has-text("{element["text"]}")'))
    
    return candidates


async def verify_selectors_on_reload(page, url, elements):
    """Reload page and verify which selectors from elements list are stable."""
    await page.goto(url, wait_until="domcontentloaded")
    await asyncio.sleep(1)
    
    stable_results = {}
    
    for el in elements:
        element_key = f'{el.get("tag", "unknown")}:{el.get("text", "")[:30]}'
        candidates = build_selector_candidates(el)
        stable_selectors = []
        
        for selector_type, selector in candidates:
            try:
                result = await page.query_selector(selector)
                if result:
                    stable_selectors.append(selector_type)
            except:
                pass
        
        stable_results[element_key] = {
            "candidates": candidates,
            "stable": stable_selectors
        }
    
    return stable_results


def write_selectors_md(folder, stability_results, pages):
    """Write selectors.md with per-page selector tables."""
    lines = ["# Discovered Selectors\n"]
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    for p in pages:
        url = p["url"]
        page_title = p.get("title", "Untitled")
        iframe_info = p.get("iframes", [])
        page_stability = stability_results.get(url, {})
        
        lines.append(f"\n## Page: {page_title} — {url}\n")
        
        lines.append("### Iframes")
        lines.append("| iframe | src | locatable by |")
        lines.append("|--------|-----|--------------|")
        
        if iframe_info:
            for iframe in iframe_info:
                src = iframe.get("src", "")[:50]
                locatable = iframe.get("locatableBy", "src")
                lines.append(f"| {iframe.get('name', 'unnamed')} | {src} | {locatable} |")
        else:
            lines.append("| (none) | — | — |")
        
        lines.append("\n### Selector Priority Table")
        lines.append("| Element | Primary | Fallback | Stable? |")
        lines.append("|---------|---------|----------|---------|")
        
        found_any = False
        for el_key, stability_data in page_stability.items():
            found_any = True
            candidates = stability_data.get("candidates", [])
            stable_list = stability_data.get("stable", [])
            
            primary = ""
            fallback = ""
            stable_status = ""
            
            if candidates:
                primary = candidates[0][1] if len(candidates) > 0 else ""
                fallback = candidates[1][1] if len(candidates) > 1 else ""
            
            if stable_list:
                stable_status = "✓ verified"
            elif candidates:
                stable_status = "? candidate"
            else:
                stable_status = "—"
            
            el_display = el_key[:50]
            lines.append(f"| {el_display} | {primary} | {fallback} | {stable_status} |")
        
        if not found_any:
            lines.append("| — | — | — | — |")
        
        lines.append(f"\n### Discovered on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    (folder / "selectors.md").write_text("\n".join(lines))


async def write_readme_md(folder, site, root_url, pages, endpoints):
    framework = await page.evaluate("""() => {
        const el = document.querySelector('[data-framework], [data-react-hydrate]') ||
                   document.querySelector('script[src*="react"]') ||
                   document.querySelector('script[src*="vue"]') ||
                   document.querySelector('meta[name="generator"]');
        return el ? el.content || 'Unknown' : 'Unknown';
    }""") if 'page' in locals() else "Unknown"
    
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
    meta = {
        "mapped": time.strftime("%Y-%m-%d"),
        "pages": len(pages),
        "endpoints": len(endpoints),
        "last_updated": time.strftime("%Y-%m-%d %H:%M")
    }
    (folder / "_meta.yaml").write_text(yaml.dump(meta))


async def map_site(site, root_url=None, headless=True):
    if not root_url:
        root_url = f"https://{site}"
    print(f"Mapping {site} from {root_url}...")
    folder = ensure_site_folder(site)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        print("Crawling pages...")
        pages = await crawl_site(page, root_url)
        print(f"  Found {len(pages)} pages")
        
        print("Intercepting endpoints...")
        endpoints = await intercept_endpoints(page, pages)
        print(f"  Found {len(endpoints)} endpoints")
        
        print("Detecting stable selectors on critical pages...")
        stability_results = {}
        critical_urls = set()
        for p in pages:
            for crit in CRITICAL_PAGES:
                if crit in p["url"]:
                    critical_urls.add(p["url"])
        
        for url in critical_urls:
            print(f"  Verifying selectors on {url}")
            elements = await detect_stable_selectors(page, url)
            stability_results[url] = await verify_selectors_on_reload(page, url, elements)
        
        print("Writing domain skills...")
        write_nav_md(folder, pages)
        write_forms_md(folder, pages)
        write_apis_md(folder, endpoints)
        write_selectors_md(folder, stability_results, pages)
        await write_readme_md(folder, site, root_url, pages, endpoints)
        write_meta_yaml(folder, pages, endpoints)
        
        meta = yaml.safe_load((folder / "_meta.yaml").read_text())
        write_frontmatter(folder / "README.md", site=site, url=root_url,
            mapped=meta.get("mapped", time.strftime("%Y-%m-%d")),
            pages=len(pages), endpoints=len(endpoints))
        
        await browser.close()
    
    print(f"Done. Mapped {len(pages)} pages, {len(endpoints)} endpoints.")
    print(f"Output: {folder}")


if __name__ == "__main__":
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "students.ezralms.com"
    root_url = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(map_site(site, root_url))