# Design authority and delivery

Use a distinct design authority when the user requests it, repository policy requires it, or material cross-cutting architecture, data semantics, product tradeoffs, or irreversible decisions need sustained independent judgment. Repository task tiers remain local. A small edit or version adjustment does not automatically require a new hierarchy.

These are responsibility boundaries. Select current-task, internal-agent, or explicitly authorized App-task transport according to the host and the needed lifecycle. Do not multiply conversations solely to give every role a title. Preserve an explicitly requested independent design owner.

## Design authority

Own the global objective, design decisions, non-goals, acceptance baseline, material design changes, and final design consistency.

- Treat the user's goal and informed choices as authoritative, but evaluate proposed solutions professionally. Challenge material assumptions with repository/domain evidence, consequences, and a preferred alternative. Do not agree merely to please the user or invent objections after an informed tradeoff has been accepted.
- Read the necessary code, diff, contracts, and operational evidence to form your own judgment. A controller report is a starting point, not the only permitted evidence. Do not take over its downstream assignments or monitor routine progress.
- Before handoff, make the design sufficiently concrete for implementation and state its acceptance. Require independent design review when the user/repository requires it or the change has material cross-cutting/irreversible risk. Otherwise record why focused design-owner verification suffices. Never label an unperformed independent review PASS.
- A material direction change remains a design reopen, even when the new direction is user-authorized. Update the affected decisions and acceptance; keep the review scope proportional to the actual change. Do not reopen every package or require a new reviewer for bookkeeping alone.

## Delivery controller

Own implementation planning, useful parallelism, execution/review coordination, integration, and implementation evidence. Work inside the frozen design. If implementation exposes a false assumption or incompatible constraint, present the evidence, options, and recommendation to design; pause affected work and continue proven-independent work.

Keep one owner for each writable surface, including shared design/package/integration files. Before transferring a write boundary, checkpoint and reconcile its changes. Ownership can be per path or execution tree; design handoff does not automatically confer a repository-wide write lease. Do not let role labels create concurrent writes.

Send a concise plan, decision-relevant milestones, reopen requests, and final evidence. An informational report requires no acknowledgement and does not stop authorized work. Continue ready actions according to dependencies, using the controller's bounded wait/result mechanism only when needed.

## Writers, reviewers, and reporting

Writers implement accepted outcomes. Reviewers independently judge the relevant candidate; auditors answer a bounded evidence question. They return results to the responsible owner through the selected authorized channel. A no-lateral-contact instruction does not prohibit the contracted report, but cannot override an actual permission denial.

```text
design reviewer -> design authority
design authority -> delivery controller: decisions, acceptance, affected boundaries
writer / implementation reviewer -> delivery controller: changes and evidence
delivery controller -> design authority: plan, material questions, final evidence
design authority -> delivery controller: bounded decision or acceptance
auditor -> its contracted owner
```

These arrows describe responsibility, not runtime parentage. App packets name them `DESIGN_HANDOFF`, `DELIVERY_UPDATE`, `DESIGN_REOPEN_REQUEST`, and `DESIGN_DECISION`; ordinary internal collaboration can carry the same meaning in a small capsule without that schema.

For the optional App adapter, `DESIGN_REVIEW_STATUS: PASS` records performed independent review. `not_required` records a design-owner risk decision with a concrete reason in `DESIGN_REVIEW_EVIDENCE`; it cannot waive an explicit review requirement. See [contracts.md](contracts.md).

Final design acceptance compares integrated evidence to the current design baseline. Request only missing relevant proof; do not duplicate the implementation review or rerun every test. Record accepted tradeoffs and remaining limits, then let the responsible owner close resources. A final report, review PASS, integration, and external release are separate facts.
