# Dispatch and report contracts

Read repository policy before filling these templates. Use absolute paths and exact Git coordinates.

## Repository profile

Keep repository-specific choices outside the reusable skill:

```text
MAIN_BRANCH: <branch>
ROOT_WORKTREE_POLICY: <root worktree role>
WORKTREE_ROOT: <repo-local directory>
BRANCH_PREFIX: <repository branch prefix>
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
WRITE_TASK_MODEL: <explicit execution model and reasoning>
REVIEW_TASK_MODEL: app_default
SHARED_INTEGRATION_PATHS: <repository-specific paths>
EXTERNAL_GATES: <deployment/data/credential/publication boundaries>
```

The controller retains the model and reasoning selected for its current App task. A write task must use `WRITE_TASK_MODEL` through actual task-creation or continuation parameters. Reviews default to `REVIEW_TASK_MODEL: app_default` without per-task user selection; a repository or explicit user instruction may override that policy. With `app_default`, omit a model override for the review task so the App default applies. It does not guarantee inheritance of a controller model that was manually changed away from the App default.

## Write task

```text
TASK_ID: <id or client id>
WORKTREE_POLICY: repo_local_only
WORKTREE_ROOT: <absolute repository-local worktree root>
WORKTREE: <absolute existing worktree>
BRANCH: <task branch>
BASE_COMMIT: <full exact sha>
OBJECTIVE: <one independently accepted outcome>
OWNED_PATHS: <exclusive write paths>
DO_NOT_TOUCH: <shared and excluded paths>
ACCEPTANCE: <observable acceptance conditions>
REQUIRED_TESTS: <commands or checks>
INTEGRATION_TARGET: <branch or integration task>
MODEL_POLICY: repo_write_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
EXPECTED_NEXT_MILESTONE: <milestone>
CONTROLLER_AFTER_DISPATCH: event_driven_yield
NO_REPORT_CHECK_AFTER: <ISO-8601|current_turn_once>
```

Create and verify the worktree before creating the user-visible task. Never use `app_default` for a write task. A successful task API call proves submitted binding, not the effective runtime model unless the product echoes it.

Every dispatched stage must declare `CONTROLLER_AFTER_DISPATCH: event_driven_yield` and a non-`none` missing-report checkpoint. `current_turn_once` permits at most one immediate nonblocking status snapshot after successful creation or continuation; whether used or skipped, the controller then ends its turn and waits for task-message delivery. Use a real ISO-8601 one-shot wakeup only when the product supports it. If neither can be enforced, report the capability gap instead of silently using `none` or keeping the controller online.

Before dispatch, resolve and verify the repository and worktree root; main head and dirty state; full base SHA; unoccupied branch and target; absence of path substitution; and the final path, branch, head, and base shown by the Git worktree registry. Create only immediately ready worktrees. A task session does not create or own an implicit platform-managed tree.

Preflight the actual task-creation interface and project registry. Distinguish the task host from its Git execution worktree. An absolute path in the prompt alone does not satisfy execution binding.

When the interface offers project `local`, project `worktree`, or `projectless`:

1. Require the current repository's saved project id and resolved repository-root path.
2. For `TASK_HOST_POLICY: repository_project_local`, create against that repository project with environment `local` and an initial read-only route-check prompt.
3. Reject `projectless`, because it runs under a user-global directory.
4. Do not use project environment `worktree` when repository policy requires an existing repo-local tree; that route creates a different App-managed tree.
5. Treat the repository-root cwd as the task host only. Bind all repository commands and file operations to the separate existing `WORKTREE` using exact command working directories and absolute file paths.
6. If the repository project cannot be bound locally, stop with `CAPABILITY_BLOCKED_REPOSITORY_PROJECT_HOST`.
7. Treat a pending creation result as the single in-flight task; do not retry and create duplicates.

After creation and before any write authorization, validate this binding receipt:

```text
TASK_ID: <actual task id>
REPOSITORY_ROOT: <absolute repository root>
WORKTREE_ROOT: <absolute repository-local worktree root>
EXECUTION_WORKTREE: <same absolute existing task worktree>
TASK_PROJECT_ID: <non-null saved project id>
TASK_PROJECT_PATH: <resolved repository-root saved project path>
TASK_ENVIRONMENT: local
ACTUAL_THREAD_CWD: <repository-root cwd returned or read from the task>
ACTUAL_THREAD_PROJECT_ID: <project id returned or read from the task>
COMMAND_WORKDIR_POLICY: exact_execution_worktree
ROOT_WRITE_POLICY: forbidden
BINDING_STATUS: verified
```

`TASK_PROJECT_PATH` and `ACTUAL_THREAD_CWD` must resolve to `REPOSITORY_ROOT`; both project ids must be non-null and equal. `EXECUTION_WORKTREE` must resolve below `WORKTREE_ROOT`, and `WORKTREE_ROOT` must resolve below `REPOSITORY_ROOT`. Run the validator with `--kind binding`. Until it passes, the task may only report coordinates and must not edit, test with persistent outputs, stage, commit, or start a milestone.

