"""Async facade with a serial worker so synchronous providers stay off the event loop."""
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio
from typing import Any

from memory_sdk.client import Memory
from memory_sdk.filters import MemoryFilter
from memory_sdk.models import MemoryFact


class AsyncMemory:
    def __init__(self, memory: Memory | None = None, **kwargs: Any) -> None:
        self._memory = memory if memory is not None else Memory(**kwargs)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="memory-sdk")

    async def _call(self, method: str, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor, partial(getattr(self._memory, method), **kwargs)
        )

    async def save(self, *, user_id: str, key: str, value: str, kind: str = "fact",
                   importance: float = 0.5) -> MemoryFact:
        return await self._call("save", user_id=user_id, key=key, value=value,
                                kind=kind, importance=importance)

    async def save_text(self, *, user_id: str, text: str) -> list[MemoryFact]:
        return await self._call("save_text", user_id=user_id, text=text)

    async def retrieve(self, *, user_id: str, query: str | None = None, limit: int = 10,
                       filters: MemoryFilter | None = None) -> list[MemoryFact]:
        return await self._call("retrieve", user_id=user_id, query=query,
                                limit=limit, filters=filters)

    async def forget(self, *, user_id: str, memory_id: str) -> bool:
        return await self._call("forget", user_id=user_id, memory_id=memory_id)
