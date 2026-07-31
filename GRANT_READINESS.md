# Grant Readiness Matrix

| Sentient requirement | Current status | Evidence / gap |
| --- | --- | --- |
| Works on a phone | Packaging ready, device test pending | `app/` is a mobile-responsive PWA and `android/` contains a native WebView shell. A physical low-cost Android test remains. |
| Works without internet | Yes after installation | Service worker caches UI and `app/data/index.json`; initial install/export still needs a host. |
| Open source at least partially | Yes | Code, source manifest, ingestion pipeline, evals, and prompts are in the repository. |
| Runs on a non-modern phone | Designed for it | No hosted backend, no JS framework, small TF-IDF index. Needs a real low-end Android benchmark. |
| Useful Sentient-like application | Yes, narrow MVP | Plain-language access to labor and consumer-protection sources. |
| Uses an LLM / neural model | Partial | Qwen 2.5 1.5B Q2 GGUF target is selected and the `llama.cpp` adapter is implemented; runtime and phone benchmark remain. |
| Low resource use | Measured for retrieval, pending for LLM | `python -m openrights benchmark` records latency/RSS. LLM memory budget still needs a phone measurement. |

## Honest submission position

The project is a credible technical MVP, not yet a finished mobile product. The strongest remaining evidence is one low-cost Android test, one small GGUF model benchmark, and a short screen recording showing airplane-mode search.
