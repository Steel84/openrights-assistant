# Architecture

OpenRights Assistant is designed as a modular offline-first information retrieval system. Each layer can be used independently.

## System overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                         │
│  PWA (browser/phone) │ Android WebView │ CLI             │
└──────────────┬───────────────┬──────────────┬───────────┘
               │               │              │
┌──────────────▼───────────────▼──────────────▼───────────┐
│                   Retrieval Layer                         │
│  TF-IDF cosine search over chunked legal passages        │
│  Input: natural-language question                         │
│  Output: ranked passages with source URL and score        │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│               Generation Layer (optional)                 │
│  llama.cpp with a quantized 1.5-4B parameter model       │
│  Input: question + retrieved passages                     │
│  Output: plain-language answer with [1][2] citations      │
│  Constraint: 256 token cap, temperature 0.2              │
└─────────────────────────────────────────────────────────┘
```

## Data flow

1. **Ingest**: Official HTML sources are downloaded, cleaned (tags/nav/scripts removed), split into ~450-word overlapping chunks, and indexed with TF-IDF.
2. **Index**: The index stores term frequencies, inverse document frequencies, and metadata (source title, URL, chunk ID) in a single JSON file.
3. **Search**: A user question is tokenized and vectorized with the same IDF weights. Cosine similarity ranks passages. Top-k results are returned with provenance.
4. **Generate** (optional): Retrieved passages are formatted into a strict prompt. A local GGUF model produces a short cited answer.
5. **Export**: For the phone, vectors are stripped (recomputed in the browser) and the index is exported as a JS assignment for WebView compatibility.

## Design decisions

| Decision | Rationale |
| --- | --- |
| TF-IDF over embeddings | Zero dependencies, deterministic, fast on weak hardware, easy to debug |
| No external vector DB | Offline requirement; single JSON file is portable |
| 450-word chunks with 60-word overlap | Balances context length vs. retrieval precision |
| JS assignment instead of fetch | WebView file:// origin blocks fetch(); script tags work |
| Optional LLM | Retrieval alone is useful; generation adds value but requires more resources |
| Apache 2.0 | Compatible with all major open-source AI ecosystems |

## Resource budget (target)

| Resource | Budget |
| --- | --- |
| Install size (retrieval only) | < 5 MB |
| Install size (with model) | < 2 GB |
| RAM at rest (retrieval) | < 50 MB |
| RAM during generation | < 3 GB |
| Query latency (retrieval) | < 50 ms |
| Query latency (generation) | < 15 seconds on mid-range phone |
| Network after install | Zero |

## Directory structure

```
openrights-assistant/
├── openrights/          # Python package: ingest, search, generate, benchmark
├── app/                 # PWA: HTML, CSS, JS, service worker, exported index
├── android/             # Android WebView shell (Gradle project)
├── data/                # Source manifest + gitignored raw/processed data
├── evals/               # Evaluation question set
├── models/              # Gitignored GGUF files + download instructions
├── scripts/             # Build and download helpers
├── tests/               # Unit tests
├── benchmarks/          # Gitignored benchmark results
└── docs/                # Additional documentation
```

## Extensibility

- **New jurisdiction**: add entries to `data/sources.json`, run ingest.
- **New language**: the tokenizer handles Latin-script languages; CJK/Arabic would need a tokenizer swap (planned).
- **Better retrieval**: swap TF-IDF for sentence-transformer embeddings by replacing `rag.py`; the CLI and app interfaces stay the same.
- **Better generation**: swap llama.cpp for any local inference runtime that accepts a text prompt.
