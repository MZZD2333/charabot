from sys import exc_info, stderr

from dataclasses import dataclass
from datetime import datetime
from multiprocessing import current_process
from threading import current_thread
from typing import Any, Callable, Optional, TextIO, Union
from types import TracebackType

from chara.log.style import C256, rgb_wrap


CRITICAL = FATAL = 100
EXCEPTION = ERROR = 80
WARN = WARNING = 60
SUCCESS = 40
INFO = 20
TRACE = 10
DEBUG = 0

_LOG_LEVEL = {
    'CRITICAL':     CRITICAL,
    'FATAL':        FATAL,
    'EXCEPTION':    EXCEPTION,
    'ERROR':        ERROR,
    'WARN':         WARN,
    'WARNING':      WARNING,
    'SUCCESS':      SUCCESS,
    'INFO':         INFO,
    'TRACE':        TRACE,
    'DEBUG':        DEBUG,
}

_LOG_LEVEL_STYLE = {
    'CRITICAL':     rgb_wrap(255,   0,   0),
    'FATAL':        rgb_wrap(255,   0,   0),
    'EXCEPTION':    rgb_wrap(231,  51,  24),
    'ERROR':        rgb_wrap(231,  51,  24),
    'WARN':         rgb_wrap(247, 163,   0),
    'WARNING':      rgb_wrap(247, 163,   0),
    'SUCCESS':      rgb_wrap(  0, 204,   0),
    'INFO':         rgb_wrap( 51, 153, 255),
    'TRACE':        rgb_wrap(255, 182, 230),
    'DEBUG':        rgb_wrap(178, 178, 178),
}

def add_level(name: str, value: int, style_wrap: Callable[..., str]) -> None:
    ln = name.upper()
    assert ln not in _LOG_LEVEL, f'level {ln} already exists.'
    _LOG_LEVEL[ln] = value
    _LOG_LEVEL_STYLE[ln] = style_wrap

@dataclass(eq=False, repr=False, slots=True)
class RecordThread:
    id: int
    name: str


@dataclass(eq=False, repr=False, slots=True)
class RecordProcess:
    id: int
    name: str


@dataclass(eq=False, repr=False, slots=True)
class RecordException:
    type: Optional[type[BaseException]]
    value: Optional[BaseException]
    traceback: Optional[TracebackType]


@dataclass(eq=False, repr=False, slots=True)
class Record:
    time: datetime
    level: str
    msg: object
    exception: Optional[RecordException] = None
    extra: Any = None
    
    @property
    def thread(self) -> RecordThread:
        ct = current_thread()
        return RecordThread(ct.ident, ct.name) # type: ignore
    
    @property
    def process(self) -> RecordProcess:
        cp = current_process()
        return RecordProcess(cp.ident, cp.name) # type: ignore


@dataclass(eq=False, repr=False, slots=True)
class Stream:
    io: TextIO
    level: int

    def write(self, record: Record) -> None:
        if _LOG_LEVEL.get(record.level, INFO) < self.level:
            return
        
        log = self.format(record)
        self.io.write(log)
        self.io.flush()
    
    def format(self, record: Record) -> str:
        T = record.time
        level = record.level
        log = \
            C256.f_7fb80e(f'{T.year}-{T.month}-{T.day} ') + \
            C256.f_ef5b9c(f'{T.hour:02d}:{T.minute:02d}:{T.second:02d} ') + \
            C256.f_33a3dc(f'[{record.process.name}]') + \
            _LOG_LEVEL_STYLE.get(level, _LOG_LEVEL_STYLE['INFO'])('▌') + \
            str(record.msg)
        log = self.check_end(log)
        if (re := record.exception) is not None:
            log = self.check_end(log + self.format_exception(re))
        return log
    
    def format_exception(self, record_exception: RecordException) -> str:
        if record_exception.type is None:
            return ''
        et = '    Traceback (most recent call last):\n'
        tb = record_exception.traceback
        while tb:
            frame = tb.tb_frame
            et += f'        File \"{frame.f_code.co_filename}\", line {tb.tb_lineno}, in {frame.f_code.co_name}\n'
            tb = tb.tb_next
        et += f'    {record_exception.type.__name__}: {record_exception.value}.'
        return et
    
    def check_end(self, log: str) -> str:
        if log.endswith('\n'):
            return log
        return log + '\n'


class Logger:
    
    __slots__ = ('_level', '_record_factory', '_streams')
    
    _level: int
    _streams: list[Stream]
    
    def __init__(self, level: int) -> None:
        self._level = level
        self._record_factory = _record_factory
        self._streams = list()
    
    def add_stream(self, stream: Stream) -> None:
        self._streams.append(stream)
    
    def set_level(self, level: Union[int, str]) -> None:
        if isinstance(level, int):
            self._level = level
        else:
            ln = level.upper()
            assert ln in _LOG_LEVEL
            self._level = _LOG_LEVEL[ln]
    
    def set_record_factory(self, factory: Callable[..., Record]) -> None:
        self._record_factory = factory
    
    @property
    def level(self) -> int:
        return self._level
    
    @property
    def streams(self) -> list[Stream]:
        return self._streams
    
    def fork(self, level: Optional[Union[int, str]] = None) -> 'Logger':
        if level is None:
            level = INFO
        elif isinstance(level, str):
            ln = level.upper()
            assert ln in _LOG_LEVEL
            level = _LOG_LEVEL[ln]
        
        new_logger = Logger(level)
        for stream in new_logger.streams:
            new_logger.add_stream(stream)

        return new_logger
    
    def log(self, level: str, msg: object, exc: bool = False, extra: Any = None) -> None:
        lvl = _LOG_LEVEL.get(level, INFO)
        if lvl < self._level:
            return
        
        record = self._record_factory(level, msg, exc, extra)

        for stream in self._streams:
            if lvl < stream.level:
                continue
            stream.write(record)
    
    def fatal(self, msg: object, exc: bool = True, extra: Any = None) -> None:
        self.log('FATAL', msg, exc, extra)

    def critical(self, msg: object, exc: bool = True, extra: Any = None) -> None:
        self.log('CRITICAL', msg, exc, extra)
    
    def error(self, msg: object, exc: bool = True, extra: Any = None) -> None:
        self.log('ERROR', msg, exc, extra)

    def exception(self, msg: object, exc: bool = True, extra: Any = None) -> None:
        self.log('EXCEPTION', msg, exc, extra)
    
    def warn(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('WARN', msg, exc, extra)

    def warning(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('WARNING', msg, exc, extra)

    def success(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('SUCCESS', msg, exc, extra)

    def info(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('INFO', msg, exc, extra)

    def trace(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('TRACE', msg, exc, extra)

    def debug(self, msg: object, exc: bool = False, extra: Any = None) -> None:
        self.log('DEBUG', msg, exc, extra)


def _record_factory(level: str, msg: object, exc: bool, extra: Any = None) -> Record:
    T = datetime.now()
    re = RecordException(*exc_info()) if exc else None
    record = Record(T, level, msg, re, extra)
    return record


logger = Logger(INFO)
logger.add_stream(Stream(stderr, DEBUG))

