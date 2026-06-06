# Phase 3 Questions — REQ-NFUNC-012, REQ-NFUNC-014, REQ-NFUNC-016

Generated: 2026-03-06

---

## REQ-NFUNC-014 (Responsive Layout Master Detail)

No questions. The requirement has `status: implemented` and all trackable sections (`SEC-01`, `SEC-02`, `SEC-03`) are `target_release: "0.0.1"`. No new tasks were created.

---

## REQ-NFUNC-016 (Local Database Technology)

No questions. AC-05 and AC-06 are clearly specified. TASK-NFUNC-016-02 was created to cover both ACs, blocked by the exploration task TASK-NFUNC-016-01.

---

## REQ-NFUNC-012 (Growth Tree Theme)

### Q-NFUNC-012-01: What does AC-08 mean concretely for release 0.0.1?

**AC-08 text**: "All components incrementally support both modes" (`target_release: "0.0.1"`)

**Problem**: "All components incrementally" is self-contradictory as a task boundary. If it means all components in the current codebase must have dual-mode (Tree/Simple) support before 0.0.1 ships, that is a large, unbounded scope. If it means only a defined subset of components must support both modes at 0.0.1, the list of components needs to be specified.

The existing components folder covers: LeafPopout, ContextHelp, Skeleton, Toast, loading indicators (listed in REQ-NFUNC-012 section 12). Skeleton and Toast are noted as "same in both modes."

**Options to consider**:

1. **Narrow interpretation**: For 0.0.1, "incremental" means the isTreeTheme check pattern is implemented in at least the core shell/navigation and one or two representative components (LeafPopout, ContextHelp). Remaining components are deferred to later sprints.

2. **Broad interpretation**: All components listed in section 12 of REQ-NFUNC-012 must have dual-mode support before 0.0.1 ships.

3. **Defer AC-08 entirely**: Move AC-08 to a later release (e.g. 0.1.0) and update the requirements.md accordingly, since the Tree Theme organic visuals (AC-04, AC-07) are already deferred to 0.4.0.

**Action required**: Please clarify which interpretation applies, or update the `target_release` on AC-08 in `requirements.md`. Without this clarification, no task can be created for AC-08 with a well-defined scope boundary.
