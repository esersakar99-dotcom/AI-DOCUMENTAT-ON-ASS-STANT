from .vector_store import VectorStore


def retrieve_context(store: VectorStore, question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    results = store.query(question, top_k=top_k)
    blocks = [f"[Kaynak: {r['metadata']['source']}, sayfa {r['metadata']['page']}]\n{r['text']}"
              for r in results]
    return "\n\n---\n\n".join(blocks), results
