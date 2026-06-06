# Phase 3 Questions — REQ-NFUNC-001, REQ-NFUNC-010, REQ-NFUNC-011

Generated: 2026-03-06

---

## REQ-NFUNC-001 — Data Model Versioning and Migration

No questions. All 5 ACs are clearly specified with concrete behavior. Task TASK-NFUNC-001-01 created.

---

## REQ-NFUNC-010 — In-Detail Navigation

### Q1: Scope of `showAdaptiveOverlay()` migration

The requirements doc says "Optionally migrate to utility function once created" for `plan_template_detail_content.dart`. Should TASK-NFUNC-010-01 **require** full migration of the existing implementation to use the new utility, or only update the hardcoded breakpoints (600/1200 → 600/1240) as a minimum?

**Impact**: If full migration is required, the scope includes refactoring the existing `_showAdaptiveDetailOverlay` method. If only breakpoint fix is required, the scope is smaller.

---

## REQ-NFUNC-011 — Main Navigation

No tasks created. Status is `implemented` and the requirement document explicitly states "**COMPLETE** - This requirement is fully documented based on codebase investigation." All 4 sections (SEC-01 through SEC-04) are documentation/guidelines — there are no pending action items, follow-up tasks, or TODO markers in the document.

**Decision**: No task created for REQ-NFUNC-011. If coverage tracking requires a formal "verify implementation" task, please advise.
