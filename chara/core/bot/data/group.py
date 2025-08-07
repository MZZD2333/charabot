from typing import Any, Generator, Optional



class Group:
    
    __slots__ = ('group_id', 'group_name', 'member_count', 'max_member_count', 'role')
    
    def __init__(self, group_id: int, group_name: str = '', member_count: int = 0, max_member_count: int = 200, **kwargs: Any) -> None:
        self.group_id = int(group_id)
        self.group_name = group_name
        self.member_count = member_count
        self.max_member_count = max_member_count
        
    def json(self) -> dict[str, Any]:
        return {
            'group_id': self.group_id,
            'group_name': self.group_name,
            'member_count': self.member_count,
            'max_member_count': self.max_member_count,
        }


class Groups:
    
    __slots__ = ('_groups', 'owned', 'admin')
    
    _groups: dict[int, Group]
    owned: list[int]
    admin: list[int]
    
    def __init__(self) -> None:
        self._groups = dict()
        self.owned = list()
        self.admin = list()
    
    def __contains__(self, gid: int) -> bool:
        return gid in self._groups
    
    def __getitem__(self, gid: int) -> Optional[Group]:
        return self._groups.get(gid, None)
    
    def __iter__(self) -> Generator[tuple[int, Group], Any, None]:
        for gid, group in self._groups.items():
            yield gid, group
    
    def get(self, gid: int) -> Optional[Group]:
        return self._groups.get(gid, None)

    def update(self, data: dict[str, Any]) -> None:
        try:
            if group_list := data.get('list', None):
                for gd in group_list:
                    group = Group(**gd)
                    self._groups[group.group_id] = group
            
            if owned := data.get('owned', None):
                for gid in owned:
                    if gid not in self.owned:
                        self.owned.append(gid)
        
            if admin := data.get('admin', None):
                for gid in admin:
                    if gid not in self.admin:
                        self.admin.append(gid)
        except:
            pass
    
    def json(self) -> dict[str, Any]:
        return {'owned': self.owned, 'admin': self.admin, 'list': [group.json() for group in self._groups.values()]}

