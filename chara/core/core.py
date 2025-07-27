import asyncio
import signal
import time

from contextlib import asynccontextmanager
from typing import Any

import uvicorn

from fastapi import FastAPI

from chara.config import GlobalConfig
from chara.core.bot import Bot
from chara.core.color import colorize
from chara.core.hazard import BOTS, CONTEXT_GLOBAL_CONFIG, CONTEXT_LOOP, SHARED_VALUES
from chara.core.plugin.load import load_plugins
from chara.core.web.websocket import WebSocketServer
from chara.core.web.ui import WebUI
from chara.core.workers.manager import WorkerManager
from chara.log import C256, logger


class Core:
    
    __slots__ = ('app', 'config', 'wm', 'ws', 'ui', 'server')
    
    app: FastAPI
    wm: WorkerManager
    ui: WebUI
    ws: WebSocketServer
    
    
    def __init__(self, config: GlobalConfig) -> None:
        self.config = config
        # WorkerManager
        self.wm = WorkerManager(self)
        if config.module.fastapi.enable_docs:
            self.app = FastAPI()
        else:
            self.app = FastAPI(docs_url=None, redoc_url=None)
        
        # WebSocketServer
        self.ws = WebSocketServer(self)
        if self.config.server.webui.enable:
            self.ui = WebUI(self)
        
        # Server
        self.server = uvicorn.Server(
            uvicorn.Config(
                self.app,
                host=config.server.host,
                port=config.server.port,
                log_config={
                    'version': 1,
                    'disable_existing_loggers': False,
                    'handlers': {
                        'default': {
                            'class': 'chara.log.convert.ConvertHandler',
                        },
                    },
                    'loggers': {
                        'uvicorn': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
                        'uvicorn.error': {'level': 'INFO'},
                        'uvicorn.access': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
                    },
                },
                **config.module.uvicorn.model_dump()
            )
        )
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self._on_startup()
            yield
            await self._on_shutdown()
        
        self.app.router.lifespan_context = lifespan

    async def _on_startup(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        LOOP.create_task(self.wm.start_all())
        
        if self.config.server.webui.enable:
            logger.success('Web-UI 已在[' + C256.f_33a3dc(f'http://{self.config.server.host}:{self.config.server.port}{self.ui.config.path}') + ']开启.')
        
    async def _on_shutdown(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        LOOP.create_task(self.wm.close_all())
        
    async def _main(self) -> None:
        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        config = self.server.config
        if not config.loaded:
            config.load()
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()
        await self.server.main_loop()
        await self.server.shutdown()
    
    def run(self) -> None:
        logger.success(C256.f_7bbfea('主进程启动') + f'{colorize.pid(str(self.wm.pid))}.')
        CONTEXT_GLOBAL_CONFIG.set(self.config)
        BOTS.update({bot_config.uin: Bot(bot_config) for bot_config in self.config.bots})

        last_quit_time = 0
        
        def handle_exit(sig: int, _: Any) -> None:
            nonlocal last_quit_time
            
            now = time.time()
            if now - last_quit_time >= 3:
                last_quit_time = now
                logger.warning(C256.f_f15a22('[3s内]再次按下[CTRL+C]后退出.'))
                return
            self.server.should_exit = True

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_exit)
        
        logger.set_level(self.config.log.level)
        self.config.data.directory.mkdir(exist_ok=True)
        load_plugins()
                
        asyncio.run(self._main())
        for sv in SHARED_VALUES.values():
            sv.unlink()

        logger.success(C256.f_7bbfea('主进程关闭') + colorize.pid(str(self.wm.pid)))

