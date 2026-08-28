---
skill: task-resolve
mode: machine_resolution
decision: ""
task_id: TASK-PROC-068-11
captured_at: 2026-07-03
---

# Question

---
task_id: TASK-PROC-068-11
session_id: 91be1f5b-25be-4577-a8f4-ae4dfa718184
account: gmail2
status: awaiting_answer
asked_at: 2026-07-01T00:00:00Z
skill: task-resolve
---

# Pending Question

Full details in: `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-01_impl_harness-anchors-reauthor/plans_and_protocols/2026-07-01_01_protocol_anchor-authoring-mechanism-blocker.md`

**Blocker (before any tree mutation):** `ux-write-persona` / `ux-write-scenario` are hardwired to the
**main** `requirements_user_needs/` tree — no target-root parameter. Running them in this session would
author rating-app anchors into the **real mood-tracker** product definition and mutate its ID registry /
SCENARIO_INDEX / cascade links (hard to reverse). The sanctioned "run with the harness as cwd" deploy
mechanism is out of scope here, and the harness mirror lacks `CLAUDE.md` / `doc/` / `.claude/`. No prior
task has ever authored harness anchors via the real skills.

**Decision needed — how should the anchor authoring skills target `test_harness_app/`?**

- **Option A — cwd/deploy redirect (mirror-first):** first complete the harness structural mirror
  (`CLAUDE.md`, `doc/`, README type-defs, `.claude/` — goal step 4 / AC-01), then run the two skills with
  the harness as cwd via an isolated child session. Cleanest AC-06 conformance, but leans on
  deploy/isolate machinery this task lists out of scope (overlaps TASK-PROC-071-05-05). Confirm the
  minimal cwd-redirect is acceptable here vs. must wait.
- **Option B — parametrize the skills:** add a target-root arg (+ harness-local ID space / SCENARIO_INDEX /
  cascade scope) to both skills via `claude-modify-skill`. A governed-skill change — arguably scope creep.
- **Option C — hand-author to harness paths per README_3/README_4:** fastest but **violates AC-06** (the
  exact failure this remediation chain corrects). Not recommended.

Pick A, B, C, or specify another mechanism. On resume I will: clean-slate the non-conformant artifacts →
author via the chosen mechanism → park again for the mandatory developer approval gate (AC-4).

# Developer Answer

---
parked_task_id: TASK-PROC-068-11
resolving_task_id: TASK-PROC-068-17
resolution_obligation: "resolves_parked_task: TASK-PROC-068-11"
resolving_session_id: 585bc823-94d1-46e4-b185-7c4768cc177e
resolving_account: gmail
resolved_at: 2026-07-03T15:48:13Z
---

# Resolution

**Decision: Option A — cwd/deploy redirect (mirror-first).**

The harness-targeting deploy mechanism this park was waiting on now exists and is proven working:
**TASK-PROC-068-16** (T-B, REQ-PROC-068 AC-10) extended `scripts/playground/deploy.py` to copy the
**whole factory** (not just `.claude/skills/`) into `test_harness_app/`, and its completion evidence
(`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-02_impl_extend-harness-deploy-full-factory (completed)/plans_and_protocols/2026-07-03_02_evidence_ac10-functional-proof.md`)
is a real, non-mocked run in which a `containment.py`-contained child session ran a script-calling
factory skill's underlying script end-to-end inside the harness jail, using only the deployed
contents, with no reach-back to the host factory tree (negative control confirmed).

**Resume instructions for TASK-PROC-068-11:**

1. Clean-slate any non-conformant artifacts from the prior attempt (per this task's own note in its
   blocker protocol: "On resume I will: clean-slate the non-conformant artifacts...").
2. Complete the harness structural mirror step (goal step 4 / AC-01) if not already done.
3. Run `scripts/playground/deploy.py` to deploy the whole factory into `test_harness_app/`.
4. Invoke `ux-write-persona` / `ux-write-scenario` with the deployed harness as `cwd`, via an
   isolated **contained** child session (`scripts/playground/containment.py`), so the rating-app
   anchors are authored into the harness's own `requirements_user_needs/` tree — never the real
   mood-tracker product tree.
5. Park again for the mandatory developer approval gate (AC-4), per this task's original plan.

**Provenance:** T-B (TASK-PROC-068-16) — `status: completed`, AC-10 evidence file above. Obligation
minted at the developer gate (interactive authorization, 2026-07-02) — see
`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-02_impl_resolve-068-11-targeting/goal.md`
Notes section, "Obligation mint".

# Rationale Captured

Machine resolution (REQ-PROC-041-04 AC-15). Authored by TASK-PROC-068-17 under obligation 'resolves_parked_task: TASK-PROC-068-11'. resolving_session_id=585bc823-94d1-46e4-b185-7c4768cc177e, resolving_account=gmail, resolved_at=2026-07-03T15:48:13+00:00.
