from multiprocessing.connection import _ConnectionBase as Connection # type: ignore
from typing import Optional, Union

from chara.config import GlobalConfig, PluginGroupConfig
from chara.core.workers.worker import WorkerProcess
from chara.core.bot import Bot
from chara.core.bot.event import BotEvent, BotConnectedEvent, BotDisConnectedEvent
from chara.core.hazard import BOTS, CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG, CONTEXT_LOOP, PLUGINS
from chara.core.plugin.load import load_plugins
from chara.onebot.events import Event


class PluginGroupProcess(WorkerProcess):
    
    def __init__(self, config: PluginGroupConfig, global_config: GlobalConfig, name: str, pipes: Optional[tuple[Connection, Connection]] = None) -> None:
        self.config = config
        super().__init__(global_config, name, pipes, True)
    
    async def tick(self) -> None:
        while True:
            if not self.pipe_recv.poll():
                break
            
            event: Union[BotEvent, Event] = self.pipe_recv.recv()
            bot = BOTS[event.self_id]

            LOOP = CONTEXT_LOOP.get()
            if isinstance(event, Event):
                for plugin in PLUGINS.values():
                    LOOP.create_task(plugin.handle_event(bot, event))
                continue
            
            if isinstance(event, BotConnectedEvent):
                bot.connected = True
                for plugin in PLUGINS.values():
                    LOOP.create_task(plugin.tm.handle_on_bot_connect(bot))
            
            elif isinstance(event, BotDisConnectedEvent):
                bot.connected = False
                for plugin in PLUGINS.values():
                    LOOP.create_task(plugin.tm.handle_on_bot_disconnect(bot))
    
    async def shutdown(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        for plugin in PLUGINS.values():
            LOOP.create_task(plugin.tm.handle_on_shutdown())
    
    async def startup(self) -> None:
        # hazard
        LOOP = CONTEXT_LOOP.get()
        CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG.set(self.config)
        
        # bot
        BOTS.update({config.uin: Bot(config) for config in self.global_config.bots})
        
        # plugin
        load_plugins()
        for plugin in PLUGINS.values():
            LOOP.create_task(plugin.tm.handle_on_load())
    
    def new(self) -> 'PluginGroupProcess':
        return PluginGroupProcess(self.config, self.global_config, self.name, (self.pipe_recv, self.pipe_send))

