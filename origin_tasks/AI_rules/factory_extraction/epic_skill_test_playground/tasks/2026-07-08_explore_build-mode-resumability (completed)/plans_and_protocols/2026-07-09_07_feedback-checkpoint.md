---
skill: ideation-start
mode: automated
decision: ""
task_id: TASK-PROC-068-20
captured_at: 2026-07-09
---

# Question

---
task_id: TASK-PROC-068-20
session_id: f9f98c5d-e1ce-4c6a-a3a5-dbbff842e229
account: gmail2
status: awaiting_answer
asked_at: 2026-07-09T09:10:09Z
skill: ideation-start
---

# Pending Question — Iteration 2 gate: approve the SIMPLER v2 design & confirm next step

Your ITERATE feedback is worked in. Full revised design in:
`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-08_explore_build-mode-resumability/plans_and_protocols/2026-07-09_006_synthesis_v2.md`
(ledger rendered: `…/2026-07-09_001_ideation_ledger.html`).

## What I verified against the code (your claims were right)
- **State location**: `workspace.py` ALREADY puts the playground test-mode workspace in
  `<parent-of-project>/playground_ws_<uuid8>` and git-inits it. `build.py` diverged to `/tmp` (`mkdtemp`) —
  that is the bug. Fix = build.py reuses the existing parent-dir + git-init helpers.
- **Project-environment config already exists**: `worktree_root.py` + `worktree.config.json` (per-developer,
  gitignored, precedence explicit → config → parent-of-repo). Reuse it; no new config surface.
- **No orchestrator modification needed**: `automation/` IS deployed into the copy (inner orchestrator is
  real); `rate_limit_sleep` confirms every orchestrator freezes on all-accounts-limited and resumes after
  reset. The shared window freezes the whole tree together — your "freeze in time" model holds.
- **Autorun stop signal** = `stop_requested` in `automation/state.json` (atomic) — a ready-made pause
  primitive if ever needed.

## The v2 reframe — 3 separated concerns; only ONE is genuinely new work
- **A. Completion-gated harvest** (core safety fix) — UNCHANGED, load-bearing: build.py must not
  harvest+discard unless the inner run signalled complete; else preserve + skip harvest.
- **B. Durable state** — REUSE the parent-dir git-init workspace + `worktree.config.json` (already durable).
- **C. Usage-limit** — NO orchestrator mod: inner+outer orchestrators already freeze-and-resume.
- **D. Explicit external pause** — DEFER (YAGNI): I could not find a use case where the outer run must
  preempt a healthy inner run; usage-limit is fully covered by C. `stop_requested` documented as the
  extension point if a real case appears. **Do you know a preempt use case I'm missing?**

Full inner/outer × task × limit state-space enumeration is in the synthesis (§"Full state-space enumeration").

## Decisions to confirm or override
- **D1** completion policy = preserve + skip-ALL-harvest on any non-complete exit. *[recommend: yes]*
- **D2 (REVISED)** state model = reuse existing parent-dir git-init workspace + `worktree.config.json`
  (no new runs dir). *[recommend: yes]*
- **D3** generalize via an injected completion-predicate seam; implement derivation first. *[recommend: yes]*
- **D4** requirements land in BOTH REQ-PROC-068 and REQ-PROC-071-06. *[recommend: yes]*
- **D5 (NEW)** poll ownership = (a) outer session self-polls a completion file at a DYNAMIC interval for v1,
  with (b) orchestrator-monitored as a documented optimization. *[recommend: (a)]*
- **D6 (NEW)** no explicit external pause in v1 (rely on orchestrator freeze). *[recommend: yes]*

## 1. Approve v2? (APPROVE / ITERATE — if ITERATE, say what changed)

## 2. Confirm the next step on resume (unchanged from iter-1, gated on approval)
1. `requ-explore` → author the resumability ACs into REQ-PROC-068 + REQ-PROC-071-06 (per D4).
2. `task-derive-from-requ` → impl tasks: build.py workspace-reuse + completion-signal-gated harvest + run
   registry + dynamic-poll helper + a **validation task closing U2** (inner autorun completing a real chain
   under a real usage-limit inside the jail — the thing 068-18 never exercised).
3. Unblock TASK-PROC-068-12: `after:` = the new impl-task IDs; re-author How-to-Approach to the build-mode
   resume path; clear `session_id`; clear the interim `awaiting` hold.

Confirm this next step or state a different one.

## Now-central uncertainty
**U2** — the inner autorun completing a real chain (and freezing/resuming under a real shared limit) inside
the jail is UNPROVEN (068-18 used a deterministic child that could not hit a limit). v2 makes proving it a
dedicated validation task before the design is trusted end-to-end.

# Developer Answer

Approved as suggested.

Perform all necessary requirement updates, then derive implementation tasks.

Make sure that you add all cr created tasks to flutter_app/.claude/task_ordering_priority_override.txt

# Rationale Captured

(Automated archival — no rationale extracted.)
