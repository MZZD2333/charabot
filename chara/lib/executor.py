import inspect

from typing import Any, Awaitable, Callable, Generic, Type, TypeAlias, TypeVar, Union, get_origin
from types import GenericAlias


R = TypeVar('R', default=Any)

ExecutorCallable: TypeAlias = Union[Callable[..., R], Callable[..., Awaitable[R]]]

class Executor(Generic[R]):
    '''
    ## 执行器
    '''
    
    __slots__ = ('__func', '__awaitable', '__param_annotations')
    
    def __init__(self, func: ExecutorCallable[R]) -> None:
        self.__func = func
        self.__awaitable = self.__is_awaitable(func)
        self.__param_annotations = self.__get_param_annotations(func)

    @property
    def func(self) -> ExecutorCallable[R]:
        return self.__func

    async def __call__(self, *params: Any) -> R:
        if self.__awaitable:
            return await self.__func(*self.__parse_params(params)) # type: ignore
        else:
            return self.__func(*self.__parse_params(params)) # type: ignore

    def __is_awaitable(self, call: Callable[..., Any]) -> bool:
        if inspect.isroutine(call):
            return inspect.iscoroutinefunction(call)
        elif inspect.isclass(call):
            return False
        else:
            return inspect.iscoroutinefunction(getattr(call, '__call__', None))

    def __get_param_annotations(self, func: ExecutorCallable[R]) -> tuple[Type[Any], ...]:
        params = list(inspect.signature(func).parameters.values())
        return tuple(get_origin(param.annotation) if isinstance(param.annotation, GenericAlias) else param.annotation for param in params)

    def __parse_params(self, params: tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(next((param for param in params if isinstance(param, t)), None) for t in self.__param_annotations)

    def verify_params(self, params: tuple[Any, ...]) -> bool:
        return all(any(isinstance(arg, t) for arg in params) for t in self.__param_annotations)


__all__ = [
    'Executor',
    'ExecutorCallable',
]

