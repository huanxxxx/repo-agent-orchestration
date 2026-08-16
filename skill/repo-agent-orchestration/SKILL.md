---
name: repo-agent-orchestration
description: Coordinate repository work in direct, delivery, or architected mode using bounded internal subagents, peer tasks, repository-local worktrees, validated packets, independent review, and lightweight recovery.
---

# Repository Agent Orchestration

Keep product delivery primary; pay coordination cost only for real task boundaries.

## Start once; wake lightly

At task start, read repository `AGENTS.md`, resolve mode/role and configuration, and run the fast route gate once per task/runtime binding. Record route, acceptance, and report destination; PASS continues in the same turn.

On later wakes or compaction, reuse proven facts. Do not reload the Skill bundle, profile, route gate, or unchanged continuity unless route identity, Skill version, or authority changed or became ambiguous. Commits do not invalidate the route; new packets live-check branch/HEAD. Consume one event, read changed hot state, act, and yield.

Load references progressively:

- [architected.md](references/architected.md): select/operate `architected`;
- [controller.md](references/controller.md): controller readiness, parallelism, acceptance, closure;
- [contracts.md](references/contracts.md): first use or failure of a packet kind;
- [continuity.md](references/continuity.md): repository-opted durable package or post-PASS closeout;
- [recovery.md](references/recovery.md): takeover, silence, wrong route, mixed ownership, cleanup.

For routine dispatch, do not inspect protocol source, enumerate tool schemas, load executor-only Skills, or walk implementation. Use the CLI; writers load implementation instructions. Inspect deeper only for planning, acceptance, adjudication, recovery, or protocol defects.

## Choose authority

| Mode | Use |
|---|---|
| `direct` | Short current-task work or read-only analysis with no independent acceptance boundary |
| `delivery` | A frozen or straightforward outcome needing independent implementation, review, recovery, or parallel delivery |
| `architected` | New/changing architecture, data contracts, core workflows, product boundaries, multiple implementation packages, material direction choices, or an explicitly requested design authority |

Repository tiers keep local meanings. In `delivery`, the controller owns the outcome. In `architected`, design owns direction/final consistency, delivery owns implementation, and peers execute/review; only the design authority may change the design baseline through `DESIGN_REOPEN_REQUEST` and `DESIGN_DECISION`.

## Choose the lightest route

- Keep bounded current-turn slices here or in an internal subagent; inherit the path, create no worktree, and return this turn.
- Use a peer writer for independently acceptable, cross-turn, recoverable, or model-bound work; give it one repository-local worktree.
- Use a peer review task for formal review: stable root needs none, a frozen candidate reuses its paused writer tree read-only, and only a long/test-running/historical review gets a detached snapshot.

An App-created user-visible task is a peer task. Its actual creation capability is `create_thread`; deliver via `send_message_to_thread`. `spawn_agent` creates only the same-task parent/subagent relationship; its id is never a peer `TASK_ID`. `send_input`, agent send/follow-up, and `wait_agent` are internal-only: inherit path/authority, return this turn, and get no formal packet, acceptance, checkpoint, model, recovery, branch, or tree. If synchronous return is unsuitable, use a peer. More agents alone never justify more worktrees; different peer write tasks never share one.

## Dispatch and execute

1. Create peers only for separate acceptance, wait, model, branch, recovery, or formal review. After authorization, dispatch all ready, non-conflicting peer tasks within capacity; do not await another parallelism instruction or split coupled work to fill slots.
2. Require the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`. Every changed path must have a concrete acceptance justification. Once the required acceptance and tests pass, stop implementation; no speculative feature, abstraction, alternate path, refactor, or hardening.
3. Give a ready writer one local branch/tree and exclusive paths. Internal subagents inherit it; that task verifies and commits the combined checkpoint. Reject projectless/foreign-project tasks. Create peers in the saved project with `environment: {type: "local"}` and the repository-local execution path, never an App-managed tree.
4. Call `create_thread` once. Its id proves creation; one `send_message_to_thread` receipt proves dispatch. Create inert, send one id-bound packet, and do not wait. Empty/ambiguous/timed-out/queued-worktree/`clientThreadId`-only/unparseable is phantom: end the turn and reconcile on wake. Unavailable/failed peer routing is `PROTOCOL_BLOCKED`; never substitute `spawn_agent`.
5. For `app_default`, omit `model` and `thinking`. Explicit bindings use actual task parameters only after host discovery; prompt text is not binding. Reports must omit `model` and `thinking` and preserve destination settings.
6. Use the exact execution path. The CLI proves required paths currently exist and match Git registry, branch, and commit. Root status is compared with its baseline, not forced clean.
7. Before a cross-turn pause, ownership handoff, formal review, or `final`, verify and locally commit coherent owned output. Never stage another owner's files; if unsafe, preserve and report exact dirty paths and recovery action.

## Cross a task boundary once

Stream each outgoing packet's JSON fields to one command:

```text
python scripts/construct_packet.py --kind <kind> --live -
```

This constructs, statically/live validates, and emits only on PASS. Do not create temporary packet files or invoke the validator afterward. Stream an incoming packet once to:

```text
python scripts/validate_dispatch_contract.py --kind <kind> -
```

The validator is a boundary check, not a workflow engine. An inexpressible boundary is `PROTOCOL_BLOCKED`: do not handcraft, relabel, or continue its dependent action.

## Process one event and yield

Treat each App wake as one bounded event batch. Process only its event and already-delivered facts needed for the same decision. Before continuing a peer, check current top-level status once: `idle` or `notLoaded` means no live turn despite stale `inProgress` history; `active` forbids another continuation or correction.

Successful delivery ends the sender turn. Do not inspect its target or another peer. Only a product-required first-dispatch check may call `wait_threads` once, never `wait_agent`; any result ends the turn. Resume on an inbound report, user request, or acceptance; never poll.

## Accept and close

Freeze acceptance, threat model, and non-goals. Review the exact delta by default: changed paths/clauses, focused checks, and checkpoint evidence. Full context/suite needs a reason. Corrections reuse the original eligible reviewer; `fresh` means a new range/judgment, not a new task. Findings cite criteria and evidence; reviewers never invent acceptance. Controller verifies diff, commit, checks, and evidence limits; focused checks do not prove the full repository, protected systems, or production behavior. Two rounds with new blockers trigger scope-drift audit, not an automatic third.

In `architected`, final evidence returns to design authority. Merge, push, deploy, publish, production data, credentials, and permissions keep separate gates.

After PASS, do not reopen review merely because rolling handoff moves HEAD. Keep the reviewed checkpoint distinct from the later continuity checkpoint. A `continuity_only` closeout changes no implementation, normative design/contracts, acceptance, non-goals, findings, or verdict evidence; root-write authority verifies/commits it without review.

Archive an accepted peer only after correction/in-flight work ends and confirm it. Final, archive, worktree removal, integration, push, and deploy are separate. A clean task-tree HEAD is already a recovery anchor.
