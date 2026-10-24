from __future__ import annotations

import unittest

from libh_automation.validate import foo

VALID = {
    "validation_status": "ok",
    "issues": [],
    "title": "A valid library science article title",
    "excerpt": "Short excerpt from the abstract.",
    "year": 2025,
    "volume": 63,
    "issue": 4,
    "first_page": 429,
    "last_page": 448,
    "doi": "10.5958/0976-2469.2025.00033.5",
    "authors": [{"name": "Harish Chander", "affiliation": "GNDU"}],
    "abstract": "This is a real abstract about scientometric analysis.",
    "keywords": ["Scientometric analysis"],
    "print_issn": "0024-2292",
    "online_issn": "0976-2469",
}


class FooTests(unittest.TestCase):
    def test_accepts_ok_items(self) -> None:
        result = foo([VALID])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0].title, VALID["title"])

    def test_needs_review_not_posted(self) -> None:
        item = {**VALID, "validation_status": "needs_review", "issues": ["mismatch"]}
        result = foo([item])
        self.assertEqual(result.accepted, [])
        self.assertEqual(len(result.needs_review), 1)

    def test_reject_status(self) -> None:
        item = {**VALID, "validation_status": "reject"}
        result = foo([item])
        self.assertEqual(len(result.rejected), 1)

    def test_invalid_doi_and_extra_keys(self) -> None:
        bad_doi = {**VALID, "doi": "not-a-doi"}
        extra = {**VALID, "draftPost": {"hack": True}}
        result = foo([bad_doi, extra])
        self.assertEqual(len(result.invalid), 2)

    def test_empty_authors_invalid(self) -> None:
        result = foo([{**VALID, "authors": []}])
        self.assertEqual(len(result.invalid), 1)


if __name__ == "__main__":
    unittest.main()
