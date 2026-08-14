# Repo Agent Orchestration

### A controllable, repository-native Ultra-style workflow for Codex

**Choose the lightest useful mode: direct work, controller-led delivery, or independent design authority plus parallel delivery.**

Repo Agent Orchestration is a lightweight Codex Skill for coordinating multi-agent repository work through explicit authority, model routing, on-demand Git worktrees, optional repository continuity packages, independent review, direct reports, and evidence-based acceptance.

Codex already knows how to use agents. This project focuses on the harder engineering questions: who may write, where they may write, which model is submitted for the task, how completion is proven, and who may integrate the result.

> Unofficial community project. It does not unlock, reproduce, or bypass OpenAI's proprietary Ultra implementation, product entitlements, or usage limits. “Ultra-style” describes a multi-agent collaboration pattern, not compatibility with or equivalence to an OpenAI product mode.

## Why

Multi-agent coding fails when:

- two independent task owners write to the same working tree;
- an execution task runs from the wrong repository or cwd;
- a worker silently falls back to an unintended model;
- a reviewer modifies the candidate it is supposed to review;
- an agent reports PASS and nobody verifies the real diff;
- a worker finishes in its own task but never delivers the final milestone to the controller;
- a completed turn says `owner=task` even though it cannot restart itself;
- a safety handshake takes longer than the work it protects;
- merge, push, deploy, or production access becomes implicit.

This Skill turns those failure modes into explicit contracts and fail-closed gates.

**No daemon. No dashboard. No shared writable worktree between independent tasks.**

## Default host-compatible profile

| Role | Responsibility | Default policy |
|---|---|---|
| Design authority | Freeze the professional global design, decide reopen requests, and accept final design consistency in `architected` mode | Current Codex task selection |
| Delivery controller | Plan dependencies, proactively dispatch ready work, adjudicate implementation findings, integrate, and report back | Same task in `delivery`; App default or explicit repository binding in `architected` |
| Peer write task | Implement one independently accepted change | App default unless repository or user explicitly binds a supported model |
| Peer review task | Review one frozen candidate without writing | App default unless repository or user overrides it |
| Internal subagent | Bounded current-turn retrieval or non-overlapping contribution | Inherits the current task path; never owns a branch or worktree |

The installer defaults architected delivery controllers, writers, and reviewers to `app_default`, which omits model overrides and lets the destination host select a compatible model. An explicit repository or user binding is used only after the host advertises that model. Model names remain repository configuration, not a promise that every Codex surface exposes the same catalog or echoes the effective runtime model; never infer availability only from the current authority model family.

## Workflow

```text
                  +--------------------------+
                  | Design authority         |
                  | Freeze / Reopen / Accept |
                  +------------+-------------+
                               |
                     DESIGN_HANDOFF / reports
                               |
                  +------------v-------------+
                  | Delivery controller      |
                  | Plan / Dispatch / Merge  |
                  +------------+-------------+
                               |
                    ready-set parallel dispatch
                 +-------------+-------------+
                 |             |             |
          +------v------+ +----v--------+ +--v-----------+
          | Writer A    | | Writer B    | | Reviewer     |
          | Worktree A  | | Worktree B  | | Read-only    |
          +-------------+ +-------------+ +--------------+
```

This diagram shows `architected` mode. Ordinary `delivery` collapses design and delivery authority into the current controller; `direct` creates no peer tasks. Every App-created user-visible task is still a runtime peer, even when another task dispatched it: authority arrows are not App parentage. Every peer write task owns one branch, one repository-local worktree, and one writable ownership boundary. Internal subagents are participants inside one current task: they inherit its path, receive non-overlapping scopes, return within the current turn, and create no tree of their own. A peer task is justified by independent acceptance, cross-turn waiting, model binding, recovery, or formal review—not by agent count alone. Candidate review reuses the frozen implementation tree while its writer is paused; long or historical review gets an on-demand detached snapshot only when a stable filesystem is useful.

When a repository defines an execution package or equivalent continuity entry, the Skill keeps it separate from both the App task and Git worktree. It stores durable objective, scope, state, acceptance, recovery, and next-step facts; repository-specific tiers, paths, templates, and scaffolding stay in the repository. Clean worktrees use their current HEAD as the recovery anchor, and prechange snapshots remain explicit rather than ceremonial.

Task startup is one phase: the initial instruction performs a fast route gate and continues in the same turn when it passes. A route mismatch fails before the first write; there is no mandatory binding-only turn followed by a second authorization turn.

## Install into a repository

