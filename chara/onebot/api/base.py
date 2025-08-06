from typing import NoReturn


class API:
    
    __slots__ = ()

    def __getattr__(self, name: str) -> NoReturn:
        raise Exception(f'请使用bot[{type(self).__name__}].{name}调用.')

