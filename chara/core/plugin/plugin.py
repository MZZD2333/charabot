from enum import IntEnum
from packaging.version import Version
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from chara.core.bot import Bot
from chara.core.plugin.trigger import Trigger
from chara.onebot.events import Event


class MetaData(BaseModel):
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed=True)

    name: str
    uuid: str
    description: str
    authors: list[str]
    version: Version
    icon: Optional[str] = None
    readme: Optional[str] = None

    @field_validator('version', mode='before')
    def _check_version(cls, version: str) -> Version:
        return Version(version)


class PluginState(IntEnum):
    NOT_IMPORTED = 0
    WORKING = 1
    PART_WORKING = 2
    NOT_WORKING = 3


class Plugin:
    
    __slots__ = ('metadata', 'triggers', 'state')
    
    metadata: MetaData
    triggers: list[Trigger]
    state: PluginState
    
    def __init__(self, metadata: MetaData) -> None:
        self.metadata = metadata
        self.triggers = list()
        self.state = PluginState.NOT_IMPORTED
    
    def __str__(self) -> str:
        return f'Plugin[{self.metadata.name}][{self.metadata.version}][{self.metadata.uuid}]'

    def __repr__(self) -> str:
        return f'Plugin[{self.metadata.name}][{self.metadata.version}][{self.metadata.uuid}]'

    def add_trigger(self, trigger: list[Trigger] | Trigger) -> None:
        if isinstance(trigger, list):
            for t in trigger:
                t.plugin = self
            self.triggers.extend(trigger)
        else:
            trigger.plugin = self
            self.triggers.append(trigger)
        self.triggers.sort(key=lambda t: t.priority)

    async def handle_event(self, bot: Bot, event: Event) -> None:
        triggers = self.triggers.copy()
        block = False
        for trigger in triggers:
            if not block and await trigger.check(bot, event):
                block = trigger.block

            if not trigger.alive and trigger in self.triggers:
                self.triggers.remove(trigger)

