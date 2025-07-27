from dataclasses import dataclass
from itertools import chain
from typing import Any, Type

from chara.lib.tree import Node
from chara.onebot.events import Event, GroupMessageEvent, MessageEvent


@dataclass(repr=False, eq=False, slots=True)
class BotEvent:
    self_id: int


@dataclass(repr=False, eq=False, slots=True)
class BotConnectedEvent(BotEvent):
    pass


@dataclass(repr=False, eq=False, slots=True)
class BotDisConnectedEvent(BotEvent):
    pass

# 解析Onebot事件
_SUB_POST_TYPES = ['message_type', 'meta_event_type', 'notice_type', 'request_type']

def _generate_event_tree() -> Node:
    def get_subclass(cls: Type[Event] | list[Type[Event]]) -> list[Type[Event]]:
        if isinstance(cls, list):
            return list(chain(*[get_subclass(c) for c in cls]))
        elif subcls := cls.__subclasses__():
            return get_subclass(subcls) + [cls]
        return [cls]
    event_subclass = get_subclass(Event)
    
    TREE = Node()

    for event in event_subclass:
        pt = event.model_fields.get('post_type', None)
        rt = None
        st = event.model_fields.get('sub_type')
        for spt in _SUB_POST_TYPES:
            if rt := event.model_fields.get(spt, None):
                break
        pt_v = pt.default if pt and not pt.is_required() else None
        rt_v = rt.default if rt and not rt.is_required() else None
        st_v = st.default if st and not st.is_required() else None
        TREE[pt_v, rt_v, st_v] = Node(event)
    
    return TREE

_EVENT_TREE = _generate_event_tree()

def _get_event_nodes(json_data: dict[str, str]) -> tuple[str, str, str | None] | tuple[None, None, None]:
    sub_type = None
    if 'notice_type' in json_data:
        sub_type = json_data.get('sub_type', None)
    for post_type in _SUB_POST_TYPES:
        if _type := json_data.get(post_type, None):
            return post_type, _type, sub_type
    return None, None, None    

def get_event(json_data: dict[str, Any]) -> Event | None:
    if node := _EVENT_TREE[_get_event_nodes(json_data)]:
        event = node.value(**json_data)
        if isinstance(event, MessageEvent):
            if event.message.array and (cqcode := event.message.segments[0]).type == 'reply':
                event.reply_id = cqcode.data.get('id')
            if isinstance(event, GroupMessageEvent):
                event.at_me = str(event.self_id) in event.at_ids                        
            else:
                event.at_me = True
        return event
    else:
        return None

del _generate_event_tree
