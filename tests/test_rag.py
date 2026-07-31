import tempfile
import unittest
from pathlib import Path

from openrights.rag import TfidfIndex


class TfidfIndexTest(unittest.TestCase):
    def test_search_ranks_matching_chunk(self):
        index = TfidfIndex.build([
            {"id": "labor", "text": "Overtime compensation is one and one-half times the regular rate."},
            {"id": "scam", "text": "Phishing messages ask you to click a suspicious link."},
        ])
        self.assertEqual(index.search("How is overtime compensation calculated?", 1)[0]["id"], "labor")

    def test_round_trip(self):
        index = TfidfIndex.build([{"id": "one", "text": "A public source passage."}])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.json"
            index.save(path)
            self.assertEqual(TfidfIndex.load(path).search("public source", 1)[0]["id"], "one")


if __name__ == "__main__":
    unittest.main()
