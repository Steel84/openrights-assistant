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

The `app/` directory is a dependency-free responsive PWA. The fastest way to see it:

```bash
python -m openrights bundle      # one self-contained file in dist/
python -m openrights serve       # prints a LAN address to open on a phone
```

`serve` prints both a `localhost` address and a same-Wi-Fi address for a phone. Install the page from the browser menu, then switch the phone to airplane mode: the service worker has cached the interface and the archive, and search makes no network request. `RUNNING.md` covers all three ways to run it, including the Android APK. `GRANT_READINESS.md` tracks the honest status of each grant requirement.

## Commands

```bash
python -m openrights ingest              # download and index official sources
python -m openrights ask "..."           # retrieve cited passages
python -m openrights ask --top-k 8 "..."
python -m openrights evaluate             # run the small smoke-test set
python -m openrights export-web           # build the self-contained mobile web archive
python -m openrights bundle               # build dist/openrights-demo.html (single file)
python -m openrights serve                # serve app/ to this machine and to a phone
python -m openrights benchmark            # measure retrieval latency and memory
```

The optional `--model` path expects a GGUF model and a `llama-cli` executable on `PATH`. Without it, the application remains fully usable as a cited retrieval tool.

For an Android debug APK, install Android SDK/Gradle, set `ANDROID_HOME`, then run `scripts/build_android.sh`. The script copies the same offline app into a native WebView shell; no network permission is requested. Step-by-step instructions, including the Android Studio route, are in `RUNNING.md`.

The phone archive is exported as `app/data/index.js` rather than a JSON file that the page fetches, because a WebView running from `file:///android_asset/` is not allowed to fetch a sibling file.

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

## Measured status

From `python -m openrights benchmark` on a development machine (not a phone):

| Metric | Value |
| --- | --- |
| Passages indexed | 142 |
| Retrieval latency | ~3.8 ms per query |
| Index resident memory | ~0.5 MB |
| Archive shipped to the phone | 504 KB |
| Evaluation | 13/13 questions retrieve the expected source |

## Current status

The repository contains a working retrieval MVP and a thirteen-question evaluation set. The local generation layer is implemented but intentionally optional until a model is selected and tested on the target phone. See `GRANT_READINESS.md` and `GRANT_DRAFT.md` for the current grant position.
