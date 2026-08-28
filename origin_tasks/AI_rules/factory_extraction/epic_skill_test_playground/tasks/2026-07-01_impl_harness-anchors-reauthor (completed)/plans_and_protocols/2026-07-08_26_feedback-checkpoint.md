---
skill: task-start
mode: machine_resolution
decision: ""
task_id: TASK-PROC-068-11
captured_at: 2026-07-08
---

# Question

---
task_id: TASK-PROC-068-11
session_id: ec060365-1ed5-4d49-98ce-cce64740eaf8
account: web
status: awaiting_answer
asked_at: 2026-07-06T20:26:28Z
skill: task-start
---

# Pending Question

Full details in: `plans_and_protocols/2026-07-06_25_protocol_redrive-succeeded-park-for-ac4.md`
(run history in protocols 23–24).

Per your answer **A**, the contained re-derivation ran (3rd attempt succeeded after fixing a
non-interactive-approval-gate bug and a harvest-scope bug from the first two attempts — see
protocol 25 for the failure/fix trail). The persona folders are renamed
(`archivist`→`theo`, `quick_logger`→`maya`) per your directive, and both personas + both scenarios
are deepened against the Driver–Context spine (R0/R1/R2/T, swap-test) now in README_3/4.

**This is the mandatory AC-4 developer-approval gate.** Please review:

- Persona: `test_harness_app/requirements_user_needs/personas/theo/persona.md`
- Scenario: `test_harness_app/requirements_user_needs/personas/theo/scenarios/detailed_entry_after_movie/scenario.md`
- Persona: `test_harness_app/requirements_user_needs/personas/maya/persona.md`
- Scenario: `test_harness_app/requirements_user_needs/personas/maya/scenarios/quick_rating_after_movie/scenario.md`
- Index: `test_harness_app/requirements_user_needs/SCENARIO_INDEX.md` (unchanged besides the folder
  rename — no content updates needed, its `notes:` remain accurate)

All four files: `review_status: draft` (not self-approved), `version: 1.1`, real R0 (Driver & Lens +
swap-test) / R1 (beyond-the-moment) / R2 (social field) / T (trajectory) content specific to each
persona, scenarios properly draw down from the persona spine without duplicating it, and remain
strictly status-quo/pre-app.

**One judgment call flagged, not resolved unilaterally**: README_3's Depth Requirements checklist
asks for "exactly one memorable anchor" — both personas embed a concrete anchor inline within R1
(Theo: notebook wedged on the bookshelf; Maya: Notes app in the phone dock) rather than under a
separate heading. Content-wise this satisfies the requirement; flag if you want a dedicated heading.

Please answer:
1. Do you approve the two personas and two scenarios as re-derived (AC-4 satisfied)? Yes / No.
2. If No, what changes are needed before approval?

# Developer Answer

---
parked_task_id: TASK-PROC-068-11
resolving_task_id: TASK-PROC-010-18
resolution_obligation: "resolves_parked_task: TASK-PROC-068-11"
resolving_session_id: 22b6b521-0d57-4ef0-9d41-a249c99aae14
resolving_account: gmail2
resolved_at: 2026-07-08T06:39:04Z
---

# Resolution

**Decision: discard the stale AC-4 approval request and re-derive against the reworked persona/scenario
guidance, then re-park at AC-4.**

The guidance this park's harness personas were authored against (TASK-PROC-010-17) has been reworked by
**TASK-PROC-010-18** (developer-approved 2026-07-08). The four harness artifacts currently sitting at
068-11's AC-4 gate were written under the *old* guidance and exhibit exactly the defects 010-18
corrects: leaked authoring method (R0/R1/R2/T headings, swap-test / method-anchor jargon emitted as
artifact content), no brevity/no-repetition discipline, and — for Maya — a circular, tool-referential
R0 driver ("habit preservation through friction minimization"). Presenting them for approval as-is
would approve sub-spec fixtures. The stale AC-4 request is therefore withdrawn, not answered.

**What changed in the guidance (now in effect — re-read these before re-deriving):**
- `REQ-PROC-010` §3/§4, `requirements_user_needs/README_3_PERSONA_DEFINITION.md`,
  `README_4_SCENARIO_DEFINITION.md` — method↔artifact separation (the spine/tests/anchors are
  pre-write reasoning, **never** emitted as sections/headings), output schema fixed to README_3's
  6-element template, **hard brevity bars** (persona body ≤ 120 lines, scenario body ≤ 150 lines excl.
  YAML), a no-repetition rule, and a **product-independent R0 driver** requiring the why-stack /
  product-independence test alongside the swap-test.
- `.claude/skills/ux-write-persona/SKILL.md`, `ux-write-scenario/SKILL.md` — the depth pass now
  carries an explicit "do-not-emit-as-sections" instruction plus a distinct output self-check step
  (schema · brevity · no-leaked-method · no-repetition) before each approval gate.

**Resume instructions for TASK-PROC-068-11:**

1. Clean-slate the four non-conformant artifacts from the prior attempt (both `persona.md` + both
   `scenario.md` under `test_harness_app/requirements_user_needs/personas/theo/` and `.../maya/`).
2. Re-deploy the whole factory into `test_harness_app/` (`scripts/playground/deploy.py`) so the
   contained child session runs against the **reworked** guidance and skills, not stale copies.
3. Re-run the contained derivation — invoke `ux-write-persona` / `ux-write-scenario` with the deployed
   harness as `cwd` via an isolated contained child session
   (`scripts/playground/containment.py`) — authoring the anchors into the harness's own
   `requirements_user_needs/` tree only, never the real mood-tracker product tree. Each artifact must
   pass the new output self-check: no leaked method, within the brevity bar, no repetition, and a
   product-independent driver (fix Maya's circular driver via the why-stack test).
4. Re-park at the mandatory AC-4 developer-approval gate with the re-derived, spec-conformant personas
   and scenarios for a fresh human approval.

**Provenance:** obligation minted at the developer gate (interactive authorization, 2026-07-07) —
`resolves_parked_task: TASK-PROC-068-11` on TASK-PROC-010-18's goal.md, baton moved off the spent
TASK-PROC-068-17 (whose obligation was for 068-11's earlier, already-resolved targeting park).
TASK-PROC-010-18's guidance rework is developer-approved (AC-7, 2026-07-08). The human `answer.md`
channel is left untouched — a real developer answer still overrides this machine resolution.

# Rationale Captured

Machine resolution (REQ-PROC-041-04 AC-15). Authored by TASK-PROC-010-18 under obligation 'resolves_parked_task: TASK-PROC-068-11'. resolving_session_id=22b6b521-0d57-4ef0-9d41-a249c99aae14, resolving_account=gmail2, resolved_at=2026-07-08T06:39:04+00:00.
