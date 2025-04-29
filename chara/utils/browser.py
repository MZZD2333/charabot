from contextvars import ContextVar
from typing import Optional

from playwright.async_api import Playwright, Browser, async_playwright


_PW: ContextVar[Optional[Playwright]] = ContextVar('PW', default=None)
_BW: ContextVar[Optional[Browser]] = ContextVar('BW', default=None)


async def launch():
    global _PW, _BW
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()
    _PW.set(_playwright)
    _BW.set(_browser)


def get_browser():
    bw = _BW.get()
    assert bw, 'chromium未启动'
    return bw


