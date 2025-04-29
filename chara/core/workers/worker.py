import asyncio
import signal

from multiprocessing import Process
from typing import Any

from chara.config import GlobalConfig


class WorkerProcess(Process):
    _start_method = 'spawn'
    
    should_exit: bool

    def __init__(self, global_config: GlobalConfig, name: str) -> None:
        super().__init__(name=name)
        self.global_config = global_config
        self.should_exit = False

    async def _main(self) -> None:
        from chara.core.param import CONTEXT_LOOP

        LOOP = asyncio.get_event_loop()
        CONTEXT_LOOP.set(LOOP)

        captured_signals: list[int] = list()
        def handle_exit(sig: int, _: Any):
            captured_signals.append(sig)
            self.should_exit = True

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handle_exit)

        await self.startup()
        if self.should_exit:
            return
        await self.main()
        await self.shutdown()
        
        for sig in reversed(captured_signals):
            signal.raise_signal(sig)

    async def main(self) -> None:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    def run(self) -> None:
        from chara.log import logger, set_logger_config

        set_logger_config(self.global_config.log)
        logger.success(f'子进程开启 [PID: {self.pid}].')
        try:
            asyncio.run(self._main())
        except KeyboardInterrupt:
            pass
        except:
            logger.exception('子进程捕获到异常.')
        
        logger.success(f'子进程关闭 [PID: {self.pid}].')
    
    def new(self) -> 'WorkerProcess':
        return WorkerProcess(self.global_config, self.name)


__all__ = [
    'WorkerProcess',
]
