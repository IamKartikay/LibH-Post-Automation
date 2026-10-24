from __future__ import annotations

import re
from pathlib import Path

from docx import Document

from libh_automation.models import ArticleChunk, ArticleGuess, Author

JOURNAL_LINE = "LIBRARY HERALD"
BIBLIO_RE = re.compile(
    r"Year\s*:\s*(\d+)\s*,\s*Volume\s*:\s*(\d+)\s*,\s*Issue\s*:(\d+)",
    re.I,
)
PAGES_RE = re.compile(
    r"First page\s*:\s*\(?(\d+)\)?\s*Last page\s*:\s*\(?(\d+)\)?",
    re.I,
)
ISSN_RE = re.compile(
    r"Print ISSN\s*:\s*([0-9Xx-]+)\.?\s*Online ISSN\s*:\s*([0-9Xx-]+)",
    re.I,
)
DOI_LINE_RE = re.compile(r"Article DOI\s*:\s*(.+)", re.I)
DOI_TOKEN_RE = re.compile(r"(10\.\d{4,9}/\S+)")
AFFIL_RE = re.compile(r"^(\d+)\s+(.+)$")
AUTHOR_MARK_RE = re.compile(r"(\d+)")


def read_paragraphs(path: str | Path) -> list[str]:
    document = Document(path)
    paragraphs: list[str] = []
    for para in document.paragraphs:
        text = " ".join(para.text.split()).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def _issue_header(paragraphs: list[str]) -> str:
    header_parts: list[str] = []
    for line in paragraphs[:3]:
        header_parts.append(line)
    return " / ".join(header_parts)


def _title_indices(paragraphs: list[str]) -> list[int]:
    indices: list[int] = []
    for i, line in enumerate(paragraphs[:-1]):
        if paragraphs[i + 1] == JOURNAL_LINE and line.upper() != "FOR LIBRARY HERALD":
            indices.append(i)
    return indices


def _split_keywords(raw: str) -> list[str]:
    parts = re.split(r"[;]+", raw) if ";" in raw else re.split(r",", raw)
    cleaned: list[str] = []
    for part in parts:
        item = part.strip(" .")
        if item:
            cleaned.append(item)
    return cleaned


def _clean_doi(raw: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    match = DOI_TOKEN_RE.search(raw)
    if not match:
        return "", [f"Could not parse DOI from: {raw}"]
    doi = match.group(1).rstrip(".,;")
    leftover = raw[match.end() :].strip()
    if leftover:
        warnings.append(f"Stripped trailing DOI junk: {leftover!r}")
    return doi, warnings


def _parse_authors(lines: list[str]) -> list[Author]:
    if not lines:
        return []
    author_line = lines[0]
    affil_map: dict[str, str] = {}
    for line in lines[1:]:
        match = AFFIL_RE.match(line)
        if match:
            affil_map[match.group(1)] = match.group(2).strip()

    names = re.split(r"\s*,\s*", author_line)
    authors: list[Author] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        marks = AUTHOR_MARK_RE.findall(name)
        clean_name = re.sub(r"\d+", "", name).strip(" ,")
        clean_name = re.sub(r"\s+", " ", clean_name)
        affiliation = ""
        if marks:
            affiliation = affil_map.get(marks[0], "")
        elif len(affil_map) == 1:
            affiliation = next(iter(affil_map.values()))
        authors.append(Author(name=clean_name, affiliation=affiliation))
    return authors


def _significant_tokens(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "of",
        "a",
        "an",
        "in",
        "on",
        "at",
        "to",
        "from",
        "with",
        "by",
        "a",
        "study",
        "analysis",
        "research",
        "journal",
        "library",
        "india",
    }
    tokens = re.findall(r"[A-Za-z]{4,}", text.lower())
    return {t for t in tokens if t not in stop}


def _title_abstract_mismatch(title: str, abstract: str) -> bool:
    if not title or not abstract:
        return False
    title_tokens = _significant_tokens(title)
    abstract_tokens = _significant_tokens(abstract)
    if not title_tokens or not abstract_tokens:
        return False
    return len(title_tokens & abstract_tokens) == 0


def parse_article_block(block: list[str], issue_header: str = "") -> ArticleGuess:  # noqa: ARG001
    warnings: list[str] = []
    title = block[0] if block else ""
    year = volume = issue = first_page = last_page = None
    print_issn = online_issn = doi = abstract = ""
    keywords: list[str] = []
    author_lines: list[str] = []

    i = 1
    while i < len(block):
        line = block[i]
        if line == JOURNAL_LINE:
            i += 1
            continue
        biblio = BIBLIO_RE.search(line)
        if biblio:
            year, volume, issue = (int(biblio.group(1)), int(biblio.group(2)), int(biblio.group(3)))
            i += 1
            continue
        pages = PAGES_RE.search(line)
        if pages:
            first_page, last_page = int(pages.group(1)), int(pages.group(2))
            i += 1
            continue
        issn = ISSN_RE.search(line)
        if issn:
            print_issn, online_issn = issn.group(1), issn.group(2)
            i += 1
            continue
        doi_line = DOI_LINE_RE.search(line)
        if doi_line:
            doi, doi_warnings = _clean_doi(doi_line.group(1))
            warnings.extend(doi_warnings)
            i += 1
            continue
        if line.lower() == "abstract":
            if i + 1 < len(block) and block[i + 1].lower() != "keywords":
                abstract = block[i + 1]
                i += 2
            else:
                warnings.append("Missing abstract text")
                i += 1
            continue
        if line.lower() == "keywords":
            if i + 1 < len(block):
                keywords = _split_keywords(block[i + 1])
                i += 2
            else:
                warnings.append("Missing keywords text")
                i += 1
            continue
        author_lines.append(line)
        i += 1

    authors = _parse_authors(author_lines)
    if not authors:
        warnings.append("No authors parsed")
    if _title_abstract_mismatch(title, abstract):
        warnings.append("Title and abstract appear to be about different topics")

    return ArticleGuess(
        title=title,
        year=year,
        volume=volume,
        issue=issue,
        first_page=first_page,
        last_page=last_page,
        print_issn=print_issn,
        online_issn=online_issn,
        doi=doi,
        authors=authors,
        abstract=abstract,
        keywords=keywords,
        parser_warnings=warnings,
    )


def extract_chunks(path: str | Path) -> list[ArticleChunk]:
    paragraphs = read_paragraphs(path)
    header = _issue_header(paragraphs)
    starts = _title_indices(paragraphs)
    chunks: list[ArticleChunk] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(paragraphs)
        block = paragraphs[start:end]
        guess = parse_article_block(block, header)
        chunks.append(
            ArticleChunk(
                index=idx,
                issue_header=header,
                raw_text="\n".join(block),
                guess=guess,
            )
        )
    return chunks
