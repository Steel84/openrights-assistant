import unittest

from openrights.generator import build_prompt


class GeneratorTest(unittest.TestCase):
    def test_prompt_contains_only_cited_context(self):
        prompt = build_prompt("What is overtime?", [{"source": "FLSA", "text": "Overtime is paid at one and one-half times.", "url": "https://example.test/flsa"}])
        self.assertIn("[1] FLSA", prompt)
        self.assertIn("cite claims with [1]", prompt)
        self.assertIn("https://example.test/flsa", prompt)


if __name__ == "__main__":
    unittest.main()
