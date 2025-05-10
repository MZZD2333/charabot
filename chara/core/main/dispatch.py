import asyncio
import pickle

from itertools import chain
from multiprocessing.connection import _ConnectionBase as Connection # type: ignore
from typing import Any, Type, TYPE_CHECKING

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from chara.config import GlobalConfig
from chara.core.event import CoreEvent, PluginStatusUpdateEvent, BotConnectedEvent, BotDisConnectedEvent
from chara.core.param import BOTS, CONTEXT_LOOP, PLUGINS, PLUGIN_GROUPS
from chara.core.workers import PluginGroupProcess
from chara.lib.tree import Node
from chara.log import style, logger
from chara.onebot.events import Event, GroupMessageEvent, MessageEvent, MetaEvent, NoticeEvent, RequestEvent
from chara.utils.richtext import unescape

if TYPE_CHECKING:
    from chara.core.main._main import MainProcess


class Dispatcher:

    __slots__ = ('main', 'config', 'pipes', 'router')
    
    main: 'MainProcess'
    config: GlobalConfig
    pipes: list[tuple[Connection, Connection]]
    router: APIRouter

    def __init__(self, main: 'MainProcess', config: GlobalConfig) -> None:
        self.main = main
        self.config = config
        self.router = APIRouter()
        self.router.websocket_route(self.config.server.websocket.path)(self._handle_websocket)
        self.main.app.include_router(self.router)

        
    async def _handle_websocket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        
        data: dict[str, Any] = await websocket.receive_json()
        if event := get_event(data):
            if bot := BOTS.get(event.self_id, None):
                logger.success(f'连接至{style.g(bot.name)}' + style.c(f'[{bot.uin}]') + '.')
                log_event(event)
            else:
                logger.warning(f'与配置文件不相符的账号[{event.self_id}], 请检测配置文件.')
                return
            del event
        else:
            logger.warning(f'收到错误的客户端信息.\n{data}')
            return
        del data
        
        await bot.update_bot_data()
        bot.connected = True
        event_bytes = pickle.dumps(BotConnectedEvent(bot.uin))
        for _, pipe_send in self.pipes:
            pipe_send.send_bytes(event_bytes)

        try:
            while True:
                data: dict[str, Any] = await websocket.receive_json()
                if event := get_event(data):
                    log_event(event)
                    if isinstance(event, MetaEvent):
                        continue
                    event_bytes = pickle.dumps(event)
                    for _, pipe_send in self.pipes:
                        pipe_send.send_bytes(event_bytes)
        
        except WebSocketDisconnect:
            logger.warning(f'与{bot.name}[{bot.uin}]断开连接.')

        event_bytes = pickle.dumps(BotDisConnectedEvent(bot.uin))
        for _, pipe_send in self.pipes:
            pipe_send.send_bytes(event_bytes)
        
        bot.connected = False
    
    async def event_loop(self):
        LOOP = CONTEXT_LOOP.get()
        self.update_pipes()
        ticks = 0
        pipes = [pipe_recv for pipe_recv, _ in self.pipes]
        count = len(pipes)
        while True:
            if len(self.pipes) != count:
                pipes = [pipe_recv for pipe_recv, _ in self.pipes]
                count = len(pipes)
            
            if count > 0 and (pipe := pipes[ticks % count]).poll():
                event: CoreEvent = pipe.recv()
                if isinstance(event, PluginStatusUpdateEvent):
                    group = PLUGIN_GROUPS[event.group_name]
                    status = event.status
                    for uuid in status:
                        group[uuid].state = status[uuid]
                        PLUGINS[uuid].state = status[uuid]
            
            await asyncio.sleep(0.1)
            
            if ticks % 30 == 0:
                for bot in BOTS.values():
                    if bot.connected and not bot.is_latest_data_file():
                        LOOP.create_task(bot.update_bot_data())
            
            if ticks == 300:
                ticks = 0
            
            ticks += 1
    
    def update_pipes(self) -> None:
        pipes: list[tuple[Connection, Connection]] = list()
        for worker in self.main.workers.values():
            process = worker.process
            if isinstance(process, PluginGroupProcess) and worker.is_alive:
                pipes.append((process.pipe_p_recv, process.pipe_p_send))
        self.pipes = pipes


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

def _wrap_gid(gid: str):
    return style.g(f'[G:{gid}]')

def _wrap_uid(uid: str):
    return style.c(f'[U:{uid}]')

def _wrap_oid(oid: str):
    return style.lr(f'[O:{oid}]')

def _wrap_tid(tid: str):
    return style.lm(f'[T:{tid}]')

def _meta_event(event: MetaEvent):
    data = event.model_dump()
    log = style.e('MetaEvent')
    if sub_type := data.get('sub_type', None):
        style.y(f'[{event.meta_event_type}.{sub_type}]')
    else:
        style.y(f'[{event.meta_event_type}]')
    logger.debug(log)

def _message_event(event: MessageEvent):
    data = event.model_dump()
    log = style.c('Message')
    if group_id := data.get('group_id', None):
        log += _wrap_gid(group_id)
    if user_id := data.get('user_id', None):
        log += _wrap_uid(user_id)
    log += ' ' + unescape(event.raw_message)
    logger.info(log)

def _notice_event(event: NoticeEvent):
    data = event.model_dump()
    log = style.y('Notice')
    if group_id := data.get('group_id', None):
        log += _wrap_gid(group_id)
    if user_id := data.get('user_id', None):
        log += _wrap_uid(user_id)
    if operator_id := data.get('operator_id', None):
        log += _wrap_oid(operator_id)
    if target_id := data.get('target_id', None):
        log += _wrap_tid(target_id)
    if sub_type := data.get('sub_type', None):
        style.y(f'[{event.notice_type}.{sub_type}]')
    else:
        style.y(f'[{event.notice_type}]')
    logger.info(log)

def _request_event(event: RequestEvent):
    data = event.model_dump()
    log = style.lm('Request')
    if group_id := data.get('group_id', None):
        log += _wrap_gid(group_id)
    if user_id := data.get('user_id', None):
        log += _wrap_uid(user_id)
    if request_type := data.get('request_type', None):
        if sub_type := data.get('sub_type', None):
            _log = style.y(f'[{request_type}.{sub_type}]')
        else:
            _log = style.y(f'[{request_type}]')
        log += _log
    logger.info(log)

def _unknown_event(event: Event):
    data = event.model_dump()
    log = style.r('Unknown')
    if group_id := data.get('group_id', None):
        log += _wrap_gid(group_id)
    if user_id := data.get('user_id', None):
        log += _wrap_uid(user_id)
    if operator_id := data.get('operator_id', None):
        log += _wrap_oid(operator_id)
    if target_id := data.get('target_id', None):
        log += _wrap_oid(target_id)
    if sub_type := data.get('sub_type', None):
        log += style.y(f'[{sub_type}]')
    logger.info(log)

def log_event(event: Event):
    if isinstance(event, MetaEvent):
        _meta_event(event)
    elif isinstance(event, MessageEvent):
        _message_event(event)
    elif isinstance(event, NoticeEvent):
        _notice_event(event)
    elif isinstance(event, RequestEvent):
        _request_event(event)
    else:
        _unknown_event(event)

