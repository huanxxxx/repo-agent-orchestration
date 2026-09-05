# Delivery controller

Own the outcome, dependencies, acceptance, integration, and result delivery. In `architected`, preserve the design authority's baseline and return decision-relevant evidence to it. Otherwise the current owner can make ordinary design and implementation decisions within the user's scope.

## Plan only enough to act

Keep the objective, acceptance, non-goals, next useful step, ready work, dependencies, and write ownership clear. Ask what existing mechanism already solves the problem and which smallest useful slice can demonstrate the intended result.

Choose responsibilities before tools. A bounded writer, independent reviewer, or investigator may be an internal agent. A separate App lifecycle requires explicit user task-creation authority and host support. Use only necessary fresh-context inputs for independent judgment; do not supply the expected verdict. Shared filesystem access still requires exclusive paths and one integration owner.

Delegate all ready, separable contributions within capacity when it saves time or improves quality. Do not wait for a second instruction to parallelize already-authorized delegation. Serialize for an actual dependency, overlapping writes, acceptance coupling, or resource constraint. Sending the first assignment does not cancel the rest of the ready set.

The task capsule needs objective, relevant inputs, scope, acceptance/checks, and report destination. `OWNED_PATHS` limits where work can happen; it is not permission for arbitrary changes there. Prefer narrow call-chain evidence over whole-repository reading. No packet construction, project-id lookup, or worktree creation is required merely because a subagent is used.

## Filesystem and model choices

Verify the actual Git root, branch/HEAD, status baseline, and owned paths before writing. Internal contributions use the owner's execution tree with disjoint scopes; do not create a tree per helper. Separately running App writers use separate registered repository-local branches/worktrees under the repository profile. Check their exact current base rather than trusting remembered paths or deleted branches.

Read-only review can use a stable root or frozen candidate. Pause writes to the candidate while it is reviewed; use a detached snapshot when a stable historical/test-running filesystem is needed. A reviewer does not need an extra writable branch merely to be independent.

For `app_default`, omit model and reasoning overrides. Honor an explicit supported binding through the host's actual parameters; do not guess availability from the owner's model. Messages reporting results omit destination model/thinking overrides. If actual metadata differs, report the fact without attributing causality from unrelated task rows.

For an authorized App task use [contracts.md](contracts.md). That adapter's saved-project/local policy applies to App routing, not to ordinary current-task work or internal agents. A profile is not permission to call an unavailable or restricted API.

## Continue according to dependencies

On a new result, decision, or user request, refresh the facts it changes and act on newly ready work. Reuse stable routing and acceptance evidence. Do not repeatedly load every reference, packet script, executor Skill, or package document just to send an already-defined assignment.

Dispatch other ready contributions, do useful local work, and collect relevant completed results. An informational report does not pause authorized work. A blocking dependency pauses only affected/dependent actions; independent authorized work may continue.

When a result is genuinely needed, use the matching host wait/result tool with a bounded wait. Internal-agent ids belong to collaboration APIs; App ids belong to App APIs. After a meaningful result, proceed with acceptance or the next stage. For an App task with a supported future wake, yield once nothing useful remains. Silence is not a reason for repeated list/read/status calls. See [recovery.md](recovery.md) if results cannot reach the owner.

Do not send duplicate assignments or a plain continuation to already active work. If new evidence requires correction, use the host-supported steering mechanism and existing task identity. Historical `inProgress` rows do not prove a live turn; use current runtime facts when a lifecycle decision actually needs them.

## Accept and report

Use an independent reviewer when required by the user/repository or justified by correctness risk. Delta review gets relevant contracts, raw diff/evidence, non-goals, required checks, and a reason to expand if needed. Reuse the reviewer for ordinary correction; choose fresh context when judgment has become anchored or a genuinely independent second opinion is needed. No fixed number of review rounds substitutes for judging the blocker.

Verify actual changes and required checks. Stop expansion when acceptance passes. Distinguish targeted, full-repository, protected-environment, and production evidence. If repeated corrections change the target or repeat stale assumptions, re-establish the current acceptance and use [continuity.md](continuity.md) at a safe boundary, even on the same slice.

Before a planned pause, handoff, formal review, or final, locally commit coherent owned output. Internal agents return changed paths/checks; the owner verifies and commits the combined unit. Preserve mixed/untracked work and describe any unresolved ownership precisely.

Reports carry progress that changes a decision, a genuine blocker, or final evidence. Include the checkpoint, acceptance evidence, limits, and required next action. Use internal result delivery for internal agents; use the selected authorized App channel for App tasks. A failed message is not delivered, but it does not erase the completed result or stop unrelated work.

In `architected`, send the initial plan, material milestones, design questions, and final evidence to design. A `DECISION_REQUIRED: no` report permits continued work inside the frozen baseline. A design conflict needs a bounded reopen decision and pauses only affected scope. Final implementation evidence still needs design-consistency acceptance by the design authority.

## Close once

Record accepted status in the repository's sole rolling handoff when opted in. A continuity-only commit does not invalidate the reviewed checkpoint; do not create another review just to record PASS. Normative changes require the applicable acceptance/design decision.

Archive an accepted App task only when no correction or live operation remains, and confirm the archive result. Then make a worktree/branch cleanup decision using [recovery.md](recovery.md). Internal results need no App archival. If removal is unsafe or unauthorized, record exact retained coordinates, reason, and next action rather than losing track of the residue.
