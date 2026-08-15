# Delivery controller workflow

In `delivery`, the controller owns the accepted objective and baseline. In `architected`, operate from a validated `DESIGN_HANDOFF`, preserve its checkpoint, and report to the design authority. Do not absorb the design-authority role.

## Keep only delivery hot state

Keep the product objective, current gate, dependency-ready set, active peers, acceptance baseline, next product step, and—only in `architected`—design checkpoint and design task id. Keep the initial controller model/settings without rediscovering them each wake. If current runtime metadata reveals an unexplained change, stop routing and report controller-model drift.

If repository policy opts into continuity, update its sole rolling handoff only when scope, material state, acceptance, recovery coordinates, or next product step changes. App messages carry task reports; do not mirror agent mechanics.

## Decide and dispatch ready work

For each candidate, ask whether authority and dependencies are ready, writes are exclusive/read-only, and the outcome needs separate acceptance, a cross-turn wait, model, branch, recovery, or formal review. A yes to either boundary makes it a user-visible peer; otherwise use the current task or a bounded internal subagent. Agent count alone is not a task boundary.

Dispatch every ready, non-conflicting peer within capacity; this does not require a separate user request to parallelize. Record the concrete dependency, shared write, acceptance coupling, or external gate behind serialization. Recompute only after a decision-relevant event.

Every App-created user-visible task is a peer. The controller is a coordination role, not its runtime parent. A same-task internal subagent inherits the exact current execution path, returns this turn, and may write only within non-overlapping paths already owned by the parent; it must not create another branch or worktree.

`OWNED_PATHS` says where a task may write, not that any change there is acceptable. Require the smallest sufficient implementation and a mapping from each acceptance condition to changed paths and evidence. Boundary expansion is `blocked`, not permission to redesign.

## Prepare one route

Create one repository-local branch/worktree only after its peer is ready. Validate its path, base, branch, registry entry, and status using the one-command packet path in [contracts.md](contracts.md). Never treat a remembered task path as current proof.

For review, prefer `root_readonly` for a short stable-root review, `existing_worktree` for a frozen candidate, and an on-demand `detached_snapshot` for long, test-running, or historical review. Pause a writer while its frozen worktree is reviewed. The reviewer creates no tree. Design review is dispatched only by design authority.

For `app_default`, omit task model settings. For an explicit binding, use the host's advertised model catalog instead of guessing from the controller model name; submit it through real creation parameters and treat it as unverified until the host echoes the effective model.

Make exactly one creation call per dispatch. Target the saved project with `target: {type: "project", projectId, environment: {type: "local"}}`. A task id completes creation only. Reject projectless, foreign-project, queued-worktree, App-managed-worktree, and `clientThreadId`-only routes. An empty, ambiguous, timed-out, or unparseable receipt means `creation outcome unknown`; end the turn. On real wake, list tasks and reconcile by source, project, objective, worktree, branch, and base before retrying.

Packets need the returned id. Create with an inert route fingerprint and no authority, then validate/send one id-bound packet. It is dispatch, not a continuation/correction or startup wait; receipt completes dispatch. If delivery fails/is unknown, retain id/packet, do not recreate, and reconcile next wake. Peer executes only after route PASS.

## Wake fast path

The task-start route gate and repository-profile read are once per task binding. On later wakes:

1. Consume the wake-causing report/decision and already-delivered facts required for the same decision.
2. Reuse the validated route and stable profile. Recheck only identity/baseline facts that changed or became ambiguous.
3. Do not reread the full Skill/reference bundle, validator source, executor-only domain Skills, or implementation source merely to restate a frozen dispatch. Read deeper only for actual planning, acceptance, adjudication, recovery, or protocol debugging.
4. Build and live-validate one outgoing packet in the single constructor call; send it once.
5. Complete synchronous acceptance, dispatch, correction, integration, or reporting, then End the controller turn.

Do not keep the controller alive to observe a peer. Use one startup wait only when the product explicitly requires confirmation beyond its creation receipt. An active/progress/timeout result must not trigger a second wait. Do not call recursive waits or invent immediate snapshots as future silence checks.

Before continuing/correcting, inspect current top-level runtime status once. `idle` and `notLoaded` mean no live turn; persisted historical turn rows are not a live-turn inventory. Record stale metadata but do not block, archive/restore, interrupt, or ask the user to stop a historical turn. If the task is `active`, do not send a plain `continue`. Use current active-turn evidence to steer/stop; if current active-turn evidence identifies more than one live turn, recover all of them. Confirm an urgent HOLD actually stopped the runtime before rerouting.

## Checkpoint and reports

Do not strand completed work only in a dirty worktree. Before a cross-turn pause, ownership handoff, formal review, or final, verify exact owned paths and create a local checkpoint commit. Internal subagents return paths/evidence; the owning task makes the combined commit. Mixed ownership stays unstaged and is reported exactly.

`progress`, `blocked`, and `final` must use direct task-message with `TARGET_SETTINGS: preserve`. Task failure is not delivery failure. `progress` carries a decision fact; delivered terminal reports return control, and writer final names the checkpoint. A failed call leaves the packet undelivered; keep it plus a local failure note for next-wake recovery.

In `architected`, report only the initial plan, decision-relevant milestones, reopen requests, and final evidence. `DECISION_REQUIRED: no` does not pause authorized work. A delivery controller may adjudicate implementation inside the frozen baseline, but it may not authorize itself to change the design; send `DESIGN_REOPEN_REQUEST` and pause only affected/dependent scope.

## Review, integrate, close

Freeze acceptance IDs, threat model, and non-goals. Default to `delta` on the exact range: scope changed paths/direct clauses and budget context/checks/expand_if. Reuse exact-checkpoint evidence; independent judgment is not a full rerun. `full` requires a reason. The prompt is route capsule plus packet. Do not append duplicate lineage, package reads, or test matrices. Correction review is delta-only unless the baseline reopens. Findings map criteria to evidence. Severity alone never grants scope. After two rounds with new blockers, perform a scope-drift audit.

Verify the actual diff/commit, owned paths, checks, evidence limits, unresolved findings, and root-baseline drift. Passing acceptance is the stop condition. In `architected`, send final evidence with `DECISION_REQUIRED: yes`; design consistency remains with the design authority.

After PASS, classify any proposed closeout diff as `continuity_only` or `normative`. A continuity-only diff records existing state on repository-allowlisted paths; commit it under the current root-write lease. Never dispatch a docs-only reviewer merely to record PASS. Normative changes reopen the applicable baseline.

Archive only after acceptance and after correction/in-flight work is absent. Call `set_thread_archived({threadId: <accepted-task-id>, archived: true})` and confirm success. Task final, archival, and worktree removal remain separate.
