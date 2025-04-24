import sys

from datetime import datetime
from logging import Formatter, Logger, LogRecord, Handler, addLevelName, getLogger, setLoggerClass
from typing import Any, Callable, Optional, TextIO

from chara.config import LogConfig
from chara.log._style import style


CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
SUCCESS = 25
INFO = 20
DEBUG = 10
TRACE = 5

addLevelName(SUCCESS, 'SUCCESS')
addLevelName(TRACE, 'TRACE')

_LEVEL_COLOR: dict[int, Optional[Callable[..., str]]] = {
    FATAL: style.lr,
    ERROR: style.r,
    WARN: style.y,
    SUCCESS: style.g,
    INFO: None,
    DEBUG: style.c,
    TRACE: style.e,
}


class _Formatter(Formatter):
    
    def format(self, record: LogRecord) -> str:
        record.message = record.getMessage()

        time = datetime.now().strftime('\033[32m%H:%M:%S\033[0m')
        process = f'\033[36m[{(record.processName or str(record.process) or __name__)}]\033[0m'
        level = '▌'
        if wrap := _LEVEL_COLOR.get(record.levelno, None):
            level = wrap(level)

        text = self._check_end(''.join([time, process, level, record.message]))
        
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            text = self._check_end(text)
            text += record.exc_text
        if record.stack_info:
            text = self._check_end(text)
            text += record.stack_info
        return self._check_end(text)
    
    @staticmethod
    def _check_end(text: str):
        if not text.endswith('\n'):
            text += '\n'
        return text

class CharaHandler(Handler):

    def __init__(self, stream: Optional[TextIO] = None):
        super().__init__()
        self.stream = stream or sys.stderr
        self.formatter = _Formatter()

    def emit(self, record: LogRecord) -> None:
        try:
            self.stream.write(self.formatter.format(record)) # type: ignore
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


class _Logger(Logger):
        
    def trace(self, msg: Any, *args: Any, **kwargs: Any):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)
    
    def success(self, msg: Any, *args: Any, **kwargs: Any):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

setLoggerClass(_Logger)

_handler = CharaHandler()
logger: _Logger = getLogger('default') # type: ignore
logger.addHandler(_handler)

def set_logger_config(config: LogConfig):
    logger.setLevel(config.level.upper())

