---
name: repo-agent-orchestration
description: Split long repository work into direct work, internal help, or independent peer tasks with minimal context, reports, and repo-local safety.
---

# Repository Agent Orchestration

Keep product primary. Use this Skill to split context; avoid bureaucracy.

Default path: choose boundary -> send minimum capsule -> peer works in its own context -> peer reports once to `REPORT_TO` -> owner accepts, archives, and classifies cleanup or sends one correction.

Hard boundaries: repo-local paths, write ownership, read-only review, preserved settings, and separate gates for merge, push, deploy, production data, credentials, and permissions.

## Start once; wake lightly

At task start, read repository `AGENTS.md`, resolve mode/role/config, and run the fast route gate once per task/runtime binding. Record route, acceptance, and report destination; PASS continues in the same turn.

On later wakes, reuse proven facts. Reload only when route identity, Skill version, or authority changed or became ambiguous. Commits do not invalidate the route; new packets live-check branch/HEAD. Consume one event, read changed hot state, act, and yield.

Read only the needed reference: [architected.md](references/architected.md), [controller.md](references/controller.md), [contracts.md](references/contracts.md), [continuity.md](references/continuity.md), or [recovery.md](references/recovery.md).

For routine dispatch, use the CLI; do not inspect protocol source, enumerate schemas, load executor-only Skills, or walk implementation. Inspect deeper only for planning, acceptance, recovery, or defects.

## Rotate context at a checkpoint

A cumulative token total is only a pressure signal. At a recoverable commit, if a different slice remains or facts are going stale, follow [continuity.md](references/continuity.md) for fresh-context rotation; never rotate mid-operation.

Rotation replaces the owner. A confirmed, explicitly authorized successor ends the predecessor without waiting; failed optional delivery emits `HANDOFF_READY` once and retains the owner - no `PROTOCOL_BLOCKED`, retry, poll, or internal substitute.

## Choose authority

Use `direct` for short current-task work, `delivery` for a frozen outcome needing independent implementation/review/recovery/parallel work, and `architected` for architecture, data contracts, core workflows, product boundaries, multiple packages, material direction choices, or an explicitly requested design authority.

Think in task types: `direct`, `peer_write`, `peer_review`, `peer_design`, and `peer_audit`. In `delivery`, the controller owns the outcome. In `architected`, design owns direction/final consistency, delivery owns implementation, and only design may change the baseline through `DESIGN_REOPEN_REQUEST` and `DESIGN_DECISION`.

## Choose the lightest route

Keep bounded current-turn slices here or in an internal subagent; inherit the path, create no worktree, and return this turn. Use a peer for separate context, independent acceptance, cross-turn waiting, model binding, recovery, design, audit, or formal review. Stable-root review needs no tree; a frozen candidate reuses its paused writer tree read-only; only long/test-running/historical review gets a detached snapshot.

An App-created user-visible task is a peer. `create_thread` carries its complete first prompt; later messages use `send_message_to_thread`. `spawn_agent`, `send_input`, agent send/follow-up, and `wait_agent` are internal-only: they inherit path/authority, return this turn, and get no peer packet/tree/branch. Their id is never a peer `TASK_ID`; use a peer when synchronous return is unsuitable. More agents alone never justify more worktrees; different peer writers never share one.

## Dispatch and execute

