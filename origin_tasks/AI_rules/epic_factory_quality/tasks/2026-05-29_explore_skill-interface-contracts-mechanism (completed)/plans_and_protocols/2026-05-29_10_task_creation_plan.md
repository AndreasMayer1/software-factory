---
requirement: REQ-PROC-044
requirements_version: b10665f5
created: 2026-05-29
mode: full
source_exploration: TASK-PROC-044-02
---

# Task Creation Plan for REQ-PROC-044 — Skill Interface Contracts Rollout

Derived from the exploration in TASK-PROC-044-02 (see `05_round_3_synthesis.md` and `09_amendments.md` in this task's `plans_and_protocols/`).

All 8 tasks land under REQ-PROC-044 because the proposed mechanism operationalizes ACs AC-01..AC-06. None of the tasks touches `lib/`, `test/`, or `integration_test/` directly — all are skill/script/process work. None requires `task-create-code`.

## Tasks

- task_name: "Wave 1: contract.yaml + schemas for producer skills + lint productionization"
  bundle_id: FU-1
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-01, AC-02, AC-03, AC-04]
  effort: L
  layer: factory_infrastructure
  after: []
  task_type: impl
  opus_recommended: true
  scope_description: "Author contract.yaml for the 4 producer skills (task-create, requ-explore, ui-create-scribble, ux-write-canon-concept). Author 5 initial schemas (.claude/schemas/scribble_metadata.yaml, goal_metadata.yaml, flutter_handoff.yaml, concept_canon_entry.yaml, requirements_frontmatter.yaml). Productionize the prototype lint at scripts/quality/check_skill_contracts.py with full named-producer verification (not the PoC simplification). Atomically delete prose specs the new schemas replace (file 14 §4.4 obligation). Wire lint into verify-quality per-change gates."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-2, §D-5 Wave 1. Prototype reference: prototypes/contract_*.yaml + prototypes/check_skill_contracts.py. Source annotation MANDATORY: every derived_from item declares source: external | skill:<name>. Side_effects gain action: write|append|delete|regenerate enum."

- task_name: "Wave 2: contract.yaml for consumer skill families + runtime pre-checks + schema validator"
  bundle_id: FU-2
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-01, AC-02, AC-03, AC-04]
  effort: L
  layer: factory_infrastructure
  after: [FU-1]
  task_type: impl
  opus_recommended: true
  scope_description: "Author contract.yaml for consumer skill families: code-simple, code-complex, code-bugfix, code-test, ui-verify-flutter, ui-improve-flutter, task-derive-from-requ, task-create-code, task-complete. Author scripts/quality/validate_against_schema.py (YAML-dialect schema validator). Add 5-line bash pre-checks at the top of each consumer skill body. Re-run sub-skill-vs-agent rubric on every skill being migrated; document refinements; if any signal weight needs adjustment, propose via revision_target.yaml to FU-6."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-5 Wave 2 + 09_amendments.md §A-5. Wave 2 lands the verification leg (PwC 7× evidence)."

- task_name: "Wave 3: contract.yaml for remaining skills + sunset contract_version: 0"
  bundle_id: FU-3
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-01, AC-03, AC-06]
  effort: M
  layer: factory_infrastructure
  after: [FU-2]
  task_type: impl
  opus_recommended: false
  scope_description: "Complete migration: contract.yaml for all claude-*, doc-*, release-*, misc skills (brb, codegraph, product-intake, verify-quality). 60 days after Wave 3 starts, remove contract_version: 0 from the lint's allowlist. Re-run sub-skill-vs-agent rubric per family; document refinements. Final cleanup: delete any prose duplicates remaining in folder-root READMEs."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-5 Wave 3 + 09_amendments.md §A-5. The sunset is enforced via task_ordering_priority_override.txt — this task carries the sunset commit at its scheduled date."

