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

Read once per authority/task binding. Repository defaults map to `repo_delivery_default`, `repo_write_default`, or `repo_review_default`; `app_default` remains host-selected. `user_explicit:<model>/<reasoning>` is a runtime override, not a repository default.

## One ordinary packet path

Run the installed helper from the repository root. Build the complete initial peer prompt before task creation:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <write|review|design_handoff> --live --launch -
```

Use the resulting packet unchanged as `create_thread.prompt`. For later task messages:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <kind> --live --task-message-to <target-task-id> -
```

`--task-message-to` injects target, delivery, and destination-setting fields and emits exact `send_message_to_thread` JSON only on PASS. Pass it unchanged; App adds delegation framing. The constructor supplies invariant defaults but invents no semantic facts. It never creates tasks, touches Git, sends messages, waits, archives, or orchestrates. Use no temporary packet or second validation.

Validate incoming raw packet once:

```text
python .agents/skills/repo-agent-orchestration/scripts/validate_dispatch_contract.py --kind <kind> -
```

The schema file is the field SSoT; the catalog below describes meaning only.

The fresh-context owner rotation in [continuity.md](continuity.md) is not an ordinary peer dispatch. Its compact continuity capsule is the complete successor prompt, and the successor performs the normal task-start identity/repository checks before writing. Do not add a packet kind merely to serialize that capsule. Required peer boundaries and later task messages still use the constructor path above.

## Packet catalog

The human task capsule is small: `OBJECTIVE`, `CONTEXT`, `BOUNDARY`, `ACCEPTANCE`, and `REPORT_TO`. The packet schema adds route, model, archive, and Git facts only so the boundary is reproducible.

| Kind | Direction and purpose |
|---|---|
| `binding` | task startup route identity |
| `write` | delivery controller to peer writer |
| `review` | owning authority to read-only peer reviewer or governance auditor |
| `update` | writer/reviewer/auditor to contracted authority |
| `design_handoff` | design authority to delivery controller |
| `delivery_update` | delivery controller to design authority |
| `design_reopen` | delivery controller asks design authority to change/clarify a boundary |
| `design_decision` | design authority returns the bounded decision |

Required and optional field order lives in `scripts/packet_schema.py`. Keep this reference for meaning, not as a duplicate schema. Conditional fields include `FULL_REVIEW_REASON` for full review, `DESIGN_REVIEW_EVIDENCE` for `reopen_approved`, and the existing architected plan/milestone fields.

## Fixed boundary values

```text
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
TASK_MODE: design_authority|delivery_controller|write|review_root|review_worktree
TARGET_MODE: root_readonly|existing_worktree|detached_snapshot
REVIEW_CLASS: design|implementation|governance
REVIEW_DEPTH: delta|full
UPDATE_CLASS: implementation|design_review|governance_audit
STATUS: progress|blocked|final
MODEL_POLICY: app_default|repo_write_default:<model>/<reasoning>|repo_review_default:<model>/<reasoning>|repo_delivery_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
TARGET_SETTINGS: preserve
```

App peers use saved-project `create_thread` with a complete prompt and explicit `environment: {type: "local"}`; later messages use `send_message_to_thread`. Never rely on the host's Git-project worktree default. `spawn_agent` ids are never peer `TASK_ID`s. Give internal subagents only:

```text
EXECUTION_PATH: inherit_current
OBJECTIVE: <bounded contribution>
OWNED_PATHS: <non-overlapping paths or read_only>
DO_NOT_TOUCH: <sibling scopes>
RETURN: current_turn
```

They inherit authority/path and return this turn. Separate acceptance/model/wait/review/recovery needs an App peer; failed/unavailable routing is `PROTOCOL_BLOCKED`, never an internal substitute.

## Route and write semantics

Initial packets omit their not-yet-created self id; the App receipt supplies the runtime id. The validated packet is `create_thread.prompt`, so a returned `threadId` completes creation and dispatch in one call. Never create an inert task or resend the launch. The peer validates its route and continues in the same initial turn on PASS, otherwise writes nothing. Rebind only if identity changes; packets live-check HEAD.

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

Prompt equals route capsule plus packet: no duplicated lineage, package reads, global status, or test matrices. `design` belongs to design authority; `implementation` to delivery; `governance` covers route, takeover, recovery, or protocol questions. Review is read-only and cannot expand scope.

## Architected packet semantics

`DESIGN_HANDOFF` follows independent design-review PASS and transfers the single repository-root write lease to delivery. Its checkpoint, frozen decisions, non-goals, acceptance, implementation boundary, and gates constrain delivery.

`DELIVERY_UPDATE` uses `UPDATE_TYPE: plan|milestone|final` and `DECISION_REQUIRED: yes|no`. A plan contains ready set, parallel dispatch, dependency graph, and shared-path owner; a milestone contains only the decision-relevant milestone; final requires `DECISION_REQUIRED: yes`. An informational `DECISION_REQUIRED: no` does not pause authorized work.

`DESIGN_REOPEN_REQUEST` pauses affected scope. Design authority creates design review; delivery never proxies it. Pending review needs no interim decision. Only `reopen_approved` adds a checkpoint and requires PASS evidence; other decisions are `clarify|continue|hold|reopen_rejected`.

Before send, correct one constructor shape error once from known facts; meaning, roles, kind, ids, destination, authority, and verdict stay fixed. Repeat failure, incoming validation failure, inexpressible boundary, or attempted/ambiguous delivery is `PROTOCOL_BLOCKED`. Do not relabel the same content or handcraft a bypass.

## Report and checkpoint semantics

`UPDATE_CLASS: implementation` goes to the delivery controller; `design_review` goes to the design authority; `governance_audit` goes only to the authority named by `REPORT_TO`. `progress` carries a new decision fact while the peer turn continues. `blocked` and `final` return control. Do not add owner/turn-state fields.

For a write-task `final`, `EVIDENCE` names the local checkpoint commit and maps acceptance to paths/checks. Include `RISKS_OR_LIMITS` or `PENDING_ITEMS` only when there is something material to report; omission never means the constructor inferred `none`. For a governance audit final, `EVIDENCE` separates verified facts, high-confidence inference, and items requiring authority verification. Before a planned pause or handoff, commit each coherent owned unit. If unsafe, report blocked with the exact dirty paths, ownership reason, and recovery action; do not stage another owner's work.

For reports, `--task-message-to` derives `TARGET_TASK_ID`, `DELIVERY`, and `TARGET_SETTINGS: preserve` from the API target; do not hand-copy them. It omits destination-thread overrides. Task failure is not delivery failure. A reviewer may not message lateral peers, but its required report is not lateral contact. Validate/send once, confirm, and end. A failed call delivered nothing: keep the packet plus `DELIVERY_FAILURE: <reason>` outside it.
