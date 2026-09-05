# Continuity and fresh-context handoff

Use a repository continuity package only when repository policy opts in. A repository may call it an execution package, task package, ADR bundle, topic folder, or another stable name. Keep its paths, tiers, templates, scaffolding, archive rules, and promotion destinations in that repository.

## Keep three coordinates separate

- The conversation or agent owns the current work context; App tasks additionally have their own user-visible lifecycle.
- The Git worktree owns the writable filesystem, branch, and commit candidate.
- The continuity package owns durable repository facts and recovery coordinates.

None substitutes for another. A package is not an authorization token, workflow engine, task-message channel, agent roster, heartbeat, checkpoint schedule, or formal review verdict.

## Rotate at a semantic checkpoint

A fresh-context handoff separates current facts from accumulated conversation history. It adds no design layer or worktree. First establish a recoverable boundary: commit coherent owned output, identify unfinished work, and resolve ownership. Do not transfer during an edit, test, external action, or ambiguous/mixed write state.

At that boundary, consider handoff when either a substantially independent phase remains or repeated rediscovery, repeated correction, or revived obsolete decisions show drift. Repeated failure on the same slice is a valid reason; a new topic and proven drift are not both required. Total tokens and compaction count alone do not establish drift, and a large task alone is not a checkpoint schedule.

Write one concise capsule, linking evidence instead of copying history or logs:

```text
FRESH_CONTEXT_HANDOFF
OBJECTIVE: <one current outcome>
ACCEPTED_BASELINE: <accepted scope, criteria, or design checkpoint>
RECOVERY_COORDINATES: repo=<path>; execution_path=<path>; branch=<branch>; head=<sha>
COMPLETED_AND_EVIDENCE: <verified results and their locations>
VALID_DECISIONS: <decisions still in force>
INVALIDATED_ROUTES: <approaches the successor must not revive and why>
NEXT_ACTION: <first concrete action>
NON_GOALS_AND_AUTHORITY: <scope and action gates>
UNRESOLVED: <facts or blockers still open>
WORKTREE_STATE: <clean, or exact dirty/untracked owned paths>
```

If continuity is enabled, update its sole rolling handoff and commit any continuity-only change without reopening accepted review. Otherwise carry the capsule in the launch or final message; create no package. This capsule is plain continuity data, not a new packet kind or validator schema.

For a fresh contribution within the current request, use an authorized internal agent with only the capsule and necessary raw evidence. The current owner remains accountable for acceptance; this is not a transfer of the user-owned App task. Prefer an independent reconstruction of the next step over copying the predecessor's entire reasoning.

For full owner replacement, use a host-supported fresh task only with explicit user authority. Under the App repository-local profile, launch once in the same saved project with `local`, identifying the existing execution tree and transfer boundary. A confirmed task id and unambiguous ownership transfer let the predecessor stop; the successor verifies repository, path, branch, HEAD, and state before writing. Read the capsule and necessary current sources, not the full predecessor conversation.

If full owner replacement was requested but is unconfirmed, the current owner remains responsible. Emit `HANDOFF_READY` with the capsule and explain the missing capability or authorization. Ordinary fresh internal contributions do not need this marker. Use one if it preserves the requested independence, but do not pretend it replaced the persistent owner. Continue unaffected bounded work when possible. An ambiguous creation requires reconciliation before retry; a denied action must not be bypassed.

## Route and maintain

1. Check the repository's active index or declared entry before creating anything.
2. Reuse a matching active package when its product boundary still applies. Create a new one only when repository policy requires durable state and the existing boundary does not fit.
3. Record only the durable minimum: objective, scope and non-goals, current state, acceptance, recovery coordinates, unresolved limits, and next product step.
4. Update the package and any repository index only when scope, state, acceptance, recovery coordinates, archival, or promotion materially changes.
5. Keep reports in the selected result channel and reproducible evidence in its natural repository or artifact location. Link rather than duplicate.
6. At closure, promote stable facts to the repository's declared long-lived source, record remaining limits, and archive or retain the package according to repository policy.

## Close a passed candidate without reopening it

Classify every proposed post-PASS diff before writing it:

- `continuity_only` records an existing verdict, reviewed checkpoint, current state, next action, recovery coordinate, or archive pointer. It changes no implementation, normative design or contract, acceptance criterion, non-goal, finding, or verdict-bearing evidence.
- `normative` changes one of those reviewed surfaces or introduces a new requirement, claim, finding, or evidence conclusion.

For `continuity_only` closeout:

1. Use the repository-declared rolling handoff or equivalent as the sole detailed hot-state surface. Update active or package indexes only with the minimal route, state token, or pointer required by repository policy; do not mirror detailed status across design, plan, task-matrix, acceptance, and evidence documents.
2. Record the reviewed checkpoint separately from the later continuity checkpoint. A bookkeeping commit that moves HEAD does not invalidate the prior PASS for the reviewed checkpoint.
3. Let the owner of those paths verify the exact allowed fields, then commit the closeout. Do not dispatch a reviewer, invent new acceptance criteria, or review merely to prove that a document says the review passed.
4. If the diff is actually `normative`, stop before writing and route it through the applicable design, acceptance, or implementation reopen path.

A `continuity_only` closeout does not reopen review. Re-review only when implementation, normative design or contracts, acceptance, non-goals, findings, or verdict-bearing evidence changes.

Do not create a package for short work merely to satisfy orchestration. Do not let a historical package reactivate obsolete contracts, gates, roles, or commands.
