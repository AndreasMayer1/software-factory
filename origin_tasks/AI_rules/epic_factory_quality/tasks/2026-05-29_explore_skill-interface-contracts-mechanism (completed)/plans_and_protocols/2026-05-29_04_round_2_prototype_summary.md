# Round 2 Prototype Summary

**Task:** TASK-PROC-044-02 · **Date:** 2026-05-29 · **Model:** Sonnet 4.6
**Agent:** abde60c41c38951a7

---

## What was built (one bullet per file)

- **`contract_ui-create-scribble.yaml`** — Contract for the catalyst skill: 4 required inputs (requirements.md marked `source: external`, personas, T1/T2 rules, concept_canon), 5 optional inputs (flow.md, implementation_notes, 2 developer-provided image seeds marked `source: external`, prior scribble version), 4 required outputs (index.html, screen HTML files, metadata.yaml, feedback.md) + 2 conditional outputs (flutter_handoff.yaml on approval, scribble_index.html when flow exists), side_effects (supersedes prior version, auto-promotion to _scribble_components), may_invoke: requ-explore, doc-update-guidelines, ux-validate-rule, ux-write-canon-concept.

- **`contract_code-simple.yaml`** — Contract for the primary implementer skill: goal.md required (annotated `source: skill:task-create`), doc/ guidelines required, conditional scribble folder input (Sketch Gate), lib/ + test/ as required outputs, lookup_log.jsonl as required output, may_invoke: task-create, ui-create-scribble, verify-quality, task-complete, doc-update-guidelines, doc-lookup-dependencies, doc-update-tokens.

- **`contract_task-create.yaml`** — Contract for the primary goal.md PRODUCER: requirements.md required (`source: external`), id_registry.md required (`source: external`), produces goal.md (references goal_metadata schema) and plans_and_protocols/ directory as required outputs; cascade_log.md and user_initial_input.md as conditional outputs; side_effects: atomic reserve markers, id_registry regeneration; may_invoke: requ-explore, task-derive-from-requ.

- **`schema_scribble_metadata.yaml`** — Schema for scribble metadata.yaml: status enum `[draft, reviewed, approved, superseded, stale]`, 4 required fields, 9 optional fields; includes migration note listing which SKETCHES_README.md sections this schema replaces (not deleted yet — rollout task responsibility).

- **`schema_goal_metadata.yaml`** — Schema for goal.md YAML frontmatter: 5 required fields (task_id, type, parent_requirement, status, created) with type enum `[explore, impl, define, review, analyze, bugfix]` and status enum `[pending, in_progress, completed, blocked]`; 22 optional fields covering all goal.md frontmatter keys found in the codebase.

- **`check_skill_contracts.py`** — Lint script, 76 code lines (under 80-line cap), tier B, no external deps beyond PyYAML. Two checks: (1) derived_from cross-reference against produces (with folder-level matching), (2) may_invoke existence check against .claude/skills/. Bypass mechanism: `source: external` for developer-owned inputs, `source: skill:<name>` for declared cross-references. `--prototypes-dir` flag for prototype folder use.

- **`lint_demo_run.md`** — Full demo with verbatim command outputs: clean pass (exit 0), injected violation (`scribbles/v{n}/` renamed to `prototypes_test_violation_scribbles/iteration_{n}/`), violation output (exit 1, specific error quoting the exact path), revert, re-verify (exit 0).

- **`example_revision_target.yaml`** — Demo revision_target.yaml at hypothetical `automation/pending_feedback/TASK-FUNC-007-15/revision_target.yaml`: originator ui-verify-flutter → target_skill ui-create-scribble, reason: structural, `responder_required: skill`, detail quoting exact component mismatch ([NavigationBar] vs [TabBar]), cycle_count for 5-cycle escalation.

- **`README.md`** — Index listing all 8 files with one-line descriptions, production locations for rollout, key design decisions demonstrated.

---

## What the lint catches and how

The lint performs two cross-reference checks:

**Check 1 — derived_from vs produces (the main value):**
For every path in a skill's `derived_from.required` or `derived_from.optional`, it verifies that some skill's `produces.required` or `produces.conditional` declares the same path. Matching is both exact (full path) and folder-level (a skill consuming `scribbles/v{n}/` matches a producer that declares `scribbles/v{n}/index.html`). Items with `source: external` or `source: skill:*` bypass the check.

**Demo output — violation caught:**
```
FAIL — 1 contract violation(s):
  - contract_code-simple.yaml derived_from[optional] 'requirements_tasks/<feature>/prototypes_test_violation_scribbles/iteration_{n}/' — no producer declares this path and it is not a known external source. Add it to a producing skill's produces: block.
```
This is the exact format specified in web research file 02 §Q5: actionable, quotes the string, names the file and section, tells the author what to do.

