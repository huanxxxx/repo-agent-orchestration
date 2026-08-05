# Recovery and mode changes

## Silent task

1. Confirm that the expected milestone and checkpoint are still valid.
2. Query the target once with a clear purpose.
3. If no new fact appears, stop querying and preserve task ownership.
4. Do not create recurring heartbeats to imitate a one-time check.
5. If a true one-shot wakeup is unavailable, report that proactive checking cannot be guaranteed.

## Controller takeover

1. Read the previous controller’s latest completed turns without messaging it unless authorized.
2. Rebuild the mainline anchor from repository and task evidence.
3. Enumerate active user-visible tasks, internal helpers, worktrees, branches, heads, and dirty paths.
4. Separate submitted instructions from confirmed runtime effects.
5. Preserve external and production gates.
6. Notify active tasks only after the takeover authority and new routing are explicit.

## Switching from internal writers to visible tasks

1. Stop assigning new work to internal helpers at the next safe boundary.
2. Do not discard, restore, overwrite, stage, or commit their in-flight output merely to make routing clean.
3. Record each helper’s task, paths, worktree, dirty state, commit state, and remaining work.
4. Freeze the current candidate and identify one safe owner for each write boundary.
5. Create repository-local worktrees for separable future work. If existing dirty changes cannot be separated safely, report the conflict instead of forcing a split.
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
4. A repository-root cwd is valid only as a verified `repository_project_local` host. Confirm the non-null repository project id, clean root, exact registered execution worktree, and exact-workdir policy before continuing.
5. Detect duplicate task ids before restoring any owner. Multiple sessions that touched one writable worktree make every overlapping path mixed ownership until proven otherwise.
6. Preserve dirty evidence and stop. Do not reset, overwrite, combine, stage, commit, or remove the task directory merely to restore routing cleanliness.
7. Re-dispatch only after a repository-host/execution-worktree or direct-existing-cwd receipt passes. If unavailable, keep the implementation blocked.

## Completion and cleanup

Mark a user-visible task `PASS_VERIFIED` only after final evidence and controller verification show that acceptance is complete and no blocker, reply, correction, or in-flight operation remains. Archive it immediately after that gate; do not leave it merely labelled “ready to archive.” Keep blocked or correctable tasks active.

Receive an internal helper's final result, confirm it stopped, and release its slot promptly.

Treat task archival and worktree removal as separate actions. Before removing a worktree, resolve and inspect its exact path, branch, head, and dirty state. Remove it only when it is clean, integrated or explicitly abandoned, evidence and recovery coordinates are saved, and it has no recovery value. Remove an integrated local branch only after the worktree is safely unregistered. Never force-delete unknown or recoverable changes.
