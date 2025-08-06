import asyncio

from contextvars import ContextVar
from typing import Any, Optional

from playwright._impl._connection import Connection as _CONN
from playwright._impl._object_factory import create_remote_object as _cro  # type: ignore
from playwright._impl._transport import PipeTransport as _OPT
from playwright.async_api import Browser as _BW
from playwright.async_api import Playwright as _PW


from chara.core.hazard import CONTEXT_LOOP

class _PT(_OPT):
    
    async def run(self) -> None:
        assert self._proc.stdout
        assert self._proc.stdin
        while not self._stopped:
            try:
                buffer = await self._proc.stdout.readexactly(4)
                if self._stopped:
                    break
                length = int.from_bytes(buffer, byteorder='little', signed=False)
                buffer = bytes(0)
                while length:
                    to_read = min(length, 32768)
                    data = await self._proc.stdout.readexactly(to_read)
                    if self._stopped:
                        break
                    length -= to_read
                    if len(buffer):
                        buffer = buffer + data
                    else:
                        buffer = data
                if self._stopped:
                    break

                obj = self.deserialize_message(buffer)
                self.on_message(obj)
            except:
                break
            await asyncio.sleep(0)

        await self._proc.communicate()
        self._stopped_future.set_result(None)  # type: ignore


class _PCM:
    def __init__(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        self._connection = _CONN(None, _cro, _PT(LOOP), LOOP)
        LOOP.create_task(self._connection.run())
        self._exit_was_called = False

    async def __aenter__(self) -> _PW:
        playwright_future = self._connection.playwright_future

        done, _ = await asyncio.wait({self._connection._transport.on_error_future, playwright_future}, return_when=asyncio.FIRST_COMPLETED)  # type: ignore
        if not playwright_future.done():
            playwright_future.cancel()
        playwright = _PW(next(iter(done)).result())  # type: ignore
        playwright.stop = self.__aexit__  # type: ignore
        return playwright

    async def start(self) -> _PW:
        return await self.__aenter__()

    async def __aexit__(self, *args: Any) -> None:
        if self._exit_was_called:
            return
        self._exit_was_called = True
        await self._connection.stop_async()


_CPW: ContextVar[Optional[_PW]] = ContextVar('CPW', default=None)
_CBW: ContextVar[Optional[_BW]] = ContextVar('CBW', default=None)

async def launch() -> _BW:
    global _CPW, _CBW
    
    _playwright = _CPW.get()
    if _playwright is None:
        _pcm = _PCM()
        _playwright = await _pcm.start()
        _CPW.set(_playwright)
    
    _browser = _CBW.get()
    if _browser is None:
        _browser = await _playwright.chromium.launch()
        _CBW.set(_browser)
        
    return _browser

async def get_browser() -> _BW:
    global _CBW
    _browser = _CBW.get()
    if _browser is None:
        return await launch()
    return _browser

async def close() -> None:
    global _CPW, _CBW

    try:
        _browser = _CBW.get()
        if _browser is None:
            return
        await _browser.close()
        _CBW.set(None)
        
        _playwright = _CPW.get()
        if _playwright is None:
            return
        await _playwright.stop()
        _CPW.set(None)
    except:
        pass

