from typing import Any, Optional, Union

from chara.lib.executor import Executor
from chara.typing import ConditionCallable


class Condition:
    '''
    ## 条件类

    同时使用多个条件时用`&`连接 如 `A & B`
    '''
    __slots__ = ('checkers', )

    def __init__(self, *checkers: Union[ConditionCallable, Executor[bool]]) -> None:
        self.checkers: set[Executor[bool]] = {checker if isinstance(checker, Executor) else Executor[bool](checker) for checker in checkers}

    async def __call__(self, *args: Any) -> bool:
        for checker in self.checkers:
            if not checker.verify_params(args):
                return False
            if not await checker(*args):
                return False
        return True

    def __and__(self, other: Optional[Union['Condition', ConditionCallable, Executor[bool]]]) -> 'Condition':
        if other is None:
            return self
        if isinstance(other, Condition):
            return Condition(*self.checkers, *other.checkers)
        else:
            return Condition(*self.checkers, other)

    def __rand__(self, other: Optional[Union['Condition', ConditionCallable, Executor[bool]]]) -> 'Condition':
        if other is None:
            return self
        if isinstance(other, Condition):
            return Condition(*other.checkers, *self.checkers)
        else:
            return Condition(other, *self.checkers)


__all__ = [
    'Condition',
]

