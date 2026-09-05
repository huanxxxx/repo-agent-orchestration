# Contributing

Contributions should preserve the distinction between reusable orchestration behavior and repository-specific policy.

## Before opening a change

1. Keep generic controller, routing, contract, review, recovery, and cleanup behavior inside the installable skill.
2. Keep concrete repository paths, model selections, shared write surfaces, and external gates in examples rather than hard-coding them into the skill.
3. Add or update tests for every validator behavior change.
4. Avoid adding task state machines, authorization receipts, or product-specific execution packages to the reusable skill.
5. Separate core collaboration guidance from optional App transport. Preserve explicit independence requirements and real authority/ownership boundaries while allowing unaffected work to continue.
6. Test observable behavior or mechanical invariants rather than requiring policy sentences verbatim. For workflow changes, replay relevant `examples/behavioral/cases.json` inputs with a fresh evaluator and withhold the expected outcomes; distinguish decision-only exercises from real tool execution.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
```

If Codex's official `skill-creator` validator is available, also run its `quick_validate.py` against `skill/repo-agent-orchestration`.

## Pull requests

Describe the behavior being changed, the failure mode it prevents, the tests executed, and any compatibility impact on repository profiles or task contracts.
