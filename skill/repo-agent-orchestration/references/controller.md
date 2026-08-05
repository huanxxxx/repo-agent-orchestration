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
- Process milestone reports and actually deliver decisions through the task-message capability; do not make the user relay routine coordination.
- Verify evidence, integrate in order, and rerun acceptance.
- Update repository-owned shared status at integration points.
- Mark `PASS_VERIFIED` only after all acceptance, evidence, blocker, reply, correction, and in-flight-operation checks clear; then archive the task immediately.
- Receive internal-helper results, confirm the helper stopped, and release its slot promptly.
- Retain recoverable worktrees until their separate cleanup gate clears.

Do not delegate final authorization, integration acceptance, or product-state claims.
