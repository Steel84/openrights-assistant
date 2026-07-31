from __future__ import annotations

import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from .rag import TfidfIndex


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "header", "footer", "noscript"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "header", "footer", "noscript"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            text = re.sub(r"\s+", " ", html.unescape(data)).strip()
            if text:
                self.parts.append(text)


def fetch(url: str, target: Path) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "openrights-assistant/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read().decode("utf-8", errors="replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return content


def clean(source: str) -> str:
    parser = TextExtractor()
    parser.feed(source)
    return "\n".join(parser.parts)


def chunk(text: str, size: int = 450, overlap: int = 60) -> list[str]:
    words = text.split()
    step = max(size - overlap, 1)
    return [" ".join(words[start : start + size]) for start in range(0, len(words), step) if words[start : start + size]]


def ingest(root: Path) -> int:
    sources = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    chunks: list[dict] = []
    for source in sources:
        raw_path = root / "data/raw" / f"{source['id']}.html"
        raw = fetch(source["url"], raw_path)
        for number, text in enumerate(chunk(clean(raw))):
            chunks.append({"id": f"{source['id']}:{number}", "source": source["title"], "url": source["url"], "text": text})
    TfidfIndex.build(chunks).save(root / "data/processed/index.json")
    return len(chunks)
