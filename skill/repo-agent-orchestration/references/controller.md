# Controller workflow

## Keep four mainline facts

Keep the product objective, current gate, active tasks, and next product step. Add an authorization ceiling only when external or destructive actions are in scope. Do not maintain a second project-management system for agent mechanics.

## Decide readiness

Before dispatch, answer four questions:

1. Is the work authorized?
2. Are its inputs and dependencies ready?
3. Does it have an exclusive write boundary, or is it read-only?
4. Can it be accepted independently?

Dispatch every ready, non-conflicting task when capacity permits. When serializing, record the one concrete dependency, shared write, acceptance coupling, or external gate. Re-run this decision when a task reports or another real event wakes the controller; do not stay online merely to rescan.

## Prepare the route

For a writer, create one repository-local worktree and branch only when ready. Verify its base, branch, registry entry, and status. Record the root status as a baseline rather than demanding an unrelated user-owned root be clean.

For a review, select the lightest target:

- stable short committed review: `root_readonly`;
- frozen candidate: `existing_worktree`;
- long, cross-turn, test-running, or historical review: create `detached_snapshot` on demand below `WORKTREE_ROOT`.

The reviewer does not create a tree. Never share a writable worktree between owners.

## Create once and continue once

1. Preflight the saved repository project and task API.
2. Create the task against that project with environment `local`; reject `projectless` and App-managed substitute trees.
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

Verify the actual diff or reviewed commit, owned paths, required tests, evidence limits, unresolved findings, and root-baseline drift. Integrate only within authority and in dependency order. Keep external gates separate.

Archive a task after acceptance is verified and no correction or in-flight operation remains. Remove a worktree separately, only when clean and without recovery value.
