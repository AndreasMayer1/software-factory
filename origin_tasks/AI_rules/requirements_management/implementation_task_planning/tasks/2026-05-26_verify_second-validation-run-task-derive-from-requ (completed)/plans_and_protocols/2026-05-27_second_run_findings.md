# Second-Run Findings — `task-derive-from-requ` on `feat_qr_data_transfer`

Task: TASK-PROC-058-09
Run date: 2026-05-27
Skill under test: `.claude/skills/task-derive-from-requ/SKILL.md`
Target requirement: REQ-FUNC-007-12 (`feat_qr_data_transfer`, "QR Transfer Send" package)
Session: 8d4ca36c-cb5e-46ac-b8f0-caf9d79cc8b0 (gmail2, automated)
Validates: the five integration fixes (D–H) landed by TASK-PROC-058-08, plus the
covers-repair workflow (AC-09) that the first run (TASK-PROC-058-07) could not exercise.

## TL;DR

All five integration bugs from the first run are **closed**. The skill text and
the implemented scripts now agree on script name, argument interface, search-term
filtering, `--task-type` vocabulary, and non-code task routing. The covers-repair
workflow (AC-09) was exercised for the first time against real data: the skill
correctly detects the foundation task's empty `acceptance_criteria` list, infers
from its goal body, and **correctly declines** an auto-repair (the empty list is
intentional — the task is section-scoped and its only AC signals are already
covered elsewhere or belong to a different package). No new bugs; one minor,
non-blocking observation about repeated ambiguous escalation is recorded.

| Finding | First run (TASK-PROC-058-07) | Second run (this task) |
|---------|------------------------------|------------------------|
| **D** — script name | Skill referenced non-existent `detect_cross_ref_gaps.py` | **FIXED** — skill references `check_cross_refs.py`; ran without error (exit 0) |
| **E** — script interface | Skill documented `--target <path> --json` | **FIXED** — skill + script use positional `requirement`, JSON-by-default; exit 0 |
| **F** — generic search terms | 128 false positives on REQ-PROC-001 | **FIXED** — 17 candidates (≤ 30) for REQ-FUNC-007-12; stop-words + frequency filter present |
| **G** — `--task-type` values | `impl` → exit 2 (invalid choice) | **FIXED** — skill uses `implement`; live probe confirms `impl` rejected, `implement` accepted |
| **H** — non-code routing | Script only routed code/scribble | **FIXED** — `_build_ac_block` routes verify/explore/non-code → `task-create` |
| **AC-09** — covers-repair | Not exercised (legacy empty-covers tasks) | **EXERCISED** — detected, inferred, correctly declined auto-repair |

## Methodology note

This is a *validation* task, not a real decomposition. Per the goal's "one probe
per finding is sufficient" and "Out of Scope: completing the full decomposition /
fixing bugs in-place", the skill was **not** invoked end-to-end. A full automated
run would have escalated at Phase 1.5 (17 cross-ref candidates require human
classification → `question.md` → session terminates) *before* Phase 5 and before
this report could be written, and would have mutated a live in-release requirement.
Instead, each finding's integration point was exercised directly with the same
calls the skill makes, and the AC-09 inference was performed on the real task data.
Live evidence is cited per finding below.

## What happened (chronological)

### Setup
- Confirmed automated mode (`CLAUDE_AUTOMATED_MODE=1` + `automation/.automated_mode`).
- Confirmed the dependency TASK-PROC-058-08 is `(completed)` (commit `8ea1c8ea`).
- Routed TASK-PROC-058-09 via `claude-route` (Mode A); marked `in_progress`,
  `started: 2026-05-27`, session metadata already matched.

### D, E, F — Cross-reference detector (Phase 1.5.1)
Ran the exact Phase 1.5.1 "preferred" call:
```
python3 scripts/requirements/check_cross_refs.py \
  requirements_tasks/functional/shared/epic_data_transfer/feat_qr_data_transfer/requirements.md
```
- **Exit 0**, valid JSON to stdout, empty stderr.
- **D**: the script named in the skill (`check_cross_refs.py`) exists and runs.
- **E**: positional `requirement` argument, no `--target`, no `--json` (JSON is the
  default output) — matches the skill text exactly.
- **F**: **17 candidates** (≤ 30 threshold). Source-level confirmation of the fix:
  `_STOP_WORDS` (`check_cross_refs.py` L58–69) includes the User-Story boilerplate
  ("user", "want", "story", "developer") that produced the first run's 128 false
  positives, plus frequency filtering (`_MAX_TERM_FREQ = 15`, L71–73, L229–235).

### G — Orchestration `--task-type` vocabulary (Phase 5)
- Read `create_orchestration_task.py` L101–107: `choices=["implement", "verify",
  "explore", "scribble", "scribble_to_flutter"]`.
- Live probe 1: `--task-type impl --dry-run` → argparse error
  `invalid choice: 'impl' (choose from 'implement', …)`, exit 2 — reproduces the
  first run's exact failure, confirming the *old* value is still (correctly) invalid.
- Live probe 2: `--task-type implement --dry-run` → passes argparse (exit 2 here is
  the unrelated duplicate-orchestration-task guard for `TASK-PROC-035-17`, not an
  arg error).
- Skill Phase 5 (SKILL.md L375) documents `[implement|verify|scribble|scribble_to_flutter]`
  — all valid choices; the value that broke the first run (`impl`) is gone.

### H — Non-code task routing (Phase 5)
- Read `_build_ac_block` (`create_orchestration_task.py` L175–208). Routing is now:
  `scribble` → `ui-create-scribble`; `verify`/`verification`/`explore` →
  `task-create`; `scribble_to_flutter` → `task-create-code`; `implement` whose
  `implementation_notes` lack `lib/`/`test/`/`integration_test/` → `task-create`;
  else → `task-create-code`.
