from typing import TYPE_CHECKING

from chara.core.share import shared_bot_protocol

if TYPE_CHECKING:
    from chara.core.bot import Bot


class Protocol:
    
    __slots__ = ('_sv_protocol', )
    
    def __init__(self, bot: 'Bot') -> None:
        self._sv_protocol = shared_bot_protocol(f'bot_protocol_{bot.uin}')

    @property
    def name(self) -> str:
        return self._sv_protocol.value
    
    @name.setter
    def name(self, value: str) -> None:
        self._sv_protocol.write(value)
    
    @property
    def onebot(self) -> bool:
        name = self._sv_protocol.value.lower()
        return 'onebot' in name

    @property
    def napcat(self) -> bool:
        name = self._sv_protocol.value.lower()
        return 'napcat' in name
    
    @property
    def lagrange(self) -> bool:
        name = self._sv_protocol.value.lower()
        return 'lagrange' in name

