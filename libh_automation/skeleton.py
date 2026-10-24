from __future__ import annotations

import copy
from typing import Any

from libh_automation.models import ArticleData, Author

SKELETON: dict[str, Any] = {
    "draftPost": {
        "title": "",
        "memberId": "",
        "excerpt": "",
        "commentingEnabled": True,
        "richContent": {
            "nodes": [
                {
                    "type": "HEADING",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "Authors", "decorations": []},
                        }
                    ],
                    "headingData": {"level": 2, "textStyle": {"textAlignment": "AUTO"}},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "PARAGRAPH",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "", "decorations": []},
                        }
                    ],
                    "paragraphData": {},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "HEADING",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "Bibliographic details", "decorations": []},
                        }
                    ],
                    "headingData": {"level": 2, "textStyle": {"textAlignment": "AUTO"}},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "PARAGRAPH",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "", "decorations": []},
                        }
                    ],
                    "paragraphData": {},
                },
                {
                    "type": "PARAGRAPH",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "", "decorations": []},
                        }
                    ],
                    "paragraphData": {},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "HEADING",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "Abstract", "decorations": []},
                        }
                    ],
                    "headingData": {"level": 2, "textStyle": {"textAlignment": "AUTO"}},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "PARAGRAPH",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "", "decorations": []},
                        }
                    ],
                    "paragraphData": {},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "HEADING",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "Keywords", "decorations": []},
                        }
                    ],
                    "headingData": {"level": 2, "textStyle": {"textAlignment": "AUTO"}},
                },
                {"type": "PARAGRAPH"},
                {
                    "type": "PARAGRAPH",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {"text": "", "decorations": []},
                        }
                    ],
                    "paragraphData": {},
                },
            ]
        },
    },
    "publish": False,
}

# Indices of TEXT nodes that hold replaceable body copy inside richContent.nodes
_AUTHORS_NODE = 2
_BIBLIO_NODE = 6
_DOI_NODE = 7
_ABSTRACT_NODE = 11
_KEYWORDS_NODE = 15


def authors_line(authors: list[Author]) -> str:
    parts: list[str] = []
    for author in authors:
        if author.affiliation:
            parts.append(f"{author.name} ({author.affiliation})")
        else:
            parts.append(author.name)
    return "; ".join(parts)


def biblio_line(article: ArticleData) -> str:
    return (
        f"Library Herald, Year: {article.year}, Volume: {article.volume}, "
        f"Issue: {article.issue}, pp. {article.first_page}–{article.last_page}. "
        f"Print ISSN: {article.print_issn}. Online ISSN: {article.online_issn}."
    )


def doi_line(article: ArticleData) -> str:
    return f"Article DOI: {article.doi}"


def keywords_line(article: ArticleData) -> str:
    return "; ".join(article.keywords)


def _set_paragraph_text(nodes: list[dict[str, Any]], index: int, text: str) -> None:
    nodes[index]["nodes"][0]["textData"]["text"] = text


def merge_skeleton(article: ArticleData, member_id: str) -> dict[str, Any]:
    payload = copy.deepcopy(SKELETON)
    draft = payload["draftPost"]
    draft["title"] = article.title
    draft["memberId"] = member_id
    draft["excerpt"] = article.excerpt or article.abstract[:500]
    nodes = draft["richContent"]["nodes"]
    _set_paragraph_text(nodes, _AUTHORS_NODE, authors_line(article.authors))
    _set_paragraph_text(nodes, _BIBLIO_NODE, biblio_line(article))
    _set_paragraph_text(nodes, _DOI_NODE, doi_line(article))
    _set_paragraph_text(nodes, _ABSTRACT_NODE, article.abstract)
    _set_paragraph_text(nodes, _KEYWORDS_NODE, keywords_line(article))
    return payload
