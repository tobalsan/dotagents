#!/usr/bin/env python3
"""Validate one deep-research node handoff without third-party packages."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

KINDS = {"scope", "plan", "researcher", "extract", "skeptic", "merge", "persist", "synthesize"}
STATUSES = {"completed", "retryable", "failed", "cancelled"}
RELATIVE = re.compile(r"^(?![\\/])(?![A-Za-z]:)(?!.*(?:^|[\\/])\.\.(?:[\\/]|$))[^\r\n]+$")
INPUT_KEYS = {"iteration_id", "node_id", "node_kind", "lane", "attempt", "goal", "dependencies", "campaign_state_paths", "output_dir", "retrieval_skills", "repair", "limits"}
RESULT_KEYS = {"iteration_id", "node_id", "node_kind", "lane", "attempt", "status", "summary", "artifacts", "sources", "citations", "retry_reason", "error"}
DEFAULT_SCHEMA = Path(__file__).parents[1] / "references" / "node-execution-v1.schema.json"

class Invalid(ValueError):
    pass

def load(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise Invalid(f"invalid JSON: {path}") from exc

def nonempty(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value: raise Invalid(f"{field} must be non-empty string")

def relative(value: Any, field: str) -> str:
    nonempty(value, field)
    if not RELATIVE.fullmatch(value): raise Invalid(f"{field} must be safe relative path")
    return value

def uri(value: Any, field: str) -> None:
    nonempty(value, field); parsed=urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc: raise Invalid(f"{field} must be absolute http(s) URL")

def identity(value: dict[str, Any], label: str) -> None:
    for key in ("iteration_id", "node_id"): nonempty(value.get(key), f"{label}.{key}")
    if value.get("node_kind") not in KINDS: raise Invalid(f"{label}.node_kind invalid")
    attempt=value.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1: raise Invalid(f"{label}.attempt invalid")
    if "lane" in value: nonempty(value["lane"], f"{label}.lane")

def validate_input(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict): raise Invalid("input must be object")
    unknown=set(value)-INPUT_KEYS
    if unknown: raise Invalid("input has unknown fields: " + ", ".join(sorted(unknown)))
    required=INPUT_KEYS-{"lane","repair"}; missing=required-set(value)
    if missing: raise Invalid("input missing fields: " + ", ".join(sorted(missing)))
    identity(value,"input"); nonempty(value["goal"],"input.goal"); relative(value["output_dir"],"input.output_dir")
    for field in ("dependencies","campaign_state_paths","retrieval_skills"):
        if not isinstance(value[field],list): raise Invalid(f"input.{field} must be array")
    seen=set()
    for i,dep in enumerate(value["dependencies"]):
        if not isinstance(dep,dict) or set(dep)!={"node_id","result_path"}: raise Invalid(f"input.dependencies[{i}] invalid")
        nonempty(dep["node_id"],f"input.dependencies[{i}].node_id"); relative(dep["result_path"],f"input.dependencies[{i}].result_path")
        marker=json.dumps(dep,sort_keys=True)
        if marker in seen: raise Invalid("input.dependencies must be unique")
        seen.add(marker)
    for i,path in enumerate(value["campaign_state_paths"]): relative(path,f"input.campaign_state_paths[{i}]")
    if len(value["campaign_state_paths"])!=len(set(value["campaign_state_paths"])): raise Invalid("input.campaign_state_paths must be unique")
    for i,name in enumerate(value["retrieval_skills"]): nonempty(name,f"input.retrieval_skills[{i}]")
    if len(value["retrieval_skills"])!=len(set(value["retrieval_skills"])): raise Invalid("input.retrieval_skills must be unique")
    if "repair" in value:
        repair=value["repair"]
        if not isinstance(repair,dict) or set(repair)!={"mode","prior_attempt","readable_paths"}: raise Invalid("input.repair invalid")
        if repair["mode"]!="contract_only": raise Invalid("input.repair.mode invalid")
        prior=repair["prior_attempt"]
        if isinstance(prior,bool) or not isinstance(prior,int) or prior != value["attempt"]-1: raise Invalid("input.repair.prior_attempt invalid")
        paths=repair["readable_paths"]
        if not isinstance(paths,list) or not paths: raise Invalid("input.repair.readable_paths invalid")
        for i,path in enumerate(paths): relative(path,f"input.repair.readable_paths[{i}]")
        if len(paths)!=len(set(paths)): raise Invalid("input.repair.readable_paths must be unique")
        if value["dependencies"] or value["campaign_state_paths"] or value["retrieval_skills"]: raise Invalid("contract repair cannot declare dependencies, campaign state, or retrieval skills")
    limits=value["limits"]
    if not isinstance(limits,dict) or set(limits)-{"timeout_seconds","max_concurrency","budget"}: raise Invalid("input.limits invalid")
    for key in ("timeout_seconds","max_concurrency"):
        number=limits.get(key)
        if isinstance(number,bool) or not isinstance(number,int) or number < 1: raise Invalid(f"input.limits.{key} invalid")
    if "budget" in limits:
        budget=limits["budget"]
        if not isinstance(budget,dict) or not budget or set(budget)-{"max_cost","currency","max_tokens"}: raise Invalid("input.limits.budget invalid")
        if ("max_cost" in budget) != ("currency" in budget): raise Invalid("input.limits.budget max_cost and currency must appear together")
        if "max_cost" in budget:
            cost=budget["max_cost"]
            if isinstance(cost,bool) or not isinstance(cost,(int,float)) or not math.isfinite(cost) or cost < 0: raise Invalid("input.limits.budget.max_cost invalid")
            nonempty(budget["currency"],"input.limits.budget.currency")
        if "max_tokens" in budget:
            tokens=budget["max_tokens"]
            if isinstance(tokens,bool) or not isinstance(tokens,int) or tokens < 1: raise Invalid("input.limits.budget.max_tokens invalid")
    return value

def validate_error(value: Any, field: str) -> None:
    if not isinstance(value,dict) or set(value)-{"code","message","exit_code"} or not {"code","message"}<=set(value): raise Invalid(f"{field} invalid")
    nonempty(value["code"],f"{field}.code"); nonempty(value["message"],f"{field}.message")
    if "exit_code" in value and (isinstance(value["exit_code"],bool) or not isinstance(value["exit_code"],int)): raise Invalid(f"{field}.exit_code invalid")

def validate_result(value: Any) -> dict[str, Any]:
    if not isinstance(value,dict): raise Invalid("result must be object")
    unknown=set(value)-RESULT_KEYS
    if unknown: raise Invalid("result has unknown fields: " + ", ".join(sorted(unknown)))
    required={"iteration_id","node_id","node_kind","attempt","status","summary","artifacts","sources","citations"}; missing=required-set(value)
    if missing: raise Invalid("result missing fields: " + ", ".join(sorted(missing)))
    identity(value,"result"); status=value["status"]
    if status not in STATUSES: raise Invalid("result.status invalid")
    nonempty(value["summary"],"result.summary")
    if status=="completed" and ("error" in value or "retry_reason" in value): raise Invalid("completed result cannot include error or retry_reason")
    if status=="retryable" and not {"error","retry_reason"}<=set(value): raise Invalid("retryable result requires error and retry_reason")
    if status in {"failed","cancelled"} and "error" not in value: raise Invalid(f"{status} result requires error")
    if "error" in value: validate_error(value["error"],"result.error")
    if "retry_reason" in value: nonempty(value["retry_reason"],"result.retry_reason")
    artifacts=value["artifacts"]
    if not isinstance(artifacts,dict): raise Invalid("result.artifacts must be object")
    for key,path in artifacts.items(): nonempty(key,"artifact label"); relative(path,f"result.artifacts.{key}")
    if not isinstance(value["sources"],list) or not isinstance(value["citations"],list): raise Invalid("sources and citations must be arrays")
    citation_map={}
    for i,citation in enumerate(value["citations"]):
        if not isinstance(citation,dict) or set(citation)-{"citation_id","source_url","locator","artifact_path"} or not {"citation_id","source_url","locator"}<=set(citation): raise Invalid(f"result.citations[{i}] invalid")
        cid=citation["citation_id"]; nonempty(cid,f"result.citations[{i}].citation_id")
        if cid in citation_map: raise Invalid(f"duplicate citation_id: {cid}")
        uri(citation["source_url"],f"result.citations[{i}].source_url"); nonempty(citation["locator"],f"result.citations[{i}].locator")
        if "artifact_path" in citation: relative(citation["artifact_path"],f"result.citations[{i}].artifact_path")
        citation_map[cid]=citation
    source_urls=set()
    for i,source in enumerate(value["sources"]):
        if not isinstance(source,dict) or set(source)-{"canonical_id","url","title","citation_ids","artifact_path"} or "url" not in source: raise Invalid(f"result.sources[{i}] invalid")
        uri(source["url"],f"result.sources[{i}].url"); source_urls.add(source["url"])
        for key in ("canonical_id","title"):
            if key in source: nonempty(source[key],f"result.sources[{i}].{key}")
        ids=source.get("citation_ids",[])
        if not isinstance(ids,list) or len(ids)!=len(set(ids)) or any(not isinstance(x,str) or not x for x in ids): raise Invalid(f"result.sources[{i}].citation_ids invalid")
        for cid in ids:
            if cid not in citation_map: raise Invalid(f"source citation missing: {cid}")
            if citation_map[cid]["source_url"] != source["url"]: raise Invalid(f"source URL differs from citation {cid}")
        if "artifact_path" in source: relative(source["artifact_path"],f"result.sources[{i}].artifact_path")
    uncovered=sorted({citation["source_url"] for citation in value["citations"]}-source_urls)
    if uncovered: raise Invalid("citation source_url has no matching source: " + ", ".join(uncovered))
    return value

def inside_path(candidate: Path, parent: Path) -> bool:
    try: candidate.relative_to(parent); return True
    except ValueError: return False

def contained_file(root: Path, relative_path: str, label: str) -> Path:
    target=(root/relative_path).resolve(); resolved_root=root.resolve()
    if not inside_path(target,resolved_root): raise Invalid(f"{label} escapes output directory")
    if not target.is_file(): raise Invalid(f"{label} missing: {relative_path}")
    return target

def validate_counts(path: Path, result: dict[str, Any]) -> None:
    counts=load(path)
    if not isinstance(counts,dict) or set(counts)-{"sources","citations","artifacts"}: raise Invalid("counts artifact must contain only sources, citations, artifacts")
    expected={"sources":len(result["sources"]),"citations":len(result["citations"]),"artifacts":len(result["artifacts"])}
    for key,value in counts.items():
        if isinstance(value,bool) or not isinstance(value,int) or value < 0 or value != expected[key]: raise Invalid(f"counts.{key} does not match result")

def validate_schema(path: Path) -> None:
    schema=load(path)
    definitions=schema.get("definitions") if isinstance(schema,dict) else None
    if schema.get("$schema") != "http://json-schema.org/draft-07/schema#" or not isinstance(definitions,dict): raise Invalid("unsupported node schema")
    for name,keys in (("input",INPUT_KEYS-{"lane","repair"}),("result",{"iteration_id","node_id","node_kind","attempt","status","summary","artifacts","sources","citations"})):
        definition=definitions.get(name)
        if not isinstance(definition,dict) or definition.get("additionalProperties") is not False or not keys<=set(definition.get("required",[])): raise Invalid(f"node schema {name} contract mismatch")

def run(input_path: Path, result_path: Path, artifact_root: Path, process_exit: int, schema_path: Path=DEFAULT_SCHEMA) -> dict[str, Any]:
    validate_schema(schema_path); node_input=validate_input(load(input_path)); result=validate_result(load(result_path))
    output=(artifact_root/node_input["output_dir"]).resolve(); expected_result=(output/"node-result.json").resolve(); actual_result=result_path.resolve()
    if actual_result != expected_result or not inside_path(actual_result,output): raise Invalid("result must be exactly output_dir/node-result.json")
    for key in ("iteration_id","node_id","node_kind","attempt"): 
        if result[key] != node_input[key]: raise Invalid(f"identity mismatch: {key}")
    if result.get("lane") != node_input.get("lane"): raise Invalid("identity mismatch: lane")
    if result["status"]=="completed" and process_exit != 0: raise Invalid("completed result requires zero process exit")
    root=artifact_root.resolve()
    try: output.relative_to(root)
    except ValueError as exc: raise Invalid("output_dir escapes artifact root") from exc
    for label,path in result["artifacts"].items():
        target=contained_file(output,path,f"artifact {label}")
        if label=="counts": validate_counts(target,result)
    for i,source in enumerate(result["sources"]):
        if "artifact_path" in source: contained_file(output,source["artifact_path"],f"source artifact {i}")
    for citation in result["citations"]:
        if "artifact_path" in citation: contained_file(output,citation["artifact_path"],f"citation artifact {citation['citation_id']}")
    return {"valid":True,"status":result["status"],"sources":len(result["sources"]),"citations":len(result["citations"]),"artifacts":len(result["artifacts"])}

def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--input",required=True,type=Path); parser.add_argument("--result",required=True,type=Path); parser.add_argument("--schema",type=Path,default=DEFAULT_SCHEMA); parser.add_argument("--artifact-root",required=True,type=Path); parser.add_argument("--process-exit",required=True,type=int); args=parser.parse_args(argv)
    try: print(json.dumps(run(args.input,args.result,args.artifact_root,args.process_exit,args.schema),sort_keys=True,separators=(",",":"))); return 0
    except Invalid as exc: print(json.dumps({"valid":False,"error":str(exc)},sort_keys=True),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
