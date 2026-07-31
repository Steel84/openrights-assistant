# Grant Readiness Matrix

| Sentient requirement | Current status | Evidence / gap |
| --- | --- | --- |
| Works on a phone | Partial | `app/` is a mobile-responsive PWA. Native Android packaging and device test remain. |
| Works without internet | Yes after installation | Service worker caches UI and `app/data/index.json`; initial install/export still needs a host. |
| Open source at least partially | Yes | Code, source manifest, ingestion pipeline, evals, and prompts are in the repository. |
| Runs on a non-modern phone | Designed for it | No hosted backend, no JS framework, small TF-IDF index. Needs a real low-end Android benchmark. |
| Useful Sentient-like application | Yes, narrow MVP | Plain-language access to labor and consumer-protection sources. |
| Uses an LLM / neural model | Partial | Optional `llama.cpp` GGUF generation layer is implemented; weights and phone benchmark are still pending. |
| Low resource use | Yes for retrieval | Browser retrieval uses a compact local JSON index. LLM memory budget is documented but unverified. |

## Honest submission position

The project is a credible technical MVP, not yet a finished mobile product. The strongest next evidence is one low-cost Android test, one small GGUF model benchmark, and a short screen recording showing airplane-mode search.
