import asyncio

from chara.config import GlobalConfig
from chara.core.workers.worker import WorkerProcess


class GenerateResourceProcess(WorkerProcess):
    is_latest: dict[str, bool]
    
    def __init__(self, global_config: GlobalConfig, name: str) -> None:
        super().__init__(global_config, name)
        self.is_latest = dict()
    
    async def check(self):
        plugin = await self._check_plugin_usage()
        self.is_latest['plugin_usage'] = plugin
        
        return all(self.is_latest.values())

    async def _check_plugin_usage(self):
        #TODO: 检查插件用法文件
                
        return False

    async def _generate_plugin(self):
        self.is_latest['plugin_usage'] = True

    async def main(self) -> None:
        from chara.core.param import CONTEXT_LOOP
        
        LOOP = CONTEXT_LOOP.get()
        LOOP.create_task(self._generate_plugin())
        while not all(self.is_latest.values()):
            await asyncio.sleep(1)

