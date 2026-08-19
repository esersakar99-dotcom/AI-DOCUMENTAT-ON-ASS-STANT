from pathlib import Path
import re
import unicodedata
import chromadb
from .chunker import Chunk
from .embedder import OllamaEmbedder


class VectorStore:
    def __init__(self, path: Path, embedder: OllamaEmbedder):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self.client = chromadb.PersistentClient(path=str(path))
        self.collection = self.client.get_or_create_collection(
            name="documents", metadata={"hnsw:space": "cosine"})

    @property
    def count(self) -> int:
        return self.collection.count()

    @property
    def sources(self) -> list[str]:
        """Return every distinct indexed document name."""
        if not self.count:
            return []
        result = self.collection.get(include=["metadatas"])
        return sorted({meta["source"] for meta in result["metadatas"]})

    def replace_source(self, source: str, chunks: list[Chunk]) -> None:
        self.collection.delete(where={"source": source})
        # Avoid keeping every embedding in memory for large PDFs.
        # A 32-chunk batch is a conservative default for systems with 8 GB VRAM or less.
        batch_size = 32
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            self.collection.upsert(
                ids=[c.id for c in batch], documents=[c.text for c in batch],
                embeddings=self.embedder.embed([c.text for c in batch]),
                metadatas=[{"source": c.source, "page": c.page, "chunk": c.chunk_index} for c in batch])

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        if not self.count:
            return []
        embedding = self.embedder.embed([question])
        candidate_count = min(max(top_k * 6, 30), self.count)
        semantic = self.collection.query(query_embeddings=embedding, n_results=candidate_count)
        semantic_items = [
            {"id": item_id, "text": text, "metadata": meta, "distance": distance}
            for item_id, text, meta, distance in zip(semantic["ids"][0], semantic["documents"][0],
                                                      semantic["metadatas"][0], semantic["distances"][0])
        ]

        # Multilingual embedding models can miss exact Turkish wording and numbers. Scan all
        # indexed chunks lexically as well, then fuse both rankings. This still searches every
        # PDF, while avoiding irrelevant context being forced into the final prompt.
        stored = self.collection.get(include=["documents", "metadatas"])
        query_terms = self._search_terms(question)
        lexical_items = []
        for item_id, text, meta in zip(stored["ids"], stored["documents"], stored["metadatas"]):
            text_terms = self._search_terms(text)
            overlap = sum(1 for term in query_terms if any(word.startswith(term) for word in text_terms))
            if overlap:
                lexical_items.append((overlap, {"id": item_id, "text": text, "metadata": meta,
                                                "distance": 1.0}))
        lexical_items.sort(key=lambda item: item[0], reverse=True)

        fused: dict[str, dict] = {}
        for rank, item in enumerate(semantic_items, 1):
            fused[item["id"]] = {**item, "score": 1 / (60 + rank)}
        for rank, (_, item) in enumerate(lexical_items[:candidate_count], 1):
            if item["id"] not in fused:
                fused[item["id"]] = {**item, "score": 0.0}
            # Exact wording is especially valuable for names, figures and Turkish suffixes.
            fused[item["id"]]["score"] += 3 / (20 + rank)
        ranked = sorted(fused.values(), key=lambda item: item["score"], reverse=True)[:top_k]
        return [{key: value for key, value in item.items() if key not in {"id", "score"}}
                for item in ranked]

    @staticmethod
    def _search_terms(text: str) -> set[str]:
        normalized = unicodedata.normalize("NFKD", text.casefold().replace("ı", "i"))
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        stop_words = {"acaba", "ama", "ancak", "bana", "bir", "bu", "butun", "da", "daha",
                      "de", "icin", "ile", "kac", "mi", "mu", "nedir", "olan", "olarak",
                      "sonra", "soru", "ve", "veya"}
        words = re.findall(r"[a-z0-9]+", normalized)
        terms = {word if word.isdigit() else word[:5] for word in words
                 if len(word) >= 3 and word not in stop_words}
        return terms - {"arast", "bunla", "edilm", "kaci"}

    def clear(self) -> None:
        self.client.delete_collection("documents")
