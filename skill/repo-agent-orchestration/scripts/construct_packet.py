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
from validate_dispatch_contract import (
    has_delegation_framing,
    validate,
    validate_live,
)


TASK_MESSAGE_TARGET_FIELDS = {
    "write": "TASK_ID",
    "review": "REVIEW_TASK_ID",
    "update": "TARGET_TASK_ID",
    "design_handoff": "DELIVERY_TASK_ID",
    "delivery_update": "TARGET_TASK_ID",
    "design_reopen": "TARGET_TASK_ID",
    "design_decision": "TARGET_TASK_ID",
}

LAUNCH_ID_FIELDS = {
    "write": "TASK_ID",
    "review": "REVIEW_TASK_ID",
    "design_handoff": "DELIVERY_TASK_ID",
}
FIELD_ALIASES = {
    "write": {"REPORT_TO": "REPORT_TO_TASK_ID"},
    "review": {"REPORT_TO": "REPORT_TO_TASK_ID"},
    "design_handoff": {"REPORT_TO": "REPORT_TO_TASK_ID"},
    "update": {
        "SOURCE_TASK_ID": "TASK_ID",
        "VERDICT": "SUMMARY",
        "FINDINGS": "EVIDENCE",
    },
}
MECHANICAL_DEFAULTS = {
    "write": {
        "SOURCE_ROLE": "delivery_controller",
        "TARGET_ROLE": "peer_writer",
        "TASK_ENVIRONMENT": "local",
        "TASK_ARCHIVE_POLICY": "dispatching_authority_after_acceptance",
        "MODEL_POLICY": "app_default",
    },
    "review": {
        "TARGET_ROLE": "peer_reviewer",
        "TASK_ENVIRONMENT": "local",
        "TASK_ARCHIVE_POLICY": "dispatching_authority_after_acceptance",
        "READ_ONLY": "true",
        "MODEL_POLICY": "app_default",
    },
    "design_handoff": {
        "ORCHESTRATION_MODE": "architected",
        "SOURCE_ROLE": "design_authority",
        "TARGET_ROLE": "delivery_controller",
        "TASK_ENVIRONMENT": "local",
        "TASK_ARCHIVE_POLICY": "dispatching_authority_after_acceptance",
        "MODEL_POLICY": "app_default",
    },
    "delivery_update": {
        "ORCHESTRATION_MODE": "architected",
        "SOURCE_ROLE": "delivery_controller",
        "TARGET_ROLE": "design_authority",
        "TARGET_SETTINGS": "preserve",
    },
    "design_reopen": {
        "ORCHESTRATION_MODE": "architected",
        "SOURCE_ROLE": "delivery_controller",
        "TARGET_ROLE": "design_authority",
        "TARGET_SETTINGS": "preserve",
    },
    "design_decision": {
        "ORCHESTRATION_MODE": "architected",
        "SOURCE_ROLE": "design_authority",
        "TARGET_ROLE": "delivery_controller",
        "TARGET_SETTINGS": "preserve",
    },
}


def _string_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return ""
    return str(value).strip()


