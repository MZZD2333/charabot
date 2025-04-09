import inspect

from typing import Any, Awaitable, Callable, Generic, Type, TypeAlias, TypeVar, Union
from types import GenericAlias


R = TypeVar('R')

ExecutorCallable: TypeAlias = Union[Callable[..., R], Callable[..., Awaitable[R]]]

class Executor(Generic[R]):
    '''
    ## 执行器
    '''
    
    __slots__ = ('__callable', '__is_awaitable', '__param_annotations')
    
    def __init__(self, call: ExecutorCallable[R]) -> None:
        self.__callable = call
        self.__is_awaitable = _is_awaitable(call)
        self.__param_annotations = self.__get_param_annotations(call)

    async def __call__(self, *params: Any) -> R:
        if self.__is_awaitable:
            return await self.__callable(*self.__parse_params(params)) # type: ignore[call-arg]
        else:
            return self.__callable(*self.__parse_params(params)) # type: ignore[call-arg]

    def __get_param_annotations(self, func: ExecutorCallable[R]) -> tuple[Type[Any], ...]:
        params = list(inspect.signature(func).parameters.values())
        return tuple(param.annotation.__origin__ if isinstance(param.annotation, GenericAlias) else param.annotation for param in params)

    def __parse_params(self, params: tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(next((param for param in params if isinstance(param, t)), None) for t in self.__param_annotations)

    def verify_params(self, params: tuple[Any, ...]) -> bool:
        return all(any(isinstance(arg, t) for arg in params) for t in self.__param_annotations)


def _is_awaitable(call: Callable[..., Any]) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    elif inspect.isclass(call):
        return False
    else:
        return inspect.iscoroutinefunction(getattr(call, '__call__', None))


__all__ = [
    'Executor',
    'ExecutorCallable',
]
