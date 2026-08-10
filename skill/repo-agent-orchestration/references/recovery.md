# Recovery and mode changes

## Recovery anchors

1. Treat the current HEAD of a clean task worktree as its recovery anchor; do not create an empty or ceremonial snapshot.
2. Create a prechange snapshot only when the user explicitly requests one, or when an authorized task must preserve task-owned tracked changes before a risky rewrite.
3. Confirm the exact owned paths first. Stop when candidate changes include ambiguous, user-owned, or another task's files.
4. Keep snapshot commit, push, main integration, deployment, and publication as separate authorization boundaries. Use a repository utility when one exists; this Skill does not prescribe a repository-specific script.
5. Distinguish a prechange snapshot from a checkpoint commit: the former preserves prior dirty input before risky rewriting; the latter records real task output before a pause, handoff, review, or final.

## Silent task

1. Start only on a real wake: a one-shot checkpoint, task signal, user request, or another controller decision.
2. Inspect the task once and distinguish an active turn from a completed or idle turn.
3. If it is active, do not interrupt or send a duplicate continuation. Stop after the one check.
4. If it completed without a delivered task message, read its latest final once and treat it as recovery evidence.
5. A completed turn returns control to the controller. Continue the task only when the recovered state actually requires another stage.
6. If no new fact appears, stop querying and preserve the task and worktree evidence.
7. Do not create recurring heartbeats or immediate snapshots to imitate a future missing-report check. If a true one-shot wakeup is unavailable, say that proactive silent-task detection cannot be guaranteed.

## Controller takeover

1. Read the previous controller’s latest completed turns without messaging it unless authorized.
2. Rebuild the mainline anchor from repository and task evidence.
3. Enumerate active user-visible tasks, internal subagents, worktrees, branches, heads, and dirty paths.
4. Separate submitted instructions from confirmed runtime effects.
5. Preserve external and production gates.
6. Notify active tasks only after the takeover authority and new routing are explicit.

## Switching from internal writers to visible tasks

1. Stop assigning new work to internal subagents at the next safe boundary.
2. Do not discard, restore, overwrite, stage, or commit their in-flight output merely to make routing clean.
3. Record each helper's parent task, inherited execution path, owned paths, dirty state, commit state, and remaining work.
4. Freeze the current candidate and identify one safe owner for each write boundary.
5. Create one repository-local worktree for each separable future independent task. Do not create one per helper. If existing dirty changes cannot be separated safely, report the conflict instead of forcing a split.
6. Re-dispatch unfinished implementation and formal review as user-visible tasks with explicit model binding.
7. Keep the product mainline unchanged unless the user separately changes it.

## Dirty or ambiguous worktree

Stop before overwriting. Identify the exact paths, owner, base, branch, head, tracked changes, untracked files, and recovery value. Do not search sibling worktrees as substitute activity sources. Do not force-delete a tree with unknown or recoverable work.

## Unexpected platform-managed worktree

Treat any worktree created outside the declared repository-local root as an orphan candidate. Do not use it as an activity source or continue writing. Identify its task or session, resolved path, branch, head, base, dirty state, untracked files, and recovery value. Remove it only through the Git worktree flow after its session is cancelled or archived, it is clean, and it has no recovery value. Never force-delete it merely because its path is wrong.

## Foreign-cwd or projectless task

1. Revoke further write authority and send a stop instruction once; do not rely on the task to reinterpret its prompt.
2. Record the task id, actual cwd, project id, intended worktree, last successful write, dirty paths, in-flight commands, and recovery value.
3. Never let a user-global or projectless task continue by addressing a repository through absolute paths.
4. A repository-root cwd is valid only as a verified `repository_project_local` host. Confirm the non-null repository project id, recorded root baseline, and exact execution path before continuing.
5. Detect duplicate task ids before restoring any owner. Multiple sessions that touched one writable worktree make every overlapping path mixed ownership until proven otherwise.
6. Preserve dirty evidence and stop. Do not reset, overwrite, combine, stage, commit, or remove the task directory merely to restore routing cleanliness.
7. Re-dispatch only after the fast route gate can pass. If unavailable, keep the implementation blocked.

## Completion and cleanup

Mark a user-visible task `PASS_VERIFIED` only after final evidence and controller verification show that acceptance is complete and no blocker, reply, correction, or in-flight operation remains. Archive it immediately after that gate; do not leave it merely labelled “ready to archive.” Keep blocked or correctable tasks active.

Receive an internal subagent's final result, confirm it stopped, and release its slot promptly.

Treat task archival and worktree removal as separate actions. Before removing a worktree, resolve and inspect its exact path, branch, head, and dirty state. Remove it only when it is clean, integrated or explicitly abandoned, evidence and recovery coordinates are saved, and it has no recovery value. Remove an integrated local branch only after the worktree is safely unregistered. Never force-delete unknown or recoverable changes.
