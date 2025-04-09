import asyncio

from dataclasses import dataclass
from typing import Any, NoReturn, Optional, TYPE_CHECKING

from chara.core.bot import Bot
from chara.core.plugin.condition import Condition
from chara.exception import HandleFinished
from chara.log import logger, style
from chara.lib.executor import Executor
from chara.onebot.message import Message, MessageSegment
from chara.typing import MessageLike

if TYPE_CHECKING:
    from chara.core.plugin.trigger import Trigger, TriggerCapturedData


@dataclass(repr=False, eq=False, frozen=False, slots=True)
class Handler:
    bot: Bot
    condition: Optional[Condition]
    exc: Executor[Any]
    tcd: 'TriggerCapturedData'
    loop: asyncio.AbstractEventLoop
    _trigger: 'Trigger'
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
        group_id = event_dict.get('group_id', None)
        user_id = event_dict.get('user_id', None)
        if group_id:
            params['group_id'] = group_id
        elif user_id:
            params['user_id'] = user_id
        else:
            # TODO: 添加日志
            raise
        message = Message(message)
        if at_sender and group_id and user_id:
            message = MessageSegment.at(str(user_id)) + message
        params['message'] = message
        
        response = await self.bot.send_msg(**params)
        message_id = response['message_id']
        if recall_after > 0:
            async def delete(mid: int):
                await asyncio.sleep(recall_after)
                try:
                    await self.bot.delete_msg(message_id=mid)
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

    async def __call__(self):
        if self._is_running:
            # TODO: 添加日志
            logger.warning(self._trigger._trigger_info + style.r(' catch an exception while checking handler\'s condition.')) # type: ignore
            return
        self._is_running = True
        event = self.tcd.event
        logger.success(self._trigger._trigger_info + ' will handle this event.') # type: ignore
        try:
            if self.condition and not await self.condition(event, self, self.bot, self.tcd):
                return
        except HandleFinished:
            return
        except:
            logger.exception(self._trigger._trigger_info + style.r(' catch an exception while checking handler\'s condition.')) # type: ignore
            return
        
        try:
            if self.exc.verify_params((event, self, self.bot, self.tcd)):
                await self.exc(event, self, self.bot, self.tcd)
        except HandleFinished:
            return
        except:
            logger.exception(self._trigger._trigger_info + style.r(' catch an exception while handler processing.')) # type: ignore
            return
        logger.success(self._trigger._trigger_info + ' execute completely.') # type: ignore
