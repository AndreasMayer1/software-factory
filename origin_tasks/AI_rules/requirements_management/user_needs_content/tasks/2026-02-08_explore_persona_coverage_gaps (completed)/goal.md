---
task_id: TASK-PROC-027-02
type: explore+impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-QUAL
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-02-08
completed: 2026-02-08
after: []
awaiting: []
covers:
  acceptance_criteria: []
---

# Goal: Analyze Persona Coverage Gaps and Create Missing Personas

## Context

All current client personas (Max, Jana, Elias, Sophie) are in therapy forms that fall under the Richtlinienverfahren "Verhaltenstherapie" (CBT, DBT, Exposure Therapy, ADHD Therapy). The therapist persona Prof. Dr. Weber represents Tiefenpsychologie (depth psychology/psychoanalysis), but has **no associated client persona**. This means the fundamentally different requirements of depth-psychology clients (dream diaries, free association, narrative tracking vs. structured homework) are not represented.

## Phase 1: Explore - Persona Coverage Analysis

Systematically analyze the current persona landscape for gaps:

1. **Read all existing personas** (clients, therapists, self-users) to understand current coverage
2. **Map therapist-client relationships**: Which therapists have associated clients? Which don't?
3. **Map therapy types**: Which Richtlinienverfahren/therapy approaches are covered by client personas?
4. **Identify gaps**: Are there therapy types, user behaviors, or protocol patterns that no current persona covers?
5. **Evaluate**: For each gap found, assess whether a new persona is needed or whether an existing persona can be extended

### Known Gaps to Evaluate
- **Prof. Dr. Weber (Tiefenpsychologie)**: Needs a client. Dream diaries, free-form narrative entries, and anti-metrics attitudes create fundamentally different app requirements than structured VT homework.
- **Dr. med. Turan (Psychiatrie)**: Sophie already covers medication tracking. Evaluate whether a dedicated psychiatry-only client adds unique requirements or whether existing personas suffice (possibly via additional scenarios).
- **Any other gaps**: Are there therapy types, accessibility needs, or user patterns that are completely unrepresented?

### Decision Criteria for "New Persona Needed"
A new persona is justified ONLY if it introduces **requirements that no existing persona covers**. If the gap can be filled by adding a scenario to an existing persona, prefer that approach.

## Phase 2: Impl - Create Missing Personas

For each gap identified in Phase 1 that requires a new persona:

1. Follow the existing persona template structure (see `requirements_user_needs/personas/` for examples)
2. Describe the **Ist-Zustand (Status Quo)** only - how they manage today WITHOUT the app
3. Include: demographics, diagnosis/context, implicit clusters, pain points, device reality
4. Set `review_status: draft` and `gold_status: false`
5. Register new persona IDs in the id_registry

## User Decisions (Pre-Made)
- Prof. Dr. Weber client: **Yes, create** (depth psychology has fundamentally different protocol needs)
- Dr. med. Turan client: **Likely no** (Sophie covers medication; consider adding a scenario instead)
- Other gaps: **Flag and pause** for user decision before creating
