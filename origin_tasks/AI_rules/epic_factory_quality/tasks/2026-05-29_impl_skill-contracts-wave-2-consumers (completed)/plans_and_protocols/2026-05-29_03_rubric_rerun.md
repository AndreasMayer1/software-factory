# Rubric Re-run — Wave 2 Consumer Skills (TASK-PROC-044-04)

**Date:** 2026-05-30 · **Task:** TASK-PROC-044-04 · **Session:** 136c4709 (gmail, automated, Opus)

## Rubric (from `claude-create-skill` §"Phase Split Decision")

| # | Signal | YES if… |
|---|--------|---------|
| S1 | Independently invocable? | Callable without manufacturing parent-held context |
| S2 | Coordinates ≥ 2 agents? | Real fan-out — one agent + wait is a wrapper, not orchestration |
| S3 | Natural human-review point? | Developer pauses/approves at this boundary |
| S4 | File-based artifact crosses boundary? | Producer writes, consumer reads — file is the contract |

**Split if ≥ 2 YES → sub-skill. < 2 YES → agent (collapsed into parent).**

---

## Per-Skill Scores

### code-simple

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: User invokes "Use code-simple for [task]" directly — no parent context needed.
- **S2**: Spawns `implementation-engineer` (Phase 3) + `test-engineer` per test file (Phase 4) + `quality-checker` (Phase 5) → real fan-out, ≥3 agents.
- **S3**: Presentation Layer path requires user approval for scribble gate ("pause for user approval"). Also, optional quality-checker RED triggers a review loop.
- **S4**: Produces `lib/<feature>/...` and `test/<feature>/...` — consumed by test infrastructure and task-complete.

---

### code-complex

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Independently invocable; the "heavyweight" sibling of code-simple.
- **S2**: Spawns architecture-advisor + implementation-engineer + test-engineer + quality-checker → explicit multi-agent orchestration.
- **S3**: Plan review checkpoint after architecture-advisor phase; explicit user approval before implementation proceeds.
- **S4**: Produces `lib/` + `test/` + `plans_and_protocols/` artifacts crossing skill boundaries.

---

### code-bugfix

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill (borderline) |

- **S1**: User invokes "Use code-bugfix for [task]" directly.
- **S2**: Both slim mode (inline, no worktree) and worktree mode execute in the main session without agent fan-out — worktree is isolation machinery, not agent orchestration.
- **S3**: No human review point in either mode; fix → test → complete is automated.
- **S4**: Produces modified `lib/` or `scripts/` files that cross to testing + task-complete.

**Note**: 2/4 borderline is expected and consistent with the SCRIBBLE-SPLIT benchmark (ui-scribble-approve-handoff also 2/4). The skill is correctly a sub-skill because users directly invoke it by name (S1) and its outputs are file artifacts (S4). No rubric edge case — the ≥2 threshold holds without ambiguity.

---

### code-test

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Directly invocable; used when test-only work is needed.
- **S2**: Spawns `test-engineer` (planning phase) + quality-checker + optional fix agents — ≥2 agents.
- **S3**: "Optional: Wait for user plan approval" — explicit human-review checkpoint after test plan.
- **S4**: Produces `test/<feature>/...` files consumed by CI + task-complete.

---

### ui-verify-flutter

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Invoked on a per-requirement path; no parent context manufactured.
- **S2**: Spawns scribble-comparison agent + review agent; may spawn revision subtask creation agents.
- **S3**: Verdict review point — RED/YELLOW/GREEN classification is a natural human-visible decision boundary; may produce `revision_target.yaml` requiring developer awareness.
- **S4**: Produces `flutter_review/comparison.md` and optional `revision_target.yaml` — consumed by ui-create-scribble (revision path) and ui-improve-flutter.

---

### ui-improve-flutter

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: User invokes "Use ui-improve-flutter for [screen path]".
- **S2**: Spawns one targeted fix agent per approved change — multiple sequential agents across the improvement session.
- **S3**: "Present grouped list to user. Apply (a) and (b) automatically on approval. Ask separately before applying (c)." — explicit human review + selective approval.
- **S4**: Modifies `lib/features/[feature]/presentation/` files consumed by task-complete + test-engineer.

---

### task-derive-from-requ

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Invoked on a requirements.md path directly.
- **S2**: Spawns gather agent (for ≥3 related requirements) + apply agent (background, run_in_background: true) — real parallel/async fan-out.
- **S3**: Classification review point before apply phase; interactive mode surfaces residuals for user decision.
- **S4**: Produces `goal.md` files (one per task) consumed by code-simple/complex/bugfix/test + task-complete.

---

### task-create-code

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Invoked as "Use task-create-code for [feature]" or via claude-route.
- **S2**: Creates task metadata files but does not spawn multiple agents — single-pass file-creation workflow.
- **S3**: Phase 4.1 presents `goal.md` for user review (interactive mode); plan-driven mode skips but the checkpoint is structurally present.
- **S4**: Produces `goal.md` consumed by code-simple/complex/test/bugfix on the next invocation.

---

### task-complete

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Terminal step invoked by every workflow; independently callable.
- **S2**: Invokes `verify-quality` (which spawns quality-checker agent) + `claude-commit`; in code-change mode this is a real multi-skill fan-out.
- **S3**: Quality gate is the canonical human-review-equivalent decision boundary (RED blocks completion — developer must intervene if gates cannot be resolved within 5 cycles).
- **S4**: Writes final `goal.md` (status: completed), triggers `STATUS.md` regeneration — both consumed by the orchestration layer and next-task selection scripts.

---

## Summary

| Skill | Score | Verdict |
|---|:---:|---|
| code-simple | 4/4 | Sub-skill ✓ |
| code-complex | 4/4 | Sub-skill ✓ |
| code-bugfix | 2/4 | Sub-skill (borderline) |
| code-test | 4/4 | Sub-skill ✓ |
| ui-verify-flutter | 4/4 | Sub-skill ✓ |
| ui-improve-flutter | 4/4 | Sub-skill ✓ |
| task-derive-from-requ | 4/4 | Sub-skill ✓ |
| task-create-code | 3/4 | Sub-skill ✓ |
| task-complete | 4/4 | Sub-skill ✓ |

**All 9 consumer skills score ≥ 2 → all correctly structured as sub-skills.**

## Rubric Refinement Proposals

**None.** The one borderline case (code-bugfix, 2/4) is not an edge case — it is the same category as the benchmark borderline (ui-scribble-approve-handoff, 2/4) from the SCRIBBLE-SPLIT example. The ≥2 threshold correctly handles it without ambiguity.

The v1 rubric holds across the full code-*/ui-*/task-* consumer family. No `revision_target.yaml` filed to TASK-PROC-044-08.
