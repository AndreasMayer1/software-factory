---
skills_used:
  - task-create
  - task-complete
  - claude-commit
  - claude-log
---

# Protocol: Persistent Harness Git Design (TASK-PROC-068-28)

**Agent ID**: ae9e3acc2e45df955
**Date**: 2026-07-17
**Task type**: task-backed tail of a closed `requ-explore` on REQ-PROC-068 — design already decided
and developer-approved; this task applied the verbatim edits, no re-opened decisions.

## Decision

The maintenance-mode (`build`/`maintain`) harness deploy currently initializes a fresh `git init` on
every run (AC-13). This loses any commit reference a prior run recorded — a materialization artifact's
provenance commit, a task's pinned requirements version — once that run's deployed copy is harvested
and discarded. The approved fix: **persistent harness git via a git bundle**.

- **Restore-on-deploy**: a maintenance-mode run's deployed copy initializes its git repository by
  restoring from the harness's persisted bundle (kept with the harness in the container project)
  rather than a fresh empty repository.
- **Persist-on-harvest**: on harvest, the copy's advanced history is exported back to the bundle and
  persisted with the harness.
- **Test mode is unaffected**: a test-mode run resets to a clean baseline after each run and carries
  no persisted history — it keeps the existing throwaway `git init` behavior. This is deliberate: the
  persistence problem is specific to maintenance-mode's cross-run artifact-reference need; test mode's
  clean-reset contract (AC-07) is the correct behavior for its purpose and is unchanged.

## Compaction policy

- **Preserve every referenced commit** — any commit that a harvested artifact's provenance field
  references (a materialization artifact's provenance commit, a task's pinned requirements version)
  must remain reachable, with a **stable hash**, in the persisted history forever.
- **Squash unreferenced intermediate commits** — commits between preserved points that nothing
  references may be compacted to keep the bundle from growing unbounded.
- **Prior runs' persisted commits are immutable** — once a run's commits have been persisted, a later
  run's compaction pass must not rewrite them (only append + selectively squash the unreferenced gaps).

## The backward-reference constraint (why no global squash-and-rewrite)

An artifact can't reference its own commit — a provenance field always points *backward* to an
already-existing commit at the time the field was written. This means any referenced commit's hash
must stay stable for as long as the referencing artifact exists; a global squash-and-rewrite (which
changes every downstream commit's hash) would silently break every existing backward reference. The
compaction policy above (preserve-referenced, squash-only-unreferenced, immutable-once-persisted) is
the direct consequence of this constraint — it is not an arbitrary choice among alternatives, it is the
only shape that keeps backward references valid.

## Superseded options

This design **supersedes** the earlier options considered during the closed exploration:
- **Option A — SHA-rewrite**: periodically rewrite history to compact it, remapping old SHAs to new
  ones via a translation table. Rejected: requires every artifact holding a provenance reference to be
  updated in lockstep with the rewrite, which is exactly the fragility the backward-reference
  constraint rules out; a missed update silently orphans a reference.
- **Option B — content-hash addressing**: address commits by content hash instead of git SHA so
  compaction can't break references. Rejected: reinvents a second addressing scheme parallel to git's
  own, adding complexity without a proportional benefit once preserve-referenced compaction is
  available.
- **Option C** (a discarded intermediate hybrid considered during exploration): not adopted; superseded
  by the bundle + preserve-referenced approach directly.

No REQ-PROC-074/075 provenance-contract change is needed — the provenance contract's shape (a
backward-pointing commit reference) is unchanged; only the *persistence mechanism* underneath the
harness's own git repository changes.

## Encapsulation invariant (AC-21)

The harness's presentation as an ordinary standalone project — including this durable git history and
the harness's own factory-runtime provenance (AC-11's reworded tail) — is established **entirely
within the playground deploy/harvest mechanism**. No other factory mechanism grows harness-specific
handling; every other mechanism (skills, scripts, quality gates, orchestration) continues to operate on
the harness exactly as it would on any real project. This is the same encapsulation principle already
applied to de-hardcoding harness-specific paths/behavior out of shared factory code, landed at commit
**969e3c70** — this task extends that precedent to git persistence and provenance realism specifically.

## Requirement edits applied

1. **AC-11 reword** — the final sentence now reads: "...the transient deployed factory machinery — the
   skills, scripts, and registries copied in to run the derivation — is absent from
   `test_harness_app/`, while the harness retains its own factory-runtime provenance grounding its
   product definition (the ideation index and ledger backing a derived decision) as project data of the
   standalone harness." The existing `EGP: F (...); consequence: MEDIUM` inline tail was kept as-is.
2. **AC-20 added** — persistent harness git (restore-on-deploy / persist-on-harvest / preserve-referenced
   compaction / test-mode excluded). EGP: F, consequence HIGH.
3. **AC-21 added** — encapsulation invariant (playground owns harness realism; no other mechanism
   special-cases the harness). EGP: X, consequence MEDIUM.
4. **Frontmatter** — added `trackable_items.acceptance_criteria` entries for AC-20 (`egp: {archetype: F,
   referent: "..."}, egp_auto: {archetype: F}, consequence: HIGH`) and AC-21 (`egp: {archetype: X,
   referent: "..."}, egp_auto: {archetype: X}, consequence: MEDIUM`). Extended AC-11's frontmatter
   `egp.referent` with "; and to retain its own factory-runtime provenance as project data".
   - Note: added explicit `egp_auto` for AC-20/AC-21 (not in the original edit spec) because
     `check_egp_audit.py`'s text-cue heuristic defaulted both to fail-safe `Q` without it, producing a
     confirmed≠auto mismatch — this mirrors the pattern already used by AC-11 through AC-19, all of
     which carry an explicit `egp_auto: {archetype: F}` for the same reason (their AC text doesn't
     contain the heuristic's literal F-cue phrases).

## Verification results

- `python3 scripts/artifacts/merge_requirements.py` — regenerated cleanly (285 files merged).
- `python3 scripts/artifacts/generate_id_registry.py --requirements` — regenerated cleanly.
- `python3 scripts/requirements/check_egp_audit.py requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md`
  — 21 ACs audited, **0 missing dispositions**, **0 invalid consequences**. 11 mismatches remain, all
  **pre-existing** (AC-01–10, AC-17 — self-certifiable/not-bearing ACs whose text doesn't trigger the
  auto-heuristic's bearing cues; present before this task). **AC-20 and AC-21 both show no mismatch.**

## Follow-on IMPL tasks (to be derived later, NOT part of this task's scope)

1. `workspace.py` (or equivalent harness-deploy module) — restore/persist-bundle logic replacing the
   fresh `git init` call in maintenance mode.
2. Harvest-time compaction — implement preserve-referenced / squash-unreferenced / immutable-once-
   persisted policy at the harvest step.
3. Trivial `deploy.py` `_SUBFOLDER_EXCLUDES` addition of `requirements_user_needs/product_materialization`
   (unrelated-but-noted trivial fix surfaced during the closed exploration).
4. Coordinate sequencing after TASK-PROC-068-27 (shared `build.py` COMPLETE branch) — the persistent-git
   restore/persist points likely sit adjacent to that branch's harvest logic.

These are intentionally **not** created as tasks by this exploration — `task-derive-from-requ` should
decompose AC-20/AC-21 (plus the AC-11 reword's downstream implication) into properly-sized, dependency-
ordered IMPL tasks in a later session.

## Outcome

All four goal.md ACs satisfied. No design decisions were re-opened; this task applied a closed,
developer-approved edit end-to-end (requirement text + frontmatter + regeneration + audit).
