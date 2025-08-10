from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Optional, Union

from chara.core.bot import Bot
from chara.core.color import colorize
from chara.core.plugin.trigger import Trigger
from chara.core.share import shared_plugin_state
from chara.log import logger
from chara.lib.executor import Executor
from chara.onebot.events import Event
from chara.typing import ExecutorCallable


@dataclass(eq=False, repr=False, slots=True)
class PlugiMetaData:
    name: str
    uuid: str
    description: str
    authors: list[str]
    version: str
    docs: Optional[str] = None
    icon: Optional[str] = None

    def __post_init__(self) -> None:
        self.name = str(self.name)
        self.uuid = str(self.uuid)
        self.description = str(self.description)
        self.authors = list(map(str, self.authors))
        self.version = str(self.version)
        
        if self.docs is not None:
            self.docs = self.docs.lstrip('.').lstrip('/')
        if self.icon is not None:
            self.docs = self.icon.lstrip('.').lstrip('/')


class PluginState(IntEnum):
    NOT_IMPORTED = 0
    WORKING = 1
    PART_WORKING = 2
    NOT_WORKING = 3


class PluginTaskManager:
    
    __slots__ = ('on_load', 'on_shutdown', 'on_bot_connect', 'on_bot_disconnect', 'plugin')
        
    on_load: list[tuple[int, ExecutorCallable[Any]]]
    on_shutdown: list[tuple[int, ExecutorCallable[Any]]]
    on_bot_connect: list[tuple[int, ExecutorCallable[Any]]]
    on_bot_disconnect: list[tuple[int, ExecutorCallable[Any]]]

    def __init__(self, plugin: 'Plugin') -> None:
        self.on_load = list()
        self.on_shutdown = list()
        self.on_bot_connect = list()
        self.on_bot_disconnect = list()
        self.plugin = plugin

    async def handle_on_load(self) -> None:
        for task in self.on_load:
            try:
                await task[1]()
            except:
                logger.exception(colorize.plugin(self.plugin) + f'在执行加载后任务时出错.')

    async def handle_on_shutdown(self) -> None:
        for task in self.on_shutdown:
            try:
                await task[1]()
            except:
                logger.exception(colorize.plugin(self.plugin) + f'在执行进程结束前任务时出错.')

    async def handle_on_bot_connect(self, bot: Bot) -> None:
        for task in self.on_bot_connect:
            try:
                await task[1](bot)
            except:
                logger.exception(colorize.plugin(self.plugin) + f'在执行连接至bot后任务时出错.')

    async def handle_on_bot_disconnect(self, bot: Bot) -> None:
        for task in self.on_bot_disconnect:
            try:
                await task[1](bot)
            except:
                logger.exception(colorize.plugin(self.plugin) + f'在执行与bot断开任务时出错.')


class Plugin:
    
    __slots__ = ('config', 'index', 'group', 'metadata', 'data_path', 'root_path', 'triggers', 'tm', '_sv_state')
    
    config: dict[str, Any]
    index: int
    '''## 插件编号(导入顺序)'''
    group: str
    '''## 插件组名称'''
    metadata: PlugiMetaData
    data_path: Path
    '''## 数据目录'''
    root_path: Path
    '''## 插件目录'''
    triggers: list[Trigger]
    tm: PluginTaskManager
    
    def __init__(self, metadata: PlugiMetaData) -> None:
        self.config = dict()
        self.metadata = metadata
        self.triggers = list()
        self.tm = PluginTaskManager(self)
        self._sv_state = shared_plugin_state(metadata.uuid)
    
    @property
    def state(self) -> PluginState:
        return PluginState(self._sv_state.value)
    
    @state.setter
    def state(self, s: Union[int, PluginState]) -> None:
        if isinstance(s, PluginState):
            s = s.value
        assert 0 <= s < 4
        self._sv_state.write(s)

    @property
    def data(self) -> dict[str, Any]:
        return {
            'index': self.index,
            'uuid': self.metadata.uuid,
            'name': self.metadata.name,
            'group': self.group,
            'state': self.state.value,
            'authors': self.metadata.authors,
            'version': self.metadata.version,
            'description': self.metadata.description,
            'icon': self.metadata.icon,
            'docs': self.metadata.docs,
        }

    async def handle_event(self, bot: Bot, event: Event) -> None:
        triggers = self.triggers.copy()
        block = False
        for trigger in triggers:
            if not block and await trigger.check(bot, event):
                block = trigger.block

            if not trigger.alive and trigger in self.triggers:
                self.triggers.remove(trigger)
    
    def add_trigger(self, trigger: list[Trigger] | Trigger) -> None:
        '''
        ## 添加触发器至当前插件
        '''
        if isinstance(trigger, list):
            for t in trigger:
                t.plugin = self
            self.triggers.extend(trigger)
        else:
            trigger.plugin = self
            self.triggers.append(trigger)
        self.triggers.sort(key=lambda t: t.priority)

    def on_load(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0) -> ExecutorCallable[Any]:
        '''
        ## 创建一个在插件加载完成后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.tm.on_load.append((priority, Executor(func)))
            self.tm.on_load.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_shutdown(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0) -> ExecutorCallable[Any]:
        '''
        ## 创建一个在进程结束前执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.tm.on_shutdown.append((priority, Executor(func)))
            self.tm.on_shutdown.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_bot_connect(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0) -> ExecutorCallable[Any]:
        '''
        ## 创建一个连接至bot后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.tm.on_bot_connect.append((priority, Executor(func)))
            self.tm.on_bot_connect.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_bot_disconnect(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0) -> ExecutorCallable[Any]:
        '''
        ## 创建一个与bot断开连接后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]) -> ExecutorCallable[Any]:
            self.tm.on_bot_disconnect.append((priority, Executor(func)))
            self.tm.on_bot_disconnect.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap
    
