#!/usr/bin/env python3
"""Build validated orchestration packet data without workflow side effects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from packet_schema import PACKET_SCHEMAS, REQUIRED, allowed_fields, packet_header
from validate_dispatch_contract import validate, validate_live


def _string_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return ""
    return str(value).strip()


def build_packet(kind: str, **fields: Any) -> dict[str, str]:
    """Return ordered, statically valid packet fields; perform no I/O or live checks."""
    if kind not in PACKET_SCHEMAS:
        raise ValueError(f"unsupported packet kind: {kind}")
    unknown = sorted(set(fields) - set(allowed_fields(kind)))
    if unknown:
        raise ValueError("unknown packet fields: " + ", ".join(unknown))

    ordered: dict[str, str] = {}
    for name in allowed_fields(kind):
        if name in fields:
            ordered[name] = _string_value(fields[name])
    missing = [name for name in REQUIRED[kind] if name not in ordered]
    if missing:
        raise ValueError("missing packet fields: " + ", ".join(missing))

    errors = validate(kind, ordered)
    if errors:
        raise ValueError("invalid packet: " + "; ".join(errors))
    return ordered


def serialize_packet(kind: str, fields: dict[str, str]) -> str:
    """Serialize packet fields in schema order with a human-readable header."""
    packet = build_packet(kind, **fields)
    lines = [packet_header(kind)]
    lines.extend(f"{name}: {value}" for name, value in packet.items())
    return "\n".join(lines) + "\n"


def binding_packet(**fields: Any) -> dict[str, str]:
    return build_packet("binding", **fields)


def write_packet(**fields: Any) -> dict[str, str]:
    return build_packet("write", **fields)


def review_packet(**fields: Any) -> dict[str, str]:
    return build_packet("review", **fields)


def update_packet(**fields: Any) -> dict[str, str]:
    return build_packet("update", **fields)


def design_handoff_packet(**fields: Any) -> dict[str, str]:
    return build_packet("design_handoff", **fields)


def delivery_plan_packet(**fields: Any) -> dict[str, str]:
    return build_packet("delivery_update", UPDATE_TYPE="plan", **fields)


def delivery_milestone_packet(**fields: Any) -> dict[str, str]:
    return build_packet("delivery_update", UPDATE_TYPE="milestone", **fields)


def delivery_final_packet(**fields: Any) -> dict[str, str]:
    return build_packet("delivery_update", UPDATE_TYPE="final", **fields)


def design_reopen_packet(**fields: Any) -> dict[str, str]:
    return build_packet("design_reopen", **fields)


def design_decision_packet(**fields: Any) -> dict[str, str]:
    return build_packet("design_decision", **fields)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(PACKET_SCHEMAS), required=True)
    parser.add_argument(
        "--live",
        action="store_true",
        help="also verify current filesystem and Git facts before emitting the packet",
    )
    parser.add_argument(
        "fields_json",
        help="UTF-8 JSON object path, or - to read the object from stdin",
    )
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.fields_json == "-" else Path(args.fields_json).read_text(encoding="utf-8")
        fields = json.loads(raw)
        if not isinstance(fields, dict):
            raise ValueError("fields JSON must be an object")
        packet = build_packet(args.kind, **fields)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"INVALID packet input: {exc}", file=sys.stderr)
        return 2

    if args.live:
        errors = validate_live(args.kind, packet)
        if errors:
            print(f"INVALID live {args.kind} packet", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

    print(serialize_packet(args.kind, packet), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