def _normalized_input(kind: str, fields: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(fields)
    for alias, canonical in FIELD_ALIASES.get(kind, {}).items():
        if alias not in normalized:
            continue
        alias_value = _string_value(normalized.pop(alias))
        if canonical in normalized and _string_value(normalized[canonical]) != alias_value:
            raise ValueError(f"conflicting packet fields: {alias} and {canonical}")
        normalized[canonical] = alias_value
    return normalized


def _apply_mechanical_defaults(kind: str, fields: dict[str, Any]) -> None:
    for name, value in MECHANICAL_DEFAULTS.get(kind, {}).items():
        fields.setdefault(name, value)

    if "ORCHESTRATION_MODE" in REQUIRED[kind] and not fields.get(
        "ORCHESTRATION_MODE"
    ):
        architected = bool(fields.get("DESIGN_CHECKPOINT")) or kind in {
            "design_handoff",
            "delivery_update",
            "design_reopen",
            "design_decision",
        }
        fields["ORCHESTRATION_MODE"] = "architected" if architected else "delivery"

    if kind == "review" and not fields.get("SOURCE_ROLE"):
        fields["SOURCE_ROLE"] = (
            "design_authority"
            if fields.get("REVIEW_CLASS") == "design"
            else "delivery_controller"
        )

    if kind == "update":
        update_class = fields.get("UPDATE_CLASS")
        if update_class == "design_review":
            fields.setdefault("SOURCE_ROLE", "peer_reviewer")
            fields.setdefault("TARGET_ROLE", "design_authority")
            fields.setdefault("ORCHESTRATION_MODE", "architected")
        elif update_class == "governance_audit":
            fields.setdefault("SOURCE_ROLE", "peer_reviewer")
            fields.setdefault(
                "TARGET_ROLE",
                "design_authority"
                if fields.get("DESIGN_CHECKPOINT")
                else "delivery_controller",
            )
        elif update_class == "implementation":
            fields.setdefault("SOURCE_ROLE", "peer_writer")
            fields.setdefault("TARGET_ROLE", "delivery_controller")
        fields.setdefault(
            "NEXT",
            {
                "progress": "continue_authorized_scope",
                "blocked": "authority_decision_required",
                "final": "authority_acceptance",
            }.get(_string_value(fields.get("STATUS")), "authority_next_step"),
        )


def _apply_launch_identity(kind: str, fields: dict[str, Any]) -> None:
    identity_field = LAUNCH_ID_FIELDS.get(kind)
    if identity_field is None:
        raise ValueError(
            "launch mode supports only write, review, and design_handoff packets"
        )
    supplied = _string_value(fields.get(identity_field))
    if supplied:
        raise ValueError(
            f"{identity_field} is assigned by create_thread in launch mode; omit it"
        )


def _apply_task_message_target(
    kind: str, fields: dict[str, Any], target_task_id: str
) -> None:
    target_field = TASK_MESSAGE_TARGET_FIELDS.get(kind)
    if target_field is None:
        raise ValueError(f"{kind} packets are not sent through task-message")
    target_task_id = _string_value(target_task_id)
    if not target_task_id:
        raise ValueError("task-message target must identify an actual task")
    supplied = _string_value(fields.get(target_field))
    if supplied and supplied != target_task_id:
        raise ValueError(
            f"task-message target conflicts with packet field {target_field}"
        )
    fields[target_field] = target_task_id
    if "DELIVERY" in allowed_fields(kind):
        fields["DELIVERY"] = f"task_message:{target_task_id}"
    if "TARGET_SETTINGS" in allowed_fields(kind):
        fields["TARGET_SETTINGS"] = "preserve"


def build_packet(
    kind: str,
    *,
    launch: bool = False,
    task_message_target: str | None = None,
    **fields: Any,
) -> dict[str, str]:
    """Return ordered, statically valid packet fields; perform no I/O or live checks."""
    if kind not in PACKET_SCHEMAS:
        raise ValueError(f"unsupported packet kind: {kind}")
    fields = _normalized_input(kind, fields)
    _apply_mechanical_defaults(kind, fields)
    if launch:
        _apply_launch_identity(kind, fields)
    if task_message_target is not None:
        _apply_task_message_target(kind, fields, task_message_target)
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


def _serialize_built_packet(kind: str, packet: dict[str, str]) -> str:
    lines = [packet_header(kind)]
    lines.extend(f"{name}: {value}" for name, value in packet.items())
    return "\n".join(lines) + "\n"


def serialize_packet(
    kind: str,
    fields: dict[str, str],
    *,
    launch: bool = False,
    task_message_target: str | None = None,
) -> str:
    """Serialize packet fields in schema order with a human-readable header."""
    packet = build_packet(
        kind,
        launch=launch,
        task_message_target=task_message_target,
        **fields,
    )
    return _serialize_built_packet(kind, packet)


def launch_prompt(kind: str, **fields: Any) -> str:
    """Return a complete initial create_thread prompt for one peer task."""
    return serialize_packet(kind, fields, launch=True)


def task_message_args(
    kind: str, *, target_task_id: str | None = None, **fields: Any
) -> dict[str, str]:
    """Return exact send_message_to_thread arguments without App-managed framing."""
    target_field = TASK_MESSAGE_TARGET_FIELDS.get(kind)
    if target_field is None:
        raise ValueError(f"{kind} packets are not sent through task-message")
    packet = build_packet(kind, task_message_target=target_task_id, **fields)
    prompt = _serialize_built_packet(kind, packet)
    if has_delegation_framing(prompt):
        raise ValueError("task-message prompt must not contain delegation framing")
    return {"threadId": packet[target_field], "prompt": prompt}


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
        "--task-message",
        action="store_true",
        help=(
            "emit exact send_message_to_thread arguments with a raw packet prompt "
            "and no App-managed delegation framing"
        ),
    )
    parser.add_argument(
        "--task-message-to",
        metavar="TASK_ID",
        help=(
            "inject transport fields and emit exact send_message_to_thread arguments; "
            "the target id stays an API argument instead of a hand-authored packet fact"
        ),
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help=(
            "emit the complete initial create_thread prompt for write, review, or "
            "design_handoff without an inert bootstrap task"
        ),
    )
    parser.add_argument(
        "fields_json",
        help="UTF-8 JSON object path, or - to read the object from stdin",
    )
    args = parser.parse_args()

    if args.launch and (args.task_message or args.task_message_to):
        parser.error("--launch cannot be combined with task-message output")

    try:
        raw = sys.stdin.read() if args.fields_json == "-" else Path(args.fields_json).read_text(encoding="utf-8")
        fields = json.loads(raw)
        if not isinstance(fields, dict):
            raise ValueError("fields JSON must be an object")
        packet = build_packet(
            args.kind,
            launch=args.launch,
            task_message_target=args.task_message_to,
            **fields,
        )
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

    try:
        if args.task_message or args.task_message_to:
            target_field = TASK_MESSAGE_TARGET_FIELDS.get(args.kind)
            if target_field is None:
                raise ValueError(f"{args.kind} packets are not sent through task-message")
            print(
                json.dumps(
                    {
                        "threadId": packet[target_field],
                        "prompt": _serialize_built_packet(args.kind, packet),
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(_serialize_built_packet(args.kind, packet), end="")
    except ValueError as exc:
        print(f"INVALID packet output: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
