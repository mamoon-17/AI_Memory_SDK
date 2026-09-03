from memory_sdk import ExtractedFact, Memory, MemoryConfig


class FakeExtractor:
    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
        assert user_id == "alice"
        return [
            ExtractedFact(key="language", value="Python", importance=0.8),
            ExtractedFact(key="language", value="Python", importance=0.8),
            ExtractedFact(key="editor", value="Neovim", importance=0.6),
        ]


class ChangedLanguageExtractor:
    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
        assert user_id == "alice"
        return [ExtractedFact(key="language", value="Rust", importance=0.9)]


class QualityExtractor:
    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
        assert user_id == "alice"
        return [
            ExtractedFact(key="theme", value="dark mode", kind="preference", importance=0.5),
            ExtractedFact(key="status", value="busy", kind="transient", importance=0.5),
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


def test_importance_scoring_runs_before_storage(tmp_path):
    memory = Memory(
        MemoryConfig(database_path=tmp_path / "memory.db"),
        extractor=QualityExtractor(),
        embedder=FakeEmbedder(),
    )

    saved = memory.save_text(user_id="alice", text="I prefer dark mode but am busy now")
    by_key = {fact.key: fact for fact in saved}

    assert by_key["theme"].importance > by_key["status"].importance
    assert by_key["theme"].importance != 0.5


def test_conflicting_fact_replaces_prior_value_for_same_user(tmp_path):
    config = MemoryConfig(database_path=tmp_path / "memory.db")
    memory = Memory(config, extractor=ChangedLanguageExtractor(), embedder=FakeEmbedder())
    old_fact = memory.save(user_id="alice", key="language", value="Python", importance=0.8)
    other_user_fact = memory.save(user_id="bob", key="language", value="Go", importance=0.7)

    saved = memory.save_text(user_id="alice", text="I switched from Python to Rust")

    alice_facts = memory.retrieve(user_id="alice")
    bob_facts = memory.retrieve(user_id="bob")
    assert [fact.value for fact in saved] == ["Rust"]
    assert [fact.value for fact in alice_facts] == ["Rust"]
    assert old_fact.id not in {fact.id for fact in alice_facts}
    assert [fact.id for fact in bob_facts] == [other_user_fact.id]


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
