import unittest

from src.chunker import chunk_pages
from src.pdf_loader import Page


class ChunkerTests(unittest.TestCase):
    def test_preserves_page_metadata_for_large_document(self):
        pages = [Page("rapor.pdf", page, (f"Sayfa {page} içeriği. " * 100))
                 for page in range(1, 13)]
        chunks = chunk_pages(pages)
        self.assertEqual({chunk.page for chunk in chunks}, set(range(1, 13)))
        self.assertTrue(all(chunk.source == "rapor.pdf" for chunk in chunks))

    def test_rejects_invalid_overlap(self):
        with self.assertRaises(ValueError):
            chunk_pages([], chunk_size=100, overlap=100)


if __name__ == "__main__":
    unittest.main()
