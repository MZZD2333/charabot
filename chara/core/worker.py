import asyncio
import pickle

from contextlib import asynccontextmanager
from multiprocessing.connection import Connection, PipeConnection
from typing import Union

from chara.config import GlobalConfig, PluginConfig
from chara.core.child import ChildProcess
from chara.core.event import PluginStatusUpdateEvent, BotEvent, BotConnectedEvent, BotDisConnectedEvent
from chara.core.plugin import Plugin
from chara.onebot.events import Event


class WorkerProcess(ChildProcess):
    
    def __init__(self, config: GlobalConfig, plugin_config: PluginConfig, pipe_c: Union[Connection, PipeConnection], pipe_p: Union[Connection, PipeConnection]) -> None:
        super().__init__(config)
        self.config = config
        self.plugin_config = plugin_config
        self.name = self.plugin_config.group_name
        self.pipe_c = pipe_c
        self.pipe_p = pipe_p
        self.plugins: list[Plugin] = list()
    
    def new(self) -> ChildProcess:
        return WorkerProcess(self.config, self.plugin_config, self.pipe_c, self.pipe_p)

    def main(self):
        from chara.core._load_plugin import load_plugins
        from chara.core.param import PLUGINS
        
        load_plugins(self.plugin_config.directory, self.name)
        self.plugins = list(PLUGINS.values())
        asyncio.run(self._main())
        
        
    async def _main(self):

        async with self._lifespan():
            try:
                await self._loop()
            except EOFError:
                pass
    
    async def _loop(self):
        from chara.core.param import BOTS, CONTEXT_LOOP, PLUGINS

        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        ticks = 0
        while True:
            if self.pipe_c.poll():
                event: Union[BotEvent, Event] = self.pipe_c.recv()
                bot = BOTS[event.self_id]
                if isinstance(event, BotEvent):
                    if isinstance(event, BotConnectedEvent):
                        bot.connected = True
                    elif isinstance(event, BotDisConnectedEvent):
                        bot.connected = False
                    continue

                for plugin in self.plugins:
                    LOOP.create_task(plugin.handle_event(bot, event))
            else:
                future = LOOP.create_future()
                LOOP.call_later(0.05, self._tick, future)
                await future
            
            ticks += 1
            if ticks % 100 == 0:
                ticks = 0
                event_bytes = pickle.dumps(PluginStatusUpdateEvent(self.name, {plugin.metadata.uuid: plugin.state for plugin in PLUGINS.values()}))
                self.pipe_c.send_bytes(event_bytes)
    
    def _tick(self, future: asyncio.Future[None]):
        try:
            future.set_result(None)
        except:
            pass

    @asynccontextmanager
    async def _lifespan(self):
        await self.on_startup()
        yield
        await self.on_shutdown()

    async def on_startup(self) -> None:        
        # import signal
        
        from chara.core import Bot
        from chara.core.param import BOTS

        # def close():
        #     for task in asyncio.all_tasks():
        #         task.cancel()
        
        # LOOP = asyncio.get_running_loop()
        # print(type(LOOP))
        # LOOP.add_signal_handler(signal.SIGTERM, close)

        global_data_path = self.config.data.directory
        for config in self.config.bots:
            bot = Bot(config)
            bot.data_path = global_data_path / str(config.uin)
            bot.global_data_path = global_data_path
            bot.data_path.mkdir(exist_ok=True)
            BOTS[config.uin] = bot


    async def on_shutdown(self) -> None:
        pass


