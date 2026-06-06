---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - requ-explore
  - claude-commit
  - task-complete
---

# Protocol — Author the Generator Carrier-Format & Review-Layer Requirement (TASK-PROC-032-31)

- **Agent ID:** afed9edfb7d00269c
- **Date:** 2026-06-05
- **Task:** TASK-PROC-032-31 (manifest handle T-A3) — `requ-explore` authoring only (no task-start / package
  assignment / quality gates / task-complete; those are the orchestrator's).
- **Target:** `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`
  (REQ-PROC-032, `status: active` — kept active).

## Files read

- `tasks/.../2026-06-05_explore_author-generator-carrier-and-review-layer/goal.md` (objective, seeds, manifest pointers)
- `.claude/skills/requ-explore/SKILL.md` (§2.2 YAGNI gate, §2.3 structure / forbidden content / end-state &
  transition-language & abstraction-level tests, §2.5 quality check)
- Synthesis §7 + AC-mapping table: `.../2026-06-04_explore_redesign-implementation-workflow-scribble-gate (completed)/plans_and_protocols/2026-06-04_02_round_1_synthesis.md`
- Manifest rows T-A3 / T-C15: `.../2026-06-05_13_implementation-task-manifest.md`
- Eval substrate: `.../2026-06-04_explore_eval-scribble-workflow-live-iteration (completed)/plans_and_protocols/2026-06-04_04_round_2_evaluation.md` §1 (comment-leak, grounded) and `2026-06-04_02_round_1_evaluation.md` (PROP-1 L244, PROP-3 L269, PROP-4 L281, PROP-5 L290, PROP-13(C) L481/L492)
- Target requirement: frontmatter ACs (AC-01..AC-55), AC-22/27/29, sections list (SEC-01..SEC-18), and body
  sections `## Scribble Format`, `## Scribble–Coder Contract`, `## Scribble Review Doctrine`,
  `## Scribble Content Extensions`, `## Consistency and Scribble-Layer Model`.

## ACs added (AC-56 … AC-62) — all end-state, evidence-cited

- **AC-56** — Flat un-nestable JSON `<script type="application/json" id="review-data">` carrier renders nothing; comment-nesting leak structurally impossible. (R2§1, synthesis §7)
- **AC-57** — JSON carrier is the single dual-audience contract document; schema keys = component mapping, a11y intent, AC-27 rule-audit trace, per-element reviewer detail.
- **AC-58** — Visible human-facing review layer (PROP-1), distinct from + derived from the machine carrier.
- **AC-59** — Script-rendered findings overlay (PROP-13C): count badge + per-element markers + gate prompt, read from the carrier.
- **AC-60** — Per-reviewer findings persisted to `plans_and_protocols/` before merge, attributable, survive across versions (PROP-4).
- **AC-61** — Single reusable, authored-once review-guide component in `requirements_tasks/_scribble_components/`, referenced not regenerated (PROP-3).
- **AC-62** — Script-generated small-multiples state variants from a single source, no full-copy drift, per-state semantics retained (PROP-5).

## Body added

- New section `## Scribble Carrier Format and Human Review Layer` (SEC-19), placed after
  `## Consistency and Scribble-Layer Model`, before `## Related Requirements`. End-state language; PROP-ids and
  R2§1 cited inline.
- SEC-19 added to frontmatter `sections` list.

## Existing-AC text changed (targeted reference additions only — no rewrites)

- **AC-22** — appended: "The per-screen machine-readable detail underlying this dual framing is carried in the
  screen's review-data JSON carrier (AC-56, AC-57); the reviewer-facing framing is surfaced through the
  rendered human review layer (AC-58)."
- **AC-27** — appended: "This trace is carried in the screen's review-data JSON carrier (AC-57)."
- **AC-29** — appended: "The findings this brief draws on are surfaced on the screens through the
  script-rendered findings overlay over the review-data carrier (AC-59), backed by per-reviewer finding
  provenance (AC-60)."

## YAGNI evidence

Every AC is grounded in a substrate proposal or the grounded R2§1 defect (cited inline). No items deferred; no
`## Deferred (YAGNI)` section. Picked the strictly simpler shape: one carrier (not separate machine + human
JSON), human layer *derived from* the carrier (not a parallel authored copy).

## Open uncertainties (for the synthesis-approval gate)

- AC-58 chooses the human layer as **derived from** the carrier (script-rendered) rather than separately
  authored. Defensible alternative: generator authors a parallel human panel. Derived chosen to avoid drift;
  developer may prefer authored for richer prose. **[DECISION]**
- AC-60 persistence locus = per-reviewer file in the scribble task's `plans_and_protocols/`. Alternative: a
  field in `scribble_metadata.yaml` / a dedicated findings file under the version folder. Chosen to match the
  file-based-memory rule and PROP-4's literal text. **[DECISION]**
- AC-61 — left the component's concrete filename unspecified (folder fixed: `_scribble_components/`), per the
  factory-AC abstraction rule (folder pattern permitted, internal file naming is an impl detail for T-C15).
- AC-62 — PROP-5 feasibility ("can a script generate state variants without losing per-state semantics") was
  flagged *uncertain* in R1 §"What remains uncertain". AC-62 states the end state; the feasibility risk is an
  implementation concern for T-C15, not a requirement gap. Flag to developer that this AC encodes a property
  whose mechanism is unproven.

## Package-assignment note

REQ-PROC-032 is **internal process tooling** (the scribble *workflow* itself — agents, scripts, artifact
formats under `requirements_tasks/`). For package-assignment purposes these ACs are unassigned/internal; the
manifest already routes the impl (T-C15) via the `task_ordering_priority_override.txt` mechanism since these
tasks carry no `target_package`.
