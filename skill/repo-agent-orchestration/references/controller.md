# Controller workflow

## Keep four mainline facts

Keep the product objective, current gate, active tasks, and next product step. Add an authorization ceiling only when external or destructive actions are in scope. Do not maintain a second project-management system for agent mechanics.

If repository policy defines a continuity package, treat it as the durable repository copy of objective, scope, current state, acceptance, recovery coordinates, and next product step. Update it only when one of those facts materially changes. App task messages remain the delivery channel; do not copy every progress message or agent mechanic into the package.

## Decide readiness

Before dispatch, answer five questions:

1. Is the work authorized?
2. Are its inputs and dependencies ready?
3. Does it have an exclusive write boundary, or is it read-only?
4. Can it be accepted independently?
5. Does it need its own cross-turn wait, model binding, branch, or recovery boundary?

Use an independent user-visible task when question 4 or 5 is yes, or for formal review. Otherwise use the current task or a bounded internal subagent. Agent count alone is not a task boundary. Dispatch every ready, non-conflicting independent task when capacity permits. When serializing, record the one concrete dependency, shared write, acceptance coupling, or external gate. Re-run this decision when a task reports or another real event wakes the controller; do not stay online merely to rescan.

## Prepare the route

For an independent write task, create one repository-local worktree and branch only when ready. That task owns the tree. Its internal subagents inherit the exact execution path and may receive disjoint file scopes, but must not create another branch or worktree. Run the validator CLI to verify the owning task's physical path, base, branch, registry entry, and status. Never reuse a task or chat's remembered path as a baseline without this live check; restore or recreate a missing tree first. Record the root status as a baseline rather than demanding an unrelated user-owned root be clean.

For a review, select the lightest target:

- stable short committed review: `root_readonly`;
- frozen candidate: `existing_worktree`;
- long, cross-turn, test-running, or historical review: create `detached_snapshot` on demand below `WORKTREE_ROOT`.

The reviewer does not create a tree. Pause the implementation owner while a formal reviewer uses its frozen tree. Never share a writable worktree between independent task owners.

## Delegate inside the current task

Use internal subagents for bounded current-turn retrieval, comparison, or implementation slices that do not need separate acceptance or recovery. The parent task remains accountable for the combined result and gives each writing subagent non-overlapping paths. A subagent inherits the current cwd, branch, and worktree; it must not create or select another worktree. If the parent lacks write authority for that path, or the work becomes independently acceptable or cross-turn, stop and promote the remaining boundary to an independent task.

## Freeze and adjudicate review scope

Before the first review, freeze criterion IDs, the bounded threat model, and non-goals from the user's request and authoritative repository material. Keep that baseline unchanged across correction reviews unless the user or an authorized parent decision explicitly reopens it.

Require each blocking finding to identify the violated criterion and reproducible evidence. The controller, not the reviewer, decides whether it is an `accepted_blocker`, `non_blocking_observation`, or `scope_reopen_request`. Severity alone never grants scope or correction authority. Do not send non-blocking hardening to a writer.

On correction review, check the accepted blockers and regressions against the same baseline. New observations may be reported, but only mapped baseline violations can fail it. If two consecutive reviews each introduce a new accepted blocker, stop automatic correction, compare the work with the last minimal candidate, and run a scope-drift audit. Revert unnecessary hardening, defer it, or request explicit authority; do not silently start a third correction cycle.

## Create once and continue once

1. Preflight the saved repository project and task API.
2. Create the task against that project with the explicit target object `target: {type: "project", projectId, environment: {type: "local"}}`; do not rely on the Git-project default, and reject `projectless` or App-managed substitute trees. If using a fork, require `environment: {type: "same-directory"}` and reject `worktree`.
3. Include the dispatch packet and conditional execution authority in the initial instruction.
4. The task performs the fast route gate first. A passing task continues implementation or review in the same turn; a failing task writes nothing and reports `blocked`.
5. Do not require a binding-only turn, a controller receipt decision, and a second authorization message for a route that can be decided deterministically.

Use the repository write model through real creation parameters. Omit a model override only when review policy deliberately says `app_default`. Treat the submitted model as unverified unless the product echoes the effective runtime model.

## Receive reports and yield

Only direct task-message delivery is an ordinary report. Require `TARGET_SETTINGS: preserve`: the worker must omit `model` and `thinking` because task-message overrides apply to the destination controller. `progress` keeps the current task turn; record the new fact but do not send a continuation to an already-running task. `blocked` and `final` return control to the controller. A child local final may be read once for recovery, but is not normal delivery.

Record the controller model and reasoning effort before dispatch. On a report-triggered wake, compare the current turn settings with that baseline. If they changed without an explicit user selection, stop routing and report controller-model drift before accepting or integrating evidence.

After successful creation or continuation, end the controller turn. Resume only on:

- a delivered task report;
- a real one-shot checkpoint;
- a blocker or input request;
- a user status request;
- an acceptance or integration decision.

Do not call recursive waits, emit unchanged status, or use an immediate snapshot as a fake future checkpoint. If the product has no one-shot wakeup, silent-task recovery is available only on the next real controller wake; state that limitation once instead of adding per-task ceremony.

## Accept and close

Verify the actual diff or reviewed commit, owned paths, required tests, evidence limits, adjudicated findings, and root-baseline drift. The baseline passes when it has no accepted blocker; non-blocking observations do not prevent PASS. Integrate only within authority and in dependency order. Keep external gates separate.

Archive a task after acceptance is verified and no correction or in-flight operation remains. Call `set_thread_archived({threadId: <accepted-task-id>, archived: true})` and confirm success before declaring closure. A child `final` does not archive itself. Do not archive a task that still needs correction, input, or recovery. Remove a worktree separately, only when clean and without recovery value.
