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
        await client.aclose()

    asyncio.run(run())


def test_context_manager_drains_and_rejects_closed_calls(tmp_path):
    import pytest

    async def run():
        async with AsyncMemory(config=MemoryConfig(database_path=tmp_path / 'memory.db')) as client:
            fact = await client.save(user_id='alice', key='a', value='b')
            assert (await client.retrieve(user_id='alice'))[0].id == fact.id
        await client.aclose()
        with pytest.raises(RuntimeError, match='closed'):
            await client.retrieve(user_id='alice')

    asyncio.run(run())


def test_async_export_import_and_list(tmp_path):
    async def run():
        async with AsyncMemory(config=MemoryConfig(database_path=tmp_path / 'memory.db')) as client:
            fact = await client.save(user_id='alice', key='a', value='b')
            data = await client.export_json(user_id='alice')
            assert await client.import_json(user_id='alice', data=data) == [fact]
            assert await client.list(user_id='alice') == [fact]
            assert await client.forget(user_id='bob', memory_id=fact.id) is False
            assert await client.forget(user_id='alice', memory_id=fact.id) is True

    asyncio.run(run())
