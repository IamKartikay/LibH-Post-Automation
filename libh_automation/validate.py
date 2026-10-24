from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from libh_automation.models import ArticleData, FooResult


def foo(llm_items: list[Any]) -> FooResult:
    """Validate the LLM list of article data objects.

    Posts only items with validation_status == "ok" that pass schema checks.
    """
    result = FooResult()
    for item in llm_items:
        if not isinstance(item, dict):
            result.invalid.append({"error": "item is not an object", "item": item})
            continue
        try:
            article = ArticleData.model_validate(item)
        except ValidationError as exc:
            result.invalid.append({"error": exc.errors(), "item": item})
            continue
        if article.validation_status == "ok":
            result.accepted.append(article)
        elif article.validation_status == "needs_review":
            result.needs_review.append(article)
        else:
            result.rejected.append(article)
    return result


def write_review_log(result: FooResult, path: str | Path) -> None:
    import json

    payload = {
        "needs_review": [a.model_dump() for a in result.needs_review],
        "rejected": [a.model_dump() for a in result.rejected],
        "invalid": result.invalid,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
