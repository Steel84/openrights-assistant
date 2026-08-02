# OpenRights Assistant

[![CI](https://github.com/Steel84/openrights-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Steel84/openrights-assistant/actions)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org)
[![Offline](https://img.shields.io/badge/works-offline-brightgreen.svg)](#)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-orange.svg)](#)

An offline-first legal information assistant that searches official public law on your phone. No internet needed. No account. No server.

---

## What it does

You ask a plain-language question about your rights. The app searches 300+ passages from 10 official U.S. government sources and shows you the exact legal text that answers your question, with a link to verify it yourself.

**Example:**
```
$ python -m openrights ask "Can my employer require overtime?"

[1] Fair Labor Standards Act | score=0.4821
For a workweek longer than forty hours, the employee shall be compensated
at a rate not less than one and one-half times the regular rate...
Source: https://www.govinfo.gov/content/pkg/USCODE-2023-title29/...
```

## Key features

- **Fully offline** after a one-time source download
- **Zero dependencies** beyond Python standard library
- **10 official sources**: labor law, consumer protection, workplace safety, discrimination, organising, housing, finance
- **59 plain-language answers** across wages, dismissal, leave, safety, debt, credit, discrimination, organising, and housing
- **32 retrieval checks, 50 answer checks, and 7 must-decline checks**, run on every commit
- **Mobile-ready**: PWA with service worker + Android WebView APK
- **< 4ms** average query latency
- **< 500 KB** phone archive size
- **Optional local LLM** via llama.cpp for plain-language summaries
- **Apache 2.0** licensed

## Quick start

```bash
git clone https://github.com/Steel84/openrights-assistant.git
cd openrights-assistant
python -m pip install -e .
python -m openrights ingest        # download official sources, build index
python -m openrights ask "What is the minimum wage?"
python -m openrights evaluate       # 32 retrieval checks
python -m openrights coverage       # 50 answer checks + 7 must-decline checks
python -m openrights benchmark      # measure latency and memory
```

## Try it on your phone

```bash
python -m openrights serve          # prints a LAN address
```

Open the printed address on your phone (same Wi-Fi), install from browser menu, then switch to airplane mode. It still works.

Or build a single offline HTML file: `python -m openrights bundle`

For a native Android APK: see [RUNNING.md](RUNNING.md).

## Sources

| Source | Domain |
| --- | --- |
| Fair Labor Standards Act | Labor/wages |
| FMLA | Family/medical leave |
| OSHA Workers' Rights | Workplace safety |
| EEOC Discrimination Types | Employment discrimination |
| FTC Phishing Guide | Consumer protection |
| FTC Advertising Basics | Consumer protection |
| FTC Debt Collection FAQs | Consumer protection |
| CFPB Mortgages | Consumer finance |

## Commands

| Command | What it does |
| --- | --- |
| `ingest` | Download sources and build the search index |
| `ask "..."` | Search for relevant passages |
| `ask --model path.gguf "..."` | Search + generate answer with local LLM |
| `evaluate` | Check that the right source is retrieved |
| `coverage` | Check that a question reaches a plain-language answer |
| `benchmark` | Measure latency, memory, archive size |
| `freshness` | Check whether any source law has changed since it was reviewed |
| `export-web` | Build phone archive in app/data/ |
| `bundle` | Build single-file demo in dist/ |
| `serve` | Serve to phone over LAN |

## Measured performance

From `python -m openrights benchmark`, on a development machine rather than a
phone. The archive grew when the plain-language answers were added.

| Metric | Value |
| --- | --- |
| Sources | 10 official government sources |
| Plain-language answers | 59 |
| Indexed statute passages | 1,144 |
| Retrieval accuracy | 32/32 |
| Answer coverage | 50/50 |
| Query latency | ~17 ms |
| Index RAM | ~13 MB |
| Phone archive | 1.8 MB |
| Install size (no model) | ~2 MB |
| External dependencies | 0 |

## Documentation

- [RUNNING.md](RUNNING.md) - How to run on phone/computer/APK
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and decisions
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to add sources and contribute
- [SECURITY.md](SECURITY.md) - Security policy and threat model
- [DEMO_SCRIPT.md](DEMO_SCRIPT.md) - Video recording guide
- [GRANT_DRAFT.md](GRANT_DRAFT.md) - Grant application
- [GRANT_READINESS.md](GRANT_READINESS.md) - Readiness checklist
- [docs/MULTI_JURISDICTION.md](docs/MULTI_JURISDICTION.md) - Expansion roadmap
- [docs/COVERAGE.md](docs/COVERAGE.md) - What the archive answers, and what it does not
- [docs/IMPACT.md](docs/IMPACT.md) - Impact measurement framework

## Roadmap

1. **DONE**: Offline retrieval, mobile interface, 8 sources, 32 evals, CI, documentation
2. **Next**: Local LLM benchmark on budget Android phone, demo video
3. **Planned**: India pilot (labor + consumer law in English/Hindi)
4. **Future**: Brazil, Nigeria, Philippines; multilingual tokenizer; community contribution pipeline

## License

Apache 2.0. See [LICENSE](LICENSE).

---

*This is not legal advice. It is a tool for finding and reading official public legal text. Always verify the current law and your specific jurisdiction.*
