import unittest
from openrights.generator import build_prompt


class GeneratorTest(unittest.TestCase):
    def test_prompt_contains_citation_instruction(self):
        prompt = build_prompt("What is overtime?", [{"source": "FLSA", "text": "Overtime is paid at one and one-half times.", "url": "https://example.test/flsa"}])
        self.assertIn("[1]", prompt)
        self.assertIn("Cite every factual claim", prompt)
        self.assertIn("NOT legal advice", prompt)

    def test_prompt_includes_question(self):
        prompt = build_prompt("What is the minimum wage?", [{"source": "FLSA", "text": "The minimum wage is $7.25.", "url": "https://example.test/flsa"}])
        self.assertIn("What is the minimum wage?", prompt)

    def test_prompt_includes_source_text(self):
        prompt = build_prompt("test?", [{"source": "Test", "text": "Unique passage text here.", "url": "https://example.test"}])
        self.assertIn("Unique passage text here.", prompt)


if __name__ == "__main__":
    unittest.main()
