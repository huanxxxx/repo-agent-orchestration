# Recovery and mode changes

## Recovery anchors

1. Treat the current HEAD of a clean task worktree as its recovery anchor; do not create an empty or ceremonial snapshot.
2. Create a prechange snapshot only when the user explicitly requests one, or when an authorized task must preserve task-owned tracked changes before a risky rewrite.
3. Confirm the exact owned paths first. Stop when candidate changes include ambiguous, user-owned, or another task's files.
4. Keep snapshot commit, push, main integration, deployment, and publication as separate authorization boundaries. Use a repository utility when one exists; this Skill does not prescribe a repository-specific script.
5. Distinguish a prechange snapshot from a checkpoint commit: the former preserves prior dirty input before risky rewriting; the latter records real task output before a pause, handoff, review, or final.

## Missing result or uncertain delivery

When a real dependency needs its result, use the host's supported result/wait mechanism. A task event, user request, or acceptance decision may justify inspecting current runtime state. Historical `inProgress` rows are not proof of stoppable work. Do not interrupt active work or resend its assignment merely because it is quiet.

If work completed without a message, retrieve its final through an authorized read/result tool and verify relevant evidence. State that the owner recovered the result rather than claiming the original send succeeded. A permission denial requires a permitted alternative or user action, never rewritten envelopes or repeated sends intended to bypass the denial.

An ambiguous creation/message receipt means the outcome is unknown, not definitely failed. Reconcile the existing task/delivery before retrying; do not create duplicates. Continue unrelated authorized work. If no supported future wake exists, explain how the pending result will be collected instead of claiming event-driven resumption is guaranteed. Do not add recurring monitoring unless the user asks for it, or repeatedly snapshot unchanged status.

## Packet error versus execution blocker

A local formatting error is repairable from known facts; it is not a global `PROTOCOL_BLOCKED` state. Correct the reported errors without changing the objective, authority, destination, or verdict. If errors recur, inspect the relevant schema/example rather than resending unchanged input or inventing missing facts. Preserve readable evidence if the helper cannot express it.

For malformed incoming reports, recover unambiguous facts and ask the sender only for missing material information. Do not execute an ambiguous instruction or accept a claimed PASS without evidence. Uncertain identity, conflicting ownership, insufficient authority, and unresolved acceptance are real blockers for the affected action; unrelated work can continue.

## Controller takeover

1. Read the previous controller’s latest completed turns without messaging it unless authorized.
2. Rebuild the mainline anchor from repository and task evidence.
3. Enumerate active user-visible peer tasks, internal subagents, worktrees, branches, heads, and dirty paths.
4. Separate submitted instructions from confirmed runtime effects.
5. Preserve external and production gates.
6. Notify active tasks only after the takeover authority and new routing are explicit.

## Switching from internal writers to visible tasks

1. Stop assigning new work to internal subagents at the next safe boundary.
2. Do not discard, restore, overwrite, stage, or commit their in-flight output merely to make routing clean.
3. Record each helper's parent task, inherited execution path, owned paths, dirty state, commit state, and remaining work.
4. Freeze the current candidate and identify one safe owner for each write boundary.
5. Create one repository-local worktree for each separable future peer task. Do not create one per helper. If existing dirty changes cannot be separated safely, report the conflict instead of forcing a split.
6. Re-dispatch only when the user authorized the separate App tasks and the host supports them; preserve supported explicit model choices, otherwise use host defaults.
7. Keep the product mainline unchanged unless the user separately changes it.

## Dirty or ambiguous worktree

Stop before overwriting. Identify the exact paths, owner, base, branch, head, tracked changes, untracked files, and recovery value. Do not search sibling worktrees as substitute activity sources. Do not force-delete a tree with unknown or recoverable work.

## Unexpected platform-managed worktree

If a route required a repository-local worktree but creation produced a different tree, pause writes on that route and identify its task, resolved path, branch, head, base, and dirty/untracked state. A queued setup is not a started writer; follow the actual host receipt without creating a replacement blindly. Preserve any recovery value and obtain a valid authorized route. Never delete a tree merely because its path is unexpected.

## Wrong repository or execution identity

Pause affected writes and identify the actual Git root, execution path, branch, HEAD, owner, in-flight operations, and dirty/untracked changes. Re-establish the authorized boundary before continuing. Multiple owners touching the same path create an ownership conflict until reconciled; do not reset or stage mixed work to make the route appear clean.

The optional `repository_project_local` App adapter also verifies its saved project id and local hosting. Those checks protect that chosen route. A current-task or internal-agent workflow does not acquire or lose repository write authority merely because an App project id is absent; use explicit user scope, host permissions, actual Git identity, and ownership. Never evade a route restriction by changing directories or relabelling an App peer as an internal agent.

## Completion and cleanup

Mark a user-visible peer task `PASS_VERIFIED` only after final evidence and verification by its dispatching authority show that acceptance is complete and no blocker, reply, correction, or in-flight operation remains. Archive it immediately after that gate; do not leave it merely labelled “ready to archive.” Keep blocked or correctable peers active.

Receive an internal subagent's final result, confirm it stopped, and release its slot promptly.

Treat task archival and worktree removal as separate actions, but do not leave the removal decision for future archaeology. After a peer is accepted/archived, make one explicit closeout classification for every peer-owned worktree and branch:

- `REMOVED_WORKTREE`: exact path was registered, resolved, clean, integrated or explicitly abandoned, recovery coordinates were saved, and no recovery value remains.
- `REMOVED_BRANCH`: the corresponding local branch was removed after the worktree was unregistered and Git proved it safe to delete.
- `RETAINED_WORKTREE`: deletion was unsafe, not authorized, or not yet valuable enough.

Before removing, resolve and inspect exact path, branch, head, dirty/untracked state, integration target, and recovery value. Prefer proof that the branch head is ancestor or patch-equivalent to the integration target; use repository-specific evidence when a branch was intentionally abandoned. Remove the registered Git worktree before deleting the local branch. Never delete a remote branch, force-delete unknown/dirty/recoverable work, or use archive status, directory age, or path name as cleanup proof.

A retained item must include `TASK_ID`, `WORKTREE`, `BRANCH`, `HEAD`, `REASON`, and `NEXT_ACTION`. Keep the reason concrete: dirty, untracked, not integrated, unknown owner, blocked, user-retained, missing external gate, or recoverable evidence.
