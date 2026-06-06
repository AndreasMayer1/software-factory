# Test Case Findings — `task-derive-from-requ` on REQ-PROC-001

Task: TASK-PROC-058-07
Run date: 2026-05-25 (Phase 1 + 1.5 detect + escalate) → 2026-05-26 (resume + apply + Phases 2–6)
Skill under test: `.claude/skills/task-derive-from-requ/SKILL.md`
Target requirement: REQ-PROC-001 (Context Window)
Sessions: 60d42e81-7a35-434b-87dd-1e6f3f73bec8 (gmail2, automated, both halves)

## TL;DR

The skill works end-to-end on a real, known-imperfect requirement. The
coverage matrix, verification-task gate, cross-ref detection, automated-mode
escalation, and final coverage validation all fire correctly. Five concrete
integration mismatches between the skill's documented behavior and the
implemented scripts were surfaced (Findings D, E, F, G, H) and filed as a
follow-up task (TASK-PROC-058-08). Two positive signals: the coverage matrix
is computed live (Finding A) and the automated-mode pause/resume cycle worked
without manual intervention.

| Result | Detail |
|--------|--------|
| Skill fires correctly | Coverage gate detected uncovered AC-07; verification-task gate detected missing verify task |
| Pause/resume works | Phase 1.5 escalation wrote `question.md`; developer answered; session resumed cleanly |
| Cross-ref gate works | 2 genuine semantic links found (REQ-PROC-008, REQ-PROC-058) and applied |
| Final coverage | 100% (10/10 trackable items) — was 90% (9/10) at start |
| Bugs filed | 5 integration mismatches → TASK-PROC-058-08 |

## What happened (chronological)

### Phase 1 — Gather
- Read REQ-PROC-001 (8 ACs, 10 existing tasks).
- Ran `scripts/requirements/coverage_report.py` → AC-07 sole uncovered AC,
  no verification task exists.
- Read 2 completed tasks (TASK-PROC-001-01, -02) for covers-repair; both
  legitimately empty (legacy / explore type) — no auto-repair applied.

### Phase 1.5 — Cross-Reference Completeness Gate
- Used `scripts/requirements/check_cross_refs.py` (Findings D, E: actual
  script name and interface differ from skill text).
- Default (auto-derived) terms produced 128 generic false positives
  (Finding F). Explicit domain terms produced 9 candidates.
- REQ-PROC-001 has zero cross-references today.
- Identified 2 genuine `semantic` candidates (REQ-PROC-008, REQ-PROC-058)
  and 7 false positives.
- Automated-mode escalation fired: wrote `question.md`, copied `answer.md`,
  committed (`SKIP_QUALITY_GATES=1` WIP), terminated session via
  `scripts/automation/terminate_session.sh`.
- Developer approved recommendations: `Related Requirements recommendations
  approved.` + "create follow-up task for skill issues".

### Phase 1.5.3 — Apply (resume)
- Wrote classifications file; spawned background apply agent with
  `requ-explore` semantics (prompt is in skill template, used verbatim).
- Agent added `## Related Requirements` section to REQ-PROC-001 with the two
  semantic bullets. Committed (`8c0eaa33`); appended completion note in a
  follow-up commit (`d48e352c`).

### Phase 1.5.4 — Verify
- Re-ran detector → 7 candidates remained, exactly the 7 `ignore` set.
  Residual after subtracting ignores = empty. Gate passed.

### Phase 2–3 — Analyze + Plan
- Plan: 2 new tasks. TASK-PROC-001-11 (impl, AC-07) +
  TASK-PROC-001-12 (verify, all 8 ACs). 100% coverage post-creation.

### Phase 5 — Create (automated → orchestration pattern attempted)
- Attempted `create_orchestration_task.py --task-type impl` → exit 2
  (`invalid choice: 'impl'`). Finding G: actual values are
  `implement|verify|scribble|scribble_to_flutter`, no `mixed`.
- Examined the script — line 183 only branches between `task-create-code` and
  `ui-create-scribble`. No routing to `task-create` for non-code tasks
  (Finding H). Skill text assumes a routing the script does not implement.
- Fell back to invoking `task-create` inline per plan entry (the path the
  skill takes in interactive mode). Both tasks created successfully:
  TASK-PROC-001-11 and TASK-PROC-001-12.

### Phase 6 — Validate
- `coverage_report.py` shows REQ-PROC-001: 100% (10/10).
- Verification task present (TASK-PROC-001-12, `verification_task: true`).
- No circular `after:` chains. All sizing signals populated.

## Findings

