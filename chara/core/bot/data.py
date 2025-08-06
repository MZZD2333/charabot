import json
import time

from typing import Any, TYPE_CHECKING

from chara.core.bot.friend import Friends
from chara.core.bot.group import Groups
from chara.core.bot.nickname import NickNames
from chara.core.bot.superuser import SuperUsers
from chara.core.color import colorize
from chara.core.hazard import BOTS, CONTEXT_GLOBAL_CONFIG
from chara.core.share import shared_bot_data_update_time
from chara.log import logger
from chara.onebot.api import OneBotAPI

if TYPE_CHECKING:
    from chara.core.bot import Bot


class Data:
    
    __slots__ = ('uin', 'name', 'nicknames', 'superusers', 'groups', 'friends', 'path', 'public_path', 'last_update_time', '_sv_update_time')
    
    uin: int
    name: str
    nicknames: NickNames
    superusers: SuperUsers
    groups: Groups
    friends: Friends

    def __init__(self, bot: 'Bot') -> None:
        self.uin = bot.config.uin
        self.name = bot.config.name
        self.nicknames = NickNames(bot.config.nicknames)
        self.superusers = SuperUsers(bot.config.superusers)
        self.groups = Groups()
        self.friends = Friends()
        
        group_config = CONTEXT_GLOBAL_CONFIG.get()
        self.public_path = group_config.data.directory
        self.path = self.public_path / 'bots' / str(self.uin)
        self.path.mkdir(parents=True, exist_ok=True)

        self.last_update_time = -1
        self._sv_update_time = shared_bot_data_update_time(str(self.uin))
        self.load()

    @property
    def updated(self) -> bool:
        return int(self._sv_update_time.value) == self.last_update_time

    def json(self) -> dict[str, Any]:
        return {
            'update_time': self.last_update_time,
            'groups': self.groups.json(),
            'friends': self.friends.json(),
            'nicknames': self.nicknames.json(),
            'superusers': self.superusers.json(),
        }

    def load(self) -> None:
        if (path := (self.path / 'data.json')).exists():
            data: dict[str, Any] = json.loads(path.read_bytes())
            self.last_update_time = data.get('update_time', -1)

            if groups := data.get('groups', None):
                self.groups.update(groups)

            if friends := data.get('friends', None):
                self.groups.update(friends)

            if nicknames := data.get('nicknames', None):
                self.groups.update(nicknames)

            if superusers := data.get('superusers', None):
                self.groups.update(superusers)
        
        else:
            self.last_update_time = -1
        
        self._sv_update_time.write(self.last_update_time)

    def save(self) -> None:
        with open(self.path / 'data.json', 'w', encoding='UTF-8') as f:
            json.dump(self.json(), f, ensure_ascii=False, indent=4)

    async def update(self) -> None:
        BOT = BOTS[self.uin]

        # Friend
        try:
            friends = await BOT[OneBotAPI].get_friend_list()
            self.friends.update(friends)
        except:
            logger.exception(f'{colorize.bot(BOT)}更新好友数据失败.')

        # Groups
        try:
            groups = await BOT[OneBotAPI].get_group_list()
            data: dict[str, Any] = {'owned': list(), 'admin': list(), 'list': groups}
            for gd in groups:
                group_id = gd['group_id']
                result = await BOT[OneBotAPI].get_group_member_info(group_id=group_id, user_id=self.uin)
                role = result.get('role', None)
                if role == 'owner':
                    data['owned'].append(group_id)
                elif role == 'admin':
                    data['admin'].append(group_id)
            
            self.groups.update(data)
        except:
            logger.exception(f'{colorize.bot(BOT)}更新群聊数据失败.')

        self.last_update_time = time.time()
        self.save()
        self._sv_update_time.write(self.last_update_time)
        
