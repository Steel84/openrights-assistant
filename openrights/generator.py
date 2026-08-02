from __future__ import annotations

import subprocess
from pathlib import Path


SYSTEM_PROMPT = """You are OpenRights Assistant, an offline legal information tool. You are NOT a lawyer and this is NOT legal advice.

Rules:
1. Answer ONLY from the source passages provided below. Do not use outside knowledge.
2. If the passages do not answer the question, say: "I could not find an answer in the available sources."
3. Use plain, simple English that a non-lawyer can understand.
4. Cite every factual claim with [1], [2], etc. referring to the passage numbers.
5. Mention that the user should verify the current law and their specific jurisdiction.
6. Keep answers under 150 words.
7. Never invent legal citations or statutes not present in the passages."""


def build_prompt(question: str, results: list[dict]) -> str:
    """Build a generation prompt from retrieved passages."""
    sources = "\n\n".join(
        f"[{number}] {result['source']}\n{result['text']}\nURL: {result['url']}"
        for number, result in enumerate(results, 1)
    )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Question: {question}\n\n"
        f"Source passages:\n{sources}\n\n"
        f"Answer (cite with [1], [2], etc.):"
    )


def generate(model: Path, prompt: str, llama_cli: str = "llama-cli") -> str:
    """Run local inference via llama.cpp CLI."""
    result = subprocess.run(
        [
            llama_cli,
            "-m", str(model),
            "-p", prompt,
            "-n", "256",
            "--temp", "0.2",
            "--top-p", "0.9",
            "--repeat-penalty", "1.1",
            "--no-display-prompt",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout.strip()
