from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


@dataclass(frozen=True)
class Page:
    source: str
    page_number: int
    text: str


def load_document(file_path: Path) -> list[Page]:
    """Load a supported document while preserving page metadata."""
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Desteklenmeyen dosya türü: {suffix}")
    if suffix == ".pdf":
        reader = PdfReader(file_path)
        pages = [Page(file_path.name, number, (page.extract_text() or "").strip())
                 for number, page in enumerate(reader.pages, start=1)]
    else:
        pages = [Page(file_path.name, 1, file_path.read_text(encoding="utf-8").strip())]
    return [page for page in pages if page.text]


def discover_documents(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    return sorted(path for path in directory.iterdir()
                  if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)


def load_pdf(file_path: Path) -> str:
    return "\n\n".join(page.text for page in load_document(file_path))