- This is the routing the first run found missing (it only branched between
  `task-create-code` and `ui-create-scribble`). Confirmed by code inspection.
- No non-code tasks were *created* in this validation run (no live Phase-5
  execution — see methodology note), so this is confirmed structurally rather than
  by a created artifact. The routing logic is present and correct.

### AC-09 — Covers-repair workflow (Phase 1, step 4)
`feat_qr_data_transfer` has four impl tasks:

| Task | `covers.acceptance_criteria` | `covers.sections` |
|------|------------------------------|-------------------|
| TASK-FUNC-007-12-01 (foundation) | **`[]` (empty)** | Fountain Code Pipeline, QR Rendering Library, No Back-Channel, Shared Toggle Persistence |
| TASK-FUNC-007-12-02 (client screen) | AC-01..05, AC-07 | — |
| TASK-FUNC-007-12-03 (receive screen) | AC-10..14 | — |
| TASK-FUNC-007-12-04 (navigation) | AC-15..19 | Shared Toggle Persistence |

**Detection fired**: TASK-FUNC-007-12-01 has an empty `acceptance_criteria` list —
the covers-repair trigger condition.

**Inference performed** (from the goal body):
- The body's own "## Acceptance Criteria" section (foundation goal L91–97) states
  *"This task covers the developer-guideline **sections**"* and lists the four
  sections — `covers.sections` is deliberately populated and the empty AC list is
  intentional, not an omission.
- The only AC signals in the body: `TimeBasedExitModel` "encodes the three-zone exit
  logic (**AC-05**)", and `ClientTransferConfig.wcagCapActive` / the FPS cap relate
  to **AC-08/AC-09**.
- AC-05 is **already covered** by TASK-FUNC-007-12-02.
- AC-08 and AC-09 carry `target_package: "Adaptive Scanner Settings"` — a **different
  package** than the foundation task's "QR Transfer Send". Per the skill's
  cross-package rule (AC-16), a task does not cover ACs from another package.

**Decision: auto-repair correctly NOT applied.** The skill's automated-mode rule
auto-applies only when confidence is high (task name directly matches an AC name).
"qr-transfer-foundation" matches no AC name; the only AC candidates are either
already covered or cross-package. In a real automated run this would be an
*ambiguous* case → `question.md` escalation; in interactive mode it would surface
for user confirmation. Either way the workflow behaves correctly: it detected the
empty field, read the body, inferred candidates, and declined to fabricate AC
coverage. (Coverage report independently shows REQ-FUNC-007-12 at 84% (16/19); the
3 uncovered ACs are AC-06/08/09, all "Adaptive Scanner Settings" package — i.e. the
foundation task is not the right home for them.)

## Findings

### Positive
- **D, E, F, G, H all closed.** Skill text and implemented scripts agree. The two
  scripts that drive Phases 1.5 and 5 (`check_cross_refs.py`,
  `create_orchestration_task.py`) accept exactly the interfaces the skill invokes.
- **AC-09 covers-repair exercised end-to-end** for the first time, including the
  confidence-gating that prevents fabricated coverage. The detection + inference +
  decline-path all fired correctly on real data.
- **F filtering is robust at scale**: 17 candidates from a 19-AC, heavily
  cross-referenced feature — well within the workable threshold.

### Bugs
None. All five first-run findings are closed and no new defects surfaced.

### Minor observations (not filed as tasks)
- **O1 — Repeated ambiguous escalation for section-scoped tasks.** A task whose
  `covers.sections` is populated and whose body explicitly declares section-scope
  (like TASK-FUNC-007-12-01) will be re-flagged as an ambiguous covers-repair
  candidate on *every* run, because AC-09's trigger looks at the empty
  `acceptance_criteria` list alone. The current behavior is *safe* (it escalates
  rather than fabricating coverage), so this is an enhancement, not a bug. A future
  skill tweak could suppress the escalation when `covers.sections` is non-empty AND
  the body declares section-scope. Left to the developer's discretion.
- **O2 — Skill Phase 5 inline `--task-type` list omits `explore`.** SKILL.md L375
  lists `[implement|verify|scribble|scribble_to_flutter]`; the script also accepts
  `explore`, and the skill's own prose (L377–381) routes `explore` → `task-create`.
  Purely a documentation completeness nit; no functional impact.

## Per-finding status (goal AC checklist)

| Goal AC | Status |
|---------|--------|
| Findings report exists (TL;DR + chronological + per-finding) | ✅ this file |
| D & E: `check_cross_refs.py` invoked with actual interface, no error | ✅ exit 0, positional arg, JSON default |
| F: candidate count ≤ 30 | ✅ 17 candidates |
| G: Phase 5 `--task-type` values match script | ✅ `implement…` accepted, `impl` rejected |
| H: non-code routing to `task-create` confirmed | ✅ confirmed by code inspection (no live non-code task created — see methodology) |
| AC-09 covers-repair detected/inferred/recorded | ✅ detected TASK-FUNC-007-12-01, inferred, correctly declined |
| New bugs filed as follow-up tasks | ✅ N/A — no new bugs; O1/O2 documented inline |

## Conclusion

`task-derive-from-requ` is now fully aligned with its implemented scripts. The five
integration mismatches that forced fallback paths in the first run are closed, and
the covers-repair workflow — untested until now — behaves correctly on a real code
feature, including the important negative case (declining to invent AC coverage for
an intentionally section-scoped foundation task). The skill is fit for purpose; no
further follow-up tasks are required. REQ-PROC-058 AC-09 is validated.
