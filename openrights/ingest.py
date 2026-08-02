from __future__ import annotations

import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from .rag import TfidfIndex


class TextExtractor(HTMLParser):
    """Extract visible text from HTML, skipping navigation and scripts."""

    SKIP_TAGS = frozenset({"script", "style", "nav", "header", "footer", "noscript", "svg"})

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            text = re.sub(r"\s+", " ", html.unescape(data)).strip()
            if text:
                self.parts.append(text)


def fetch(url: str, target: Path) -> str:
    """Download a URL and cache the raw HTML locally."""
    request = urllib.request.Request(url, headers={"User-Agent": "openrights-assistant/0.2"})
    with urllib.request.urlopen(request, timeout=90) as response:
        content = response.read().decode("utf-8", errors="replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return content


def clean(source: str) -> str:
    """Strip HTML tags and return clean text."""
    parser = TextExtractor()
    parser.feed(source)
    return "\n".join(parser.parts)


def chunk(text: str, size: int = 450, overlap: int = 60) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    step = max(size - overlap, 1)
    return [
        " ".join(words[start : start + size])
        for start in range(0, len(words), step)
        if words[start : start + size]
    ]


def ingest(root: Path) -> int:
    """Download all sources, clean, chunk, and build the TF-IDF index."""
    sources = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    chunks: list[dict] = []
    failed: list[str] = []

    for source in sources:
        raw_path = root / "data/raw" / f"{source['id']}.html"
        try:
            raw = fetch(source["url"], raw_path)
        except Exception as exc:
            print(f"  WARNING: could not fetch {source['id']}: {exc}")
            failed.append(source["id"])
            continue

        text = clean(raw)
        if len(text.split()) < 20:
            print(f"  WARNING: {source['id']} produced very little text ({len(text.split())} words)")
            failed.append(source["id"])
            continue

        for number, chunk_text in enumerate(chunk(text)):
            chunks.append({
                "id": f"{source['id']}:{number}",
                "source": source["title"],
                "url": source["url"],
                "text": chunk_text,
                "jurisdiction": source.get("jurisdiction", "US"),
            })

    if not chunks:
        raise SystemExit("No chunks produced. Check network and source URLs.")

    TfidfIndex.build(chunks).save(root / "data/processed/index.json")

    if failed:
        print(f"  {len(failed)} source(s) failed: {', '.join(failed)}")
        print(f"  Indexed {len(chunks)} chunks from {len(sources) - len(failed)} source(s).")
    else:
        print(f"  All {len(sources)} sources indexed successfully.")

    return len(chunks)
