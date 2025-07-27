import stat

from email.utils import parsedate
from pathlib import Path
from typing import Any, Optional
from fastapi.datastructures import Headers
from fastapi.responses import FileResponse, Response
from starlette.exceptions import HTTPException
from starlette.staticfiles import NotModifiedResponse
from starlette.types import Receive, Scope, Send

from chara.config import WebUIConfig
from chara.core.hazard import PLUGINS

    
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


