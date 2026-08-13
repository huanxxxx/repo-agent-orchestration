#!/usr/bin/env python3
"""Declarative field order for repository orchestration packets."""

from __future__ import annotations


PACKET_SCHEMAS: dict[str, dict[str, tuple[str, ...] | str]] = {
    "binding": {
        "header": "ROUTE_BINDING",
        "required": (
            "TASK_ID",
            "TASK_MODE",
            "TASK_ENVIRONMENT",
            "REPOSITORY_ROOT",
            "WORKTREE_ROOT",
            "EXECUTION_PATH",
            "TASK_PROJECT_ID",
            "ACTUAL_THREAD_CWD",
            "ACTUAL_THREAD_PROJECT_ID",
        ),
        "optional": (),
    },
    "write": {
        "header": "PEER_WRITE_DISPATCH",
        "required": (
            "TASK_ID",
            "ORCHESTRATION_MODE",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "REPORT_TO_TASK_ID",
            "AUTHORITY_BASELINE",
            "TASK_ENVIRONMENT",
            "TASK_ARCHIVE_POLICY",
            "WORKTREE_ROOT",
            "WORKTREE",
            "BRANCH",
            "BASE_COMMIT",
            "OBJECTIVE",
            "OWNED_PATHS",
            "DO_NOT_TOUCH",
            "ACCEPTANCE",
            "REQUIRED_TESTS",
            "MODEL_POLICY",
        ),
        "optional": ("DESIGN_CHECKPOINT",),
    },
    "review": {
        "header": "READ_ONLY_REVIEW_DISPATCH",
        "required": (
            "REVIEW_TASK_ID",
            "ORCHESTRATION_MODE",
            "REVIEW_CLASS",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "REPORT_TO_TASK_ID",
            "TASK_ENVIRONMENT",
            "TASK_ARCHIVE_POLICY",
            "TARGET_MODE",
            "TARGET_PATH",
            "TARGET_COMMIT_OR_RANGE",
            "READ_ONLY",
            "ACCEPTANCE_BASELINE",
            "THREAT_MODEL",
            "NON_GOALS",
            "REVIEW_SCOPE",
            "ACCEPTANCE",
            "MODEL_POLICY",
        ),
        "optional": ("DESIGN_CHECKPOINT",),
    },
    "update": {
        "header": "TASK_UPDATE",
        "required": (
            "TASK_ID",
            "ORCHESTRATION_MODE",
            "UPDATE_CLASS",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "TARGET_TASK_ID",
            "STATUS",
            "SUMMARY",
            "EVIDENCE",
            "DELIVERY",
            "TARGET_SETTINGS",
            "NEXT",
        ),
        "optional": (
            "DESIGN_CHECKPOINT",
            "RISKS_OR_LIMITS",
            "PENDING_ITEMS",
        ),
    },
    "design_handoff": {
        "header": "DESIGN_HANDOFF",
        "required": (
            "DESIGN_TASK_ID",
            "DELIVERY_TASK_ID",
            "ORCHESTRATION_MODE",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "REPORT_TO_TASK_ID",
            "TASK_ENVIRONMENT",
            "TASK_ARCHIVE_POLICY",
            "REPOSITORY_ROOT",
            "DESIGN_CHECKPOINT",
            "DESIGN_REVIEW_STATUS",
            "DESIGN_REVIEW_EVIDENCE",
            "OBJECTIVE",
            "AUTHORITATIVE_INPUTS",
            "FROZEN_DECISIONS",
            "NON_GOALS",
            "ACCEPTANCE_BASELINE",
            "IMPLEMENTATION_BOUNDARY",
            "EXTERNAL_GATES",
            "DESIGN_REOPEN_RULE",
            "MODEL_POLICY",
        ),
        "optional": (),
    },
    "delivery_update": {
        "header": "DELIVERY_UPDATE",
        "required": (
            "DELIVERY_TASK_ID",
            "DESIGN_TASK_ID",
            "ORCHESTRATION_MODE",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "TARGET_TASK_ID",
            "UPDATE_TYPE",
            "DESIGN_CHECKPOINT",
            "SUMMARY",
            "DESIGN_ALIGNMENT",
            "EVIDENCE",
            "RISKS_OR_LIMITS",
            "PENDING_ITEMS",
            "DECISION_REQUIRED",
            "DELIVERY",
            "TARGET_SETTINGS",
            "NEXT",
        ),
        "optional": (
            "READY_SET",
            "PARALLEL_DISPATCH",
            "DEPENDENCY_GRAPH",
            "SHARED_PATH_OWNER",
            "MILESTONE",
        ),
    },
    "design_reopen": {
        "header": "DESIGN_REOPEN_REQUEST",
        "required": (
            "DELIVERY_TASK_ID",
            "DESIGN_TASK_ID",
            "ORCHESTRATION_MODE",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "TARGET_TASK_ID",
            "DESIGN_CHECKPOINT",
            "AFFECTED_SCOPE",
            "CONFLICT",
            "EVIDENCE",
            "OPTIONS",
            "RECOMMENDATION",
            "PAUSED_SCOPE",
            "UNAFFECTED_WORK",
            "DELIVERY",
            "TARGET_SETTINGS",
            "NEXT",
        ),
        "optional": (),
    },
    "design_decision": {
        "header": "DESIGN_DECISION",
        "required": (
            "DESIGN_TASK_ID",
            "DELIVERY_TASK_ID",
            "ORCHESTRATION_MODE",
            "SOURCE_ROLE",
            "TARGET_ROLE",
            "TARGET_TASK_ID",
            "PRIOR_DESIGN_CHECKPOINT",
            "DECISION",
            "RATIONALE",
            "UPDATED_DESIGN_CHECKPOINT",
            "AFFECTED_SCOPE",
            "AUTHORITY_BOUNDARY",
            "DELIVERY",
            "TARGET_SETTINGS",
            "NEXT",
        ),
        "optional": (),
    },
}


REQUIRED: dict[str, tuple[str, ...]] = {
    kind: schema["required"]  # type: ignore[assignment]
    for kind, schema in PACKET_SCHEMAS.items()
}


def allowed_fields(kind: str) -> tuple[str, ...]:
    schema = PACKET_SCHEMAS[kind]
    required = schema["required"]
    optional = schema["optional"]
    assert isinstance(required, tuple) and isinstance(optional, tuple)
    return required + optional


def packet_header(kind: str) -> str:
    header = PACKET_SCHEMAS[kind]["header"]
    assert isinstance(header, str)
    return header
