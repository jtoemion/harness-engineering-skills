"""
map-site.py — Auto-discover site structure and document it.

Usage:
    from map_site import map_site
    map_site("students.ezralms.com")
"""

import sys, os, json, time, re, yaml
from pathlib import Path

HARNESS = Path("C:/Users/jtoem/Repo/browser-harness")
sys.path.insert(0, str(HARNESS))
from helpers import (
    goto, page_info, screenshot, js, wait, wait_for_load,
    http_get, cdp
)

SKILL_ROOT = Path("C:/Users/jtoem/.config/opencode/skills/browser-agent")
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
        meta.write_text(f"mapped: \npages: 0\nendpoints: 0\n")
    return folder


def write_frontmatter(path, site, url, **kwargs):
    fm = ["---", f"site: {site}", f"url: {url}"]
    for k, v in kwargs.items():
        fm.append(f"{k}: {v}")
    fm.append("---\n")
    content = path.read_text() if path.exists() else ""
    path.write_text("\n".join(fm) + "\n" + content)


def crawl_site(root_url, max_pages=20):
    visited, to_visit, results, seen_urls = set(), [root_url], [], set()
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
            links_raw = js("""
                Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith(window.location.origin))
                    .filter(h => !h.includes('#'))
                    .slice(0, 50)
            """) or []
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
                "title": info.get("title", ""),
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


def intercept_endpoints(pages):
    endpoints, seen = [], set()
    for page in pages[:5]:
        try:
            goto(page["url"])
            wait_for_load()
            wait(1)
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
    lines = ["# Discovered APIs\n"]
    for ep in endpoints:
        lines.append(f"- {ep['url']} (source: {ep.get('source', 'unknown')})")
    (folder / "apis.md").write_text("\n".join(lines))


def write_readme_md(folder, site, root_url, pages, endpoints):
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
    meta = {
        "mapped": time.strftime("%Y-%m-%d"),
        "pages": len(pages),
        "endpoints": len(endpoints),
        "last_updated": time.strftime("%Y-%m-%d %H:%M")
    }
    (folder / "_meta.yaml").write_text(yaml.dump(meta))


def map_site(site, root_url=None):
    if not root_url:
        root_url = f"https://{site}"
    print(f"Mapping {site} from {root_url}...")
    folder = ensure_site_folder(site)
    print("Crawling pages...")
    pages = crawl_site(root_url)
    print(f"  Found {len(pages)} pages")
    print("Intercepting endpoints...")
    endpoints = intercept_endpoints(pages)
    print(f"  Found {len(endpoints)} endpoints")
    print("Writing domain skills...")
    write_nav_md(folder, pages)
    write_forms_md(folder, pages)
    write_apis_md(folder, endpoints)
    write_readme_md(folder, site, root_url, pages, endpoints)
    write_meta_yaml(folder, pages, endpoints)
    import yaml
    meta = yaml.safe_load((folder / "_meta.yaml").read_text())
    write_frontmatter(folder / "README.md", site=site, url=root_url,
        mapped=meta.get("mapped", time.strftime("%Y-%m-%d")),
        pages=len(pages), endpoints=len(endpoints))
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