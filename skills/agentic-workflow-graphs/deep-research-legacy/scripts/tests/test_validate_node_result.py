import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "validate_node_result.py"
spec = importlib.util.spec_from_file_location("validate_node_result", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(validator)

class ValidateNodeResultTests(unittest.TestCase):
    def fixture(self, root: Path):
        output=root/"passes/pass-1/attempts/researcher-a-1"; output.mkdir(parents=True)
        node_input={"iteration_id":"pass-1","node_id":"researcher-a","node_kind":"researcher","lane":"a","attempt":1,"goal":"research","dependencies":[],"campaign_state_paths":["source-ledger.jsonl"],"output_dir":"passes/pass-1/attempts/researcher-a-1","retrieval_skills":["research/exa"],"limits":{"timeout_seconds":30,"max_concurrency":2}}
        result={"iteration_id":"pass-1","node_id":"researcher-a","node_kind":"researcher","lane":"a","attempt":1,"status":"completed","summary":"done","artifacts":{"report":"report.md"},"sources":[{"url":"https://example.com/a","citation_ids":["c1"]}],"citations":[{"citation_id":"c1","source_url":"https://example.com/a","locator":"line 1","artifact_path":"evidence.txt"}]}
        (root/"input.json").write_text(json.dumps(node_input)); (output/"node-result.json").write_text(json.dumps(result)); (output/"report.md").write_text("report"); (output/"evidence.txt").write_text("evidence")
        return root/"input.json",output/"node-result.json",result,output

    def test_accepts_valid_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,_,_=self.fixture(root)
            self.assertTrue(validator.run(inp,res,root,0)["valid"])

    def test_rejects_duplicate_citation_and_nonzero_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,result,_=self.fixture(root)
            result["citations"].append(dict(result["citations"][0])); res.write_text(json.dumps(result))
            with self.assertRaisesRegex(validator.Invalid,"duplicate citation_id"): validator.run(inp,res,root,0)
            result["citations"].pop(); res.write_text(json.dumps(result))
            with self.assertRaisesRegex(validator.Invalid,"zero process exit"): validator.run(inp,res,root,1)

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,result,output=self.fixture(root); outside=root/"outside.txt"; outside.write_text("secret"); (output/"link.txt").symlink_to(outside); result["artifacts"]["leak"]="link.txt"; res.write_text(json.dumps(result))
            with self.assertRaisesRegex(validator.Invalid,"escapes output directory"): validator.run(inp,res,root,0)

    def test_checks_only_explicit_machine_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,result,output=self.fixture(root); result["artifacts"]["counts"]="counts.json"; (output/"counts.json").write_text(json.dumps({"sources":99})); res.write_text(json.dumps(result))
            with self.assertRaisesRegex(validator.Invalid,"does not match"): validator.run(inp,res,root,0)

    def test_rejects_invalid_budget_shapes(self):
        invalid=({},{"max_cost":1},{"currency":"USD"},{"max_tokens":0},{"max_cost":True,"currency":"USD"},{"max_cost":1,"currency":"USD","extra":1})
        for budget in invalid:
            with self.subTest(budget=budget), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); inp,res,_,_=self.fixture(root); value=json.loads(inp.read_text()); value["limits"]["budget"]=budget; inp.write_text(json.dumps(value))
                with self.assertRaises(validator.Invalid): validator.run(inp,res,root,0)

    def test_requires_exact_result_location_and_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,_,_=self.fixture(root); copy=root/"other-result.json"; copy.write_text(res.read_text())
            with self.assertRaisesRegex(validator.Invalid,"exactly output_dir/node-result.json"): validator.run(inp,copy,root,0)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,_,_=self.fixture(root); outside=root/"outside-result.json"; outside.write_text(res.read_text()); res.unlink(); res.symlink_to(outside)
            with self.assertRaisesRegex(validator.Invalid,"exactly output_dir/node-result.json"): validator.run(inp,res,root,0)

    def test_rejects_citation_without_source_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,result,_=self.fixture(root); result["citations"].append({"citation_id":"c2","source_url":"https://example.com/unlisted","locator":"line 2"}); res.write_text(json.dumps(result))
            with self.assertRaisesRegex(validator.Invalid,"no matching source"): validator.run(inp,res,root,0)

    def test_accepts_retrieval_free_contract_repair_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp,res,_,_=self.fixture(root); value=json.loads(inp.read_text()); value["attempt"]=2; value["dependencies"]=[]; value["campaign_state_paths"]=[]; value["retrieval_skills"]=[]; value["repair"]={"mode":"contract_only","prior_attempt":1,"readable_paths":["passes/pass-1/attempts/researcher-a-1/node-result.json"]}; value["output_dir"]="passes/pass-1/attempts/researcher-a-2"; output=root/value["output_dir"]; output.mkdir(); repaired=output/"node-result.json"; result=json.loads(res.read_text()); result["attempt"]=2; repaired.write_text(json.dumps(result)); (output/"report.md").write_text("report"); (output/"evidence.txt").write_text("evidence"); inp=output/"node-input.json"; inp.write_text(json.dumps(value))
            self.assertTrue(validator.run(inp,repaired,root,0)["valid"])

    def test_rejects_contract_repair_with_research_access(self):
        base={"mode":"contract_only","prior_attempt":1,"readable_paths":["passes/pass-1/attempts/researcher-a-1/node-result.json"]}
        for field,value in (("dependencies",[{"node_id":"plan","result_path":"plan.json"}]),("campaign_state_paths",["source-ledger.jsonl"]),("retrieval_skills",["research/exa"])):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); inp,_,_,_=self.fixture(root); node=json.loads(inp.read_text()); node["attempt"]=2; node["repair"]=base; node[field]=value; inp.write_text(json.dumps(node))
                with self.assertRaisesRegex(validator.Invalid,"contract repair cannot declare"): validator.validate_input(node)

if __name__ == "__main__": unittest.main()
