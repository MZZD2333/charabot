from dataclasses import dataclass

from chara.core.plugin import PluginState


@dataclass(repr=False, eq=False, slots=True)
class CoreEvent:
    pass


@dataclass(repr=False, eq=False, slots=True)
class PluginStatusUpdateEvent(CoreEvent):
    group_name: str
    status: dict[str, PluginState]


@dataclass(repr=False, eq=False, slots=True)
class BotEvent(CoreEvent):
    self_id: int


@dataclass(repr=False, eq=False, slots=True)
class BotConnectedEvent(BotEvent):
    pass


@dataclass(repr=False, eq=False, slots=True)
class BotDisConnectedEvent(BotEvent):
    pass

