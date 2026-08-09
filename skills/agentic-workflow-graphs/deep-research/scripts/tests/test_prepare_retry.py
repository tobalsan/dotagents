import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "prepare_retry.py"
REASON = "temporary failure"

class PrepareRetryTests(unittest.TestCase):
    def prior(self, root: Path) -> Path:
        (root/"passes/pass-1/attempts").mkdir(parents=True,exist_ok=True)
        value={"iteration_id":"pass-1","node_id":"extract-a","node_kind":"extract","attempt":1,"goal":"extract","dependencies":[],"campaign_state_paths":[],"output_dir":"passes/pass-1/attempts/extract-a-1","retrieval_skills":[],"limits":{"timeout_seconds":30,"max_concurrency":1}}
        path=root/"prior.json"; path.write_text(json.dumps(value)); return path

    def manifest(self, root: Path, **overrides) -> Path:
        event={"iteration_id":"pass-1","node_id":"extract-a","node_kind":"extract","attempt":1,"state":"failed","retry_decision":"retry","retry_reason":REASON}; event.update(overrides)
        path=root/"manifest.jsonl"; path.write_text(json.dumps(event)+"\n"); return path

    def run_retry(self, root: Path, *extra: str, manifest_overrides=None):
        current=root/"passes/pass-1/current"; current.mkdir(parents=True,exist_ok=True); (current/"researcher-a.json").write_text("{}")
        (root/"source-ledger.jsonl").write_text("")
        return subprocess.run([sys.executable,str(SCRIPT),"--input",str(self.prior(root)),"--manifest",str(self.manifest(root,**(manifest_overrides or {}))),"--artifact-root",str(root),"--output-dir","passes/pass-1/attempts/extract-a-2","--reason",REASON,*extra],text=True,capture_output=True)

    def test_prepares_fresh_input_and_event_templates_without_mutating_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); completed=self.run_retry(root,"--dependency","researcher-a=passes/pass-1/current/researcher-a.json","--campaign-state","source-ledger.jsonl")
            self.assertEqual(completed.returncode,0,completed.stderr); out=root/"passes/pass-1/attempts/extract-a-2"; node=json.loads((out/"node-input.json").read_text()); prep=json.loads((out/"retry-preparation.json").read_text())
            self.assertEqual(node["attempt"],2); self.assertEqual(node["dependencies"][0]["node_id"],"researcher-a"); self.assertFalse(prep["manifest_mutated"]); self.assertEqual(len((root/"manifest.jsonl").read_text().splitlines()),1)

    def test_rejects_stale_or_completed_manifest(self):
        for overrides in ({"attempt":2},{"state":"completed","retry_decision":None}):
            with self.subTest(overrides=overrides), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); completed=self.run_retry(root,manifest_overrides=overrides)
                self.assertEqual(completed.returncode,2); self.assertIn("manifest retry state mismatch",completed.stderr); self.assertFalse((root/"passes/pass-1/attempts/extract-a-2").exists())

    def test_denies_lexical_and_symlink_prior_attempt_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); completed=self.run_retry(root,"--dependency","old=passes/pass-1/attempts/researcher-a-1/node-result.json")
            self.assertEqual(completed.returncode,2); self.assertIn("prior-attempt read denied",completed.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.prior(root); prior=root/"passes/pass-1/attempts/extract-a-1"; prior.mkdir(); (prior/"node-result.json").write_text("{}"); alias=root/"alias"; alias.symlink_to(prior, target_is_directory=True)
            completed=self.run_retry(root,"--dependency","old=alias/node-result.json")
            self.assertEqual(completed.returncode,2); self.assertIn("prior-attempt read denied",completed.stderr)

    def test_rejects_readable_escape_and_output_overlap(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root=Path(tmp); alias=root/"outside"; alias.symlink_to(Path(outside),target_is_directory=True); (Path(outside)/"source.json").write_text("{}")
            completed=self.run_retry(root,"--dependency","bad=outside/source.json")
            self.assertEqual(completed.returncode,2); self.assertIn("escapes artifact root",completed.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); output_parent=root/"passes/pass-1/attempts"; output_parent.mkdir(parents=True,exist_ok=True)
            completed=self.run_retry(root,"--campaign-state","passes/pass-1/attempts","--allow-prior-attempts")
            self.assertEqual(completed.returncode,2); self.assertIn("overlaps output_dir",completed.stderr)

    def test_failure_leaves_no_output_or_temp_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); completed=self.run_retry(root,"--campaign-state","../escape")
            self.assertEqual(completed.returncode,2); attempts=root/"passes/pass-1/attempts"; self.assertFalse((attempts/"extract-a-2").exists()); self.assertEqual(list(attempts.glob(".extract-a-2.tmp-*")),[])

    def test_requires_fresh_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.prior(root); (root/"passes/pass-1/attempts/extract-a-2").mkdir(); completed=self.run_retry(root)
            self.assertEqual(completed.returncode,2); self.assertIn("already exists",completed.stderr)

if __name__ == "__main__": unittest.main()
