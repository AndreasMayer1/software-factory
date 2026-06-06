---
task_id: TASK-PROC-029-02
type: impl
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 4
impact_reason: I4-PRODUCT_DIRECTION
status: completed
completed: 2026-02-14
effort: L
created: 2026-02-14
after: [TASK-PROC-029-01]
awaiting: []
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04]
  sections: []
scope_description: "Design and implement the market research workflow: project-level data store, findings format, push-to-requirements mechanism, scope_exclusions integration, skill adaptations, traceability"
requirements_version:
  commit: 25e51b1
  file: ../requirements.md
---

# Implementation Task: Incorporate Market Research into Requirements Workflow

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/requirements_management/market_research/requirements.md` (REQ-PROC-029)
- **Status**: Not Started

## Goal

Design and implement the **3rd requirements flow**: a workflow that takes market research data, extracts structured findings, and propagates those findings into four destinations — functional requirements, non-functional requirements, user flows, and persona/scenario scope exclusions — as traceable, reevaluable references alongside the existing user-needs and design-bridge flows.

## Background: The Three Requirements Flows

The project uses three parallel flows to inform feature decisions. Each provides a different perspective, and they will not always agree. That tension is intentional — it forces explicit decision-making with documented trade-offs.

| Flow | Source | Destinations | Existing? |
|------|--------|-------------|-----------|
| **1. User Needs** | Persona → Scenario → User Flow | Functional requirements (`user_needs` YAML field) | ✅ Yes |
| **2. Design Bridge** | User needs traits | UX/Design system rules (REQ-PROC-026) | ✅ Yes |
| **3. Market Research** | Competitor analysis, trend data, user demand evidence | See below | 🔲 This task |

### Market Research Flow Destinations

The 3rd flow has **four distinct output channels**:

| Output | Target | Purpose | Example |
|--------|--------|---------|---------|
| **Feature priorities** | `requirements_tasks/functional/` | Confirm/challenge demand for features | "DiGA market shows mood tracking is table-stakes → prioritize" |
| **Quality/design influence** | `requirements_tasks/non-functional/` | Inform technical and UX standards | "Data protection is #1 concern → strengthen privacy requirements" |
| **User flow refinement** | `requirements_user_needs/user_flows/` | Validate or question user flow assumptions | "Blended care trend validates therapist-assigns-homework flow" |
| **Scope exclusions** | `requirements_user_needs/personas/*/persona.md` and `scenarios/*/scenario.md` | Mark user groups or behaviors as out-of-scope based on market evidence | "No market demand for social/community features → exclude from all personas" |

The scope_exclusions channel is especially important: market research is an authoritative source for `reason: business` exclusions (see `requirements_user_needs/README_17_SCOPE_EXCLUSIONS.md`). When research shows that a user group, behavior, or feature has no market demand, it should be recorded as a scope exclusion with a traceable reference to the finding — preventing wasted effort on scenarios and features that market data does not support.

## Scope Overview

**Affected Layers**: Process layer (`.claude/skills/`, `requirements_market_research/`, `requirements_user_needs/`, `requirements_tasks/`)
**Estimated Files**: ~10–15 files (new folder structure, README, skill, YAML format changes, skill updates, examples)
**Patterns to Follow**: How Flow 1 (user needs) is structured — bidirectional references between source data and requirements; see `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` and `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md` for reference notation patterns. Also see `requirements_user_needs/README_17_SCOPE_EXCLUSIONS.md` for scope exclusion schema and reason taxonomy.

## What Needs to Be Built

### 1. Project-Level Folder: `requirements_market_research/`

Create a **new top-level folder** at the project root (alongside `requirements_tasks/`, `requirements_user_needs/`, `requirements_general_overview/`) for storing all market research data:

```
requirements_market_research/
├── README.md                        ← Explains the 3rd flow end-to-end
├── YYYY-MM-DD_[topic]/
│   ├── raw/                         ← Original source files (Gemini exports, survey results, etc.)
│   └── findings.md                  ← Structured analysis extracted from raw data
└── _templates/
    └── findings_template.md         ← Template for new findings.md files
```

**Why project-level?** Market research data is a primary input to the requirements process, not a sub-artifact of process rules. Placing it at the same level as `requirements_tasks/` and `requirements_user_needs/` makes it a peer input source — reflecting its role as the 3rd flow.

**Migration**: The initial Gemini research (`Copy of App Marktanalyse.json` currently in the explore task folder) must be migrated into `requirements_market_research/2026-02-14_german-mental-health-apps/raw/`. The older research (`initial research november 2023.md`) becomes `requirements_market_research/2023-11_initial-market-overview/raw/`.

### 2. Findings Format (`findings.md`)

Define a standard `findings.md` template that structures raw research into actionable insights:

- Each finding has: ID, statement, evidence summary, confidence level, source reference
- Findings are categorized by their primary output channel:
  - **demand** — evidence about user willingness / market demand (→ feature priorities)
  - **quality** — evidence about technical or quality expectations (→ non-functional)
  - **flow** — evidence that validates or challenges user flow assumptions (→ user flows)
  - **exclusion** — evidence that a user group, behavior, or feature lacks demand (→ scope_exclusions)
- Findings link forward to requirements or personas/scenarios they influence (populated after applying)

### 3. Traceability: `market_research_refs` in Requirements

Define how requirements cite market research. Two scenarios:

**A. Research supports or influences a requirement** — requirement gets a `market_research_refs` field:
```yaml
market_research_refs:
  - finding: MR-2026-02-14-001
    source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md
    influence: "Confirms demand; DiGA market shows mood tracking is table-stakes"
