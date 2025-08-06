import re

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional, Type

from chara.core.bot import Bot
from chara.core.plugin import Condition, Trigger, TriggerCapturedData
from chara.lib.commandparse import CommandParser, ParseResult
from chara.onebot.events import Event, MessageEvent


@dataclass(repr=False, eq=False, slots=True)
class RegexTriggerCapturedData(TriggerCapturedData):
    '''## 正则触发器触发时捕获数据'''
    
    matched: re.Match[str]


@dataclass(repr=False, eq=False, slots=True)
class CommandTriggerCapturedData(TriggerCapturedData):
    '''## 命令触发器触发时捕获数据'''
    
    result: ParseResult


def event_trigger(event_type: Type[Event], condition: Optional[Condition] = None, block: bool = False, name: Optional[str] = None, priority: int = 1) -> Trigger:
    '''
    ## 创建一个基于事件类型的触发器

    ---
    ### 参数
    - event_type: 事件类型
    - condition: 条件
    - priority: 优先度
    - block: 是否阻塞低优先度触发器
    ---
    ### 触发时捕获数据结构
    - `TriggerCapturedData`
        - `event`: Event
        - `extra`: dict
    '''
    def checker(bot: Bot, event: Event, trigger: Trigger, context: ContextVar[TriggerCapturedData]) -> bool:
        if isinstance(event, event_type):
            context.set(trigger.captured_data_factory(bot=bot, event=event, extra=dict()))
            return True
        return False
    return Trigger(Condition(checker) & condition, block, priority, name, TriggerCapturedData)

def regex_trigger(pattern: str | re.Pattern[str], flags: re.RegexFlag = re.S, condition: Optional[Condition] = None, block: bool = False, name: Optional[str] = None, priority: int = 1) -> Trigger:
    '''
    ## 创建一个基于正则表达式的触发器

    ---
    ### 参数
    - pattern: 正则表达式
    - flags: 正则标记
    - condition: 条件
    - priority: 优先度
    - block: 是否阻塞低优先度触发器
    ---
    ### 触发时捕获数据结构
    - `RegexTriggerCatchedData`
        - `event`: Event
        - `extra`: dict
        - `matched`: re.Match[str]
    '''
    def checker(bot: Bot, event: MessageEvent, trigger: Trigger, context: ContextVar[TriggerCapturedData]) -> bool:
        if matched := re.search(pattern, event.pure_text.strip(), flags):
            context.set(trigger.captured_data_factory(bot=bot, event=event, extra=dict(), matched=matched))
            return True
        return False
    return Trigger(Condition(checker) & condition, block, priority, name, RegexTriggerCapturedData)

def command_trigger(parser: CommandParser, condition: Optional[Condition] = None, block: bool = False, name: Optional[str] = None, priority: int = 1) -> Trigger:
    '''
    ## 创建一个基于命令解析器的触发器

    ---
    ### 参数
    - parser: 命令解析器
    - condition: 条件
    - priority: 优先度
    - block: 是否阻塞低优先度触发器
    ---
    ### 触发时捕获数据结构
    - `CommandTriggerCatchedData`
        - `event`: Event
        - `extra`: dict
        - `result`: ParseResult
    '''
    def checker(bot: Bot, event: MessageEvent, trigger: Trigger, context: ContextVar[TriggerCapturedData]) -> bool:
        if result := parser.parse(event.pure_text.strip()):
            context.set(trigger.captured_data_factory(bot=bot, event=event, extra=dict(), result=result))
            return True
        return False
    return Trigger(Condition(checker) & condition, block, priority, name, CommandTriggerCapturedData)


__all__ = [
    'event_trigger',
    'regex_trigger',
    'command_trigger',
    'RegexTriggerCapturedData',
    'CommandTriggerCapturedData',
]

