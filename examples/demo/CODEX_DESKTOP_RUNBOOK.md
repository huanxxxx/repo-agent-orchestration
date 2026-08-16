# Codex Desktop end-to-end runbook

Use this runbook only on a disposable demonstration repository. It exercises the full product-facing workflow that the local demo cannot automate.

## Preconditions

- Open the repository as a saved local project in Codex Desktop on Windows.
- Install the Skill with `python scripts/install_repository.py --repo <absolute-repository-root>`.
- Confirm the surface can create user-visible tasks, submit explicit model parameters, deliver task messages, and read the task project/cwd receipt.
- Keep merge, push, deployment, credentials, permissions, and production data out of scope.

## Scenario

1. Ask the controller to split independent backend and frontend changes with a shared test acceptance gate.
2. Record the readiness audit and why each candidate is safe to dispatch concurrently.
3. Create two repository-local Git worktrees and two visible write tasks using App `create_thread`. Create each visible task in the saved project with explicit App environment `local`; never select or default to App `worktree`, and never substitute `spawn_agent`. Omit model overrides for `WRITE_TASK_MODEL: app_default`; submit an explicit model through real task parameters only after the destination host advertises it.
4. Create each task with an inert route fingerprint and no execution authority. After the creation receipt, use `send_message_to_thread` once to deliver one validated packet containing its actual task id; the task runs the fast route gate and continues on PASS. Each command must use its exact execution path.
5. Freeze one candidate and create a visible delta read-only review task against its exact SHA range, with explicit context/check/expansion budget. Use `full` only with a recorded reason. Also exercise either a short `root_readonly` review or an on-demand `detached_snapshot` review.
6. Require blocked and final reports to use `DELIVERY: task_message:<target-task-id>` and `TARGET_SETTINGS: preserve`. Confirm the task-message call omits `model` and `thinking` and succeeds before the peer emits its local final.
7. Have the delivery controller verify the real diff, staged paths, tests, findings, and evidence limits before integration. After acceptance and with no correction or in-flight operation, require the dispatching authority to archive the peer task and record the successful archive receipt.
8. Create one read-only route-check task with `projectless` or an escaping execution path. Confirm rejection and that no write authority is sent.

## Evidence to retain

- Task IDs, submitted `environment: local`, and submitted model policies; record the effective model as unverified unless the product echoes it.
- Repository root, worktree paths, branches, base/full candidate SHAs, and clean-state checks.
- Route validator output for accepted and rejected starts, including proof that the id-bound packet was delivered and a passing task continued without a startup wait.
- Direct task-message delivery result, proof that controller-bound reports omitted model/thinking overrides, test commands/results, reviewer findings, controller acceptance, and successful post-acceptance archival.
- A statement that local evidence does not authorize push, deployment, production access, credentials, or permissions.

This repository does not claim that this UI runbook is automated. Run `python scripts/run_local_demo.py` for the deterministic local Git/contract portion.
