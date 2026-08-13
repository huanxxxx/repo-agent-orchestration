# Repository orchestration profile example

Add an equivalent section to the target repository's root `AGENTS.md`. Replace every placeholder with repository facts.

## Agent Orchestration Profile

- Use the repository-local `$repo-agent-orchestration` skill when work needs independent peer-task ownership, formal review, parallel peer dispatch, cross-turn handoffs or recovery, integration, or closure; keep bounded same-task collaboration inside the current task.
- If the skill or a required visible peer-task, existing-path, or model-binding capability is unavailable, stop and report. Do not collapse work that needs a peer task into controller or internal-subagent implementation.

```text
MAIN_BRANCH: main
ROOT_WORKTREE_POLICY: observe_integrate_validate
WORKTREE_ROOT: <absolute-repository-path>/.worktrees
BRANCH_PREFIX: codex/
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
WRITE_TASK_MODEL: app_default|<execution-model>/<reasoning>
REVIEW_TASK_MODEL: app_default
SHARED_INTEGRATION_PATHS: <repository-specific shared paths>
CONTINUITY_POLICY: none|repository_defined:<index or entry>
EXTERNAL_GATES: merge main; push; deploy; publish; production data; credentials; permissions
```

`WRITE_TASK_MODEL: app_default` and `REVIEW_TASK_MODEL: app_default` mean deliberately omitting `model` and `thinking` so the destination host selects its compatible default. An explicit model must be submitted through actual task creation or continuation parameters only after the destination host advertises it; it does not become available merely because the controller belongs to a particular model family.
