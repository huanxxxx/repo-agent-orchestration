# Continuity and fresh-context handoff

Use a repository continuity package only when repository policy opts in. A repository may call it an execution package, task package, ADR bundle, topic folder, or another stable name. Keep its paths, tiers, templates, scaffolding, archive rules, and promotion destinations in that repository.

## Keep three coordinates separate

- The App task owns activity, model routing, messages, and archival.
- The Git worktree owns the writable filesystem, branch, and commit candidate.
- The continuity package owns durable repository facts and recovery coordinates.

None substitutes for another. A package is not an authorization token, workflow engine, task-message channel, agent roster, heartbeat, checkpoint schedule, or formal review verdict.

## Rotate at a semantic checkpoint

A fresh-context rotation replaces the active owner; it adds no authority layer, parallel lane, or worktree. The successor is still an App runtime peer, but owns the accepted objective instead of reporting to the predecessor.

Rotate only after a coherent slice is committed, different work remains, and context shows drift: repeated rediscovery, conflict with a frozen decision, repeated correction, or substantial compaction. A cumulative token number alone never triggers rotation. Do not rotate during an edit, test, external action, mixed ownership, or ambiguous repository/worktree state.

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

With explicit task-creation authority, launch once in the same project with `local`. A confirmed `threadId` transfers ownership: the predecessor ends without waiting, while the successor verifies repository, path, branch, HEAD, and state, then reads only the capsule and cited current surfaces, not the full predecessor conversation.

Without a confirmed id, no transfer occurred. Emit `HANDOFF_READY` plus the capsule once; do not retry, poll, invent a peer id, or use an internal subagent as a persistent replacement. This optional transport failure is not `PROTOCOL_BLOCKED`; the current task remains owner and may take one bounded next slice when uninterrupted progress was requested. A phantom task must fail its normal route gate before writing.

## Route and maintain

1. Check the repository's active index or declared entry before creating anything.
2. Reuse a matching active package when its product boundary still applies. Create a new one only when repository policy requires durable state and the existing boundary does not fit.
3. Record only the durable minimum: objective, scope and non-goals, current state, acceptance, recovery coordinates, unresolved limits, and next product step.
4. Update the package and any repository index only when scope, state, acceptance, recovery coordinates, archival, or promotion materially changes.
5. Keep detailed task reports in App task messages and reproducible evidence in its natural repository or artifact location. Link rather than duplicate.
6. At closure, promote stable facts to the repository's declared long-lived source, record remaining limits, and archive or retain the package according to repository policy.

## Close a passed candidate without reopening it

Classify every proposed post-PASS diff before writing it:

- `continuity_only` records an existing verdict, reviewed checkpoint, current state, next action, recovery coordinate, or archive pointer. It changes no implementation, normative design or contract, acceptance criterion, non-goal, finding, or verdict-bearing evidence.
- `normative` changes one of those reviewed surfaces or introduces a new requirement, claim, finding, or evidence conclusion.

For `continuity_only` closeout:

1. Use the repository-declared rolling handoff or equivalent as the sole detailed hot-state surface. Update active or package indexes only with the minimal route, state token, or pointer required by repository policy; do not mirror detailed status across design, plan, task-matrix, acceptance, and evidence documents.
2. Record the reviewed checkpoint separately from the later continuity checkpoint. A bookkeeping commit that moves HEAD does not invalidate the prior PASS for the reviewed checkpoint.
3. Let the authority holding the repository-root write lease verify the exact allowlisted paths and fields, then commit the closeout. Do not dispatch a peer reviewer, invent new acceptance criteria, or review merely to prove that a document says the review passed.
4. If the diff is actually `normative`, stop before writing and route it through the applicable design, acceptance, or implementation reopen path.

A `continuity_only` closeout does not reopen review. Re-review only when implementation, normative design or contracts, acceptance, non-goals, findings, or verdict-bearing evidence changes.

Do not create a package for short work merely to satisfy orchestration. Do not let a historical package reactivate obsolete contracts, gates, roles, or commands.
