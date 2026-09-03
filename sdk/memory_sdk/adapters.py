from __future__ import annotations

import json
from typing import Any

from memory_sdk.providers import ExtractedFact


class LiteLLMFactExtractor:
    """Provider-agnostic extractor backed by LiteLLM.

    LiteLLM is imported on first use so importing the SDK never requires provider setup.
    Provider credentials continue to be resolved by LiteLLM/environment configuration.
    """

    def __init__(self, model: str) -> None:
        if not model.strip():
            raise ValueError("model must not be empty")
        self.model = model

    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]:
        try:
            from litellm import completion
        except ImportError as exc:  # pragma: no cover - depends on installation profile
            raise RuntimeError("LiteLLM is required for text fact extraction") from exc

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract durable user memory as JSON only. Return an object with a "
                        "'facts' array. Each fact must have key, value, kind, and importance "
                        "(0 to 1). Ignore transient or non-user-specific chatter."
                    ),
                },
                {"role": "user", "content": f"user_id={user_id}\n{text}"},
            ],
            response_format={"type": "json_object"},
        )
        content = _response_content(response)
        payload = json.loads(content)
        facts = payload.get("facts", [])
        if not isinstance(facts, list):
            raise TypeError("LiteLLM extractor response must contain a facts array")
        return [ExtractedFact.model_validate(item) for item in facts]


class FastEmbedEmbeddingProvider:
    """Local ONNX embedding adapter loaded lazily on first embedding request."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from fastembed import TextEmbedding
            except ImportError as exc:  # pragma: no cover - depends on installation profile
                raise RuntimeError("FastEmbed is required for local embeddings") from exc
            kwargs = {"model_name": self.model_name} if self.model_name else {}
            self._model = TextEmbedding(**kwargs)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._load_model().embed(texts)
        return [[float(value) for value in vector] for vector in vectors]


def _response_content(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise ValueError("LiteLLM extractor returned an unexpected response shape") from exc
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LiteLLM extractor returned empty content")
    return content
