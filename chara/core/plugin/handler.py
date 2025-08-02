import asyncio

from typing import Any, NoReturn, Optional, TYPE_CHECKING

from chara.core.bot import Bot
from chara.core.color import colorize
from chara.core.plugin.condition import Condition
from chara.exception import HandleFinished, IgnoreException
from chara.log import logger
from chara.lib.executor import Executor
from chara.onebot.api import OneBotAPI
from chara.onebot.message import Message, MessageSegment
from chara.typing import MessageLike

if TYPE_CHECKING:
    from chara.core.plugin.trigger import Trigger, TriggerCapturedData


class Handler:
    
    __slots__ = ('bot', 'condition', 'exc', 'loop', 'tcd', 'trigger', '__running')
    
    bot: Bot
    condition: Optional[Condition]
    exc: Executor[Any]
    loop: asyncio.AbstractEventLoop
    tcd: 'TriggerCapturedData'
    trigger: 'Trigger'
    __running: bool
    
    def __init__(self, exc: Executor[Any], condition: Optional[Condition], trigger: 'Trigger') -> None:
        self.exc = exc
        self.condition = condition
        self.trigger = trigger
        self.__running = False
        
    def new(self, bot: Bot, loop: asyncio.AbstractEventLoop, tcd: 'TriggerCapturedData') -> 'Handler':
        handler = Handler(self.exc, self.condition, self.trigger)
        handler.bot = bot
        handler.loop = loop
        handler.tcd = tcd
        return handler

    async def send(self, message: MessageLike, at_sender: bool = False, recall_after: int = 0, user_id: Optional[int] = None, group_id: Optional[int] = None) -> str:
        '''
        ## 发送消息
        
        ---
        ### 参数
        - message: 消息
        - at_sender: 是否@发送者[仅在群聊中生效]
        - recall_after: 在给定时间后撤回消息[时间受到QQ撤回时限限制]
        #### 以下参数会自动尝试获取，如果当前事件无法获取请给出
        - user_id: 用户QQ号[发送私聊消息|at_sender=True时需要]
        - group_id: 群号[发送群聊消息时需要]
        '''

        event_dict = self.tcd.event.model_dump()
        
        params: dict[str, Any] = dict()
        group_id = event_dict.get('group_id', group_id)
        user_id = event_dict.get('user_id', user_id)
        if group_id:
            params['group_id'] = group_id
        elif user_id:
            params['user_id'] = user_id
        else:
            logger.warning(f'获取user_id或group_id失败. 当前事件: \n{event_dict}')
            raise HandleFinished
        message = Message(message)
        if at_sender and group_id and user_id:
            message = MessageSegment.at(str(user_id)) + message
        params['message'] = message
        
        response = await self.bot[OneBotAPI].send_msg(**params)
        message_id = response['message_id']
        if recall_after > 0:
            async def delete(mid: int):
                await asyncio.sleep(recall_after)
                try:
                    await self.bot[OneBotAPI].delete_msg(message_id=mid)
                except:
                    pass
            self.loop.create_task(delete(message_id), name=message_id)
        
        return message_id
    
    async def done(self, message: Optional[MessageLike] = None, at_sender: bool = False, recall_after: int = 0, user_id: Optional[int] = None, group_id: Optional[int] = None) -> NoReturn:
        '''
        ## 发送消息并立即结束当前事件处理流程
        
        ---
        ### 参数
        - message: 消息
        - at_sender: 是否@发送者[仅在群聊中生效]
        - recall_after: 在给定时间后撤回消息[时间受到QQ撤回时限限制]
        #### 以下参数会自动尝试获取，如果当前事件无法获取请给出
        - user_id: 用户QQ号[发送私聊消息|`at_sender=True`时需要]
        - group_id: 群号[发送群聊消息时需要]
        '''
        if message:
            await self.send(message, at_sender, recall_after, user_id, group_id)
        raise HandleFinished

    async def __call__(self) -> int:
        # 0 成功
        # 1 跳过
        # 2 失败
        log_text = colorize.handler(self)
        if self.__running:
            logger.warning(log_text + '被循环调用.')
            return 1
        
        self.__running = True
        params = (self.tcd.event, self, self.bot, self.trigger, self.tcd)
        try:
            if self.condition and not await self.condition(*params):
                return 1
        except IgnoreException:
            return 1
        except:
            logger.exception(log_text + '在检查自身条件时发生异常.')
            return 2
        
        try:
            if self.exc.verify_params(params):
                await self.exc(*params)
            
        except IgnoreException:
            return 1
        except:
            logger.exception(log_text + '在处理事件时发生异常.')
            return 2

        return 0
