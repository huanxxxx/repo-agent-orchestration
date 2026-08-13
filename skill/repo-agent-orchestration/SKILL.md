---
name: repo-agent-orchestration
description: Coordinate repository work across direct, delivery, or architected modes using an independent design authority when needed, a delivery controller, bounded same-task internal subagents, and peer write or review tasks. Use for architecture and design governance, multi-step implementation, proactive parallel dispatch, Git worktree isolation, durable repository continuity packages, independent review, explicit model routing, task handoffs, recovery, integration, or closure.
---

# Repository Agent Orchestration

Keep the product mainline primary and the coordination protocol small.

## Authority

1. Read the repository `AGENTS.md` and only the active continuity-package material needed for the task.
2. Treat user instructions and repository facts as authoritative. Keep model defaults, product boundaries, shared paths, and external gates in the repository.
3. Resolve the lightest orchestration mode from repository policy and task facts. Repository-local task tiers keep their repository-defined meaning.
4. In `delivery`, the delivery controller owns planning, routing, verification, integration, and closure. In `architected`, separate design authority from delivery control; peer writers implement and peer reviewers review without writing.
5. Never turn local evidence into deployment or production authority.

## Choose the orchestration mode

| Mode | Use |
|---|---|
| `direct` | Short answers, bounded current-task work, or ordinary read-only analysis with no independent acceptance boundary |
| `delivery` | A frozen or straightforward outcome that needs independent implementation, review, recovery, or parallel delivery |
| `architected` | New or changed architecture, data contracts, core workflows, product boundaries, multiple implementation packages, material direction choices, or an explicitly requested independent design authority |

Do not infer that every multi-file change needs design authority. Conversely, do not collapse an `architected` task into an ordinary controller because a prompt calls the controller “lead” or “designer.” Read [references/architected.md](references/architected.md) for the three-layer authority, professional design judgment, proactive parallel delivery, and report chain.

## Choose the lightest route

| Work | Route | Worktree |
|---|---|---|
| Short current-turn lookup or comparison | Current task or internal subagent | Inherit the current execution path; create none |
| Bounded current-turn decomposition inside an already authorized task | Internal subagent | Inherit the current execution path; create none |
| Independently acceptable, cross-turn, separately recoverable, or explicitly model-bound implementation | User-visible peer write task | One repository-local worktree for that task |
| Review of a frozen implementation candidate | User-visible peer review task | Reuse the candidate worktree read-only while its writer is paused |
| Short review of a stable committed root | User-visible peer review task | None |
| Long, cross-turn, test-running, or historical review | User-visible peer review task | Controller creates an on-demand detached snapshot |

An App-created user-visible task is a peer task even when a controller dispatches it. The controller is a coordination role, not its runtime parent. Only a same-task internal subagent has a parent/subagent relationship: it inherits the current task's authority and exact execution path, must return in the current turn, and must not own an independent milestone, branch, worktree, formal verdict, or recovery lifecycle. It may write only when the current task already has write authority and gives it non-overlapping owned paths. Classify by the actual creation capability, not by words such as helper, delegated, or child. More agents alone never justify more worktrees.

Read [references/controller.md](references/controller.md) when acting as delivery controller or deciding parallelism. Read [references/contracts.md](references/contracts.md) and use the pure packet constructor before dispatching a task or sending a task report. Read [references/continuity.md](references/continuity.md) only when repository policy defines an execution package, task package, ADR bundle, or equivalent durable recovery entry.

## Keep implementation bounded

A write task implements the smallest change that satisfies its `OBJECTIVE` and `ACCEPTANCE`. Do not add features, reusable abstractions, alternate execution paths, platform-wide refactors, or speculative hardening unless they are required by the accepted outcome. Every changed path must have a concrete acceptance justification. If acceptance appears to require architecture or scope expansion, stop and request reauthorization before crossing the current boundary. Once the required acceptance and tests pass, stop implementation; report extra hardening only as a non-blocking observation.

## Dispatch without ceremony

