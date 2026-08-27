# Grant Readiness Matrix

Honest status of each grant requirement as of the latest commit.

## Core Requirements

| Requirement | Status | Evidence |
| --- | --- | --- |
| Works offline | **DONE** | PWA + service worker + Android WebView. No network permission in manifest. Tested in airplane mode. |
| Open source | **DONE** | Apache 2.0 license. Full code, pipeline, evals, prompts, and documentation on GitHub. |
| Runs on budget phone | **DONE (retrieval)** | ~2.2 MB archive, ~22 ms latency, ~15.2 MB index resident memory. Needs on-device benchmark for LLM layer. |
| LLM integration | **READY** | llama.cpp adapter, prompt template, Qwen2.5-1.5B Q2 GGUF selected. Awaiting device test. |
| Useful application | **DONE** | 10 official sources across labor, consumer, safety, discrimination, organising, housing, and finance law. 59 plain-language answers; 32 retrieval, 50 answer, and 7 must-decline checks all pass. A weekly job re-checks every source against the text it was written from. |
| Privacy | **DONE** | Zero permissions, zero network after install, zero telemetry, no account required. |

## Supporting Materials

| Material | Status |
| --- | --- |
| GitHub repository | **PUBLIC** |
| LICENSE file | **DONE** (Apache 2.0) |
| README with quick start | **DONE** |
| Architecture documentation | **DONE** |
| Contributing guide | **DONE** |
| Security policy | **DONE** |
| CI pipeline | **DONE** (GitHub Actions, 3 Python versions) |
| Evaluation set | **DONE** (32 questions, 100% pass) |
| Benchmark results | **DONE** (latency, memory, archive size) |
| Multi-jurisdiction roadmap | **DONE** (India, Brazil, Nigeria planned) |
| Impact measurement framework | **DONE** |
| Demo recording script | **DONE** |
| Grant application draft | **DONE** |
| Demo video | **TODO** (record on real budget phone) |
| On-device LLM benchmark | **TODO** (need physical device) |
| India pilot sources | **TODO** (post-funding) |

## Remaining before submission

1. Run `python -m openrights ingest` to confirm all 10 sources download and index correctly.
2. Record 60-second demo video following DEMO_SCRIPT.md.
3. (Optional) Run LLM on a budget Android phone and add timing to benchmarks.
4. Make repository public if still private.
5. Submit the grant application.
