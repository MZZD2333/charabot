import importlib
import inspect

from pathlib import Path
from typing import Any, Iterable, Generator, cast

import yaml

from chara.config import GlobalConfig, PluginGroupConfig
from chara.core.color import colorize
from chara.core.hazard import CONTEXT_CURRENT_PLUGIN, CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG, CONTEXT_GLOBAL_CONFIG, PLUGINS, PLUGIN_GROUPS, PLUGIN_CUSTOM_CONFIGS
from chara.core.plugin.plugin import PlugiMetaData, Plugin, PluginState
from chara.core.plugin.trigger import Trigger
from chara.log import logger
from chara.typing import PathLike
from chara.utils.path import is_in_env, add_to_env


def load_plugins() -> None:
    from chara.core.hazard import IN_SUB_PROCESS
    
    global_config = CONTEXT_GLOBAL_CONFIG.get()
    
    load_plugin_custom_configs(global_config, IN_SUB_PROCESS)
    for group_config in global_config.plugins:
        load_plugin_group(global_config, group_config, IN_SUB_PROCESS)

    generate_plugin_custom_configs(global_config, IN_SUB_PROCESS)


def load_plugin_custom_configs(global_config: GlobalConfig, in_sub_process: bool) -> None:
    path = global_config.data.directory / 'plugin-configs.yaml'
    if not path.exists():
        return
    
    try:
        with open(path, 'rb') as f:
            configs: list[dict[str, Any]] = yaml.safe_load(f)
    except:
        if not in_sub_process:
            logger.exception('插件自定义配置文件加载失败.')
        return
    
    if not configs:
        return
    
    for pc in configs:
        uuid = pc.get('uuid', None)
        if uuid is None:
            continue
        
        config = pc.get('config', None)
        if config is None:
            continue
        
        if not isinstance(config, dict):
            continue
        
        PLUGIN_CUSTOM_CONFIGS[uuid] = config


def generate_plugin_custom_configs(global_config: GlobalConfig, in_sub_process: bool) -> None:
    if in_sub_process:
        return
    path = global_config.data.directory / 'plugin-configs.yaml'
    if path.exists():
        return
    
    contents = ''
    for uuid, plugin in PLUGINS.items():
        content = f'# {plugin.metadata.name}\n'
        config: dict[str, Any] = {'uuid': uuid, 'config': plugin.config}
        text = yaml.dump(config, indent=2, allow_unicode=True, sort_keys=False)
        lines = text.split('\n')
        content += f'- {lines[0]}\n'
        for line in lines[1:]:
            content += f'  {line}\n'
        contents += content + '\n\n'
    
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(contents)


def load_plugin_group(global_config: GlobalConfig, group_config: PluginGroupConfig, in_sub_process: bool) -> None:
    group_name = group_config.group_name
    if group_name not in PLUGIN_GROUPS:
        PLUGIN_GROUPS[group_name] = dict()
    
    for path in detect_plugin_path(group_config.directory):
        # metadata
        try:
            metadata = load_plugin_metadata(path)
        except:
            if not in_sub_process:
                logger.exception(f'错误的插件信息格式, 跳过导入[{path}].')
            continue
        plugin = Plugin(metadata)
        plugin.group = group_name
        plugin.root_path = path
        plugin.data_path = global_config.data.directory / 'plugins' / metadata.uuid
        if metadata.uuid in PLUGINS:
            if not in_sub_process:
                logger.warning(colorize.plugin_full(plugin) + '与' + colorize.plugin_full(PLUGINS[metadata.uuid]) + '具有相同的uuid跳过导入.')
            continue
        plugin.index = len(PLUGINS) + 1
        
        # default config
        try:
            load_plugin_config(plugin)
        except:
            if not in_sub_process:
                logger.exception(f'导入插件默认配置格式失败, 跳过导入[{path}].')
            continue
        
        # default config
        try:
            load_plugin_custom_config(plugin)
        except:
            if not in_sub_process:
                logger.warning(f'导入{colorize.plugin_full(plugin)}自定义配置格式失败, 使用默认配置.')
            continue
        
        PLUGINS[metadata.uuid] = plugin
        PLUGIN_GROUPS[group_name][metadata.uuid] = plugin
        
    # 仅在对应子进程导入
    if not in_sub_process:
        return
    
    current_group_config = CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG.get()
    if current_group_config.directory == group_config.directory:
        folder = group_config.directory.parent.absolute()
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


def load_plugin_metadata(path: PathLike) -> PlugiMetaData:
    path = Path(path)
    with open(path / 'plugin.yaml', 'rb') as f:
        data = yaml.safe_load(f)
    return PlugiMetaData(**data)


def load_plugin_config(plugin: Plugin) -> None:
    path = plugin.root_path / 'config.yaml'
    if not path.exists():
        return

    with open(path, 'rb') as f:
        default_config = yaml.safe_load(f)
    plugin.config.update(default_config)


def load_plugin_custom_config(plugin: Plugin) -> None:
    custom_config = PLUGIN_CUSTOM_CONFIGS.get(plugin.metadata.uuid, None)
    if custom_config is None:
        return
    
    plugin.config.update(custom_config)


def detect_plugin_path(directory: PathLike) -> Generator[Path, Any, None]:
    directory = Path(directory)
    for path in directory.iterdir():
        if path.stem.startswith(('_', '.')):
            continue
        if not path.is_dir():
            continue
        if (path / '__init__.py').exists() and (path / 'plugin.yaml').exists():
            yield path

