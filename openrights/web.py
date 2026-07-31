from __future__ import annotations

import json
from pathlib import Path

from .rag import TfidfIndex


def export_web(root: Path) -> int:
    index_path = root / "data/processed/index.json"
    if not index_path.exists():
        raise SystemExit("Index not found. Run: python -m openrights ingest")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    target = root / "app/data/index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"idf": payload["idf"], "chunks": payload["chunks"]}, separators=(",", ":")), encoding="utf-8")
    return len(payload["chunks"])
