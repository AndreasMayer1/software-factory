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
asked_at: 2026-07-03T20:30:00Z
skill: task-resolve
needs_human: true
---

# Pending Question (THIRD park — needs the actual developer, not the auto-resolver)

Full details in: `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-01_impl_harness-anchors-reauthor/plans_and_protocols/2026-07-03_06_protocol_containment-impossibility-and-resolver-loop.md`

**Please note — this is a machine-resolver loop.** Feedback checkpoints 02, 03, and 05 all carry the
*identical* resolution (same `resolving_session_id 585bc823…`, same `resolved_at 2026-07-03T15:48:13Z`):
"Option A / use `containment.py`." Checkpoint 05 never engaged my previous follow-up. Re-serving it again
will not unblock the task — a human decision is required.

**Decisive new fact (empirically proven this turn):** the resolution's prescribed mechanism —
"author via an isolated **contained** child session (`containment.py`)" — is **technically impossible**.
`containment.py` uses `bwrap --unshare-all` (no network). I tested it: inside the jail,
`create_connection('api.anthropic.com', 443)` fails DNS resolution. A `claude -p` session needs the API,
so **no LLM authoring skill can run inside the jail** — the jail can only run offline scripts (which is
all the AC-10 proof ever did). Authoring via a contained child session cannot work, at all.

Plus the two still-valid blockers: (1) `test_harness_app/` is not its own git repo, so `reset.py`'s
`git reset --hard` would wipe the whole outer repo (known unfixed 068-16 risk); (3) `deploy.py` excludes
`requirements_user_needs/`, so the skills' READMEs are absent under the harness cwd.

**The only mechanisms that can actually author, and the decision needed:**

- **(1) Authorize A2′ — UNCONTAINED child session** (`cd test_harness_app && claude -p`, network on, NO
  bwrap, NO reset), trusted host authoring into `test_harness_app/requirements_user_needs/`. This is the
  closest functional realization of your Option A. Needs explicit sign-off because uncontained
  `--dangerously-skip-permissions` nested `claude` is normally forbidden (CLAUDE.md §Agent Spawn Topology)
  and drops the AC-09 isolation. (Optionally pair with fixing the harness git topology first.)
- **(2) Authorize A3 — parametrize the skills** via `claude-modify-skill` (target-root arg) and author
  from THIS session — no child session. You previously chose Option A over this; option (2) reverses that.
- **(3) Something else / defer.**

Note: fixing the git topology alone does NOT unblock — a *contained* claude still has no network. Only
(1) or (2) can produce the anchors. No tree mutation has occurred; a clean re-park strands nothing.

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
