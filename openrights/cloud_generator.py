"""Cloud LLM backends (Gemini, Qwen) as optional online mode.

Zero external dependencies - uses only urllib from stdlib.
Falls back gracefully if network is unavailable.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error

from .generator import build_prompt


def generate_gemini(prompt: str, api_key: str | None = None) -> str:
    """Generate via Google Gemini 3.5 Flash API (free tier: 15 RPM)."""
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set. Get one at https://aistudio.google.com/apikey")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={key}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 300,
        },
    }).encode()

    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def generate_qwen(prompt: str, api_key: str | None = None) -> str:
    """Generate via Qwen API (DashScope compatible endpoint)."""
    key = api_key or os.environ.get("QWEN_API_KEY", "")
    if not key:
        raise RuntimeError("QWEN_API_KEY not set. Get one at https://dashscope.console.aliyun.com/")

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    payload = json.dumps({
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 300,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    return data["choices"][0]["message"]["content"].strip()


PROVIDERS = {
    "gemini": generate_gemini,
    "qwen": generate_qwen,
}


def generate_cloud(
    provider: str, question: str, results: list[dict], **kwargs
) -> str:
    """Unified cloud generation with automatic fallback message."""
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Available: {list(PROVIDERS)}")

    prompt = build_prompt(question, results)

    try:
        return PROVIDERS[provider](prompt, **kwargs)
    except (urllib.error.URLError, OSError) as e:
        return f"[Cloud unavailable: {e}. Use --model for offline LLM mode.]"
    except RuntimeError as e:
        return str(e)
