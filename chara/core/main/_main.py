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
from chara.core.plugin._load import load_plugins
from chara.core.param import WINDOWS_PLATFORM
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

    def start(self) -> None:
        self.process.start()
        self.util = ProcessUtil(self.process.pid)

    @property
    def status(self) -> dict[str, Any]:
        pid = self.util.pid
        cpu = self.util.cpu_percent()
        mem = round(self.util.memory_info().vms / 1024 /1024, 2)
        name = self.process.name
        return {'pid': pid, 'cpu': cpu, 'mem': mem, 'name': name}

    def close(self) -> None:
        if WINDOWS_PLATFORM:
            self.util.send_signal(signal.CTRL_C_EVENT)
        else:
            self.util.send_signal(signal.SIGINT)
        self.process.join()

    def restart(self) -> None:
        _RESTARTING_PROCESS.append(self.process.name)
        self.close()
        process = self.process.new()
        del self.process
        self.process = process
        self.start()
        _RESTARTING_PROCESS.remove(self.process.name)


class MainProcess:
    
    __slots__ = ('app', 'child_processes', 'config', 'process', 'process_util', 'running', 'server', 'dispatcher')
    
    app: FastAPI
    child_processes: dict[str, _ChildProcess]
    config: GlobalConfig
    running: bool
    server: uvicorn.Server
    dispatcher: Dispatcher
    
    def __init__(self, config: GlobalConfig) -> None:
        if config.module.fastapi.enable_docs:
            self.app = FastAPI()
        else:
            self.app = FastAPI(docs_url=None, redoc_url=None)
        self.dispatcher = Dispatcher(config)
        self.app.include_router(self.dispatcher.router)
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
        self.child_processes = dict()
        self.config = config
        self.running = False
        self.process = current_process()
        self.process_util = ProcessUtil(self.process.pid)

    async def _on_startup(self) -> None:
        from chara.core.param import CONTEXT_LOOP
        
        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        self.running = True
        for process in self.child_processes.values():
            if not process.is_alive:
                process.start()

        self.dispatcher.update_pipes([cp.process for cp in self.child_processes.values()])
        LOOP.create_task(self.dispatcher.event_loop())

    async def _on_shutdown(self) -> None:
        self.running = False
        for process in self.child_processes.values():
            if process.is_alive:
                process.close()

    def add_process(self, process: WorkerProcess) -> None:
        name = process.name
        if name in self.child_processes:
            logger.warning(f'{name} 名称已存在.')
            return
        self.child_processes[name] = _ChildProcess(process)

    def restart_process(self, name: str) -> None:
        if not self.running:
            logger.warning('仅在主进程运行时可用!')
            return
        if name not in self.child_processes:
            logger.warning(f'{name} 进程不存在.')
            return
        self.child_processes[name].restart()

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
            self.add_process(PluginGroupProcess(self.config, group, pipe_c, pipe_p))

        asyncio.run(self._main())
        logger.success(f'主进程关闭 [PID: {self.process.pid}].')

    async def _main(self):
        config = self.server.config
        if not config.loaded:
            config.load()
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()
        await self.server.main_loop()
        await self.server.shutdown()
        
