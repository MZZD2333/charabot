from contextvars import ContextVar
from typing import Optional

from playwright.async_api import Playwright, Browser, async_playwright


_PW: ContextVar[Optional[Playwright]] = ContextVar('PW', default=None)
_BW: ContextVar[Optional[Browser]] = ContextVar('BW', default=None)


async def launch():
    global _PW, _BW
    
    _playwright = _PW.get()
    if _playwright is None:
        _playwright = await async_playwright().start()
        _PW.set(_playwright)
    
    _browser = _BW.get()
    if _browser is None:
        _browser = await _playwright.chromium.launch()
        _BW.set(_browser)
        
    return _browser


async def close():
    global _PW, _BW

    _browser = _BW.get()
    if _browser is None:
        return
    
    await _browser.close()
    
    _playwright = _PW.get()
    if _playwright is None:
        return
    await _playwright.stop()
