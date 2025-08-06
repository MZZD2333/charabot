from typing import Any, Optional, Sequence, TypeVar, overload

from chara.core.bot import Bot
from chara.core.hazard import BOTS
from chara.onebot.api.onebot import OneBotAPI
from chara.onebot.events import GroupMessageEvent, MessageEvent
from chara.onebot.message import Message, MessageSegment


def construct_forward_message(messages: Sequence[str|Message|MessageSegment], name: str = 'chara', uin: int = 999999999) -> list[dict[str, Any]]:
    '''## 构建合并消息'''
    return [MessageSegment.node(name=name, uin=uin, content=msg).dict for msg in messages]


MT = TypeVar('MT', MessageEvent, GroupMessageEvent, default=MessageEvent)

@overload
async def get_reply_message(message: MT, bot: Optional[Bot] = None) -> Optional[MT]:
    '''## 获取回复的消息事件'''

@overload
async def get_reply_message(message: MT, bot: Optional[Bot] = None, return_event: bool = False) -> Optional[Message]:
    '''## 获取回复的消息'''

async def get_reply_message(message: MessageEvent, bot: Optional[Bot] = None, return_event: bool = True):
    if message.reply_id is None:
        return
    
    if bot is None:
        bot = BOTS[message.self_id]
    
    raw_msg = await bot[OneBotAPI].get_msg(message_id=message.reply_id)
    event = type(message)(**raw_msg)
    
    if return_event:
        return event
    
    return event.message

