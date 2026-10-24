from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Author(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    affiliation: str = ""


class ArticleGuess(BaseModel):
    """Deterministic parser output for one article record."""

    title: str = ""
    year: int | None = None
    volume: int | None = None
    issue: int | None = None
    first_page: int | None = None
    last_page: int | None = None
    print_issn: str = ""
    online_issn: str = ""
    doi: str = ""
    authors: list[Author] = Field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = Field(default_factory=list)
    parser_warnings: list[str] = Field(default_factory=list)


class ArticleChunk(BaseModel):
    index: int
    issue_header: str
    raw_text: str
    guess: ArticleGuess


class ArticleData(BaseModel):
    """LLM (or skip-llm) payload that fills the Wix skeleton."""

    model_config = ConfigDict(extra="forbid")

    validation_status: Literal["ok", "needs_review", "reject"]
    issues: list[str] = Field(default_factory=list)
    title: str
    excerpt: str = ""
    year: int
    volume: int
    issue: int
    first_page: int
    last_page: int
    doi: str
    authors: list[Author]
    abstract: str
    keywords: list[str] = Field(default_factory=list)
    print_issn: str = "0024-2292"
    online_issn: str = "0976-2469"

    @field_validator("title")
    @classmethod
    def title_len(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title is required")
        if len(value) > 200:
            raise ValueError("title must be at most 200 characters")
        return value

    @field_validator("excerpt")
    @classmethod
    def excerpt_len(cls, value: str) -> str:
        value = value.strip()
        if len(value) > 500:
            return value[:500].rstrip()
        return value

    @field_validator("doi")
    @classmethod
    def doi_shape(cls, value: str) -> str:
        import re

        value = value.strip()
        if not re.fullmatch(r"10\.\d{4,9}/\S+", value):
            raise ValueError("doi must look like 10.xxxx/suffix")
        return value

    @field_validator("abstract")
    @classmethod
    def abstract_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("abstract is required")
        return value

    @field_validator("authors")
    @classmethod
    def authors_required(cls, value: list[Author]) -> list[Author]:
        if not value:
            raise ValueError("authors must not be empty")
        return value


class FooResult(BaseModel):
    accepted: list[ArticleData] = Field(default_factory=list)
    needs_review: list[ArticleData] = Field(default_factory=list)
    rejected: list[ArticleData] = Field(default_factory=list)
    invalid: list[dict] = Field(default_factory=list)
