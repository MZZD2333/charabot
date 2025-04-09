from functools import partial
from typing import Any, Coroutine, Optional


class API:

    def __getattr__(self, name: str) -> partial[Coroutine[Any, Any, Any]]:
        return partial(self.call_api, name)

    async def call_api(self, api: str, **data: Any) -> Optional[dict[Any, Any]]:
        pass

