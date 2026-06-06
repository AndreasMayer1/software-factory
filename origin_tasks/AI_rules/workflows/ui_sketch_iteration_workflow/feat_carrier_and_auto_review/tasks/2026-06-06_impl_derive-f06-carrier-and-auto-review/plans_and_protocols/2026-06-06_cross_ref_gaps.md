# Cross-Reference Completeness Gate — Candidate Gaps

**Target requirement:** REQ-PROC-032-06 (Carrier and Auto-Review)
**Path:** `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_carrier_and_auto_review/requirements.md`
**Current cross-refs:** `after: []`, `blocks: []`, no `## Related Requirements` section
**Detection date:** 2026-06-06
**Skill:** task-derive-from-requ (Phase 1.5)

## Context for classification

REQ-PROC-032-06 is one of 7 features under the REQ-PROC-032 epic, produced by the
restructure TASK-PROC-032-34 ("zero spec change, verified"). **All four sibling
features inspected (032-01, 032-02, 032-03, 032-05) carry `after: []`, `blocks: []`
and no `## Related Requirements` section** — i.e. the restructure deliberately did
NOT wire sibling-to-sibling cross-refs; the epic relationship is captured structurally
(epic → features), not per-feature.

Two detection runs:
- Auto-derived terms (`readers`, `coder`) → broad false positives (generic words).
- Domain terms (`carrier`, `auto-review`, `findings-overlay`, `convergence`) → table below.

## Candidate gaps (domain-term run) with recommended classification

| REQ-ID | Title / area | Matched terms | Recommendation | Rationale |
|--------|-------------|---------------|----------------|-----------|
| REQ-FUNC-014-03 | Questionnaire editor | `carrier` | `ignore` | Coincidental — "framing carrier for Open questions", unrelated domain. |
| REQ-PROC-004 | Interactive brainstorming | `convergence` | `ignore` | Coincidental — "converge too quickly" in brainstorming, unrelated. |
| REQ-PROC-032 | Parent epic | `carrier` | `ignore` | Parent epic; relationship is structural (epic→feature), not a cross-ref edge. Consistent with sibling convention. |
| REQ-PROC-032-01 | feat_scribble_core_artifact (sibling) | `auto-review` | `ignore` | Sibling under same epic; epic convention = no sibling cross-refs. Match is a generic mention. |
| REQ-PROC-032-02 | feat_iteration_and_rule_protocol (sibling) | `auto-review` | `ignore` (or `semantic`) | Sibling; the auto-review control model defined here is consumed by the iteration protocol. Per epic convention → ignore; flag if you want the consumer link recorded. |
| REQ-PROC-032-03 | feat_handoff_skills_and_contract (sibling) | `auto-review`, `carrier`, `convergence` | **`semantic` (decision needed)** | This requirement's BODY explicitly references "the REQ-PROC-032-03 AC-11 trace, now carried in this block" and the Scribble–Coder Contract. A genuine semantic link — but no sibling currently cross-refs. Confirm whether to record it as Related despite the epic convention. |
| REQ-PROC-032-05 | feat_consistency_sci_layer (sibling) | `auto-review`, `convergence` | `ignore` (or `semantic`) | Sibling; references "L4 auto-review non-convergence" (defined here in AC-01). Per epic convention → ignore; flag if you want the link recorded. |
| REQ-PROC-045 | requirements_structure_quality | `carrier` | `ignore` | Coincidental generic word. |
| REQ-PROC-068-01 | Home Dashboard (different epic) | `carrier` | `ignore` | Coincidental generic word; unrelated epic (factory_extraction). |

## Key decision

The only non-trivial call is **REQ-PROC-032-03**: it is genuinely referenced in the
body, but the verified epic restructure left siblings without cross-refs. Either:
- **(A) all `ignore`** — honour the established epic convention (siblings carry no
  cross-refs; the epic captures the relationship). Recommended for consistency with
  the "zero spec change, verified" restructure.
- **(B) mark 032-03 (and optionally 032-02, 032-05) `semantic`** — add a
  `## Related Requirements` section recording the genuine semantic links, accepting
  divergence from the sibling convention.
