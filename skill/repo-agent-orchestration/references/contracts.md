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
WRITE_TASK_MODEL: <explicit model/reasoning>
REVIEW_TASK_MODEL: app_default|<explicit model/reasoning>
SHARED_INTEGRATION_PATHS: <paths>
EXTERNAL_GATES: <gates>
```

Repository configuration is read once by the controller. Do not copy invariant wait policy, root-write policy, or integration policy into every child packet.

## Write dispatch

```text
TASK_ID: <id or pending>
WORKTREE_ROOT: <absolute repository-local root>
WORKTREE: <absolute existing worktree>
BRANCH: <task branch>
BASE_COMMIT: <full sha>
OBJECTIVE: <one independently accepted outcome>
OWNED_PATHS: <exclusive write paths>
DO_NOT_TOUCH: <shared or excluded paths>
ACCEPTANCE: <observable conditions>
REQUIRED_TESTS: <commands or checks>
MODEL_POLICY: repo_write_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
```

Create and verify the worktree only when the task is ready. Submit the model through the real task API. The initial task instruction grants execution conditionally: run the fast route gate first, continue in the same turn when it passes, and report `blocked` without writing when it fails.

## Read-only review dispatch

```text
REVIEW_TASK_ID: <id or pending>
TARGET_MODE: root_readonly|existing_worktree|detached_snapshot
TARGET_PATH: <absolute path>
TARGET_COMMIT_OR_RANGE: <full sha or exact range>
READ_ONLY: true
REVIEW_SCOPE: <requirements and risk surface>
ACCEPTANCE: <PASS/FAIL standard>
MODEL_POLICY: app_default|repo_review_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
```

- `root_readonly`: use only for a stable committed root and a short review that neither writes nor needs a frozen filesystem across turns.
- `existing_worktree`: reuse the frozen implementation worktree. The implementation owner pauses until review ends.
- `detached_snapshot`: the controller creates an on-demand detached worktree below `WORKTREE_ROOT` for a long, cross-turn, test-running, or historical review. The reviewer never creates it.

A reviewer never modifies files, the index, commits, or external state. Review tests must be explicitly safe for the selected target; otherwise use a disposable detached snapshot.

## Fast route gate

Run this at the start of the task and continue in the same turn when it passes:

```text
TASK_ID: <actual id>
TASK_MODE: write|review_root|review_worktree
REPOSITORY_ROOT: <absolute root>
WORKTREE_ROOT: <absolute repository-local worktree root>
EXECUTION_PATH: <absolute root or worktree>
TASK_PROJECT_ID: <saved repository project id>
ACTUAL_THREAD_CWD: <actual task cwd>
ACTUAL_THREAD_PROJECT_ID: <actual project id>
```

The actual cwd must equal `REPOSITORY_ROOT`, and both project ids must be non-null and equal. `write` and `review_worktree` execution paths must be strict descendants of `WORKTREE_ROOT`; `review_root` must equal `REPOSITORY_ROOT`.

This gate checks routing shape. Also verify through Git that the selected worktree is registered at the contracted branch/commit and that its status is suitable. Record the repository-root status before the task starts and verify that the task did not change it; unrelated pre-existing root changes do not by themselves block an isolated task.

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
NEXT: <next action>
```

`progress` is optional and means the same task turn continues. `blocked` and `final` end the task turn and return control to the controller. Do not duplicate this with separate owner or turn-state fields.

Validate the report, send it through the task-message capability, and confirm delivery before the task emits its local final. If delivery fails, emit a local `blocked` report with `DELIVERY: blocked:<reason>`; recover it on the next real controller wake. Do not claim that an immediate snapshot is a future missing-report check.
