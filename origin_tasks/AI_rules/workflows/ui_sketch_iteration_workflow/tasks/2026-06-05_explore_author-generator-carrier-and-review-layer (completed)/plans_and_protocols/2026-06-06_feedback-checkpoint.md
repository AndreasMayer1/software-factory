---
skill: requ-explore
mode: automated
decision: ""
task_id: TASK-PROC-032-31
captured_at: 2026-06-06
---

# Question

---
task_id: TASK-PROC-032-31
session_id: 3faa5909-94d8-469a-8ef0-ec85c62cf326
account: web
status: awaiting_answer
asked_at: 2026-06-05T16:52:40Z
skill: requ-explore
---

# Pending Question — Approve REQ-PROC-032 carrier-format & review-layer synthesis

## What was authored

This task (`requ-explore`, manifest row **T-A3**) authored the dual-audience artifact
contract for the scribble generator into
`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`
(REQ-PROC-032, `status: active` retained). Seven new acceptance criteria (**AC-56 … AC-62**)
plus one new body section **SEC-19 — "Scribble Carrier Format and Human Review Layer"**,
with targeted reference-only appends to AC-22 / AC-27 / AC-29. No code touched; this is a
process/factory requirement, so its ACs are unassigned for package purposes (impl lands via
manifest T-C15 on the `ui-scribble-generator` agent + overlay script, routed through
`task_ordering_priority_override.txt`).

### The new ACs

- **AC-56** — Flat un-nestable JSON `<script type="application/json" id="review-data">`
  carrier renders nothing; the R2§1 comment-nesting leak is *structurally impossible*
  (no nesting construct to break), not merely avoided. No scribble carries multi-line
  reviewer/coder detail in an HTML comment block.
- **AC-57** — That JSON carrier is the **single** dual-audience source: one block read by both
  the findings-overlay script and the coder/LLM, with no second copy on the screen. Schema
  holds, per screen/element: component mapping (HTML→Flutter widget), accessibility intent,
  the AC-27 rule-application trace, and per-element reviewer detail (critique + locked-in /
  re-derive framing).
- **AC-58** — Visible human review layer (PROP-1), distinct from the machine carrier and
  **derived from it** (script-rendered, not separately authored).
- **AC-59** — Script-rendered findings overlay (PROP-13C): count badge + per-element markers
  + gate prompt.
- **AC-60** — Per-reviewer findings persisted & attributable (PROP-4), surviving across
  versions.
- **AC-61** — One reusable, authored-once review-guide component under
  `requirements_tasks/_scribble_components/`, referenced not regenerated (PROP-3).
- **AC-62** — Script-generated small-multiples state variants from one source, no full-copy
  drift, per-state semantics retained (PROP-5).

### The carrier decision (the core fix)

The previous carrier wrapped reviewer detail in one large `<!-- … -->` block and emitted
inline `<!-- a11y-intent: … -->` comments inside it. Because HTML comments cannot nest, the
parser closed the outer block at the first inner `-->` and leaked the remainder as visible
wall-of-text (R2§1, grounded on `02_handover_send.{tablet,desktop}.html`). The fix replaces
this with a single flat `<script type="application/json">` block: it renders nothing (no leak
possible) and has no nesting construct (the defect is impossible, not just avoided). One
carrier, two audiences, zero leak — and it is what makes the PROP-1 human layer implementable
in the same change.

## What needs your decision

Three design choices were made among defensible alternatives — please confirm or redirect:

1. **AC-58 — human layer derived vs. authored.** Chosen: the human review layer is
   *script-rendered/derived from* the JSON carrier (single source, prevents drift).
   Alternative: a separately authored prose panel (richer wording, but can drift from the
   machine block). **Keep derived, or switch to authored?**

2. **AC-60 — persistence locus.** Chosen: each reviewer's raw findings persist to a
   *per-reviewer file in the scribble task's `plans_and_protocols/`* (matches PROP-4's literal
   text + the file-based-memory rule). Alternatives: a `scribble_metadata.yaml` field, or a
   file in the version folder (`scribbles/v{n}/`). **Keep plans_and_protocols/, or relocate?**

3. **AC-62 — PROP-5 feasibility.** The R1 substrate flagged script-generating state variants
   *without losing per-state semantics* as **uncertain**. The AC encodes only the end-state
   property; the mechanism is unproven and is an impl risk for T-C15 (not a requirement gap).
   **Accept AC-62 as written (risk acknowledged), or soften/defer it?**

## What I need to proceed

Per the goal's ACs, I need (a) your approval of this synthesis (with answers to the three
decisions above, or "all as-written"), and (b) the **next action** you want performed — most
likely: run `task-derive-from-requ` on REQ-PROC-032 to derive **T-C15** (generator agent +
`.contract.yaml` + overlay script), appending the derived tasks to
`.claude/task_ordering_priority_override.txt` per the goal's developer directive. Confirm that,
or state a different next step.

# Developer Answer

- 58: Keep derived
- 60: Keep plans_and_protocols/
- Accept AC-62 as written

approved

---
## ⚠ STRUCTURE CHANGE — developer-authorized (2026-06-06)

REQ-PROC-032 was restructured into an EPIC + 7 child FEATURES (zero specification change; all AC/section
text migrated byte-exact and independently verified). The ACs you authored now live in feature **REQ-PROC-032-06** (`feat_carrier_and_auto_review/`). Your authored ACs AC-56→AC-02, AC-57..62→AC-03..08.

AUTHORING COMPLETE — your deliverable (carrier + human-review-layer ACs) is done. Do NOT run
task-derive-from-requ on F06 yourself: F06 is fused (carrier + auto-review) and is derived ONCE by the
dedicated task **TASK-PROC-032-06-01** (derive-F06), gated after this task and TASK-PROC-032-32.
CONTINUE against the FEATURE, not the epic (the epic is non-implementable).

DEVELOPER DIRECTIVE: every task you create via task-derive-from-requ MUST be appended to
`.claude/task_ordering_priority_override.txt` (process tasks carry no target_package and won't
surface in next_tasks.py otherwise).

Crosswalk + restructure record:
requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-06-06_impl_restructure-req-proc-032-into-epic/plans_and_protocols/

# Rationale Captured

(Automated archival — no rationale extracted.)
