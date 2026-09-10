---
name: repo-agent-orchestration
description: Coordinate repository work across useful context boundaries, with clear ownership, scoped review, reliable results, and recoverable handoff. Use for multi-part delivery or long-task continuity, not every small edit.
---

# Repository Agent Orchestration

Help finish the user's objective without overloading one conversation. Separate work when another context improves execution or judgment; keep coordination proportional to the work.

## Authority and initiative

The user's instructions take precedence over this Skill's workflow guidance. Host permissions and tool restrictions still apply. A role, packet, or repository profile grants no extra authority.

Within the authorized objective, choose reasonable, reversible implementation details and continue without routine confirmation. Ask when missing information materially changes scope, correctness, ownership, or risk. If this Skill causes a pause or changes the requested course, cite the exact instruction and explain the concrete conflict; distinguish a real boundary from a workflow preference.

Preserve exact repository/execution paths, exclusive write ownership, read-only review, other owners' changes, and destination model settings. Merge, push, publication, deployment, production data, credentials, permissions, and destructive cleanup require their own applicable authorization. A task's PASS does not grant it.

## Start with the outcome

Read repository `AGENTS.md` and only the references needed for the current decision:

- [controller.md](references/controller.md): delegation, dependencies, acceptance, and reporting.
- [architected.md](references/architected.md): a separate design authority is requested or justified by material cross-cutting risk.
- [contracts.md](references/contracts.md): structured packets for an explicitly authorized App-task route.
- [continuity.md](references/continuity.md): an actual handoff, recovery, or repository-defined continuity update.
- [recovery.md](references/recovery.md): ambiguous delivery, route/ownership trouble, or resource cleanup.

Establish the objective, acceptance, non-goals, current evidence, and next useful step. Verify repository and execution identity before writing. Reuse stable facts; refresh changed or ambiguous facts instead of repeatedly reading all instructions, history, or schemas. Repository task size alone does not require a continuity package.

## Choose responsibility and transport separately

Use `direct` when one context can finish the bounded outcome; `delivery` when an owner coordinates useful contributions; `architected` when a distinct design authority is explicitly requested, required by repository policy, or needed to resolve material architecture/data/product tradeoffs. Mentioning architecture or changing a version does not by itself require three layers. Repository tiers retain their repository-defined meaning.

Design, delivery, implementation, review, and audit are responsibilities, not mandatory App tasks. A reviewer must be independent of the implementation being judged and receive the acceptance baseline and raw evidence, not the author's preferred conclusion. Use a fresh context with only relevant inputs when independence or context pressure calls for it.

For subtasks of the current request, use available collaboration tools when delegation is authorized and can save time or improve quality. Delegate ready, separable work proactively within capacity; do not split coupled work merely to fill slots. Internal agents have their own contexts but share the owning task's authority and filesystem: give them explicit non-overlapping paths or read-only scope. Use the host's actual result, follow-up, and wait mechanisms; do not invent a one-turn lifetime.

Internal results return to the creating parent through native final/result delivery or parent-addressed collaboration messages. This relationship survives context recovery: role labels, historical package owners, and task titles do not select a new recipient. Do not search App tasks for a "controller" or use App messages for ordinary internal reports. If the parent's address is unavailable, return a normal final result instead of guessing an App destination or blocking on id lookup.

Use an App user-owned task only when the user explicitly requests a separate task and the host supports the intended route. Cross-App contact is a separate authorized action for the owning user task, not an internal reporting step. Keep App task ids and internal agent ids in their respective APIs. If an explicitly required capability is unavailable, preserve that requirement, explain the gap, and continue unaffected work; do not silently substitute a weaker form of independence.

## Delegate, act, and collect results

Send a small capsule: objective, necessary context/evidence, writable boundary or read-only scope, acceptance and required checks, and expected output. Add exact Git coordinates when needed. Internal capsules need neither an App recipient id nor the App packet schema.

Complete all currently authorized, dependency-ready actions, including independent dispatches and local work. Sending a task or an informational report is not a reason to end the turn. Process a returned result when it enables acceptance or another ready action. Pause only affected work when a decision is genuinely required.

Wait only for an actual unfinished dependency, using the host's bounded/event wait mechanism. Collect internal-agent results before claiming completion. For durable App tasks, follow the host's initial-check and wake mechanisms; yield when no useful work remains and a supported future event will resume the owner. Do not repeatedly read/list tasks or use sleep loops merely to observe unchanged progress. Do not claim a future wake or successful delivery without evidence that the host provides it.

## Implement and verify proportionally

Choose the smallest change that satisfies the objective and acceptance. Read enough of the affected call chain and contracts to understand it; avoid whole-tree exploration by default. Prove the requested user-visible path before unrelated hardening or generalization.

Run the repository's required acceptance checks and risk-relevant tests. Broaden or repeat only for new changes, failures, or a specific unresolved risk affecting this outcome. A review starts with the exact delta, relevant baseline, and evidence. Reuse still-valid evidence; a failed relevant check must not be hidden by a narrow test budget. Focused checks do not prove the full repository or production behavior.

The owner verifies the actual diff, ownership, acceptance evidence, and remaining limitations. Once acceptance passes, stop expanding implementation. Out-of-scope findings remain recommendations unless they demonstrate that the accepted result would be incorrect or unsafe; then explain the conflict and obtain the necessary scope decision.

## Checkpoint, report, and hand off

Commit coherent, verified task-owned output before a planned pause, ownership handoff, formal review, or final delivery. Internal contributors normally return their changes to the owning task for a combined commit. Never stage mixed or another owner's changes; record exact unresolved paths and recovery needs instead.

Results include the outcome, checkpoint/paths, checks, evidence limits, unresolved issues, and next decision if any. The owning task collects internal results and handles any separately authorized App communication, preserving recipient model/settings. If delivery fails, retain the result and distinguish produced from delivered; use an available authorized result-retrieval path without bypassing a permission denial.

At a recoverable boundary, consider fresh-context handoff when moving to a substantially independent phase or when repeated correction/rediscovery shows context drift, including repeated failure on the same slice. Do not wait for both a new topic and proven drift. Use [continuity.md](references/continuity.md); cumulative tokens alone do not measure current context health.

After acceptance, a rolling-state update records the existing result; it does not reopen review unless it changes normative content or verdict-bearing evidence. Archive eligible App tasks, then classify every owned worktree/branch for safe removal or explicit retention under [recovery.md](references/recovery.md). Preserve unintegrated or recoverable work. Completion, integration, archive, cleanup, push, and deployment are distinct facts.
