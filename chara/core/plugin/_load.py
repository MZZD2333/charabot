import importlib
import inspect

from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterable, Generator, cast

import yaml

from chara.core.plugin.plugin import MetaData, Plugin, PluginState, Trigger
from chara.log import style, logger
from chara.typing import PathLike
from chara.utils.path import is_in_env, add_to_env


_CURRENT_PLUGIN: ContextVar[Plugin] = ContextVar('CURRENT_PLUGIN')
_ON_LOADING: ContextVar[bool] = ContextVar('ON_LOADING', default=False)

def current_plugin() -> Plugin:
    '''
    ## 获取当前插件(仅插件导入时可调用)
    '''
    if _ON_LOADING.get():
        return _CURRENT_PLUGIN.get()
    raise Exception('仅插件导入时可用.')


def load_plugins(directory: PathLike, group_name: str, in_worker_process: bool = True) -> None:
    from chara.core.param import CONTEXT_GLOBAL_CONFIG, PLUGINS, PLUGIN_GROUPS
    
    global_config = CONTEXT_GLOBAL_CONFIG.get()
    directory = Path(directory)

    for path in detect_plugin_path(directory):
        try:
            metadata = load_plugin_metadata(path)
            plugin = Plugin(group_name, metadata)
            log_content = str(plugin)
            plugin.root_path = path
            plugin.data_path = global_config.data.directory / 'plugins' / path.stem
            if metadata.uuid in PLUGINS:
                if in_worker_process:
                    continue
                ep = PLUGINS[metadata.uuid]
                logger.warning(log_content + '与' + str(ep) + '具有相同的uuid. 跳过导入.')
                continue
            PLUGINS[metadata.uuid] = plugin
        except:
            logger.exception(f'错误的插件格式, 跳过导入[{path}].')
            continue
        
        if not in_worker_process:
            plugin.data_path.mkdir(parents=True, exist_ok=True)
            if group_name not in PLUGIN_GROUPS:
                PLUGIN_GROUPS[group_name] = dict()
            PLUGIN_GROUPS[group_name][metadata.uuid] = plugin
            logger.info(log_content + '已添加至' + style.c(f'GROUP[{group_name}]') + '.')
            continue

        _ON_LOADING.set(True)
        _CURRENT_PLUGIN.set(plugin)
        try:
            if not is_in_env(directory):
                add_to_env(directory)
            module = importlib.import_module(f'{path.parent.stem}.{path.stem}')
            if trigger_instances := inspect.getmembers(module, lambda x: type(x) is Trigger):
                trigger_instances = cast(Iterable[tuple[str, Trigger]], trigger_instances)
                for instance_name, trigger in trigger_instances:
                    if trigger.name is None:
                        trigger.name = instance_name
                plugin.add_trigger([t[1] for t in trigger_instances])
            plugin.state = PluginState.WORKING
            logger.success(log_content + style.g('加载成功!'))
        
        except:
            plugin.state = PluginState.NOT_WORKING
            logger.exception(log_content + style.r('加载失败!'))

        _ON_LOADING.set(False)


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

