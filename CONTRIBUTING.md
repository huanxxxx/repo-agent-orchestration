# Contributing

Contributions should preserve the distinction between reusable orchestration behavior and repository-specific policy.

## Before opening a change

1. Keep generic controller, routing, contract, review, recovery, and cleanup behavior inside the installable skill.
2. Keep concrete repository paths, model selections, shared write surfaces, and external gates in examples rather than hard-coding them into the skill.
3. Add or update tests for every validator behavior change.
4. Avoid adding task state machines, authorization receipts, or product-specific execution packages to the reusable skill.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
```

If Codex's official `skill-creator` validator is available, also run its `quick_validate.py` against `skill/repo-agent-orchestration`.

## Pull requests

Describe the behavior being changed, the failure mode it prevents, the tests executed, and any compatibility impact on repository profiles or task contracts.
