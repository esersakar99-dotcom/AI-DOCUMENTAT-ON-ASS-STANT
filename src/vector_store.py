from pathlib import Path
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

    def replace_source(self, source: str, chunks: list[Chunk]) -> None:
        self.collection.delete(where={"source": source})
        # Büyük PDF'lerde tüm embedding'leri tek seferde belleğe alma.
        # 32 parça, 8 GB ve altı VRAM'e sahip sistemlerde güvenli bir varsayılandır.
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
        result = self.collection.query(query_embeddings=self.embedder.embed([question]),
                                       n_results=min(top_k, self.count))
        return [{"text": text, "metadata": meta, "distance": distance}
                for text, meta, distance in zip(result["documents"][0], result["metadatas"][0],
                                                result["distances"][0])]

    def clear(self) -> None:
        self.client.delete_collection("documents")
