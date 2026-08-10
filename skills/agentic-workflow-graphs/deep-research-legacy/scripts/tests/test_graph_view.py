import http.client
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "graph_view.py"
sys.path.insert(0, str(SCRIPT.parent))
import graph_view as gv

FIXTURE_CAMPAIGN = Path(__file__).parent / "fixtures" / "campaign"
EXTERNAL_REF = re.compile(r'(?:src|href)\s*=\s*"https?://|url\(\s*[\'"]?https?://', re.IGNORECASE)


def event(eid, node_id, kind, state, attempt=1, time_="2026-08-01T00:00:00Z", **extra):
    return {"event_id": eid, "iteration_id": "pass-1", "node_id": node_id, "node_kind": kind, "state": state, "attempt": attempt, "observed_at": time_, "dependencies": [], **extra}


def write_manifest(root: Path, pass_id: str, lines: list[str]) -> Path:
    path = root / "passes" / pass_id / "iteration-manifest.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n" if lines else "")
    return path


class FoldTests(unittest.TestCase):
    def test_per_pass_fold_does_not_collapse_recurring_node_ids(self):
        result = gv.assemble(FIXTURE_CAMPAIGN)
        self.assertEqual(list(result["passes"]), ["pass-1", "pass-2"])
        plan1 = next(n for n in result["passes"]["pass-1"]["nodes"] if n["node_id"] == "plan")
        plan2 = next(n for n in result["passes"]["pass-2"]["nodes"] if n["node_id"] == "plan")
        self.assertEqual((plan1["state"], plan1["attempt"], plan1["harness"]), ("completed", 1, "opencode"))
        self.assertEqual((plan2["state"], plan2["attempt"], plan2["harness"]), ("running", 1, "codex"))
        self.assertEqual(result["campaign"]["pass_count"], 2)
        self.assertEqual(result["campaign"]["source_count"], 2)  # folded rows from fixtures/campaign/source-ledger.jsonl

    def test_node_fields_duration_model_artifacts_dependencies_and_state_counts(self):
        result = gv.assemble(FIXTURE_CAMPAIGN)
        plan1 = next(n for n in result["passes"]["pass-1"]["nodes"] if n["node_id"] == "plan")
        self.assertEqual(plan1["duration_ms"], 4000)
        self.assertEqual(plan1["model"], "model-a")
        self.assertEqual(plan1["artifact_paths"], {"plan": "plan.md"})
        researcher_x = next(n for n in result["passes"]["pass-1"]["nodes"] if n["node_id"] == "researcher-x")
        self.assertEqual(researcher_x["dependencies"], ["plan"])
        self.assertEqual(result["campaign"]["node_state_counts"], {"completed": 3, "running": 1})

    def test_researcher_retry_attempt_trail_and_current_attempt_snapshot(self):
        result = gv.assemble(FIXTURE_CAMPAIGN)
        node = next(n for n in result["passes"]["pass-1"]["nodes"] if n["node_id"] == "researcher-x")
        self.assertEqual(node["state"], "completed")
        self.assertEqual(node["attempt"], 2)
        self.assertEqual(len(node["attempts"]), 6)  # pending,running,failed,retrying,running,completed
        self.assertEqual([e["error"]["code"] for e in node["attempts"] if e.get("error")], ["weird_custom_code"])
        # current-attempt snapshot must not leak the attempt-1 error onto the attempt-2 (completed) node
        self.assertIsNone(node["error"])
        self.assertEqual(node["harness"], "opencode")
        self.assertEqual(node["duration_ms"], 10000)

    def test_terminal_iteration_rollup(self):
        result = gv.assemble(FIXTURE_CAMPAIGN)
        terminal = result["campaign"]["terminal_iterations"]
        self.assertEqual(terminal["pass-1"]["state"], "completed")
        self.assertIsNone(terminal["pass-2"])  # pass-2 has no iteration event at all


