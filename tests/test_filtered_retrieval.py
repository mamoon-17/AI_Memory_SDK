from memory_sdk import Memory, MemoryConfig, MemoryFilter


def test_filter_is_applied_before_limit(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    memory.save(user_id='alice', key='a', value='Python', importance=1)
    match = memory.save(user_id='alice', key='b', value='Python', kind='preference')
    memory.save(user_id='bob', key='b', value='Python', kind='preference')
    assert memory.retrieve(user_id='alice', query='Python', limit=1,
                           filters=MemoryFilter(kind='preference')) == [match]


def test_filtered_vector_search_does_not_truncate_before_filter(tmp_path):
    class Embedder:
        def embed(self, texts):
            return [[1.0, 0.0] for _ in texts]

    from memory_sdk import MemoryFact

    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'), embedder=Embedder())
    memory.save_many([MemoryFact(user_id='alice', key=str(i), value='x',
                                embedding=[1.0, 0.0]) for i in range(10)])
    match = MemoryFact(user_id='alice', key='target', value='y', embedding=[0.5, 0.5])
    memory.save_many([match])
    assert memory.retrieve(user_id='alice', query='y', limit=1,
                           filters=MemoryFilter(key='target')) == [match]