Run from this cloned project:

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository
```

The installer:

1. requires the exact absolute Git repository root;
2. copies the Skill to `.agents/skills/repo-agent-orchestration`;
3. creates or idempotently updates one marked block in the root `AGENTS.md`;
4. writes an explicit instruction to use the Skill for architecture-sensitive work or when delivery needs independent task ownership, formal review, parallel dispatch, cross-turn recovery, integration, or closure;
5. preserves existing repository configuration outside the managed block;
6. excludes `__pycache__` and `.pyc` artifacts.

Preview without writing:

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository --dry-run
```

Check whether an installed copy or managed profile has drifted without writing:

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository --check
```

On upgrade, omitted CLI options preserve values already present in the managed `AGENTS.md` block, except the former installer default `gpt-5.6-luna/max`, which migrates automatically to `app_default`. Defaults are used only when a value does not yet exist. Pass an explicit CLI value only when deliberately binding a repository to a supported model.

The installer accepts `--main-branch`, `--worktree-root`, `--branch-prefix`, `--root-worktree-policy`, `--task-host-policy`, `--controller-model-policy`, `--delivery-controller-model`, `--write-task-model`, `--review-task-model`, `--shared-integration-paths`, `--continuity-policy`, and `--external-gates`. The fixed protocol fields currently accept only `TASK_HOST_POLICY: repository_project_local` and `CONTROLLER_MODEL_POLICY: app_current_task`. Model values must be `app_default` or `<model>/<reasoning>`; invalid values are rejected before any write. Operational failures print a structured JSON error and exit nonzero instead of a traceback.

The repository profile remains configurable:

```text
MAIN_BRANCH: main
ROOT_WORKTREE_POLICY: observe_integrate_validate
WORKTREE_ROOT: <absolute repo-local worktree root>
BRANCH_PREFIX: codex/
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
DELIVERY_CONTROLLER_MODEL: app_default|<explicit model>/<reasoning>
WRITE_TASK_MODEL: app_default|<explicit model>/<reasoning>
REVIEW_TASK_MODEL: app_default
SHARED_INTEGRATION_PATHS: <repository-specific paths>
CONTINUITY_POLICY: none|repository_defined:<index or entry>
EXTERNAL_GATES: <merge, push, deploy, data, credential, and publication gates>
```

See [examples/AGENTS.profile.md](examples/AGENTS.profile.md) for a neutral profile.

## Run the local end-to-end demo

```bash
python scripts/run_local_demo.py
```

The demo creates a temporary Git repository, two independent writer branches and worktrees, valid route/write/review/final contracts, one deliberately invalid `projectless` route with an escaping `..` path, and one missing-worktree route. It passes only when both writers are registered separately, valid contracts pass, both invalid routes are rejected, and the writers do not change the root baseline. The final contract also proves direct controller delivery.

Evidence boundary: this deterministic demo exercises local Git isolation and the contract gate. It does not create Codex tasks, verify task-message delivery, or prove an effective runtime model. Use [the Codex Desktop runbook](examples/demo/CODEX_DESKTOP_RUNBOOK.md) for a reproducible product-facing demonstration and record those external receipts separately.

## Run contract examples

Validate every published positive and negative example:

```bash
python scripts/validate_examples.py
```

Individual examples live in [examples/contracts](examples/contracts):

- valid Windows binding;
- valid App-default write task;
- valid explicit Luna Max write task;
- valid read-only review;
- valid worker final update;
- valid architected delivery plan and milestone;
- valid design handoff, reopen, and decision packets;
- invalid projectless task;
- invalid worktree path escape;
- invalid App-managed worktree environment;
- invalid local-final-only report;
- invalid controller-bound report model override;
- invalid obsolete ownership fields;
- invalid obsolete waiting fields.

You can also invoke the validator directly:

```bash
python skill/repo-agent-orchestration/scripts/validate_dispatch_contract.py \
  --kind update examples/contracts/valid-final-update.txt
