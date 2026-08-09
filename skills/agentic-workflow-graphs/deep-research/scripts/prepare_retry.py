#!/usr/bin/env python3
"""Prepare a fresh harness-neutral deep-research retry attempt."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ATTEMPT = re.compile(r"(?:^|[\\/])attempts?(?:[\\/]|$)", re.I)

class Invalid(ValueError):
    pass

def load(path: Path) -> dict[str, Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise Invalid(f"invalid prior input: {path}") from exc
    if not isinstance(value,dict): raise Invalid("prior input must be object")
    return value

def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        rows=[]
        for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if not line.strip(): raise Invalid(f"manifest line {number} is blank")
            value=json.loads(line)
            if not isinstance(value,dict): raise Invalid(f"manifest line {number} must be object")
            rows.append(value)
        return rows
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise Invalid(f"invalid manifest: {path}") from exc

def safe(path: str, label: str) -> None:
    candidate=Path(path)
    if not path or candidate.is_absolute() or ".." in candidate.parts or re.match(r"^[A-Za-z]:",path): raise Invalid(f"unsafe {label}: {path}")

def parse_dependency(value: str) -> dict[str,str]:
    node,sep,path=value.partition("=")
    if not sep or not node or not path: raise argparse.ArgumentTypeError("dependency must be NODE_ID=RESULT_PATH")
    safe(path,"dependency path"); return {"node_id":node,"result_path":path}

def inside(candidate: Path, parent: Path) -> bool:
    try: candidate.relative_to(parent); return True
    except ValueError: return False

def verify_manifest(rows: list[dict[str,Any]], prior: dict[str,Any], reason: str, contract_repair: bool) -> dict[str,Any]:
    current={}
    for row in rows:
        node=row.get("node_id")
        if isinstance(node,str): current[node]=row
    event=current.get(prior.get("node_id"))
    if not event: raise Invalid("manifest has no current event for node")
    expected={"iteration_id":prior.get("iteration_id"),"node_kind":prior.get("node_kind"),"attempt":prior.get("attempt"),"state":"failed","retry_decision":"retry","retry_reason":reason}
    mismatches=[key for key,value in expected.items() if event.get(key)!=value]
    if mismatches: raise Invalid("manifest retry state mismatch: " + ", ".join(mismatches))
    error=event.get("error")
    if contract_repair and (not isinstance(error,dict) or error.get("code")!="invalid_node_result_format"): raise Invalid("contract repair requires invalid_node_result_format manifest error")
    return event

def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True,type=Path,help="failed attempt node-input.json")
    parser.add_argument("--manifest",required=True,type=Path,help="read-only iteration manifest")
    parser.add_argument("--artifact-root",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,help="fresh artifact-root-relative attempt directory")
    parser.add_argument("--reason",required=True)
    parser.add_argument("--dependency",action="append",default=[],type=parse_dependency)
    parser.add_argument("--campaign-state",action="append",default=[])
    parser.add_argument("--allow-prior-attempts",action="store_true")
    parser.add_argument("--contract-repair",action="store_true",help="prepare a retrieval-free repair for invalid_node_result")
    parser.add_argument("--repair-read",action="append",default=[],help="prior-attempt file readable by contract repair")
    args=parser.parse_args(argv); temporary=None
    try:
        prior=load(args.input); rows=load_manifest(args.manifest); safe(args.output_dir,"output_dir")
        if not args.reason: raise Invalid("reason must be non-empty")
        expected=prior.get("attempt")
        if isinstance(expected,bool) or not isinstance(expected,int) or expected < 1: raise Invalid("prior input attempt invalid")
        required={"iteration_id","node_id","node_kind","goal","retrieval_skills","limits","output_dir"}; missing=required-set(prior)
        if missing: raise Invalid("prior input missing fields: " + ", ".join(sorted(missing)))
        safe(prior["output_dir"],"prior output_dir")
        verify_manifest(rows,prior,args.reason,args.contract_repair)
        dependencies=args.dependency; states=args.campaign_state
        if len({json.dumps(x,sort_keys=True) for x in dependencies}) != len(dependencies): raise Invalid("dependencies must be unique")
        for path in states: safe(path,"campaign-state path")
        if len(set(states)) != len(states): raise Invalid("campaign-state paths must be unique")
        for path in args.repair_read: safe(path,"repair-readable path")
        if len(set(args.repair_read)) != len(args.repair_read): raise Invalid("repair-readable paths must be unique")
        if args.contract_repair:
            if dependencies or states or args.allow_prior_attempts: raise Invalid("contract repair cannot declare dependencies, campaign state, or broad prior-attempt access")
            if not args.repair_read: raise Invalid("contract repair requires --repair-read")
        elif args.repair_read:
            raise Invalid("--repair-read requires --contract-repair")
        root=args.artifact_root.resolve(); output=(root/args.output_dir).resolve(); prior_output=(root/prior["output_dir"]).resolve()
        try: output.relative_to(root)
        except ValueError as exc: raise Invalid("output_dir escapes artifact root") from exc
        if output.exists(): raise Invalid("fresh output_dir already exists")
        if not output.parent.is_dir(): raise Invalid("output_dir parent must already exist")
        readable=args.repair_read if args.contract_repair else [x["result_path"] for x in dependencies]+states
        resolved_readable=[(path,(root/path).resolve()) for path in readable]
        if args.contract_repair:
            expected_result=(Path(prior["output_dir"])/"node-result.json").as_posix()
            if expected_result not in {Path(path).as_posix() for path in readable}: raise Invalid("contract repair must read prior node-result.json")
            for path,resolved in resolved_readable:
                if not inside(resolved,prior_output): raise Invalid(f"contract repair read escapes prior output: {path}")
                if not resolved.is_file(): raise Invalid(f"contract repair readable file missing: {path}")
        elif not args.allow_prior_attempts:
            offending=[]
            for path,resolved in resolved_readable:
                lexical=ATTEMPT.search(path.replace("\\","/")) is not None
                resolved_attempts="attempts" in {part.lower() for part in resolved.parts}
                if lexical or resolved_attempts or inside(resolved,prior_output): offending.append(path)
            if offending: raise Invalid("prior-attempt read denied: " + ", ".join(offending))
        for path,resolved in resolved_readable:
            if not inside(resolved,root): raise Invalid(f"readable path escapes artifact root: {path}")
            if not resolved.exists(): raise Invalid(f"readable path missing: {path}")
            if inside(resolved,output) or inside(output,resolved): raise Invalid(f"readable path overlaps output_dir: {path}")
        new_attempt=expected+1
        node_input={key:prior[key] for key in ("iteration_id","node_id","node_kind")}
        if "lane" in prior: node_input["lane"]=prior["lane"]
        node_input.update({"attempt":new_attempt,"goal":prior["goal"],"dependencies":[] if args.contract_repair else dependencies,"campaign_state_paths":[] if args.contract_repair else states,"output_dir":args.output_dir,"retrieval_skills":[] if args.contract_repair else prior["retrieval_skills"],"limits":prior["limits"]})
        if args.contract_repair: node_input["repair"]={"mode":"contract_only","prior_attempt":expected,"readable_paths":readable}
        instructions=["Orchestrator validates node-input.json before dispatch.","Orchestrator appends retrying for the verified failed attempt.","Orchestrator appends pending or running for the new attempt only when dispatch begins."]
        if args.contract_repair: instructions += ["Worker may only normalize declared prior files into the new output directory.","Worker must not use retrieval, network, workspace discovery, or subagents."]
        preparation={"manifest_mutated":False,"readable_paths":readable,"prior_attempt_policy":"contract-repair" if args.contract_repair else ("allow" if args.allow_prior_attempts else "deny"),"instructions":instructions,"event_templates":[{"node_id":prior["node_id"],"attempt":expected,"state":"retrying"},{"node_id":prior["node_id"],"attempt":new_attempt,"state":"pending"}]}
        temporary=Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-",dir=output.parent))
        (temporary/"node-input.json").write_text(json.dumps(node_input,indent=2)+"\n",encoding="utf-8")
        (temporary/"retry-preparation.json").write_text(json.dumps(preparation,indent=2)+"\n",encoding="utf-8")
        os.replace(temporary,output); temporary=None
        print(json.dumps({"prepared":True,"output_dir":args.output_dir,"attempt":new_attempt,"manifest_mutated":False},sort_keys=True,separators=(",",":"))); return 0
    except (Invalid,OSError) as exc:
        if temporary is not None: shutil.rmtree(temporary,ignore_errors=True)
        print(json.dumps({"prepared":False,"error":str(exc)},sort_keys=True),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
