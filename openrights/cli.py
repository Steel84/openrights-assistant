from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ingest import ingest
from .generator import build_prompt, generate
from .benchmark import run as run_benchmark, save as save_benchmark
from .rag import TfidfIndex, is_on_subject
from .serve import serve
from .bundle import build as build_bundle
from .web import export_web

ROOT = Path(__file__).resolve().parents[1]

# Below this similarity a plain-language answer is not about the same
# subject as the question. Measured: correct answers score 0.36 and up,
# unrelated ones 0.33 and below.
ANSWER_FLOOR = 0.35


def ask(question: str, top_k: int, model: str | None) -> None:
    index = TfidfIndex.load(ROOT / "data/processed/index.json")
    results = index.search(question, top_k)
    if model:
        print(generate(Path(model), build_prompt(question, results)))
        return
    print("\nRetrieval-only answer (verify the source and jurisdiction):\n")
    for number, result in enumerate(results, 1):
        print(f"[{number}] {result['source']} | score={result['score']}")
        print(result["text"])
        print(f"Source: {result['url']}\n")


def evaluate() -> None:
    index = TfidfIndex.load(ROOT / "data/processed/index.json")
    cases = json.loads((ROOT / "evals/questions.json").read_text(encoding="utf-8"))
    passed = 0
    for case in cases:
        question = case["question"]
        expected = case["expected_source"]
        # Score what the interface would actually present. An off-subject
        # plain-language answer is filtered out before display, so counting it
        # here would measure the index rather than the product.
        results = [
            r
            for r in index.search(question, 8)
            if r.get("kind") != "plain" or is_on_subject(question, r["text"], index.idf)
        ][:3]
        # A plain-language answer is filed under its topic ("Wages and
        # overtime") but names the statute it summarises. Either satisfies an
        # expectation of that statute: the answer does come from that law.
        ok = any(
            expected.lower() in result["source"].lower()
            or expected.lower() in result.get("statute", "").lower()
            for result in results
        )
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}: {question}")
    print(f"{passed}/{len(cases)} cases passed")
    if passed != len(cases):
        raise SystemExit(1)


def coverage() -> None:
    """Check that questions reach the right answer, and that others reach none.

    `evaluate` asks whether the right source was retrieved. That passes even
    when the user is handed raw statute text, and it passes when a confident
    answer about wages is served to someone asking about rent. Both halves
    matter: an answer to the wrong question is worse than no answer, because it
    looks authoritative.
    """
    index = TfidfIndex.load(ROOT / "data/processed/index.json")
    cases = json.loads((ROOT / "evals/coverage.json").read_text(encoding="utf-8"))

    def best_answer(question: str) -> dict | None:
        results = index.search(question, 14)
        return next(
            (
                r
                for r in results
                if r.get("kind") == "plain"
                and r["score"] >= ANSWER_FLOOR
                and is_on_subject(question, r["text"], index.idf)
            ),
            None,
        )

    failures = 0
    covered = cases["covered"]
    for case in covered:
        answer = best_answer(case["question"])
        heading = (answer or {}).get("heading")
        ok = heading == case["expected_heading"]
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}: {case['question']}")
        if not ok:
            print(f"      got: {heading or 'no answer'}")
    print(f"{len(covered) - failures}/{len(covered)} questions reach the right answer")

    not_covered = cases["not_covered"]
    wrong = 0
    print()
    for question in not_covered:
        answer = best_answer(question)
        ok = answer is None
        wrong += not ok
        print(f"{'PASS' if ok else 'WARN'}: {question}")
        if not ok:
            print(f"      answered anyway: {answer['heading']} ({answer['score']})")
    print(f"{len(not_covered) - wrong}/{len(not_covered)} uncovered questions correctly decline to answer")
    if wrong:
        print(f"{wrong} known false positive(s); see docs/COVERAGE.md")

    if failures:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="openrights")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ingest")
    subparsers.add_parser("evaluate")
    subparsers.add_parser("coverage")
    subparsers.add_parser("export-web")
    subparsers.add_parser("benchmark")
    subparsers.add_parser("bundle")
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--port", type=int, default=8000)
    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--top-k", type=int, default=5)
    ask_parser.add_argument("--model", help="Path to a GGUF model used by llama-cli")
    args = parser.parse_args()
    if args.command == "ingest":
        print(f"Indexed {ingest(ROOT)} chunks.")
    elif args.command == "evaluate":
        evaluate()
    elif args.command == "coverage":
        coverage()
    elif args.command == "export-web":
        chunks, size = export_web(ROOT)
        print(f"Exported {chunks} chunks to app/data/index.js ({size / 1024:.0f} KB).")
    elif args.command == "bundle":
        target, size = build_bundle(ROOT)
        print(f"Wrote {target.relative_to(ROOT)} ({size / 1024:.0f} KB). Open it in any browser, online or offline.")
    elif args.command == "serve":
        serve(ROOT, args.port)
    elif args.command == "benchmark":
        result = run_benchmark(ROOT)
        save_benchmark(ROOT, result)
        print(json.dumps(result, indent=2))
    elif args.command == "ask":
        ask(args.question, args.top_k, args.model)


if __name__ == "__main__":
    main()