- task_name: "revision_target.yaml schema + task-create sub-procedure + pending_feedback cleanup discipline"
  bundle_id: FU-4
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-02, AC-04]
  effort: S
  layer: factory_infrastructure
  after: []
  task_type: impl
  opus_recommended: false
  scope_description: "Define revision_target.yaml schema (per 09_amendments.md §A-1). Add sub-section to task-create/SKILL.md for 'Creating a revision-attached task'. Update pending_feedback/README.md with: (a) the new revision-via-task pattern; (b) the 'no cross-task scan for revision_target.yaml' rule; (c) cleanup convention — pending_feedback/{TASK_ID}/ moves to answered_feedback/{TASK_ID}/ on resolution. Write scripts/maintenance/archive_answered_feedback.py to periodically prune old answered_feedback entries (git preserves history)."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-3 (REPLACED by 09_amendments.md §A-1). The cleanup discipline addresses the user's discipline concern in the round-3 followup feedback."

- task_name: "SCRIBBLE-SPLIT: refactor ui-create-scribble into ui-scribble-iterate + 3 sub-skills + 6 ui-scribble-* agents"
  bundle_id: FU-5
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-01, AC-03]
  effort: L
  layer: scribble_pipeline
  after: [FU-3]
  task_type: impl
  opus_recommended: true
  scope_description: "Per 09_amendments.md §A-2 naming + 05_round_3_synthesis.md §D-1 shape. Refactor ui-create-scribble into: thin orchestrator ui-scribble-iterate (owns iteration loop + version tracking); 3 sub-skills (ui-scribble-auto-review, ui-scribble-feedback-classify, ui-scribble-approve-handoff); 6 agents (ui-scribble-generator, ui-scribble-rule-reviewer, ui-scribble-heuristics-reviewer, ui-scribble-persona-walker, ui-scribble-feedback-classifier, ui-scribble-handoff-emitter). Each sub-skill carries contract.yaml. Apply the sub-skill-vs-agent rubric to confirm the 3/4 + 2/4 split holds in production. Existing consumers (ui-verify-flutter, ui-improve-flutter, code-simple, code-complex) gain one-line edits to point at new producer names."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-1, §3.3; 09_amendments.md §A-2. ui-scribble-persona-walker is scribble-scoped (YAGNI per A-2); if Wave 2 surfaces a flutter-implementation need, sibling ui-flutter-persona-walker is a Wave-3 follow-up."

- task_name: "Codify sub-skill-vs-agent rubric in claude-create-skill AND claude-modify-skill"
  bundle_id: FU-6
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-03]
  effort: S
  layer: factory_infrastructure
  after: []
  task_type: impl
  opus_recommended: false
  scope_description: "Add 'Phase split decision' sub-section to claude-create-skill/SKILL.md and 'Re-evaluate phase split' sub-section to claude-modify-skill/SKILL.md. The rubric (4 binary signals; split if 2+): (S1) independent invocation possible? (S2) fan-out to ≥2 agents? (S3) natural human review point? (S4) file-based artifact crossing boundary? Include the SCRIBBLE-SPLIT worked example. Track Wave-2/3 refinements via revision_target.yaml to this task's parent or a refinement sibling."
  implementation_notes: "Source: 05_round_3_synthesis.md §D-1 §3.4 + web research file 02 §Q3. Hermify's bidirectional warning is the rationale for landing in both skills."

- task_name: "Factory-map render (Cytoscape.js) + AC-06 interpretation + token-cost measurement hooks + heat overlay"
  bundle_id: FU-7
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-02, AC-06]
  effort: M
  layer: factory_infrastructure
  after: [FU-1]
  task_type: impl
  opus_recommended: false
  scope_description: "Per 09_amendments.md §A-4. Build scripts/factory/render_factory_map.py: reads all .claude/skills/<name>/contract.yaml + .claude/schemas/*.yaml + factory_flows.md; outputs Cytoscape.js JSON ({nodes:[], edges:[]}); produces static HTML viewer with filters (by family, by artifact-type, by may_invoke graph distance). Include script-call edges as decorations on skill nodes (inferred from may_invoke + side_effects naming scripts). Author hooks (PreToolUse/PostToolUse on Read) to log file path + active task ID + bytes per session. Aggregator script computes per-file/per-skill read-frequency. Render heat overlay on factory-map nodes. Feed read-frequency events into .factory/optimize/events/ for claude-optimize consumption. Document the AC-06 interpretation (single-location read via the factory-map artifact) in this task's plans_and_protocols/."
  implementation_notes: "Source: 09_amendments.md §A-4 + the round-3-followup user feedback confirming Cytoscape.js + scripts-as-edges + fold token measurement into FU-7. The 'larger box' (promoting scripts to first-class nodes with their own contracts) is deferred to Wave-3+ refinement."

