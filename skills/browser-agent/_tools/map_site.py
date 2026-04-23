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

SKILL_ROOT = Path(__file__).parent.parent
DOMAIN_SKILLS = SKILL_ROOT / "domain-skills"


def slugify(hostname):
    return hostname.replace(".", "-").replace(":", "-")


def ensure_site_folder(site):
    folder = DOMAIN_SKILLS / slugify(site)
    folder.mkdir(parents=True, exist_ok=True)
    for fname in ["README.md", "nav.md", "forms.md", "apis.md", "failures.md"]:
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
            
            results.append({
                "url": url,
                "title": title,
                "forms": forms_info,
                "links": [l for l in links if l not in seen_urls][:20]
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
        
        print("Writing domain skills...")
        write_nav_md(folder, pages)
        write_forms_md(folder, pages)
        write_apis_md(folder, endpoints)
        await write_readme_md(folder, site, root_url, pages, endpoints)
        write_meta_yaml(folder, pages, endpoints)
        
        # Write frontmatter on README
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