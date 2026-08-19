from pathlib import Path
from .chunker import chunk_pages
from .embedder import OllamaEmbedder
from .llm import create_llm
from .pdf_loader import discover_documents, load_document
from .retriever import retrieve_context
from .vector_store import VectorStore


class RAGAssistant:
    def __init__(self, database_dir: Path = Path("database"), chat_model: str = "llama3.2:3b",
                 embedding_model: str = "nomic-embed-text", host: str | None = None,
                 provider: str = "ollama", api_key: str = "", base_url: str | None = None):
        self.store = VectorStore(database_dir, OllamaEmbedder(embedding_model, host))
        self.llm = create_llm(provider, chat_model, api_key, host, base_url)

    def index_file(self, path: Path) -> int:
        chunks = chunk_pages(load_document(path))
        self.store.replace_source(path.name, chunks)
        return len(chunks)

    def index_directory(self, path: Path) -> dict[str, int]:
        return {doc.name: self.index_file(doc) for doc in discover_documents(path)}

    def ask(self, question: str, top_k: int = 5) -> tuple[str, list[dict]]:
        context, sources = retrieve_context(self.store, question, top_k)
        if not context:
            return "No documents have been indexed yet.", []
        return self.llm.answer(question, context), sources
