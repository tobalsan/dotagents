#!/usr/bin/env python3
"""Deterministic guardrails for deep-research JSONL state."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, TextIO
from urllib.parse import parse_qs, parse_qsl, quote, urlencode, urlsplit, urlunsplit

LEDGER_FIELDS = {"canonical_id", "status", "url", "observed_at", "content_id", "work_id", "title", "source_type", "retrieved_at", "reason", "lane_id", "pass_id", "collision"}
STATUSES = {"seen", "fetched", "extracted", "rejected"}
MANIFEST_FIELDS = {"event_id", "iteration_id", "node_id", "node_kind", "state", "attempt", "observed_at", "started_at", "finished_at", "duration_ms", "dependencies", "harness", "model", "thinking", "routing_rationale", "routing_policy_ref", "artifact_paths", "error", "retry_decision", "retry_reason", "terminal_outcome"}
KINDS = {"iteration", "scope", "plan", "researcher", "extract", "skeptic", "merge", "persist", "synthesize"}
STATES = {"pending", "running", "completed", "failed", "retrying", "saturated"}
TERMINAL = {"completed", "saturated", "failed"}
TRACKING = {"fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "ref", "ref_source", "share_id", "context"}
CONTENT_ID = re.compile(r"(?:doi|arxiv|youtube|isbn):.+")
RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})")

class Invalid(ValueError): pass

def timestamp(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str) or not RFC3339.fullmatch(value): raise Invalid(f"{field} must be RFC 3339 date-time")
    try: parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise Invalid(f"{field} must be RFC 3339 date-time") from exc
    return parsed

def nonempty(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value: raise Invalid(f"{field} must be non-empty string")

def normalize(url: str) -> dict[str, str | None]:
    try: p = urlsplit(url.strip()); host = p.hostname
    except ValueError as exc: raise Invalid(f"url is malformed: {exc}") from exc
    if p.scheme.lower() not in {"http", "https"} or not host: raise Invalid("url must be absolute http(s) URL")
    host = host.lower()
    path = re.sub(r"/{2,}", "/", p.path) or "/"
    query = parse_qsl(p.query, keep_blank_values=True)
    content_id = None
    if host in {"youtu.be", "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        video = path.strip("/").split("/")[0] if host == "youtu.be" else (parse_qs(p.query).get("v") or [None])[0]
        if not video and path.startswith("/shorts/"): video = path.split("/")[2]
        if not video and path.startswith("/embed/"): video = path.split("/")[2]
        if video and re.fullmatch(r"[A-Za-z0-9_-]{6,}", video):
            content_id = f"youtube:{video}"; host = "youtube.com"; path = "/watch"; query = [("v", video)]
    elif host in {"arxiv.org", "export.arxiv.org"}:
        m = re.match(r"/(?:abs|pdf)/([^/?]+?)(?:\.pdf)?$", path)
        if m:
            ident = re.sub(r"v\d+$", "", m.group(1), flags=re.I)
            content_id = f"arxiv:{ident.lower()}"; host = "arxiv.org"; path = f"/abs/{ident.lower()}"; query = []
    elif host in {"doi.org", "dx.doi.org"}:
        doi = path.lstrip("/").lower()
        if doi.startswith("10."):
            content_id = f"doi:{doi}"; host = "doi.org"; path = "/" + doi; query = []
    elif host in {"reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com", "np.reddit.com", "redd.it"}:
        short_id = path.strip("/").split("/")[0] if host == "redd.it" else None
        host = "reddit.com"
        m = re.search(r"/comments/([a-z0-9]+)", path, re.I)
        if m or short_id: path = f"/comments/{(m.group(1) if m else short_id).lower()}"
        query = []
    query = sorted((k, v) for k, v in query if not k.lower().startswith("utm_") and k.lower() not in TRACKING)
    try: port = p.port
    except ValueError as exc: raise Invalid(f"url is malformed: {exc}") from exc
    display_host = f"[{host}]" if ":" in host else host
    netloc = display_host + (f":{port}" if port and not (p.scheme.lower() == "http" and port == 80) and not (p.scheme.lower() == "https" and port == 443) else "")
    canonical_url = urlunsplit((p.scheme.lower(), netloc, quote(path, safe="/%:@-._~!$&'()*+,;="), urlencode(query), ""))
    canonical_id = content_id or "sha256:" + hashlib.sha256(canonical_url.encode()).hexdigest()
    return {"normalized_url": canonical_url, "content_id": content_id, "canonical_id": canonical_id}

def validate_ledger(row: Any) -> None:
    if not isinstance(row, dict): raise Invalid("ledger row must be object")
    if set(row) - LEDGER_FIELDS: raise Invalid("unknown ledger fields: " + ", ".join(sorted(set(row)-LEDGER_FIELDS)))
    for key in ("canonical_id", "status", "url", "observed_at"):
        if key not in row: raise Invalid(f"missing {key}")
    nonempty(row["canonical_id"], "canonical_id")
    if not re.fullmatch(r"(?:sha256:[a-f0-9]{64}|(?:doi|arxiv|youtube|isbn):.+)", row["canonical_id"]): raise Invalid("invalid canonical_id")
    if row["status"] not in STATUSES: raise Invalid("invalid status")
    identity = normalize(row["url"]); timestamp(row["observed_at"], "observed_at")
    if "retrieved_at" in row: timestamp(row["retrieved_at"], "retrieved_at")
    for key in ("content_id", "work_id", "title", "source_type", "reason", "lane_id", "pass_id"):
        if key in row: nonempty(row[key], key)
    if "content_id" in row and not CONTENT_ID.fullmatch(row["content_id"]): raise Invalid("invalid content_id")
    expected = row.get("content_id") or identity["canonical_id"]
    if row["canonical_id"] != expected: raise Invalid("canonical_id does not match URL identity or content_id")
    if "collision" in row and not isinstance(row["collision"], bool): raise Invalid("collision must be boolean")

def validate_manifest(event: Any) -> None:
    if not isinstance(event, dict): raise Invalid("manifest event must be object")
    if set(event) - MANIFEST_FIELDS: raise Invalid("unknown manifest fields: " + ", ".join(sorted(set(event)-MANIFEST_FIELDS)))
    for key in ("event_id", "iteration_id", "node_id", "node_kind", "state", "attempt", "observed_at", "dependencies"):
        if key not in event: raise Invalid(f"missing {key}")
    for key in ("event_id", "iteration_id", "node_id"): nonempty(event[key], key)
    if event["node_kind"] not in KINDS or event["state"] not in STATES: raise Invalid("invalid node_kind or state")
    if isinstance(event["attempt"], bool) or not isinstance(event["attempt"], int) or event["attempt"] < 1: raise Invalid("attempt must be positive integer")
    timestamp(event["observed_at"], "observed_at")
    for key in ("started_at", "finished_at"):
        if key in event: timestamp(event[key], key)
    deps = event["dependencies"]
    if not isinstance(deps, list) or len(deps) != len(set(deps)) or any(not isinstance(x, str) or not x for x in deps): raise Invalid("dependencies must be unique non-empty strings")
    if "duration_ms" in event and (isinstance(event["duration_ms"], bool) or not isinstance(event["duration_ms"], int) or event["duration_ms"] < 0): raise Invalid("duration_ms must be nonnegative integer")
    for key in ("harness", "model", "thinking", "routing_rationale", "routing_policy_ref", "retry_reason"):
        if key in event: nonempty(event[key], key)
    artifacts = event.get("artifact_paths")
    if artifacts is not None and (not isinstance(artifacts, dict) or any(not isinstance(k, str) or not k or not isinstance(v, str) or not v for k,v in artifacts.items())): raise Invalid("artifact_paths must map non-empty strings to paths")
    if event["state"] == "failed":
        error = event.get("error")
        if not isinstance(error, dict) or set(error)-{"code","message"} or "message" not in error: raise Invalid("failed state requires valid error")
        nonempty(error["message"], "error.message")
        if event.get("retry_decision") not in {"retry", "do_not_retry"}: raise Invalid("failed state requires retry_decision")
    if event.get("retry_decision") == "retry" and "retry_reason" not in event: raise Invalid("retry requires retry_reason")
    if "retry_decision" in event and event["retry_decision"] not in {"retry", "do_not_retry"}: raise Invalid("invalid retry_decision")
    if event["node_kind"] == "iteration" and event["state"] in TERMINAL:
        if event.get("terminal_outcome") != event["state"]: raise Invalid("terminal_outcome must equal terminal state")
        if not artifacts or "gap_report" not in artifacts: raise Invalid("terminal iteration requires gap_report")

def read_jsonl(path: Path, validator) -> list[dict[str, Any]]:
    rows=[]
    if not path.is_file(): raise Invalid(f"missing state: {path}")
    with path.open(encoding="utf-8") as fh:
        for no, line in enumerate(fh, 1):
            if not line.strip(): raise Invalid(f"{path}:{no}: blank line")
            try: row=json.loads(line)
            except json.JSONDecodeError as exc: raise Invalid(f"{path}:{no}: invalid JSON") from exc
            try: validator(row)
            except Invalid as exc: raise Invalid(f"{path}:{no}: {exc}") from exc
            rows.append(row)
    return rows

def check_manifest_stream(events: list[dict[str, Any]]) -> None:
    seen=set(); latest={}; iteration_id=None; iteration_node=None; terminal_seen=False
    allowed={None:{"pending","running"}, "pending":{"pending","running","failed"}, "running":{"running","completed","failed","saturated"}, "failed":{"failed","retrying"}, "retrying":{"retrying"}, "completed":{"completed"}, "saturated":{"saturated"}}
    for event in events:
        if iteration_id is None: iteration_id=event["iteration_id"]
        elif event["iteration_id"] != iteration_id: raise Invalid("manifest stream must contain one iteration_id")
        if event["node_kind"] == "iteration":
            if iteration_node is None: iteration_node=event["node_id"]
            elif event["node_id"] != iteration_node: raise Invalid("iteration node_id must be stable")
            if event["state"] in TERMINAL:
                if terminal_seen: raise Invalid("iteration terminal event must be unique")
                terminal_seen=True
        eid=event["event_id"]
        if eid in seen: raise Invalid(f"duplicate event_id: {eid}")
        seen.add(eid); previous=latest.get(event["node_id"])
        if previous:
            if event["node_kind"] != previous["node_kind"]: raise Invalid("node identity changed")
            if timestamp(event["observed_at"], "observed_at") < timestamp(previous["observed_at"], "observed_at"): raise Invalid("timestamp regression")
            pa, attempt=previous["attempt"],event["attempt"]
            if attempt == pa + 1:
                if previous["state"] != "retrying" or event["state"] not in {"pending","running"}: raise Invalid("invalid attempt progression")
            elif attempt != pa: raise Invalid("invalid attempt progression")
            if attempt == pa and event["state"] not in allowed[previous["state"]]: raise Invalid(f"invalid transition: {previous['state']} -> {event['state']}")
        elif event["state"] not in allowed[None] and not (event["node_kind"] == "iteration" and event["state"] in TERMINAL):
            raise Invalid("first node state must be pending or running (or terminal iteration)")
        latest[event["node_id"]]=event
    if terminal_seen and (not events or events[-1]["node_id"] != iteration_node or events[-1]["state"] not in TERMINAL): raise Invalid("terminal iteration event must be current stream event")

def lock_file(fh: TextIO) -> None:
    if os.name == "posix":
        import fcntl
        fcntl.flock(fh, fcntl.LOCK_EX)
    elif os.name == "nt":
        import msvcrt
        fh.seek(0); msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
    else: raise Invalid(f"file locking unsupported on platform: {os.name}")

def fsync_parent(path: Path) -> None:
    if os.name != "posix": return
    fd=os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)

def append_line(path: Path, row: dict[str, Any], kind: str) -> None:
    validator = validate_ledger if kind == "ledger" else validate_manifest
    validator(row); parent_existed=path.parent.exists(); path.parent.mkdir(parents=True, exist_ok=True); created=not path.exists()
    if not parent_existed: fsync_parent(path.parent)
    with path.open("a+", encoding="utf-8") as fh:
        lock_file(fh); fh.seek(0)
        existing=[]
        for no,line in enumerate(fh,1):
            try: item=json.loads(line); validator(item)
            except (json.JSONDecodeError, Invalid) as exc: raise Invalid(f"existing stream invalid at line {no}: {exc}") from exc
            existing.append(item)
        if kind == "manifest": check_manifest_stream(existing+[row])
        data=json.dumps(row,separators=(",",":"),sort_keys=True)+"\n"
        fh.seek(0,os.SEEK_END); fh.write(data); fh.flush(); os.fsync(fh.fileno())
    if created: fsync_parent(path)

def folded(rows):
    result={}
    for row in rows: result[row["canonical_id" if "canonical_id" in row else "node_id"]]=row
    return result
def emit(value: Any) -> None: print(json.dumps(value, sort_keys=True, separators=(",",":")))

def load_json(path: Path, label: str) -> Any:
    if not path.is_file(): raise Invalid(f"missing {label}: {path}")
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise Invalid(f"invalid {label}: {path}") from exc

def verified_saturation(manifests: list[Path], root: Path) -> list[bool]:
    values=[]; root=root.resolve(); seen_iterations=set(); previous_time=None
    for path in manifests:
        events=read_jsonl(path,validate_manifest); check_manifest_stream(events)
        terminal=[e for e in folded(events).values() if e["node_kind"]=="iteration" and e["state"] in TERMINAL]
        if len(terminal) != 1: raise Invalid(f"manifest has no unique terminal iteration: {path}")
        iteration_id=terminal[0]["iteration_id"]
        if iteration_id in seen_iterations: raise Invalid(f"duplicate iteration_id across manifests: {iteration_id}")
        seen_iterations.add(iteration_id)
        terminal_time=timestamp(terminal[0]["observed_at"],"observed_at")
        if previous_time is not None and terminal_time <= previous_time: raise Invalid("manifests must have strictly increasing terminal observed_at values")
        previous_time=terminal_time
        gap=terminal[0].get("artifact_paths",{}).get("gap_report")
        candidate=Path(gap or "")
        if not gap or candidate.is_absolute() or ".." in candidate.parts: raise Invalid(f"unsafe gap_report path: {gap}")
        target=(root/candidate).resolve()
        try: target.relative_to(root)
        except ValueError as exc: raise Invalid(f"gap_report escapes root: {gap}") from exc
        evidence=load_json(target,"gap evidence")
        if not isinstance(evidence,dict) or not isinstance(evidence.get("saturated"),bool): raise Invalid(f"gap evidence requires boolean saturated: {target}")
        values.append(terminal[0]["state"]=="saturated" and evidence["saturated"])
    return values

def evaluate_predicate(predicate: Any, context: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    if not isinstance(predicate,dict) or not isinstance(predicate.get("type"),str): raise Invalid("predicate must be object with type")
    kind=predicate["type"]
    allowed={"count":{"type","at_least","statuses","source_types"},"saturation":{"type","streak"},"deadline":{"type","at"},"budget":{"type","metric","limit"},"all":{"type","predicates"},"any":{"type","predicates"},"not":{"type","predicate"}}
    required={"count":{"type","at_least","statuses"},"saturation":{"type","streak"},"deadline":{"type","at"},"budget":{"type","metric","limit"},"all":{"type","predicates"},"any":{"type","predicates"},"not":{"type","predicate"}}
    if kind not in allowed: raise Invalid(f"unknown predicate type: {kind}")
    unknown=set(predicate)-allowed[kind]
    if unknown: raise Invalid("unknown predicate fields: " + ", ".join(sorted(unknown)))
    missing=required[kind]-set(predicate)
    if missing: raise Invalid("missing predicate fields: " + ", ".join(sorted(missing)))
    if kind == "count":
        status_values=predicate["statuses"]; type_values=predicate.get("source_types",[]); threshold=predicate["at_least"]
        if not isinstance(status_values,list) or len(status_values) != len(set(status_values)): raise Invalid("count statuses must be unique array")
        if not isinstance(type_values,list) or len(type_values) != len(set(type_values)): raise Invalid("source_types must be unique array")
        statuses=set(status_values); types=set(type_values)
        if not statuses or not statuses <= STATUSES: raise Invalid("count statuses must be non-empty valid statuses")
        if isinstance(threshold,bool) or not isinstance(threshold,int) or threshold < 0: raise Invalid("count at_least must be nonnegative integer")
        if any(not isinstance(value,str) or not value for value in types): raise Invalid("source_types must be non-empty strings")
        count=sum(1 for row in context["ledger"] if row["status"] in statuses and (not types or row.get("source_type") in types))
        return count >= threshold, {"type":kind,"value":count,"at_least":threshold,"statuses":sorted(statuses),"source_types":sorted(types)}
    if kind == "saturation":
        streak=predicate["streak"]; values=context["saturation"]
        if isinstance(streak,bool) or not isinstance(streak,int) or streak < 1: raise Invalid("saturation streak must be positive integer")
        actual=0
        for value in reversed(values):
            if not value: break
            actual+=1
        return actual>=streak, {"type":kind,"value":actual,"streak":streak}
    if kind == "deadline":
        deadline=timestamp(predicate.get("at"),"deadline.at")
        return context["now"] >= deadline, {"type":kind,"now":context["now_text"],"at":predicate.get("at")}
    if kind == "budget":
        metric=predicate.get("metric"); limit=predicate.get("limit")
        if metric not in {"cost_usd","tokens"} or isinstance(limit,bool) or not isinstance(limit,(int,float)) or limit < 0: raise Invalid("invalid budget predicate")
        value=context["usage"].get(metric)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or value < 0: raise Invalid(f"usage requires nonnegative {metric}")
        return value >= limit, {"type":kind,"metric":metric,"value":value,"limit":limit}
    if kind in {"all","any"}:
        children=predicate.get("predicates")
        if not isinstance(children,list) or not children: raise Invalid(f"{kind} requires non-empty predicates")
        results=[evaluate_predicate(child,context) for child in children]
        value=all(x[0] for x in results) if kind=="all" else any(x[0] for x in results)
        return value,{"type":kind,"predicates":[x[1] for x in results]}
    if kind == "not":
        value,detail=evaluate_predicate(predicate.get("predicate"),context)
        return not value,{"type":kind,"predicate":detail}
    raise Invalid(f"unknown predicate type: {kind}")

def predicate_uses_type(predicate: Any, kind: str) -> bool:
    if not isinstance(predicate,dict): return False
    if predicate.get("type") == kind: return True
    if predicate.get("type") in {"all","any"}: return any(predicate_uses_type(child,kind) for child in predicate.get("predicates",[]))
    if predicate.get("type") == "not": return predicate_uses_type(predicate.get("predicate"),kind)
    return False

def positive_completing_limit(predicate: dict[str, Any], candidate: dict[str, Any], context: dict[str, Any]) -> bool:
    """True only when candidate occurs positively and contributes to a true target."""
    value,_=evaluate_predicate(predicate,context)
    if not value: return False
    if predicate == candidate: return True
    kind=predicate["type"]
    if kind == "all": return any(positive_completing_limit(child,candidate,context) for child in predicate["predicates"])
    if kind == "any": return any(positive_completing_limit(child,candidate,context) for child in predicate["predicates"])
    return False

def input_row(text: str | None) -> dict[str, Any]:
    try: value=json.loads(text if text is not None else sys.stdin.read())
    except json.JSONDecodeError as exc: raise Invalid("row is not valid JSON") from exc
    if not isinstance(value, dict): raise Invalid("row must be object")
    return value

def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("normalize"); p.add_argument("url")
    for name,kind in (("ledger-validate","ledger"),("manifest-validate","manifest")):
        p=sub.add_parser(name); p.add_argument("path",type=Path); p.set_defaults(kind=kind)
    for name,kind in (("ledger-append","ledger"),("manifest-append","manifest")):
        p=sub.add_parser(name); p.add_argument("path",type=Path); p.add_argument("--row"); p.set_defaults(kind=kind)
    for name,kind in (("ledger-fold","ledger"),("manifest-fold","manifest")):
        p=sub.add_parser(name); p.add_argument("path",type=Path); p.set_defaults(kind=kind)
    p=sub.add_parser("ledger-count"); p.add_argument("path",type=Path); p.add_argument("--status",action="append",required=True,choices=sorted(STATUSES)); p.add_argument("--source-type",action="append")
    p=sub.add_parser("manifest-verify"); p.add_argument("path",type=Path); p.add_argument("--artifact-root",required=True,type=Path)
    p=sub.add_parser("campaign-evaluate"); p.add_argument("--config",required=True,type=Path); p.add_argument("--ledger",required=True,type=Path); p.add_argument("--manifest",action="append",default=[],type=Path); p.add_argument("--artifact-root",required=True,type=Path); p.add_argument("--usage",type=Path); p.add_argument("--now",required=True)
    args=parser.parse_args(argv)
    if args.command == "campaign-evaluate":
        try:
            config=load_json(args.config,"campaign config")
            if not isinstance(config,dict) or config.get("version") != 1 or "target" not in config: raise Invalid("campaign config requires version 1 and target")
            if set(config)-{"version","target","limits"}: raise Invalid("campaign config contains unknown fields")
            now=timestamp(args.now,"now")
            ledger=folded(read_jsonl(args.ledger,validate_ledger)).values()
            usage=load_json(args.usage,"usage state") if args.usage else {}
            if not isinstance(usage,dict): raise Invalid("usage state must be object")
            limits=config.get("limits",[])
            if not isinstance(limits,list): raise Invalid("limits must be array")
            evaluate_predicate(config["target"],{"ledger":list(ledger),"saturation":[],"usage":usage,"now":now,"now_text":args.now})
            needs_saturation = predicate_uses_type(config["target"],"saturation")
            if needs_saturation and not args.manifest: raise Invalid("saturation evaluation requires at least one manifest")
            context={"ledger":list(ledger),"saturation":verified_saturation(args.manifest,args.artifact_root),"usage":usage,"now":now,"now_text":args.now}
            complete,detail=evaluate_predicate(config["target"],context)
            for limit in limits:
                if not isinstance(limit,dict) or limit.get("type") not in {"deadline","budget"}: raise Invalid("limits support only deadline and budget predicates")
                exceeded,limit_detail=evaluate_predicate(limit,context)
                if exceeded and not positive_completing_limit(config["target"],limit,context):
                    emit({"outcome":"failed","reason":"operational_limit_exceeded","limit":limit_detail}); return 20
            outcome="complete" if complete else "continue"; emit({"outcome":outcome,"target":detail}); return 10 if complete else 0
        except (Invalid, OSError, UnicodeError) as exc:
            emit({"outcome":"failed","reason":"state_error","error":str(exc)}); return 20
    if args.command == "normalize": emit(normalize(args.url)); return 0
    validator=validate_ledger if getattr(args,"kind",None)=="ledger" else validate_manifest
    if args.command.endswith("-validate"):
        rows=read_jsonl(args.path,validator)
        if args.kind == "manifest": check_manifest_stream(rows)
        emit({"valid":True,"rows":len(rows)}); return 0
    if args.command.endswith("-append"):
        append_line(args.path,input_row(args.row),args.kind); emit({"appended":True}); return 0
    if args.command.endswith("-fold"):
        rows=read_jsonl(args.path,validator)
        if args.kind == "manifest": check_manifest_stream(rows)
        emit({"rows":list(folded(rows).values())}); return 0
    if args.command == "ledger-count":
        current=folded(read_jsonl(args.path,validate_ledger)).values(); statuses=set(args.status); types=set(args.source_type or [])
        count=sum(1 for row in current if row["status"] in statuses and (not types or row.get("source_type") in types))
        emit({"count":count,"predicate":{"statuses":sorted(statuses),"source_types":sorted(types)}}); return 0
    events=read_jsonl(args.path,validate_manifest); check_manifest_stream(events); current=folded(events)
    iteration=[e for e in current.values() if e["node_kind"]=="iteration" and e["state"] in TERMINAL]
    if len(iteration) != 1: emit({"verified":False,"reason":"no unique current terminal iteration event"}); return 3
    terminal=iteration[0]; missing=[]; root=args.artifact_root.resolve()
    for label,path in terminal["artifact_paths"].items():
        candidate=Path(path)
        if candidate.is_absolute() or ".." in candidate.parts: raise Invalid(f"unsafe artifact path: {path}")
        target=(root/candidate).resolve()
        try: target.relative_to(root)
        except ValueError as exc: raise Invalid(f"artifact escapes root: {path}") from exc
        if not target.is_file(): missing.append(label)
    if missing: emit({"verified":False,"reason":"missing artifacts","missing":sorted(missing)}); return 3
    emit({"verified":True,"outcome":terminal["state"],"single_pass_action":"stop"}); return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except Invalid as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr); raise SystemExit(2)
