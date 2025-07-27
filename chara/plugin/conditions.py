from typing import Literal, Optional

from chara.core.bot import Bot
from chara.core.plugin import Condition, Handler
from chara.onebot.events import Event, GroupMessageEvent, MessageEvent, PrivateMessageEvent
from chara.typing import MessageLike


async def _is_superuser(bot: Bot, event: MessageEvent) -> bool:
    return event.user_id in bot.superusers

async def _is_at_me(event: Event) -> bool:
    return event.at_me

async def _is_call_me(bot: Bot, event: MessageEvent) -> bool:
    if event.pure_text.startswith(bot.name):
        return True
    for nickname in bot.nicknames:
        if event.pure_text.startswith(nickname):
            return True
    return False

async def _is_friend(bot: Bot, event: MessageEvent) -> bool:
    return event.sub_type == 'friend' or event.user_id in bot.friends

async def _is_friend_private(event: PrivateMessageEvent) -> bool:
    return event.sub_type == 'friend'

async def _sender_is_group_owner(event: GroupMessageEvent) -> bool:
    return event.sender.role == 'owner'

async def _sender_is_group_admin(event: GroupMessageEvent) -> bool:
    return event.sender.role == 'admin'

async def _sender_is_group_member(event: GroupMessageEvent) -> bool:
    return event.sender.role == 'member'

async def _sender_is_group_owner_or_admin(event: GroupMessageEvent) -> bool:
    return event.sender.role == 'owner' or event.sender.role == 'admin'

async def _bot_is_group_owner(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.group_id in bot.groups.owned

async def _bot_is_group_admin(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.group_id in bot.groups.admin

async def _bot_is_group_member(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.group_id not in bot.groups.owned or event.group_id not in bot.groups.admin

async def _bot_is_group_owner_or_admin(bot: Bot, event: GroupMessageEvent) -> bool:
    return event.group_id in bot.groups.owned or event.group_id in bot.groups.admin

SUPERUSER = Condition(_is_superuser)
'''## Config中设置的SuperUser'''

SU = SUPERUSER
'''## Config中设置的SuperUser'''

AT_ME = Condition(_is_at_me)
'''## bot被at或私聊消息'''

CALL_ME = Condition(_is_call_me)
'''## 消息以bot名字或昵称开头'''

TO_ME = AT_ME & CALL_ME
'''## 消息以bot名字或昵称开头或被at或私聊消息'''

FRIEND = Condition(_is_friend)
'''## 发送者为好友'''

FRIEND_PRIVATE = Condition(_is_friend_private)
'''## 会话为好友私聊'''

SP_0 = Condition(_sender_is_group_owner)
'''## 消息发送者为群主'''

SP_1 = Condition(_sender_is_group_owner_or_admin)
'''## 消息发送者为群主或管理员'''

SP_2 = Condition(_sender_is_group_admin)
'''## 消息发送者为管理员'''

SP_3 = Condition(_sender_is_group_member)
'''## 消息发送者为普通群员'''

BP_0 = Condition(_bot_is_group_owner)
'''## bot为收到消息群的群主'''

BP_1 = Condition(_bot_is_group_owner_or_admin)
'''## bot为收到消息群的群主或管理员'''

BP_2 = Condition(_bot_is_group_admin)
'''## bot为收到消息群的管理员'''

BP_3 = Condition(_bot_is_group_member)
'''## bot为收到消息群的普通群员'''


def Frequency(num: int = 1, time: float = 10, mode: Literal['group_shared', 'user_shared', 'independent'] = 'independent', prompt: Optional[MessageLike] = None) -> Condition:
    '''
    ## 创建一个频率条件
    
    ---
    ### 参数
    - num: 设定时长内最大触发次数
    - time: 时长(s)
    - mode: 计时模式
        - group_shared: 当前会话[群聊|私聊]共用一个计时器
        - user_shared: 用户的所有会话[群聊|私聊]共用一个计时器
        - independent: 用户的每个会话[群聊|私聊]单独使用一个计时器
    - prompt: 未满足频率限制时发送的内容
    '''
    ACTIVITY: dict[str, int] = dict()

    if mode == 'group_shared':
        def get_key(event: MessageEvent):
            if isinstance(event, GroupMessageEvent):
                return f'{event.group_id}'
            else:
                return f'{event.user_id}'
    elif mode == 'user_shared':
        def get_key(event: MessageEvent):
            return f'{event.user_id}'
    elif mode == 'independent':
        def get_key(event: MessageEvent):
            if isinstance(event, GroupMessageEvent):
                return f'{event.group_id}.{event.user_id}'
            else:
                return f'{event.user_id}'
    else:
        raise Exception(f'{mode} is not a given mode.')
    
    def _call_later(key: str):
        if key in ACTIVITY:
            ACTIVITY[key] -= 1
            if ACTIVITY[key] <= 0:
                del ACTIVITY[key]
    
    async def _frequency(handler: Handler, event: MessageEvent):
        key = get_key(event)
        if key in ACTIVITY and ACTIVITY[key] >= num:
            if prompt:
                await handler.send(prompt)
            return False
        ACTIVITY[key] = ACTIVITY.get(key, 0) + 1
        handler.loop.call_later(time, _call_later, key)
        return True
    return Condition(_frequency)


def Cooldown(cd: float = 10, mode: Literal['group_shared', 'user_shared', 'independent'] = 'independent', prompt: Optional[MessageLike] = None) -> Condition:
    '''
    ## 创建一个冷却条件
    
    ---
    ### 参数
    - cd: 冷却时间
    - mode: 计时模式
        - group_shared: 当前会话[群聊|私聊]共用一个计时器
        - user_shared: 用户的所有会话[群聊|私聊]共用一个计时器
        - independent: 用户的每个会话[群聊|私聊]单独使用一个计时器
    - prompt: 未到冷却时间时发送的内容
    '''
    return Frequency(1, cd, mode, prompt)


def Probability(p: float) -> Condition:
    '''
    ## 创建一个概率条件
    
    ---
    ### 参数
    - p: 触发概率 `p∈[0, 1]`
    '''
    from random import random
    
    async def _probability():
        return random() <= p

    return Condition(_probability)


def RandomDelay(max: float = 1, min: float = 0) -> Condition:
    '''
    ## 创建一个永远为真的随机延时条件
    
    ---
    ### 参数
    - max: 最长时间
    - min: 最短时间
    '''
    assert max >= min
    time_range = max - min
    
    from asyncio import Future
    from random import random
    from chara.core.hazard import CONTEXT_LOOP
    
    def _finish(future: Future[None]):
        future.set_result(None)
    
    async def _delay():
        time = min + time_range * random()
        LOOP = CONTEXT_LOOP.get()
        future = LOOP.create_future()
        LOOP.call_later(time, _finish, future)
        await future
        return True
    
    return Condition(_delay)


__all__ = [
    'SUPERUSER',
    'SU',
    'AT_ME',
    'CALL_ME',
    'TO_ME',
    'FRIEND',
    'FRIEND_PRIVATE',
    'SP_0',
    'SP_1',
    'SP_2',
    'SP_3',
    'BP_0',
    'BP_1',
    'BP_2',
    'BP_3',
    'Cooldown',
    'Frequency',
    'Probability',
    'RandomDelay',
]