- task_name: "Explore: external-interface contracts for factory boundary (E1–E9)"
  bundle_id: FU-8
  req_path: "requirements_tasks/process/AI_rules/factory_quality/requirements.md"
  requirements_version: "b10665f5"
  covers_acs: [AC-01, AC-02, AC-04]
  effort: M
  layer: factory_boundary
  after: []
  task_type: explore
  opus_recommended: true
  scope_description: "Per 07_external_interfaces.md. Inventory factory-boundary interfaces (developer questions, product intake, web research, OS installs, dependency admission, code release, optimize events; check for missed channels). For each: declare a contract using the internal format. Define the external-state postcondition vocabulary (command_exited_zero, url_returned_2xx, file_exists_at_path, developer_responded, package_installed_at_version). Identify additive fields the internal format may need to absorb (input_modality:). Produce 6-10 small validator scripts implementing the vocabulary. Determine: should external-interface declarations live in a sibling REQ-PROC-NEW or fold under REQ-PROC-044? Decide and route via product-intake if a new requirement is needed."
  implementation_notes: "Source: 07_external_interfaces.md. Compatibility check confirms zero rework risk on internal mechanism. The explore deliverable: synthesis + concrete declarations for ≥3 external interfaces + vocabulary draft + recommendation on REQ home."

## Coverage Matrix

| AC | Task(s) | Notes |
|----|---------|-------|
| AC-01 (skill has documented reachable output, no silent failure) | FU-1, FU-2, FU-3, FU-5, FU-8 | Declaration leg lands in Waves 1-3; SCRIBBLE-SPLIT validates on a real refactor; FU-8 extends to external boundaries |
| AC-02 (artifact pipeline traceable end-to-end) | FU-1, FU-2, FU-4, FU-7, FU-8 | Traceability via contract.yaml graph; factory-map renders it; revision channel + external interfaces close the loop |
| AC-03 (new task type / artifact / skill added without unrelated modifications) | FU-1, FU-2, FU-3, FU-5, FU-6 | contract_version: 0 opt-out + schema referencing + rubric guidance |
| AC-04 (malformed/missing input → visible warning or graceful stop) | FU-1, FU-2, FU-4, FU-8 | Verification leg lands in Wave 2 runtime pre-checks; revision channel handles cross-skill drift |
| AC-05 (LLM non-determinism isolated; deterministic steps reproducible) | (covered by mechanism design itself; no separate task) | Lint, schemas, pre-checks are 100% deterministic; contract.yaml is human-authored frozen artifact |
| AC-06 (active skills + artifact dependencies + ordering documented in single authoritative location) | FU-3, FU-7 | Per-dimension authoritative location + factory-map render produces the single readable artifact |

AC-05 is satisfied by the mechanism's nature (no LLM-runtime-generated contract), so no separate task is needed — this is documented in 05_round_3_synthesis.md §D-6.

## Verification

8 impl/explore tasks (> 3 threshold) → a dedicated verification task SHOULD exist per task-derive-from-requ Phase 3 rule. **Folded into FU-3's completion criteria**: when Wave 3 completes (60-day sunset has fired), the lint + render script + pre-checks together act as the verification — every skill has a contract, every contract validates, the factory-map renders the full graph. The FU-3 task explicitly enumerates these final-state checks as ACs. A separate verification task would be redundant overhead given the mechanism is self-verifying at full migration.

(If the user disagrees with this folding, a 9th task `FU-Verify: confirm REQ-PROC-044 AC-01..AC-06 hold after FU-1..FU-7 land` can be added trivially.)

## Sequencing summary

```
FU-1 ──► FU-2 ──► FU-3 ──► FU-5 (SCRIBBLE-SPLIT)
   └──► FU-7 (factory-map + token-measurement)
FU-4 (revision channel) — parallel
FU-6 (rubric codification) — parallel
FU-8 (external interfaces explore) — parallel
```

All 8 tasks go into `.claude/task_ordering_priority_override.txt` to outrank the 0.0.1 release work (per file 12 §7 total-cost decision + file 08 confirmation that the full migration completes before scribble work resumes which in turn blocks 0.0.1).
