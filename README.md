# Repo Agent Orchestration

### Useful context boundaries for repository delivery

A lightweight Codex Skill for finishing repository work across appropriate contexts, with clear ownership, proportional verification, reliable results, and recoverable handoff.

The core describes engineering responsibilities, not a mandatory App task hierarchy. Use direct work for bounded outcomes, available internal agents for useful subtasks and independent judgment, and explicitly requested App tasks for a separate user-owned lifecycle. Choose a distinct design authority for material design tradeoffs or when the user/repository requires one.

Unofficial community project. It does not grant permissions, unlock product capabilities, or reproduce a proprietary OpenAI orchestration system.

## What changes decisions

- Delegate ready, separable work when authorized and useful. Sending one assignment or an informational report does not end the owner turn.
- Continue dependency-ready work; wait through the host's bounded/result mechanism only when a real dependency needs it. Do not poll unchanged task status or promise unsupported wakeups.
- Keep implementation and review judgments independent without requiring every reviewer to be a user-visible App task.
- Verify actual Git identity and exclusive paths. Internal writers share their owner's tree with disjoint scopes; independently running App writers use separate registered repository-local worktrees.
- Read the affected call chain and run required/risk-relevant checks. Stop implementation at acceptance; expand verification for concrete evidence, not ceremony.
- Preserve meaningful local commits, result delivery status, and recovery coordinates. A failed report does not erase a completed result.
- Consider fresh context at a safe boundary for an independent next phase **or** repeated drift on the same slice. Do not require both. Persistent owner replacement still requires appropriate host support and explicit user authority.
- Preserve single ownership, read-only review, destination model settings, and external-action gates. Classify accepted task worktrees/branches for safe removal or explicit retention.
- Keep repository execution-package names, tiers, templates, and scaffolding in that repository. A post-PASS rolling-state update does not create another review cycle.

## Responsibilities and tools

| Need | Default choice within actual host permissions |
|---|---|
| Small coherent outcome | Current task |
| Parallel bounded contribution or fresh-context investigation | Internal agent with minimal inputs and explicit paths |
| Independent review | Non-author reviewer, relevant raw evidence and acceptance |
| Separate user-visible lifecycle / persistent owner replacement | App task only when explicitly requested and supported |
| Material independent design judgment | Distinct design responsibility; transport chosen separately |

`direct`, `delivery`, and `architected` describe who owns decisions. They are not mandatory numbers of conversations. In architected work, design owns direction and final consistency; delivery owns implementation and returns plans, material questions, and final evidence. Design can inspect necessary code and evidence directly without managing downstream routine work.

Independent design review is required by explicit user/repository requirements or material cross-cutting/irreversible risk. Low-risk adjustments can record why design-owner verification suffices. A real direction change still needs an updated design decision; bookkeeping does not.

## Install or update one repository

Run from this source checkout:

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository
```

The installer copies `skill/repo-agent-orchestration` to `.agents/skills/repo-agent-orchestration` and idempotently updates its marked root `AGENTS.md` block. Existing repository rules outside that block and configured values are preserved. Installation is a local repository change, not a commit, push, release, or permission grant.

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository --dry-run
python scripts/install_repository.py --repo /absolute/path/to/repository --check
```

`--dry-run` previews writes; `--check` detects installed-file/profile drift without changing the target. Upgrades refresh the managed routing prose as well as the Skill, so an old mandatory-App rule is not left in that managed block. Unmanaged repository rules are never rewritten.

Model defaults are `app_default`, which omits model/thinking overrides. On upgrade, existing explicit bindings are preserved except the retired installer default `gpt-5.6-luna/max`, which migrates to `app_default`. Explicit supported bindings remain configurable; this Skill does not select Astra or change the user's current model.

The installer accepts `--main-branch`, `--worktree-root`, `--branch-prefix`, `--root-worktree-policy`, `--task-host-policy`, `--controller-model-policy`, `--delivery-controller-model`, `--write-task-model`, `--review-task-model`, `--shared-integration-paths`, `--continuity-policy`, and `--external-gates`. See [the profile example](examples/AGENTS.profile.md).

