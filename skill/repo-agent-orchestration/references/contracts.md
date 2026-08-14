# Dispatch, route, and report contracts

Keep only facts that cross a task boundary. Repository policy remains the source for product tiers, paths, models, shared ownership, continuity, and external gates.

## Repository profile

```text
MAIN_BRANCH: <branch>
ROOT_WORKTREE_POLICY: <root role>
WORKTREE_ROOT: <repository-local directory>
BRANCH_PREFIX: <prefix>
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
DELIVERY_CONTROLLER_MODEL: app_default|<explicit model/reasoning>
WRITE_TASK_MODEL: app_default|<explicit model/reasoning>
REVIEW_TASK_MODEL: app_default|<explicit model/reasoning>
SHARED_INTEGRATION_PATHS: <paths>
CONTINUITY_POLICY: none|repository_defined:<entry>
EXTERNAL_GATES: <gates>
```

Read this once per authority/task binding. Repository defaults map to `repo_delivery_default`, `repo_write_default`, or `repo_review_default`; `app_default` remains host-selected. `user_explicit:<model>/<reasoning>` is a runtime override, not a repository default.

## One ordinary packet path

Stream outgoing JSON fields directly to the constructor:

```text
python scripts/construct_packet.py --kind <kind> --live -
```

It shares `scripts/packet_schema.py` with the validator, rejects missing/unknown or contradictory fields, performs live route/Git checks where applicable, and emits text only on PASS. Its library functions stay pure: It never creates tasks, touches Git, sends messages, waits, archives, or orchestrates workflow. Avoid temporary JSON/packet files and do not run a second validator after this command.

Validate an incoming raw packet once with:

```text
python scripts/validate_dispatch_contract.py --kind <kind> -
```

The schema file is the exact required/optional-field SSoT. The compact catalog below describes meaning; do not copy these lists into another implementation.

## Packet catalog

| Kind | Direction and purpose |
|---|---|
| `binding` | task startup route identity |
| `write` | delivery controller to peer writer |
| `review` | owning authority to read-only peer reviewer |
| `update` | writer/reviewer to contracted authority |
| `design_handoff` | design authority to delivery controller |
| `delivery_update` | delivery controller to design authority |
| `design_reopen` | delivery controller asks design authority to change/clarify a boundary |
| `design_decision` | design authority returns the bounded decision |

Required fields, in emitted order:

```text
binding: TASK_ID, TASK_MODE, TASK_ENVIRONMENT, REPOSITORY_ROOT, WORKTREE_ROOT, EXECUTION_PATH, TASK_PROJECT_ID, ACTUAL_THREAD_CWD, ACTUAL_THREAD_PROJECT_ID
write: TASK_ID, ORCHESTRATION_MODE, SOURCE_ROLE, TARGET_ROLE, REPORT_TO_TASK_ID, AUTHORITY_BASELINE, TASK_ENVIRONMENT, TASK_ARCHIVE_POLICY, WORKTREE_ROOT, WORKTREE, BRANCH, BASE_COMMIT, OBJECTIVE, OWNED_PATHS, DO_NOT_TOUCH, ACCEPTANCE, REQUIRED_TESTS, MODEL_POLICY
review: REVIEW_TASK_ID, ORCHESTRATION_MODE, REVIEW_CLASS, REVIEW_DEPTH, SOURCE_ROLE, TARGET_ROLE, REPORT_TO_TASK_ID, TASK_ENVIRONMENT, TASK_ARCHIVE_POLICY, TARGET_MODE, TARGET_PATH, TARGET_COMMIT_OR_RANGE, READ_ONLY, ACCEPTANCE_BASELINE, THREAT_MODEL, NON_GOALS, REVIEW_SCOPE, REVIEW_BUDGET, ACCEPTANCE, MODEL_POLICY
update: TASK_ID, ORCHESTRATION_MODE, UPDATE_CLASS, SOURCE_ROLE, TARGET_ROLE, TARGET_TASK_ID, STATUS, SUMMARY, EVIDENCE, DELIVERY, TARGET_SETTINGS, NEXT
design_handoff: DESIGN_TASK_ID, DELIVERY_TASK_ID, ORCHESTRATION_MODE, SOURCE_ROLE, TARGET_ROLE, REPORT_TO_TASK_ID, TASK_ENVIRONMENT, TASK_ARCHIVE_POLICY, REPOSITORY_ROOT, DESIGN_CHECKPOINT, DESIGN_REVIEW_STATUS, DESIGN_REVIEW_EVIDENCE, OBJECTIVE, AUTHORITATIVE_INPUTS, FROZEN_DECISIONS, NON_GOALS, ACCEPTANCE_BASELINE, IMPLEMENTATION_BOUNDARY, EXTERNAL_GATES, DESIGN_REOPEN_RULE, MODEL_POLICY
delivery_update: DELIVERY_TASK_ID, DESIGN_TASK_ID, ORCHESTRATION_MODE, SOURCE_ROLE, TARGET_ROLE, TARGET_TASK_ID, UPDATE_TYPE, DESIGN_CHECKPOINT, SUMMARY, DESIGN_ALIGNMENT, EVIDENCE, RISKS_OR_LIMITS, PENDING_ITEMS, DECISION_REQUIRED, DELIVERY, TARGET_SETTINGS, NEXT
design_reopen: DELIVERY_TASK_ID, DESIGN_TASK_ID, ORCHESTRATION_MODE, SOURCE_ROLE, TARGET_ROLE, TARGET_TASK_ID, DESIGN_CHECKPOINT, AFFECTED_SCOPE, CONFLICT, EVIDENCE, OPTIONS, RECOMMENDATION, PAUSED_SCOPE, UNAFFECTED_WORK, DELIVERY, TARGET_SETTINGS, NEXT
design_decision: DESIGN_TASK_ID, DELIVERY_TASK_ID, ORCHESTRATION_MODE, SOURCE_ROLE, TARGET_ROLE, TARGET_TASK_ID, PRIOR_DESIGN_CHECKPOINT, DECISION, RATIONALE, UPDATED_DESIGN_CHECKPOINT, AFFECTED_SCOPE, AUTHORITY_BOUNDARY, DELIVERY, TARGET_SETTINGS, NEXT
```

