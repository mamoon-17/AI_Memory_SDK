import asyncio
import threading

from memory_sdk import Memory, MemoryConfig
from memory_sdk.async_client import AsyncMemory


def test_async_io_does_not_block_loop(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    entered, release = threading.Event(), threading.Event()
    original = memory.retrieve

    def slow_retrieve(**kwargs):
        entered.set()
        assert release.wait(5)
        return original(**kwargs)

    memory.retrieve = slow_retrieve

    async def run():
        client = AsyncMemory(memory)
        task = asyncio.create_task(client.retrieve(user_id='alice'))
        try:
            assert await asyncio.to_thread(entered.wait, 2)
            assert not task.done()
        finally:
            release.set()
        assert await task == []
        client._executor.shutdown()

    asyncio.run(run())