class TruncatedTailTests(unittest.TestCase):
    def test_truncated_trailing_line_tolerated_and_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            good = json.dumps(event("e1", "plan", "plan", "pending"))
            manifest = write_manifest(root, "pass-1", [])
            manifest.write_text(good + "\n" + '{"event_id":"e2","node_id":"plan","state":"pen')
            events, truncated = gv.read_manifest_tolerant(manifest)
            self.assertTrue(truncated)
            self.assertEqual([e["event_id"] for e in events], ["e1"])
            result = gv.assemble(root)
            self.assertTrue(result["passes"]["pass-1"]["truncated_tail"])
            self.assertEqual(len(result["passes"]["pass-1"]["nodes"]), 1)

    def test_clean_trailing_newline_is_not_flagged_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_manifest(root, "pass-1", [json.dumps(event("e1", "plan", "plan", "pending"))])
            events, truncated = gv.read_manifest_tolerant(root / "passes" / "pass-1" / "iteration-manifest.jsonl")
            self.assertFalse(truncated)
            self.assertEqual(len(events), 1)


class ErrorCodeTests(unittest.TestCase):
    def test_unknown_error_code_flagged_not_dropped(self):
        self.assertEqual(gv.build_error({"code": "totally_made_up", "message": "m"}), {"code": "totally_made_up", "message": "m", "uncategorized": True})
        self.assertFalse(gv.build_error({"code": "timeout", "message": "m"})["uncategorized"])
        self.assertIsNone(gv.build_error(None))

    def test_node_level_failed_state_surfaces_uncategorized_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lines = [
                event("e1", "researcher-y", "researcher", "pending"),
                event("e2", "researcher-y", "researcher", "running", time_="2026-08-01T00:00:01Z", harness="opencode", model="m", started_at="2026-08-01T00:00:01Z"),
                event("e3", "researcher-y", "researcher", "failed", time_="2026-08-01T00:00:02Z", finished_at="2026-08-01T00:00:02Z", error={"code": "mystery_code", "message": "boom"}, retry_decision="do_not_retry"),
            ]
            write_manifest(root, "pass-1", [json.dumps(x) for x in lines])
            result = gv.assemble(root)
            node = result["passes"]["pass-1"]["nodes"][0]
            self.assertEqual(node["error"], {"code": "mystery_code", "message": "boom", "uncategorized": True})


