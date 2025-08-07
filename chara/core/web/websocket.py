from typing import Any, TYPE_CHECKING

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from chara.config import GlobalConfig
from chara.core.bot.event import BotConnectedEvent, BotDisConnectedEvent, get_event
from chara.core.color import colorize
from chara.core.hazard import BOTS
from chara.log import logger
from chara.onebot.api.onebot import OneBotAPI
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
                try:
                    info = await bot[OneBotAPI].get_version_info()
                except:
                    logger.exception(f'{colorize.bot(bot)}协议没有实现[/get_version_info]API.')
                    return
                bot.protocol.name = info.get('app_name', 'Unknown')
                logger.success(f'{colorize.bot(bot)}{colorize.bot_protocol(bot.protocol.name)}已连接.')
            
            else:
                logger.warning(f'与配置文件不相符的账号{colorize.uid(event.self_id)}, 请检测配置文件.')
                return
        
        else:
            logger.warning(f'未知的客户端信息.\n{data}')
            return
        
        bot.connected = True
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
                    
        except WebSocketDisconnect:
            logger.warning(f'{colorize.bot(bot)}{colorize.bot_protocol(bot.protocol.name)}断开连接.')

        await self.core.wm.dispatch(BotDisConnectedEvent(bot.uin))        
        bot.connected = False


