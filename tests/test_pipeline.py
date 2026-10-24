from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from libh_automation.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parent.parent
DEC = ROOT / "LH Dec 2025 Doc.docx"


class PipelineTests(unittest.TestCase):
    def test_dry_run_skip_llm_dec_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = run_pipeline(DEC, out_dir=tmp, dry_run=True, skip_llm=True)
        self.assertEqual(summary["chunks"], 9)
        # First Dec article is a title/abstract mismatch → needs_review, not posted.
        self.assertEqual(summary["needs_review"], 1)
        self.assertEqual(summary["accepted"], 8)
        self.assertTrue(summary["dry_run"])
        self.assertEqual(len(summary["posted"]), 8)


if __name__ == "__main__":
    unittest.main()
