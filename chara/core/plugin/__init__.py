from chara.core.param import CONTEXT_GLOBAL_CONFIG, CONTEXT_LOOP, CONTEXT_PLUGIN_GROUP_CONFIG
from chara.core.plugin._load import current_plugin
from chara.core.plugin.condition import Condition
from chara.core.plugin.handler import Handler
from chara.core.plugin.plugin import MetaData, Plugin, PluginState
from chara.core.plugin.trigger import Session, Trigger, TriggerCapturedData


def get_global_config():
    return CONTEXT_GLOBAL_CONFIG.get()

def get_plugin_group_loop():
    return CONTEXT_PLUGIN_GROUP_CONFIG.get()

def get_running_loop():
    return CONTEXT_LOOP.get()


__all__ = [
    'current_plugin',
    'get_global_config',
    'get_plugin_group_loop',
    'get_running_loop',
    'Condition',
    'Handler',
    'MetaData',
    'Plugin',
    'PluginState',
    'Session',
    'Trigger',
    'TriggerCapturedData',
]
