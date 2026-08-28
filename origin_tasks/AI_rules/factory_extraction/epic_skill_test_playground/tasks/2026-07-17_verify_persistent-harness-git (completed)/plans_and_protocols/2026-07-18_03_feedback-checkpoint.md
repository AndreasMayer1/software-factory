---
skill: task-resolve
mode: automated
decision: ""
task_id: TASK-PROC-068-34
captured_at: 2026-07-18
---

# Question

---
task_id: TASK-PROC-068-34
session_id: 69804c91-9f5e-4c63-af04-e7983ca11aeb
account: gmail2
status: awaiting_answer
asked_at: 2026-07-18T16:50:03Z
skill: task-resolve
---

# Pending Question

Full details in: `plans_and_protocols/2026-07-18_02_protocol_run1-and-finding.md`.

AC-21 verified PASS (static check). AC-20/AC-11 need a real build/maintain run to reach the
harvest step, but a real run just proved that **every** maintenance run against the current host
state is misclassified BLOCKED (never harvests, no bundle ever persisted) — `has_recorded_blocker`
in `scripts/playground/build.py` globs the whole workspace copy for `automation/pending_feedback/*/question.md`
with no diff against the pre-run baseline, and `deploy.py` does not exclude `automation/` from the
copy. So the host's own **pre-existing, unrelated** standing developer questions (currently 5:
TASK-FUNC-014-06-01, TASK-FUNC-007-01-05, TASK-PROC-031-04, TASK-PROC-046-16, TASK-PROC-068-26) get
deployed into the copy and are indistinguishable, to this detector, from a blocker the child run
itself created. Verified my child run created none (workspace diff confirms; my prompt forbade it)
and legitimately reached chainstate `complete: true` — it was still classified BLOCKED and never
harvested. This isn't a one-off: it recurs on any day the host has a standing question, which the
git history shows is common.

Two candidate fixes (protocol file has full detail):
- **Option A** — `has_recorded_blocker` diffs against the pre-run baseline snapshot; only a
  `question.md` that is NEW since baseline counts as this run's blocker.
- **Option B** — `deploy.py` excludes `automation/pending_feedback/` (or all of `automation/`) from
  the deployed copy, same class as the existing `requirements_tasks/process` exclude.

Please choose Option A, Option B, both, or a different fix. This is a real code change to the
BLOCKED-classification gate / deploy excludes — outside this verify task's declared scope
("Out of Scope: Implementing the mechanism"), so I'm not self-authorizing it.

Once fixed, my preserved workspace `/workspaces/private_mood_tracker/playground_ws_8303399e`
(BLOCKED, not auto-resumable — `blocked` isn't in `build_resume`'s resumable set) already has the
full chain-state DONE + all commits ready; a fresh `build_resume.py resume` after the fix should
reach COMPLETE and let me verify AC-20/AC-11 for real (the $2.06 already spent doesn't need to be
redone). Note the real run took ~6.4 min and $2.06 (slightly over the $2.00 default cap, which
only gates *between* runs, not mid-run) — if you'd like a different cap for the retry, let me know.

# Developer Answer

**Option B** — `deploy.py` excludes all of `automation/`

# Rationale Captured

(Automated archival — no rationale extracted.)
