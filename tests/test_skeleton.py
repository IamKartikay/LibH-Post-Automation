from __future__ import annotations

import unittest

from libh_automation.models import ArticleData
from libh_automation.skeleton import merge_skeleton

ARTICLE = ArticleData(
    validation_status="ok",
    issues=[],
    title="Open Access in Agricultural Universities",
    excerpt="This study examines open access.",
    year=2025,
    volume=63,
    issue=4,
    first_page=463,
    last_page=473,
    doi="10.5958/0976-2469.2025.00035.8",
    authors=[{"name": "Raghavendra B. Bonal", "affiliation": "CUK"}],
    abstract="This study brings into the limelight the transformative effect of Open-Access.",
    keywords=["Open Access Trends", "Agricultural Knowledge Exchange"],
)


class SkeletonTests(unittest.TestCase):
    def test_replaces_data_only(self) -> None:
        payload = merge_skeleton(ARTICLE, "c00e8a5c-322b-4e77-8813-002e3ea7e811")
        self.assertFalse(payload["publish"])
        draft = payload["draftPost"]
        self.assertEqual(draft["title"], ARTICLE.title)
        self.assertEqual(draft["memberId"], "c00e8a5c-322b-4e77-8813-002e3ea7e811")
        nodes = draft["richContent"]["nodes"]
        self.assertEqual(nodes[0]["type"], "HEADING")
        self.assertEqual(nodes[1], {"type": "PARAGRAPH"})
        texts = [
            node["nodes"][0]["textData"]["text"]
            for node in nodes
            if node.get("type") == "PARAGRAPH" and node.get("nodes")
        ]
        self.assertTrue(any("Raghavendra" in t for t in texts))
        self.assertTrue(any(ARTICLE.doi in t for t in texts))
        self.assertTrue(any(ARTICLE.abstract in t for t in texts))
        self.assertTrue(any("Open Access Trends" in t for t in texts))

    def test_text_never_at_root(self) -> None:
        payload = merge_skeleton(ARTICLE, "member")
        for node in payload["draftPost"]["richContent"]["nodes"]:
            self.assertNotEqual(node["type"], "TEXT")


if __name__ == "__main__":
    unittest.main()
