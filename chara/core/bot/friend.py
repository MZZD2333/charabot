from typing import Any, Generator, Optional


class Friend:
    
    __slots__ = ('user_id', 'nickname', 'remark')
    
    def __init__(self, user_id: int, nickname: str = '', remark: str = '', **kwargs: Any) -> None:
        self.user_id = user_id
        self.nickname = nickname
        self.remark = remark

    def json(self) -> dict[str, Any]:
        return {
            'user_id': self.user_id,
            'nickname': self.nickname,
            'remark': self.remark,
        }


class Friends:
    
    __slots__ = ('_friends')
    
    _friends: dict[int, Friend]
    
    def __init__(self) -> None:
        self._friends = dict()
    
    def __contains__(self, uid: int) -> bool:
        return uid in self._friends
    
    def __getitem__(self, uid: int) -> Optional[Friend]:
        return self._friends.get(uid, None)
    
    def __iter__(self) -> Generator[tuple[int, Friend], Any, None]:
        for uid, friend in self._friends.items():
            yield uid, friend

    def get(self, uid: int) -> Optional[Friend]:
        return self._friends.get(uid, None)

    def update(self, data: list[dict[str, Any]]) -> Any:
        try:
            for fd in data:
                friend = Friend(**fd)
                self._friends[friend.user_id] = friend
        except:
            pass
    
    def json(self) -> list[dict[str, Any]]:
        return [friend.json() for friend in self._friends.values()]