```

Supported kinds are `binding`, `write`, `review`, `update`, `design_handoff`, `delivery_update`, `design_reopen`, and `design_decision`. Direct CLI checks for route packets are live: synthetic example paths are intentionally rejected unless they currently exist and match the Git worktree registry, branch, commit, and clean-state contract. `scripts/validate_examples.py` performs the portable static example matrix.

For a new outgoing packet, stream JSON fields through the constructor's single boundary command. `--live` combines construction, static validation, and live route/Git validation, so no temporary packet or second validator call is needed:

```powershell
Get-Content -Raw fields.json | python skill/repo-agent-orchestration/scripts/construct_packet.py --kind design_reopen --live -
```

Incoming packet text can likewise be streamed to `validate_dispatch_contract.py --kind <kind> -`. The constructor shares its declarative schema with the validator and does not create tasks, touch Git, send messages, wait, or archive anything. The ordinary `delivery` mode remains available; use the optional `architected` mode when repository policy or task facts require a separate design authority, delivery controller, and independent execution/review layer.

## Compatibility and evidence limits

OpenAI documents repository-local Skill discovery from `$REPO_ROOT/.agents/skills` and repository instruction discovery through `AGENTS.md`. Standalone Skills are documented for the desktop app, Codex CLI, and the IDE extension. See the official [Skill documentation](https://learn.chatgpt.com/docs/build-skills) and [AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

| Surface | Status for this project |
|---|---|
| Codex Desktop on Windows, saved local repository project | **Primary tested surface** for the full repository-host/execution-worktree workflow |
| Python validator and installer | Standard-library only; repository CI targets Python 3.11 and 3.13 on Ubuntu, and local acceptance runs on Python 3.13/Windows |
| Codex CLI and IDE extension | Repository Skill discovery is documented; the full visible-task, project-id/cwd receipt, and direct task-message workflow is **unverified here** |
| macOS/Linux Codex product workflow | POSIX path behavior is unit-tested; product-level task hosting and receipts are **unverified here** |
| ChatGPT Work on the web | Full standalone repository workflow is **unsupported or unverified here**; a future Plugin may be a better distribution surface |

The full profile depends on capabilities that a surface may not expose uniformly: a saved repository project, local task hosting, user-visible task creation, explicit model parameters, direct task messages, actual project/cwd receipts, and a separately controlled execution worktree. If any required capability is missing, stop and report the capability gap instead of downgrading the route.

OpenAI's desktop worktree feature uses Codex-managed worktrees and is documented separately. This project intentionally supports an existing repository-local worktree boundary and does not claim that a Codex-managed worktree is equivalent. See the official [worktree documentation](https://learn.chatgpt.com/docs/environments/git-worktrees).

## Security properties

- Projectless repository tasks are rejected.
- Task hosting and Git execution coordinates are validated separately.
- Windows, extended Windows, and POSIX paths are normalized lexically before containment checks; nonexistent paths are supported and `..` escapes fail closed.
- Every repository command must use the exact execution path.
- Review selects the lightest safe target: root, frozen candidate, or detached snapshot.
- Worker or reviewer PASS remains evidence, not acceptance by the contracted authority.
- A peer task's local final is not a delivered authority report; blocked and final reports use direct peer-to-peer task-message delivery.
- Task-message reports preserve destination settings: senders omit `model` and `thinking`, which otherwise override the destination task.
- Visible repository tasks explicitly use App environment `local`; isolation comes from the repository-local execution worktree, never an App-managed worktree.
- A queued App worktree setup or worktree-creation receipt is a failed peer route, not a task to wait on or recover as if it had started.
- Accepted peer tasks are archived explicitly by the authority that dispatched them; a peer `final` is delivery, not archival.
- Repository continuity packages are optional durable fact anchors, never task-message channels, authorization tokens, or workflow engines.
- A post-PASS continuity-only closeout keeps the reviewed checkpoint distinct from its later bookkeeping commit and never triggers review merely to record that PASS occurred.
- A clean task worktree uses its HEAD as the recovery anchor; prechange snapshots require an explicit request or an authorized risky rewrite of task-owned tracked changes.
- Coherent task-owned output is committed locally before a cross-turn pause, ownership handoff, formal review, or final; unsafe mixed ownership is reported precisely instead of staged.
- Write tasks make the smallest acceptance-satisfying change and stop when acceptance passes; unrequested architecture, alternate paths, and hardening require a separately authorized scope.
- A product-required peer startup wait occurs at most once; ordinary active, progress, or timeout results end the controller turn instead of starting another wait.
- Each authority wake processes one bounded event batch and ends; future peer events must wake a new turn rather than extending a polling session.
- The route gate and repository profile are read once per stable task binding; later wakes reuse them and load only changed hot state.
- Routine outgoing packets use one streamed constructor/live-validation command instead of temporary files and duplicate validation calls.
- Constructor, schema, or validator contradictions fail closed as `PROTOCOL_BLOCKED`; packet kinds cannot be relabelled to bypass the failed boundary.
- Merge, push, deployment, publication, production data, credentials, and permissions remain separate gates.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The test suite and project scripts use only the Python standard library. Git is required for installer repository checks and the local worktree demo.

## Project layout

```text
skill/repo-agent-orchestration/  Installable Codex Skill
scripts/install_repository.py    Repository-local installer
scripts/validate_examples.py     Published contract-example runner
scripts/run_local_demo.py        Temporary Git/worktree demonstration
examples/contracts/              Runnable positive and negative contracts
examples/demo/                   Product-facing demonstration runbook
tests/                           Contract, installer, example, and demo tests
.github/workflows/               Python 3.11/3.13 CI
```

## License

MIT. See [LICENSE](LICENSE).
