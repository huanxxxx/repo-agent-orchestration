# Delivery controller workflow

The delivery controller is a context router and acceptance owner. In `delivery`, it owns the accepted objective and baseline. In `architected`, operate from a validated `DESIGN_HANDOFF`, preserve its checkpoint, and report to the design authority. Do not absorb the design-authority role.

## Hot state

Keep only product objective, current gate, dependency-ready set, active peers, acceptance baseline, next product step, and, in `architected`, design checkpoint/task id. Keep the initial controller model/settings; if runtime metadata shows unexplained drift, stop routing and report controller-model drift.

If continuity is enabled, update the sole rolling handoff only when scope, material state, acceptance, recovery coordinates, or next product step changes. App messages carry task reports; do not mirror agent mechanics.

## Decide and dispatch

Start with a scope challenge: what existing mechanism already solves this, what is the smallest useful slice, and which independent lanes can run without shared writes or acceptance coupling?

For each candidate, ask whether authority/dependencies are ready, writes are exclusive/read-only, and the outcome needs separate context, acceptance, cross-turn wait, model, branch, recovery, design, audit, or formal review. A yes makes it a peer; otherwise use the current task or bounded internal subagent. Agent count alone is not a task boundary.

Dispatch every ready, non-conflicting peer within capacity; this does not require a separate user request to parallelize. Record the concrete dependency, shared write, acceptance coupling, or external gate behind serialization. Recompute only after a decision-relevant event.

Send the minimum task capsule: objective, necessary context, boundary, acceptance, and report target. Leave repository history, full test matrices, and unrelated package status out unless they change the peer's decision.

Every App-created user-visible task is a peer. Use `create_thread`, then `send_message_to_thread`; the controller is a coordination role, not its runtime parent. Internal tools - `spawn_agent`, `send_input`, agent send/follow-up, `wait_agent` - inherit the current path, return this turn, stay in parent-owned paths, and get no peer packet/tree/branch. Their id is never a peer `TASK_ID`; if synchronous return is unsuitable, use a peer.

`OWNED_PATHS` says where a task may write, not that any change there is acceptable. Require the smallest sufficient implementation and a mapping from each acceptance condition to changed paths and evidence. Boundary expansion is `blocked`, not permission to redesign.

## Prepare one route

Create one repository-local branch/worktree only after its peer is ready. Validate path, base, branch, registry, and status with the one-command packet path in [contracts.md](contracts.md). Never treat a remembered task path as current proof.

For review, prefer `root_readonly` for short stable-root review, `existing_worktree` for a frozen candidate, and `detached_snapshot` only for long, test-running, or historical review. Pause a writer while its frozen worktree is reviewed. The reviewer creates no tree. Design review is dispatched only by design authority.

For `app_default`, omit task model settings. For an explicit binding, use the host's advertised model catalog instead of guessing from the controller model name; submit real creation parameters and treat the binding as unverified until the host echoes the effective model.

Call `create_thread` once per dispatch in the saved project with `environment: {type: "local"}`. Its id proves creation only. Reject projectless, foreign-project, queued/App-managed-worktree, and `clientThreadId`-only routes. Empty/ambiguous/timed-out/unparseable means `creation outcome unknown`: end the turn, then reconcile source, project, objective, tree, branch, and base. Unavailable/failed App routing is `PROTOCOL_BLOCKED`; never fall back to `spawn_agent`.

Create inert first, not as continuation/correction/wait. Pass `--task-message` arguments unchanged to `send_message_to_thread`; App adds framing, so never embed `<codex_delegation>`. On failure/unknown, retain id/packet and reconcile next wake; never recreate/substitute. Start after route PASS.

## Wake fast path

The task-start route gate and repository-profile read are once per task binding. On later wakes:

1. Consume the wake-causing report/decision and already-delivered facts required for the same decision.
2. Reuse the validated route and stable profile. Recheck only identity/baseline facts that changed or became ambiguous.
3. Do not reread the full Skill/reference bundle, validator source, executor-only domain Skills, or implementation source merely to restate a frozen dispatch.
4. Construct `--task-message` once; send its arguments unchanged.
5. Complete synchronous acceptance, dispatch, correction, integration, or reporting, then End the controller turn.

