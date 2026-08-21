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

On later wakes or compaction, reuse proven facts. Do not reload the Skill bundle, profile, route gate, or unchanged continuity unless route identity, Skill version, or authority changed or became ambiguous. Commits do not invalidate the route; new packets live-check branch/HEAD. Consume one event, read changed hot state, act, and yield.

References: [architected.md](references/architected.md) for `architected`; [controller.md](references/controller.md) for dispatch/acceptance; [contracts.md](references/contracts.md) for first use or failure of a packet kind; [continuity.md](references/continuity.md) for durable state; [recovery.md](references/recovery.md) for takeover, silence, wrong route, mixed ownership, or cleanup.

For routine dispatch, use the CLI; do not inspect protocol source, enumerate tool schemas, load executor-only Skills, or walk implementation. Writers load implementation instructions. Inspect deeper only for planning, acceptance, adjudication, recovery, or defects.

## Choose authority

Use `direct` for short current-task work, `delivery` for a frozen outcome needing independent implementation/review/recovery/parallel work, and `architected` for architecture, data contracts, core workflows, product boundaries, multiple packages, material direction choices, or an explicitly requested design authority.

Think in task types first: `direct`, `peer_write`, `peer_review`, `peer_design`, and `peer_audit`. The older mode labels remain compatibility boundaries. In `delivery`, the controller owns the outcome. In `architected`, design owns direction/final consistency, delivery owns implementation, and peers execute/review/audit; only the design authority may change the design baseline through `DESIGN_REOPEN_REQUEST` and `DESIGN_DECISION`.

## Choose the lightest route

Keep bounded current-turn slices here or in an internal subagent; inherit the path, create no worktree, and return this turn. Use a peer for separate context, independent acceptance, cross-turn waiting, model binding, recovery, design, audit, or formal review. Stable-root review needs no tree; a frozen candidate reuses its paused writer tree read-only; only long/test-running/historical review gets a detached snapshot.

An App-created user-visible task is a peer task. Its actual creation capability is `create_thread`; deliver via `send_message_to_thread`. `spawn_agent`, `send_input`, agent send/follow-up, and `wait_agent` are internal-only: inherit path/authority, return this turn, and get no formal packet, acceptance, checkpoint, model, recovery, branch, or tree. Their id is never a peer `TASK_ID`; if synchronous return is unsuitable, use a peer. More agents alone never justify more worktrees; different peer write tasks never share one.

## Dispatch and execute

1. Dispatch all ready, non-conflicting peers within capacity; do not await another parallelism instruction or split coupled work to fill slots.
2. Send a small task capsule: `OBJECTIVE`, `CONTEXT`, `BOUNDARY`, `ACCEPTANCE`, `REPORT_TO`. The packet schema adds route, model, archive, and Git facts; those mechanics must not become the task itself.
3. Require the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`. Every changed path must have a concrete acceptance justification. Once the required acceptance and tests pass, stop implementation.
4. Give a ready writer one local branch/tree and exclusive paths. Internal subagents inherit it; that task verifies and commits the combined checkpoint. Reject projectless/foreign-project tasks. Create peers in the saved project with `environment: {type: "local"}` and the repository-local execution path, never an App-managed tree.
5. Call `create_thread` once. Its id proves creation; a `send_message_to_thread` receipt proves dispatch. Create inert, pass `--task-message` JSON unchanged, and do not wait. Empty/ambiguous/timed-out/queued-worktree/`clientThreadId`-only/unparseable is phantom: end and reconcile on wake. Failed/unavailable peer routing is `PROTOCOL_BLOCKED`; never substitute `spawn_agent`.
6. For `app_default`, omit `model` and `thinking`; explicit bindings use actual task parameters only after host discovery. Reports must omit `model` and `thinking` and preserve destination settings.
7. Use the exact execution path; the CLI proves paths match Git registry, branch, and commit. Root status is compared with its baseline, not forced clean.
8. Before a cross-turn pause, ownership handoff, formal review, or `final`, verify and locally commit coherent owned output. Never stage another owner's files; if unsafe, report exact dirty paths and recovery action.

## Cross a task boundary once

Stream each outgoing packet's JSON fields to one command:

```text
python scripts/construct_packet.py --kind <kind> --live --task-message -
```

`--task-message` emits validated arguments. Pass unchanged; App frames them. Do not create temporary packet files or validate twice. Validate incoming once:

```text
python scripts/validate_dispatch_contract.py --kind <kind> -
```

The validator is a boundary check, not a workflow engine. Before send, correct one shape error once without changing semantics or route. A repeat error, incoming validation failure, or attempted/ambiguous delivery is `PROTOCOL_BLOCKED`.

## Process one event and yield

Treat each App wake as one bounded event batch. Process only its event and already-delivered facts needed for the same decision. Before continuing a peer, check current top-level status once: `idle` or `notLoaded` means no live turn despite stale `inProgress` history; `active` forbids another continuation or correction.

Successful delivery ends the sender turn. Sending a formal report to `REPORT_TO` is required delivery, not cross-peer meddling. Do not inspect its target or another peer afterward. Only a product-required first-dispatch check may call `wait_threads` once, never `wait_agent`; any result ends the turn. Resume on an inbound report, user request, overdue committed milestone, or acceptance; never poll.

## Accept and close

Freeze acceptance, threat model, and non-goals. Review the exact delta by default: changed paths/clauses, focused checks, and checkpoint evidence. Full context/suite needs a reason. Corrections reuse the original eligible reviewer; `fresh` means a new range/judgment, not a new task. Findings cite criteria and evidence; reviewers never invent acceptance. Controller verifies diff, commit, checks, and evidence limits; focused checks do not prove the full repository, protected systems, or production behavior.

In `architected`, final evidence returns to design authority. Merge, push, deploy, publish, production data, credentials, and permissions keep separate gates.

After PASS, do not reopen review merely because rolling handoff moves HEAD. Keep the reviewed checkpoint distinct from the later continuity checkpoint. A `continuity_only` closeout changes no implementation, normative design/contracts, acceptance, non-goals, findings, or verdict evidence; root-write authority verifies/commits it without review.

Archive an accepted peer only after correction/in-flight work ends and confirm it. Then run `CLOSEOUT_CLEANUP`: classify the task worktree and local branch as removed or retained. Remove only after resolving path/branch/head/status, proving clean state plus integration or explicit abandonment, saving recovery coordinates, and confirming no recovery value. Remove the registered worktree before deleting the local branch; never delete remote branches or force-delete unknown, dirty, or recoverable work. If cleanup is unsafe or deferred, emit `RETAINED_WORKTREE` with exact task id, path, branch, head, reason, and next action. Final, archive, cleanup, integration, push, and deploy are separate gates.
