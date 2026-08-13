# Dispatch, route, and report contracts

Use repository policy before these templates. Keep only facts that cross a task boundary; do not repeat controller-only state in every packet.

- [Repository profile](#repository-profile)
- [Packet construction](#packet-construction)
- [Internal subagent handoff](#internal-subagent-handoff)
- [Peer write-task dispatch](#peer-write-task-dispatch)
- [Read-only review dispatch](#read-only-review-dispatch)
- [Architected delivery packets](#architected-delivery-packets)
- [Fast route gate](#fast-route-gate)
- [Task report](#task-report)

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
CONTINUITY_POLICY: none|repository_defined:<index or entry>
EXTERNAL_GATES: <gates>
```

Each authority reads repository configuration once for its role. Pass only cross-boundary facts in task packets; do not copy invariant wait, root-write, or integration policy into every packet.

`DELIVERY_CONTROLLER_MODEL`, `WRITE_TASK_MODEL`, and `REVIEW_TASK_MODEL` translate to `repo_delivery_default`, `repo_write_default`, and `repo_review_default` packet policies. `app_default` stays `app_default`. `user_explicit:<model>/<reasoning>` is reserved for a user runtime override and is not stored as the repository default.

Repository-local tiers may map to `direct`, `delivery`, or `architected`; keep that mapping in repository policy. Without a local mapping, choose from task facts using [architected.md](architected.md). `direct` creates no cross-task packet.

## Packet construction

Use `scripts/construct_packet.py` or its pure functions for every new cross-task packet. It reads the declarative field order from `scripts/packet_schema.py`, performs static validation, and returns data or text only. It never creates tasks, touches Git, sends messages, waits, archives, or performs live path checks.

```text
build_packet(kind, **fields) -> dict[str, str]
write_packet(...) / review_packet(...) / update_packet(...)
design_handoff_packet(...) / design_reopen_packet(...) / design_decision_packet(...)
delivery_plan_packet(...) / delivery_milestone_packet(...) / delivery_final_packet(...)
```

Run `validate_dispatch_contract.py` at the actual dispatch or report boundary for live checks. The constructor reduces handwritten shape and routing errors; it does not prove repository state or workflow completion.

Constructor or validator failure closes that task boundary as `PROTOCOL_BLOCKED`. Do not relabel the same content as `plan`, `milestone`, `final`, or a generic update to evade the failure, and do not handcraft a packet that bypasses the shared schema. Report the protocol defect in the current task and stop only the affected routing or acceptance action; unrelated authorized work may continue only when it has no dependency on that boundary.

## Internal subagent handoff

Internal subagents do not cross a user-visible task boundary, so do not give them a branch, worktree, App task, model-binding, or task-report contract. Give only the current-turn facts they need:

```text
EXECUTION_PATH: inherit_current
OBJECTIVE: <bounded contribution to the owning current task>
OWNED_PATHS: <non-overlapping paths, or read_only>
DO_NOT_TOUCH: <sibling scopes>
RETURN: current_turn
```

The owning current task is the internal subagent's parent and owns acceptance and recovery. Writing is allowed only when that task already owns the execution path and write authority. If the work needs independent acceptance, a separate model, cross-turn waiting, or its own recovery coordinate, use a peer write dispatch instead.

## Peer write-task dispatch

```text
TASK_ID: <id or pending>
ORCHESTRATION_MODE: delivery|architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: peer_writer
REPORT_TO_TASK_ID: <delivery-controller task id>
AUTHORITY_BASELINE: <user/repository acceptance or frozen design reference>
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
WORKTREE_ROOT: <absolute repository-local root>
WORKTREE: <absolute existing worktree>
BRANCH: <task branch>
BASE_COMMIT: <full sha>
OBJECTIVE: <one independently accepted outcome>
OWNED_PATHS: <exclusive write paths>
DO_NOT_TOUCH: <shared or excluded paths>
ACCEPTANCE: <observable conditions>
REQUIRED_TESTS: <commands or checks>
MODEL_POLICY: app_default|repo_write_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
DESIGN_CHECKPOINT: <full sha; required only in architected mode>
```

These fields are the implementation boundary. `OWNED_PATHS` grants locations, not permission to redesign everything inside them. Implement the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`; do not add unrequired features, abstractions, alternate paths, refactors, or hardening. If the accepted outcome requires crossing that boundary, report `blocked` with the conflict and request reauthorization rather than expanding scope. Passing acceptance is the stop condition.

Create and verify one worktree for the peer write task only when it is ready. Create the visible peer with `target: {type: "project", projectId: <saved-project-id>, environment: {type: "local"}}`; never use or omit into the Git-project default of `worktree`. If a same-task fork or internal subagent is genuinely required, it inherits the owning task's execution path and must never request `worktree`. For `app_default`, omit `model` and `thinking`. For an explicit binding, confirm the destination host advertises the requested model, then submit it through the real task API only while creating or continuing this peer write task; do not guess compatibility from the source task's model family. The initial task instruction grants execution conditionally: run the fast route gate first, continue in the same turn when it passes, and report `blocked` without writing when it fails. In `architected`, every writer inherits the exact frozen `DESIGN_CHECKPOINT` and still reports only to the delivery controller.

## Read-only review dispatch

```text
REVIEW_TASK_ID: <id or pending>
ORCHESTRATION_MODE: delivery|architected
REVIEW_CLASS: design|implementation
SOURCE_ROLE: design_authority|delivery_controller
TARGET_ROLE: peer_reviewer
REPORT_TO_TASK_ID: <dispatching authority task id>
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
TARGET_MODE: root_readonly|existing_worktree|detached_snapshot
TARGET_PATH: <absolute path>
TARGET_COMMIT_OR_RANGE: <full sha or exact range>
READ_ONLY: true
ACCEPTANCE_BASELINE: <frozen criterion IDs and authoritative references>
THREAT_MODEL: <bounded actors and failures covered by the baseline>
NON_GOALS: <excluded hardening or none>
REVIEW_SCOPE: <requirements and risk surface>
ACCEPTANCE: <PASS/FAIL only against the frozen baseline>
MODEL_POLICY: app_default|repo_review_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
DESIGN_CHECKPOINT: <full sha; required only in architected mode>
```

- `root_readonly`: use only for a stable committed root and a short review that neither writes nor needs a frozen filesystem across turns.
- `existing_worktree`: reuse the frozen implementation worktree. The implementation owner pauses until review ends.
- `detached_snapshot`: the dispatching authority creates an on-demand detached worktree below `WORKTREE_ROOT` for a long, cross-turn, test-running, or historical review. The reviewer never creates it.

`REVIEW_CLASS: design` is valid only in `architected` mode, is dispatched by `design_authority`, and reports back there. `REVIEW_CLASS: implementation` is dispatched by and reports to `delivery_controller` in either cross-task mode.

A reviewer never modifies files, the index, commits, or external state. Review tests must be explicitly safe for the selected target; otherwise use a disposable detached snapshot.

The baseline is immutable for the review cycle. Every blocking finding must contain a stable finding ID, severity, violated acceptance ID, reproducible evidence, and impact within `THREAT_MODEL`. If it cannot cite a frozen criterion, place it under non-blocking observations even when it is useful hardening. A potentially critical out-of-baseline issue becomes a scope-reopen request to the dispatching authority; it does not silently rewrite the current verdict or authorize a writer.

The reviewer reports `PASS` when the frozen baseline has no blocking finding. On correction review, recheck accepted finding IDs and regressions against that same baseline. The dispatching authority adjudicates findings before sending any correction and performs a scope-drift audit instead of automatically starting a third correction cycle when two consecutive reviews introduce new accepted blockers.

## Architected delivery packets

Use these only with `ORCHESTRATION_MODE: architected`. All task-message packets use `TARGET_SETTINGS: preserve` and omit `model` and `thinking` from the actual message call.

### Design handoff

```text
DESIGN_HANDOFF
DESIGN_TASK_ID: <actual design-authority task id>
DELIVERY_TASK_ID: <id or pending>
ORCHESTRATION_MODE: architected
SOURCE_ROLE: design_authority
TARGET_ROLE: delivery_controller
REPORT_TO_TASK_ID: <design-authority task id>
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: dispatching_authority_after_acceptance
REPOSITORY_ROOT: <absolute repository root>
DESIGN_CHECKPOINT: <full sha>
DESIGN_REVIEW_STATUS: PASS
DESIGN_REVIEW_EVIDENCE: <review task, target, and verdict evidence>
OBJECTIVE: <product outcome>
AUTHORITATIVE_INPUTS: <repository and user facts>
FROZEN_DECISIONS: <decisions the delivery controller cannot reopen>
NON_GOALS: <excluded scope>
ACCEPTANCE_BASELINE: <stable criterion IDs>
IMPLEMENTATION_BOUNDARY: <allowed delivery scope>
EXTERNAL_GATES: <still-closed gates>
DESIGN_REOPEN_RULE: <when affected delivery must return to design authority>
MODEL_POLICY: app_default|repo_delivery_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
```

The design authority sends this only after the design candidate is committed and an independent design review passes. The handoff also transfers the single repository-root write lease to the delivery controller; the design authority remains read-only there during ordinary delivery. A prompt that merely calls a task “chief engineer” is not a handoff.

`TASK_ARCHIVE_POLICY` names the role that crossed the task boundary: the delivery controller archives accepted writer/reviewer peers, while the design authority archives an accepted delivery-controller peer. No task archives itself.

### Delivery plan, milestone, or final

```text
DELIVERY_UPDATE
DELIVERY_TASK_ID: <actual delivery-controller task id>
DESIGN_TASK_ID: <design-authority task id>
ORCHESTRATION_MODE: architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: design_authority
TARGET_TASK_ID: <design-authority task id>
UPDATE_TYPE: plan|milestone|final
DESIGN_CHECKPOINT: <full sha>
SUMMARY: <decision-relevant fact>
DESIGN_ALIGNMENT: <mapping to the frozen design>
EVIDENCE: <commits, checks, or task evidence>
RISKS_OR_LIMITS: <remaining limits or none>
PENDING_ITEMS: <remaining work or none>
READY_SET: <currently dependency-ready outcomes; required for plan>
PARALLEL_DISPATCH: <independent peers dispatched; required for plan>
DECISION_REQUIRED: yes|no
DEPENDENCY_GRAPH: <required for plan>
SHARED_PATH_OWNER: <required for plan>
MILESTONE: <required for milestone>
DELIVERY: task_message:<design-authority task id>
TARGET_SETTINGS: preserve
NEXT: <next action>
```

Do not send routine peer progress. `DECISION_REQUIRED: no` is informational and does not pause authorized work inside the frozen design. A final update always uses `yes` because the design authority owns final design-consistency acceptance.

The three delivery variants are exclusive: `plan` requires the four planning fields and omits `MILESTONE`; `milestone` requires `MILESTONE` and omits the planning fields; `final` omits both sets. If the declared variant cannot carry the intended fact, stop with `PROTOCOL_BLOCKED` instead of changing its label.

### Design reopen request and decision

```text
DESIGN_REOPEN_REQUEST
DELIVERY_TASK_ID: <delivery-controller task id>
DESIGN_TASK_ID: <design-authority task id>
ORCHESTRATION_MODE: architected
SOURCE_ROLE: delivery_controller
TARGET_ROLE: design_authority
TARGET_TASK_ID: <design-authority task id>
DESIGN_CHECKPOINT: <full sha>
AFFECTED_SCOPE: <scope and dependents>
CONFLICT: <false assumption or required boundary change>
EVIDENCE: <reproducible evidence>
OPTIONS: <bounded alternatives>
RECOMMENDATION: <delivery controller recommendation>
PAUSED_SCOPE: <paused affected work>
UNAFFECTED_WORK: <independent work that may continue or none>
DELIVERY: task_message:<design-authority task id>
TARGET_SETTINGS: preserve
NEXT: await design decision for affected scope
```

```text
DESIGN_DECISION
DESIGN_TASK_ID: <design-authority task id>
DELIVERY_TASK_ID: <delivery-controller task id>
ORCHESTRATION_MODE: architected
SOURCE_ROLE: design_authority
TARGET_ROLE: delivery_controller
TARGET_TASK_ID: <delivery-controller task id>
PRIOR_DESIGN_CHECKPOINT: <full sha>
DECISION: clarify|continue|hold|reopen_approved|reopen_rejected
RATIONALE: <evidence and tradeoff>
UPDATED_DESIGN_CHECKPOINT: unchanged|<new full sha>
AFFECTED_SCOPE: <scope covered by the decision>
AUTHORITY_BOUNDARY: <what this decision does and does not authorize>
DELIVERY: task_message:<delivery-controller task id>
TARGET_SETTINGS: preserve
NEXT: <next action>
```

`reopen_approved` requires a new committed design checkpoint. Before creating it, require evidence that root integration is stopped, delivery-owned root changes are checkpointed, and root status is reconciled with its recorded baseline; isolated unaffected peers may keep working but may not integrate. The design authority must make a professional recommendation, but it must not turn a reopen decision into an unbounded redesign. An accepted final does not need a `DESIGN_DECISION` that wakes a completed delivery task: verify final consistency, archive the accepted delivery-controller peer, and report completion. Send a decision packet only when delivery must resume, change, clarify, or hold.

## Fast route gate

Run this at the start of the task and continue in the same turn when it passes:

```text
TASK_ID: <actual id>
TASK_MODE: delivery_controller|write|review_root|review_worktree
TASK_ENVIRONMENT: local
REPOSITORY_ROOT: <absolute root>
WORKTREE_ROOT: <absolute repository-local worktree root>
EXECUTION_PATH: <absolute root or worktree>
TASK_PROJECT_ID: <saved repository project id>
ACTUAL_THREAD_CWD: <actual task cwd>
ACTUAL_THREAD_PROJECT_ID: <actual project id>
```

The submitted task environment must be exactly `local`, the actual cwd must equal `REPOSITORY_ROOT`, and both project ids must be non-null and equal. `write` and `review_worktree` execution paths must be strict descendants of `WORKTREE_ROOT`; `delivery_controller` and `review_root` must equal `REPOSITORY_ROOT`.

Run the validator CLI on the packet immediately before dispatch and again for the task's fast route gate. The CLI fails closed unless each required path exists and the selected worktree is registered at the contracted branch/commit. A path remembered by a task or chat is only a hint: after cleanup or restore, validate it again before treating it as a baseline. Record the repository-root status before the task starts and verify that the task did not change it; unrelated pre-existing root changes do not by themselves block an isolated task.

## Task report

```text
TASK_UPDATE
TASK_ID: <id>
ORCHESTRATION_MODE: delivery|architected
UPDATE_CLASS: implementation|design_review
SOURCE_ROLE: peer_writer|peer_reviewer
TARGET_ROLE: delivery_controller|design_authority
TARGET_TASK_ID: <contracted report destination task id>
STATUS: progress|blocked|final
SUMMARY: <new fact only>
EVIDENCE: <commands, commit, paths, findings, or none>
RISKS_OR_LIMITS: <required for final>
PENDING_ITEMS: <required for final>
DELIVERY: task_message:<target-task-id>|blocked:<reason>
TARGET_SETTINGS: preserve
NEXT: <next action>
DESIGN_CHECKPOINT: <full sha; required only in architected mode>
```

`progress` is optional and means the same peer turn continues. `blocked` and `final` end the peer turn and return control to the contracted authority. `implementation` reports go to the delivery controller; `design_review` reports go to the design authority. `TARGET_TASK_ID` must equal the task id in `DELIVERY`. Do not duplicate this with separate owner or turn-state fields.

For a write-task `final`, `EVIDENCE` must name the local checkpoint commit and concisely map each acceptance condition to its changed paths and verification evidence. Before a planned pause or handoff, commit every coherent task-owned unit even when the broader task continues later. If a safe commit is impossible, use `blocked` and put the exact dirty paths, ownership issue, and recovery action in `EVIDENCE`, `RISKS_OR_LIMITS`, and `NEXT`. Never hide recoverable work behind `none`, and never stage another owner's files merely to satisfy this boundary. Put optional hardening under `RISKS_OR_LIMITS` without implementing it under the completed task.

`TARGET_SETTINGS: preserve` is mandatory. When sending the report, omit both `model` and `thinking` from the task-message call. These are destination-thread overrides, not sender metadata; attaching the sender model changes the destination task. Model overrides are allowed only when creating or continuing the task whose policy authorizes that model.

```text
send_message_to_thread({threadId: <TARGET_TASK_ID>, prompt: <validated-report>})
```

Validate the report, send it through the task-message capability without target-setting overrides, and confirm delivery before the task emits its local final. If delivery fails, emit a local `blocked` report with `DELIVERY: blocked:<reason>` and `TARGET_SETTINGS: preserve`; recover it on the next real controller wake. Do not claim that an immediate snapshot is a future missing-report check.
