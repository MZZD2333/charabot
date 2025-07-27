from typing import Any, TYPE_CHECKING

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from chara.config import GlobalConfig
from chara.core.bot.event import BotConnectedEvent, BotDisConnectedEvent, get_event
from chara.core.color import colorize
from chara.core.hazard import BOTS, CONTEXT_LOOP
from chara.log import logger
from chara.onebot.events import MetaEvent

if TYPE_CHECKING:
    from chara.core.core import Core


class WebSocketServer:

    __slots__ = ('core', 'config', 'dispatcher', 'router', '_log_wrap')
    
    core: 'Core'
    config: GlobalConfig
    router: APIRouter
    
    def __init__(self, core: 'Core') -> None:
        self.core = core
        self.config = self.core.config
        self.router = APIRouter()
        self.router.websocket_route(self.config.server.websocket.path)(self._handle)
        self.core.app.include_router(self.router)

    async def _handle(self, websocket: WebSocket) -> None:
        await websocket.accept()
        
        data: dict[str, Any] = await websocket.receive_json()
        if event := get_event(data):
            if bot := BOTS.get(event.self_id, None):
                logger.success(f'{colorize.bot(bot)}已连接.')
            else:
                logger.warning(f'与配置文件不相符的账号{colorize.uid(event.self_id)}, 请检测配置文件.')
                return
        else:
            logger.warning(f'未知的客户端信息.\n{data}')
            return
        
        bot.connected = True

        LOOP = CONTEXT_LOOP.get()
        if not bot.data.updated:
            LOOP.create_task(bot.data.update())

        await self.core.wm.dispatch(BotConnectedEvent(bot.uin))
        try:
            while True:
                data = await websocket.receive_json()
                if event := get_event(data):
                    if isinstance(event, MetaEvent):
                        logger.debug(colorize.event(event))
                    else:
                        logger.info(colorize.event(event))
                    
                    await self.core.wm.dispatch(event)
                    
                    if event.time - bot.data.last_update_time > 3600:
                        LOOP.create_task(bot.data.update())
                    
        except WebSocketDisconnect:
            logger.warning(f'{colorize.bot(bot)}断开连接.')

        await self.core.wm.dispatch(BotDisConnectedEvent(bot.uin))        
        bot.connected = False


