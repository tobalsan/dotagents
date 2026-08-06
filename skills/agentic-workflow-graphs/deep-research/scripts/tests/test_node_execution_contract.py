import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
SCHEMA_PATH = ROOT / "references" / "node-execution-v1.schema.json"
CONTRACT_PATH = ROOT / "references" / "node-execution-v1.md"


class NodeExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text())

    def test_envelopes_and_identity_are_closed(self):
        definitions = self.schema["definitions"]
        self.assertFalse(definitions["identity"]["additionalProperties"])
        for name in ("input", "result"):
            envelope = definitions[name]
            self.assertFalse(envelope["additionalProperties"])
            self.assertNotIn({"$ref": "#/definitions/identity"}, envelope.get("allOf", []))
            self.assertTrue(set(definitions["identity"]["required"]) <= set(envelope["required"]))
            self.assertTrue(set(definitions["identity"]["properties"]) <= set(envelope["properties"]))

    def test_relative_path_pattern_is_portable(self):
        pattern = re.compile(self.schema["definitions"]["relativePath"]["pattern"])
        for path in ("node/out.json", "nested\\out.json", ".hidden", "a..b/file"):
            with self.subTest(path=path):
                self.assertIsNotNone(pattern.fullmatch(path))
        for path in (
            "/absolute",
            "../escape",
            "a/../escape",
            "..\\escape",
            "a\\..\\escape",
            "C:\\absolute",
            "c:/absolute",
            "\\\\server\\share",
        ):
            with self.subTest(path=path):
                self.assertIsNone(pattern.fullmatch(path))

    def test_citation_runtime_invariant_is_explicit(self):
        contract = CONTRACT_PATH.read_text()
        self.assertIn("Every `citation_id` must be unique across the result", contract)
        self.assertIn("must resolve to exactly one entry in `citations`", contract)
        self.assertIn("orchestrator must enforce them at runtime", contract)


if __name__ == "__main__":
    unittest.main()
