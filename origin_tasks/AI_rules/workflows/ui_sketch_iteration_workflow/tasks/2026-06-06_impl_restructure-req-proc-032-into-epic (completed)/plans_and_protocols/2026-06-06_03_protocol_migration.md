---
skills_used: []
---

# Protocol — REQ-PROC-032 Migration (Phase 1: Epic + Feature File Creation)

**Task:** TASK-PROC-032-34  
**Date:** 2026-06-06  
**Agent ID:** `a5adc94ec36b9d188`  
**Phase:** 1 of N (this phase: create epic + 7 feature files; verify byte-exact fidelity)

---

## Summary

Phase 1 is complete. The epic `REQ-PROC-032` has been restructured into an epic
shell plus 7 child feature `requirements.md` files. All 70 ACs and 21 SECs were
migrated with **zero specification drift** — confirmed by the verification harness.

---

## Files Created

### Feature requirements.md files (7)
| Feature folder | REQ-ID | ACs | SECs |
|---|---|---|---|
| `feat_scribble_core_artifact/requirements.md` | REQ-PROC-032-01 | 5 | 5 |
| `feat_iteration_and_rule_protocol/requirements.md` | REQ-PROC-032-02 | 4 | 5 |
| `feat_handoff_skills_and_contract/requirements.md` | REQ-PROC-032-03 | 17 | 3 |
| `feat_scribble_content_extensions/requirements.md` | REQ-PROC-032-04 | 14 | 4 |
| `feat_consistency_sci_layer/requirements.md` | REQ-PROC-032-05 | 14 | 1 |
| `feat_carrier_and_auto_review/requirements.md` | REQ-PROC-032-06 | 12 | 2 |
| `feat_embedded_flow_viewer/requirements.md` | REQ-PROC-032-07 | 4 | 1 |

**Total ACs distributed: 70 (sums to 70: 5+4+17+14+14+12+4)**

### Epic shell rewritten
- `ui_sketch_iteration_workflow/requirements.md` — `id: REQ-PROC-032`, `trackable_items.acceptance_criteria: []`, `trackable_items.sections: []`; body retains Background and Motivation (SEC-01), new `## Features` index, Related Requirements, Version History.

### Task-local tooling (plans_and_protocols/ only, not under scripts/)
- `plans_and_protocols/migrate.py` — migration script (byte-exact copy via yaml.safe_load + yaml.dump round-trip; no LLM in copy path)
- `plans_and_protocols/verify.py` — verification harness (4 checks)
- `plans_and_protocols/crosswalk.yaml` — 70-row `old→new` AC mapping

---

## Reserve Markers Deleted

All 7 `.reserve-REQ-PROC-032-0N` markers deleted from the epic folder:
- `.reserve-REQ-PROC-032-01` through `.reserve-REQ-PROC-032-07`

---

## Harness Command

```bash
python3 requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-06-06_impl_restructure-req-proc-032-into-epic/plans_and_protocols/verify.py
```

---

## Final Harness Output (verbatim PASS — empty diff on all four checks)

```
=== REQ-PROC-032 Migration Verification Harness ===

Golden ACs: 70
Golden SECs in FM: 21
Golden body sections: 18

Crosswalk rows: 70

--- Check 1: AC fidelity ---
  PASS: all 70 AC names and descriptions are byte-identical to golden

--- Check 2: Bijective crosswalk ---
  PASS: crosswalk is bijective (70 rows, each old AC exactly once, new ids gapless)

--- Check 3: Section fidelity ---
  PASS: all 18 body sections are byte-identical; 3 empty sections present in FM only

--- Check 4: Epic body fidelity ---
  PASS: epic Background, Related Requirements, Version History are byte-identical to golden

=== RESULT: ALL CHECKS PASS — empty diff on all four checks ===
```

---

## Judgment Calls

1. **AC title in feature body**: Each feature `requirements.md` body starts with a `# <Feature Title>` heading derived from the folder name. This is a new addition not in the golden file — it is NOT content from the golden; it is navigation scaffolding. The harness does not check the body title (only SEC headings and epic-retained sections). This is acceptable per scope.

2. **`effort: M` comment on feature files**: Frontmatter field `effort: M` carries an inline comment `# review-later: sized as metadata placeholder` as specified in `decisions_locked.md`. This is not a copy from golden (the golden has `effort: XL`); it is metadata set per spec.

3. **`market_research_refs: []`**: Golden has `market_research_refs: [] # No relevant findings identified`. PyYAML round-trips this as just `market_research_refs: []` (comment stripped). This is acceptable — comments are not preserved by YAML parsers and are not part of the AC/SEC fidelity check.

4. **`created` date preserved as string**: The golden `created: 2026-02-28` is preserved verbatim in all feature files.

5. **SEC-01 body on epic**: The epic retains `## Background and Motivation` (SEC-01) byte-exact. This is correct per `decisions_locked.md` ("Epic intro / Background and Motivation → stays on the epic"). The epic body also has SEC-01 in the body even though the epic's `trackable_items.sections: []` — this is intentional: the intro is non-trackable boilerplate on the epic.

6. **F03 folder name `feat_handoff_skills_and_contract`**: Used the decisions_locked.md name (not the seam-map's original `feat_handoff_three_skill_and_contract`). This is the locked decision.

---

## Remaining Phases (not started here per scope)

- Phase 2: Reference rewrite across 22 AC-citing files + implementation-task-manifest
- Phase 3: Regenerate generated artifacts (requirements.md merge, id_registry, STATUS)
- Phase 4: Retarget 4 in-flight tasks (TASK-PROC-032-30/31/32/33) via pending_feedback answer.md
- Phase 5: Developer approval + orchestrator resume

---

## 2026-06-06T12:20 — Phase 1 Complete

**Agent**: implementation-engineer  
**Agent ID**: a5adc94ec36b9d188  
**Action**: Created epic shell (REQ-PROC-032) + 7 feature requirements.md files; wrote task-local migration script (migrate.py) and verification harness (verify.py); deleted all 7 reserve markers; produced crosswalk.yaml (70 rows).  
**Outcome**: PASS — verification harness exits 0, all 4 checks pass, empty diff on all checks. 70 ACs distributed (5+4+17+14+14+12+4=70). 21 SECs assigned exactly once. No specification drift.  
**Next Step**: Phase 2 — reference rewrite across 22 AC-citing files + implementation-task-manifest (separate agent/session; requires developer go-ahead).
