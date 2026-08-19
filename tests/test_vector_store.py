import unittest
from unittest.mock import Mock, call

from src.vector_store import VectorStore


class VectorStoreMultiDocumentTests(unittest.TestCase):
    def test_hybrid_query_scans_all_documents_and_prioritizes_lexical_match(self):
        store = VectorStore.__new__(VectorStore)
        store.embedder = Mock()
        store.embedder.embed.return_value = [[0.1, 0.2]]
        store.collection = Mock()
        store.collection.count.return_value = 4
        store.collection.get.return_value = {
            "ids": ["a", "b"], "documents": ["unrelated text", "425 kişiye anket uygulandı"],
            "metadatas": [{"source": "a.pdf", "page": 1}, {"source": "b.pdf", "page": 8}],
        }
        store.collection.query.return_value = {
            "ids": [["a", "b"]], "documents": [["unrelated text", "425 kişiye anket uygulandı"]],
            "metadatas": [[{"source": "a.pdf", "page": 1}, {"source": "b.pdf", "page": 8}]],
            "distances": [[0.1, 0.2]],
        }

        results = store.query("Kaç kişiye anket uygulandı?", top_k=2)

        self.assertEqual(results[0]["metadata"]["source"], "b.pdf")
        self.assertEqual(store.embedder.embed.call_count, 1)
        store.collection.get.assert_called_with(include=["documents", "metadatas"])


if __name__ == "__main__":
    unittest.main()
