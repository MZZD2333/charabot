from enum import IntEnum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from chara.core.bot import Bot
from chara.core.plugin.trigger import Trigger
from chara.lib.executor import Executor
from chara.log import style, logger
from chara.onebot.events import Event
from chara.typing import ExecutorCallable


class MetaData(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    uuid: str
    description: str
    authors: list[str]
    version: str
    docs: Optional[str] = None
    icon: Optional[str] = None


class PluginState(IntEnum):
    NOT_IMPORTED = 0
    WORKING = 1
    PART_WORKING = 2
    NOT_WORKING = 3


class Plugin:
    
    __slots__ = ('group', 'metadata', 'data_path', 'root_path', 'state', 'triggers', '_task_on_load', '_task_on_shutdown', '_task_on_bot_connect', '_task_on_bot_disconnect')
    
    group: str
    metadata: MetaData
    data_path: Path
    root_path: Path
    state: PluginState
    triggers: list[Trigger]
    
    _task_on_load: list[tuple[int, ExecutorCallable[Any]]]
    _task_on_shutdown: list[tuple[int, ExecutorCallable[Any]]]
    _task_on_bot_connect: list[tuple[int, ExecutorCallable[Any]]]
    _task_on_bot_disconnect: list[tuple[int, ExecutorCallable[Any]]]
    
    def __init__(self, group: str, metadata: MetaData) -> None:
        self.group = group
        self.metadata = metadata
        self.state = PluginState.NOT_IMPORTED
        self.triggers = list()
        self._task_on_load = list()
        self._task_on_shutdown = list()
        self._task_on_bot_connect = list()
        self._task_on_bot_disconnect = list()
    
    def __str__(self) -> str:
        return style.g('Plugin') + style.c(f'[{self.metadata.name}]') + style.m(f'[{self.metadata.version}]') + style.y(f'[{self.metadata.uuid}]')

    def __repr__(self) -> str:
        return style.g('Plugin') + style.c(f'[{self.metadata.name}]') + style.m(f'[{self.metadata.version}]') + style.y(f'[{self.metadata.uuid}]')

    async def _handle_event(self, bot: Bot, event: Event) -> None:
        triggers = self.triggers.copy()
        block = False
        for trigger in triggers:
            if not block and await trigger.check(bot, event):
                block = trigger.block

            if not trigger.alive and trigger in self.triggers:
                self.triggers.remove(trigger)
    
    async def _handle_task_on_load(self):
        for task in self._task_on_load:
            try:
                await task[1]()
            except:
                logger.exception(str(self) + f'在执行加载后任务时出错.')

    async def _handle_task_on_shutdown(self):
        for task in self._task_on_shutdown:
            try:
                await task[1]()
            except:
                logger.exception(str(self) + f'在执行进程结束前任务时出错.')

    async def _handle_task_on_bot_connect(self, bot: Bot):
        for task in self._task_on_bot_connect:
            try:
                await task[1](bot)
            except:
                logger.exception(str(self) + f'在执行连接至bot后任务时出错.')

    async def _handle_task_on_bot_disconnect(self, bot: Bot):
        for task in self._task_on_bot_disconnect:
            try:
                await task[1](bot)
            except:
                logger.exception(str(self) + f'在执行与bot断开任务时出错.')

    def add_trigger(self, trigger: list[Trigger] | Trigger) -> None:
        '''
        ## 添加一个触发器至当前插件
        '''
        if isinstance(trigger, list):
            for t in trigger:
                t.plugin = self
            self.triggers.extend(trigger)
        else:
            trigger.plugin = self
            self.triggers.append(trigger)
        self.triggers.sort(key=lambda t: t.priority)

    def on_load(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0):
        '''
        ## 创建一个在插件加载后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]):
            self._task_on_load.append((priority, Executor(func)))
            self._task_on_load.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_shutdown(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0):
        '''
        ## 创建一个在进程结束前执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]):
            self._task_on_shutdown.append((priority, Executor(func)))
            self._task_on_shutdown.sort(key=lambda t: t[0])
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_bot_connect(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0):
        '''
        ## 创建一个连接至bot后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]):
            self._task_on_bot_connect.append((priority, Executor(func)))
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

    def on_bot_disconnect(self, func: Optional[ExecutorCallable[Any]] = None, priority: int = 0):
        '''
        ## 创建一个与bot断开连接后执行的任务
        '''
        def wrap(func: ExecutorCallable[Any]):
            self._task_on_bot_disconnect.append((priority, Executor(func)))
            return func
        if func is not None:
            return wrap(func)
        else:
            return wrap

