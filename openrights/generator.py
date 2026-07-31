from __future__ import annotations

import subprocess
from pathlib import Path


def build_prompt(question: str, results: list[dict]) -> str:
    sources = "\n\n".join(
        f"[{number}] {result['source']}\n{result['text']}\nURL: {result['url']}"
        for number, result in enumerate(results, 1)
    )
    return (
        "You are an offline legal information assistant. This is not legal advice. "
        "Answer only from the source passages below. If they do not answer the question, say so. "
        "Use plain English and cite claims with [1], [2], etc. Mention that jurisdiction and date matter.\n\n"
        f"Question: {question}\n\nSource passages:\n{sources}\n\nAnswer:"
    )


def generate(model: Path, prompt: str, llama_cli: str = "llama-cli") -> str:
    result = subprocess.run(
        [llama_cli, "-m", str(model), "-p", prompt, "-n", "256", "--temp", "0.2", "--no-display-prompt"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
