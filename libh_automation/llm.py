from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

from libh_automation.models import ArticleChunk, ArticleData, ArticleGuess

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system.txt"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _excerpt_from_abstract(abstract: str) -> str:
    text = abstract.strip()
    if len(text) <= 500:
        return text
    return text[:500].rsplit(" ", 1)[0]


def guess_to_article_data(guess: ArticleGuess) -> dict:
    status = "ok"
    issues = list(guess.parser_warnings)
    if any("different topics" in w.lower() for w in guess.parser_warnings):
        status = "needs_review"
    if not guess.title or not guess.authors or not guess.abstract or not guess.doi:
        status = "reject"
        issues.append("Missing required parser fields")
    if None in (guess.year, guess.volume, guess.issue, guess.first_page, guess.last_page):
        status = "reject"
        issues.append("Missing bibliographic numbers")
    return {
        "validation_status": status,
        "issues": issues,
        "title": guess.title,
        "excerpt": _excerpt_from_abstract(guess.abstract),
        "year": guess.year or 0,
        "volume": guess.volume or 0,
        "issue": guess.issue or 0,
        "first_page": guess.first_page or 0,
        "last_page": guess.last_page or 0,
        "doi": guess.doi,
        "authors": [a.model_dump() for a in guess.authors],
        "abstract": guess.abstract,
        "keywords": guess.keywords,
        "print_issn": guess.print_issn or "0024-2292",
        "online_issn": guess.online_issn or "0976-2469",
    }


def build_user_message(chunk: ArticleChunk) -> str:
    payload = {
        "issue_header": chunk.issue_header,
        "raw_text": chunk.raw_text,
        "parser_guess": chunk.guess.model_dump(),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


class OllamaClient:
    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: float = 180.0,
    ) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.timeout = timeout
        self.system_prompt = load_system_prompt()

    def complete_article(self, chunk: ArticleChunk) -> dict:
        url = f"{self.host}/api/chat"
        body = {
            "model": self.model,
            "format": "json",
            "stream": False,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": build_user_message(chunk)},
            ],
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=body)
            response.raise_for_status()
            data = response.json()
        content = data.get("message", {}).get("content", "")
        return json.loads(content)


def process_chunks(
    chunks: list[ArticleChunk],
    *,
    skip_llm: bool = False,
    client: OllamaClient | None = None,
) -> list[dict]:
    results: list[dict] = []
    llm = None if skip_llm else (client or OllamaClient())
    for chunk in chunks:
        if skip_llm:
            results.append(guess_to_article_data(chunk.guess))
            continue
        try:
            results.append(llm.complete_article(chunk))
        except Exception as exc:  # noqa: BLE001 — keep pipeline going per article
            fallback = guess_to_article_data(chunk.guess)
            fallback["validation_status"] = "needs_review"
            fallback["issues"] = list(fallback.get("issues") or []) + [f"LLM error: {exc}"]
            results.append(fallback)
    return results


def parse_llm_item(item: dict) -> ArticleData:
    return ArticleData.model_validate(item)
