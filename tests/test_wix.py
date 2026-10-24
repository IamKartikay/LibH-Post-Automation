from __future__ import annotations

import unittest

from libh_automation.wix import wix_headers


class WixTests(unittest.TestCase):
    def test_headers(self) -> None:
        headers = wix_headers("IST.example-key", "site-guid")
        self.assertEqual(headers["Authorization"], "IST.example-key")
        self.assertEqual(headers["wix-site-id"], "site-guid")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertFalse(headers["Authorization"].startswith("Bearer "))


if __name__ == "__main__":
    unittest.main()
