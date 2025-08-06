from typing import Union, TYPE_CHECKING

from chara.log import C256
from chara.onebot.events import Event, MetaEvent, MessageEvent, NoticeEvent, RequestEvent
from chara.utils.richtext import unescape

if TYPE_CHECKING:
    from chara.core.bot import Bot
    from chara.core.plugin.plugin import Plugin
    from chara.core.plugin.handler import Handler
    from chara.core.plugin.trigger import Trigger


class ColorWrap:
    
    def __init__(self) -> None:
        # const - event
        self._const_event_meta      = C256.f_90d7ec('MetaEvent')
        self._const_event_message   = C256.f_33a3dc('Message')
        self._const_event_notice    = C256.f_faa755('Notice')
        self._const_event_request   = C256.f_ffd900('Request')
        self._const_event_unknown   = C256.f_6f60aa('Unknown')
        # const - plugin
        self._const_plugin          = C256.f_7fb80e('Plugin')
        # const - handler
        self._const_handler         = C256.f_33a3dc('Handler')
    
    def pid(self, pid: Union[str, int]) -> str:
        return C256.f_bed742(f'[P:{pid}]')

    def gid(self, gid: Union[str, int]) -> str:
        return C256.f_7fb80e(f'[G:{gid}]')

    def uid(self, uid: Union[str, int]) -> str:
        return C256.f_7bbfea(f'[U:{uid}]')

    def oid(self, oid: Union[str, int]) -> str:
        return C256.f_f8aba6(f'[O:{oid}]')

    def tid(self, tid: Union[str, int]) -> str:
        return C256.f_fcaf17(f'[T:{tid}]')

    def meta_event(self, event: MetaEvent) -> str:
        data = event.model_dump()
        log = self._const_event_meta
        if sub_type := data.get('sub_type', None):
            log += C256.f_003a6c(f'[{event.meta_event_type}.{sub_type}]')
        else:
            log += C256.f_003a6c(f'[{event.meta_event_type}]')
        return log

    def message_event(self, event: MessageEvent) -> str:
        data = event.model_dump()
        log = self._const_event_message
        if group_id := data.get('group_id', None):
            log += self.gid(group_id)
        if user_id := data.get('user_id', None):
            log += self.uid(user_id)
        log += unescape(event.raw_message)
        return log

    def notice_event(self, event: NoticeEvent) -> str:
        data = event.model_dump()
        log = self._const_event_notice
        if group_id := data.get('group_id', None):
            log += self.gid(group_id)
        if user_id := data.get('user_id', None):
            log += self.uid(user_id)
        if operator_id := data.get('operator_id', None):
            log += self.oid(operator_id)
        if target_id := data.get('target_id', None):
            log += self.tid(target_id)
        if sub_type := data.get('sub_type', None):
            log += C256.f_003a6c(f'[{event.notice_type}.{sub_type}]')
        else:
            log += C256.f_003a6c(f'[{event.notice_type}]')
        return log

    def request_event(self, event: RequestEvent) -> str:
        data = event.model_dump()
        log = self._const_event_request
        if group_id := data.get('group_id', None):
            log += self.gid(group_id)
        if user_id := data.get('user_id', None):
            log += self.uid(user_id)
        if request_type := data.get('request_type', None):
            if sub_type := data.get('sub_type', None):
                log += C256.f_003a6c(f'[{request_type}.{sub_type}]')
            else:
                log += C256.f_003a6c(f'[{request_type}]')
        return log

    def unknown_event(self, event: Event) -> str:
        data = event.model_dump()
        log = self._const_event_unknown
        if group_id := data.get('group_id', None):
            log += self.gid(group_id)
        if user_id := data.get('user_id', None):
            log += self.uid(user_id)
        if operator_id := data.get('operator_id', None):
            log += self.oid(operator_id)
        if target_id := data.get('target_id', None):
            log += self.oid(target_id)
        if sub_type := data.get('sub_type', None):
            log += C256.f_003a6c(f'[{sub_type}]')
        return log

    def event(self, event: Event) -> str:
        if isinstance(event, MetaEvent):
            return self.meta_event(event)
        elif isinstance(event, MessageEvent):
            return self.message_event(event)
        elif isinstance(event, NoticeEvent):
           return self.notice_event(event)
        elif isinstance(event, RequestEvent):
            return self.request_event(event)
        else:
            return self.unknown_event(event)

    def bot(self, bot: 'Bot') -> str:
        return C256.f_faa755(bot.name) + C256.f_7bbfea(f'[{bot.uin}]')

    def plugin(self, plugin: 'Plugin') -> str:
        return self._const_plugin + C256.f_f8aba6(f'[{plugin.metadata.name}]')

    def plugin_full(self, plugin: 'Plugin') -> str:
        return self.plugin(plugin) + C256.f_33a3dc(f'[{plugin.metadata.version}]') + C256.f_fcf16e(f'[{plugin.metadata.uuid}]')

    def trigger(self, trigger: 'Trigger') -> str:
        return C256.f_f8aba6(type(trigger).__name__) + C256.f_f8aba6(f'[{trigger.plugin.metadata.name}.{self.trigger_name(trigger)}]')
    
    def trigger_name(self, trigger: 'Trigger') -> str:
        return trigger.name or hex(id(trigger))
    
    def handler(self, handler: 'Handler') -> str:
        trigger = handler.trigger
        return self._const_handler + C256.f_f8aba6(f'[{trigger.plugin.metadata.name}.{self.trigger_name(trigger)}]')
    
    def handler_results(self, results: list[int]) -> str:
        return C256.f_7fb80e(f'[SUCCESS:{results[0]}]') + C256.f_33a3dc(f'[SKIP:{results[1]}]') + C256.f_ed1941(f'[ERROR:{results[2]}]')
    
    
colorize = ColorWrap()

