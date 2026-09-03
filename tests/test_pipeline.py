from memory_sdk import ExtractedFact, Memory, MemoryConfig


class FakeExtractor:
    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
        assert user_id == "alice"
        return [
            ExtractedFact(key="language", value="Python", importance=0.8),
            ExtractedFact(key="language", value="Python", importance=0.8),
            ExtractedFact(key="editor", value="Neovim", importance=0.6),
        ]


class FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            lowered = text.casefold()
            if "python" in lowered:
                vectors.append([1.0, 0.0])
            elif "neovim" in lowered:
                vectors.append([0.0, 1.0])
            else:
                vectors.append([0.5, 0.5])
        return vectors


def test_save_text_runs_pipeline_and_deduplicates(tmp_path):
    memory = Memory(
        MemoryConfig(database_path=tmp_path / "memory.db"),
        extractor=FakeExtractor(),
        embedder=FakeEmbedder(),
    )

    first = memory.save_text(user_id="alice", text="I use Python and Neovim")
    second = memory.save_text(user_id="alice", text="I use Python and Neovim")

    assert [fact.key for fact in first] == ["language", "editor"]
    assert second == []
    assert len(memory.retrieve(user_id="alice")) == 2
    assert all(fact.embedding is not None for fact in first)


def test_retrieve_prefers_vector_similarity_when_embedder_is_available(tmp_path):
    memory = Memory(
        MemoryConfig(database_path=tmp_path / "memory.db"),
        extractor=FakeExtractor(),
        embedder=FakeEmbedder(),
    )
    memory.save_text(user_id="alice", text="I use Python and Neovim")

    results = memory.retrieve(user_id="alice", query="python", limit=1)

    assert len(results) == 1
    assert results[0].key == "language"


def test_blank_text_does_not_call_extractor(tmp_path):
    class ExplodingExtractor:
        def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
            raise AssertionError("extractor should not be called")

    memory = Memory(
        MemoryConfig(database_path=tmp_path / "memory.db"),
        extractor=ExplodingExtractor(),
        embedder=FakeEmbedder(),
    )

    assert memory.save_text(user_id="alice", text="   ") == []
