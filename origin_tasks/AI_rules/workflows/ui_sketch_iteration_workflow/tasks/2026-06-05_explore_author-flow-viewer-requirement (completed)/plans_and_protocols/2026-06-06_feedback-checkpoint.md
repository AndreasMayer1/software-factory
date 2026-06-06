---
skill: requ-explore
mode: automated
decision: ""
task_id: TASK-PROC-032-33
captured_at: 2026-06-06
---

# Question

---
task_id: TASK-PROC-032-33
session_id: e952d1cd-002f-4016-909c-0b570393983c
account: web
status: awaiting_answer
asked_at: 2026-06-05T00:00:00Z
skill: requ-explore
---

# Pending Question

## Task
TASK-PROC-032-33 — Author the Flow-Viewer Requirement (PROP-14, REQ-PROC-032 + REQ-PROC-060)

## What was done

Authored four new ACs (AC-67 through AC-70) and one new section (SEC-21) into REQ-PROC-032
(`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`).

### New AC-67: Embedded flow-viewer sidebar
The scribble's `index.html` contains a "Show User Flows" toggle that opens a sidebar panel; the panel presents one tab per user flow listed in the scribble's `flow_positions` metadata; selecting a tab renders that flow's content inline. When no user flows are associated with the scribble, the toggle is absent.

### New AC-68: Script-driven flow content — no LLM re-emission
Flow content displayed by the flow viewer is sourced by a generator helper script that copies or symlinks the canonical user flow Markdown files into the scribble artifact directory. No LLM agent reads flow source files and re-emits their content as HTML in the scribble. The single normative copy — the canonical flow source — is what the viewer renders.

### New AC-69: Markdown renderer: developer-authorized, client-side vendored, pinned
The flow viewer renders Markdown to HTML using a single pinned, client-side, vendored JavaScript renderer bundled within the scribble artifact directory. The renderer is not added without recorded developer pre-authorization under REQ-PROC-060 AC-01. The recommended approach is a single-file pinned client-side renderer (the `marked`-class of libraries), preferred over a build-step approach because it keeps the scribble artifact self-contained and zero-build. The pinned renderer file is not updated without a fresh REQ-PROC-060 admission evaluation.

### New AC-70: Flow-passage colour-highlighting from flow_positions (conditional)
When the scribble's `flow_positions` metadata names specific step numbers for a flow, the flow viewer highlights the text passages corresponding to those step numbers in a distinct colour. The highlighting is derived mechanically from `flow_positions.step_number` mappings — no LLM re-read of the flow is performed. Passages not mapped to any scribble step are rendered at reduced opacity. When step numbers are absent or no per-step text anchors can be resolved, the viewer renders unhighlighted flow text.

### New Section SEC-21: Embedded Flow-Viewer Sidebar
Body section added to requirements.md with full descriptive prose for all four AC-67..AC-70 properties, including the REQ-PROC-060 gate framing for the renderer decision.

## What remains uncertain

- The specific Markdown renderer library (e.g. `marked.min.js`) is not named in the requirement — this is the developer's admission decision under REQ-PROC-060. AC-69 records the recommendation and the gate but does not self-select the library.
- The exact colour scheme for highlighting (AC-70) is left to the implementation — the requirement specifies the mechanism (distinct colour / reduced opacity) but not the visual values.
- AC-70 depends on `flow_positions` carrying `step_number` with resolvable text anchors — how anchors map to flow-text paragraphs is an implementation detail for T-C18.

## Question

Please review the four ACs and the new section above.

**The dependency decision (D-5):** AC-69 frames this as a REQ-PROC-060 developer-authorized call with the recommendation already recorded (`marked`-class, client-side vendored). No action is required for the requirement itself — but when T-C18 is eventually implemented, the developer will need to explicitly authorize the specific renderer package before it is added.

If you approve:

**Next step options:**
1. Run `task-derive-from-requ` on REQ-PROC-032 to generate the T-C18 impl task (flow viewer script + renderer). The derived task ID must then be appended to `.claude/task_ordering_priority_override.txt` (developer directive 2026-06-05 — no `target_package`, won't surface in `next_tasks.py` otherwise).
2. Or: proceed to the next unblocked task in the queue (T-C18 derivation can happen in a later session).

If you want changes to any AC, specify them in answer.md and the session will resume.

# Developer Answer

approved

---
## ⚠ STRUCTURE CHANGE — developer-authorized (2026-06-06)

REQ-PROC-032 was restructured into an EPIC + 7 child FEATURES (zero specification change; all AC/section
text migrated byte-exact and independently verified). The ACs you authored now live in feature **REQ-PROC-032-07** (`feat_embedded_flow_viewer/`). Your authored ACs AC-67..70 → AC-01..04.

CONTINUE: run `task-derive-from-requ` on `feat_embedded_flow_viewer/requirements.md` — a clean 1:1 with
your flow-viewer slice.
CONTINUE against the FEATURE, not the epic (the epic is non-implementable).

DEVELOPER DIRECTIVE: every task you create via task-derive-from-requ MUST be appended to
`.claude/task_ordering_priority_override.txt` (process tasks carry no target_package and won't
surface in next_tasks.py otherwise).

Crosswalk + restructure record:
requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-06-06_impl_restructure-req-proc-032-into-epic/plans_and_protocols/

# Rationale Captured

(Automated archival — no rationale extracted.)
