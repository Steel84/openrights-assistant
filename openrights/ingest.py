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


def chunk(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    step = max(size - overlap, 1)
    chunks = []
    for start in range(0, len(words), step):
        segment = words[start : start + size]
        if not segment:
            continue
        joined = " ".join(segment)
        # Skip chunks that are mostly legal citations, amendment history, or procedural
        noise_markers = ("Pub.", "Stat.", "Subsec.", "subsec.", "par.", "subpar.", "§", "sect.", "Amdt.")
        noise_count = sum(1 for w in segment if w in noise_markers or w.startswith("§"))
        # Also count patterns like "L. 89-601" as noise
        text_check = joined.lower()
        pub_l_count = text_check.count("pub. l.") + text_check.count("stat.")
        if noise_count > len(segment) * 0.05 or pub_l_count > 3:
            continue
        chunks.append(joined)
    return chunks


# Each plain-language file is a set of "## question" sections. One section is one
# answer, so a search hit is a whole thought rather than a slice cutting across
# unrelated topics.
PLAIN_SOURCES = {
    "flsa": (
        "Wages and overtime",
        "Fair Labor Standards Act",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title29/html/USCODE-2023-title29-chap8.htm",
    ),
    "fmla": (
        "Family and medical leave",
        "Family and Medical Leave Act",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title29/html/USCODE-2023-title29-chap28.htm",
    ),
    "osha": (
        "Workplace safety",
        "Occupational Safety and Health Act",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title29/html/USCODE-2023-title29-chap15.htm",
    ),
    "debt": (
        "Debt collection",
        "Fair Debt Collection Practices Act",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title15/html/USCODE-2023-title15-chap41-subchapV.htm",
    ),
    "discrimination": (
        "Workplace discrimination",
        "Civil Rights Act Title VII",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap21-subchapVI.htm",
    ),
}


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split a plain-language file into (heading, body) pairs."""
    sections: list[tuple[str, str]] = []
    heading = None
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if heading:
                sections.append((heading, "\n".join(body).strip()))
            heading = line[3:].strip()
            body = []
        elif heading:
            body.append(line)
    if heading:
        sections.append((heading, "\n".join(body).strip()))
    return [(h, b) for h, b in sections if b]


def load_plain_answers(root: Path) -> list[dict]:
    directory = root / "data/curated"
    if not directory.exists():
        return []
    answers: list[dict] = []
    for path in sorted(directory.glob("*.md")):
        topic, statute, url = PLAIN_SOURCES.get(
            path.stem, (path.stem.title(), path.stem.upper(), "")
        )
        for number, (heading, body) in enumerate(split_sections(path.read_text(encoding="utf-8"))):
            answers.append({
                "id": f"plain-{path.stem}:{number}",
                "source": topic,
                "statute": statute,
                "heading": heading,
                "url": url,
                # The heading is indexed with the body: users search in the words
                # of the question they are asking, not the words of the statute.
                "text": f"{heading}\n\n{body}",
                "jurisdiction": "US",
                "kind": "plain",
            })
    if answers:
        print(f"  Loaded {len(answers)} plain-language answers.")
    return answers


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
                "kind": "law",
            })

    chunks.extend(load_plain_answers(root))

    if not chunks:
        raise SystemExit("No chunks produced. Check network and source URLs.")

    TfidfIndex.build(chunks).save(root / "data/processed/index.json")

    if failed:
        print(f"  {len(failed)} source(s) failed: {', '.join(failed)}")
        print(f"  Indexed {len(chunks)} chunks from {len(sources) - len(failed)} source(s).")
    else:
        print(f"  All {len(sources)} sources indexed successfully.")

    return len(chunks)
