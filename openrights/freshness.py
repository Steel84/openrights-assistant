"""Detect when the law behind an answer has changed.

A hand-written summary of a statute is correct on the day it is written and
decays silently after that. Nothing in the archive would show it: the answer
still reads well, still cites a real source, and is simply out of date. That is
the worst failure this project can have, because it looks exactly like success.

This compares the current text of each source against a recorded fingerprint
and names the answers that depend on anything that moved.

The fingerprint is taken over the *cleaned* text, not the HTML. Government
pages regenerate constantly with unchanged content: banners, session ids, build
timestamps. Hashing the raw response would cry wolf every week, and a monitor
that cries wolf is one people learn to ignore.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .ingest import PLAIN_SOURCES, clean, fetch, split_sections

MANIFEST = "data/freshness.json"


def fingerprint(text: str) -> str:
    """Hash of the cleaned text, whitespace normalised."""
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]


def answers_by_statute(root: Path) -> dict[str, list[str]]:
    """Which answers rest on which statute, so a change names its casualties."""
    directory = root / "data/curated"
    mapping: dict[str, list[str]] = {}
    if not directory.exists():
        return mapping
    for path in sorted(directory.glob("*.md")):
        _, statute, _ = PLAIN_SOURCES.get(path.stem, ("", "", ""))
        if not statute:
            continue
        headings = [h for h, _, _ in split_sections(path.read_text(encoding="utf-8"))]
        mapping.setdefault(statute, []).extend(headings)
    return mapping


def statute_for_source(title: str) -> str:
    """Match a source title to the statute name used by the answers."""
    for _, (_, statute, _) in PLAIN_SOURCES.items():
        if statute.lower() in title.lower():
            return statute
    return ""


def check(root: Path, update: bool = False) -> dict:
    sources = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    manifest_path = root / MANIFEST
    previous = {}
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8")).get("sources", {})

    dependants = answers_by_statute(root)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    current: dict[str, dict] = {}
    changed: list[dict] = []
    unreachable: list[str] = []

    for source in sources:
        source_id = source["id"]
        try:
            raw = fetch(source["url"], root / "data/raw" / f"{source_id}.html")
        except Exception as error:  # network, 403, DNS: all mean "cannot verify"
            unreachable.append(source_id)
            # Keep the old fingerprint. Dropping it would silently mark the
            # source fresh on the next successful run, hiding a real change.
            if source_id in previous:
                current[source_id] = {**previous[source_id], "error": str(error)[:120]}
            continue

        digest = fingerprint(clean(raw))
        before = previous.get(source_id, {})
        record = {
            "title": source["title"],
            "fingerprint": digest,
            "checked": now,
            "verified": before.get("verified", now),
        }

        if before.get("fingerprint") and before["fingerprint"] != digest:
            statute = statute_for_source(source["title"])
            changed.append({
                "id": source_id,
                "title": source["title"],
                "was": before["fingerprint"],
                "now": digest,
                "verified": before.get("verified", "unknown"),
                "answers": dependants.get(statute, []),
            })
            record["verified"] = before.get("verified", now)
        elif update:
            record["verified"] = now

        current[source_id] = record

    if update or not manifest_path.exists():
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps({"updated": now, "sources": current}, indent=2) + "\n",
            encoding="utf-8",
        )

    return {
        "checked": len(sources),
        "changed": changed,
        "unreachable": unreachable,
        "first_run": not previous,
    }


def report(result: dict) -> int:
    """Print the result. Returns the exit code: non-zero when review is due."""
    if result["first_run"]:
        print(f"Recorded fingerprints for {result['checked']} sources. Nothing to compare yet.")
        return 0

    for source_id in result["unreachable"]:
        print(f"UNREACHABLE: {source_id} (kept the previous fingerprint)")

    if not result["changed"]:
        print(f"{result['checked']} sources checked, none changed.")
        return 1 if result["unreachable"] else 0

    print(f"{len(result['changed'])} of {result['checked']} sources changed.\n")
    for item in result["changed"]:
        print(f"CHANGED: {item['title']}")
        print(f"  last verified: {item['verified']}")
        if item["answers"]:
            print(f"  {len(item['answers'])} answers to re-read:")
            for heading in item["answers"]:
                print(f"    - {heading}")
        else:
            print("  no plain-language answers depend on it")
        print()
    print("Re-read the answers above against the current text, then run:")
    print("  python -m openrights freshness --accept")
    return 2
