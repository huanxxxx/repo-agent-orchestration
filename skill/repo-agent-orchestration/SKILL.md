---
name: repo-agent-orchestration
description: Coordinate repository work between a controller, bounded internal subagents, and independently owned write or review tasks. Use for multi-step implementation, parallel dispatch, Git worktree isolation, durable repository continuity packages, independent review, explicit model routing, task handoffs, recovery, integration, or closure.
---

# Repository Agent Orchestration

Keep the product mainline primary and the coordination protocol small.

## Authority

1. Read the repository `AGENTS.md` and only the active continuity-package material needed for the task.
2. Treat user instructions and repository facts as authoritative. Keep model defaults, product boundaries, shared paths, and external gates in the repository.
3. The controller plans, routes, verifies, integrates, and closes. Write tasks implement. Review tasks review without writing.
4. Never turn local evidence into deployment or production authority.

## Choose the lightest route

| Work | Route | Worktree |
|---|---|---|
| Short current-turn lookup or comparison | Controller or internal subagent | Inherit the current execution path; create none |
| Bounded current-turn decomposition inside an already authorized task | Internal subagent | Inherit the current execution path; create none |
| Independently acceptable, cross-turn, separately recoverable, or explicitly model-bound implementation | User-visible write task | One repository-local worktree for that task |
| Review of a frozen implementation candidate | User-visible review task | Reuse the candidate worktree read-only while its writer is paused |
| Short review of a stable committed root | User-visible review task | None |
| Long, cross-turn, test-running, or historical review | User-visible review task | Controller creates an on-demand detached snapshot |

Use an internal subagent only as a bounded participant in the current task. It inherits that task's authority and exact execution path, must return in the current turn, and must not own an independent milestone, branch, worktree, formal verdict, or recovery lifecycle. It may write only when the current task already has write authority and gives it non-overlapping owned paths. More agents alone never justify more worktrees.

Read [references/controller.md](references/controller.md) when acting as controller or deciding parallelism. Read [references/contracts.md](references/contracts.md) before dispatching a task or sending a task report. Read [references/continuity.md](references/continuity.md) only when repository policy defines an execution package, task package, ADR bundle, or equivalent durable recovery entry.

## Dispatch without ceremony

1. Create an independent task only when the outcome can be accepted separately or needs its own cross-turn wait, model binding, branch, recovery boundary, or formal review. Otherwise keep bounded collaboration inside the current task.
2. Give each independent write task one branch, one repository-local worktree, and one exclusive write boundary. Internal subagents inherit that worktree and receive disjoint paths; they never create another branch or worktree. Different independent write tasks never share a writable worktree. Create a worktree only when its owning task is ready.
3. Reject projectless or foreign-project tasks. Host every user-visible task in the saved repository project with an explicit App environment of `local`; never request an App-managed worktree. Keep the repository-local worktree only as the task's explicit execution path.
4. Bind write-task models through real task creation or continuation parameters only when the destination is that write task. Prompt text alone is not model binding. For declared `app_default` review policy, omit the override deliberately.
5. Put conditional execution authority in the initial task: first perform the fast route gate; if it passes, continue the work in the same turn. If it fails, write nothing and report `blocked`. Do not require a binding-only turn followed by a second authorization turn.
6. Require every repository command to use the exact execution path. Compare the repository-root status with its recorded baseline; do not require an unrelated user-owned root to be clean.
7. Require direct task-message delivery for `blocked` and `final` reports. A report targets the controller, so its task-message call must omit `model` and `thinking`; those parameters mutate the destination task rather than describe the sender. `progress` is optional and is used only when it contains a new decision-relevant fact.
8. After dispatch or continuation, end the controller turn. Resume on a delivered task message, a real one-shot checkpoint, a blocker/input signal, a user status request, or another acceptance event. Do not poll recursively or invent an immediate check that cannot detect later silence.

Run `scripts/validate_dispatch_contract.py` on dispatch, route, and report packets when the packet crosses a task boundary. For dispatch and route packets, the CLI also proves that required paths currently exist and match the live Git worktree registry, branch, and commit; remembered task paths never substitute for this check. The validator is a small boundary check, not a workflow engine.

## Accept, integrate, and recover

Freeze the acceptance baseline, bounded threat model, and non-goals before review. A reviewer evaluates that baseline; it does not create new acceptance criteria or silently widen the threat model. Every blocking finding must cite a frozen acceptance ID and reproducible evidence. Severity describes impact, not scope or authority. Treat unmapped hardening as non-blocking unless the controller explicitly reopens the baseline within its authority.

Treat worker or reviewer PASS/FAIL as evidence. The controller adjudicates findings before routing corrections, then verifies the actual diff or reviewed commit, required checks, evidence limits, and unresolved findings before integration. A correction review keeps the same baseline and checks accepted findings plus regressions. If two consecutive reviews introduce new accepted blockers, stop automatic correction and audit scope drift before another writer cycle. Keep merge, push, deployment, publication, production data, credentials, and permissions behind their own gates.

After a task is accepted and has no correction or in-flight operation, archive its user-visible task through the App task API and confirm success. Do not confuse a child `final` with archival, and do not archive before acceptance.

Read [references/recovery.md](references/recovery.md) only for a silent task, takeover, wrong route, dirty ownership, recovery anchor, or cleanup. A clean task worktree already has its HEAD as a recovery anchor; never manufacture a snapshot commit merely because work begins. Retain a task, package, or worktree only while it has recovery value.
