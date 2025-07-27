
from typing import Any, Generator



class NickNames:
    
    __slots__ = ('_global', '_groups')
    
    _global: list[str]
    _groups: dict[int, list[str]]
    
    def __init__(self, _global: list[str]) -> None:
        self._global = _global
        self._groups = dict()
    
    def __contains__(self, nickname: str) -> bool:
        return nickname in self._global
    
    def __iter__(self) -> Generator[str, Any, None]:
        for nickname in self._global:
            yield nickname

    def __getitem__(self, gid: int) -> list[str]:
        return self._groups.get(gid, list())

    def __setitem__(self, gid: int, nickname: str) -> None:
        if gid in self._groups:
            self._groups[gid].append(nickname)
        else:
            self._groups.setdefault(gid, [nickname])

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

