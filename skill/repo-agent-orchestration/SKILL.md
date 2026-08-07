---
name: repo-agent-orchestration
description: Coordinate multi-agent repository work with deterministic routing between a controller, user-visible execution or review tasks, and short read-only internal helpers. Use for multi-step repository implementation, parallel task dispatch, repo-local worktree isolation, independent review, model binding, milestone handoffs, stalled-task recovery, integration, archival, or collaboration-governance setup.
---

# Repository Agent Orchestration

Coordinate repository work without replacing user instructions or repository policy.

## Establish authority

1. Read the current repository `AGENTS.md` and any active execution package before planning work.
2. Treat explicit user instructions and repository-local facts as authoritative.
3. Keep product scope, external-write authority, write-task model defaults, review-task model policy, shared integration paths, and release gates repository-local.
4. Preserve model-role separation: the controller keeps the model and reasoning selected for its App task; write tasks use the repository's explicitly bound execution model; review tasks follow the repository's review policy, which may deliberately use `app_default`.
5. Do not use this skill to broaden authorization or convert local evidence into production evidence.

## Anchor the product mainline

Record the objective, current gate, active tasks, ready candidates, next step after the gate, and authorization ceiling. Keep collaboration mechanics subordinate to this mainline.

Keep execution packages attached to product topics, not assistants, sessions, or worktrees. Keep live owner, model, wait, slot, and candidate-matrix state in the controller; write only durable recovery or integration facts back to repository documents.

Read [references/controller.md](references/controller.md) when acting as the controller or deciding parallelism.

## Route work deterministically

Use a user-visible task for any file write, test change, commit, formal review, long or cross-turn work, milestone ownership, or independently accepted deliverable. Bind writing to a repository-local worktree. Bind formal read-only review to the frozen implementation worktree.

Use an internal helper only for bounded read-only retrieval, evidence extraction, fact comparison, or mechanical classification that completes in the current controller turn. Do not let an internal helper write, commit, issue formal PASS/FAIL, own a milestone, or wait across turns.

If visible-task creation, worktree binding, or a required explicit write-task model binding fails, stop and report the capability gap. Do not silently fall back to App defaults, an internal writer, or controller implementation. For review tasks, `app_default` is allowed only when it is the declared repository policy, not as an accidental fallback.

## Dispatch and coordinate

1. Audit authorized candidates at task start, plan freeze, blocker clearance, dispatch, and stage integration. Check dependency closure, complete inputs, independent acceptance, isolated writes, shared mutable surfaces, and external gates.
2. Dispatch two or more ready tasks in the same wave when slots permit. Continue scanning ready candidates while other tasks run or wait. Record the exact shared write, dependency, acceptance coupling, or authorization blocker when serializing.
3. Create worktrees only for authorized, dependency-closed work that is ready to start. Do not pre-create future trees or create an integration branch merely because a task is large.
4. Give each writable worktree one task boundary, one branch, and one user-visible write owner. Never share a writable worktree between tasks.
5. Resolve and verify the repository, main head, dirty state, exact base, unoccupied branch and target, repository-local path, and final worktree coordinates before dispatch. Do not accept a symlink substitute or a silently created platform-managed tree.
6. Separate task hosting from task execution. Reject projectless tasks. For a repository-local worktree, bind the user-visible task to the current repository's saved project with environment `local`, verify the task project and host cwd equal the repository root, and bind every repository command or file operation to the separate exact execution worktree. A path written into the prompt alone is not execution binding.
7. Start a newly created task with a read-only route check and no write authority. Verify its non-null project id, repository host cwd, registered worktree coordinates, clean root tree, and exact execution worktree; then send a separate write authorization only after the binding receipt passes. Never create a replacement merely because setup is pending or a result is delayed.
8. Pass an explicit task contract. Bind write-task models through the real creation or continuation parameters; prompt text alone is not model binding. For a review contract that declares `MODEL_POLICY: app_default`, omit the model override deliberately so the task uses the App default, and record the effective model as unverified unless the product echoes it.
9. Require event-driven milestone reports with the evidence required by the milestone. Every worker or reviewer report must be validated, sent to the controller through the task-message capability, and confirmed delivered before the task emits its local final. A local task final is not controller delivery. Deliver controller decisions the same way; never make the user relay routine coordination.
10. Treat turn ownership literally. A report that ends the current task turn must use `TURN_STATE: ending` and `owner=controller`, even when the same task owns the next implementation stage. Use `owner=task` only when the current turn remains in progress after the report. Transfer ownership back only through a successful continuation message.
11. Make controller waiting event-driven. After task creation or continuation succeeds, optionally take one immediate nonblocking status snapshot, then end the controller turn. Do not keep the controller active to monitor progress, and do not emit unchanged "still running" updates. A delivered task message, due one-shot checkpoint, blocker or input signal, user status request, or acceptance decision starts the next purposeful controller turn.
12. Give every dispatched stage a non-`none` missing-report checkpoint. `current_turn_once` is consumed by at most one immediate status snapshot and does not create a long-running wait. After that snapshot, or immediately when it is skipped, yield. Use an ISO-8601 checkpoint only with a true one-shot wakeup. Never recursively call a wait after an unchanged result.
13. Never simulate a one-shot check with a recurring automation. If the product lacks a true one-shot wakeup, report that limitation.

Read [references/contracts.md](references/contracts.md) before creating a write task, review task, or milestone report. Run `scripts/validate_dispatch_contract.py` against the task packet before creation, against the binding receipt before granting execution authority, and against every milestone report before sending it to the controller.

## Accept and integrate

1. Treat worker or reviewer PASS as evidence, not as controller approval.
2. Verify task coordinates, dirty state, actual diff, exact staged paths, required tests, evidence limits, and unresolved findings. A focused or local PASS must not be promoted to repository-wide, external-system, or production evidence.
3. Integrate only within explicit authority and in dependency order. Re-run relevant acceptance after integration.
4. Keep push, deployment, publication, production data, credentials, and permission changes behind their own authorization gates.
5. Mark `PASS_VERIFIED` only after final evidence is received, acceptance is independently verified, and no blocker, reply, correction, or in-flight operation remains. Archive the user-visible task immediately after that gate. Retain a worktree while it still has recovery value.

## Recover safely

Read [references/recovery.md](references/recovery.md) before taking over a controller, changing collaboration mode, handling a silent task, or separating a dirty shared worktree. Preserve coordinates and in-flight work before rerouting.

## Keep the skill lightweight

Do not introduce repository-wide state machines, authorization receipts, machine-owned task cards, or broad policy schemas merely to coordinate agents. Prefer repository facts, explicit task contracts, Git coordinates, task messages, and focused validation.
