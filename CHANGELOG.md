# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-08-19

### Added

- GitHub Actions workflow for unit tests and compilation checks.
- Architecture and usage documentation.
- PowerShell scripts for model setup and local service management.
- Environment-based configuration with a documented `.env.example`.

### Changed

- Organized the repository around application, documentation, automation, and test concerns.

## [1.1.0] - 2026-08-19

### Changed

- Translated the complete Streamlit interface into English.
- Updated assistant instructions, retrieval labels, and citations for English responses.

## [1.0.0] - 2026-08-19

### Added

- Local Ollama and Llama RAG pipeline
- PDF, TXT, and Markdown ingestion
- Page-aware chunking and cited answers
- Persistent ChromaDB vector index
- Premium Streamlit interface
- 1 GB per-file upload support
- VRAM-conscious context, generation, and embedding batch limits
- Core chunking tests
