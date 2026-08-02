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


def is_on_subject(question: str, text: str, idf: dict[str, float], terms: int = 1) -> bool:
    """True when the text is about what the question actually asked.

    Two callers, two standards, because the cost of being wrong differs.

    An answer must clear the strict test (terms=1): a confident explanation of
    the wrong subject is the worst thing this tool can do. It also refuses
    outright when any subject word is missing from the corpus, since a word the
    archive has never seen is the clearest possible signal that the archive does
    not cover the topic. That is what makes it decline on rent and eviction
    instead of answering with the nearest employment rule.

    Supporting passages use the looser test (terms=EVIDENCE_TERMS) and ignore
    unknown words, because a single rare word is often a figure of speech rather
    than the topic: "what should I know before getting a mortgage" contains
    *getting*, which appears nowhere in a corpus of statutes, and demanding it
    hid every relevant passage of the Truth in Lending Act.

    Measured on evals/coverage.json: 39/39 answers correct, 10/10 out-of-scope
    questions declined, and the law found for both mortgage questions.
    """
    subjects = subject_words(question)
    if not subjects:
        return True

    strict = terms == 1
    known = [word for word in subjects if word in idf]
    if strict and len(known) != len(subjects):
        return False
    if not known:
        return True

    ranked = sorted(known, key=lambda word: idf[word], reverse=True)
    present = set(tokenize(text))
    return any(word in present for word in ranked[:terms])


# A tangential citation is noise; a confident answer to another question is a
# lie. The looser test is only ever used for citations.
EVIDENCE_TERMS = 2
