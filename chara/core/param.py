import sys

from asyncio import AbstractEventLoop
from contextvars import ContextVar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chara.config import GlobalConfig, PluginGroupConfig
    from chara.core.bot import Bot
    from chara.core.plugin import Plugin

WINDOWS_PLATFORM: bool = sys.platform.startswith('win')

LINUX_PLATFORM: bool = sys.platform.startswith('linux')

MACOS_PLATFORM: bool = sys.platform.startswith('darwin')

BOTS: dict[int, 'Bot'] = dict()
'''## 所有bot实例'''

PLUGINS: dict[str, 'Plugin'] = dict()
'''## 当前分组下的插件'''

PLUGIN_GROUPS: dict[str, dict[str, 'Plugin']] = dict()
'''## 所有分组下的插件(仅含插件信息)'''

CONTEXT_LOOP: ContextVar[AbstractEventLoop] = ContextVar('loop')

CONTEXT_GLOBAL_CONFIG: ContextVar['GlobalConfig'] = ContextVar('global_config')

CONTEXT_PLUGIN_GROUP_CONFIG: ContextVar['PluginGroupConfig'] = ContextVar('plugin_group_config')

__all__ = [
    'WINDOWS_PLATFORM',
    'LINUX_PLATFORM',
    'MACOS_PLATFORM',
    'BOTS',
    'PLUGINS',
    'PLUGIN_GROUPS',
    'CONTEXT_LOOP',
    'CONTEXT_GLOBAL_CONFIG',
    'CONTEXT_PLUGIN_GROUP_CONFIG',
]