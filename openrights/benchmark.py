from __future__ import annotations

import json
import resource
import time
from pathlib import Path

from .rag import TfidfIndex

QUESTIONS = [
    "What is the federal minimum wage?",
    "How do I recognize a phishing scam?",
    "What makes an advertisement deceptive?",
]

PAGE_SIZE_MB = 4096 / (1024 * 1024)


def resident_mb() -> float | None:
    """Current resident set size.

    Peak RSS (ru_maxrss) is useless here: the host interpreter can start with a
    large peak already recorded, which would be reported as the app's cost. The
    delta of current RSS across loading the index is the honest number.
    """
    try:
        pages = int(Path("/proc/self/statm").read_text().split()[1])
    except (OSError, IndexError, ValueError):
        return None
    return round(pages * PAGE_SIZE_MB, 2)


def run(root: Path, rounds: int = 100) -> dict:
    index_path = root / "data/processed/index.json"
    before = resident_mb()
    index = TfidfIndex.load(index_path)
    after = resident_mb()

    started = time.perf_counter()
    for number in range(rounds):
        index.search(QUESTIONS[number % len(QUESTIONS)], 5)
    elapsed = time.perf_counter() - started

    result = {
        "mode": "retrieval-only",
        "rounds": rounds,
        "chunks": len(index.chunks),
        "total_seconds": round(elapsed, 4),
        "average_ms": round(elapsed * 1000 / rounds, 3),
        "index_file_kb": round(index_path.stat().st_size / 1024, 1),
        "phone_archive_kb": round((root / "app/data/index.js").stat().st_size / 1024, 1) if (root / "app/data/index.js").exists() else None,
    }
    if before is not None and after is not None:
        result["index_resident_mb"] = round(after - before, 2)
        result["process_resident_mb"] = after
    result["note"] = "Retrieval only; no LLM loaded. Measured on the dev machine, not on a phone."
    return result


def save(root: Path, result: dict) -> None:
    target = root / "benchmarks/latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
