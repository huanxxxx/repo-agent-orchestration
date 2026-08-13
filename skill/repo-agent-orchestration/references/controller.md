# Delivery controller workflow

In `delivery` mode, the current controller also owns the accepted objective and baseline. In `architected` mode, operate only from a validated `DESIGN_HANDOFF`, preserve its design checkpoint, and report to the separate design authority through the architected packets. Do not absorb the design-authority role merely because both roles coordinate work.

## Keep four mainline facts

Keep the product objective, current gate, active tasks, and next product step. In `architected` mode also keep the design checkpoint and design-authority task id. Add an authorization ceiling only when external or destructive actions are in scope. Do not maintain a second project-management system for agent mechanics.

If repository policy defines a continuity package, treat it as the durable repository copy of objective, scope, current state, acceptance, recovery coordinates, and next product step. Update it only when one of those facts materially changes. App task messages remain the delivery channel; do not copy every progress message or agent mechanic into the package.

## Decide readiness

Before dispatch, answer five questions:

1. Is the work authorized?
2. Are its inputs and dependencies ready?
3. Does it have an exclusive write boundary, or is it read-only?
4. Can it be accepted independently?
5. Does it need its own cross-turn wait, model binding, branch, or recovery boundary?

Use an independent user-visible peer task when question 4 or 5 is yes, or for formal review. Otherwise use the current task or a bounded internal subagent. Agent count alone is not a task boundary. Once implementation is authorized, calculate the ready set and dispatch every ready, non-conflicting peer task when capacity permits; this does not require a separate user request to parallelize. When serializing, record the one concrete dependency, shared write, acceptance coupling, or external gate. Re-run this decision when a peer reports or another real event wakes the controller; do not stay online merely to rescan.

## Distinguish peer tasks from internal subagents

Treat every App-created user-visible task as a peer, regardless of which task dispatched it. A controller owns coordination and acceptance decisions, not the peer's runtime turn. Only an internal-subagent capability creates a same-task parent/subagent relationship whose result must be joined before the current turn ends. Route by the actual creation capability: App task creation means peer lifecycle; internal subagent creation means current-turn participation. Never keep a controller online merely because it originated a peer task.

## Lock the implementation boundary

Dispatch one accepted outcome, not an invitation to redesign the surrounding system. `OWNED_PATHS` says where a task may write; it does not authorize every possible change inside those paths. Require the writer to make the smallest sufficient change and to stop when `ACCEPTANCE` and `REQUIRED_TESTS` pass. If the writer concludes that an architecture change, alternate execution path, or broader refactor is necessary, it reports the conflict and waits for reauthorization instead of widening the task.

## Prepare the route

For an independent peer write task, create one repository-local worktree and branch only when ready. That peer owns the tree. Its internal subagents inherit the exact execution path and may receive disjoint file scopes, but must not create another branch or worktree. Run the validator CLI to verify the owning peer's physical path, base, branch, registry entry, and status. Never reuse a task or chat's remembered path as a baseline without this live check; restore or recreate a missing tree first. Record the root status as a baseline rather than demanding an unrelated user-owned root be clean.

For a review, select the lightest target:

- stable short committed review: `root_readonly`;
- frozen candidate: `existing_worktree`;
- long, cross-turn, test-running, or historical review: create `detached_snapshot` on demand below `WORKTREE_ROOT`.

The reviewer does not create a tree. Pause the implementation owner while a formal reviewer uses its frozen tree. Never share a writable worktree between independent task owners.

## Commit before crossing a task boundary

Do not strand completed work only in a dirty worktree. Before a planned cross-turn pause, ownership handoff, formal review, or final report, inspect the exact task-owned paths, run proportional checks, and create a local checkpoint commit for each coherent recoverable unit. Freeze formal review on that commit. A checkpoint commit records real output after work; it is not a prechange snapshot and grants no push, integration, deployment, or publication authority.

Internal subagents working in one task never race to commit the shared branch. They return exact changed paths and evidence; the parent task verifies ownership and creates the combined checkpoint. If changes are mixed-owned, contain unsafe material, or cannot form a coherent commit, do not stage them. Preserve the dirty state and report the paths, reason, and next recovery action.

## Delegate inside the current task

Use internal subagents for bounded current-turn retrieval, comparison, or implementation slices that do not need separate acceptance or recovery. The parent task remains accountable for the combined result and gives each writing subagent non-overlapping paths. A subagent inherits the current cwd, branch, and worktree; it must not create or select another worktree. If the parent lacks write authority for that path, or the work becomes independently acceptable or cross-turn, stop and promote the remaining boundary to an independent task.

## Freeze and adjudicate review scope

Before the first review, freeze criterion IDs, the bounded threat model, and non-goals from the user's request and authoritative repository material. Keep that baseline unchanged across correction reviews unless its owning authority explicitly reopens it. In `delivery`, that authority is the user or predeclared repository policy. In `architected`, it is the design authority through `DESIGN_DECISION`. The delivery controller may choose implementation details already inside the baseline; it may not authorize itself to add a feature, alternate path, refactor, or crossed non-goal merely because it classified a finding as a scope-reopen request.

Require each blocking finding to identify the violated criterion and reproducible evidence. The controller, not the reviewer, decides whether it is an `accepted_blocker`, `non_blocking_observation`, or `scope_reopen_request`. Severity alone never grants scope or correction authority. Do not send non-blocking hardening to a writer.

