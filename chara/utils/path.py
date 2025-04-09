import sys

from pathlib import Path

from chara.typing import PathLike


def is_same_path(path_1: PathLike, path_2: PathLike) -> bool:
    path_1 = Path(path_1)
    path_2 = Path(path_2)
    
    try:
        stat_1 = path_1.stat()
        stat_2 = path_2.stat()
        return stat_1.st_ino == stat_2.st_ino and stat_1.st_dev == stat_2.st_dev
    except:
        return False

def is_in_env(path: PathLike) -> bool:
    for sys_path in sys.path:
        if is_same_path(path, sys_path):
            return True
    return False

def add_to_env(path: PathLike) -> None:
    path = str(path)
    sys.path.append(path)
