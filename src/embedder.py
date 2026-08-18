from __future__ import annotations
import ollama


class OllamaEmbedder:
    def __init__(self, model: str = "nomic-embed-text", host: str | None = None):
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        # A short keep-alive prevents the embedding model from holding VRAM unnecessarily.
        return self.client.embed(model=self.model, input=texts, keep_alive="2m")["embeddings"]

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.embed(input)
