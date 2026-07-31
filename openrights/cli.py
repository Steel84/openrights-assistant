from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ingest import ingest
from .generator import build_prompt, generate
from .benchmark import run as run_benchmark, save as save_benchmark
from .rag import TfidfIndex
from .serve import serve
from .bundle import build as build_bundle
from .web import export_web

ROOT = Path(__file__).resolve().parents[1]


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
        results = index.search(question, 3)
        ok = any(expected.lower() in result["source"].lower() for result in results)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}: {question}")
    print(f"{passed}/{len(cases)} cases passed")
    if passed != len(cases):
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="openrights")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ingest")
    subparsers.add_parser("evaluate")
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