**Check 2 — may_invoke existence:**
For every skill name in `may_invoke:`, checks `.claude/skills/<name>/SKILL.md` exists. Catches misspellings before rollout.

---

## Discoveries during prototyping that should inform Round 3

1. **The `source:` annotation is a required addition to the contract format.** The original 4-field PRINCE2 design from file 02 §Q4 did not have it. Without distinguishing "developer-owned external inputs" from "skill outputs" in `derived_from`, the cross-reference check produces ~10 false positives on the 3 prototype contracts alone (requirements.md files, id_registry.md, RELEASE_BACKLOG.md, developer-provided image seeds). The annotation must be part of the canonical contract format in Round 3. Two values are sufficient: `external` (developer-owned) and `skill:<name>` (declared producer). Undeclared = lint-checked.

2. **Folder-level path matching is non-trivial but necessary.** Skills that consume a *folder* of outputs (e.g. `scribbles/v{n}/`) need folder-to-file matching against producers that declare individual files in that folder. The `_folder()` normalization function handles this but introduces a subtle ambiguity: `v{n}/` matches any file under any `v{n}/` folder. Round 3 should specify whether path templates use a canonical glob syntax or stick to the current freeform `{n}` notation.

3. **The `iteration_{n}` normalization in `_norm()` directly implements Scenario A from Round 1 §2.** The lint normalizes both sides before comparison, so a rename from `v{n}` to `iteration_{n}` IS caught (the injected violation demonstrates this). This validation is working as designed.

4. **`side_effects:` field needs an enum for the `write` action.** During authoring, `write` was used consistently, but other reasonable values could be `delete`, `append`, `regenerate`. Without an enum, contracts may diverge. Recommend: `action: write | append | delete | regenerate` sub-field within each side_effect entry.

5. **`source: skill:task-create` in code-simple's goal.md entry is declared but not verified by the lint.** The lint skips `skill:` annotated items entirely rather than checking that the named skill's produces block actually declares the path. This is a deliberate PoC simplification — full verification would require the named-producer lookup. Round 3 should decide: (a) add named-producer verification, or (b) accept that `skill:` annotations are trusted declarations checked only at code review.

6. **The `may_invoke` check found all referenced skills exist (passing on the real `.claude/skills/` tree).** Skills referenced: requ-explore, doc-update-guidelines, ux-validate-rule, ux-write-canon-concept, task-create, ui-create-scribble, verify-quality, task-complete, doc-update-tokens, doc-lookup-dependencies, task-derive-from-requ. All resolve. This validates that the 3 prototype contracts are internally consistent with the actual factory skill tree.

7. **schema_scribble_metadata.yaml uses a YAML-dialect schema, not JSON Schema.** The format is readable and covers required/optional split, enums, and descriptions — but it is NOT machine-executable (no `jsonschema` library validates it). Round 3 should decide: stay with human-readable YAML dialect (lower authoring cost, less rigidity) vs full JSON Schema (tooling support but higher verbosity). Given the project's token budget, the YAML dialect is recommended — it serves as documentation and a lint-augmented check, not a runtime validator.

---

## Honest list of what the prototype could NOT validate

- **Cross-skill consistency requires more skills migrated.** With 3 of 60 skills having contracts, the `derived_from` check only catches paths that happen to be in the prototype set. A real migration would need at least the `ui-*`, `code-*`, and `task-*` families contracted before the cross-reference graph becomes useful.

- **Runtime pre-condition checks were not prototyped.** File 02 §Q1 and Round 1 §1.1 both argue that the lint is necessary but not sufficient — the "5-line bash pre-check" at consumer skill entry is the load-bearing verification step (PwC 7× argument). No runtime guard was written in this round. Round 3 must specify the runtime check pattern.

- **Schema validation of actual metadata.yaml files was not implemented.** The `schema_scribble_metadata.yaml` file is human-readable spec, not an executable validator. Checking whether existing scribble metadata.yaml files conform to the schema requires a second script or an augmented lint step.

- **The `source: external` bypass is trust-based.** The lint cannot verify that a `source: external` annotation is honest. A skill author could mark a cross-skill dependency as `external` to silence a violation. Code review is the only check.

- **Path template ambiguity.** The `{n}`, `<feature>`, `<task>` template placeholders work for human reading but are opaque to automated tooling. If a future migration wants to generate contracts from skill execution traces, the template syntax needs formalization.

---

Agent ID: abde60c41c38951a7
