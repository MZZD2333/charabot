import json
import re

from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Any, Generator, Optional, Union, overload

from PIL.Image import Image


class MessageSegment:
    '''## 消息段'''
    
    __slots__ = ('type', 'data')
    
    data: dict[str, Any]

    def __init__(self, type: str, data: dict[str, Any]) -> None:
        self.type = type
        if self.type == 'json':
            if raw_data := data.get('data', None):
                self.data = json.loads(raw_data)
            else:
                self.data = {k: self._escape(v) for k, v in data.items()}
        else:
            self.data = {k: self._escape(v) for k, v in data.items()}
    
    def __str__(self) -> str:
        return str(self.cqcode)

    def __repr__(self) -> str:
        return str(self.dict)

    def __add__(self, other: Union[str, 'MessageSegment', 'Message']) -> 'Message':
        message = Message(self)
        return message + other

    def __radd__(self, other: Union[str, 'MessageSegment', 'Message']) -> 'Message':
        message = Message(other)
        return message + self

    @staticmethod
    def _escape(v: Any) -> Any:
        if isinstance(v, str):
            v = v.replace('&', '&amp;').replace(',', '&#44;').replace('[', '&#91;').replace(']', '&#93;')
        return v

    @property
    def cqcode(self) -> str:
        data = ','.join([f'{k}={v}' for k, v in self.data.items()])
        data = ',' + data if data else ''
        return f'[CQ:{self.type}{data}]'

    @property
    def dict(self) -> dict[str, Any]:
        return dict(type=self.type, data=self.data)

    @staticmethod
    def text(text: str) -> 'MessageSegment':
        return MessageSegment('text', {'text': text})

    @staticmethod
    def at(qq: str, name: Optional[str] = None) -> 'MessageSegment':
        if name:
            return MessageSegment('at', {'qq': qq, 'name': name})
        return MessageSegment('at', {'qq': qq})

    @staticmethod
    def face(id: str) -> 'MessageSegment':
        return MessageSegment('face', {'id': id})

    @staticmethod
    def image(file: Union[str, Path, bytes, Image]) -> 'MessageSegment':
        if isinstance(file, bytes):
            file = 'base64://'+b64encode(file).decode()
        elif isinstance(file, Path):
            file = file.resolve().as_uri()
        elif isinstance(file, Image):
            io = BytesIO()
            file.save(io, format='PNG')
            file = 'base64://'+b64encode(io.getvalue()).decode()
        return MessageSegment('image', {'file': file})

    @staticmethod
    def music(type: str, id: str) -> 'MessageSegment':
        return MessageSegment('music', {'type': type, 'id': id})

    @staticmethod
    def music_custom(url: str, audio: str, title: str, content: Optional[str] = None, image: Optional[str] = None) -> 'MessageSegment':
        return MessageSegment('music', {'type': 'custom', 'url': url, 'audio': audio, 'title': title, 'content': content, 'image': image})

    @staticmethod
    def record(file: Union[str, Path, bytes, BytesIO], magic: bool = False, cache: bool = False, proxy: bool = False, timeout: Optional[int] = None, url: Optional[str] = None) -> 'MessageSegment':
        if isinstance(file, BytesIO):
            file = file.getvalue()
        if isinstance(file, bytes):
            file = 'base64://'+b64encode(file).decode()
        elif isinstance(file, Path):
            file = file.resolve().as_uri()
        if url:
            return MessageSegment('record', {'file': file, 'magic': str(magic).lower(), 'url': url})
        return MessageSegment('record', {'file': file, 'magic': str(magic).lower(), 'cache': cache, 'proxy': proxy, 'timeout': timeout})
    
    @staticmethod
    def reply(id: str) -> 'MessageSegment':
        return MessageSegment('reply', {'id': id})

    @staticmethod
    def share(url: str, title: str, content: Optional[str] = None, image: Optional[str] = None) -> 'MessageSegment':
        return MessageSegment('share', {'url': url, 'title': title, 'content': content, 'image': image})

    @staticmethod
    def video(file: Union[str, Path, bytes, BytesIO], cover: Optional[Union[str, Path, bytes]] = None, c: int = 1) -> 'MessageSegment':
        if isinstance(file, BytesIO):
            file = file.getvalue()
        if isinstance(file, bytes):
            file = 'base64://'+b64encode(file).decode()
        elif isinstance(file, Path):
            file = file.resolve().as_uri()
        if cover:
            if isinstance(cover, BytesIO):
                cover = cover.getvalue()
            if isinstance(cover, bytes):
                cover = 'base64://'+b64encode(cover).decode()
            elif isinstance(cover, Path):
                cover = cover.resolve().as_uri()
            return MessageSegment('video', {'file': file, 'cover': cover, 'c': c})
        return MessageSegment('video', {'file': file, 'c': c})

    @staticmethod
    def poke(qq: int) -> 'MessageSegment':
        return MessageSegment('poke', {'qq': qq})

    @staticmethod
    def cardimage(file: Union[str, Path, bytes, Image], minwidth: int = 400, minheight: int = 400, maxwidth: int = 500, maxheight: int = 1000, source: str = '', icon: str = '') -> 'MessageSegment':
        if isinstance(file, bytes):
            file = 'base64://'+b64encode(file).decode()
        elif isinstance(file, Path):
            file = file.resolve().as_uri()
        elif isinstance(file, Image):
            io = BytesIO()
            file.save(io, format='PNG')
            file = 'base64://'+b64encode(io.getvalue()).decode()
        return MessageSegment('cardimage', {'file': file, 'minwidth': minwidth, 'minheight': minheight, 'maxwidth': maxwidth, 'maxheight': maxheight, 'source': source, 'icon': icon})

    @staticmethod
    def tts(text: str) -> 'MessageSegment':
        return MessageSegment('tts', {'text': text})

    @staticmethod
    def forward(id: str) -> 'MessageSegment':
        return MessageSegment('forward', {'id': id})

    @staticmethod
    def node(id: Optional[str] = None, name: str = 'bot', uin: int = 100000, content: Union[str, 'MessageSegment', 'Message'] = '') -> 'MessageSegment':
        if id is not None:
            return MessageSegment('node', {'id': id})
        else:
            return MessageSegment('node', {'name': name, 'uin': uin, 'content': content})

    @staticmethod
    def json(data: str) -> 'MessageSegment':
        return MessageSegment('json', {'data': data})

    @staticmethod
    def xml(data: str) -> 'MessageSegment':
        return MessageSegment('xml', {'data': data})


