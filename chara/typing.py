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
- `Bot`: 当前Bot实例
- `Event`: 当前Event实例
'''

MessageLike: TypeAlias = Union['Message', 'MessageSegment', str]
'''
## 可发送的消息类型
- `Message`
- `MessageSegment`
- `str`
'''

