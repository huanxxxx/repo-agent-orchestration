# Architected delivery

Use this mode only when repository policy maps the task to it, the user requests an independent design authority, or the work creates or changes architecture, data contracts, core workflows, product boundaries, multiple implementation packages, or a material direction choice. A repository may use local tiers such as T0-T3, but it owns their meaning and maps them to `direct`, `delivery`, or `architected`; this Skill does not redefine those tiers.

## Keep three authority layers

### Design authority

Own the product objective, global design, frozen decisions, non-goals, acceptance baseline, design review, design reopen decisions, and final design-consistency acceptance.

- Treat the user's goal, constraints, and informed final choices as authoritative. Treat a proposed solution as input, not proof that the design is sound.
- Reconstruct repository facts, current architecture, domain contracts, operator experience, long-term evolution, cost, and material risks before freezing a direction.
- Challenge a user or repository assumption only when it materially affects the objective, main architecture, data contract, user experience, maintainability, or serious risk. Cite evidence, explain the tradeoff, and recommend a preferred option.
- Do not manufacture objections, expand the threat model, or keep debating after an informed decision merely to appear independent. Record the accepted tradeoff and freeze it unless new evidence, safety, or authority requires reopening.
- Checkpoint the candidate, directly dispatch it, and require independent design-review PASS before `DESIGN_HANDOFF` or `reopen_approved`; never proxy or relabel through delivery.
- Bounded reopen is delta: reuse facts, inspect affected clauses/evidence, make one minimal checkpoint, dispatch one reviewer, and yield. Defer index/continuity/global status until PASS; send no interim `DESIGN_DECISION`.
- Own design writes before handoff. `DESIGN_HANDOFF` transfers the single repository-root write lease to the delivery controller; remain read-only while delivery owns that lease.
- Do not dispatch implementation peers or manage their routine progress. Receive only the delivery plan, decision-relevant milestones, design reopen requests, and final delivery evidence.
- End the design-authority turn after sending `DESIGN_HANDOFF` or `DESIGN_DECISION`, or after handling the decision requested by one `DELIVERY_UPDATE`. For `DECISION_REQUIRED: no`, record the bounded fact and end the turn without replying merely to acknowledge it.
- While delivery owns the write lease, the design authority must not inspect, wait on, or monitor the delivery controller's downstream peers, task statuses, logs, worktrees, environment setup, or routine checkpoints. It may inspect repository evidence cited in a formal decision packet or perform user-authorized route recovery, but it does not shadow delivery execution.

### Delivery controller

Own implementation planning, the dependency graph, ready-set calculation, task dispatch, implementation finding adjudication, integration, and delivery evidence. Do not change the frozen objective, architecture, non-goals, or acceptance baseline.

- Validate `DESIGN_HANDOFF`, translate it into milestones and independently acceptable implementation slices, and preserve the exact design checkpoint in every architected packet.
- Name one `SHARED_PATH_OWNER` in the delivery plan and keep repository-root integration single-writer. Never write the root concurrently with the design authority.
- Once implementation is authorized, dispatch every ready, non-conflicting peer task within available capacity without waiting for a separate user instruction to parallelize. Require independent acceptance, non-overlapping write ownership, satisfied dependencies, and closed external gates.
- Keep coupled small work in the current task or bounded internal subagents. Never create duplicate tasks or split work only to fill capacity.
- Send `DELIVERY_UPDATE` for the initial plan, a decision-relevant milestone, and final delivery. A report with `DECISION_REQUIRED: no` does not pause work inside the frozen design.
- Send `DESIGN_REOPEN_REQUEST` when implementation exposes a false assumption, incompatible constraint, or required boundary change. Pause the affected scope and its dependents; continue unrelated ready work only when independence is proven.
- When a reopen needs a new design checkpoint, stop root integration, checkpoint all delivery-owned root changes, and reconcile root status with its recorded baseline before the design authority temporarily retakes the root-write lease. Unaffected peers may continue only in their isolated worktrees. The new `DESIGN_DECISION` transfers the lease back with the updated checkpoint.
- End the controller turn after completing the synchronous planning, dispatch, routing, integration, or reporting actions caused by the current event. A peer remaining active, a future checkpoint, or another message expected later is not permission to keep the turn open.

### Independent peers

Peer writers implement their exact accepted outcome. Peer reviewers evaluate either the frozen design (`REVIEW_CLASS: design`) or a frozen implementation candidate (`REVIEW_CLASS: implementation`). They report to the role that dispatched them and never create design authority.

## Preserve the report chain

```text
design reviewer -> design authority
design authority --DESIGN_HANDOFF--> delivery controller
peer writer/reviewer -> delivery controller
delivery controller --DELIVERY_UPDATE/DESIGN_REOPEN_REQUEST--> design authority
design authority --DESIGN_DECISION--> delivery controller
```

All App-created tasks remain runtime peers. The arrows describe authority and task-message destinations, not App parent-child ownership. Each wake handles one bounded event batch; neither the design authority nor the delivery controller stays online to poll another peer or stretches one turn across later task messages.

Use [contracts.md](contracts.md) and the pure constructor before crossing these boundaries. Before its final report, the delivery controller accepts and archives completed implementation peers. A delivery final is evidence, not overall acceptance: the design authority compares the integrated result with the frozen design checkpoint. If it passes, archive the accepted delivery-controller peer and report completion without waking it merely to acknowledge acceptance. If delivery must resume, send a bounded `DESIGN_DECISION` instead.
