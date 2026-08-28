# Protocol: Run 1 executed — real structural finding blocks AC-20/AC-11 verification

**Session**: 69804c91-9f5e-4c63-af04-e7983ca11aeb (automated, gmail2)
**Date**: 2026-07-18

## AC-21 — VERIFIED PASS (static check, no run needed)

Grepped all non-`scripts/playground/` factory code (`scripts/`, `.claude/`, `doc/`) for
`test_harness_app` mentions. Six hits, all benign:
- `scripts/quality/check_web_gates.sh`, `doc/web/**` — treat `test_harness_app` as an ordinary
  React/TypeScript project needing standard web quality gates/guidelines — exactly "operates on
  the harness exactly as on any real project," not special-casing it as a test fixture.
- `scripts/artifacts/generate_id_registry.py` — a generic `--root <path>` CLI flag (works for any
  nested/standalone project); the code comment explains the harness as the *motivating* use case
  but the mechanism itself is not gated on `if path == test_harness_app`.

No non-playground mechanism contains harness-specific handling. AC-21 holds.

## AC-20 / AC-11 — real run attempted, blocked by a genuine defect (not yet verifiable)

### Run design
Single real `run_build_mode` against the actual `test_harness_app/` (required — the bundle's
storage convention is inside the harness itself, not a throwaway target). Prompt (full text:
`plans_and_protocols/driver_prompt_run1.txt`) drove three parts inside the isolated copy:
- Part A: cheap degenerate chain-state certification (`persona-scenario-fixed`, existing approved
  PERSONA-001/PERSONA-002 anchors) to satisfy the chainstate acceptance oracle.
- Part B: one real, standalone, Quick-effort `ideation-start` (embedded mode) for a genuinely
  trivial decision (pick one of two one-line persona phrasings) — produces real
  `.factory/ideation/index.yaml` + ledger (the AC-11 provenance material) and a real commit to
  reference (the AC-20 compaction material).
- Part C: author `requirements_user_needs/personas/persona-gitproof/persona.md` referencing Part
  B's commit via `<!-- decided_by: IDEATION-001 @ <sha> -->`, then two throwaway noise commits
  (tail_len=2 minimum for compaction to actually fire — `_MIN_SQUASHABLE_TAIL`).

