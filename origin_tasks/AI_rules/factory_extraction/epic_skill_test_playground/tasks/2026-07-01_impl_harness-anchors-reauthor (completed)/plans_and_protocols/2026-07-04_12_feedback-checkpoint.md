---
skill: task-resolve
mode: automated
decision: ""
task_id: TASK-PROC-068-11
captured_at: 2026-07-04
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

# Developer answer (2026-07-04, interactive)

**Resolved. Proceed with the CONTAINED authoring path — no uncontained session, no skill
parametrization needed.** The premise this park was stuck on ("contained LLM authoring is
technically impossible", protocol 06) was wrong. It is now genuinely possible and proven:

- `containment.py` gained bwrap `--share-net` — the jail keeps the host network namespace, so a
  child `claude`/`ccs` session reaches `api.anthropic.com` (CON-04/AC-09 filesystem isolation is a
  mount-namespace guarantee and is unaffected).
- **REQ-PROC-068 AC-12** (new): the jail binds `~/.claude` (mandatory) and `~/.ccs` (optional,
  silent when absent) read-write at their real paths, so both native `claude` and `ccs` authenticate
  inside the jail. Verified end-to-end by a green `run_skeleton` live smoke (child returned SMOKE_OK,
  cost recorded, ephemeral workspace reset + destroyed, outer repo untouched, no leak).
- The deploy/run/reset mechanism was also hardened: an **ephemeral workspace** in the project's parent
  folder (git-init'd so `reset` is safe and skills that need git work), a `reset.py` own-repo guard so
  `git reset --hard` can never hit the outer tree, and a `deploy.py` fix so the authoring-guide
  machinery under `requirements_user_needs/` is deployed.

Mechanism commits: `524a8867` (AC-12 requirement) and `be270123` (mechanism + tests + protocols 07–11).

**Resolution resume path fixed:** the machine-resolver loop pathology this park hit (an identical stale
`resolution.md` re-served on every resume without engaging the follow-up — protocol 06) is fixed by
commit **e6584a6fa97eccce571007557e5d11676c1ba612** (`fix(TASK-PROC-041-04-10): delete stale
resolution.md on ineffective resume`). A future resume will no longer loop on the stale resolution.

**Resume instructions for TASK-PROC-068-11** (the existing `resolution.md` plan is now actually
executable — follow it):
1. Clean-slate the non-conformant harness product-definition artifacts from the prior attempt.
2. Complete the harness structural mirror (AC-01) if not already done.
3. Deploy the whole factory into the ephemeral run workspace (via `run_skeleton` / `deploy.py`).
4. Author the anchor layers by invoking `ux-write-persona` / `ux-write-scenario` in a **contained**
   child session with the deployed harness as cwd (network + auth now work), writing into the
   harness's own `requirements_user_needs/` — never the real mood-tracker product tree.
5. Park again for the mandatory developer-approval gate (AC-4) before completion.

# Rationale Captured

(Automated archival — no rationale extracted.)
