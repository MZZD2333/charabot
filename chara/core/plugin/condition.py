from typing import Any, Optional, Union

from chara.lib.executor import Executor, ExecutorCallable
from chara.typing import ConditionCallable


class Checker(Executor[bool]):

    __slots__ = ('__callable', '__awaitable', '__param_annotations', '__invert')
    
    def __init__(self, call: ExecutorCallable[bool], invert: bool = False) -> None:
        super().__init__(call)
        self.__invert = invert
    
    def __neg__(self) -> 'Checker':
        return Checker(self.func, not self.__invert)
    
    async def __call__(self, *params: Any) -> bool:
        result = await super().__call__(*params)
        if self.__invert:
            return not result
        return result


class Condition:
    '''
    ## 条件类

    同时使用多个条件时可用`&`连接, 如`A & B`
    
    使用`-`取对立条件, 如`-A`
    '''
    __slots__ = ('checkers', )
    
    checkers: set[Checker]

    def __init__(self, *checkers: Union[ConditionCallable, Executor[bool]]) -> None:
        self.checkers = {Checker(checker.func) if isinstance(checker, Executor) else Checker(checker) for checker in checkers}

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

    def __neg__(self) -> 'Condition':
        condition = Condition()
        condition.checkers = set(-c for c in self.checkers)
        return condition
    
    async def __call__(self, *params: Any) -> bool:
        for checker in self.checkers:
            if not checker.verify_params(params):
                return False
            if not await checker(*params):
                return False
        return True


__all__ = [
    'Condition',
]

