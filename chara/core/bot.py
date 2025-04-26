import json
import time

from pathlib import Path
from typing import Any, Optional
from httpx import AsyncClient, ByteStream, Headers, Request, TimeoutException, URL

from chara.config import BotConfig
from chara.core.param import CONTEXT_GLOBAL_CONFIG
from chara.exception import APICallFailed
from chara.log import style, logger
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
        self.group_list = list()
        self.friend_list = list()
        self.owner_groups = list()
        self.admin_groups = list()
        self.config = config
        self.connected = False
        self.client = AsyncClient(base_url=f'http://{config.http_host}:{config.http_port}')
        self.client.headers = {'Host': f'{config.http_host}:{config.http_port}'}
        
        group_config = CONTEXT_GLOBAL_CONFIG.get()
        global_data_path = group_config.data.directory
        self.data_path = global_data_path / str(config.uin)
        self.global_data_path = global_data_path
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self._last_update_time = 0
    
    async def update_bot_data(self, use_cache: bool = True, cache_retention_time: float = 86400):
        '''## 更新bot数据'''
        if use_cache:
            path = next(self.data_path.rglob('info_*.json'), None)
            if path is not None:
                st = int(path.stem.lstrip('info_'))
                ct = int(time.time())
                if (ct - st) < cache_retention_time:
                    self._load_bot_data()
                    return
        try:
            self.group_list = await self.get_group_list()
            self.friend_list = await self.get_friend_list()
            self.groups = [g['group_id'] for g in self.group_list]
            self.friends = [f['user_id'] for f in self.friend_list]
            for group_id in self.groups:
                result = await self.get_group_member_info(group_id=group_id, user_id=self.uin)
                role = result.get('role', None)
                if role == 'owner':
                    self.owner_groups.append(group_id)
                elif role == 'admin':
                    self.admin_groups.append(group_id)
            self._save_bot_data()
        except APICallFailed:
            logger.exception(f'更新{style.g(self.name)}' + style.c(f'[{self.uin}]') + '数据时发生错误')
    
    def is_latest_data_file(self):
        '''## bot数据文件是否为最新'''
        path = next(self.data_path.rglob('info_*.json'), None)
        if path is None:
            return False
        st = int(path.stem.lstrip('info_'))
        return self._last_update_time == st
    
    def _save_bot_data(self):
        data = dict(
            groups=self.groups,
            friends=self.friends,
            group_list=self.group_list,
            friend_list=self.friend_list,
            owner_groups=self.owner_groups,
            admin_groups=self.admin_groups,
        )
        for path in self.data_path.rglob('info_*.json'):
            path.unlink()
        ct = int(time.time())
        with open(self.data_path / f'info_{ct}.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def _load_bot_data(self):
        path = next(self.data_path.rglob('info_*.json'), None)
        if path is None:
            return None
        data = json.loads(path.read_text(encoding='UTF-8'))
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


