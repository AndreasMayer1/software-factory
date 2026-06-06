---
task_id: TASK-PROC-055-04
type: impl
parent_requirement: REQ-PROC-055
urgency: 2
urgency_reason: U2-OPP
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T08:53:54Z
effort: M
created: 2026-05-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Selective-pilot one self-contained han specialist agent as a frozen, renamed copy with MIT attribution"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 3053f73c
  file: ../requirements.md
session_id: eb85c956-4759-42cd-a6b6-7d4b03517471
session_account: web

---
# Goal: Pilot One Self-Contained han Specialist Agent (Frozen Copy)

## Objective

Selectively adopt (copy + adapt + freeze) **one** self-contained, project-agnostic han band-F specialist agent to test whether a dedicated specialist lens measurably improves our outputs. Our 6 broad agents have no adversarial / gap-analysis lens.

**Agent choice** (decide during the task): `adversarial-validator` (challenges a plan/finding by searching for counter-evidence) or `gap-analyzer` (compares any current-state artifact against a desired-state artifact using a Missing/Partial/Divergent/Implicit taxonomy). The synthesis report leans toward `adversarial-validator` as the top pilot candidate.

This is the one *selective-copy* exception to the otherwise inspirational-first posture (user-approved). It must follow REQ-PROC-055 OR-3/OR-4/OR-5 exactly.

## Requirements Summary

Governed by REQ-PROC-055 (External Tooling & Plugin Adoption) — OR-3 (attribution/provenance), OR-4 (frozen + collision-free), OR-5 (re-test). Source: TASK-PROC-055-01.

For full context, read:
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_05_synthesis_decision_report.md` (sections 3.2, 4 "Selective", 5 item 5)
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_02_gather_han_agents.md` (the chosen agent's row + standout notes)
- Web research file `..._03_gather_web_research.md` (Q3 cherry-picking gotchas, Q4 MIT attribution)

Source files (fetch the snapshot, record the commit SHA):
`https://raw.githubusercontent.com/testdouble/han/main/plugin/agents/<agent>.md`

Current requirements: ../requirements.md

## Scope

### In Scope
- Copy ONE han agent file into `.claude/agents/`, adapt it to our conventions, and **rename** it to avoid any collision with built-in or existing agent names (OR-4).
- Verify the chosen agent has NO dependency on an un-copied han skill (pick a self-contained agent; OR-4 bundle rule).
- Set its `model:` per han's cognitive-profile guidance (likely sonnet).
- Create a root-level `THIRD_PARTY_NOTICES.md` recording: source (han), MIT license text, "Copyright 2026 Test Double, Inc.", the source commit SHA copied from, and the adapted file(s) (OR-3).
- Wire the agent as an **optional**, explicitly-invoked step in `code-complex` (not always-on); edit that skill via `claude-modify-skill`.
- Pilot it on 1–2 representative tasks and record in the protocol whether the lens added signal (OR-5 + OR-6).

### Out of Scope
- Copying any han *skill* (collision risk with built-in `/code-review` etc. — avoid).
- Copying more than one agent in this pilot.
- Wiring the agent to track upstream (it is a frozen snapshot).

## Acceptance Criteria

- [x] Exactly one self-contained han agent is present in `.claude/agents/`, adapted and renamed to avoid collisions (OR-4).
- [x] `THIRD_PARTY_NOTICES.md` exists at repo root with source, MIT text, copyright, source commit SHA, and adapted-file list (OR-3).
- [x] The agent is an optional, explicitly-invoked step in `code-complex` (edited via `claude-modify-skill`); it is not always-on.
- [x] The pilot was run on ≥1 representative task and the protocol records whether the lens measurably improved output (OR-5 re-test + OR-6 recorded decision).
- [x] No upstream-tracking wiring exists; the copy is a frozen snapshot.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

The third of three follow-ups from the han evaluation, and the only selective-copy item (user-approved). Applies REQ-PROC-055's policy rather than covering a section, so `covers` is intentionally empty. If the pilot shows no signal, the reversible exit is: remove the agent file, the THIRD_PARTY_NOTICES entry, and the optional code-complex step.

**Scribble skill inspiration (TASK-PROC-032-09 depends on this)**

The adversarial-validator or gap-analyzer agent is a strong candidate for Phase 2 of
the `ui-create-scribble` skill, specifically as a challenger for:

- **Impossible system states**: the agent challenges each state panel by asking "what
  information does the app side have? Does the rendered state require information the
  channel model says is unavailable?"
- **Flow coverage gaps**: the agent compares the screens generated against the flow
  steps and exception paths using the Missing/Partial/Divergent/Implicit taxonomy.

If the pilot is wired into `code-complex` as an optional step and shows measurable
signal (OR-5), the same agent can be wired optionally into Phase 2 of the scribble
skill. This is only worth doing if the pilot confirmed signal — don't add the wiring
speculatively.

When running the pilot on representative tasks, consider including a scribble Phase 2
auto-review as one of the test cases (if available). Record in your protocol whether
the adversarial lens caught anything the current Phase 2 rubric missed. TASK-PROC-032-09
will read your protocol to decide whether to wire the agent into the scribble workflow.
