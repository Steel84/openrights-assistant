# OpenRights Assistant

An offline-first prototype that helps users find plain-language answers in public legal and consumer-protection sources.

The first demo jurisdiction is the United States. The prototype currently uses retrieval-only answers: it returns the most relevant source passages and their URLs rather than pretending to provide legal advice. A local small language model can be added as an optional generation layer after retrieval quality is measured.

## Goals

- Run locally after the initial data download.
- Keep the searchable corpus and retrieval code open and inspectable.
- Work on modest hardware without a hosted vector database.
- Show source passages and provenance for every result.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m openrights ingest
python -m openrights ask "What is the federal minimum wage?"
python -m openrights ask --model models/model.gguf "What is overtime pay?"
```

The current index is a dependency-light TF-IDF index. It is deliberately boring and deterministic so that the first MVP can be evaluated on a laptop before adding sentence embeddings or a quantized LLM.

## Mobile demo

The `app/` directory is a dependency-free responsive PWA. Run `python -m openrights export-web`, serve the repository over HTTPS, and open `/app/` on a phone. After the first load, the service worker caches the interface and local index. The search itself makes no network request. See `GRANT_READINESS.md` for the honest status of each grant requirement.

## Commands

```bash
python -m openrights ingest              # download and index official sources
python -m openrights ask "..."           # retrieve cited passages
python -m openrights ask --top-k 8 "..."
python -m openrights evaluate             # run the small smoke-test set
python -m openrights export-web           # build the self-contained mobile web index
```

The optional `--model` path expects a GGUF model and a `llama-cli` executable on `PATH`. Without it, the application remains fully usable as a cited retrieval tool.

The generated files under `data/raw/` and `data/processed/` are ignored by Git. Re-run `ingest` to recreate them.

## Sources

The initial corpus is limited to official public sources listed in `data/sources.json`:

- Fair Labor Standards Act, U.S. Code Title 29, Chapter 8, via GovInfo.
- FTC consumer advice on phishing and FTC advertising/marketing guidance.

This is an experimental information-retrieval tool, not a lawyer, and not a substitute for professional advice. Source coverage is incomplete; users should verify the current law and their jurisdiction.

## Roadmap

1. Establish retrieval and citation evaluation on 10-15 representative questions.
2. Add an optional local embedding index and compare it with TF-IDF.
3. Add llama.cpp-compatible quantized generation with a strict citation prompt.
4. Package the same pipeline behind a minimal mobile UI.
5. Publish a transparent evaluation set and limitations before submitting the grant application.

## Current status

The repository contains a working retrieval MVP and a twelve-question evaluation set. The local generation layer is implemented but intentionally optional until a model is selected and tested on the target phone. See `GRANT_READINESS.md` and `GRANT_DRAFT.md` for the current grant position.
