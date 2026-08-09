#!/usr/bin/env python3
"""Materialize an exact worker contract packet for one node attempt."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path

from validate_node_result import DEFAULT_SCHEMA, Invalid, load, validate_input, validate_result, validate_schema

VALIDATOR = Path(__file__).with_name("validate_node_result.py")


def write_once(path: Path, content: str) -> None:
    if path.exists():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise Invalid(f"contract file already exists with different content: {path.name}")
        return
    path.write_text(content, encoding="utf-8")


def run(input_path: Path, artifact_root: Path) -> dict[str, str]:
    node_input = validate_input(load(input_path))
    schema_path = DEFAULT_SCHEMA
    validate_schema(schema_path)
    root = artifact_root.resolve()
    output = (root / node_input["output_dir"]).resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise Invalid("output_dir escapes artifact root") from exc
    if input_path.resolve() != output / "node-input.json":
        raise Invalid("input must be exactly output_dir/node-input.json")
    output.mkdir(parents=True, exist_ok=True)

    schema_name = "node-execution-v1.schema.json"
    validator_name = "validate_node_result.py"
    template_name = "node-result.template.json"
    command_name = "self-validate.sh"
    contract_name = "worker-contract.json"

    write_once(output / schema_name, schema_path.read_text(encoding="utf-8"))
    write_once(output / validator_name, VALIDATOR.read_text(encoding="utf-8"))

    template = {
        "iteration_id": node_input["iteration_id"],
        "node_id": node_input["node_id"],
        "node_kind": node_input["node_kind"],
        "attempt": node_input["attempt"],
        "status": "completed",
        "summary": "REPLACE WITH COMPLETION SUMMARY",
        "artifacts": {},
        "sources": [],
        "citations": [],
    }
    if "lane" in node_input:
        template["lane"] = node_input["lane"]
    validate_result(template)
    write_once(output / template_name, json.dumps(template, indent=2) + "\n")

    root_arg = shlex.quote(str(root))
    script = f'''#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec uv run --no-project python "$HERE/{validator_name}" \\
  --input "$HERE/node-input.json" \\
  --result "$HERE/node-result.json" \\
  --schema "$HERE/{schema_name}" \\
  --artifact-root {root_arg} \\
  --process-exit 0
'''
    write_once(output / command_name, script)
    os.chmod(output / command_name, 0o755)

    contract = {
        "schema": schema_name,
        "template": template_name,
        "validator": validator_name,
        "self_validation_command": f"./{command_name}",
        "requirements": [
            "Read the exact schema and template before substantive work.",
            "Write node-result.json using only schema-permitted fields.",
            "Run the self-validation command before exit.",
            "Do not report completion unless self-validation returns valid true.",
        ],
    }
    write_once(output / contract_name, json.dumps(contract, indent=2) + "\n")
    return {
        "contract": str(output / contract_name),
        "schema": str(output / schema_name),
        "template": str(output / template_name),
        "self_validation": str(output / command_name),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--artifact-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run(args.input, args.artifact_root), sort_keys=True, separators=(",", ":")))
        return 0
    except (Invalid, OSError, UnicodeError) as exc:
        print(json.dumps({"prepared": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
