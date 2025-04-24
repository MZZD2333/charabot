import asyncio
import pickle

from multiprocessing.connection import Connection, PipeConnection
from typing import Union

from chara.config import GlobalConfig, PluginGroupConfig
from chara.core.workers.worker import WorkerProcess
from chara.core.event import PluginStatusUpdateEvent, BotEvent, BotConnectedEvent, BotDisConnectedEvent, CoreEvent
from chara.onebot.events import Event


class PluginGroupProcess(WorkerProcess):
    
    def __init__(self, config: GlobalConfig, group_config: PluginGroupConfig, pipe_c: Union[Connection, PipeConnection], pipe_p: Union[Connection, PipeConnection]) -> None:
        super().__init__(config, group_config.group_name)
        self.config = config
        self.group_config = group_config
        self.pipe_c = pipe_c
        self.pipe_p = pipe_p

    def _tick(self, future: asyncio.Future[None]):
        try:
            future.set_result(None)
        except:
            pass

    async def main(self) -> None:
        from chara.core.param import BOTS, CONTEXT_LOOP, PLUGINS

        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        
        ticks = 0
        while not self.should_exit:
            ticks += 1
            if self.pipe_c.poll():
                event: Union[CoreEvent, Event] = self.pipe_c.recv()
                if isinstance(event, CoreEvent):
                    if isinstance(event, BotEvent):
                        bot = BOTS[event.self_id]
                        if isinstance(event, BotConnectedEvent):
                            bot.connected = True
                            await bot.update_bot_info()
                            for plugin in PLUGINS.values():
                                LOOP.create_task(plugin._handle_task_on_bot_connect(bot)) # type: ignore
                        elif isinstance(event, BotDisConnectedEvent):
                            bot.connected = False
                            for plugin in PLUGINS.values():
                                LOOP.create_task(plugin._handle_task_on_bot_disconnect(bot)) # type: ignore
                    continue
                
                bot = BOTS[event.self_id]
                for plugin in PLUGINS.values():
                    LOOP.create_task(plugin._handle_event(bot, event)) # type: ignore
            
            else:
                future = LOOP.create_future()
                LOOP.call_later(0.1, self._tick, future)
                await future
            
            if ticks % 100 == 0:
                ticks = 0
                event_bytes = pickle.dumps(PluginStatusUpdateEvent(self.name, {plugin.metadata.uuid: plugin.state for plugin in PLUGINS.values()}))
                self.pipe_c.send_bytes(event_bytes)

    async def startup(self) -> None:
        from chara.core.bot import Bot
        from chara.core.param import BOTS, PLUGINS, CONTEXT_GLOBAL_CONFIG, CONTEXT_LOOP, CONTEXT_PLUGIN_GROUP_CONFIG
        from chara.core.plugin._load import load_plugins
        
        LOOP = asyncio.get_event_loop()
        CONTEXT_GLOBAL_CONFIG.set(self.global_config)
        CONTEXT_LOOP.set(LOOP)
        CONTEXT_PLUGIN_GROUP_CONFIG.set(self.group_config)
        load_plugins(self.group_config.directory, self.name)
        global_data_path = self.config.data.directory
        for config in self.config.bots:
            bot = Bot(config)
            bot.data_path = global_data_path / str(config.uin)
            bot.global_data_path = global_data_path
            bot.data_path.mkdir(exist_ok=True)
            BOTS[config.uin] = bot
        
        for plugin in PLUGINS.values():
            LOOP.create_task(plugin._handle_task_on_load()) # type: ignore

    async def shutdown(self) -> None:
        from chara.core.param import PLUGINS
        
        LOOP = asyncio.get_event_loop()
        for plugin in PLUGINS.values():
            LOOP.create_task(plugin._handle_task_on_shutdown()) # type: ignore

    def new(self) -> 'PluginGroupProcess':
        return PluginGroupProcess(self.config, self.group_config, self.pipe_c, self.pipe_p)