1. Dispatch all ready, non-conflicting peers within current task-creation authority and capacity; do not await another parallelism instruction or split coupled work to fill slots. This Skill grants no missing authority.
2. Send a small task capsule: `OBJECTIVE`, `CONTEXT`, `BOUNDARY`, `ACCEPTANCE`, `REPORT_TO`. The packet schema adds route, model, archive, and Git facts; those mechanics must not become the task itself.
3. Require the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`. Every changed path must have a concrete acceptance justification. Once the required acceptance and tests pass, stop implementation.
4. Give a ready writer one local branch/tree and exclusive paths. Internal subagents inherit it; that task verifies and commits the combined checkpoint. Reject projectless/foreign-project tasks. Create peers in the saved project with `environment: {type: "local"}` and the repository-local execution path, never an App-managed tree.
5. Build the full launch prompt, then call `create_thread` once with a meaningful title, saved project, explicit `environment: {type: "local"}`, and that prompt. A returned `threadId` proves creation and initial delivery; never create `AWAIT_FORMAL_DISPATCH` or resend the launch. A host-required first check calls `wait_threads` once, then yields. Ambiguous, queued-worktree, or `clientThreadId`-only creation is phantom; reconcile next wake. Failed routing for a required peer boundary is `PROTOCOL_BLOCKED`, never `spawn_agent`; optional rotation uses `HANDOFF_READY`.
6. For `app_default`, omit `model` and `thinking`; explicit bindings use actual task parameters only after host discovery. Reports must omit `model` and `thinking` and preserve destination settings.
7. Use the exact execution path; the CLI proves paths match Git registry, branch, and commit. Root status is compared with its baseline, not forced clean.
8. Before a cross-turn pause, ownership handoff, formal review, or `final`, verify and locally commit coherent owned output. Never stage another owner's files; if unsafe, report exact dirty paths and recovery action.

## Cross a required peer boundary once

From the repository root, build a peer's complete initial prompt with the installed Skill:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <write|review|design_handoff> --live --launch -
```

Use its output unchanged as `create_thread.prompt`. For later reports, decisions, or corrections, let the constructor inject transport fields:

```text
python .agents/skills/repo-agent-orchestration/scripts/construct_packet.py --kind <kind> --live --task-message-to <target-task-id> -
```

Pass emitted arguments unchanged; App frames them. A launch omits its unknown self id; the returned `threadId` is authoritative. The constructor supplies other mechanics, never objective, evidence, findings, or acceptance. Do not create temporary packet files or validate twice. Validate incoming once:

```text
python .agents/skills/repo-agent-orchestration/scripts/validate_dispatch_contract.py --kind <kind> -
```

The validator is a boundary check, not a workflow engine. Before send, correct one shape error once without changing semantics or route. A repeat error, incoming validation failure, or attempted/ambiguous delivery is `PROTOCOL_BLOCKED`.

## Process one event and yield

Treat each App wake as one bounded event batch. Process only its event and already-delivered facts needed for the same decision. Before continuing a peer, check current top-level status once: `idle` or `notLoaded` means no live turn despite stale `inProgress` history; `active` forbids another continuation or correction.

Successful creation or later delivery ends the sender turn after at most the host-required first check. A formal report to `REPORT_TO` is required delivery, not cross-peer meddling. Do not inspect its target or another peer afterward. `wait_threads` may run once for that first check, never `wait_agent`; any result ends the turn. Resume on an event or user request; never poll.

## Accept and close

Freeze acceptance, threat model, and non-goals. Review the exact delta by default; full context/suite needs a reason. Corrections reuse the eligible reviewer: `fresh` means a new range/judgment, not a new task. Findings cite frozen criteria. Controller verifies diff, commit, checks, and evidence limits; focused checks do not prove the full repository, protected systems, or production behavior.

In `architected`, final evidence returns to design authority. Merge, push, deploy, publish, production data, credentials, and permissions keep separate gates.

After PASS, do not reopen review merely because rolling handoff moves HEAD. Keep the reviewed checkpoint distinct from the later continuity checkpoint. A `continuity_only` closeout changes no implementation, normative design/contracts, acceptance, non-goals, findings, or verdict evidence; root-write authority verifies/commits it without review.

After accepted work is idle, archive and confirm it, then run `CLOSEOUT_CLEANUP`. Remove a worktree/branch only after proving identity, clean state, integration or explicit abandonment, and no recovery value; remove the registered tree before the local branch. Otherwise emit `RETAINED_WORKTREE` with exact recovery coordinates and reason. Never delete remote, unknown, dirty, or recoverable work. Final, archive, cleanup, integration, push, and deploy remain separate gates.
