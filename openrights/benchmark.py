from __future__ import annotations

import json
import resource
import time
from pathlib import Path

from .rag import TfidfIndex


def run(root: Path, rounds: int = 100) -> dict:
    index = TfidfIndex.load(root / "data/processed/index.json")
    questions = ["What is the federal minimum wage?", "How do I recognize a phishing scam?", "What makes an advertisement deceptive?"]
    started = time.perf_counter()
    for number in range(rounds):
        index.search(questions[number % len(questions)], 5)
    elapsed = time.perf_counter() - started
    return {"mode": "retrieval-only", "rounds": rounds, "chunks": len(index.chunks), "total_seconds": round(elapsed, 4), "average_ms": round(elapsed * 1000 / rounds, 3), "max_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2)}


def save(root: Path, result: dict) -> None:
    target = root / "benchmarks/latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
