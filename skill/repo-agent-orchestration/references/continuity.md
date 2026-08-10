# Repository continuity packages

Use a repository continuity package only when repository policy opts in. A repository may call it an execution package, task package, ADR bundle, topic folder, or another stable name. Keep its paths, tiers, templates, scaffolding, archive rules, and promotion destinations in that repository.

## Keep three coordinates separate

- The App task owns activity, model routing, messages, and archival.
- The Git worktree owns the writable filesystem, branch, and commit candidate.
- The continuity package owns durable repository facts and recovery coordinates.

None substitutes for another. A package is not an authorization token, workflow engine, task-message channel, agent roster, heartbeat, checkpoint schedule, or formal review verdict.

## Route and maintain

1. Check the repository's active index or declared entry before creating anything.
2. Reuse a matching active package when its product boundary still applies. Create a new one only when repository policy requires durable state and the existing boundary does not fit.
3. Record only the durable minimum: objective, scope and non-goals, current state, acceptance, recovery coordinates, unresolved limits, and next product step.
4. Update the package and any repository index only when scope, state, acceptance, recovery coordinates, archival, or promotion materially changes.
5. Keep detailed task reports in App task messages and reproducible evidence in its natural repository or artifact location. Link rather than duplicate.
6. At closure, promote stable facts to the repository's declared long-lived source, record remaining limits, and archive or retain the package according to repository policy.

Do not create a package for short work merely to satisfy orchestration. Do not let a historical package reactivate obsolete contracts, gates, roles, or commands.