1. Create an independent peer task only when the outcome can be accepted separately or needs its own cross-turn wait, model binding, branch, recovery boundary, or formal review. Otherwise keep bounded collaboration inside the current task.
2. Once implementation is authorized, compute the dependency-ready set after every decision-relevant event and dispatch all ready, non-conflicting peer tasks within available capacity. Do not wait for the user to repeat a parallelism instruction. Do not split coupled work merely to create more tasks.
3. Give each peer write task one branch, one repository-local worktree, and one exclusive write boundary. Internal subagents inherit that worktree and receive disjoint paths; they never create another branch or worktree. Different peer write tasks never share a writable worktree. Create a worktree only when its owning task is ready.
4. Reject projectless or foreign-project tasks. Host every user-visible peer task in the saved repository project with an explicit App environment of `local`; never request an App-managed worktree. Keep the repository-local worktree only as the task's explicit execution path. Make one creation call per logical dispatch in a controller turn. An empty, ambiguous, timed-out, unparseable, queued-worktree, or `clientThreadId`-only receipt means the outcome is unknown or the route failed; it never authorizes an immediate second creation call. End the turn and reconcile the task list before any later retry.
5. Resolve the destination model policy before task creation. For `app_default`, omit `model` and `thinking` so the task host selects a compatible default. For an explicit repository or user binding, confirm that the destination host advertises the requested model, then submit it through the real creation or continuation parameters only for that task. Prompt text alone is not model binding; never infer compatibility from the controller model name.
6. Put conditional execution authority in the initial task: first perform the fast route gate; if it passes, continue the work in the same turn. If it fails, write nothing and report `blocked`. Do not require a binding-only turn followed by a second authorization turn.
7. Require every repository command to use the exact execution path. Compare the repository-root status with its recorded baseline; do not require an unrelated user-owned root to be clean.
8. Before a cross-turn pause, ownership handoff, formal review, or `final`, create a local checkpoint commit for every coherent task-owned change set after proportional verification. Internal subagents return their paths and evidence to the owning current task; that task verifies and commits the combined checkpoint instead of allowing concurrent commits on one branch. If ownership is mixed or the change cannot be committed safely, leave it untouched and report the exact dirty paths and reason.
9. Require direct task-message delivery for `blocked` and `final` reports. A report targets the contracted authority role, so its task-message call must omit `model` and `thinking`; those parameters mutate the destination task rather than describe the sender. `progress` is optional and is used only when it contains a new decision-relevant fact.
10. Before continuing a peer task, inspect its current top-level runtime status. `idle` or `notLoaded` means no live turn even if a persisted historical row still says `inProgress`; record that stale metadata, but do not page history, block, interrupt, or ask the user to stop it. When the task is `active`, do not send another continuation or correction; use only the product's current active-turn evidence for stop, steer, and multi-in-flight recovery. An urgent HOLD must be followed by confirmation that the current runtime is no longer active.
11. After dispatching or continuing a peer task, perform any product-required startup wait at most once to detect immediate failure or confirm that the peer started. An ordinary active, progress, or timeout result is not authority to wait again: end the controller turn. Resume on a delivered task message, a real one-shot checkpoint, a blocker/input signal, a user status request, or another acceptance event. Do not poll recursively or invent an immediate check that cannot detect later silence.

Run `scripts/validate_dispatch_contract.py` on dispatch, route, and report packets when the packet crosses a task boundary. For dispatch and route packets, the CLI also proves that required paths currently exist and match the live Git worktree registry, branch, and commit; remembered task paths never substitute for this check. The validator is a small boundary check, not a workflow engine.

## Accept, integrate, and recover

Freeze the acceptance baseline, bounded threat model, and non-goals before review. A reviewer evaluates that baseline; it does not create new acceptance criteria or silently widen the threat model. Every blocking finding must cite a frozen acceptance ID and reproducible evidence. Severity describes impact, not scope or authority. A delivery controller may adjudicate implementation details inside the frozen outcome, but in `architected` mode only the design authority may change the design baseline. Route a required boundary change through `DESIGN_REOPEN_REQUEST`; do not treat a local scope-reopen classification as authority.

Treat worker or reviewer PASS/FAIL as evidence. The delivery controller adjudicates implementation findings before routing corrections, then verifies the actual diff or reviewed commit, required checks, evidence limits, and unresolved findings before integration. State the proven scope: focused checks do not prove the full repository, a protected environment, or production behavior. A correction review keeps the same baseline and checks accepted findings plus regressions. If two consecutive reviews introduce new accepted blockers, stop automatic correction and audit scope drift before another writer cycle. In `architected` mode, send final delivery evidence to the design authority for design-consistency acceptance. Keep merge, push, deployment, publication, production data, credentials, and permissions behind their own gates.

After a peer task is accepted and has no correction or in-flight operation, archive it through the App task API and confirm success. Do not confuse the peer's `final` with archival, and do not archive before acceptance.

Read [references/recovery.md](references/recovery.md) only for a silent task, takeover, wrong route, dirty ownership, recovery anchor, or cleanup. A clean task worktree already has its HEAD as a recovery anchor; never manufacture a snapshot commit merely because work begins. Retain a task, package, or worktree only while it has recovery value.
