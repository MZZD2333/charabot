from typing import Any, Optional


class Node:
    
    __slots__ = ('value' ,'parent', 'subnodes')
    
    value: Any
    parent: Optional['Node']
    subnodes: dict[Any, 'Node']
    

    def __init__(self, value: Any = None, parent: Optional['Node'] = None) -> None:
        self.value = value
        self.parent = parent
        self.subnodes: dict[Any, Node] = dict()

    def __getitem__(self, keys: Any) -> Optional['Node']:
        if isinstance(keys, tuple):
            if len(keys) == 1: # type: ignore
                return self.subnodes.get(keys[0], None)
            if subnode := self.subnodes.get(keys[0], None):
                return subnode[keys[1:]]
        return self.subnodes.get(keys, None)
    
    def __setitem__(self, keys: Any, value: 'Node') -> None:
        node = self
        if isinstance(keys, tuple):
            for key in keys[:-1]: # type: ignore
                node = node.subnodes.setdefault(key, Node(parent=node))
            node.subnodes[keys[-1]] = value
        else:
            self.subnodes[keys] = value
        value.parent = node
        
    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        return not self.subnodes
    

__all__ = [
    'Node',
]

