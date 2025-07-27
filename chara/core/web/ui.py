import asyncio

from typing import Any, Optional, TYPE_CHECKING

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

from chara.config import WebUIConfig
from chara.core.hazard import BOTS, PLUGINS, PLUGIN_GROUPS
from chara.core.web.static import StaticFiles
from chara.log import logger

if TYPE_CHECKING:
    from chara.core.core import Core


class WebUI:
    
    __slots__ = ('config', 'core', 'sf', 'api', 'web')

    config: WebUIConfig
    core: 'Core'
    sf: StaticFiles
    api: APIRouter
    web: APIRouter

    def __init__(self, core: 'Core') -> None:
        self.core = core
        self.config = core.config.server.webui
        if not self.config.assets.exists():
            self.config.assets.mkdir(exist_ok=True)
            logger.warning(f'目录[{self.config.assets}]不存在, 已创建.')
        if not self.config.static.exists():
            self.config.static.mkdir(exist_ok=True)
            logger.warning(f'目录[{self.config.static}]不存在, 已创建.')
        
        self.sf = StaticFiles(self.config)
        self.api = APIRouter(prefix='/api')
        self.web = APIRouter(prefix=self.config.path)
        self._set_apiroute()
        core.app.mount('/static', self.sf)
        core.app.include_router(self.api)
        core.app.include_router(self.web)
    
    def _response(self, code: int, msg: Optional[str] = None, data: Any = None) -> JSONResponse:
        return JSONResponse(dict(code=code, msg=msg, data=data), code)
    
    def _set_apiroute(self):
        @self.web.get('')
        @self.web.get('/')
        async def _():
            index = self.config.assets / self.config.index
            if index.is_file():
                content = index.read_text(encoding='UTF-8')
            else:
                content = ''
                logger.warning(f'web-ui入口文件({index})不存在')
            return HTMLResponse(content)
        
        @self.api.websocket('/monitor')
        async def _(websocket: WebSocket):
            await websocket.accept()
            try:
                ticks = 0
                while True:
                    await websocket.send_json({'type': 'process', 'data': self.core.wm.all_process_status})
                    
                    if ticks % 5 == 0:
                        await websocket.send_json({'type': 'plugin', 'data': [{'uuid': plugin.metadata.uuid, 'state': plugin.state.value} for plugin in PLUGINS.values()]})
                    
                    await asyncio.sleep(1)

                    if ticks == 100:
                        ticks = 0
                    
                    ticks += 1
            
            except WebSocketDisconnect:
                pass

        @self.api.post('/process/list')
        async def _():
            return JSONResponse(self.core.wm.all_process_status)

        @self.api.post('/process/{name}/close')
        async def _(name: str):
            if worker := self.core.wm.workers.get(name, None):
                if worker.is_alive:
                    await worker.close()
                    return self._response(200)
                return self._response(200, f'进程{name}已关闭, 请勿重复调用.')
            return self._response(400, f'进程{name}不存在.')

        @self.api.post('/process/{name}/start')
        async def _(name: str):
            if worker := self.core.wm.workers.get(name, None):
                if not worker.is_alive:
                    await worker.start()
                    return self._response(200)
                return self._response(200, f'进程{name}已启动, 请勿重复调用.')
            return self._response(400, f'进程{name}不存在.')

        @self.api.post('/process/{name}/restart')
        async def _(name: str):
            if worker := self.core.wm.workers.get(name, None):
                if worker.is_alive:
                    await worker.restart()
                    return self._response(200)
                return self._response(200, f'进程{name}正在重启, 请勿重复调用.')
            return self._response(400, f'进程{name}不存在.')

        @self.api.post('/plugin/list')
        async def _() -> JSONResponse:
            data: list[dict[str, Any]] = [plugin.data for plugin in PLUGINS.values()]
            return self._response(200, None, data)

        @self.api.post('/plugin/{uuid}/data')
        async def _(uuid: str):
            if plugin := PLUGINS.get(uuid, None):
                return self._response(200, None, plugin.data)
            return self._response(400, f'插件{uuid}不存在.')

        @self.api.post('/plugin/group/list')
        async def _():
            data: list[dict[str, Any]] = [
                {
                    'name': name,
                    'plugins': [plugin.data for plugin in group.values()],
                }
                for name, group in PLUGIN_GROUPS.items()
            ]
            return self._response(200, None, data)

        @self.api.post('/bot/list')
        async def _():
            data: list[dict[str, Any]] = [
                {
                    'uin': uin,
                    'name': bot.name,
                    'connected': bot.connected,
                    'data': bot.data.json(),
                }
                for uin, bot in BOTS.items()
            ]
            return self._response(200, None, data)


