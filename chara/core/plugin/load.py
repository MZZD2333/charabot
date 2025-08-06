import importlib
import inspect

from pathlib import Path
from typing import Any, Iterable, Generator, cast

import yaml

from chara.config import PluginGroupConfig
from chara.core.color import colorize
from chara.core.hazard import CONTEXT_CURRENT_PLUGIN, CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG, CONTEXT_GLOBAL_CONFIG, PLUGINS, PLUGIN_GROUPS
from chara.core.plugin.plugin import MetaData, Plugin, PluginState
from chara.core.plugin.trigger import Trigger
from chara.log import logger
from chara.typing import PathLike
from chara.utils.path import is_in_env, add_to_env


def load_plugins() -> None:
    global_config = CONTEXT_GLOBAL_CONFIG.get()
    
    for group in global_config.plugins:
        load_plugin_group(group)


def load_plugin_group(config: PluginGroupConfig) -> None:
    from chara.core.hazard import IN_SUB_PROCESS
    
    global_config = CONTEXT_GLOBAL_CONFIG.get()

    group_name = config.group_name
    if group_name not in PLUGIN_GROUPS:
        PLUGIN_GROUPS[group_name] = dict()
    
    for path in detect_plugin_path(config.directory):
        try:
            metadata = load_plugin_metadata(path)
            plugin = Plugin(metadata)
            plugin.group = group_name
            plugin.root_path = path
            plugin.data_path = global_config.data.directory / 'plugins' / path.stem
            if metadata.uuid in PLUGINS:
                if not IN_SUB_PROCESS:
                    logger.warning(colorize.plugin_full(plugin) + '与' + colorize.plugin_full(PLUGINS[metadata.uuid]) + '具有相同的uuid. 跳过导入.')
                continue
            plugin.index = len(PLUGINS) + 1
            PLUGINS[metadata.uuid] = plugin
            PLUGIN_GROUPS[group_name][metadata.uuid] = plugin
        except:
            if not IN_SUB_PROCESS:
                logger.exception(f'错误的插件信息格式, 跳过导入[{path}].')
            continue
    
    # 仅在对应子进程导入
    if not IN_SUB_PROCESS:
        return
    
    group_config = CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG.get()
    if group_config.directory == config.directory:
        folder = config.directory.parent.absolute()
        if not is_in_env(folder):
            add_to_env(folder)
        
        for plugin in PLUGINS.values():
            import_plugin(plugin)
            

def import_plugin(plugin: Plugin) -> None:
    TOKEN = CONTEXT_CURRENT_PLUGIN.set(plugin)
    
    try:
        module = importlib.import_module(f'{plugin.root_path.parent.stem}.{plugin.root_path.stem}')
        
        if trigger_instances := inspect.getmembers(module, lambda x: isinstance(x, Trigger)):
            trigger_instances = cast(Iterable[tuple[str, Trigger]], trigger_instances)
            for instance_name, trigger in trigger_instances:
                if trigger.name is None:
                    trigger.name = instance_name
            plugin.add_trigger([t[1] for t in trigger_instances])
        
        plugin.state = PluginState.WORKING
        logger.success(colorize.plugin_full(plugin) + '导入成功!')
    
    except:
        plugin.state = PluginState.NOT_WORKING
        logger.exception(colorize.plugin_full(plugin) + '导入失败!')
    
    CONTEXT_CURRENT_PLUGIN.reset(TOKEN)


def load_plugin_metadata(path: PathLike) -> MetaData:
    path = Path(path)
    with open(path / 'plugin.yaml', 'rb') as f:
        data = yaml.safe_load(f)
    return MetaData(**data)


def detect_plugin_path(directory: PathLike) -> Generator[Path, Any, None]:
    directory = Path(directory)
    for path in directory.iterdir():
        if path.stem.startswith(('_', '.')):
            continue
        if not path.is_dir():
            continue
        if (path / '__init__.py').exists() and (path / 'plugin.yaml').exists():
            yield path

