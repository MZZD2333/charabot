'''
# Charabot 全局参数

---
## !!! 在明确用途前请勿修改任何数值 !!!
'''
import sys

from asyncio import AbstractEventLoop
from contextvars import ContextVar
from typing import Any, TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chara.config import GlobalConfig, PluginGroupConfig
    from chara.core.bot import Bot
    from chara.core.plugin import Plugin
    from chara.core.share import SharedValue
    from chara.core.workers.manager import Worker


WINDOWS_PLATFORM: bool = sys.platform.startswith('win')

LINUX_PLATFORM: bool = sys.platform.startswith('linux')

MACOS_PLATFORM: bool = sys.platform.startswith('darwin')

IN_SUB_PROCESS: bool = False

SHARED_VALUES: dict[str, 'SharedValue[Any]'] = dict()

CONTEXT_LOOP: ContextVar[AbstractEventLoop] = ContextVar('loop')

CONTEXT_GLOBAL_CONFIG: ContextVar['GlobalConfig'] = ContextVar('global_config')

CONTEXT_CURRENT_PLUGIN: ContextVar['Plugin'] = ContextVar('current_plugin')

CONTEXT_CURRENT_PLUGIN_GROUP_CONFIG: ContextVar['PluginGroupConfig'] = ContextVar('plugin_group_config')

CONTEXT_CURRENT_WORKER: ContextVar['Worker'] = ContextVar('current_worker')

BOTS: dict[int, 'Bot'] = dict()

PLUGINS: dict[str, 'Plugin'] = dict()
'''## 当前分组下的插件'''

PLUGIN_GROUPS: dict[str, dict[str, 'Plugin']] = dict()
'''## 所有分组下的插件(仅含插件信息)'''

