from __future__ import annotations

import unittest
from pathlib import Path

from libh_automation.extract import extract_chunks, parse_article_block

ROOT = Path(__file__).resolve().parent.parent

DEC = ROOT / "LH Dec 2025 Doc.docx"
MAR = ROOT / "LH March 2026 Doc.docx"
JUN = ROOT / "LH June 2026 Doc.docx"

DEC_FIRST = [
    "WE-A Multi-disciplinary and Multi-lingual Peer-Reviewed Research Journal: A Scientometric Analysis",
    "LIBRARY HERALD",
    "Year : 2025, Volume : 63, Issue :4",
    "First page :(429) Last page :(448)",
    "Print ISSN : 0024-2292. Online ISSN : 0976-2469.",
    "Article DOI : 10.5958/0976-2469.2025.00033.5",
    "Harish Chander1, K. P. Singh2",
    "1 Assistant Professor, Department of Library and Information Science, Guru Nanak Dev University, Amritsar, India",
    "2 Professor, Department of Library and Information Science, University of Delhi, Delhi, India",
    "Abstract",
    "This study targets to evaluate the perceptions of the Video Conferencing Software (VCS) amongst the postgraduates’ at Rani Channamma University, Belagavi in Karnataka.",
    "Keywords",
    "Scientometric analysis; Multidisciplinary journal; University of Delhi; Scholarly research; Authorship pattern.",
]

DEC_DOI_JUNK = [
    "Cultivating Knowledge: The Impact of Open Access on Indian Agriculture Universities",
    "LIBRARY HERALD",
    "Year : 2025, Volume : 63, Issue :4",
    "First page :(463) Last page :(473)",
    "Print ISSN : 0024-2292. Online ISSN : 0976-2469.",
    "Article DOI : 10.5958/0976-2469.2025.00035.8 4",
    "Raghavendra B. Bonal1, Shilpa S. Uplaonkar",
    "1 Central University of Karnataka, Kalaburagi, Karnataka, India",
    "2 University of Agricultural Sciences, Dharwad, Karnataka, India",
    "Abstract",
    "This study brings into the limelight the transformative effect of Open-Access Publishing on education in the agricultural phase.",
    "Keywords",
    "Open Access Trends, Agricultural Knowledge Exchange, Student Perspectives",
]


class ExtractTests(unittest.TestCase):
    def test_article_counts(self) -> None:
        self.assertEqual(len(extract_chunks(DEC)), 9)
        self.assertEqual(len(extract_chunks(MAR)), 14)
        self.assertEqual(len(extract_chunks(JUN)), 8)

    def test_mismatch_warning_on_first_dec_record(self) -> None:
        guess = parse_article_block(DEC_FIRST, "Vol 63")
        self.assertEqual(guess.authors[0].name, "Harish Chander")
        self.assertTrue(
            any("different topics" in w.lower() for w in guess.parser_warnings)
        )

    def test_doi_trailing_junk_stripped(self) -> None:
        guess = parse_article_block(DEC_DOI_JUNK, "Vol 63")
        self.assertEqual(guess.doi, "10.5958/0976-2469.2025.00035.8")
        self.assertTrue(any("junk" in w.lower() for w in guess.parser_warnings))

    def test_real_docx_first_title(self) -> None:
        chunks = extract_chunks(DEC)
        self.assertIn("Scientometric", chunks[0].guess.title)
        self.assertEqual(chunks[0].guess.year, 2025)
        self.assertEqual(chunks[0].guess.volume, 63)
        self.assertEqual(chunks[0].guess.issue, 4)


if __name__ == "__main__":
    unittest.main()
