
from typing import Any, Generator, Union



class SuperUsers:
    
    __slots__ = ('_global', '_groups')
    
    _global: list[int]
    _groups: dict[int, list[int]]
    
    def __init__(self, _global: list[int]) -> None:
        self._global = _global
        self._groups = dict()
    
    def __contains__(self, superuser: Union[int, str]) -> bool:
        return superuser in self._global
    
    def __iter__(self) -> Generator[int, Any, None]:
        for superuser in self._global:
            yield superuser

    def __getitem__(self, gid: int) -> list[int]:
        return self._groups.get(gid, list())

    def __setitem__(self, gid: int, superuser: int) -> None:
        if gid in self._groups:
            self._groups[gid].append(superuser)
        else:
            self._groups.setdefault(gid, [superuser])

    def update(self, data: dict[str, Any]) -> None:
        try:
            if _global := data.get('global', None):
                if isinstance(_global, list):
                    self._global = _global
            
            if _groups := data.get('groups', None):
                if isinstance(_global, dict):
                    self._groups.update(_groups)
        except:
            pass

    def json(self) -> dict[str, Any]:
        return {'global': self._global, 'groups': self._groups}

