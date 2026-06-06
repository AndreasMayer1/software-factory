# Locked Decisions — REQ-PROC-032 Restructure

Authoritative spec for the migration. Read alongside `2026-06-06_01_plan_seam-map.md`
(the seam map provides per-AC/section assignment + the 70-row crosswalk).

## Golden source
- Commit `9a73678c`, blob `cf51a2ba`.
- Read via: `git show 9a73678c:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`
- Working tree currently == golden (verified clean).

## Structure (developer-approved)
- **7 features** (F06 carrier+auto-review stays FUSED).
- Epic keeps ID **REQ-PROC-032** and folder **`ui_sketch_iteration_workflow/`**
  (grandfathered unprefixed epic — NOT renamed; renaming would churn 20 external path refs).
- Features are `feat_*` subfolders inside the epic folder.

## Feature ID + name mapping (suffix order = table order; LOCKED)
| New REQ-ID | Feature folder | ACs owned (original ids) | Sections owned |
|---|---|---|---|
| REQ-PROC-032-01 | `feat_scribble_core_artifact` | (per seam map, 5) | SEC-01..05 |
| REQ-PROC-032-02 | `feat_iteration_and_rule_protocol` | (per seam map, 4) | SEC-06..10 |
| REQ-PROC-032-03 | `feat_handoff_skills_and_contract` | (per seam map, 17) | SEC-11,15,16 |
| REQ-PROC-032-04 | `feat_scribble_content_extensions` | (per seam map, 14) | SEC-12,13,14,17 |
| REQ-PROC-032-05 | `feat_consistency_sci_layer` | (per seam map, 14) | SEC-18 |
| REQ-PROC-032-06 | `feat_carrier_and_auto_review` | (per seam map, 12) | SEC-19,20 |
| REQ-PROC-032-07 | `feat_embedded_flow_viewer` | (per seam map, 4) | SEC-21 |

Reserve markers exist at `<epic>/.reserve-REQ-PROC-032-0N` — delete each marker
after its feature's `requirements.md` is written.

## Naming decision
- F03 name: **`feat_handoff_skills_and_contract`** — the original `..._three_skill_...`
  was renamed to drop the hardcoded count (future-proof; the workflow's skill count may change).

## Empty-section decision (zero-drift)
- SEC-12 / SEC-13 / SEC-14 exist in golden frontmatter `trackable_items.sections`
  but have **no body prose** (golden body has only 18 of 21 SEC headings).
- **Preserve as-is**: keep these three SEC ids in F04's `trackable_items.sections`
  with no body. Do NOT drop them, do NOT invent body text.

## AC numbering
- **Renumber per feature** (each feature restarts AC-01..). The 70-row
  `old (REQ-PROC-032/AC-xx) → new (REQ-PROC-032-0N/AC-yy)` crosswalk in the seam map
  is the load-bearing artifact for the downstream reference rewrite.

## Minor confirmations (developer-approved defaults)
- AC-13 (flutter_handoff.yaml) → **F03**.
- `## Related Requirements` and `## Version History` → stay on the **epic** (not a feature).
- Epic intro / `## Background and Motivation` → stays on the **epic**.

## HARD CONSTRAINT
- **Zero specification drift.** AC `description` text and SEC body prose move byte-exact
  via script (no LLM retyping). Empty normalizing-diff vs golden is the pass condition.
