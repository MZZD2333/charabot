import json

from pathlib import Path
from typing import Any, Optional
from httpx import AsyncClient, ByteStream, Headers, Request, TimeoutException, URL

from chara.config import BotConfig
from chara.exception import APICallFailed
from chara.onebot.api import API
from chara.onebot.message import MessageJSONEncoder


class OneBotAPIClient(AsyncClient):
    
    def __init__(self, x: int) -> None:
        pass


class Bot(API):
    
    uin: int
    name: str # type: ignore
    nicknames: list[str]
    superusers: list[int]
    config: BotConfig
    data_path: Path
    global_data_path: Path
    connected: bool
    client: AsyncClient
    
    def __init__(self, config: BotConfig) -> None:
        self.uin = config.uin
        self.name = config.name # type: ignore
        self.nicknames = config.nicknames
        self.superusers = config.superusers
        self.config = config
        self.data_path = Path()
        self.global_data_path = Path()
        self.connected = False
        self.client = AsyncClient(base_url=f'http://{config.http_host}:{config.http_port}')
        self.client.headers = {'Host': f'{config.http_host}:{config.http_port}'}

    async def call_api(self, api: str, **data: Any) -> Optional[dict[Any, Any]]:
        if not api.startswith('/'):
            api = '/' + api
        try:
            body = json.dumps(data, ensure_ascii=False, cls=MessageJSONEncoder).encode('utf-8')
            headers = Headers(self.client.headers)
            headers.update({'Content-Length': str(len(body)), 'Content-Type': 'application/json'})
            request = Request('POST', URL(self.client.base_url, path=api), headers=headers, stream=ByteStream(body))
            resp = await self.client.send(request)
        except TimeoutException:
            raise APICallFailed(api, f'无法请求到Http Server[{self.config.http_host}:{self.config.http_port}].')
        
        data = resp.json()
        if data['status'] == 'failed':
            raise APICallFailed(api)
        return data.get('data')


