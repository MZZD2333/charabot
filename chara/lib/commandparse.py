import re
import shlex

from dataclasses import dataclass
from typing import Any, Callable, Optional, Type


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class FlagArgument:
    '''
    ## 标记参数
    '''
    name: str
    usage: str = ''


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class KeywordArgument:
    '''
    ## 键值参数
    '''
    name: str
    prefix: str
    default: Any = None
    as_type: Type[Any] | Callable[[str], Any] = str
    usage: str = ''

    @property
    def key(self) -> str:
        return self.prefix + self.name


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class PostionArgument:
    '''
    ## 位置参数
    '''
    default: Any = None
    as_type: Type[Any] | Callable[[str], Any] = str
    usage: str = ''


@dataclass(repr=False, eq=False, slots=True)
class ParseResult:
    '''
    ## 解析结果
    '''
    commands: list[str]
    flags: dict[str, bool]
    kwargs: dict[str, Any]
    posargs: list[Any]
    uncatch: list[str]


class CommandParser:
    '''
    ## 命令解析器
    '''
    __slots__ = ('flags', 'kwargs', 'pattern', 'posargs', 'start', 'sub_parsers')
    
    flags: list[FlagArgument]
    kwargs: list[KeywordArgument]
    posargs: list[PostionArgument]
    sub_parsers: list['CommandParser']
    
    pattern: re.Pattern[str]
    start: str
    
    def __init__(self, command_start: str | re.Pattern[str]) -> None:
        if isinstance(command_start, re.Pattern):
            self.start = command_start.pattern
            self.pattern = command_start
        else:
            self.start = command_start
            self.pattern = re.compile(command_start)
        self.flags = list()
        self.kwargs = list()
        self.posargs = list()
        self.sub_parsers = list()
    
    def add_flag_argument(self, name: str, usage: str = '') -> None:
        self.flags.append(FlagArgument(name, usage))

    def add_keyword_argument(self, name: str, prefix: str = '-', default: Any = None, as_type: Type[Any] | Callable[[str], Any] = str, usage: str = '') -> None:
        self.kwargs.append(KeywordArgument(name, prefix, default, as_type, usage))

    def add_postion_argument(self, default: Any = None, as_type: Type[Any] | Callable[[str], Any] = str, usage: str = '') -> None:
        self.posargs.append(PostionArgument(default, as_type, usage))

    def add_sub_parser(self, parser: 'CommandParser') -> None:
        self.sub_parsers.append(parser)
        
    def parse(self, command: str) -> Optional[ParseResult]:
        command_args = shlex.split(command)
        if command_args:  
            if re.search(self.pattern, command_args[0]):
                return self(command_args[1:])

    def __call__(self, command: str | list[str]) -> ParseResult:
        if isinstance(command, str):
            command_args = shlex.split(command)
        else:
            command_args = command
        
        if command_args:
            command_start = command_args[0]
            for sub_parser in self.sub_parsers:
                if re.search(sub_parser.pattern, command_start):
                    result = sub_parser(command_args[1:])
                    result.commands.insert(0, self.start)
                    return result
        
        result_command = [self.start]
        result_flags = {flag.name: False for flag in self.flags}
        result_kwargs = {kwarg.name: kwarg.default for kwarg in self.kwargs}
        result_posargs: list[Any] = list()
        result_uncatch: list[str] = list()
        catched_kwargs: dict[str, KeywordArgument] = dict()
        # 0 未分配
        # 1 标记参数
        # 2 位置参数
        # 3 键值参数
        len_command_args = len(command_args)
        command_args_mask = [0] * len_command_args

        for kwarg in self.kwargs:
            if (key := kwarg.key) not in command_args:
                continue
            index = command_args.index(key)
            command_args_mask[index] = 3
            catched_kwargs[key] = kwarg
        
        for flag in self.flags:
            if flag.name not in command_args:
                continue
            index = command_args.index(flag.name)
            command_args_mask[index] = 1
        
        if self.posargs:
            for i in range(len_command_args):
                if command_args_mask[i] == 0:
                    command_args_mask[i] = 2
                else:
                    break
        last_arg = ''
        last_mask = 0
        for index, mask in enumerate(command_args_mask):
            arg = command_args[index]
            if mask == 0:
                if last_mask == 3 and last_arg in catched_kwargs:
                    kwarg = catched_kwargs[last_arg]
                    result_kwargs[kwarg.name] = kwarg.as_type(arg)
                else:
                    result_uncatch.append(command_args[index])
            elif mask == 1:
                result_flags[arg] = True
            elif mask == 2:
                len_posargs = len(result_posargs)
                result_posargs.append(self.posargs[len_posargs].as_type(arg))
            
            last_arg = arg
            last_mask = mask
        if (lack := len(result_posargs) - len(self.posargs)) > 0:
            result_posargs.extend([arg.default for arg in self.posargs[-lack:]])
        
        return ParseResult(result_command, result_flags, result_kwargs, result_posargs, result_uncatch)


__all__ = [
    'CommandParser',
    'ParseResult',
]

