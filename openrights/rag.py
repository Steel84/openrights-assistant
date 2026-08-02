from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]{1,}")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class TfidfIndex:
    def __init__(self, chunks: list[dict], idf: dict[str, float]):
        self.chunks = chunks
        self.idf = idf

    @classmethod
    def build(cls, chunks: list[dict]) -> "TfidfIndex":
        document_frequency = Counter()
        for chunk in chunks:
            document_frequency.update(set(tokenize(chunk["text"])))
        total = max(len(chunks), 1)
        idf = {term: math.log((total + 1) / (frequency + 1)) + 1 for term, frequency in document_frequency.items()}
        for chunk in chunks:
            chunk["vector"] = cls._vector(chunk["text"], idf)
        return cls(chunks, idf)

    @staticmethod
    def _vector(text: str, idf: dict[str, float]) -> dict[str, float]:
        counts = Counter(tokenize(text))
        length = sum(counts.values()) or 1
        return {term: (count / length) * idf[term] for term, count in counts.items() if term in idf}

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        query = self._vector(question, self.idf)
        query_norm = math.sqrt(sum(value * value for value in query.values())) or 1
        results = []
        for chunk in self.chunks:
            vector = chunk.get("vector", {})
            denominator = query_norm * (math.sqrt(sum(value * value for value in vector.values())) or 1)
            score = sum(query.get(term, 0) * value for term, value in vector.items()) / denominator
            results.append((score, chunk))
        return [dict(chunk, score=round(score, 4)) for score, chunk in sorted(results, reverse=True, key=lambda item: item[0])[:top_k]]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"idf": self.idf, "chunks": self.chunks}, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "TfidfIndex":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload["chunks"], payload["idf"])

# Cosine similarity rewards sentence shape. "Can my landlord raise the rent?"
# scored 0.63 against "Can my employer change my schedule?" on "can my" alone,
# while landlord and rent appeared nowhere in the answer. A confident answer to
# a question about something else is the worst failure this tool can have, so
# the subject of the question has to actually be in the answer.
GENERIC_WORDS = frozenset("""what when where which while about have does can the are from with without and get how been being same other their there they this that these those your not all any some more most much many into over under than then such only own just also need want should would could will shall""".split())


def subject_words(question: str) -> list[str]:
    """The words that carry what the question is about."""
    return [t for t in tokenize(question) if len(t) >= 4 and t not in GENERIC_WORDS]


def is_on_subject(question: str, text: str, idf: dict[str, float]) -> bool:
    """True when the answer mentions the rarest thing the question asked about."""
    subjects = subject_words(question)
    if not subjects:
        return True
    rarest = max(subjects, key=lambda word: idf.get(word, float("inf")))
    return rarest in set(tokenize(text))
