from enum import Enum
from typing import Any


def _style_wrap(text: str, *styles: str) -> str:
    if styles:
        return '\033[' + ';'.join(styles) + f'm{text}\033[0m'
    return text

class _wrapper:
    __slots__ = ('style', 'styles')
    
    def __init__(self, *styles: str) -> None:
        self.style = '\033[' + ';'.join(styles) + 'm'

    def __call__(self, text: Any) -> str:
        return self.style + str(text) + '\033[0m'


class style(Enum):
    
    custom = _style_wrap
    '''## 自定义'''

    k = _wrapper('30').__call__
    '''## 黑色'''
    r = _wrapper('31').__call__
    '''## 红色'''
    g = _wrapper('32').__call__
    '''## 绿色'''
    y = _wrapper('33').__call__
    '''## 黄色'''
    e = _wrapper('34').__call__
    '''## 蓝色'''
    m = _wrapper('35').__call__
    '''## 紫色'''
    c = _wrapper('36').__call__
    '''## 青色'''
    w = _wrapper('37').__call__
    '''## 白色'''

    lk = _wrapper('90').__call__
    '''## 亮黑色'''
    lr = _wrapper('91').__call__
    '''## 亮红色'''
    lg = _wrapper('92').__call__
    '''## 亮绿色'''
    ly = _wrapper('93').__call__
    '''## 亮黄色'''
    le = _wrapper('94').__call__
    '''## 亮蓝色'''
    lm = _wrapper('95').__call__
    '''## 亮紫色'''
    lc = _wrapper('96').__call__
    '''## 亮青色'''
    lw = _wrapper('97').__call__
    '''## 亮白色'''