After any successful send, end the turn; never inspect its target or another peer. A formal report to the contracted authority is the only allowed peer-to-peer message after read-only review or audit. Only a product-required first-dispatch `wait_threads` may run once; never call `wait_agent` for a peer. Any result ends the turn. No recursive waits or silence snapshots.

Before continuing/correcting, inspect current top-level runtime status once. `idle` and `notLoaded` mean no live turn; persisted historical turn rows are not a live-turn inventory. Record stale metadata but do not block, archive/restore, interrupt, or ask the user to stop a historical turn. If the task is `active`, do not send a plain `continue`. Use current active-turn evidence to steer/stop; if current active-turn evidence identifies more than one live turn, recover all of them.

## Checkpoint and reports

Do not strand completed work only in a dirty worktree. Before a cross-turn pause, ownership handoff, formal review, or final, verify exact owned paths and create a local checkpoint commit. Internal subagents return paths/evidence; the owning task makes the combined commit. Mixed ownership stays unstaged and is reported exactly.

`progress`, `blocked`, and `final` must use direct task-message with `TARGET_SETTINGS: preserve`. Task failure is not delivery failure. `progress` carries a decision fact; delivered terminal reports return control, and writer final names the checkpoint. A read-only audit final is a formal state update, not permission to contact other peers. A failed call leaves the packet undelivered; keep it plus a local failure note for next-wake recovery.

In `architected`, report only initial plan, decision-relevant milestones, reopen requests, and final evidence. `DECISION_REQUIRED: no` does not pause authorized work. A delivery controller may adjudicate implementation inside the frozen baseline, but it may not authorize itself to change the design; send `DESIGN_REOPEN_REQUEST` and pause only affected/dependent scope.

## Review, integrate, close

Freeze acceptance IDs/threat/non-goals. `delta` uses exact range/paths/clauses/checks, `expand_if`, reusable evidence; `full` needs a reason. Severity alone never grants scope. Correction stays delta-only unless baseline reopens. If binding/class/model unchanged, reuse the original `idle`/`notLoaded` reviewer: `fresh` means a new range/judgment, not a new task. Send one compact `send_message_to_thread` packet with findings, paths, and closure checks; reference baseline and do not resend binding. Create new only if original unavailable/archived, routing changed, conflict/second opinion is explicit, or baseline reopened. Map criteria/evidence; two new-blocker rounds trigger scope-drift audit.

Verify actual diff/commit, owned paths, checks, evidence limits, unresolved findings, and root-baseline drift. Passing acceptance is the stop condition. In `architected`, send final evidence with `DECISION_REQUIRED: yes`; design consistency remains with the design authority.

After PASS, classify any proposed closeout diff as `continuity_only` or `normative`. A continuity-only diff records existing state on repository-allowlisted paths; commit it under the current root-write lease. Never dispatch a docs-only reviewer merely to record PASS. Normative changes reopen the applicable baseline.

Archive only after acceptance and after correction/in-flight work is absent. Call `set_thread_archived({threadId: <accepted-task-id>, archived: true})` and confirm success. A peer `final` is delivery, not archive; archive is not cleanup.

After the archive decision, complete `CLOSEOUT_CLEANUP` for every peer-owned worktree/branch before ending the acceptance turn unless an external gate is explicitly missing. Inspect the exact registered worktree, local branch, head, dirty/untracked state, integration target, and saved recovery coordinates. If clean and integrated, or clean and explicitly abandoned with no recovery value, remove the Git worktree first and then delete only the local branch with the safest branch-delete mode that passes. If not safe, do not delete; emit a compact retained inventory:

```text
RETAINED_WORKTREE
TASK_ID:
WORKTREE:
BRANCH:
HEAD:
REASON:
NEXT_ACTION:
```

`REASON` must be concrete: dirty, untracked, not integrated, unknown owner, blocked, user-retained, missing external gate, or recoverable evidence. Never infer cleanup from task archival, age, naming, or directory location; never delete a remote branch from this closeout rule.
