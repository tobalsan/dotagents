"""JSON extraction from worker text, schema validation, and retry-prompt building.

Pure functions only: no I/O, no asyncio. Imports nothing from the package
(see DESIGN.md's import graph: `harness` and `schema` import nothing from
`workflow_engine`).
"""

from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
from jsonschema.exceptions import relevance

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class SchemaError(ValueError):
    """A worker reply had no extractable JSON, or failed schema validation."""


def json_instruction(schema: dict[str, Any]) -> str:
    return (
        "\n\n" + json.dumps(schema, indent=2) + "\n\n"
        "Reply with ONLY that JSON object. No prose, no markdown fences."
    )


def _widest_balanced_span(text: str) -> Any | None:
    """Return the value decoded from the widest balanced {…} or […] span in text."""
    decoder = json.JSONDecoder()
    best: Any = None
    best_len = -1
    for i, ch in enumerate(text):
        if ch not in "{[":
            continue
        try:
            obj, end = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            continue
        length = end - i
        if length > best_len:
            best_len = length
            best = obj
    return best if best_len >= 0 else None


def extract_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fence = _FENCE_RE.search(text)
    if fence is not None:
        try:
            return json.loads(fence.group(1).strip())
        except json.JSONDecodeError:
            pass

    span = _widest_balanced_span(text)
    if span is not None:
        return span

    raise SchemaError("no JSON object found in worker reply")


def validate(data: Any, schema: dict[str, Any]) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=relevance)
    if not errors:
        return
    lines = []
    for err in errors[:3]:
        path = ".".join(str(p) for p in err.absolute_path)
        lines.append(f"$.{path}: {err.message}" if path else f"$: {err.message}")
    raise SchemaError("\n".join(lines))


def repair_suffix(error: str, previous: str) -> str:
    return (
        "\n\nYour previous reply was REJECTED by schema validation:\n" + error +
        "\n\nRejected output (first 2000 chars):\n" + previous[:2000] +
        "\n\nReturn the corrected JSON only."
    )
