import asyncio
from playwright.async_api import async_playwright

class PlaywrightBackend:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    async def launch(self, headless=False):
        self._playwright = async_playwright()
        await self._playwright.start()
        self._browser = await self._playwright.chromium.launch(headless=headless)
        self._context = await self._browser.new_context(viewport={"width": 1280, "height": 800})
        self._page = await self._context.new_page()
        return self

    async def new_page(self):
        self._page = await self._context.new_page()
        return self._page

    async def goto(self, url, wait_until="domcontentloaded"):
        await self._page.goto(url, wait_until=wait_until)
        return self

    async def query_selector(self, selector):
        return await self._page.query_selector(selector)

    async def click(self, selector):
        el = await self._page.query_selector(selector)
        if el:
            await el.click()
            return True
        return False

    async def fill(self, selector, value):
        el = await self._page.query_selector(selector)
        if el:
            await el.fill(value)
            return True
        return False

    async def press(self, selector, key):
        await self._page.press(selector, key)
        return True

    async def screenshot(self, path):
        await self._page.screenshot(path=path)
        return True

    @property
    def url(self):
        return self._page.url if self._page else None

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
