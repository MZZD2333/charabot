from hashlib import md5
from multiprocessing.shared_memory import SharedMemory
from struct import pack, unpack
from typing import Callable, Generic

from chara.typing import T


class SharedValue(Generic[T]):
    
    __slots__ = ('_size', '_sm', '_read', '_write')
    
    def __init__(self, name: str, size: int, default: T, read: Callable[[bytes], T], write: Callable[[T], bytes]) -> None:
        from chara.core.hazard import IN_SUB_PROCESS, SHARED_VALUES
        
        self._size = size
        name = md5(name.encode('UTF-8')).hexdigest()
        if IN_SUB_PROCESS:
            self._sm = SharedMemory(name, False, size)
        else:
            self._sm = SharedMemory(name, name not in SHARED_VALUES, size)
        self._read = read
        self._write = write
        SHARED_VALUES[name] = self
        self.write(default)
        
    @property
    def value(self) -> T:
        return self._read(bytes(self._sm.buf[:self._size]))
    
    def write(self, data: T) -> None:
        self._sm.buf[:self._size] = self._write(data)
    
    def close(self) -> None:
        self._sm.close()

    def unlink(self) -> None:
        self._sm.unlink()


def shared_should_exit(name: str, default: bool = False) -> SharedValue[bool]:
    def read(data: bytes) -> bool:
        return unpack('>?', data)[0]
    
    def write(data: bool) -> bytes:
        return pack('>?', data)
    
    return SharedValue(name, 1, default, read, write)
    
def shared_plugin_state(name: str, default: int = 0) -> SharedValue[int]:
    def read(data: bytes) -> int:
        return unpack('>B', data)[0]
    
    def write(data: int) -> bytes:
        return pack('>B', data)
    
    return SharedValue(name, 1, default, read, write)
    
def shared_bot_data_update_time(name: str, default: float = 0) -> SharedValue[float]:
    def read(data: bytes) -> float:
        return unpack('>d', data)[0]
    
    def write(data: float) -> bytes:
        return pack('>d', data)
    
    return SharedValue(name, 8, default, read, write)
    