`TASK_HOST_POLICY: repository_project_local` remains the supported **optional App adapter** profile. It does not require App task creation for normal work or make an App project id a prerequisite for internal collaboration. `CONTROLLER_MODEL_POLICY: app_current_task` preserves the current selection.

## Optional structured App adapter

The existing constructor and validator remain available when the user explicitly requests App tasks and the host supports the saved-project/local route:

```powershell
Get-Content -Raw fields.json | python skill/repo-agent-orchestration/scripts/construct_packet.py --kind review --live --launch -
Get-Content -Raw report.json | python skill/repo-agent-orchestration/scripts/construct_packet.py --kind update --live --task-message-to controller-task-id -
```

Stream JSON directly when a temporary file is unnecessary. Use the complete launch as `create_thread.prompt`; use the later-message JSON with `send_message_to_thread` without adding another delegation envelope. Keep internal agent ids out of App APIs. New App tasks need an explicit saved project and `environment: {type: "local"}` under this profile.

The eight packet kinds remain `binding`, `write`, `review`, `update`, `design_handoff`, `delivery_update`, `design_reopen`, and `design_decision`. Their shared schema lives in `packet_schema.py`; ordinary internal collaboration does not use it.

Design handoff supports `DESIGN_REVIEW_STATUS: PASS|not_required`. An explicit `not_required` must include a concrete reason in `DESIGN_REVIEW_EVIDENCE` and cannot waive an actual review requirement. Reopen decisions can use the same explicit status; older packets without it retain the independent PASS requirement. The constructor never decides that review is unnecessary.

The adapter still checks exact path containment, saved-project identity, current Git branch/commit, read-only review, and preserved report settings. It does not prove task authorization, actual delivery, review quality, or acceptance. A report's `DELIVERY` field is the intended route, not a delivery receipt.

Local shape errors can be repaired without freezing unrelated work. Ambiguous task creation must be reconciled before retry; insufficient authority, uncertain ownership, or an incorrect target still blocks the affected action. Never bypass a denied tool call.

## Validation and evidence limits

```bash
python -m unittest discover -s tests -v
python scripts/validate_examples.py
python scripts/run_local_demo.py
```

The test suite uses the Python standard library; Git is required for installer/worktree tests. CI targets Python 3.11 and 3.13. Deterministic tests cover packet construction, legacy compatibility, path isolation, model settings, installation, and cleanup of the disposable demo. Packaging tests check discovery and links, not whether specific prohibitions remain word-for-word.

The local demo creates a temporary Git repository and isolated writer trees. It proves local Git/contract checks, not App creation, task-message delivery, effective models, or real agent behavior. [The optional Desktop runbook](examples/demo/CODEX_DESKTOP_RUNBOOK.md) describes an explicitly authorized product-facing demonstration.

[Behavioral cases](examples/behavioral/cases.json) exercise decisions that string assertions cannot prove. Use a fresh evaluator with each case's input and the Skill, withholding the expected outcomes. Record what it actually chose and distinguish decision-only exercises from real tool execution. Do not treat passing unit tests or one model exercise as a guarantee against future drift.

The core depends only on the host's actual permitted agent/result capabilities. The full App adapter has additional requirements: saved project, local task creation, messages, runtime receipts, and separate execution worktrees. Missing optional App capabilities do not invalidate ordinary authorized repository work. Preserve an explicitly requested independence requirement rather than silently substituting a different lifecycle.

## Cleanup

After accepted App work is idle, archive it and make an explicit cleanup decision for every owned worktree/branch. Remove only validated clean, integrated or explicitly abandoned residue with no recovery value, through Git's worktree flow and with applicable authorization. Remove the registered tree before deleting the local branch. Retain unsafe/useful residue with exact coordinates, reason, and next action.

No age-based cleanup, forced deletion of dirty/recoverable work, remote-branch deletion, background daemon, or automatic permission escalation is included.

## Project layout

```text
skill/repo-agent-orchestration/  Installable Skill and optional App packet helpers
scripts/install_repository.py    Repository installer/checker
scripts/validate_examples.py     Portable App packet example matrix
scripts/run_local_demo.py        Disposable Git/worktree demonstration
examples/behavioral/             Independent behavioral exercise inputs
examples/demo/                   Optional product-facing demonstration
tests/                           Deterministic acceptance tests
```

MIT. See [LICENSE](LICENSE).
