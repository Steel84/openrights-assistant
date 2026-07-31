# Grant Readiness Matrix

| Sentient requirement | Current status | Evidence / gap |
| --- | --- | --- |
| Works on a phone | Packaging ready, device test pending | `app/` is a mobile-responsive PWA and `android/` contains a native WebView shell. A physical low-cost Android test remains. |
| Works without internet | Yes after installation | Service worker caches the UI and `app/data/index.js` (504 KB); the APK reads them from local assets. Only the first download needs a network. |
| Open source at least partially | Yes | Code, source manifest, ingestion pipeline, evals, and prompts are in the repository. |
| Runs on a non-modern phone | Designed for it, not yet proven | No hosted backend, no JS framework, 504 KB index, retrieval at ~3.8 ms per query on a dev machine. A physical low-end Android measurement is still missing. |
| Useful Sentient-like application | Yes, narrow MVP | Plain-language access to labor and consumer-protection sources. |
| Uses an LLM / neural model | Partial | Qwen 2.5 1.5B Q2 GGUF target is selected and the `llama.cpp` adapter is implemented; runtime and phone benchmark remain. |
| Low resource use | Measured for retrieval, pending for LLM | `python -m openrights benchmark` records latency and the resident-memory delta of loading the index (~0.5 MB). Earlier drafts quoted a process peak RSS figure, which measured the host interpreter rather than this app and has been removed. The LLM memory budget still needs a phone measurement. |

## Honest submission position

The project is a credible technical MVP, not yet a finished mobile product. The strongest remaining evidence is one low-cost Android test, one small GGUF model benchmark, and a short screen recording showing airplane-mode search.

Reviewers can reproduce the current claims in three commands: `ingest`, `evaluate`, `benchmark`. `RUNNING.md` explains how to open the app on a phone without an Android toolchain.