class ValidationTests(unittest.TestCase):
    def test_schema_invalid_event_raises(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bad = event("e1", "plan", "plan", "not_a_real_state")
            write_manifest(root, "pass-1", [json.dumps(bad)])
            with self.assertRaises(gv.rs.Invalid):
                gv.assemble(root)

    def test_illegal_transition_raises(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lines = [
                event("e1", "plan", "plan", "pending"),
                event("e2", "plan", "plan", "completed", time_="2026-08-01T00:00:01Z"),  # pending -> completed is illegal
            ]
            write_manifest(root, "pass-1", [json.dumps(x) for x in lines])
            with self.assertRaises(gv.rs.Invalid):
                gv.assemble(root)


class LivenessTests(unittest.TestCase):
    def test_absent_pid_file_is_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            attempt_dir = Path(d)
            self.assertEqual(gv.classify_liveness(attempt_dir), {"liveness": "unknown", "pid": None})

    def test_live_pid_with_recent_writes_is_running(self):
        with tempfile.TemporaryDirectory() as d:
            attempt_dir = Path(d)
            (attempt_dir / "pid").write_text(str(os.getpid()))
            (attempt_dir / "opencode.log").write_text("hello")
            result = gv.classify_liveness(attempt_dir)
            self.assertEqual(result["liveness"], "running")
            self.assertEqual(result["pid"], os.getpid())

    def test_dead_pid_is_process_gone(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        dead_pid = proc.pid
        with tempfile.TemporaryDirectory() as d:
            attempt_dir = Path(d)
            (attempt_dir / "pid").write_text(str(dead_pid))
            result = gv.classify_liveness(attempt_dir)
            self.assertEqual(result["liveness"], "process_gone")
            self.assertEqual(result["pid"], dead_pid)
            self.assertFalse(result["exit_code_present"])

    def test_live_pid_with_stale_mtime_is_quiet(self):
        with tempfile.TemporaryDirectory() as d:
            attempt_dir = Path(d)
            pid_path = attempt_dir / "pid"
            pid_path.write_text(str(os.getpid()))
            log_path = attempt_dir / "opencode.log"
            log_path.write_text("stale")
            stale_time = time.time() - (gv.QUIET_THRESHOLD_MINUTES + 10) * 60
            os.utime(pid_path, (stale_time, stale_time))
            os.utime(log_path, (stale_time, stale_time))
            result = gv.classify_liveness(attempt_dir)
            self.assertEqual(result["liveness"], "quiet")
            self.assertGreaterEqual(result["seconds_since_last_write"], gv.QUIET_THRESHOLD_MINUTES * 60)

    def test_pid_zero_or_negative_is_unknown_not_running(self):
        # pid 0 means "my own process group" and -1 means "every signalable process" to kill(2);
        # both always succeed and must never be read as evidence of a live node process.
        for bad_pid in (0, -1):
            with tempfile.TemporaryDirectory() as d:
                attempt_dir = Path(d)
                (attempt_dir / "pid").write_text(str(bad_pid))
                self.assertEqual(gv.classify_liveness(attempt_dir), {"liveness": "unknown", "pid": None})

    def test_opencode_pid_filename_is_probed_when_pid_file_absent(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        dead_pid = proc.pid
        with tempfile.TemporaryDirectory() as d:
            attempt_dir = Path(d)
            (attempt_dir / "opencode.pid").write_text(str(dead_pid))
            result = gv.classify_liveness(attempt_dir)
            self.assertEqual(result["liveness"], "process_gone")
            self.assertEqual(result["pid"], dead_pid)

    def test_legacy_attempt_dir_without_pid_lands_on_unknown_end_to_end(self):
        # pass-2's plan-1 attempt dir in the fixture has no pid file at all.
        result = gv.assemble(FIXTURE_CAMPAIGN)
        plan2 = next(n for n in result["passes"]["pass-2"]["nodes"] if n["node_id"] == "plan")
        self.assertEqual(plan2["state"], "running")
        self.assertEqual(plan2["liveness"], {"liveness": "unknown", "pid": None})


class CLITests(unittest.TestCase):
    def test_once_prints_json_document_with_campaign_and_passes(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "--campaign", str(FIXTURE_CAMPAIGN), "--once"], text=True, capture_output=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        payload = json.loads(out.stdout)
        self.assertIn("campaign", payload)
        self.assertIn("passes", payload)
        self.assertEqual(sorted(payload["passes"]), ["pass-1", "pass-2"])

    def test_without_once_or_serve_errors_cleanly(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "--campaign", str(FIXTURE_CAMPAIGN)], text=True, capture_output=True)
        self.assertEqual(out.returncode, 2)
        self.assertIn("--once", out.stderr)

    def test_nonexistent_campaign_dir_errors_instead_of_reporting_empty(self):
        with tempfile.TemporaryDirectory() as d:
            missing = Path(d) / "does-not-exist"
            out = subprocess.run([sys.executable, str(SCRIPT), "--campaign", str(missing), "--once"], text=True, capture_output=True)
            self.assertEqual(out.returncode, 2, out.stdout)
            self.assertIn("error", json.loads(out.stderr))

    def test_mid_file_malformed_json_line_errors_with_json_envelope(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lines = [
                json.dumps(event("e1", "plan", "plan", "pending")),
                "GARBAGE",
                json.dumps(event("e2", "plan", "plan", "running", time_="2026-08-01T00:00:01Z", started_at="2026-08-01T00:00:01Z")),
            ]
            write_manifest(root, "pass-1", lines)
            out = subprocess.run([sys.executable, str(SCRIPT), "--campaign", str(root), "--once"], text=True, capture_output=True)
            self.assertEqual(out.returncode, 2, out.stdout)
            self.assertIn("invalid JSON", json.loads(out.stderr)["error"])

    def test_mid_file_blank_line_errors_with_json_envelope(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lines = [
                json.dumps(event("e1", "plan", "plan", "pending")),
                "",
                json.dumps(event("e2", "plan", "plan", "running", time_="2026-08-01T00:00:01Z", started_at="2026-08-01T00:00:01Z")),
            ]
            write_manifest(root, "pass-1", lines)
            out = subprocess.run([sys.executable, str(SCRIPT), "--campaign", str(root), "--once"], text=True, capture_output=True)
            self.assertEqual(out.returncode, 2, out.stdout)
            self.assertIn("blank line", json.loads(out.stderr)["error"])


class ServerTests(unittest.TestCase):
    """Starts a real GraphViewServer on an ephemeral port for each test and shuts it down cleanly."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_manifest(self.root, "pass-1", [json.dumps(event("e1", "plan", "plan", "pending"))])
        (self.root / "notes.txt").write_text("hello from inside campaign root", encoding="utf-8")
        self.outside = tempfile.TemporaryDirectory()
        (Path(self.outside.name) / "secret.txt").write_text("outside the campaign root", encoding="utf-8")
        (self.root / "escape-link").symlink_to(Path(self.outside.name) / "secret.txt")
        self.httpd = gv.GraphViewServer(("127.0.0.1", 0), gv.GraphViewHandler, self.root.resolve())
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        self.outside.cleanup()
        self.tmp.cleanup()

    def get(self, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", path)
            resp = conn.getresponse()
            return resp.status, resp.read()
        finally:
            conn.close()

    def test_root_serves_html_with_no_external_resource_references(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("<html", text.lower())
        self.assertIsNone(EXTERNAL_REF.search(text))

    def test_api_state_returns_valid_json_with_expected_top_level_keys(self):
        status, body = self.get("/api/state")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertIn("campaign", payload)
        self.assertIn("passes", payload)
        self.assertEqual(list(payload["passes"]), ["pass-1"])

    def test_api_file_dotdot_traversal_rejected(self):
        status, _ = self.get("/api/file?path=" + urllib.parse.quote("../../etc/passwd"))
        self.assertEqual(status, 403)

    def test_api_file_dotdot_buried_mid_path_rejected(self):
        status, _ = self.get("/api/file?path=" + urllib.parse.quote("notes.txt/../../../../etc/passwd"))
        self.assertEqual(status, 403)

    def test_api_file_absolute_path_rejected(self):
        status, _ = self.get("/api/file?path=" + urllib.parse.quote("/etc/passwd"))
        self.assertEqual(status, 403)

    def test_api_file_symlink_escape_rejected(self):
        status, _ = self.get("/api/file?path=escape-link")
        self.assertEqual(status, 403)

    def test_api_file_legitimate_relative_path_returns_bytes(self):
        status, body = self.get("/api/file?path=notes.txt")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"hello from inside campaign root")

    def test_api_file_missing_path_returns_404(self):
        status, _ = self.get("/api/file?path=does-not-exist.txt")
        self.assertEqual(status, 404)

    def test_api_file_null_byte_path_returns_400_not_dropped_connection(self):
        status, _ = self.get("/api/file?path=" + urllib.parse.quote("\x00/etc/passwd"))
        self.assertEqual(status, 400)

    @unittest.skipIf(os.name != "posix" or (hasattr(os, "geteuid") and os.geteuid() == 0), "permission bits are meaningless for root")
    def test_api_file_unreadable_file_returns_404(self):
        unreadable = self.root / "unreadable.txt"
        unreadable.write_text("secret", encoding="utf-8")
        unreadable.chmod(0o000)
        try:
            status, _ = self.get("/api/file?path=unreadable.txt")
            self.assertEqual(status, 404)
        finally:
            unreadable.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
