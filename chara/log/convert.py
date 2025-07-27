import sys

from logging import LogRecord, Handler
from typing import Optional, TextIO

from chara.log.logger import Logger, Record, Stream, DEBUG


class UvicornStream(Stream):
    
    def format(self, record: Record) -> str:
        T = record.time
        level = record.level
        log = f'{T.year}-{T.month}-{T.day} {T.hour:02d}:{T.minute:02d}:{T.second:02d} [{record.process.name}]' + f'[{record.thread.name}] [{level}] {str(record.msg)}'
        log = self.check_end(log)
        if (re := record.exception) is not None:
            log = self.check_end(log + self.format_exception(re))
        return log


class ConvertHandler(Handler):

    def __init__(self, stream: Optional[TextIO] = None) -> None:
        super().__init__()
        self.logger = Logger(DEBUG)
        if stream is None or stream is sys.stderr or stream is sys.stdout:
            self.logger.add_stream(Stream(stream or sys.stderr, DEBUG))
        else:
            self.logger.add_stream(UvicornStream(stream or sys.stderr, DEBUG))

    def emit(self, record: LogRecord) -> None:
        self.logger.log(record.levelname, record.getMessage())