### Positive

**A — Coverage matrix is computed live.** The goal.md authored 2026-05-24
listed AC-04 and AC-07 as zero-coverage. By 2026-05-25 AC-04 had been
covered by TASK-PROC-001-10 (created the same day this validation began).
The skill surfaced AC-07 only — i.e. the current gap, not a cached snapshot.

**B — Automated-mode pause/resume works.** The Phase 1.5 escalation
mechanism (write `question.md`, copy `TEMPLATE_answer.md`, commit with
`SKIP_QUALITY_GATES=1`, terminate via `terminate_session.sh`) executed
without issue. The developer answered with a short approval line; the next
session picked up cleanly at Phase 1.5.3 with all state preserved in the
protocol files.

**C — Cross-ref classification escalation produces useful artifacts.** The
`cross_ref_gaps.md` file written before terminating gave the developer a
single page with all candidates, my recommendations, and the exact summary
they needed to paste into `answer.md`. They answered in two lines.

### Bugs (filed as TASK-PROC-058-08)

**D — Cross-ref detector script name mismatch.** Skill references
`scripts/requirements/detect_cross_ref_gaps.py`. Implementation is
`scripts/requirements/check_cross_refs.py` (TASK-PROC-045-07).

**E — Cross-ref detector interface mismatch.** Skill documents
`--target <path> --json`. Implementation uses positional `requirement` and
JSON-by-default.

**F — Auto-derived search terms too generic.** Default terms for
REQ-PROC-001 were `["User", "want", "Story", "developer"]` → 128 candidates.
Stop-word filtering needed in `check_cross_refs.py`.

**G — Orchestration `--task-type` values.** Skill documents
`[impl|mixed]`. Implementation accepts
`implement|verify|scribble|scribble_to_flutter`.

**H — Orchestration script does not route to `task-create`.** Only
`task-create-code` and `ui-create-scribble`. Non-code planning (skill edits,
audits) requires the fallback path used here (invoke `task-create` inline).

### Other observations

- The `task-derive-from-requ` skill's Phase 1.5.3 prescribes
  `run_in_background: true` for the apply agent. For the cross-ref-only
  apply case (no AC changes — just adding bullets to `## Related
  Requirements`), this is conservative. The apply completed in ~80 s on a
  small edit + protocol log + commit. Worth a future tuning note but not
  filed as a bug.
- The covers-repair workflow (skill AC-09) was not exercised on real data:
  the two empty-covers tasks (TASK-PROC-001-01, -02) are legacy /
  explore-type. No high-confidence auto-repair was triggered, which is the
  correct behavior. Auto-repair confidence-scoring will need a different
  test case to be exercised.

## Deliverables produced by this run

| File | Purpose |
|------|---------|
| `plans_and_protocols/2026-05-25_01_protocol_phase1_findings.md` | Phase 1 + 1.5.1 findings (pre-escalation snapshot) |
| `plans_and_protocols/2026-05-25_cross_ref_gaps.md` | Developer-facing candidate gaps reference |
| `plans_and_protocols/2026-05-26_cross_ref_classifications.md` | Resolved classifications (apply agent input) |
| `plans_and_protocols/2026-05-26_03_protocol_cross_ref_apply.md` | Apply agent's protocol (diff + commit refs) |
| `plans_and_protocols/2026-05-26_task_creation_plan.md` | Plan for the two new REQ-PROC-001 tasks |
| `automation/pending_feedback/TASK-PROC-058-07/{question,answer}.md` | Pause artifacts |
| `requirements_tasks/.../REQ-PROC-001/.../2026-05-26_impl_ac07-iterative-fix-opus-escalation/goal.md` | TASK-PROC-001-11 |
| `requirements_tasks/.../REQ-PROC-001/.../2026-05-26_verify_req-proc-001-acs-hold/goal.md` | TASK-PROC-001-12 (verification) |
| `requirements_tasks/.../REQ-PROC-058/.../2026-05-26_impl_align-skill-with-implemented-scripts/goal.md` | TASK-PROC-058-08 (follow-up fixes per developer instruction) |
| (this file) | Test case findings |

## Conclusion

`task-derive-from-requ` is fit for purpose. The five integration bugs are
real and worth fixing, but none blocks the skill from doing its job:
falling back to a less-precise path produced a valid plan and the correct
final coverage. Re-running the validation after TASK-PROC-058-08 lands —
ideally against `feat_qr_data_transfer` (the secondary test case noted in
this task's goal.md) — would confirm the bugs are closed and exercise the
covers-repair workflow that this run did not touch.
