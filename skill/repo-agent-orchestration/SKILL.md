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

- Keep bounded current-turn lookup/comparison/non-overlapping slices in the current task or an internal subagent; inherit the exact path and create no worktree.
- Use a peer write task for independently acceptable, cross-turn, separately recoverable, or explicitly model-bound implementation; give it one repository-local worktree.
- Use a peer review task for formal review: stable root needs none, a frozen candidate reuses its paused writer tree read-only, and only a long/test-running/historical review gets a detached snapshot.

An App-created user-visible task is a peer task. Route by the actual creation capability. Only an internal subagent has a same-task parent/subagent relationship; it returns this turn, inherits path/authority, and owns no independent milestone, verdict, model, recovery, branch, or tree. More agents alone never justify more worktrees. Different peer write tasks never share a writable worktree.

## Dispatch and execute

1. Create peers only for separate acceptance, wait, model, branch, recovery, or formal review. After authorization, dispatch all ready, non-conflicting peer tasks within capacity; do not await another parallelism instruction or split coupled work to fill slots.
2. Require the smallest change that satisfies `OBJECTIVE`, `ACCEPTANCE`, and `REQUIRED_TESTS`. Every changed path must have a concrete acceptance justification. Once the required acceptance and tests pass, stop implementation; no speculative feature, abstraction, alternate path, refactor, or hardening.
3. Give a ready writer one local branch/tree and exclusive paths. Internal subagents inherit it; that task verifies and commits the combined checkpoint. Reject projectless/foreign-project tasks. Create peers in the saved project with `environment: {type: "local"}` and the repository-local execution path, never an App-managed tree.
4. Make one creation call per logical dispatch. A task id completes creation only; successful delivery completes dispatch. If id follows, create an inert peer and send one id-bound packet. Do not wait. An empty, ambiguous, timed-out, queued worktree setup, `clientThreadId`-only, or unparseable receipt is a phantom task and never authorizes an immediate second creation call; reconcile on real wake.
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

Successful delivery ends the sender turn except one new-task startup check. Do not read/list/wait on the target, narrate its progress, or inspect another peer while handling one report. A product-required startup wait at most once may follow only a new task's first dispatch; active, progress, or timeout means end the controller turn. Resume only on an inbound task message, user request, or acceptance action; never poll.

## Accept and close

Freeze acceptance, threat model, and non-goals. Review the exact delta by default: changed paths, named clauses, focused checks, and exact-checkpoint evidence reuse. Full context or full-suite reruns need an explicit reason. Findings cite a criterion and reproducible evidence; reviewers do not invent acceptance. The controller adjudicates and verifies diff, commit, checks, and evidence limits. State limits: focused checks do not prove the full repository, protected environments, or production behavior. Two correction rounds with new blockers trigger scope-drift audit, not an automatic third.

In `architected`, final evidence returns to design authority. Merge, push, deploy, publish, production data, credentials, and permissions keep separate gates.

After PASS, do not reopen review merely because rolling handoff moves HEAD. Keep the reviewed checkpoint distinct from the later continuity checkpoint. A `continuity_only` closeout changes no implementation, normative design/contracts, acceptance, non-goals, findings, or verdict evidence; root-write authority verifies/commits it without review.

Archive an accepted peer only after correction/in-flight work ends and confirm it. Final, archive, worktree removal, integration, push, and deploy are separate. A clean task-tree HEAD is already a recovery anchor.