### Execution
Two earlier attempts (`build.py` direct, then `build_resume.py` in the background) were killed
mid-flight by the session being torn down and resumed (`claude --resume ...` restarted twice within
~2 minutes each time — background Bash processes do not survive that; see workaround below). A
third attempt, `build_resume.py resume` run in the **foreground** with a bounded 9-minute Bash
timeout (to avoid the same fate — a scheduled heartbeat wakeup appears to recycle the underlying
CLI process and kill any backgrounded Bash job tied to it, at least in this environment right now;
noted as an operational hazard for future long real-run attempts, not this task's concern to fix),
completed cleanly: rc=0, `total_duration_ms=385034` (6.4 min), `total_cost_usd=2.0629` (over the
$2.00 cap — `over_budget: true`, the run still completed since the cap is checked between runs, not
mid-run).

**All three prompt parts genuinely executed** — verified directly against the preserved workspace
(`/workspaces/private_mood_tracker/playground_ws_8303399e`)'s real git history:
```
ba34809 noise commit 2
b934437 noise commit 1
d4f0a9c author gitproof persona referencing the ideation decision commit
7f71de4 ideation: decide proof-persona phrasing (Quick, embedded)
155bc0c certify degenerate persona_scenario boundary (already-approved anchors)
586881c playground baseline
```
`.layerderiv/chain_state.json` shows unit `persona-scenario-fixed` status `done` with a real gate
verdict (`drift: 0.3, passed: true`) — the chainstate acceptance oracle's `complete: true` was
genuinely reached.

### The finding — outcome misclassified BLOCKED, harvest never runs

Despite the chain reaching `complete: true`, `run_build_mode` classified the run **BLOCKED** (not
COMPLETE) and skipped harvest entirely (`"harvested_paths": []`) — so `compact_workspace_git` /
`export_workspace_git_bundle` never ran; no bundle was ever written to
`test_harness_app/.playground_harness_git/`.

Root cause, read directly from `scripts/playground/build.py`:
```python
_PENDING_FEEDBACK_GLOB = "automation/pending_feedback/*/question.md"

def has_recorded_blocker(workspace: str) -> bool:
    return any(Path(workspace).glob(_PENDING_FEEDBACK_GLOB))
```
This globs the **whole workspace copy** for any `question.md`, with **no diff against the pre-run
baseline** — it does not distinguish "this run's child created a blocker" from "the copy already
contained one before the child ever started." `deploy.py`'s `_TOP_LEVEL_EXCLUDES` does **not**
exclude `automation/` — the whole factory's `automation/pending_feedback/` tree, including every
**pre-existing, unrelated, already-standing** developer question, is deployed wholesale into every
isolated copy. Confirmed present in the preserved workspace right now:
```
automation/pending_feedback/TASK-FUNC-014-06-01/question.md
automation/pending_feedback/TASK-FUNC-007-01-05/question.md
automation/pending_feedback/TASK-PROC-031-04/question.md
automation/pending_feedback/TASK-PROC-046-16/question.md
automation/pending_feedback/TASK-PROC-068-26/question.md
```
These are real, currently-unanswered questions for **other, unrelated tasks** in the host factory
(confirmed against the host's own `automation/pending_feedback/` and `automation/orchestrate.log.spin-bug`,
which independently lists these same task IDs' `answer.md` as whitespace-only/unanswered) — none of
them were created by my child session; my prompt explicitly forbade writing under
`automation/pending_feedback/` and the workspace diff confirms it never did.

### Why this is a genuine blocking defect, not a prompt-design mistake

As long as the host factory has **any** standing developer question anywhere (a normal, frequent
state for an actively-developed factory — five exist right now), `has_recorded_blocker` will
misclassify **every** maintenance run as BLOCKED, regardless of what the child does. This makes
AC-20 (persist/restore/compaction) and AC-11 (provenance retention) **structurally unverifiable
against the real harness in practice** — not just today, but on effectively any future day this
host has an open question, which the git history shows is common. `has_recorded_blocker`'s own
docstring intent ("an explicit blocker/escalation artifact was recorded [by this run]") disagrees
with its own implementation.

### Why I did not self-fix

Fixing `has_recorded_blocker` (diff against baseline) and/or excluding `automation/pending_feedback/`
from `deploy.py` are both real, in-scope-adjacent code changes to the SAME gate mechanism (AC-18's
BLOCKED classification, AC-2/AC-4-class deploy-exclude precedent) but are **not** this task's
declared scope ("Out of Scope: Implementing the mechanism — done by TASK-PROC-068-31/32/33"; this
defect is a pre-existing gap in `build_run_outcome-classification`/`deploy.py`, unrelated to those
three tasks' actual changes). Two candidate fixes exist and the choice has real consequences (same
class of decision as the 068-19 AC-4 precedent):
- **Option A** — `has_recorded_blocker` diffs the workspace against its own pre-run baseline
  snapshot (already computed, `snapshot_product_definition`-adjacent machinery exists) and only
  counts a `question.md` that is NEW since baseline.
- **Option B** — `deploy.py` excludes `automation/pending_feedback/` (or all of `automation/`) from
  the deployed copy outright, same class as the `requirements_tasks/process` exclude
  (TASK-PROC-068-19): authoring-time/host-operational state, not a harness-runtime input.

I am not authorized to pick between these or land either — escalating.

## Cost/state left behind
- `$2.06` real spend (this session's one completed real-run attempt; the two earlier
  session-teardown-killed attempts cost effectively $0 — `total_cost_usd` was never reached before
  they died).
- Preserved workspace `/workspaces/private_mood_tracker/playground_ws_8303399e` (BLOCKED, not
  auto-resumable — `RUN_STATUS_BLOCKED` is not in `build_resume`'s resumable set) — left in place
  for inspection/reuse after the fix decision; NOT deleted.
- `test_harness_app/` itself: unchanged (harvest never ran — confirmed `git status --porcelain
  test_harness_app/` still clean, 0 new files).
- Run registry record: `/workspaces/private_mood_tracker/.playground_runs/8303399e-....json`
  (`status: blocked`).

## Outcome
AC-21 verified PASS. AC-20 and AC-11 **cannot be verified** until the developer decides how to
resolve the false-BLOCKED classification. Escalating via `pending_feedback`.
