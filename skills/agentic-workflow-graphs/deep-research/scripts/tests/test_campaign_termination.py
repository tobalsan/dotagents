import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).parents[1]/"research_state.py"
sys.path.insert(0,str(SCRIPT.parent))
import research_state as rs

class CampaignTerminationTests(unittest.TestCase):
    def row(self,url,status,source_type="web"):
        return {"canonical_id":rs.normalize(url)["canonical_id"],"status":status,"url":url,"observed_at":"2026-01-01T00:00:00Z","source_type":source_type}

    def run_case(self,root,config,rows=(),manifests=(),usage=None,now="2026-01-02T00:00:00Z"):
        config_path=root/"config.json"; config_path.write_text(json.dumps({"version":1,**config}))
        ledger=root/"ledger.jsonl"; ledger.write_text("".join(json.dumps(x)+"\n" for x in rows))
        command=[sys.executable,str(SCRIPT),"campaign-evaluate","--config",str(config_path),"--ledger",str(ledger),"--artifact-root",str(root),"--now",now]
        for manifest in manifests: command += ["--manifest",str(manifest)]
        if usage is not None:
            usage_path=root/"usage.json"; usage_path.write_text(json.dumps(usage)); command += ["--usage",str(usage_path)]
        result=subprocess.run(command,text=True,capture_output=True)
        return result,json.loads(result.stdout)

    def test_count_filters_rejected_exclusion_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); rows=[self.row("https://example.com/a","extracted","paper"),self.row("https://example.com/b","rejected","paper"),self.row("https://example.com/c","extracted","web")]
            result,out=self.run_case(root,{"target":{"type":"count","at_least":2,"statuses":["extracted"],"source_types":["paper"]}},rows)
            self.assertEqual((result.returncode,out["outcome"]),(0,"continue"))
            result,out=self.run_case(root,{"target":{"type":"count","at_least":1,"statuses":["extracted"],"source_types":["paper"]}},rows)
            self.assertEqual((result.returncode,out["outcome"]),(10,"complete"))

    def test_compound_all_any_not(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); count={"type":"count","at_least":1,"statuses":["extracted"]}; impossible={"type":"count","at_least":9,"statuses":["extracted"]}
            target={"type":"all","predicates":[count,{"type":"not","predicate":impossible},{"type":"any","predicates":[impossible,count]}]}
            result,out=self.run_case(root,{"target":target},[self.row("https://example.com/a","extracted")])
            self.assertEqual((result.returncode,out["outcome"]),(10,"complete"))

    def manifest(self,root,index,saturated):
        gap=root/f"gap-{index}.json"; gap.write_text(json.dumps({"saturated":saturated}))
        state="saturated" if saturated else "completed"
        event={"event_id":f"e{index}","iteration_id":f"i{index}","node_id":"iteration","node_kind":"iteration","state":state,"attempt":1,"observed_at":f"2026-01-{index:02d}T00:00:00Z","dependencies":[],"terminal_outcome":state,"artifact_paths":{"gap_report":gap.name}}
        path=root/f"manifest-{index}.jsonl"; path.write_text(json.dumps(event)+"\n"); return path

    def test_saturation_requires_consecutive_verified_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); manifests=[self.manifest(root,1,False),self.manifest(root,2,True),self.manifest(root,3,True)]
            result,out=self.run_case(root,{"target":{"type":"saturation","streak":2}},manifests=manifests)
            self.assertEqual((result.returncode,out["outcome"]),(10,"complete"))

    def test_deadline_budget_precedence_and_target_exception(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); deadline={"type":"deadline","at":"2026-01-02T00:00:00Z"}; budget={"type":"budget","metric":"tokens","limit":100}
            result,out=self.run_case(root,{"target":{"type":"count","at_least":0,"statuses":["extracted"]},"limits":[budget]},usage={"tokens":100})
            self.assertEqual((result.returncode,out["outcome"]),(20,"failed"))
            result,out=self.run_case(root,{"target":deadline,"limits":[deadline]},now="2026-01-02T00:00:00Z")
            self.assertEqual((result.returncode,out["outcome"]),(10,"complete"))

    def test_schema_closure_and_semantic_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for target in ({"type":"count","at_least":0,"statuses":["extracted"],"extra":1},{"type":"saturation","streak":0}):
                result,out=self.run_case(root,{"target":target})
                self.assertEqual((result.returncode,out["outcome"]),(20,"failed"))
            result,out=self.run_case(root,{"target":{"type":"count","at_least":0,"statuses":["extracted"]},"limits":[{"type":"count","at_least":0,"statuses":["extracted"]}]})
            self.assertEqual((result.returncode,out["outcome"]),(20,"failed"))

    def test_hard_limit_nested_exception_requires_positive_completed_target(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); limit={"type":"budget","metric":"tokens","limit":100}; false_count={"type":"count","at_least":1,"statuses":["extracted"]}
            targets=[{"type":"all","predicates":[limit,false_count]},{"type":"not","predicate":limit}]
            for target in targets:
                result,out=self.run_case(root,{"target":target,"limits":[limit]},usage={"tokens":100})
                self.assertEqual((result.returncode,out.get("reason")),(20,"operational_limit_exceeded"))
            target={"type":"any","predicates":[limit,false_count]}
            result,out=self.run_case(root,{"target":target,"limits":[limit]},usage={"tokens":100})
            self.assertEqual((result.returncode,out["outcome"]),(10,"complete"))

    def test_saturation_rejects_missing_reordered_and_duplicate_history(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); target={"type":"saturation","streak":1}
            result,out=self.run_case(root,{"target":target})
            self.assertEqual((result.returncode,out["outcome"]),(20,"failed"))
            first=self.manifest(root,1,True); second=self.manifest(root,2,True)
            for manifests in ([second,first],[first,first]):
                result,out=self.run_case(root,{"target":target},manifests=manifests)
                self.assertEqual((result.returncode,out["outcome"]),(20,"failed"))

    def test_filesystem_and_decoding_failures_are_json_exit_20(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); config=root/"config.json"; config.write_text(json.dumps({"version":1,"target":{"type":"count","at_least":0,"statuses":["extracted"]}}))
            ledger=root/"ledger.jsonl"; ledger.write_bytes(b"\xff")
            command=[sys.executable,str(SCRIPT),"campaign-evaluate","--config",str(config),"--ledger",str(ledger),"--artifact-root",str(root),"--now","2026-01-01T00:00:00Z"]
            result=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(result.returncode,20); self.assertEqual(json.loads(result.stdout)["outcome"],"failed")
            ledger.unlink(); ledger.mkdir()
            result=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(result.returncode,20); self.assertEqual(json.loads(result.stdout)["outcome"],"failed")

    def test_missing_state_fails_and_now_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); target={"type":"deadline","at":"2026-01-03T00:00:00Z"}
            first,a=self.run_case(root,{"target":target},now="2026-01-02T00:00:00Z"); second,b=self.run_case(root,{"target":target},now="2026-01-02T00:00:00Z")
            self.assertEqual((first.stdout,first.returncode),(second.stdout,second.returncode)); self.assertEqual(a["outcome"],"continue")
            missing=subprocess.run([sys.executable,str(SCRIPT),"campaign-evaluate","--config",str(root/"missing.json"),"--ledger",str(root/"missing.jsonl"),"--artifact-root",str(root),"--now","2026-01-01T00:00:00Z"],text=True,capture_output=True)
            self.assertEqual(missing.returncode,20); self.assertEqual(json.loads(missing.stdout)["outcome"],"failed")

if __name__ == "__main__": unittest.main()
