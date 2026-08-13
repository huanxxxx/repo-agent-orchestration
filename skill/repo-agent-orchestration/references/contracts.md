# Dispatch, route, and report contracts

Use repository policy before these templates. Keep only facts that cross a task boundary; do not repeat controller-only state in every packet.

## Repository profile

```text
MAIN_BRANCH: <branch>
ROOT_WORKTREE_POLICY: <root role>
WORKTREE_ROOT: <repository-local directory>
BRANCH_PREFIX: <prefix>
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
WRITE_TASK_MODEL: app_default|<explicit model/reasoning>
REVIEW_TASK_MODEL: app_default|<explicit model/reasoning>
SHARED_INTEGRATION_PATHS: <paths>
CONTINUITY_POLICY: none|repository_defined:<index or entry>
EXTERNAL_GATES: <gates>
```

Repository configuration is read once by the controller. Do not copy invariant wait policy, root-write policy, or integration policy into every peer-task packet.

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
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: controller_after_acceptance
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
```

These fields are the implementation boundary. `OWNED_PATHS` grants locations, not permission to redesign everything inside them. Implement the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`; do not add unrequired features, abstractions, alternate paths, refactors, or hardening. If the accepted outcome requires crossing that boundary, report `blocked` with the conflict and request reauthorization rather than expanding scope. Passing acceptance is the stop condition.

Create and verify one worktree for the peer write task only when it is ready. Create the visible peer with `target: {type: "project", projectId: <saved-project-id>, environment: {type: "local"}}`; never use or omit into the Git-project default of `worktree`. If a same-task fork or internal subagent is genuinely required, it inherits the owning task's execution path and must never request `worktree`. For `app_default`, omit `model` and `thinking`. For an explicit binding, confirm the destination host advertises the requested model, then submit it through the real task API only while creating or continuing this peer write task; do not guess compatibility from the controller model family. The initial task instruction grants execution conditionally: run the fast route gate first, continue in the same turn when it passes, and report `blocked` without writing when it fails.

## Read-only review dispatch

```text
REVIEW_TASK_ID: <id or pending>
TASK_ENVIRONMENT: local
TASK_ARCHIVE_POLICY: controller_after_acceptance
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
```

- `root_readonly`: use only for a stable committed root and a short review that neither writes nor needs a frozen filesystem across turns.
- `existing_worktree`: reuse the frozen implementation worktree. The implementation owner pauses until review ends.
- `detached_snapshot`: the controller creates an on-demand detached worktree below `WORKTREE_ROOT` for a long, cross-turn, test-running, or historical review. The reviewer never creates it.

A reviewer never modifies files, the index, commits, or external state. Review tests must be explicitly safe for the selected target; otherwise use a disposable detached snapshot.

The baseline is immutable for the review cycle. Every blocking finding must contain a stable finding ID, severity, violated acceptance ID, reproducible evidence, and impact within `THREAT_MODEL`. If it cannot cite a frozen criterion, place it under non-blocking observations even when it is useful hardening. A potentially critical out-of-baseline issue becomes a scope-reopen request to the controller; it does not silently rewrite the current verdict or authorize a writer.

The reviewer reports `PASS` when the frozen baseline has no blocking finding. On correction review, recheck accepted finding IDs and regressions against that same baseline. The controller adjudicates findings before sending any correction and performs a scope-drift audit instead of automatically starting a third correction cycle when two consecutive reviews introduce new accepted blockers.

## Fast route gate

Run this at the start of the task and continue in the same turn when it passes:

```text
TASK_ID: <actual id>
TASK_MODE: write|review_root|review_worktree
TASK_ENVIRONMENT: local
REPOSITORY_ROOT: <absolute root>
WORKTREE_ROOT: <absolute repository-local worktree root>
EXECUTION_PATH: <absolute root or worktree>
TASK_PROJECT_ID: <saved repository project id>
ACTUAL_THREAD_CWD: <actual task cwd>
ACTUAL_THREAD_PROJECT_ID: <actual project id>
```

The submitted task environment must be exactly `local`, the actual cwd must equal `REPOSITORY_ROOT`, and both project ids must be non-null and equal. `write` and `review_worktree` execution paths must be strict descendants of `WORKTREE_ROOT`; `review_root` must equal `REPOSITORY_ROOT`.

Run the validator CLI on the packet immediately before dispatch and again for the task's fast route gate. The CLI fails closed unless each required path exists and the selected worktree is registered at the contracted branch/commit. A path remembered by a task or chat is only a hint: after cleanup or restore, validate it again before treating it as a baseline. Record the repository-root status before the task starts and verify that the task did not change it; unrelated pre-existing root changes do not by themselves block an isolated task.

## Task report

```text
TASK_UPDATE
TASK_ID: <id>
STATUS: progress|blocked|final
SUMMARY: <new fact only>
EVIDENCE: <commands, commit, paths, findings, or none>
RISKS_OR_LIMITS: <required for final>
PENDING_ITEMS: <required for final>
DELIVERY: task_message:<controller-task-id>|blocked:<reason>
TARGET_SETTINGS: preserve
NEXT: <next action>
```

`progress` is optional and means the same peer turn continues. `blocked` and `final` end the peer turn and return control to the controller. Do not duplicate this with separate owner or turn-state fields.

For a write-task `final`, `EVIDENCE` must name the local checkpoint commit and concisely map each acceptance condition to its changed paths and verification evidence. Before a planned pause or handoff, commit every coherent task-owned unit even when the broader task continues later. If a safe commit is impossible, use `blocked` and put the exact dirty paths, ownership issue, and recovery action in `EVIDENCE`, `RISKS_OR_LIMITS`, and `NEXT`. Never hide recoverable work behind `none`, and never stage another owner's files merely to satisfy this boundary. Put optional hardening under `RISKS_OR_LIMITS` without implementing it under the completed task.

`TARGET_SETTINGS: preserve` is mandatory. When sending the report to the controller, omit both `model` and `thinking` from the task-message call. These are destination-thread overrides, not sender metadata; attaching the worker model to a controller-bound report changes the controller model. Model overrides are allowed only when the controller creates or continues the task whose policy authorizes that model.

```text
send_message_to_thread({threadId: <controller-task-id>, prompt: <validated-report>})
```

Validate the report, send it through the task-message capability without target-setting overrides, and confirm delivery before the task emits its local final. If delivery fails, emit a local `blocked` report with `DELIVERY: blocked:<reason>` and `TARGET_SETTINGS: preserve`; recover it on the next real controller wake. Do not claim that an immediate snapshot is a future missing-report check.
