---
task_id: TASK-PROC-044-10
type: explore
parent_requirement: REQ-PROC-044
urgency: 3
urgency_reason: U3-FRICTION
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-29
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T01:08:56Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-04]
  sections: []
scope_description: "Explore: external-interface contracts for the factory boundary (E1-E9 inventoried in 07_external_interfaces.md). Inventory all factory-boundary channels (developer questions, product intake, developer notes, web research, OS installs, dependency admission, code release, optimize events, runtime telemetry). For each: declare a contract using the internal format from REQ-PROC-044 mechanism. Define the external-state postcondition vocabulary (command_exited_zero, url_returned_2xx, file_exists_at_path, developer_responded, package_installed_at_version). Identify additive fields the internal format may need to absorb. Produce 6-10 small validator scripts implementing the vocabulary. Determine if external-interface declarations should live in a sibling REQ-PROC-NEW or fold under REQ-PROC-044 — decide and route via product-intake if a new requirement is needed."
release_description: ""
opus_recommended: true   # reason: cross-cutting exploration spanning 9+ external channels; design + policy + new-requirement decision
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-8
session_id: f2fdd72b-f3fd-4220-aac5-f2fba94a1066
session_account: gmail
---
# Goal: Explore External-Interface Contracts for the Factory Boundary

## Objective

The internal skill-interface-contracts mechanism (defined in TASK-PROC-044-02 and rolled out by TASK-PROC-044-03..05) covers skill-to-skill interfaces *inside* the factory. The factory also has external interfaces — places where information crosses the factory boundary in or out. These are currently undeclared.

This exploration determines: (a) the inventory of external interfaces; (b) whether the internal contract format extends cleanly (compatibility check confirms YES — see `07_external_interfaces.md` from the parent exploration); (c) what additive fields are needed for external-specific concerns; (d) the external-state postcondition vocabulary; (e) whether external contracts should land under REQ-PROC-044 or a new requirement.

## Background

The compatibility analysis in `requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/plans_and_protocols/07_external_interfaces.md` inventoried E1–E9:

| # | Interface | Direction |
|---|---|---|
| E1 | Developer-question response | dev → factory (pull) |
| E2 | Developer-initiated change (product intake) | dev → factory (push) |
| E3 | Developer notes (raw feedback) | dev → factory (push, async) |
| E4 | LLM web research | factory → web → factory |
| E5 | OS-level tooling install | factory → OS → factory |
| E6 | Dependency admission | factory → developer (gate) |
| E7 | Produced code → release → user | factory → end-user |
| E8 | Runtime telemetry | end-user → factory (none today, hypothetical) |
| E9 | Optimize-event channel | bash/CI → factory |

The internal contract format extends cleanly to all of them. The differences are in `quality_criteria` style (external-state checks vs file-conformance checks), not in the structural format.

## How to Approach This

1. Read `07_external_interfaces.md` in the parent exploration's plans_and_protocols/.
2. Verify the inventory: walk the factory tree for any external channel I missed (e.g. SSH/SCP, signed-package verification, git remote interactions, manual config edits).
3. For each external interface E1..E9 (and any new ones surfaced in step 2), author a contract.yaml-style declaration. Use `source: external` annotations widely; quality_criteria reference the external-state vocabulary.
4. Define the external-state postcondition vocabulary. Initial set (refine via exploration):
   - `command_exited_zero` — verify a bash command's exit code
   - `url_returned_2xx` — verify a fetched URL responded successfully
   - `file_exists_at_path` — verify a file exists (used for build artifacts, installed packages)
   - `developer_responded` — verify a pending_feedback answer.md exists with content
   - `package_installed_at_version` — verify an installed package's --version output
   - Probable additions: `git_remote_pushed`, `network_allowed_host_matched`, `pdf_render_completed`, etc.
5. Write 6-10 small validator scripts implementing the vocabulary (each is a tier-B script ≤30 lines).
6. Identify additive fields the internal format may need. Most likely candidates: `input_modality: file | frontmatter | conversation | invocation_arg | command_output | url_response` (covers the "natural language input from product intake" case).
7. **Decide**: should external-interface contracts live under REQ-PROC-044 (broadening it to cover all factory contracts) OR under a new sibling REQ-PROC-NEW (external-boundary contracts specifically)? Trade-offs:
   - Under REQ-PROC-044: one requirement covers all contracts; cleaner ACs
   - Sibling requirement: separates concerns (internal mechanism vs external policy); allows different stakeholder ownership
8. Route the decision via `product-intake` if a new requirement is needed.
9. Produce a synthesis document + follow-up tasks for the actual rollout (per the file-14 "tasks are the only integration mechanism" principle).

## Acceptance Criteria

- [x] Exhaustive inventory of external interfaces (E1..E9 verified; any new ones documented)
- [x] Concrete contract.yaml-style declarations for ≥3 external interfaces (covers the spectrum: dev-input, web, OS)
- [x] External-state postcondition vocabulary documented (≥5 initial entries; rationale per entry)
- [x] 6-10 validator scripts written, tier-annotated, passing Python gates
- [x] Recommendation on REQ home (REQ-PROC-044 vs new sibling) with rationale + concrete next step (product-intake invocation if new req needed)
- [x] Synthesis document explicitly addresses what the exploration could NOT validate
- [x] Follow-up tasks created via task-create for the rollout work

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Independent of the internal-rollout chain; can run in parallel with FU-1..FU-7 |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. The compatibility check confirms zero rework risk on the internal mechanism — internal-first sequencing is safe.

This task is `type: explore` (writes_requirements: false). If the exploration decides a new requirement is needed, the actual requirement work happens via product-intake → requ-explore in a follow-up.
