from abc import ABC, abstractmethod
import os

from _backends.selector_parser import parse_selector

class BrowserBackend(ABC):
    @abstractmethod
    async def launch(self, headless=False):
        pass

    @abstractmethod
    async def new_page(self):
        pass

    @abstractmethod
    async def goto(self, url, wait_until="domcontentloaded"):
        pass

    @abstractmethod
    async def query_selector(self, selector):
        pass

    @abstractmethod
    async def click(self, selector):
        pass

    @abstractmethod
    async def fill(self, selector, value):
        pass

    @abstractmethod
    async def press(self, selector, key):
        pass

    @abstractmethod
    async def screenshot(self, path):
        pass

    @property
    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    async def close(self):
        pass


def _load_site_meta(site):
    """Load site metadata if domain-skills folder exists."""
    try:
        from pathlib import Path
        import yaml
        folder = Path(__file__).parent.parent / "domain-skills" / site.replace(".", "-").replace(":", "-")
        meta_path = folder / "_meta.yaml"
        if meta_path.exists():
            return yaml.safe_load(meta_path.read_text()) or {}
    except Exception:
        pass
    return {}


def get_backend(site=None):
    """
    Get browser backend for a site.

    Resolution order:
    1. Site-specific `backend` field in domain-skills/<site>/_meta.yaml
    2. BROWSER_BACKEND env var
    3. Default: playwright

    Site metadata example (_meta.yaml):
        backend: chrome  # Use opencode-browser (real Chrome with profile)
        backend: playwright  # Use Playwright (headless CDP)
    """
    if site:
        meta = _load_site_meta(site)
        site_backend = meta.get("backend", "").lower()
        if site_backend in ("chrome", "opencode-browser"):
            from _backends.chrome_backend import ChromeBackend
            return ChromeBackend()
        elif site_backend == "playwright":
            from _backends.playwright_backend import PlaywrightBackend
            return PlaywrightBackend()

    env_backend = os.environ.get("BROWSER_BACKEND", "playwright").lower()
    if env_backend in ("chrome", "opencode-browser"):
        from _backends.chrome_backend import ChromeBackend
        return ChromeBackend()
    from _backends.playwright_backend import PlaywrightBackend
    return PlaywrightBackend()


__all__ = ["BrowserBackend", "get_backend", "parse_selector"]