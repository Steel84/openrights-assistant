import json
import unittest
from pathlib import Path


class TestSourcesManifest(unittest.TestCase):
    """Validate the source manifest structure."""

    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.sources = json.loads((self.root / "data/sources.json").read_text())

    def test_sources_not_empty(self):
        self.assertGreater(len(self.sources), 0)

    def test_each_source_has_required_fields(self):
        for source in self.sources:
            self.assertIn("id", source)
            self.assertIn("title", source)
            self.assertIn("url", source)
            self.assertTrue(source["url"].startswith("http"))

    def test_unique_ids(self):
        ids = [s["id"] for s in self.sources]
        self.assertEqual(len(ids), len(set(ids)))


class TestEvalsManifest(unittest.TestCase):
    """Validate the evaluation question set."""

    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.questions = json.loads((self.root / "evals/questions.json").read_text())

    def test_questions_not_empty(self):
        self.assertGreater(len(self.questions), 20)

    def test_each_question_has_required_fields(self):
        for q in self.questions:
            self.assertIn("question", q)
            self.assertIn("expected_source", q)
            self.assertTrue(len(q["question"]) > 10)


if __name__ == "__main__":
    unittest.main()
