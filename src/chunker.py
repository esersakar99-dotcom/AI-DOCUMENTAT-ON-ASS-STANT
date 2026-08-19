from __future__ import annotations

from dataclasses import dataclass
from .pdf_loader import Page


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    page: int
    chunk_index: int


def chunk_pages(pages: list[Page], chunk_size: int = 1200, overlap: int = 200) -> list[Chunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")
    chunks: list[Chunk] = []
    for page in pages:
        content = " ".join(page.text.split())
        start = index = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))
            if end < len(content):
                boundary = content.rfind(" ", start + chunk_size // 2, end)
                if boundary > start:
                    end = boundary
            text = content[start:end].strip()
            if text:
                safe_source = page.source.replace(" ", "_")
                chunks.append(Chunk(f"{safe_source}:p{page.page_number}:c{index}", text,
                                    page.source, page.page_number, index))
            if end >= len(content):
                break
            start = end - overlap
            index += 1
    return chunks