On correction review, check the accepted blockers and regressions against the same baseline. New observations may be reported, but only mapped baseline violations can fail it. If two consecutive reviews each introduce a new accepted blocker, stop automatic correction, compare the work with the last minimal candidate, and run a scope-drift audit. Revert unnecessary hardening, defer it, or request explicit authority; do not silently start a third correction cycle.

## Create once and continue once

1. Preflight the saved repository project and task API.
2. Make exactly one creation call for a logical peer dispatch in a controller turn. If its receipt is empty, ambiguous, timed out, unparseable, or otherwise lacks a confirmed task id, record `creation outcome unknown`; do not infer failure and do not call create again in that turn. On the next real controller wake, list tasks and reconcile by source controller, project, objective, worktree, branch, and base. Adopt the single match, stop and resolve duplicates, or retry only after the inventory shows no created task.
3. Create the peer task against that project with the explicit target object `target: {type: "project", projectId, environment: {type: "local"}}`; do not rely on the Git-project default, and reject `projectless` or App-managed substitute trees. A queued worktree setup, worktree-creation UI, or `clientThreadId` without a created task is a phantom task receipt, not a peer to wait on. If using a same-task fork, require `environment: {type: "same-directory"}` and reject `worktree`.
4. Include the dispatch packet and conditional execution authority in the initial instruction.
5. The task performs the fast route gate first. A passing task continues implementation or review in the same turn; a failing task writes nothing and reports `blocked`.
6. Do not require a binding-only turn, a controller receipt decision, and a second authorization message for a route that can be decided deterministically.

For `app_default` write or review policy, omit `model` and `thinking` so the destination host selects its compatible default. For an explicit repository or user binding, first confirm that the task host's advertised model catalog contains the requested model, then use real creation parameters. If the model is unavailable or capability discovery is unavailable, report the explicit-binding gap instead of guessing from the controller model name or silently substituting another model. Treat a submitted binding as unverified unless the product echoes the effective runtime model.

## Receive reports and yield

Only direct peer-to-peer task-message delivery is an ordinary report. Require `TARGET_SETTINGS: preserve`: the sender must omit `model` and `thinking` because task-message overrides apply to the destination task. Peer writers and implementation reviewers report to the delivery controller; a design reviewer reports to the design authority. In `architected` mode, send the design authority only the initial delivery plan, decision-relevant milestones, design reopen requests, and final delivery evidence. A `DELIVERY_UPDATE` with `DECISION_REQUIRED: no` is informational and does not pause authorized delivery. `progress` keeps the peer's current turn; record the new fact but do not send a continuation to an already-running peer. Before any correction or continuation, inspect the peer's current top-level runtime status. `idle` or `notLoaded` is authoritative evidence that no turn is live; persisted historical turn rows are not a live-turn inventory and must not be paged solely to prove liveness. A historical `inProgress` row superseded by later terminal turns is stale unless the product explicitly identifies it as currently active. Record the inconsistency, but do not block, archive/restore, interrupt, or ask the user to stop a historical turn. If the task is `active`, do not send a plain `continue`; use the product's current active-turn evidence for stop/interrupt, same-turn steer, or multi-in-flight recovery. If current active-turn evidence identifies more than one live turn, recover all of them instead of addressing only one. After an urgent HOLD, verify the top-level runtime is no longer active before routing again. `blocked` and `final` return control to the contracted authority. A peer write-task final names its checkpoint commit; a blocked or unsafe-to-commit report names the exact dirty paths and reason. A peer's local final may be read once for recovery, but is not normal delivery.

Record the controller model and reasoning effort before dispatch. On a report-triggered wake, compare the current turn settings with that baseline. If they changed without an explicit user selection, stop routing and report controller-model drift before accepting or integrating evidence.

After successful peer creation or continuation, perform a product-required startup wait at most once. Use it only to detect immediate failure or confirm start; an ordinary active, progress, or timeout result ends the controller turn and must not trigger a second wait. Resume only on:

- a delivered task report;
- a real one-shot checkpoint;
- a blocker or input request;
- a user status request;
- an acceptance or integration decision.

Do not call recursive waits, relay unchanged peer progress, or use an immediate snapshot as a fake future checkpoint. If the product has no one-shot wakeup, silent-peer recovery is available only on the next real controller wake; state that limitation once instead of adding per-task ceremony.

## Accept and close

Verify the actual diff or reviewed commit, owned paths, required tests, evidence limits, adjudicated findings, and root-baseline drift. Require a concise mapping from each acceptance condition to its changed paths and verification evidence; defer or reject changes that cannot be justified by the accepted outcome even when tests are green. The baseline passes when it has no accepted blocker; non-blocking observations do not prevent PASS and do not authorize more implementation. Integrate only within authority and in dependency order. In `architected` mode, send a final `DELIVERY_UPDATE` with `DECISION_REQUIRED: yes`; only the design authority may declare final design consistency. Keep external gates separate.

Archive a peer task after acceptance is verified and no correction or in-flight operation remains. Call `set_thread_archived({threadId: <accepted-task-id>, archived: true})` and confirm success before declaring closure. A peer's `final` does not archive itself. Do not archive a peer that still needs correction, input, or recovery. Remove a worktree separately, only when clean and without recovery value.
