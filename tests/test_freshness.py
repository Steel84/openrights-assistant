import unittest

from openrights.freshness import fingerprint, statute_for_source


class FingerprintTest(unittest.TestCase):
    def test_ignores_whitespace_churn(self):
        """Government pages reflow constantly without the law changing."""
        self.assertEqual(
            fingerprint("The minimum wage is $7.25"),
            fingerprint("The  minimum\n\nwage   is $7.25\n"),
        )

    def test_detects_a_real_edit(self):
        self.assertNotEqual(
            fingerprint("The minimum wage is $7.25"),
            fingerprint("The minimum wage is $9.50"),
        )


class StatuteMatchTest(unittest.TestCase):
    def test_matches_a_source_title_to_its_answers(self):
        title = "Fair Labor Standards Act - U.S. Code Title 29, Chapter 8"
        self.assertEqual(statute_for_source(title), "Fair Labor Standards Act")

    def test_unknown_source_has_no_statute(self):
        self.assertEqual(statute_for_source("Some Unrelated Page"), "")


if __name__ == "__main__":
    unittest.main()
