import asyncio
import pickle

from dataclasses import dataclass
from multiprocessing import current_process
from typing import Any, Optional, Union, TYPE_CHECKING

from psutil import Process as ProcessUtil

from chara.core.bot.event import BotEvent
from chara.core.workers.plugin import PluginGroupProcess
from chara.core.workers.worker import WorkerProcess
from chara.core.hazard import CONTEXT_LOOP, IN_SUB_PROCESS
from chara.onebot.events import Event

if TYPE_CHECKING:
    from chara.core.core import Core


CODE_RESTART: int = 100

@dataclass(eq=False, repr=False, slots=True)
class WorkerStatus:
    name: str
    alive: bool
    pid: Optional[int]
    cpu: Optional[float]
    mem: Optional[float]

    def json(self) -> dict[str, Any]:
        return {'name': self.name, 'alive': self.alive, 'pid': self.pid, 'cpu': self.cpu, 'mem': self.mem}


class Worker:
    
    __slots__ = ('process', 'psutil')
    
    process: WorkerProcess
    psutil: ProcessUtil
    
    def __init__(self, process: WorkerProcess) -> None:
        self.process = process

    @property
    def pid(self) -> Optional[int]:
        return self.process.pid

    @property
    def is_alive(self) -> bool:
        if IN_SUB_PROCESS:
            return True
        return self.process.is_alive()
    
    def _start(self) -> None:
        try:
            self.process.start()
        except:
            process = self.process.new()
            del self.process
            self.process = process
            self.process.start()
        self.psutil = ProcessUtil(self.process.pid)
        self.process.join()
    
    async def start(self) -> None:
        '''
        ## 启动Worker进程
        !!! 请勿在子进程中启动 !!!
        '''
        if self.is_alive:
            return
        assert not IN_SUB_PROCESS
        await asyncio.to_thread(self._start)
        if self.process.exitcode == CODE_RESTART:
            LOOP = CONTEXT_LOOP.get()
            LOOP.create_task(self.start())
    
    async def close(self) -> None:
        '''
        ## 关闭Worker进程
        '''
        self.process.should_exit = True
    
    async def restart(self) -> None:
        '''
        ## 重启Worker进程
        '''
        if IN_SUB_PROCESS:
            self.process.set_exitcode(CODE_RESTART)
            await self.close()
        else:
            await self.close()
            LOOP = CONTEXT_LOOP.get()
            LOOP.create_task(self.start())

    @property
    def status(self) -> WorkerStatus:
        if self.is_alive:
            pid = self.psutil.pid
            cpu = self.psutil.cpu_percent()
            mem = round(self.psutil.memory_info().vms / 1024 /1024, 2)
        else:
            pid = cpu = mem = None
        return WorkerStatus(self.process.name, self.is_alive, pid, cpu, mem)


class WorkerManager:
    
    __slots__ = ('core', 'current_process', 'psutil', 'workers')
    
    workers: dict[str, Worker]
    
    def __init__(self, core: 'Core') -> None:
        self.core = core
        self.current_process = current_process()
        self.psutil = ProcessUtil(self.current_process.pid)
        self.workers = dict()
        
        for group in self.core.config.plugins:
            self.add(PluginGroupProcess(group, self.core.config, group.group_name))
    
    @property
    def pid(self) -> Optional[int]:
        return self.current_process.pid
    
    @property
    def alive_workers(self) -> list[Worker]:
        return [worker for worker in self.workers.values() if worker.is_alive]
    
    @property
    def current_process_status(self) -> WorkerStatus:
        pid = self.psutil.pid
        cpu = self.psutil.cpu_percent()
        mem = round(self.psutil.memory_info().vms / 1024 /1024, 2)
        return WorkerStatus(self.current_process.name, True, pid, cpu, mem)
    
    @property
    def all_process_status(self) -> dict[str, Any]:
        return {
            'main': self.current_process_status.json(),
            'workers': [worker.status.json() for worker in self.workers.values()],
        }
    
    def add(self, process: WorkerProcess) -> None:
        name = process.name
        assert name not in self.workers, f'{name} 名称已存在.'
        self.workers[name] = Worker(process)

    async def start_all(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        for worker in self.workers.values():
            LOOP.create_task(worker.start())

    async def close_all(self) -> None:
        LOOP = CONTEXT_LOOP.get()
        for worker in self.workers.values():
            LOOP.create_task(worker.close())

    async def dispatch(self, event: Union[BotEvent, Event]) -> None:
        event_bytes = pickle.dumps(event)
        for worker in self.workers.values():
            worker.process.pipe_send.send_bytes(event_bytes)
