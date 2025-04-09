from chara.core.plugin import PluginState


class CoreEvent:
    __slots__ = ()


class PluginStatusUpdateEvent(CoreEvent):
    __slots__ = ('group_name', 'status')

    def __init__(self, group_name: str, status: dict[str, PluginState]) -> None:
        self.group_name = group_name
        self.status = status


class BotEvent(CoreEvent):
    __slots__ = ('self_id', )
    
    def __init__(self, self_id: int) -> None:
        self.self_id = self_id


class BotConnectedEvent(BotEvent):
    __slots__ = ('self_id', )


class BotDisConnectedEvent(BotEvent):
    __slots__ = ('self_id', )


