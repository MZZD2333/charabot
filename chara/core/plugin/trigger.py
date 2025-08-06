from asyncio import AbstractEventLoop
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Callable, Generator, NoReturn, Optional, overload, TYPE_CHECKING

from chara.core.bot import Bot
from chara.core.color import colorize
from chara.core.hazard import CONTEXT_LOOP
from chara.core.plugin.condition import Condition
from chara.core.plugin.handler import Handler
from chara.exception import IgnoreException, KillTrigger
from chara.log import logger
from chara.lib.executor import Executor
from chara.onebot.events import Event
from chara.typing import ExecutorCallable

if TYPE_CHECKING:
    from chara.core.plugin.plugin import Plugin


@dataclass(repr=False, eq=False, slots=True)
class TriggerCapturedData:
    '''
    ## 触发器触发时捕获数据
    '''
    
    bot: Bot
    event: Event
    extra: dict[str, Any]


class Trigger:
    '''
    ## 触发器
    '''

    __slots__ = ('alive', 'block', 'condition', 'handlers', 'name', 'plugin', 'priority', 'captured_data_factory')
    
    block: bool
    condition: Condition
    handlers: list[Handler]
    name: Optional[str]
    plugin: 'Plugin'
    priority: int
    captured_data_factory: Callable[..., TriggerCapturedData]

    def __init__(self, condition: Condition, block: bool = False, priority: int = 0, name: Optional[str] = None, captured_data_factory: Callable[..., TriggerCapturedData] = TriggerCapturedData) -> None:
        '''
        ## 创建一个触发器
        
        ---
        ### 参数
        - condition: 条件
        - block: 是否阻塞
        - priority: 优先级
        - name: 名字
        '''
        self.alive = True
        self.block = block
        self.condition = condition
        self.name = name
        self.priority = priority
        self.handlers = list()
        self.captured_data_factory = captured_data_factory

    def kill(self) -> NoReturn:
        self.alive = False
        raise KillTrigger

    def handle(self, func: Optional[ExecutorCallable[Any]] = None, condition: Optional[Condition] = None) -> ExecutorCallable[Any]:
        '''
        ## 创建一个事件处理流程
        
        ---
        ### 参数
        - func: 处理流程函数
        - condition: 条件
        
        ---
        ### 触发时可选注入参数类型
        - chara.onebot.events.Event
        - chara.plugin.Bot
        - chara.plugin.Handler
        - chara.plugin.Trigger
        - chara.plugin.TriggerCapturedData [不同类型的Trigger不同]
        '''
        def wrapper(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.handlers.append(Handler(Executor[Any](func), condition, self))
            return func
        if func is not None:
            return wrapper(func)
        else:
            return wrapper

    def exchange_handler(self, func: Optional[ExecutorCallable[Any]] = None, condition: Optional[Condition] = None, index: int = 0) -> ExecutorCallable[Any]:
        '''
        ## 替换一个事件处理流程
        
        ---
        ### 参数
        - func: 处理流程函数
        - condition: 条件
        - index: 索引
        '''
        if len(self.handlers) == 0:
            return self.handle(func, condition)
        
        assert 0 <= index < len(self.handlers)
        
        def wrapper(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.handlers[index] = Handler(Executor[Any](func), condition, self)
            return func
        if func is not None:
            return wrapper(func)
        else:
            return wrapper
    
    async def check(self, bot: Bot, event: Event) -> None:
        '''
        ## 检查事件是否可触发
        触发后开始事件处理流程
        
        ---
        ### 参数
        - event: 事件
        '''
        if not self.alive:
            return
        
        loop = CONTEXT_LOOP.get()
        temp_context_tcd: ContextVar[Optional[TriggerCapturedData]] = ContextVar('temp_context_tcd', default=None)
        try:
            if await self.condition(event, self, bot, temp_context_tcd):
                if (tcd := temp_context_tcd.get()) is None:
                    tcd = self.captured_data_factory(bot=bot, event=event, extra=dict())
            else:
                return
        
        except IgnoreException:
            return
        
        except:
            logger.exception(colorize.trigger(self) + '在检查自身条件时发生异常.')
            return
        
        finally:
            del temp_context_tcd
        
        loop.create_task(self._handle(self.handlers.copy(), bot, loop, tcd))
    
    async def _handle(self, handlers: list[Handler], bot: Bot, loop: AbstractEventLoop, tcd: TriggerCapturedData) -> None:
        log_text = colorize.trigger(self)
        logger.info(log_text + '将处理这个事件.')
        count = [0, 0, 0]
        for handler in handlers:
            result = await handler.new(bot, loop, tcd)()
            count[result] += 1
        
        logger.success(log_text + colorize.handler_results(count) + '处理完毕.')


class SessionHistory:
    
    __slots__ = ('events', 'maxsize')
    
    events: list[Event]
    maxsize: int
    
    def __init__(self, maxsize: int) -> None:
        self.events = list()
        self.maxsize = maxsize
    
    def __iter__(self) -> Generator[Event, Any, None]:
        for event in self.events:
            yield event
    
    def put(self, event: Event) -> None:
        if self.maxsize > 0:
            if self.length > self.maxsize:
                self.events = self.events[-self.maxsize:]
            self.events.append(event)
        
        elif self.maxsize < 0:
            self.events.append(event)
    
    @property
    def length(self) -> int:
        return len(self.events)


class Session(Trigger):
    '''
    ## 触发器(会话)
    '''

    __slots__ = ('alive', 'block', 'condition', 'handlers', 'name', 'plugin', 'priority', 'gid', 'uid', 'history')
    
    history: SessionHistory

    @overload
    def __init__(self, *, gid: int, condition: Optional[Condition] = None, history_maxsize: int = 0) -> None:
        '''
        ## 接收群消息
        
        ---
        ### 参数
        - gid: 群号
        - condition: 条件
        - history_maxsize: 最大历史消息记录数量, `0`时不记录, 小于`0`时无上限
        '''

    @overload
    def __init__(self, *, uid: int, condition: Optional[Condition] = None, history_maxsize: int = 0) -> None:
        '''
        ## 接收私聊消息
        
        ---
        ### 参数
        - uid: QQ号
        - condition: 条件
        - history_maxsize: 最大历史消息记录数量, `0`时不记录, 小于`0`时无上限
        '''

    @overload
    def __init__(self, *, gid: int, uid: int, condition: Optional[Condition] = None, history_maxsize: int = 0) -> None:
        '''
        ## 接收群成员消息
        
        ---
        ### 参数
        - gid: 群号
        - uid: QQ号
        - condition: 条件
        - history_maxsize: 最大历史消息记录数量, `0`时不记录, 小于`0`时无上限
        '''

    def __init__(self, *, gid: Optional[int] = None, uid: Optional[int] = None, condition: Optional[Condition] = None, history_maxsize: int = 0) -> None:
        if uid is None and gid is None:
            raise
        self.gid = gid
        self.uid = uid
        self.history = SessionHistory(history_maxsize)
        
        async def check(event: Event):
            event_dict = event.model_dump()
            gid = event_dict.get('group_id', None)
            uid = event_dict.get('user_id', None)
            if self.gid is None:
                result = self.uid == uid
            elif self.uid is None:
                result = self.gid == gid
            else:
                result = self.uid == uid and self.gid == gid
            if result:
                self.history.put(event)
            return result

        new_condition = Condition(check)
        if condition is not None:
            new_condition = new_condition & condition
        
        super().__init__(new_condition, True, -1, None)

