import asyncio

from contextlib import asynccontextmanager
from multiprocessing import current_process
from multiprocessing.connection import Pipe
from typing import Any

import uvicorn

from fastapi import FastAPI
from psutil import Process as ProcessUtil

from chara.config import GlobalConfig
from chara.log import logger, set_logger_config
from chara.core._load_plugin import load_plugins
from chara.core.child import ChildProcess
from chara.core.dispatch import Dispatcher
from chara.core.worker import WorkerProcess


class _ChildProcess:
    
    __slots__ = ('process', 'util')

    cpu_core: int
    process: ChildProcess
    util: ProcessUtil
    
    def __init__(self, process: ChildProcess) -> None:
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
        try:
            self.process.kill()
        except:
            self.process.kill()

    def restart(self) -> None:
        self.close()
        process = self.process.new()
        del self.process
        self.process = process
        self.start()


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
        self.child_processes = dict()
        self.config = config
        self.running = False
        self.process = current_process()
        self.process_util = ProcessUtil(self.process.pid)
        self._set_worker() 
        self._set_lifespan()

    def _set_worker(self):
        for group in self.config.plugins:
            pipe_c, pipe_p = Pipe()
            worker_process = WorkerProcess(self.config, group, pipe_c, pipe_p)
            self.add_process(group.group_name, worker_process)
            

    def _set_lifespan(self) -> None:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self._on_startup()
            yield
            await self._on_shutdown()
        self.app.router.lifespan_context = lifespan

    async def _on_startup(self) -> None:
        from chara.core.param import CONTEXT_LOOP
        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)
        self.running = True
        logger.success(f'主进程启动 [PID: {self.process.pid}].')
        for process in self.child_processes.values():
            process.start()

        self.dispatcher.update_pipes([cp.process for cp in self.child_processes.values()])
        LOOP.create_task(self.dispatcher.event_loop())

    async def _on_shutdown(self) -> None:
        self.running = False
        for process in self.child_processes.values():
            process.close()
        logger.success(f'主进程关闭 [PID: {self.process.pid}].')

    def add_process(self, name: str, process: ChildProcess) -> None:
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

    def run(self):
        try:
            set_logger_config(self.config.log)
            self.config.data.directory.mkdir(exist_ok=True)
            print(self.config.server.webui.index)
            for group in self.config.plugins:
                load_plugins(group.directory, group.group_name, False)
            self.server.run()
        except KeyboardInterrupt:
            pass


