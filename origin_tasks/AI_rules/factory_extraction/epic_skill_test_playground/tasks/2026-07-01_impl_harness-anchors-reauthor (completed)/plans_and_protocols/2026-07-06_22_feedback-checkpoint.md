---
skill: task-start
mode: automated
decision: ""
task_id: TASK-PROC-068-11
captured_at: 2026-07-06
---

# Question

---
task_id: TASK-PROC-068-11
session_id: ec060365-1ed5-4d49-98ce-cce64740eaf8
account: web
status: awaiting_answer
asked_at: 2026-07-06T12:28:51Z
skill: task-start
---

# Pending Question

Full details in: `plans_and_protocols/2026-07-06_19_protocol_resume-reconcile-and-park-venue-decision.md`
(and the gating decision in `2026-07-06_20_protocol_reset-to-pending-gated-on-041-06.md`).

The task's gate (`TASK-PROC-041-06-05`, delegated-LLM-work fix) is now verified complete. This
re-surfaces the same venue/cost decision from protocol 19, unchanged, now that the gate is satisfied:

**A)** Run the contained re-derivation now, **automated/unobserved** (harvest → reset self-approval to
draft → park for AC-4 review); OR

**B)** Hand off to an **interactive** session so you watch the "live test"
(`/autorun stop` then `/autorun-resume-interactive TASK-PROC-068-11`); OR

**C)** Skip re-derivation — proceed straight to AC-4 review on the current 066-13-corrected (shallow)
anchors as-is.

Please answer with `A`, `B`, or `C`.

# Developer Answer

Answer: A

Run the contained re-derivation now, automated/unobserved (harvest → reset self-approval to
draft → park for AC-4 review).

Additional directive: persona folders shall be named after the persona's real human name
(snake_case), not the role/archetype label. Rename `personas/archivist/` → `personas/theo/`
and `personas/quick_logger/` → `personas/maya/` (update the corresponding `scenarios/`
subfolders and any cross-references/paths, e.g. in SCENARIO_INDEX.md and each persona's
"Related Scenarios" links). This applies going forward for this harness re-derivation and
any future persona authoring in this task.

# Rationale Captured

(Automated archival — no rationale extracted.)
