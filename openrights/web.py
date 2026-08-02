from __future__ import annotations

import json
from pathlib import Path

WEB_KEYS = ("id", "source", "url", "text", "kind")
# Present only on plain-language answers, absent on raw statute passages.
WEB_OPTIONAL_KEYS = ("heading", "statute")


def payload_for_web(payload: dict) -> dict:
    """Drop the training-time vectors: the browser recomputes them from text."""
    chunks = []
    for chunk in payload["chunks"]:
        item = {key: chunk[key] for key in WEB_KEYS if key in chunk}
        item.update({key: chunk[key] for key in WEB_OPTIONAL_KEYS if key in chunk})
        chunks.append(item)
    return {"idf": payload["idf"], "chunks": chunks}


def load_index_payload(root: Path) -> dict:
    index_path = root / "data/processed/index.json"
    if not index_path.exists():
        raise SystemExit("Index not found. Run: python -m openrights ingest")
    return json.loads(index_path.read_text(encoding="utf-8"))


def index_script(payload: dict) -> str:
    """A script assignment, not JSON.

    A WebView opened at file:///android_asset/ cannot fetch() a sibling file:
    that request is a cross-origin request to the opaque file origin and is
    blocked. A <script> tag has no such restriction, so the offline archive is
    shipped as an assignment to a global.
    """
    data = json.dumps(payload_for_web(payload), separators=(",", ":"))
    return f"window.OPENRIGHTS_INDEX={data};\n"


def export_web(root: Path) -> tuple[int, int]:
    payload = load_index_payload(root)
    target = root / "app/data/index.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    script = index_script(payload)
    target.write_text(script, encoding="utf-8")
    stale = root / "app/data/index.json"
    if stale.exists():
        stale.unlink()
    return len(payload["chunks"]), len(script.encode("utf-8"))
