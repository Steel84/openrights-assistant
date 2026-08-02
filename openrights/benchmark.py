from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from .rag import TfidfIndex

QUESTIONS = [
    "What is the federal minimum wage?",
    "How do I recognize a phishing scam?",
    "What makes an advertisement deceptive?",
]


def resident_mb() -> float | None:
    """Current resident set size (Linux/macOS only; returns None on Windows)."""
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            process = kernel32.GetCurrentProcess()

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(pmc)
            psapi = ctypes.windll.psapi
            if psapi.GetProcessMemoryInfo(process, ctypes.byref(pmc), pmc.cb):
                return round(pmc.WorkingSetSize / (1024 * 1024), 2)
        except Exception:
            pass
        return None

    # Linux: read from /proc
    try:
        page_size_mb = 4096 / (1024 * 1024)
        pages = int(Path("/proc/self/statm").read_text().split()[1])
        return round(pages * page_size_mb, 2)
    except (OSError, IndexError, ValueError):
        return None


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
