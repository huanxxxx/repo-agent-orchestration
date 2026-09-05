# Codex Desktop end-to-end runbook

Use this optional App-adapter runbook only on a disposable demonstration repository, after the user explicitly requests its separate App tasks. It exercises a product-facing route that the local demo cannot automate; it is not the default route for internal collaboration.

## Preconditions

- Open the repository as a saved local project in Codex Desktop on Windows.
- Install the Skill with `python scripts/install_repository.py --repo <absolute-repository-root>`.
- Confirm the surface can create user-visible tasks, submit explicit model parameters, deliver task messages, and read the task project/cwd receipt.
- Keep merge, push, deployment, credentials, permissions, and production data out of scope.

## Scenario

1. Explicitly ask the controller to create two separate user-visible writer tasks and the review/audit tasks in this runbook, for independent backend and frontend changes with a shared acceptance gate. Authorize only the disposable repository's local writes, commits, and cleanup.
2. Record the readiness audit and why each candidate is safe to dispatch concurrently.
3. Create two repository-local Git worktrees and two visible write tasks using App `create_thread`. Create each visible task in the saved project with explicit App environment `local`; never select or default to App `worktree`, and never substitute `spawn_agent`. Omit model overrides for `WRITE_TASK_MODEL: app_default`; submit an explicit model through real task parameters only after the destination host advertises it.
4. Before creation, run the installed constructor with `--launch` and use its complete output unchanged as `create_thread.prompt`. Give each task a meaningful objective title. The task runs the fast route gate and continues on PASS in its initial turn; do not create `AWAIT_FORMAL_DISPATCH` or immediately resend the launch packet. Each command must use its exact execution path.
   Start both ready writers within capacity. Perform host-required checks and useful independent work, then collect results using the supported wait/event mechanism; do not end merely because the first assignment was sent or repeatedly snapshot unchanged status.
5. Freeze one candidate and create a visible delta read-only review task against its exact SHA range, with explicit context/check/expansion budget. Use `full` only with a recorded reason. Also exercise either a short `root_readonly` review or an on-demand `detached_snapshot` review.
6. Build reports with `--task-message-to <target-task-id>`, which injects intended `DELIVERY` and `TARGET_SETTINGS: preserve`. Confirm the call omits `model` and `thinking`; record actual success/denial/uncertainty separately. If denied, retain the final and use authorized owner-side result retrieval; do not resend to bypass the denial. An informational report must not halt independent ready work.
7. Have the delivery controller verify the real diff, staged paths, tests, findings, and evidence limits before integration. After acceptance and with no correction or in-flight operation, require the dispatching authority to archive the peer task and record the successful archive receipt.
8. In the authorized read-only route-check task, feed synthetic `projectless` and path-escape binding data to the validator. Confirm the optional App adapter rejects these routes without actually creating a misrouted writer. Ordinary current-task work is not subject to the App binding schema.
9. Send a correction delta to the original idle reviewer with `send_message_to_thread`. Confirm it receives the new exact range and closure checks without a new reviewer task or repeated binding.

## Evidence to retain

- Task IDs, submitted `environment: local`, and submitted model policies; record the effective model as unverified unless the product echoes it.
- Repository root, worktree paths, branches, base/full candidate SHAs, and clean-state checks.
- Route validator output for accepted and rejected starts, including proof that the complete launch packet was delivered in the creation call and a passing task continued without an inert turn.
- Direct task-message delivery result, proof that controller-bound reports omitted model/thinking overrides, test commands/results, reviewer findings, controller acceptance, and successful post-acceptance archival.
- A statement that local evidence does not authorize push, deployment, production access, credentials, or permissions.

This repository does not claim that this UI runbook is automated. Run `python scripts/run_local_demo.py` for the deterministic local Git/contract portion.
