from contextvars import ContextVar
from dataclasses import dataclass

from typing import Any, Optional, overload, TYPE_CHECKING

from chara.core.bot import Bot
from chara.core.plugin.condition import Condition
from chara.core.plugin.handler import Handler
from chara.core.param import CONTEXT_LOOP
from chara.log import logger, style
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
    event: Event


class Trigger:
    '''
    ## 触发器
    '''

    __slots__ = ('alive', 'block', 'condition', 'handlers', 'name', 'plugin', 'priority')
    
    block: bool
    condition: Condition
    handlers: list[tuple[Executor[Any], Optional[Condition]]]
    name: Optional[str]
    plugin: 'Plugin'
    priority: int

    def __init__(self, condition: Condition, block: bool = False, name: Optional[str] = None, priority: int = 0) -> None:
        self.alive = True
        self.block = block
        self.condition = condition
        self.name = name
        self.priority = priority
        self.handlers = list()

    def __str__(self) -> str:
        return style.lc('Trigger') + f'[{style.g(self.plugin.metadata.name)}.' + style.lm(self.name or hex(id(self))) + ']'

    def handle(self, func: Optional[ExecutorCallable[Any]] = None, condition: Optional[Condition] = None) -> ExecutorCallable[Any]:
        '''
        ## 创建一个事务处理流程
        
        ---
        ### 参数
        - func: 处理流程函数
        - condition: 条件
        
        ---
        ### 触发时可选注入参数类型
        - dict [不同类型的Trigger不同]
        - muzibot.events.Event
        - muzibot.Bot
        '''
        def wrapper(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.handlers.append((Executor[Any](func), condition))
            return func
        if func is not None:
            return wrapper(func)
        else:
            return wrapper

    async def check(self, bot: Bot, event: Event) -> None:
        '''
        ## 检查事件是否可触发
        触发后开始事务处理流程
        
        ---
        ### 参数
        - event: 事件
        '''
        temp_context_tcd: ContextVar[Optional[TriggerCapturedData]] = ContextVar('temp_context_tcd', default=None)
        try:
            if await self.condition(event, self, bot, temp_context_tcd):
                if (tcd := temp_context_tcd.get()) is None:
                    tcd = TriggerCapturedData(event=event)
            else:
                return
        except:
            logger.exception(str(self) + style.r(' 在检查自身条件时发生异常.'))
            return
        finally:
            del temp_context_tcd
        
        loop = CONTEXT_LOOP.get()
        for exc, con in self.handlers:
            loop.create_task(Handler(bot, con, exc, loop, tcd, self)())


class Session(Trigger):
    '''
    ## 触发器(会话)
    '''

    __slots__ = ('alive', 'block', 'condition', 'handlers', 'name', 'plugin', 'priority', 'gid', 'uin')

    @overload
    def __init__(self, gid: int, uin: Optional[int], condition: Optional[Condition] = None) -> None:...

    @overload
    def __init__(self, gid: Optional[int], uin: int, condition: Optional[Condition] = None) -> None:...

    def __init__(self, gid: Optional[int], uin: Optional[int], condition: Optional[Condition] = None) -> None:
        if uin is None and gid is None:
            raise
        self.gid = gid
        self.uin = uin
        
        async def check(event: Event):
            event_dict = event.model_dump()
            gid = event_dict.get('group_id', None)
            uin = event_dict.get('user_id', None)
            if self.gid is None:
                return self.uin == uin
            elif self.uin is None:
                return self.gid == gid
            return self.uin == uin and self.gid == gid

        _condition = Condition(check)
        if condition is not None:
            _condition = _condition & condition
        super().__init__(_condition, True, None, -1)

    def __str__(self) -> str:
        return style.lc('Trigger') + f'[{style.g(self.plugin.metadata.name)}.' + style.lm(self.name or hex(id(self))) + ']'

