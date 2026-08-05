# Repository Agent Orchestration

A reusable Codex skill for coordinating repository work through a deliberate split between a reasoning-heavy controller and explicitly routed execution or review tasks.

The skill keeps generic collaboration mechanics outside application repositories. Each target repository supplies only its own paths, model policy, shared write surfaces, and external authorization gates through `AGENTS.md`.

## What it provides

- Deterministic routing between the controller, user-visible tasks, and short read-only internal helpers.
- Event-driven parallel readiness audits and same-wave dispatch of independent work.
- Repository-local worktree isolation with one writable owner per task boundary.
- Fail-closed repository hosting and repo-local execution-worktree binding that rejects projectless tasks without requiring every linked worktree to become an App project.
- Explicit write-task model binding and configurable review-task model policy.
- Milestone handoffs, one-shot missing-report checkpoints, and direct task messaging.
- Frozen-candidate read-only review, controller-owned acceptance, and safe recovery.
- Contract validation for write tasks, review tasks, and milestone reports.

## Role model

| Role | Responsibility | Model policy |
|---|---|---|
| Controller | Plan, route, decide, accept, integrate, and close | Current App task selection |
| Write task | Implement an independently accepted change | Explicit repository model and reasoning |
| Review task | Review a frozen candidate without writing | App default unless the repository or user overrides it |
| Internal helper | Short current-turn read-only retrieval or comparison | Inherited; never an execution fallback |

## Install into a repository

Install the Skill into the target repository. This is the default and recommended mode:

```bash
python scripts/install_repository.py --repo /absolute/path/to/repository
```

The installer copies the Skill to `.agents/skills/repo-agent-orchestration` and idempotently manages one marked orchestration-profile block in the repository-root `AGENTS.md`. If `AGENTS.md` does not exist, it creates a minimal one. If it exists, all content outside the marked block remains unchanged.

User-global installation remains possible as a compatibility choice, but it is not the default.

## Configure a target repository

Add a repository profile to its root `AGENTS.md`:

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

Also instruct repository agents to use `$repo-agent-orchestration` for implementation, formal review, parallel dispatch, handoffs, recovery, integration, and closure. If the skill or a required task/path/model capability is unavailable, stop and report instead of silently changing routes.

See [examples/AGENTS.profile.md](examples/AGENTS.profile.md) for a complete neutral example.

## Validate a task contract

```bash
python skill/repo-agent-orchestration/scripts/validate_dispatch_contract.py \
  --kind write path/to/write-contract.txt
```

Before granting a task write or formal-review authority, validate the actual task binding too:

```bash
python skill/repo-agent-orchestration/scripts/validate_dispatch_contract.py \
  --kind binding path/to/binding-receipt.txt
```

Supported kinds are `binding`, `write`, `review`, and `update`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The test suite uses only the Python standard library.

## Project layout

```text
skill/repo-agent-orchestration/  Installable Codex skill
scripts/                         Repository-local installer
examples/                        Repository configuration examples
tests/                           Contract and structure tests
.github/workflows/               CI
```

## Scope and safety

This project coordinates authorized work; it does not grant new authority. Merge, push, deployment, publication, production data, credential, and permission changes remain behind repository and user gates.

A path named in a task prompt is not an execution binding. In `repository_project_local` mode, the user-visible task is hosted by the current repository's saved project with a repository-root cwd; all repository commands and file operations are separately bound to the existing repo-local execution worktree. The root must remain clean. This avoids user-global projectless tasks without registering every linked worktree as its own App project.

## License

MIT. See [LICENSE](LICENSE).
