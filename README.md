# Repo Agent Orchestration

### A controllable, repository-native Ultra-style workflow for Codex

**The controller plans and accepts. Explicitly routed workers execute. Independent agents review. Git worktrees keep every writer isolated.**

Repo Agent Orchestration is a lightweight Codex Skill for coordinating multi-agent repository work through explicit role separation, model routing, on-demand Git worktrees, independent review, direct reports, and controller-owned acceptance.

Codex already knows how to use agents. This project focuses on the harder engineering questions: who may write, where they may write, which model is submitted for the task, how completion is proven, and who may integrate the result.

> Unofficial community project. It does not unlock, reproduce, or bypass OpenAI's proprietary Ultra implementation, product entitlements, or usage limits. “Ultra-style” describes a multi-agent collaboration pattern, not compatibility with or equivalence to an OpenAI product mode.

## Why

Multi-agent coding fails when:

- two agents write to the same working tree;
- an execution task runs from the wrong repository or cwd;
- a worker silently falls back to an unintended model;
- a reviewer modifies the candidate it is supposed to review;
- an agent reports PASS and nobody verifies the real diff;
- a worker finishes in its own task but never delivers the final milestone to the controller;
- a completed turn says `owner=task` even though it cannot restart itself;
- a safety handshake takes longer than the work it protects;
- merge, push, deploy, or production access becomes implicit.

This Skill turns those failure modes into explicit contracts and fail-closed gates.

**No daemon. No dashboard. No shared writable worktree.**

## Default Luna-first profile

| Role | Responsibility | Default policy |
|---|---|---|
| Controller | Plan, route, decide, accept, integrate, and close | Current Codex task selection |
| Write task | Implement one independently accepted change | Explicit repository model; installer default is `gpt-5.6-luna/max` |
| Review task | Review one frozen candidate without writing | App default unless repository or user overrides it |
| Internal helper | Short current-turn read-only retrieval or comparison | Inherited; never an execution fallback |

The model names are repository configuration, not a promise that every Codex surface exposes the same models or echoes the effective runtime model. A submitted model binding is recorded as submitted; treat it as unverified unless the product returns the effective model.

## Workflow

```text
                         +----------------------+
                         | Controller           |
                         | Plan / Route / Gate  |
                         | Verify / Integrate   |
                         +----------+-----------+
                                    |
                     readiness audit and contracts
                   +----------------+----------------+
                   |                |                |
           +-------v-------+ +------v--------+ +-----v----------+
           | Write task A  | | Write task B | | Read-only      |
           | Worktree A    | | Worktree B   | | reviewer       |
           +-------+-------+ +------+--------+ +-----+----------+
                   |                |                |
                   +----------------+----------------+
                                    |
                         frozen candidate + evidence
                                    |
                         controller acceptance gate
```

Every writer owns one task boundary, one branch, one repository-local worktree, and one writable ownership boundary. Short read-only work needs no tree. Candidate review reuses the frozen implementation tree; long or historical review gets an on-demand detached snapshot only when a stable filesystem is useful.

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
4. writes an explicit instruction to use the Skill for implementation, formal review, parallel dispatch, recovery, integration, and closure;
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

On upgrade, omitted CLI options preserve values already present in the managed `AGENTS.md` block. Defaults are used only when a value does not yet exist.

The repository profile remains configurable:

```text
MAIN_BRANCH: main
ROOT_WORKTREE_POLICY: observe_integrate_validate
WORKTREE_ROOT: <absolute repo-local worktree root>
BRANCH_PREFIX: codex/
TASK_HOST_POLICY: repository_project_local
CONTROLLER_MODEL_POLICY: app_current_task
WRITE_TASK_MODEL: <explicit model>/<reasoning>
REVIEW_TASK_MODEL: app_default
SHARED_INTEGRATION_PATHS: <repository-specific paths>
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
- valid Luna Max write task;
- valid read-only review;
- valid final milestone;
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

Supported kinds are `binding`, `write`, `review`, and `update`. Direct CLI checks for `binding`, `write`, and `review` are live: synthetic example paths are intentionally rejected unless they currently exist and match the Git worktree registry, branch, commit, and clean-state contract. `scripts/validate_examples.py` performs the portable static example matrix.

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
- Worker or reviewer PASS remains evidence, not controller acceptance.
- A child task's local final is not a delivered controller report; blocked and final reports use direct task-message delivery.
- Controller-bound reports preserve the controller's task settings: workers omit `model` and `thinking`, which otherwise override the destination task.
- Visible repository tasks explicitly use App environment `local`; isolation comes from the repository-local execution worktree, never an App-managed worktree.
- Accepted child tasks are archived explicitly by the controller; a child `final` is delivery, not archival.
- The controller yields after dispatch and resumes only on a real event. The Skill does not pretend an immediate snapshot can detect later silence.
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
