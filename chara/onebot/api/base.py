from typing import Any, Optional

class API:
    
    __slots__ = ()

    async def call_api(self, api: str, **data: Any) -> Optional[dict[Any, Any]]:
        '''## 调用API'''
