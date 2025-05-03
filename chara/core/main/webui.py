import stat

from email.utils import parsedate
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from fastapi import APIRouter
from fastapi.datastructures import Headers
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from starlette.exceptions import HTTPException
from starlette.staticfiles import NotModifiedResponse
from starlette.types import Receive, Scope, Send

from chara.config import GlobalConfig, WebUIConfig
from chara.core.param import BOTS, CONTEXT_LOOP, PLUGINS, PLUGIN_GROUPS
from chara.log import logger

if TYPE_CHECKING:
    from chara.core.main._main import MainProcess


class StaticFiles:
    
    __slots__ = ('config', )
    
    config: WebUIConfig
    
    def __init__(self, config: WebUIConfig) -> None:
        self.config = config

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        response = self.file_response(scope)
        await response(scope, receive, send)
        
    def lookup_plugin_files(self, uuid: str, path: Path) -> Optional[Path]:
        if plugin := PLUGINS.get(uuid, None):
            if (request_file := plugin.root_path / path).exists():
                return request_file
            elif (request_file := plugin.data_path / path).exists():
                return request_file
            
    def lookup_static_files(self, path: Path) -> Optional[Path]:
        if (request_file := self.config.static / path).exists():
            return request_file

    def file_response(self, scope: Scope) -> Response:
        scope_path: str = scope['path'].strip('/')
        path_parts = scope_path.split('/')
        length = len(path_parts)
        if length == 1:
            raise HTTPException(status_code=404)
        elif length >= 2 and  path_parts[1] == 'plugin':
            if length < 4:
                raise HTTPException(status_code=404)
            request_file = self.lookup_plugin_files(path_parts[2], Path(*path_parts[3:]))
        else:
            request_file = self.lookup_static_files(Path(*path_parts[1:]))
        if request_file is None:
            raise HTTPException(status_code=404)
        stat_result = request_file.stat()
        if not stat.S_ISREG(stat_result.st_mode):
            raise HTTPException(status_code=404)
        request_headers = Headers(scope=scope)
        response = FileResponse(request_file, status_code=200, stat_result=stat_result)
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response

    def is_not_modified(self, response_headers: Headers, request_headers: Headers) -> bool:
        try:
            if_none_match = request_headers['if-none-match']
            etag = response_headers['etag']
            if etag in [tag.strip(' W/') for tag in if_none_match.split(',')]:
                return True
        except KeyError:
            pass
        try:
            if_modified_since = parsedate(request_headers['if-modified-since'])
            last_modified = parsedate(response_headers['last-modified'])
            if if_modified_since is not None and last_modified is not None and if_modified_since >= last_modified:
                return True
        except KeyError:
            pass
        return False


class WebUI:
    
    __slots__ = ('config', 'main', 'sf', 'api', 'web')

    config: WebUIConfig
    main: 'MainProcess'
    sf: StaticFiles
    api: APIRouter
    web: APIRouter

    def __init__(self, main: 'MainProcess', config: GlobalConfig) -> None:
        self.main = main
        self.config = config.server.webui
        if not self.config.assets.exists():
            self.config.assets.mkdir(exist_ok=True)
            logger.warning(f'目录 {self.config.assets} 不存在, 已创建.')
        if not self.config.static.exists():
            self.config.static.mkdir(exist_ok=True)
            logger.warning(f'目录 {self.config.static} 不存在, 已创建.')
        
        self.sf = StaticFiles(self.config)
        self.api = APIRouter(prefix='/api')
        self.web = APIRouter(prefix=self.config.path)
        self._set_apiroute()
        main.app.mount('/static', self.sf)
        main.app.include_router(self.api)
        main.app.include_router(self.web)
    
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
        
        @self.api.post('/plugin/list')
        async def _():
            data: list[dict[str, Any]] = [
                {
                    'index': plugin.index,
                    'uuid': plugin.metadata.uuid,
                    'name': plugin.metadata.name,
                    'group': plugin.group,
                    'state': plugin.state.value,
                    'authors': plugin.metadata.authors,
                    'version': plugin.metadata.version,
                    'description': plugin.metadata.description,
                    'icon': plugin.metadata.icon,
                    'docs': plugin.metadata.docs,
                }
                for plugin in PLUGINS.values()
            ]
            return JSONResponse(data)

        @self.api.post('/plugin/{uuid}/data')
        async def _(uuid: str):
            if plugin := PLUGINS.get(uuid, None):
                data: dict[str, Any] = {
                    'index': plugin.index,
                    'uuid': plugin.metadata.uuid,
                    'name': plugin.metadata.name,
                    'group': plugin.group,
                    'state': plugin.state.value,
                    'authors': plugin.metadata.authors,
                    'version': plugin.metadata.version,
                    'description': plugin.metadata.description,
                    'icon': plugin.metadata.icon,
                    'docs': plugin.metadata.docs,
                }                
                return JSONResponse(data)
            return Response(f'插件{uuid}不存在.', status_code=400)

        @self.api.post('/plugin/group/list')
        async def _():
            data: list[dict[str, Any]] = [
                {
                    'name': name,
                    'plugins': [
                        {
                            'index': plugin.index,
                            'uuid': plugin.metadata.uuid,
                            'name': plugin.metadata.name,
                            'group': plugin.group,
                            'state': plugin.state.value,
                            'authors': plugin.metadata.authors,
                            'version': plugin.metadata.version,
                            'description': plugin.metadata.description,
                            'icon': plugin.metadata.icon,
                            'docs': plugin.metadata.docs,
                        }
                        for plugin in group.values()
                    ]
                }
                for name, group in PLUGIN_GROUPS.items()
            ]
            return JSONResponse(data)

        @self.api.post('/plugin/group/{name}/reload')
        async def _(name: str):
            if name in PLUGIN_GROUPS:
                if (process := self.main.workers[name]).is_alive:
                    LOOP = CONTEXT_LOOP.get()
                    LOOP.create_task(process.restart())
                    return Response(status_code=200)
                return Response(f'插件组{name}正在重启, 请勿重复调用.', status_code=400)
            return Response(f'插件组{name}不存在.', status_code=400)

        @self.api.post('/bot/list')
        async def _():
            data: list[dict[str, Any]] = [
                {
                    'uin': uin,
                    'name': bot.name,
                    'connected': bot.connected,
                    'data': {
                        'friends': bot.friends,
                        'groups': bot.groups,
                        'friend_list': bot.friend_list,
                        'group_list': bot.group_list,
                        'owner_groups': bot.owner_groups,
                        'admin_groups': bot.admin_groups,
                    }
                }
                for uin, bot in BOTS.items()
            ]
            return JSONResponse(data)

