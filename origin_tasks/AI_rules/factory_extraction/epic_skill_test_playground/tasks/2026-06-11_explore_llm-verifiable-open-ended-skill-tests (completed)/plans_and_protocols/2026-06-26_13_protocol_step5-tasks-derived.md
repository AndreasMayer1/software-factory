---
skills_used:
  - claude-watch-tool-reliability
  - claude-commit
  - task-complete
---

# Protocol — STEP 5 (staged) tasks derived: Stage-0 build-out chain

**Date:** 2026-06-26 · **Task:** TASK-PROC-068-01 · interactive, Opus · developer present (resumed session).

Resumed after the prior session's background `task-create` agent was killed at spawn by a usage
limit (created nothing — verified: HEAD unchanged, no TASK-PROC-073 tasks existed). Re-did the work
**inline** (developer-approved: the design content is authored here and the edges must be verified
here, so no context double-load).

## Requirements committed first (anchor for the tasks)
The STEP-3 authoring (REQ-PROC-073-01 + REQ-PROC-073 epic marker + REQ-PROC-068 AC-08/09 + Deferred)
was committed as its own `requ:` commit **`9b25bde0`** before derivation — matching the repo
convention (`requ:` → `task:`) and giving the new tasks a real `requirements_version` anchor. Staged
exactly the 5 requirement paths; unrelated working-tree changes excluded.

## Stage-0 chain created (inline, via task-create procedure)
The build-out is a self-propagating `orchestration_task` chain (plan `…_11_…`). Stage 0 only:

| Task | ID | type | after | role |
|---|---|---|---|---|
| T-spike | `TASK-PROC-073-01-01` | impl, opus | `[]` | disproof spike on the **HARDEST** ideation defect-pair (covers REQ-PROC-073-01 **AC-02**, EGP C/MED); detection + real cost vs manual; SG-02 cost-capture; go/no-go stop-loss |
| T-orch1 | `TASK-PROC-068-02` | impl, **orchestration_task**, opus | `[TASK-PROC-073-01-01]` | first gap-filler: read verdict → GREEN authors deferred 073-01 AC-01/AC-03 slice + creates T-skeleton/corpus/maturity/T-orch2; RED creates T-fallback; re-points T-finalize; appends created tasks to override |
| T-finalize | `TASK-PROC-068-03` | impl | `[TASK-PROC-068-02]` | **unbroken-edge terminus**: stable finalization node; each orchestration task re-points its `after` to the live frontier; verifies playground+oracle finalization when finally unblocked |

**Unbroken edge** (developer directive): T-spike → T-orch1 → T-finalize is a real, continuous edge to
playground-finalization *now*, not a prose promise. The terminus's `after` is intentionally mutable —
orchestration tasks move it forward to the live frontier as the chain grows.

**Deliberate partial derivation, NOT a coverage gap:** only AC-02 of REQ-PROC-073-01 is covered here;
AC-01 (corpus) + AC-03 (maturity walk) are deferred to T-orch1 on spike-GREEN (stop-loss). Standard
`task-create`→`task-derive-from-requ` redirect overridden by design (logged in T-spike Notes). A full
decomposition now would pre-commit AC-01/03 work regardless of the spike outcome, defeating the stop-loss.

**Superseded plan point fixed:** plan `_11_`'s "Decisions" section named the serve-mode fix
(`TASK-PROC-004-04-08`, easiest) as the spike seed. STEP-3 fidelity fix re-homed serve-mode to AC-03's
maturity-walk opening batch; AC-02's spike must pick the **hardest** pair (SOL-01 §6). T-spike honors
the corrected requirement, not the stale plan section.

## Visibility override (developer directive 2026-06-26)
All three IDs appended to `.claude/task_ordering_priority_override.txt` under a dated Stage-0 block,
modelled on the existing 2026-06-05 scribble-gate precedent. The file carries **visibility only** (these
process tasks have no `target_package`, so `next_tasks.py` sees them only when listed) — **not** ordering;
ordering stays in the `after:` graph (developer-corrected; consistent with plan `_11_`). The
self-propagating append-rule ("every task the chain creates, transitively, MUST be appended") is baked
into T-orch1's goal.md step 4 + AC, and carries forward to T-orch2/T-orch3.

## Validation
- All 3 goal.md frontmatter parse as valid YAML; edges as tabled above; `orchestration_task: true` on T-orch1.
- `next_tasks.py`: surfaces **only T-spike** (unblocked); T-orch1/T-finalize correctly held by `after`.
- `generate_status_overview` ingested 824 tasks, 0 errors on the new tasks. id_registry regenerated.

## 068-01 AC status after this step
- "Action stated as next step performed successfully" → **met** (the 3 tasks created + validated).
- "Chain ordering: oracle impl/verify tasks set `after` the playground-build tasks" → satisfied by the
  orchestration design (T-orch1 wires T-maturity `after` T-skeleton/T-corpus). The **spike** intentionally
  precedes the build — it is the stop-loss that decides whether to build at all (named exception, not a
  violation; the *oracle-against-built-playground* tasks are the maturity/integration ones T-orch1 derives).

## Uncommitted after this step (for the close)
3 new task folders + override-file edit + regenerated STATUS.md + id_registry.md. Pending developer
decision: commit as a `task:` derivation commit and/or close TASK-PROC-068-01 via `task-complete`.
