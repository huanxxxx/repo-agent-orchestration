# Optional App-task packet adapter

Use this reference only for an explicitly authorized App-task route that benefits from structured packets. Ordinary current-task and internal-agent collaboration uses a small capsule and the host's native result tools; it does not need this schema or an App project id. Repository policy remains the source for paths, models, ownership, continuity, and external gates.

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

Read once for the selected route; refresh changed or ambiguous facts. `TASK_HOST_POLICY: repository_project_local` configures this App adapter only, not whether all work must become an App task. Repository defaults map to `repo_delivery_default`, `repo_write_default`, or `repo_review_default`; `app_default` remains host-selected. `user_explicit:<model>/<reasoning>` is a runtime override, not a repository default.

## One ordinary packet path

Run the installed helper from the repository root. Build the complete initial peer prompt before task creation:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <write|review|design_handoff> --live --launch -
```

Use the resulting packet unchanged as `create_thread.prompt`. For later task messages:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <kind> --live --task-message-to <target-task-id> -
```

`--task-message-to` injects target, intended delivery, and destination-setting fields and emits `send_message_to_thread` JSON after validation. Pass it unchanged; App adds delegation framing. The constructor supplies mechanical defaults but invents no semantic facts. It never creates tasks, touches Git, sends messages, waits, archives, or orchestrates. Stream input to avoid temporary packets and repeated validation. Script success proves packet checks, not authorization, actual delivery, review quality, or task completion.

When checking an incoming structured packet, use:

```text
python .agents/skills/repo-agent-orchestration/scripts/validate_dispatch_contract.py --kind <kind> -
```

The schema file is the field SSoT; the catalog below describes meaning only.

The fresh-context handoff in [continuity.md](continuity.md) reuses a continuity capsule, not another packet kind. The successor verifies actual identity and ownership before writing.

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

Required and optional field order lives in `scripts/packet_schema.py`. Conditional fields include `FULL_REVIEW_REASON` for full review, review evidence/reason for `reopen_approved`, and architected plan/milestone fields.

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

When the user explicitly requests an App task, this adapter uses saved-project `create_thread` with a complete prompt and explicit `environment: {type: "local"}`; later messages use `send_message_to_thread`. This preserves the repository-local execution-worktree choice instead of relying on the host's worktree default. Respect the actual tool schema and permissions. Internal agent ids are never App `TASK_ID`s, and their results use collaboration APIs, not these packets.

## Route and write semantics

Initial packets omit their not-yet-created self id; the App receipt supplies the runtime id. A returned `threadId` confirms creation and initial-prompt delivery, not completion. Never create an inert task or resend the launch. The selected saved-project/local binding validates its actual route before writes; packets live-check Git identity and HEAD. Queued setup or an ambiguous receipt is not proof of a running writer: reconcile it before retrying. Unrelated work can continue.

For write packets, `SOURCE_ROLE: delivery_controller`, `TARGET_ROLE: peer_writer`, and `REPORT_TO_TASK_ID` identifies the controller. `OWNED_PATHS` grants locations only. Passing acceptance is the stop condition: implement the smallest sufficient result, then map each acceptance condition to its changed paths and evidence. Architecture/scope expansion is a blocker requiring the owning authority.

`MODEL_POLICY: app_default` means omit model settings. Explicit model policies must be submitted through the task API only after host capability discovery.

## Review semantics

Review is `READ_ONLY: true` and delta-first. Freeze:

```text
ACCEPTANCE_BASELINE: <criterion ids and source>
THREAT_MODEL: <bounded risks>
NON_GOALS: <excluded outcomes>
```

`delta` requires an exact SHA range. `REVIEW_SCOPE` lists changed paths/clauses. `REVIEW_BUDGET` uses `context=...; checks=...; expand_if=...`. Reuse valid checkpoint evidence unless rerun is required. Expand when a concrete relevant risk, failure, or change justifies it; the budget cannot waive required checks. Delta caps at 5,000 characters.

`full` requires `FULL_REVIEW_REASON`, caps at 9,000 characters, and is only for new, cross-cutting, irreversible, or explicit baselines. Corrections are delta unless the baseline reopens.

Prompt equals route capsule plus packet: no duplicated lineage, package reads, global status, or test matrices. `design` belongs to design authority; `implementation` to delivery; `governance` covers route, takeover, recovery, or protocol questions. Review is read-only and cannot expand scope.

## Architected packet semantics

`DESIGN_HANDOFF` records a design-owner decision. `DESIGN_REVIEW_STATUS: PASS` means independent review was performed; `not_required` needs a concrete risk/requirement reason in `DESIGN_REVIEW_EVIDENCE`. Never use `not_required` when user/repository policy requires independent review or material cross-cutting/irreversible risk calls for it. The helper checks the recorded choice, not whether that judgment is correct. The checkpoint, decisions, acceptance, implementation boundary, and gates constrain delivery; write ownership must be explicit and does not transfer repository-wide merely because a packet was sent.

`DELIVERY_UPDATE` uses `UPDATE_TYPE: plan|milestone|final` and `DECISION_REQUIRED: yes|no`. A plan contains ready set, parallel dispatch, dependency graph, and shared-path owner; a milestone contains only the decision-relevant milestone; final requires `DECISION_REQUIRED: yes`. An informational `DECISION_REQUIRED: no` does not pause authorized work.

`DESIGN_REOPEN_REQUEST` pauses affected scope while design makes the decision. Only `reopen_approved` adds a checkpoint. It requires either independent PASS evidence or explicit `DESIGN_REVIEW_STATUS: not_required` with a concrete reason. For older decision packets, omitted review status retains the PASS requirement. Other decisions are `clarify|continue|hold|reopen_rejected`. Do not invent PASS to satisfy a format.

Correct local shape errors from known facts while preserving meaning, roles, destination, authority, and verdict. Consult the relevant schema on recurring errors; do not send malformed packets or treat formatting as a global stop condition. For incoming errors, recover unambiguous evidence and resolve only material ambiguity before acting. An unavailable optional helper can leave a readable capsule through an authorized channel; it cannot justify bypassing a host denial or explicit structured-route requirement. See [recovery.md](recovery.md).

## Report and checkpoint semantics

`UPDATE_CLASS: implementation` goes to the delivery controller; `design_review` goes to design; `governance_audit` goes to the contracted owner. `progress` carries a decision-relevant fact and does not end work. `blocked` identifies affected scope; `final` supplies acceptance evidence. These are work statuses, not runtime turn controls.

For a write-task `final`, `EVIDENCE` names the local checkpoint commit and maps acceptance to paths/checks. Include `RISKS_OR_LIMITS` or `PENDING_ITEMS` only when there is something material to report; omission never means the constructor inferred `none`. For a governance audit final, `EVIDENCE` separates verified facts, high-confidence inference, and items requiring authority verification. Before a planned pause or handoff, commit each coherent owned unit. If unsafe, report blocked with the exact dirty paths, ownership reason, and recovery action; do not stage another owner's work.

For reports, `--task-message-to` derives `TARGET_TASK_ID`, `DELIVERY`, and `TARGET_SETTINGS: preserve` from the API target and omits destination model/thinking overrides. Task failure is not delivery failure. The contracted report is not lateral contact, but still needs real host authorization. Record actual send success, denial, or uncertainty separately from the packet's intended `DELIVERY`. Retain a failed/uncertain report with `DELIVERY_FAILURE: <reason>` outside it, and use authorized result retrieval where available. Sending an informational report does not end the turn; continue dependency-ready work.