class Message:
    '''## 消息'''
    __slots__ = ('segments')

    def __init__(self, message: Optional[Union[MessageSegment, 'Message', list[dict[str, Any]], dict[str, Any], str]] = None):
        self.segments: list[MessageSegment] = list()
        if message is None:
            pass
        elif isinstance(message, Message):
            self.segments.extend(message.segments)
        elif isinstance(message, MessageSegment):
            self.segments.append(message)
        elif isinstance(message, list):
            self.segments.extend([MessageSegment(**seg) for seg in message])
        elif isinstance(message, dict):
            self.segments.append(MessageSegment(**message))
        else:
            self.segments.extend(self._construct(str(message)))

    @staticmethod
    def _construct(message: str):
        def _iter_message(message: str):
            seq = 0
            for matched in re.finditer(r'\[CQ:(?P<type>\w+),?(?P<data>(?:\w+=[^,\[\]]+,?)*)\]', message):
                if seq < (k := matched.start()):
                    yield 'text', message[seq : k]
                yield matched.group('type'), matched.group('data') or ''
                seq = matched.end()
            if seq+1 < len(message):
                yield 'text', message[seq:]
        
        for type_, data in _iter_message(message):
            if type_ == 'text':
                cqtext = MessageSegment(type_, {'text': data})
                yield cqtext
            else:
                data = {k: v for k, v in [d.split('=', 1) for d in data.split(',') if d]}
                yield MessageSegment(type_, data)

    def __iter__(self) -> Generator[MessageSegment, Any, None]:
        for segment in self.segments:
            yield segment
    
    @overload
    def __getitem__(self, v: int) -> MessageSegment:...

    @overload
    def __getitem__(self, v: slice) -> list[MessageSegment]:...

    def __getitem__(self, v: Union[int, slice]) -> Union[MessageSegment, list[MessageSegment]]:
        return self.segments[v]

    def __str__(self) -> str:
        return ''.join([str(segment) for segment in self.segments])

    def __repr__(self) -> str:
        return str(self.segments)

    def __add__(self, other: Union[str, MessageSegment, 'Message']):
        if isinstance(other, Message):
            self.segments.extend(other.segments)
        elif isinstance(other, MessageSegment):
            self.segments.append(other)
        else:
            self.segments.extend(self._construct(str(other)))
        return self

    def __radd__(self, other: Union[str, MessageSegment, 'Message']):
        if isinstance(other, Message):
            self.segments.extend(other.segments)
        elif isinstance(other, MessageSegment):
            self.segments.append(other)
        else:
            self.segments.extend(self._construct(str(other)))
        return self

    @property
    def array(self) -> list[dict[str, Any]]:
        return [segment.dict for segment in self]

