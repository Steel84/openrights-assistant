# Grant Application
## OpenRights Assistant: Offline Legal Information for Everyone
---
## Executive Summary
OpenRights Assistant is an offline-first, open-source application that helps people understand their legal rights by searching official public law on their phone, with no internet connection, no account, and no server cost. It retrieves exact passages from government sources and shows where each answer comes from, so users can verify the information themselves.
The prototype is live, tested, and open: 10 official U.S. legal sources, 1,399 indexed passages, 59 plain-language answers, 89 automated checks (32 retrieval + 50 answer coverage + 7 must-decline safety checks), a working mobile interface, and a clear path to multi-jurisdiction expansion.
---
## The Problem
Billions of people face legal situations every day: unpaid wages, workplace discrimination, debt collectors, unsafe conditions, deceptive advertising. The information they need is technically public, but:
- **Inaccessible**: legal text is dense, scattered across government websites, and assumes literacy in legal English.
- **Gated by connectivity**: most AI legal tools require constant internet and expensive API calls.
- **Gated by cost**: professional legal advice is expensive and inaccessible; even basic legal aid has months-long waitlists.
- **Gated by trust**: people in vulnerable situations (migrants, informal workers, minorities) avoid online tools that require accounts or may share data.
These barriers are highest in communities where connectivity is intermittent and professional legal advice is unaffordable.
---
## Our Solution
### How it works
1. **Install once** (phone archive is about 2.2 MB; optional local LLM adds model weight).
2. **Turn off the internet.** The app works in airplane mode.
3. **Ask a question** in plain language: "Can my employer require overtime?" or "How do I stop a debt collector from calling?"
4. **Get cited passages** from official law, ranked by relevance, with source URLs for verification.
5. **Optionally**: a local LLM via llama.cpp summarizes the passages in simple language with citations.
### What makes it different
| Feature | OpenRights | Typical legal AI |
| --- | --- | --- |
| Works offline | Yes, completely | No |
| Requires account | No | Yes |
| Shows exact source text | Always | Rarely |
| Runs on a budget phone | Yes (retrieval mode) | No |
| Open source | Fully (Apache 2.0) | No |
| Privacy | Zero network, zero telemetry | Data sent to servers |
| Cost per query | Zero | Recurring API fees |
---
## Technical Architecture
```
User question
 ||
 vv
[TF-IDF Retrieval] - searches 1,399 passages from 10 official sources
 ||
 vv
[Ranked results with citations and source URLs]
 || vv (optional)
[Local LLM via llama.cpp] - summarizes in plain language
 ||
 vv
[Answer with citations]
```
**Key technical decisions:**
- Zero external dependencies (Python standard library only)
- TF-IDF over embeddings: deterministic, debuggable, runs in ~22ms average on standard hardware
- Single JSON index file: no database, no vector store, fully portable
- PWA + Android WebView: one codebase for all mobile platforms
- Optional LLM: the app is useful without it; generation adds value for users who want summaries
---
## Current Status (Measured)
| Metric | Value |
| --- | --- |
| Official sources indexed | 10 |
| Indexed statute passages | 1,399 |
| Plain-language answers | 59 |
| Retrieval accuracy | 100% (32/32) |
| Answer coverage | 100% (50/50) |
| Query latency | ~22 ms average |
| Index memory footprint | ~15.2 MB |
| Phone archive size | ~2.2 MB |
| Install size (no model) | ~2.2 MB |
| CI pipeline | GitHub Actions |
| License | Apache 2.0 |
| External runtime dependencies | Zero |
---
## Sources Currently Indexed
1. Fair Labor Standards Act (wages, overtime, child labor)
2. Family and Medical Leave Act (FMLA)
3. Occupational Safety and Health Act (OSHA Workers' Rights)
4. EEOC Discrimination Types (employment discrimination)
5. FTC Phishing Guide (consumer protection)
6. FTC Advertising and Marketing Basics (consumer protection)
7. FTC Debt Collection FAQs (consumer protection)
8. CFPB Mortgages (consumer finance)
9. National Labor Relations Act - U.S. Code Title 29, Chapter 7 (right to organise, collective bargaining, concerted activity)
10. Fair Housing Act - U.S. Code Title 42, Chapter 45 (housing discrimination, familial status, disability accommodation)
*(See [docs/COVERAGE.md](docs/COVERAGE.md) for the full, current source manifest.)*
---
## Roadmap
### Phase 1: Foundation (COMPLETE)
- [x] Offline retrieval pipeline with 10 official sources
- [x] Mobile PWA with service worker caching
- [x] Android WebView packaging
- [x] 89 automated checks (retrieval, answer coverage, must-decline safety), 100% pass rate
- [x] Automated CI pipeline
- [x] Open source with Apache 2.0
- [x] Architecture and contribution documentation
- [x] Demo recording in airplane mode
### Phase 2: On-Device Inference Upgrade (post-funding)
- [ ] Integrate QVAC as the on-device inference backend, replacing the current generic llama.cpp call
- [ ] Benchmark latency, RAM, and battery impact on budget Android devices
- [ ] Add citation accuracy evaluation (generated answer vs. source passages)
- [ ] Publish reproducible on-device benchmarks
### Phase 3: India Pilot
- [ ] Add Indian labour law sources (2025 Labour Codes)
- [ ] Hindi interface option
- [ ] Partner with legal aid organization for user testing
- [ ] Publish first impact report
### Phase 4: Multi-Jurisdiction Expansion
- [ ] Add Brazil (CLT/CDC in Portuguese) and Nigeria (Labour Act in English)
- [ ] Multilingual tokenizer for Devanagari and other scripts
- [ ] Community contribution pipeline: anyone can submit a source + eval questions
- [ ] Reproducible benchmarks on multiple budget phones
---
## Alignment with Tether / QVAC
OpenRights Assistant already implements the architecture QVAC is built around: **local-first, zero-cloud, zero-custodian AI**. There is no server, no API key, no account, and no telemetry — the tool works fully offline, on-device, indefinitely.
| Criterion | How we meet it |
| --- | --- |
| Local-first / offline-first | 100% offline after install |
| No cloud dependency | Zero network calls, zero external APIs |
| Open source | Full repo, Apache 2.0, open evals |
| Low-resource hardware | ~22ms latency, ~2.2 MB archive |
| On-device LLM | Currently llama.cpp; migrating to QVAC |
| Real-world utility | Labor rights, consumer protection, discrimination law |
| Global scope | Multi-jurisdiction architecture; India pilot planned |
| Privacy | Zero telemetry, zero permissions, zero network |
---
## What Grant Funding Would Enable
- **QVAC integration**: replace the current generic llama.cpp call with QVAC as the on-device inference backend, and benchmark the result against the current implementation.
- **Budget Android devices** for real-world testing on hardware target users actually own (Redmi, Samsung A-series, Nokia budget line).
- **India pilot logistics**: legal text acquisition, Hindi translation verification, community outreach with legal aid organizations.
- **Multi-jurisdiction ingestion pipeline**: generalizing the source/eval pipeline beyond U.S. law.
- **Sustained open-source maintenance**: keeping sources fresh, expanding the evaluation set, supporting community contributors.
The core architecture is already built and tested. Funding accelerates the QVAC migration and multi-jurisdiction expansion, not initial development.
---
## Team
Solo developer with experience in full-stack development, mobile applications, and information retrieval systems. The project is designed for community contribution: adding a new jurisdiction requires only a source manifest and evaluation questions, not deep technical expertise.
---
## Risks and Mitigations
| Risk | Mitigation |
| --- | --- |
| Legal text changes | Versioned source manifest; freshness check in CI |
| Users treat output as legal advice | Prominent disclaimers; always show source text for verification |
| Model hallucination | Generation is optional; retrieval-only mode shows verbatim source |
| Low adoption | Start with community partners (legal aid orgs) not app stores |
| Tokenizer fails on non-Latin scripts | Character n-gram fallback planned for Phase 4 |
---
## Links
- **Repository**: https://github.com/Steel84/openrights-assistant
- **License**: Apache 2.0
- **CI**: GitHub Actions
---
*This project has no venture funding, no token, and no revenue model. It exists to make legal information accessible to people who need it most.*
