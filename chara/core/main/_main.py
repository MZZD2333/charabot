import asyncio
import signal

from contextlib import asynccontextmanager
from multiprocessing import current_process
from multiprocessing.connection import Pipe
from typing import Any

import uvicorn

from fastapi import FastAPI
from psutil import Process as ProcessUtil

from chara.config import GlobalConfig
from chara.log import logger, set_logger_config
from chara.core.main.dispatch import Dispatcher
from chara.core.main.webui import WebUI
from chara.core.plugin._load import load_plugins
from chara.core.param import CONTEXT_LOOP, WINDOWS_PLATFORM
from chara.core.workers import PluginGroupProcess, WorkerProcess


_RESTARTING_PROCESS: list[str] = list()

class _ChildProcess:
    
    __slots__ = ('process', 'util')

    process: WorkerProcess
    util: ProcessUtil
    
    def __init__(self, process: WorkerProcess) -> None:
        self.process = process

    @property
    def is_alive(self) -> bool:
        return self.process.is_alive()

    @property
    def status(self) -> dict[str, Any]:
        pid = self.util.pid
        cpu = self.util.cpu_percent()
        mem = round(self.util.memory_info().vms / 1024 /1024, 2)
        name = self.process.name
        return {'pid': pid, 'cpu': cpu, 'mem': mem, 'name': name}

    async def start(self) -> None:
        self.process.start()
        self.util = ProcessUtil(self.process.pid)

    async def close(self) -> None:
        if WINDOWS_PLATFORM:
            self.util.send_signal(signal.CTRL_C_EVENT)
        else:
            self.util.send_signal(signal.SIGINT)
        self.process.join()

    async def restart(self) -> None:
        _RESTARTING_PROCESS.append(self.process.name)
        await self.close()
        process = self.process.new()
        del self.process
        self.process = process
        await self.start()
        _RESTARTING_PROCESS.remove(self.process.name)


class MainProcess:
    
    __slots__ = ('app', 'config', 'dispatcher', 'process', 'process_util', 'running', 'server', 'web_ui', 'workers')
    
    app: FastAPI
    config: GlobalConfig
    dispatcher: Dispatcher
    running: bool
    server: uvicorn.Server
    web_ui: WebUI
    workers: dict[str, _ChildProcess]
    
    def __init__(self, config: GlobalConfig) -> None:
        if config.module.fastapi.enable_docs:
            self.app = FastAPI()
        else:
            self.app = FastAPI(docs_url=None, redoc_url=None)
        self.dispatcher = Dispatcher(self, config)
        self.web_ui = WebUI(self, config)
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
                            'class': 'chara.log.CharaHandler',
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
        self.workers = dict()
        self.config = config
        self.running = False
        self.process = current_process()
        self.process_util = ProcessUtil(self.process.pid)

    async def _on_startup(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        self.running = True
        for process in self.workers.values():
            if not process.is_alive:
                LOOP.create_task(process.start())

        self.dispatcher.update_pipes([cp.process for cp in self.workers.values()])
        LOOP.create_task(self.dispatcher.event_loop())

    async def _on_shutdown(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        print(LOOP)
        self.running = False
        for process in self.workers.values():
            if process.is_alive:
                LOOP.create_task(process.start())

    def add_worker(self, process: WorkerProcess) -> None:
        name = process.name
        if name in self.workers:
            logger.warning(f'{name} 名称已存在.')
            return
        self.workers[name] = _ChildProcess(process)
        self.dispatcher.update_pipes([cp.process for cp in self.workers.values()])

    def run(self) -> None:
        logger.success(f'主进程启动 [PID: {self.process.pid}].')
        def handle_exit(sig: int, _: Any):
            if _RESTARTING_PROCESS:
                return
            self.server.should_exit = True

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_exit)

        set_logger_config(self.config.log)
        self.config.data.directory.mkdir(exist_ok=True)
        for group in self.config.plugins:
            load_plugins(group.directory, group.group_name, False)
        
        for group in self.config.plugins:
            pipe_c, pipe_p = Pipe()
            self.add_worker(PluginGroupProcess(self.config, group, pipe_c, pipe_p))

        asyncio.run(self._main())
        logger.success(f'主进程关闭 [PID: {self.process.pid}].')

    async def _main(self):
        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        config = self.server.config
        if not config.loaded:
            config.load()
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()
        await self.server.main_loop()
        await self.server.shutdown()
        
