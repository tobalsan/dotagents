import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "prepare_node_contract.py"


class PrepareNodeContractTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path]:
        output = root / "passes/pass-1/attempts/researcher-a-1"
        output.mkdir(parents=True)
        node_input = {
            "iteration_id": "pass-1",
            "node_id": "researcher-a",
            "node_kind": "researcher",
            "lane": "a",
            "attempt": 1,
            "goal": "research",
            "dependencies": [],
            "campaign_state_paths": [],
            "output_dir": "passes/pass-1/attempts/researcher-a-1",
            "retrieval_skills": ["research/exa"],
            "limits": {"timeout_seconds": 30, "max_concurrency": 1},
        }
        path = output / "node-input.json"
        path.write_text(json.dumps(node_input))
        return path, output

    def test_materializes_exact_contract_packet_and_self_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path, output = self.fixture(root)
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(input_path), "--artifact-root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            contract = json.loads((output / "worker-contract.json").read_text())
            template = json.loads((output / "node-result.template.json").read_text())
            self.assertEqual(template["iteration_id"], "pass-1")
            self.assertEqual(template["lane"], "a")
            self.assertEqual(contract["self_validation_command"], "./self-validate.sh")
            for name in (
                "node-execution-v1.schema.json",
                "validate_node_result.py",
                "node-result.template.json",
                "worker-contract.json",
                "self-validate.sh",
            ):
                self.assertTrue((output / name).is_file())

            (output / "node-result.json").write_text(json.dumps(template))
            checked = subprocess.run([str(output / "self-validate.sh")], text=True, capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue(json.loads(checked.stdout)["valid"])

    def test_rejects_input_outside_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path, _ = self.fixture(root)
            outside = root / "node-input.json"
            outside.write_text(input_path.read_text())
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(outside), "--artifact-root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("exactly output_dir/node-input.json", completed.stderr)

    def test_schema_override_is_not_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path, _ = self.fixture(root)
            altered = root / "altered.schema.json"
            altered.write_text("{}")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(input_path), "--artifact-root", str(root), "--schema", str(altered)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("unrecognized arguments: --schema", completed.stderr)


if __name__ == "__main__":
    unittest.main()