Optional fields are schema-defined, including `FULL_REVIEW_REASON` for full review and `DESIGN_REVIEW_EVIDENCE` for `reopen_approved`; existing architected, non-final, and plan/milestone fields remain conditional.

## Fixed boundary values

```text
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
TASK_MODE: delivery_controller|write|review_root|review_worktree
TARGET_MODE: root_readonly|existing_worktree|detached_snapshot
REVIEW_DEPTH: delta|full
STATUS: progress|blocked|final
MODEL_POLICY: app_default|repo_write_default:<model>/<reasoning>|repo_review_default:<model>/<reasoning>|repo_delivery_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
TARGET_SETTINGS: preserve
```

App peer creation must target the saved project with `environment: {type: "local"}`. An internal subagent does not cross a user-visible boundary; give only:

```text
EXECUTION_PATH: inherit_current
OBJECTIVE: <bounded contribution>
OWNED_PATHS: <non-overlapping paths or read_only>
DO_NOT_TOUCH: <sibling scopes>
RETURN: current_turn
```

It inherits the current task's authority/path and returns this turn. Separate acceptance, model binding, cross-turn waiting, formal review, or recovery requires a peer packet.

## Route and write semantics

The initial peer instruction contains its dispatch plus conditional authority: run `binding` first and continue in the same turn on PASS; on failure, write nothing and report blocked. The task-start binding is not repeated on later wakes unless its task/project/cwd/execution-path facts changed or became ambiguous. Normal commits do not invalidate binding; each new write/review packet live-checks its contracted branch/HEAD.

For write packets, `SOURCE_ROLE: delivery_controller`, `TARGET_ROLE: peer_writer`, and `REPORT_TO_TASK_ID` identifies the controller. `OWNED_PATHS` grants locations only. Passing acceptance is the stop condition: implement the smallest sufficient result, then map each acceptance condition to its changed paths and evidence. Architecture/scope expansion is a blocker requiring the owning authority.

`MODEL_POLICY: app_default` means omit model settings. Explicit model policies must be submitted through the task API only after host capability discovery.

## Review semantics

Review is `READ_ONLY: true` and delta-first. Freeze:

```text
ACCEPTANCE_BASELINE: <criterion ids and source>
THREAT_MODEL: <bounded risks>
NON_GOALS: <excluded outcomes>
```

`delta` requires an exact SHA range. `REVIEW_SCOPE` lists changed paths/clauses. `REVIEW_BUDGET` uses `context=...; checks=...; expand_if=...`. Reuse exact-checkpoint evidence unless rerun is acceptance. Expand once on its cited criterion. Delta caps at 5,000 characters.

`full` requires `FULL_REVIEW_REASON`, caps at 9,000 characters, and is only for new, cross-cutting, irreversible, or explicit baselines. Corrections are delta unless the baseline reopens.

Prompt equals route capsule plus packet: no duplicated lineage, package reads, global status, or test matrices. `design` belongs to design authority; `implementation` to delivery. Review is read-only and cannot expand scope.

## Architected packet semantics

`DESIGN_HANDOFF` follows independent design-review PASS and transfers the single repository-root write lease to delivery. Its checkpoint, frozen decisions, non-goals, acceptance, implementation boundary, and gates constrain delivery.

`DELIVERY_UPDATE` uses `UPDATE_TYPE: plan|milestone|final` and `DECISION_REQUIRED: yes|no`. A plan contains ready set, parallel dispatch, dependency graph, and shared-path owner; a milestone contains only the decision-relevant milestone; final requires `DECISION_REQUIRED: yes`. An informational `DECISION_REQUIRED: no` does not pause authorized work.

`DESIGN_REOPEN_REQUEST` pauses affected scope. Design authority creates design review; delivery never proxies it. Pending review needs no interim decision. Only `reopen_approved` adds a checkpoint and requires PASS evidence; other decisions are `clarify|continue|hold|reopen_rejected`.

Constructor or validator failure marks only that dependent boundary `PROTOCOL_BLOCKED`. Do not relabel the same content; source role, packet kind, and task id are immutable. Do not handcraft a bypass or treat local classification as authority.

## Report and checkpoint semantics

`UPDATE_CLASS: implementation` goes to the delivery controller; `design_review` goes to the design authority. `progress` carries a new decision fact while the peer turn continues. `blocked` and `final` return control. Do not add owner/turn-state fields.

For a write-task `final`, `EVIDENCE` names the local checkpoint commit and maps acceptance to paths/checks; `RISKS_OR_LIMITS` and `PENDING_ITEMS` are mandatory. Before a planned pause or handoff, commit each coherent owned unit. If unsafe, report blocked with the exact dirty paths, ownership reason, and recovery action; do not stage another owner's work.

`DELIVERY` is `task_message:<TARGET_TASK_ID>` except a local delivery failure, which is `blocked:<reason>`. `TARGET_SETTINGS: preserve` means task-message calls omit `model` and `thinking`; those are destination-thread overrides. Validate, send once, confirm delivery, then end the sender turn. If delivery fails, preserve the local blocked report for recovery on the next real wake.