The validator normalizes Windows, extended Windows, and POSIX dot segments lexically before comparing paths, so nonexistent planned paths can be checked and `..` escapes are rejected. This is a contract-shape gate, not filesystem evidence: separately verify through Git that the execution worktree exists, is registered, and has the contracted branch, head, base, and owner.

After the receipt passes, every shell call must set `workdir=EXECUTION_WORKTREE` or use an equivalent exact cwd parameter. Every file read or write must use an absolute path below `EXECUTION_WORKTREE`. At baseline, every milestone, and final handoff, verify both `git -C REPOSITORY_ROOT status --short` remains clean and the execution worktree still has the contracted branch/head/owner. A host-root mutation or missing exact workdir is a blocker, even when the intended relative path also exists in the execution worktree.

The write owner must modify and stage only `OWNED_PATHS`; never use broad staging such as `git add .` or `git add -A`. Run `REQUIRED_TESTS`, relevant type or static checks, and a whitespace/diff check. Report focused evidence at its actual scope. Do not merge, push, deploy, publish, or change external data unless separately authorized.

## Read-only review task

```text
REVIEW_TASK_ID: <id or client id>
TARGET_WORKTREE: <absolute frozen implementation worktree>
TARGET_BRANCH: <exact branch>
TARGET_COMMIT_OR_RANGE: <exact sha or range>
READ_ONLY: true
REVIEW_SCOPE: <requirements and risk surface>
ACCEPTANCE: <PASS/FAIL standard>
REQUIRED_CHECKS: <read-only checks>
REPORT_FORMAT: <findings and evidence format>
MODEL_POLICY: app_default|repo_review_default:<model>/<reasoning>|user_explicit:<model>/<reasoning>
EXPECTED_NEXT_MILESTONE: <milestone>
CONTROLLER_AFTER_DISPATCH: event_driven_yield
NO_REPORT_CHECK_AFTER: <ISO-8601|current_turn_once>
```

Do not create a new worktree or branch for review, and do not modify files, the index, or commits. Freeze the implementation owner until review ends. Return findings to that owner in the same implementation worktree by default; a reviewer may write only with explicit repair authority and a separate writable boundary. When `MODEL_POLICY: app_default`, deliberately omit the model override; the user does not need to select a model for each review. If the product does not echo the runtime model, report `EFFECTIVE_MODEL=unverified` rather than claiming inheritance.

Formal review uses the same repository-host and execution-worktree receipt. Bind the task to the repository project locally, then perform every read with an exact cwd or absolute path to the frozen implementation worktree. A projectless review or a review created in a new App-managed tree is not a review of the frozen candidate.

## Milestone report

```text
TASK_UPDATE
TASK_ID: <id>
MILESTONE: baseline_confirmed|plan_frozen|blocked|fix_ready|tests_complete|final
SUMMARY: <new fact only>
EVIDENCE: <paths, sha, commands, results, or none>
RISKS_OR_LIMITS: <current limits or none; required for final>
PENDING_ITEMS: <remaining items or none; required for final>
REPORT_DELIVERY: task_message:<controller-thread-id>
TURN_STATE: continuing|ending
BLOCKER_OR_NEXT: owner=<controller|task>; action=<decision or next milestone>; check_after=<ISO-8601|current_turn_once|none>
```

Report every applicable milestone: baseline confirmation, plan or contract freeze, a blocker requiring controller or user action, correction completion, test completion, and final delivery. Report a blocker immediately. A `tests_complete` report must include actual commands and results. A `final` report must identify the artifact or commit, acceptance result, risks or limits, and pending items. Do not manufacture empty milestones or repeat unchanged facts.

Validate every report with `--kind update`, then send the validated text to the controller through the task-message capability. Confirm that call succeeds before emitting the task's local final. A report written only in the child task's commentary or final is not delivered to the controller. Do not invent milestone names such as `READY_FOR_REVIEW`; use `MILESTONE=final` and put readiness in `SUMMARY` or `action`.

`TURN_STATE=continuing` means the same task turn will keep running after sending the report; it requires `owner=task` and a non-`none` `check_after`. `TURN_STATE=ending` means the current task turn stops after the report; it requires `owner=controller`, including when the same task is expected to resume later. A local final always ends the turn. The controller transfers ownership back only after its continuation message actually succeeds.

If task-message delivery fails or is unavailable, do not claim the intended milestone was delivered. Emit only a local recovery report with `MILESTONE=blocked`, `REPORT_DELIVERY=blocked:<reason>`, `TURN_STATE=ending`, and `owner=controller`; then rely on the controller's due single checkpoint to recover it. The user must not be used as the routine relay.

`check_after` is a single missing-report checkpoint for the current owner and stage. `current_turn_once` permits at most one immediate nonblocking snapshot before the controller ends its turn and creates no automation. It never authorizes a bounded wait loop, recursive `wait_threads`, or unchanged progress commentary. `none` is valid only after ownership has returned to the controller and no worker report is outstanding. An ISO-8601 value may create a wakeup only when the product supports a true one-shot trigger.

Any new valid milestone or actually delivered stage instruction invalidates the previous checkpoint. Never emulate one-shot behavior with a recurring schedule. When a due check yields no new fact, end the controller turn rather than polling recursively. Child commentary or a timeout snapshot is not a new event and must not be narrated as controller progress.
