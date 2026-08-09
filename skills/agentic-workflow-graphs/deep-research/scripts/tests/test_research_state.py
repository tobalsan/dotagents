import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT=Path(__file__).parents[1]/"research_state.py"
sys.path.insert(0,str(SCRIPT.parent))
import research_state as rs

class StateTests(unittest.TestCase):
    def test_normalization_aliases_and_generic_identity(self):
        pairs=[
          ("https://youtu.be/AbCdEf12345?t=3","https://www.youtube.com/watch?v=AbCdEf12345&utm_source=x"),
          ("https://arxiv.org/pdf/2401.12345v2.pdf","https://export.arxiv.org/abs/2401.12345"),
          ("https://dx.doi.org/10.1000/ABC","https://doi.org/10.1000/abc"),
          ("https://old.reddit.com/r/x/comments/abc123/title/?utm_source=x","https://reddit.com/comments/abc123?share_id=z")]
        for a,b in pairs: self.assertEqual(rs.normalize(a)["canonical_id"],rs.normalize(b)["canonical_id"])
        self.assertEqual(rs.normalize("https://www.example.com/a%2Fb?b=2&utm_source=x&a=1")["normalized_url"],"https://www.example.com/a%2Fb?a=1&b=2")
        self.assertNotEqual(rs.normalize("https://www.example.com/x")["canonical_id"],rs.normalize("https://example.com/x")["canonical_id"])
        self.assertNotEqual(rs.normalize("https://example.com/a%2Fb")["canonical_id"],rs.normalize("https://example.com/a/b")["canonical_id"])

    def test_ports_ipv6_and_cli_errors(self):
        self.assertEqual(rs.normalize("http://[::1]:80/x")["normalized_url"],"http://[::1]/x")
        self.assertEqual(rs.normalize("https://[2001:db8::1]:8443/x")["normalized_url"],"https://[2001:db8::1]:8443/x")
        for url in ("https://example.com:bad/x", "https://[::1/x"):
            out=subprocess.run([sys.executable,SCRIPT,"normalize",url],text=True,capture_output=True)
            self.assertEqual(out.returncode,2); self.assertIn("url is malformed",json.loads(out.stderr)["error"])

    def ledger(self,url,status,kind="web",**extra):
        return {"canonical_id":rs.normalize(url)["canonical_id"],"status":status,"url":url,"observed_at":"2026-01-01T00:00:00Z","source_type":kind,**extra}
    def event(self,eid,state,time="2026-01-01T00:00:00Z",attempt=1,**extra):
        return {"event_id":eid,"iteration_id":extra.pop("iteration_id","pass-1"),"node_id":extra.pop("node_id","plan"),"node_kind":extra.pop("node_kind","plan"),"state":state,"attempt":attempt,"observed_at":time,"dependencies":[],**extra}

    def test_ledger_identity_must_match(self):
        row=self.ledger("https://example.com/x","seen")
        rs.validate_ledger(row)
        row["canonical_id"]="sha256:"+"a"*64
        with self.assertRaisesRegex(rs.Invalid,"does not match"): rs.validate_ledger(row)
        row["canonical_id"]=row["content_id"]="isbn:9780000000000"
        rs.validate_ledger(row)
        row["canonical_id"]="doi:10/x"
        with self.assertRaisesRegex(rs.Invalid,"does not match"): rs.validate_ledger(row)

    def test_strict_rfc3339(self):
        for invalid in ("2026-01-01 00:00:00Z","2026-01-01T00:00:00","2026-01-01T00:00Z"):
            with self.assertRaises(rs.Invalid): rs.timestamp(invalid,"time")
        rs.timestamp("2026-01-01T00:00:00.123+05:30","time")

    def test_fold_count_and_rejected_inclusion(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"l.jsonl"
            rows=[self.ledger("https://example.com/a","seen"),self.ledger("https://example.com/a","extracted"),self.ledger("https://doi.org/10/x","rejected","paper")]
            p.write_text("".join(json.dumps(x)+"\n" for x in rows))
            out=subprocess.run([sys.executable,SCRIPT,"ledger-count",p,"--status","extracted"],text=True,capture_output=True)
            self.assertEqual(json.loads(out.stdout)["count"],1)
            out=subprocess.run([sys.executable,SCRIPT,"ledger-count",p,"--status","extracted","--status","rejected"],text=True,capture_output=True)
            self.assertEqual(json.loads(out.stdout)["count"],2)

    def test_manifest_stream_invariants_and_retry_increment(self):
        invalid=[
          [self.event("1","running"),self.event("2","pending")],
          [self.event("1","running"),self.event("1","completed")],
          [self.event("1","running","2026-01-02T00:00:00Z"),self.event("2","completed","2026-01-01T00:00:00Z")],
          [self.event("1","running"),self.event("2","running",iteration_id="pass-2",node_id="other")],
          [self.event("1","retrying"),self.event("2","running")],
          [self.event("1","retrying"),self.event("2","running",attempt=3)],
        ]
        terminal=lambda eid,node="iteration": self.event(eid,"completed",node_id=node,node_kind="iteration",terminal_outcome="completed",artifact_paths={"gap_report":"gap.md"})
        invalid += [[terminal("1","i1"),terminal("2","i2")],[terminal("1"),self.event("2","running",node_id="late")]]
        for events in invalid:
            with self.subTest(events=events), self.assertRaises(rs.Invalid): rs.check_manifest_stream(events)
        rs.check_manifest_stream([self.event("1","running"),self.event("2","failed"),self.event("3","retrying"),self.event("4","running",attempt=2)])

    def test_terminal_artifacts_symlink_escape_and_single_pass_stop(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root=Path(d); manifest=root/"m.jsonl"
            event=self.event("term","completed",node_id="iteration",node_kind="iteration",terminal_outcome="completed",artifact_paths={"gap_report":"gap.md"})
            manifest.write_text(json.dumps(event)+"\n")
            cmd=[sys.executable,str(SCRIPT),"manifest-verify",str(manifest),"--artifact-root",str(root)]
            missing=subprocess.run(cmd,text=True,capture_output=True); self.assertEqual(missing.returncode,3)
            external=Path(outside)/"gap.md"; external.write_text("outside")
            try: (root/"gap.md").symlink_to(external)
            except OSError: self.skipTest("symlink unavailable")
            escaped=subprocess.run(cmd,text=True,capture_output=True); self.assertEqual(escaped.returncode,2)
            self.assertIn("escapes root",escaped.stderr)
            (root/"gap.md").unlink(); (root/"gap.md").write_text("ok")
            done=subprocess.run(cmd,text=True,capture_output=True); self.assertEqual(done.returncode,0)
            self.assertEqual(json.loads(done.stdout)["single_pass_action"],"stop")

    def test_append_creation_fsync_and_unsupported_lock(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"new"/"ledger.jsonl"; row=self.ledger("https://example.com/x","seen")
            with mock.patch.object(rs,"fsync_parent",wraps=rs.fsync_parent) as sync:
                rs.append_line(path,row,"ledger")
                self.assertGreaterEqual(sync.call_count,2)
            with path.open("a+") as fh, mock.patch.object(os,"name","other"):
                with self.assertRaisesRegex(rs.Invalid,"locking unsupported"): rs.lock_file(fh)

    def failed_event(self,eid,code,**extra):
        return self.event(eid,"failed",node_id="researcher-1",node_kind="researcher",error={"code":code,"message":"boom"},retry_decision="do_not_retry",**extra)

    def test_append_rejects_bad_error_code_but_accepts_good_one(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"m.jsonl"
            rs.append_line(path,self.event("e1","pending",node_id="researcher-1",node_kind="researcher"),"manifest")
            bad=subprocess.run([sys.executable,SCRIPT,"manifest-append",path,"--row",json.dumps(self.failed_event("e2","not_a_real_code"))],text=True,capture_output=True)
            self.assertEqual(bad.returncode,2); self.assertIn("invalid error.code",json.loads(bad.stderr)["error"])
            good=subprocess.run([sys.executable,SCRIPT,"manifest-append",path,"--row",json.dumps(self.failed_event("e2","timeout"))],text=True,capture_output=True)
            self.assertEqual(good.returncode,0); self.assertTrue(json.loads(good.stdout)["appended"])

    def test_manifest_validate_accepts_legacy_free_text_error_code(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"m.jsonl"
            rows=[self.event("e1","pending",node_id="researcher-1",node_kind="researcher"),
                  self.failed_event("e2","empty_provider_termination")]
            path.write_text("".join(json.dumps(r)+"\n" for r in rows))
            out=subprocess.run([sys.executable,SCRIPT,"manifest-validate",path],text=True,capture_output=True)
            self.assertEqual(out.returncode,0); self.assertTrue(json.loads(out.stdout)["valid"])

    def test_pending_event_with_dependencies_appends_and_folds(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"m.jsonl"
            rs.append_line(path,self.event("e1","pending",node_id="merge",node_kind="merge",dependencies=["researcher-1","extract"]),"manifest")
            folded=subprocess.run([sys.executable,SCRIPT,"manifest-fold",path],text=True,capture_output=True)
            self.assertEqual(folded.returncode,0)
            row=json.loads(folded.stdout)["rows"][0]
            self.assertEqual(row["dependencies"],["researcher-1","extract"]); self.assertEqual(row["state"],"pending")

if __name__ == "__main__": unittest.main()
