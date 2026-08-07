---
name: repo-agent-orchestration
description: Coordinate repository work between a controller, user-visible write or review tasks, and short read-only helpers. Use for multi-step implementation, parallel dispatch, Git worktree isolation, independent review, explicit model routing, task handoffs, recovery, integration, or closure.
---

# Repository Agent Orchestration

Keep the product mainline primary and the coordination protocol small.

## Authority

1. Read the repository `AGENTS.md` and only the active execution-package material needed for the task.
2. Treat user instructions and repository facts as authoritative. Keep model defaults, product boundaries, shared paths, and external gates in the repository.
3. The controller plans, routes, verifies, integrates, and closes. Write tasks implement. Review tasks review without writing.
4. Never turn local evidence into deployment or production authority.

## Choose the lightest route

| Work | Route | Worktree |
|---|---|---|
| Short current-turn read-only lookup | Controller or internal helper | None |
| File or test change, commit, or long implementation | User-visible write task | Create on demand |
| Review of a frozen implementation candidate | User-visible review task | Reuse the candidate worktree |
| Short review of a stable committed root | User-visible review task | None |
| Long, cross-turn, test-running, or historical review | User-visible review task | Controller creates an on-demand detached snapshot |

Use an internal helper only for bounded current-turn retrieval or comparison. It must not write, own a milestone, issue formal PASS/FAIL, or wait across turns.

Read [references/controller.md](references/controller.md) when acting as controller or deciding parallelism. Read [references/contracts.md](references/contracts.md) before dispatching a task or sending a task report.

## Dispatch without ceremony

1. Dispatch work when it is authorized, dependency-closed, independently acceptable, and has no overlapping writer. Record only the reason when one of these conditions blocks or serializes it.
2. Give each writer one task boundary, branch, repository-local worktree, and exclusive write scope. Create the worktree only when the task is ready.
3. Reject projectless or foreign-project tasks. Host a task in the saved repository project and keep its execution path explicit.
4. Bind write-task models through real task creation or continuation parameters only when the destination is that write task. Prompt text alone is not model binding. For declared `app_default` review policy, omit the override deliberately.
5. Put conditional execution authority in the initial task: first perform the fast route gate; if it passes, continue the work in the same turn. If it fails, write nothing and report `blocked`. Do not require a binding-only turn followed by a second authorization turn.
6. Require every repository command to use the exact execution path. Compare the repository-root status with its recorded baseline; do not require an unrelated user-owned root to be clean.
7. Require direct task-message delivery for `blocked` and `final` reports. A report targets the controller, so its task-message call must omit `model` and `thinking`; those parameters mutate the destination task rather than describe the sender. `progress` is optional and is used only when it contains a new decision-relevant fact.
8. After dispatch or continuation, end the controller turn. Resume on a delivered task message, a real one-shot checkpoint, a blocker/input signal, a user status request, or another acceptance event. Do not poll recursively or invent an immediate check that cannot detect later silence.

Run `scripts/validate_dispatch_contract.py` on dispatch, route, and report packets when the packet crosses a task boundary. For dispatch and route packets, the CLI also proves that required paths currently exist and match the live Git worktree registry, branch, and commit; remembered task paths never substitute for this check. The validator is a small boundary check, not a workflow engine.

## Accept, integrate, and recover

Treat worker or reviewer PASS as evidence. Verify the actual diff or reviewed commit, required checks, evidence limits, and unresolved findings before integration. Keep merge, push, deployment, publication, production data, credentials, and permissions behind their own gates.

Read [references/recovery.md](references/recovery.md) only for a silent task, takeover, wrong route, dirty ownership, or cleanup. Retain a task or worktree only while it has recovery value.
