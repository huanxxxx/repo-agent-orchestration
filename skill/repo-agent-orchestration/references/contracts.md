# Dispatch and report contracts

Read repository policy before filling these templates. Use absolute paths and exact Git coordinates.

## Repository profile

Keep repository-specific choices outside the reusable skill:

```text
MAIN_BRANCH: <branch>
ROOT_WORKTREE_POLICY: <root worktree role>
WORKTREE_ROOT: <repo-local directory>
BRANCH_PREFIX: <repository branch prefix>
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
NO_REPORT_CHECK_AFTER: <ISO-8601|current_turn|none>
```

Create and verify the worktree before creating the user-visible task. Never use `app_default` for a write task. A successful task API call proves submitted binding, not the effective runtime model unless the product echoes it.

Before dispatch, resolve and verify the repository and worktree root; main head and dirty state; full base SHA; unoccupied branch and target; absence of path substitution; and the final path, branch, head, and base shown by the Git worktree registry. Create only immediately ready worktrees. A task session does not create or own an implicit platform-managed tree.

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
NO_REPORT_CHECK_AFTER: <ISO-8601|current_turn|none>
```

Do not create a new worktree or branch for review, and do not modify files, the index, or commits. Freeze the implementation owner until review ends. Return findings to that owner in the same implementation worktree by default; a reviewer may write only with explicit repair authority and a separate writable boundary. When `MODEL_POLICY: app_default`, deliberately omit the model override; the user does not need to select a model for each review. If the product does not echo the runtime model, report `EFFECTIVE_MODEL=unverified` rather than claiming inheritance.

## Milestone report

```text
TASK_UPDATE
TASK_ID: <id>
MILESTONE: baseline_confirmed|plan_frozen|blocked|fix_ready|tests_complete|final
SUMMARY: <new fact only>
EVIDENCE: <paths, sha, commands, results, or none>
RISKS_OR_LIMITS: <current limits or none; required for final>
PENDING_ITEMS: <remaining items or none; required for final>
BLOCKER_OR_NEXT: owner=<controller|task>; action=<decision or next milestone>; check_after=<ISO-8601|current_turn|none>
```

Report every applicable milestone: baseline confirmation, plan or contract freeze, a blocker requiring controller or user action, correction completion, test completion, and final delivery. Report a blocker immediately. A `tests_complete` report must include actual commands and results. A `final` report must identify the artifact or commit, acceptance result, risks or limits, and pending items. Do not manufacture empty milestones or repeat unchanged facts.

`owner=controller` means the task stops for a decision. The controller transfers ownership back only after the follow-up message is actually sent. `owner=task` means the task is genuinely running; `action` names the next applicable milestone. The controller and task communicate directly through the task-message capability rather than asking the user to relay routine updates.

`check_after` is a single missing-report checkpoint for the current owner and stage. `current_turn` permits one purposeful check before the controller turn ends and creates no automation. `none` means no missing-report check. An ISO-8601 value may create a wakeup only when the product supports a true one-shot trigger.

Any new valid milestone or actually delivered stage instruction invalidates the previous checkpoint. Never emulate one-shot behavior with a recurring schedule. When a due check yields no new fact, stop rather than polling recursively.
