# Architecture

The application uses a small, explicit retrieval-augmented generation pipeline. Retrieval remains local; response generation can use Ollama, Gemini's limited free tier, or the credit-based OpenAI API without an orchestration framework.

## Indexing flow

```text
PDF / TXT / Markdown
        |
        v
Page-aware loader
        |
        v
Overlapping chunks (1,200 characters / 200 overlap)
        |
        v
Ollama embeddings (32-chunk batches)
        |
        v
Persistent ChromaDB collection
```

## Question-answering flow

```text
Question -> query embedding -> cosine similarity search
                                      |
                                      v
                         top-k source chunks
                                      |
                                      v
                         grounded Llama prompt
                                      |
                                      v
                          answer with citations
```

## Module boundaries

- `pdf_loader.py` reads supported files and preserves page numbers.
- `chunker.py` creates stable, overlapping chunks.
- `embedder.py` talks to the local Ollama embedding endpoint.
- `vector_store.py` owns ChromaDB persistence and retrieval.
- `retriever.py` formats retrieved chunks as cited context.
- `llm.py` generates grounded answers with bounded VRAM settings.
- `rag.py` exposes the indexing and question-answering API.
- `app.py` contains only the Streamlit presentation and user workflow.

## Resource profile

The default `llama3.2:3b` model, 4,096-token context, 128 generation batch, and 32-chunk embedding batch target machines with 8 GB VRAM. Ollama releases inactive models after the configured two-minute keep-alive period.
