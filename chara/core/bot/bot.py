import json

from functools import partial
from typing import Any, Coroutine, Optional

from httpx import AsyncClient, ByteStream, Headers, Request, TimeoutException, URL

from chara.config import BotConfig
from chara.core.bot.data import Data
from chara.core.bot.friend import Friends
from chara.core.bot.group import Groups
from chara.core.bot.nickname import NickNames
from chara.core.bot.superuser import SuperUsers
from chara.exception import APICallFailed
from chara.onebot.api.base import API
from chara.onebot.message import MessageJSONEncoder
from chara.typing import T


class Bot:
    
    __slots__ = ('config', 'connected', 'data', '_client')
    
    config: BotConfig
    data: Data
    
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.connected = False
        self.data = Data(self)
        self._client = AsyncClient(base_url=f'http://{config.http_host}:{config.http_port}')
        self._client.headers = {'Host': f'{config.http_host}:{config.http_port}'}

    def __getattr__(self, name: str) -> partial[Coroutine[Any, Any, Any]]:
        return partial(self.call_api, name)

    def __getitem__(self, api: type[T]) -> type[T]:
        assert issubclass(api, API)
        return self # type: ignore

    @property
    def uin(self) -> int:
        return self.data.uin

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def friends(self) -> Friends:
        return self.data.friends

    @property
    def groups(self) -> Groups:
        return self.data.groups

    @property
    def nicknames(self) -> NickNames:
        return self.data.nicknames

    @property
    def superusers(self) -> SuperUsers:
        return self.data.superusers


    async def call_api(self, api: str, **data: Any) -> Optional[dict[Any, Any]]:
        '''## 调用API'''
        if not api.startswith('/'):
            api = '/' + api
        try:
            body = json.dumps(data, ensure_ascii=False, cls=MessageJSONEncoder).encode('utf-8')
            headers = Headers(self._client.headers)
            headers.update({'Content-Length': str(len(body)), 'Content-Type': 'application/json'})
            request = Request('POST', URL(self._client.base_url, path=api), headers=headers, stream=ByteStream(body))
            resp = await self._client.send(request)
        except TimeoutException:
            raise APICallFailed(api, f'无法请求到Http Server[{self.config.http_host}:{self.config.http_port}].')
        
        data = resp.json()
        if data['status'] == 'failed':
            raise APICallFailed(api)
        return data.get('data')


