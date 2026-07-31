import json
import unittest

from openrights.web import index_script, payload_for_web


PAYLOAD = {
    "idf": {"overtime": 1.4},
    "chunks": [{"id": "labor:0", "source": "FLSA", "url": "https://example.test/flsa", "text": "Overtime pay.", "vector": {"overtime": 0.7}}],
}


class WebExportTest(unittest.TestCase):
    def test_vectors_are_not_shipped_to_the_phone(self):
        chunk = payload_for_web(PAYLOAD)["chunks"][0]
        self.assertNotIn("vector", chunk)
        self.assertEqual(chunk["text"], "Overtime pay.")

    def test_index_is_a_script_not_a_fetched_json_file(self):
        script = index_script(PAYLOAD)
        self.assertTrue(script.startswith("window.OPENRIGHTS_INDEX="))
        data = json.loads(script[len("window.OPENRIGHTS_INDEX=") : script.rstrip().rfind(";")])
        self.assertEqual(data["idf"], {"overtime": 1.4})


if __name__ == "__main__":
    unittest.main()
