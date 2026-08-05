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
3. Create two repository-local Git worktrees and two visible write tasks. Bind `WRITE_TASK_MODEL` through real task parameters.
4. Verify both binding receipts before granting write authority. Each command must use its exact execution-worktree cwd.
5. Freeze one candidate and create a visible read-only review task against that exact worktree and commit.
6. Require every turn-ending report to use `REPORT_DELIVERY: task_message:<controller-thread-id>`, `TURN_STATE: ending`, and `owner=controller`. Confirm the task-message call succeeds before the child emits its local final.
7. Have the controller verify the real diff, staged paths, tests, findings, and evidence limits before integration.
8. Create one read-only route-check task with `projectless` or an escaping execution path. Confirm rejection and that no write authority is sent.

## Evidence to retain

- Task IDs and submitted model policies; record the effective model as unverified unless the product echoes it.
- Repository root, worktree paths, branches, base/full candidate SHAs, and clean-state checks.
- Binding validator output for both accepted and rejected receipts.
- Direct task-message delivery result, validated `TURN_STATE`/owner handoff, test commands/results, reviewer findings, and controller acceptance.
- A statement that local evidence does not authorize push, deployment, production access, credentials, or permissions.

This repository does not claim that this UI runbook is automated. Run `python scripts/run_local_demo.py` for the deterministic local Git/contract portion.
