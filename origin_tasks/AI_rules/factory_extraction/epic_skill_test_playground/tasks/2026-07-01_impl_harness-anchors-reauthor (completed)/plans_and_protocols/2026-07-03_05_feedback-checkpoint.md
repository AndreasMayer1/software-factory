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
account: gmail
status: awaiting_answer
asked_at: 2026-07-03T00:00:00Z
skill: task-resolve
---

# Pending Question (follow-up — Option A execution blocker)

Full details in: `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-01_impl_harness-anchors-reauthor/plans_and_protocols/2026-07-03_04_protocol_optionA-execution-blocker.md`

You chose **Option A** (cwd/deploy redirect). On resume I verified the mechanism against the **real**
`test_harness_app/` before touching anything, and it is **not safe/functional as-prescribed** — three
concrete findings (all read-only-verified, no tree mutation made):

1. **Repo-destroying reset hazard (unfixed).** `test_harness_app/` is **not its own git repo** (nor
   gitignored) — `git -C test_harness_app rev-parse --show-toplevel` → the outer `flutter_app` repo.
   `scripts/playground/reset.py` runs `git reset --hard HEAD`, which would wipe **all uncommitted work
   in the whole repo**. TASK-PROC-068-16's own plan documents this as a known "Discovered risk … not
   fixed — out of scope," a flagged-but-never-created follow-up.
2. **AC-10 proof ≠ what Option A needs.** That proof ran a **stdlib Python script** in a **scratch repo**
   ("never the real `test_harness_app/`, per the discovered hazard") — not a `claude` session. The only
   claude-launching path (`run_skeleton.py`) uses `--unshare-all` bwrap (**no network** → API
   unreachable) and ends in the Finding-1 reset. No `claude` session has ever run against the real harness.
3. **Skill guidelines absent in harness.** `deploy.py` excludes `requirements_user_needs/`, so the READMEs
   `ux-write-persona`/`ux-write-scenario` read won't exist under the harness cwd.

**Decision needed — pick the safe path (details/rationale in protocol 04):**

- **A1 — fix harness git topology first** (the flagged follow-up): make `test_harness_app/` its own repo
  (`git rm --cached -r` + root `.gitignore` + nested `git init` + seed commit), then Option A runs safely.
  Clean but larger; authorize creating that prerequisite task.
- **A2 — minimal trusted authoring** (no containment, no reset): seed the harness mirror (`CLAUDE.md`,
  `doc/`, `requirements_user_needs/README_*`, `.claude/skills/`), then `cd test_harness_app && claude -p`
  a child session that runs the two skills. Trusted host authoring, not an untrusted-candidate run — but
  needs sign-off (nested `claude` + intentionally skipped containment).
- **A3 — parametrize the skills** (former Option B): add a target-root arg via `claude-modify-skill`;
  author from this session directly into `test_harness_app/…`. No nested session, no deploy, no reset.

Pick A1, A2, or A3 (or specify another). No tree mutation has occurred; a clean re-park strands nothing.

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
