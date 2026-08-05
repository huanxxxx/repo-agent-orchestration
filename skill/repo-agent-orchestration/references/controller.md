# Controller workflow

## Mainline anchor

Maintain these facts throughout the task:

```text
MAINLINE_OBJECTIVE: <user-visible product outcome>
CURRENT_GATE: <single gate blocking the next outcome>
ACTIVE_TASKS: <task ids and owned outcomes>
READY_CANDIDATES: <authorized and dependency-closed candidates>
NEXT_AFTER_GATE: <next product step>
AUTHORIZATION_CEILING: <explicitly excluded actions>
```

Do not turn routing, reporting, or model policy into a competing product mainline.

## Readiness audit

Run the audit at task start, plan freeze, blocker clearance, task dispatch, and stage integration. Re-run it when a task enters a wait state; one active or waiting task never suspends scanning of other candidates.

Record one row per candidate:

```text
TASK_CANDIDATE: <name>
AUTHORIZED: yes|no:<reason>
DEPENDENCIES: closed|blocked_by:<task-or-gate>
INPUTS: complete|missing:<fact>
OWNED_PATHS: <isolated paths or read-only target>
ACCEPTANCE: <independent acceptance result>
SHARED_WRITE: none|<exact surface>
EXTERNAL_GATE: none|<exact gate>
DECISION: ready|serial_with:<task>|blocked
```

Dispatch multiple ready candidates in one wave when capacity permits. Never use “another task is active” as a serialization reason.

Keep implementation and review of the same moving candidate serial. Permit parallel reviews only for different frozen candidates.

Create a worktree only when its task is authorized, dependency-closed, and ready to begin. Do not pre-create future worktrees or create a temporary integration branch merely because a task is large. Record a temporary integration topology only when multiple independent write lines actually require it.

## Worktree ownership and review corrections

- Give each writable worktree one task boundary, one branch, and one user-visible write owner.
- Never let different tasks share a writable worktree.
- Freeze the exact implementation worktree, branch, and commit or range before formal review; the implementation owner pauses while the candidate is frozen.
- Return review findings to the original implementation owner in the same worktree by default. Let a reviewer write only with explicit repair authority and a separate writable boundary.
- Stop and report when the owned scope, shared contract, dirty state, or writer identity becomes ambiguous.

## Fixed role routing

| Work | Route |
|---|---|
| Repository search or evidence extraction, current turn, read-only | Internal helper |
| Code, document, or test write | User-visible write task |
| Commit or independently accepted deliverable | User-visible write task |
| Formal PASS/FAIL review | User-visible read-only review task |
| Long-running or cross-turn work | User-visible task |
| Shared-state update and integration correction | Controller in an integration worktree |

Repository policy or an explicit user instruction may narrow these routes. Do not broaden them by preference.

## Controller responsibilities

- Preserve the mainline and authorization ceiling.
- Create worktrees, dispatch tasks, and save task ids.
- Preflight the task API and saved-project registry. For repository-local worktrees, require the selected project to resolve to the repository root, create the task in that project's local environment, and keep the exact execution worktree as a separate coordinate.
- Use a read-only bootstrap prompt for every new task. Verify the repository host and execution worktree receipt before sending execution authorization; archive or stop a mismatched task without letting it write.
- Process milestone reports and actually deliver decisions through the task-message capability; do not make the user relay routine coordination.
- Treat only a report received through the task-message capability as delivered. A worker's local final, title, status, or `owner=task` text is not a receipt. Record the expected milestone and non-`none` checkpoint for every dispatched stage.
- Before continuing a task, distinguish `inProgress` from a completed turn. Never send a redundant continuation to an in-progress task or assume a completed turn can restart itself.
- Verify evidence, integrate in order, and rerun acceptance.
- Update repository-owned shared status at integration points.
- Mark `PASS_VERIFIED` only after all acceptance, evidence, blocker, reply, correction, and in-flight-operation checks clear; then archive the task immediately.
- Receive internal-helper results, confirm the helper stopped, and release its slot promptly.
- Retain recoverable worktrees until their separate cleanup gate clears.

Do not delegate final authorization, integration acceptance, or product-state claims.

## Report delivery and turn ownership gate

For every worker or reviewer report:

1. Require the canonical milestone schema, `REPORT_DELIVERY: task_message:<controller-thread-id>`, and `TURN_STATE`.
2. Accept the report only when it arrives through the task-message capability. Do not scrape a child final as the ordinary success path.
3. Interpret `owner=task` only with `TURN_STATE=continuing` while that same turn is still in progress. A task final always ends the turn and therefore returns `owner=controller`.
4. When the next stage still belongs to the same task, validate the report, decide, then send one explicit continuation. Ownership transfers only after that call succeeds.
5. If the expected report is absent at its checkpoint, inspect status once. If the turn is in progress, do not interrupt it. If the turn completed, read its latest final once to preserve evidence, then send a continuation only when the reported state actually requires one.

## Repository host and execution-worktree gate

The task host directory and the Git execution worktree are separate authority boundaries.

- Reject `projectless` for repository execution or review, even when the prompt contains an absolute repository path.
- When repository policy requires an already-created repository-local worktree, select the current repository's saved project and environment `local`. Require the actual task cwd and project path to equal the repository root.
- Keep `EXECUTION_WORKTREE` separate. Require it to be a registered Git worktree below the declared repo-local `WORKTREE_ROOT`, with the contracted branch, head, base, and ownership.
- Require every shell command to set its working directory to `EXECUTION_WORKTREE`; require every file operation to use an absolute path below it. Never run a repository mutation from the host root and never use a relative path that could resolve there.
- Verify root status is clean before authorization and again at every milestone and final handoff. Any root drift or operation outside `EXECUTION_WORKTREE` is an immediate blocker.
- Use an App-managed `worktree` only when repository policy explicitly permits App-managed placement. It is not a substitute for a repo-local tree.
- Permit direct existing-cwd binding when a task API supports it, but do not require each linked worktree to be registered as a separate saved project.
- Treat pending creation as one in-flight task. Wait for that result; never issue duplicate creation calls as a retry.
