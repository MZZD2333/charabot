from asyncio import AbstractEventLoop

from chara.config import GlobalConfig, PluginGroupConfig
from chara.core.hazard import CONTEXT_CURRENT_PLUGIN, CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG, CONTEXT_CURRENT_WORKER, CONTEXT_GLOBAL_CONFIG, CONTEXT_LOOP
from chara.core.plugin.plugin import Plugin
from chara.core.workers.manager import Worker



def get_current_plugin() -> Plugin:
    '''
    ## 获取当前插件(仅插件导入时可调用)
    '''
    try:
        return CONTEXT_CURRENT_PLUGIN.get()
    except:
        raise Exception('仅插件导入时可用.')

def get_current_plugin_group_config() -> PluginGroupConfig:
    '''
    ## 获取当前插件配置
    '''
    return CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG.get()

def get_current_worker() -> Worker:
    '''
    ## 获取当前Worker
    '''
    return CONTEXT_CURRENT_WORKER.get()

def get_global_config() -> GlobalConfig:
    '''
    ## 获取全局配置
    '''
    return CONTEXT_GLOBAL_CONFIG.get()

def get_running_loop() -> AbstractEventLoop:
    '''
    ## 获取当前事件循环
    '''
    return CONTEXT_LOOP.get()


__all__ = [
    'get_current_plugin',
    'get_current_plugin_group_config',
    'get_current_worker',
    'get_global_config',
    'get_running_loop',
]

