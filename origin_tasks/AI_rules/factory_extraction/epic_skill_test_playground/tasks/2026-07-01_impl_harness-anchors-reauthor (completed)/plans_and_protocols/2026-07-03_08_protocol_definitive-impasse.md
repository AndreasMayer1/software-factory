# Protocol 08 — Definitive impasse: structural machine-loop + no faithful autonomous path

Task: TASK-PROC-068-11 · 2026-07-03 · fourth resume (checkpoint 07). Terminal analysis.

## The loop is structural and I cannot break it from an automated session

`orchestrate.py::find_machine_resolutions` (REQ feat_feedback_pause_resume AC-15/16/17) fires the
machine-resolution channel whenever: `question.md` + `resolution.md` exist, `answer.md` is
empty/template, and the resolution's obligation is valid. TASK-PROC-068-17 holds a **valid** obligation
(`resolves_parked_task: TASK-PROC-068-11`) and its `resolution.md` (static, `resolved_at 15:48:13Z`) says
"Option A." Every resume re-serves it unchanged (checkpoints 02/03/05/07 are byte-identical). The **only**
suppressor is AC-16 human precedence: a **non-template `answer.md`** — which automated sessions are
forbidden to write. So re-parking cannot break the loop; each re-park just re-arms the same channel.

## There is no safe, in-bounds, *faithful* autonomous path to the deliverable

- The resolution's literal mechanism — author "via an isolated **contained** child session" — is
  **proven impossible**: `containment.py`'s `bwrap --unshare-all` jail has no network (empirically:
  `create_connection('api.anthropic.com',443)` → DNS failure), so no `claude`/LLM skill can run in it.
- `ux-write-persona` / `ux-write-scenario` are hardwired to one project root with `cwd=root` (READMEs,
  ID-registry regen, SCENARIO_INDEX, cascade scan all root-relative to the main tree). The **only
  faithful** way to run them against `test_harness_app/` is a **`cwd=harness` child session**.
- A `cwd=harness` child session needs infrastructure that does not work / is out of scope: (a) network +
  credentials inside the jail (broken), OR (b) an **uncontained** child session (drops AC-09 isolation +
  `--dangerously-skip-permissions` nested `claude`, which CLAUDE.md §Agent Spawn Topology forbids without
  explicit human authorization); AND (c) the harness must be its own git repo or `reset.py` wipes the
  whole outer repo (known unfixed 068-16 "Discovered risk", never made into a task).
- **In-session "retargeting"** of the skills (writing their outputs to harness paths by hand) would
  bypass the skills' real machinery = exactly the **068-07 anti-pattern** (hand-rolled authoring, AC-06
  violation) that THIS remediation task exists to correct, and it risks mutating the real mood-tracker
  tree. Not a faithful realization.

Net: faithful authoring requires either the out-of-scope child-session infrastructure OR explicit human
authorization of the uncontained workaround. Neither is available, and the machine-resolver cannot
supply either (it only re-emits the impossible literal instruction).

## What a human must do to unblock (any one)

1. **Write `answer.md`** for TASK-PROC-068-11 (suppresses the machine loop via AC-16) choosing a real
   mechanism — recommended: **authorize the UNCONTAINED `cwd=harness` child session, no reset** (A2′),
   optionally after making `test_harness_app/` its own git repo; or **authorize A3** (parametrize the two
   skills via `claude-modify-skill`).
2. **Create the prerequisite infrastructure task**: make `test_harness_app/` its own git repo AND make
   the harness child-session launch actually run LLM skills (network + credentials in the sandbox, or a
   blessed uncontained mode) — the deferred deploy/isolate work (overlaps TASK-PROC-071-05-05). Then
   Option A runs as designed.
3. Or invalidate TASK-PROC-068-17's obligation so the park reverts to human-only.

No tree mutation has occurred across four resumes — clean-slate deliberately not run, main tree untouched.
Investigations: protocols 04, 06, and this 08. Human-facing question: `pending_feedback/.../question.md`
(`needs_human: true`).
