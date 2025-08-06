from pathlib import Path
from typing import Awaitable, Callable, TypeAlias, TypeVar, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chara.onebot.message import Message, MessageSegment


T = TypeVar('T')

PathLike: TypeAlias = Union[str, Path]

ExecutorCallable: TypeAlias = Union[Callable[..., T], Callable[..., Awaitable[T]]]

ConditionCallable: TypeAlias = ExecutorCallable[bool]
'''
## Condition类的检查器类型

依赖参数:
- chara.onebot.events.Event
- chara.plugin.Bot
- chara.plugin.Handler [Trigger的Condition不具有此项]
- chara.plugin.Trigger
- chara.plugin.TriggerCapturedData [不同类型的Trigger不同]
'''

MessageLike: TypeAlias = Union['Message', 'MessageSegment', str]
'''
## 可发送的消息类型
- `Message`
- `MessageSegment`
- `str`
'''

Number: TypeAlias = Union[str, int]