```

**B. Research leads to a scope exclusion** — persona or scenario gets a new `scope_exclusions` entry with the existing schema (README_17), citing the finding:
```yaml
scope_exclusions:
  - area: "Social/community features (peer support, forums)"
    reason: business
    reason_detail: "Market research shows no competitor success with social features in CBT therapy apps. Finding: MR-2026-02-14-007. Source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md"
    reconsider_in: "v2.0"
```

**C. Research raises a conflict or open question** — create a decision record noting the conflict and how it was resolved.

### 4. Push Workflow Skill: `apply-market-research`

Create a new Claude Code skill with two modes of operation:

**Mode A: Push to requirements**
1. Takes a `findings.md` file as input
2. Lists findings categorized by output channel (demand, quality, flow, exclusion)
3. For demand/quality/flow findings: asks which functional/non-functional/user-flow requirements they influence
4. For each connection, adds/updates the `market_research_refs` field in the target requirement
5. For conflicts between flows (e.g., a persona wants X but market says no demand for X), surfaces the conflict and asks for a decision record

**Mode B: Push to scope exclusions**
1. Identifies findings categorized as `exclusion`
2. For each exclusion finding: asks which persona(s) and/or scenario(s) should be excluded
3. Adds `scope_exclusions` entries to the target persona/scenario YAML using the existing schema (README_17)
4. Uses `reason: business` with `reason_detail` citing the finding ID and source path
5. Runs the same downstream impact check as `modify-user-needs` (warns if existing scenarios overlap with the new exclusion)

### 5. Update Existing Skills

Three existing skills need light updates to be market-research-aware:

- **`explore-requirements`**: When writing requirements for a functional feature, check if relevant market research findings exist in `requirements_market_research/` and include them in the `market_research_refs` field
- **`create-impl-task`**: When creating impl tasks for functional features, note if the feature has market research backing (or explicitly lacks it — which is a gap worth flagging)
- **`modify-user-needs`**: When adding scope_exclusions, accept market research findings as a valid source for `reason: business` exclusions and ensure the `reason_detail` cites the finding

### 6. README: The 3rd Flow Documentation

Write `requirements_market_research/README.md` documenting the complete end-to-end flow:
- What market research is and why it's the 3rd flow
- The four output channels (feature priorities, quality/design, user flows, scope exclusions)
- When to add new research (trigger: new data available)
- How to process raw data into findings.md (using the template)
- How to use `apply-market-research` skill to push findings into requirements and scope exclusions
- How to handle conflicts between the 3 flows
- How to reevaluate past decisions when new research contradicts old findings
- Folder naming conventions and structure

## Additional Context

- The initial research (Gemini conversation Feb 2026) covers: German mental health app market, CBT/DiGA apps (HelloBetter, Selfapy, deprexis, Velibra, Invirto, somnio), free apps (Woebot, MindDoc, Wysa), blended care platforms (Minddistrict), data protection analysis (DiGA vs. free apps, GDPR), and market trends (prescription-first, specialization, AI integration).
- There is also an older research file (`initial research november 2023.md`) which should be migrated as a second data entry.
- The three flows will often produce conflicting signals — that's by design. The requirement is not to resolve conflicts automatically, but to make them visible and traceable so humans can decide.
- Scope exclusions use a well-defined schema (README_17) with reason taxonomy (`technical | effort | business | strategic`). Market research most commonly produces `business` exclusions.
- This is a living workflow. New research rounds should be addable without restructuring the entire system.

## Acceptance Criteria

- [ ] `requirements_market_research/` folder created at project root with README
- [ ] `findings.md` template created with ID system, categories (demand, quality, flow, exclusion), confidence levels
- [ ] Initial Gemini research migrated into `requirements_market_research/2026-02-14_german-mental-health-apps/`
- [ ] Older research migrated into `requirements_market_research/2023-11_initial-market-overview/`
- [ ] `market_research_refs` YAML format defined and documented
- [ ] New skill `apply-market-research` created with both push-to-requirements and push-to-scope-exclusions modes
- [ ] `explore-requirements` skill updated to check `requirements_market_research/` for relevant findings
- [ ] `create-impl-task` skill updated to note market research backing (or gap)
- [ ] `modify-user-needs` skill updated to accept market research as source for business exclusions
- [ ] `requirements_market_research/README.md` documents the complete 3rd flow including all four output channels
- [ ] At least one existing requirement updated with a `market_research_refs` example
- [ ] At least one existing persona/scenario updated with a market-research-sourced `scope_exclusions` entry

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-029-01 | completed | Requirements written (REQ-PROC-029) |
| REQ-PROC-009 | implemented | Task/requirements structure this builds upon |
| TASK-PROC-010-15 | completed | Scope exclusion mechanism (README_17) this integrates with |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
