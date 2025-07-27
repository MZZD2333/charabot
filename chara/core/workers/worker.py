import asyncio
import signal
import sys

from multiprocessing import Process
from multiprocessing.connection import Pipe
from multiprocessing.connection import _ConnectionBase as Connection # type: ignore
from typing import Any, Optional

from chara.config import GlobalConfig
from chara.core.share import shared_should_exit


class WorkerProcess(Process):
    _start_method = 'spawn'
    
    def __init__(self, global_config: GlobalConfig, name: str, pipes: Optional[tuple[Connection, Connection]] = None, use_pipes: bool = True) -> None:
        super().__init__(name=name)
        
        self.global_config = global_config
        self._exitcode = 0
        self.use_pipes = use_pipes
        if self.use_pipes:
            if pipes is None:
                pipes = Pipe()
            self.pipe_recv = pipes[0]
            self.pipe_send = pipes[1]

    @property
    def should_exit(self) -> bool:
        return self._sv_should_exit.value

    @should_exit.setter
    def should_exit(self, value: bool) -> None:
        self._sv_should_exit.write(value)

    async def _main(self) -> None:
        from chara.core.hazard import CONTEXT_LOOP

        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)

        def handle_exit(sig: int, _: Any) -> None:
            return

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_exit)

        await self.startup()
        if self.should_exit:
            return
        await self.main()
        await self.shutdown()
        
    async def main(self) -> None:
        while not self.should_exit:
            await self.tick()
            await asyncio.sleep(0.2)
    
    async def tick(self) -> None:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    def set_exitcode(self, code: int = 0) -> None:
        self._exitcode = code

    def start(self) -> None:
        super().start()
        self._sv_should_exit = shared_should_exit(self.name)

    def run(self) -> None:
        from chara.core import hazard
        from chara.core.color import colorize
        from chara.core.workers.manager import Worker
        from chara.log import C256, logger
        
        hazard.IN_SUB_PROCESS = True
        hazard.CONTEXT_GLOBAL_CONFIG.set(self.global_config)
        hazard.CONTEXT_CURRENT_WORKER.set(Worker(self))

        self._sv_should_exit = shared_should_exit(self.name)
        logger.set_level(self.global_config.log.level)
        logger.success(C256.f_7bbfea('子进程启动') + colorize.pid(str(self.pid)) + '.')
        self.set_exitcode()
        try:
            asyncio.run(self._main())
        except:
            logger.exception('子进程捕获到异常.')
        
        for sv in hazard.SHARED_VALUES.values():
            sv.close()
        
        logger.success(C256.f_7bbfea('子进程关闭') + colorize.pid(str(self.pid)) + C256.f_6f60aa(f'[CODE: {self._exitcode}]') + '.')
        sys.exit(self._exitcode)
    
    def new(self) -> 'WorkerProcess':
        if self.use_pipes:
            return WorkerProcess(self.global_config, self.name, (self.pipe_recv, self.pipe_send))
        return WorkerProcess(self.global_config, self.name, None, False)


__all__ = [
    'WorkerProcess',
]
