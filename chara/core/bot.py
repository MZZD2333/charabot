import json
import time

from pathlib import Path
from typing import Any, Optional
from httpx import AsyncClient, ByteStream, Headers, Request, TimeoutException, URL

from chara.config import BotConfig
from chara.exception import APICallFailed
from chara.onebot.api import API
from chara.onebot.message import MessageJSONEncoder


class Bot(API):
    
    uin: int
    name: str # type: ignore
    nicknames: list[str]
    superusers: list[int]
    groups: list[int]
    friends: list[int]
    owner_groups: list[int]
    admin_groups: list[int]
    group_list: list[dict[str, Any]]
    friend_list: list[dict[str, Any]]
    
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
        self.groups = list()
        self.friends = list()
        self.owner_groups = list()
        self.admin_groups = list()
        self.config = config
        self.data_path = Path()
        self.global_data_path = Path()
        self.connected = False
        self.client = AsyncClient(base_url=f'http://{config.http_host}:{config.http_port}')
        self.client.headers = {'Host': f'{config.http_host}:{config.http_port}'}
    
    async def update_bot_info(self, use_cache: bool = True, cache_retention_time: float = 86400):
        if use_cache:
            path = next(self.data_path.rglob('info_*.json'), None)
            if path is not None:
                st = int(path.stem.lstrip('info_'))
                ct = int(time.time())
                if (ct - st) < cache_retention_time:
                    self.load_bot_info()
                    return
        self.group_list = await self.get_group_list()
        self.friend_list = await self.get_friend_list()
        self.groups = [g['group_id'] for g in self.group_list]
        self.friends = [f['user_id'] for f in self.friend_list]
        self.save_bot_info()
    
    def save_bot_info(self):
        '''## 保存bot信息'''
        data = dict(
            groups=self.groups,
            friends=self.friends,
            group_list=self.group_list,
            friend_list=self.friend_list,
            owner_groups=self.owner_groups,
            admin_groups=self.admin_groups,
        )
        with open(self.data_path / f'info_{int(time.time())}.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def load_bot_info(self):
        '''## 加载bot信息'''
        path = next(self.data_path.rglob('info_*.json'), None)
        if path is None:
            return None
        data = json.loads(path.read_text())
        self.groups = data['groups']
        self.friends = data['friends']
        self.group_list = data['group_list']
        self.friend_list = data['friend_list']
        self.owner_groups = data['owner_groups']
        self.admin_groups = data['admin_groups']
        

    async def call_api(self, api: str, **data: Any) -> Optional[dict[Any, Any]]:
        '''## 调用API'''
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


