import asyncio

from dataclasses import dataclass
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


@dataclass(repr=False, eq=False, slots=True)
class Handler:
    bot: Bot
    condition: Optional[Condition]
    exc: Executor[Any]
    loop: asyncio.AbstractEventLoop
    tcd: 'TriggerCapturedData'
    trigger: 'Trigger'
    _is_running: bool = False
        
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
        ## 发送消息并立即结束当前事务处理流程
        
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

    async def __call__(self) -> None:
        log_text = colorize.handler(self)
        if self._is_running:
            logger.warning(log_text + '被循环调用.')
            return
        
        self._is_running = True
        event = self.tcd.event
        logger.info(log_text + '将处理这个事件.')
        try:
            if self.condition and not await self.condition(event, self, self.bot, self.tcd):
                return
        except IgnoreException:
            return
        except:
            logger.exception(log_text + '在检查自身条件时发生异常.')
            return
        
        try:
            if not self.exc.verify_params((event, self, self.bot, self.tcd)):
                logger.warning(log_text + '类型验证未通过.')
            await self.exc(event, self, self.bot, self.tcd)
            
        except IgnoreException:
            return
        except:
            logger.exception(log_text + '在处理事件时发生异常.')
            return
        logger.success(log_text + '处理完毕.')

