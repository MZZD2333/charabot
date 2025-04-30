import asyncio

from typing import Any

from chara.config import GlobalConfig
from chara.core.workers.worker import WorkerProcess
from chara.core.plugin import Plugin


class GenerateResourceProcess(WorkerProcess):
    _task: dict[str, list[Any]]
    
    def __init__(self, global_config: GlobalConfig, name: str) -> None:
        super().__init__(global_config, name)
        self._task = dict()
    
    async def check(self):
        plugins = await self._check_plugin_docs()
        self._task['plugin_docs'] = plugins
        
        return all(self._task.values())

    async def _check_plugin_docs(self):
        from chara.core.param import PLUGINS
        
        plugins: list[Any] = list()
        for plugin in PLUGINS.values():
            directory = plugin.data_path / 'docs'
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f'{plugin.metadata.version}.png'
            if path.exists():
                continue
            plugins.append(plugin)

        return plugins

    async def _generate_plugin_docs(self):
        from chara.utils.browser import launch
        
        browser = await launch()
        
        plugins: list[Plugin] = self._task['plugin_docs']
        for plugin in plugins:
            plugin
        
        self._task['plugin_docs'].clear()

    async def main(self) -> None:
        from chara.core.param import CONTEXT_LOOP
        
        LOOP = CONTEXT_LOOP.get()
        LOOP.create_task(self._generate_plugin_docs())
        while not all(self._task.values()):
            await asyncio.sleep(1)

