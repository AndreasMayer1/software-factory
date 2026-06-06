# Plan: Incorporate Market Research Workflow
Date: 2026-02-14
Agent: architecture-advisor-001

## Overview

Implement the 3rd requirements flow by creating a project-level `requirements_market_research/` folder structure, a standard `findings.md` format, a new `apply-market-research` skill for pushing findings into requirements and scope exclusions, and minimal token-efficient additions to three existing skills. Two example applications (one requirement, one persona) complete the traceability chain.

The raw research files live in the now-completed explore task folder and must be migrated. No `requirements_market_research/` folder exists yet.

---

## Files to Create / Modify

### New files (12)
| # | Path | Purpose |
|---|------|---------|
| 1 | `requirements_market_research/README.md` | 3rd flow documentation, end-to-end guide |
| 2 | `requirements_market_research/_templates/findings_template.md` | Template for new findings.md files |
| 3 | `requirements_market_research/2026-02-14_german-mental-health-apps/raw/Copy of App Marktanalyse.json` | Migrated Gemini raw research (copy from explore task) |
| 4 | `requirements_market_research/2026-02-14_german-mental-health-apps/findings.md` | Structured findings extracted from Gemini JSON |
| 5 | `requirements_market_research/2023-11_initial-market-overview/raw/initial research november 2023.md` | Migrated older research (copy from explore task) |
| 6 | `requirements_market_research/2023-11_initial-market-overview/findings.md` | Structured findings extracted from Nov 2023 research |
| 7 | `.claude/skills/apply-market-research/skill.md` | New push-workflow skill (Mode A + Mode B) |

### Modified files (3 skills + 2 example targets = 5)
| # | Path | Change |
|---|------|--------|
| 8 | `.claude/skills/explore-requirements/skill.md` | +1 line: check market research before finalizing |
| 9 | `.claude/skills/create-impl-task/skill.md` | +1 line: flag market research backing or gap |
| 10 | `.claude/skills/modify-user-needs/skill.md` | +1 line: accept market research as business exclusion source |
| 11 | `requirements_tasks/functional/shared/epic_security/feat_database_encryption/requirements.md` | Add `market_research_refs` YAML field (example application) |
| 12 | `requirements_user_needs/personas/dr_sarah/persona.md` | Add `scope_exclusions` entry sourced from market research (example application) |

**Total: 12 files created, 5 files modified = 17 file operations**

---

## Part 1: Folder Structure

### `requirements_market_research/` — project-level peer alongside `requirements_tasks/`, `requirements_user_needs/`

```
requirements_market_research/
├── README.md
├── _templates/
│   └── findings_template.md
├── 2026-02-14_german-mental-health-apps/
│   ├── raw/
│   │   └── Copy of App Marktanalyse.json    ← migrated from explore task
│   └── findings.md
└── 2023-11_initial-market-overview/
    ├── raw/
    │   └── initial research november 2023.md ← migrated from explore task
    └── findings.md
```

### Folder naming convention

`YYYY-MM_topic-slug/` — year-month prefix for chronological ordering, topic slug describes the research batch.

### `findings_template.md` — key structure

Each finding block:
```yaml
---
id: MR-[YYYY-MM-DD]-[NNN]
date: YYYY-MM-DD
source_batch: [folder name, e.g. 2026-02-14_german-mental-health-apps]
category: demand | quality | flow | exclusion
confidence: high | medium | low
---

## Finding MR-[YYYY-MM-DD]-[NNN]

**Statement**: [One clear, falsifiable statement]

**Evidence**: [Summary of evidence from raw data; quote where possible]

**Confidence**: [high | medium | low] — [brief justification]

**Primary output channel**: [demand → functional reqs | quality → non-functional | flow → user flows | exclusion → scope_exclusions]

**Applied to** (populated after running apply-market-research):
- [ ] [Target requirement or persona/scenario path]
```

### `requirements_market_research/README.md` — content outline

1. What is the 3rd flow and why it exists alongside user-needs and design-bridge flows
2. Four output channels: demand, quality, flow, exclusion
3. When to add new research (trigger: new competitor data, user survey, market report)
4. How to process raw → findings.md (use template, assign IDs, set category + confidence)
5. How to use `apply-market-research` skill (Mode A: to requirements, Mode B: to scope exclusions)
6. How to handle conflicts between the 3 flows (record decision, do not auto-resolve)
7. How to reevaluate when new research contradicts old findings (update `Applied to`, create decision record)
8. Folder naming and ID conventions
9. Relationship to `requirements_user_needs/README_17_SCOPE_EXCLUSIONS.md` and `README_8_CROSS-REFERENCING_SYSTEMS.md`

---

## Part 2: New Skill — `apply-market-research`

**Location**: `.claude/skills/apply-market-research/skill.md`

### Skill design

**Invocation**:
- Mode A: `"Use apply-market-research skill to push [findings.md path] to requirements"`
- Mode B: `"Use apply-market-research skill to push [findings.md path] to scope exclusions"`

### Mode A: Push to Requirements

1. Read `findings.md` at provided path
2. List all findings categorized `demand`, `quality`, or `flow`
3. For each finding, ask user: "Which requirement(s) should this influence?" (or present candidate matches from codebase grep)
4. For each confirmed connection:
   - Read target `requirements.md`
   - Add/update `market_research_refs` YAML block:
     ```yaml
     market_research_refs:
       - finding: MR-2026-02-14-001
         source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md
         influence: "[brief influence description]"
     ```
   - Write back requirements.md
5. Check for conflict signals: if a finding contradicts an existing `user_needs` reference in the requirement, surface the conflict and ask user to create a decision record
6. Update findings.md: mark each applied finding's `Applied to` checklist

### Mode B: Push to Scope Exclusions

1. Read `findings.md` at provided path
2. List all findings categorized `exclusion`
3. For each exclusion finding, ask: "Which persona(s) and/or scenario(s) should receive this exclusion?"
4. For each confirmed target:
   - Read target `persona.md` or `scenario.md`
   - Add `scope_exclusions` entry using README_17 schema:
     ```yaml
     scope_exclusions:
       - area: "[excluded use case area]"
         reason: business
         reason_detail: "[Finding: MR-[ID]. Source: requirements_market_research/[batch]/findings.md]"
         reconsider_in: "[optional version string]"
     ```
   - Reset `review_status: in_review` and add `review_history` entry (same as `modify-user-needs` protocol)
   - Run downstream check: warn if existing scenarios overlap with new exclusion area
5. Update findings.md: mark `Applied to` checklist

### Skill token budget

The skill content should be compact. Estimated length: ~40-50 lines following the pattern of existing skills.

---

## Part 3: Skill Updates (MINIMAL — token efficiency)

Each addition is a single compact sentence/line. These additions go at the end of the relevant section in each skill.

### `explore-requirements/skill.md`

**Location to insert**: End of section **1.4 Read Requirement Hierarchy** (after the existing "Think:" block).

**Exact text to add** (1 line):

```
**Market research**: Before finalizing requirements for functional features, check `requirements_market_research/*/findings.md` for relevant findings → add `market_research_refs` YAML if found (see README.md in that folder for format).
```

---

### `create-impl-task/skill.md`

**Location to insert**: End of section **2.3 Estimate Size** (after the "If Large" note, before Phase 3 header).

**Exact text to add** (1 line):

```
**Market research backing**: Note in goal.md whether the feature has market research support (`requirements_market_research/*/findings.md`) or explicitly lacks it — an undocumented absence is a gap worth flagging.
```

---

### `modify-user-needs/skill.md`

**Location to insert**: In section **When Modifying `scope_exclusions`** (at the very start of that section, before the current first sentence).

**Exact text to add** (1 line):

```
**Market research as source**: Findings categorized `exclusion` in `requirements_market_research/*/findings.md` are a valid authoritative source for `reason: business` exclusions; ensure `reason_detail` cites the finding ID and source path.
```

---

## Part 4: Example Applications

### Example A — Add `market_research_refs` to a requirement

**Target**: `requirements_tasks/functional/shared/epic_security/feat_database_encryption/requirements.md`

**Rationale**: The Gemini research provides strong evidence that data protection is a primary concern for German mental health app users, and that DiGA apps (the gold standard comparison) require strict data handling. This directly supports the encryption feature's priority and approach.

**Addition to YAML frontmatter** (after existing fields, before `---`):

```yaml
market_research_refs:
  - finding: MR-2026-02-14-003
    source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md
    influence: "German market research confirms data protection as #1 user concern for mental health apps; DiGA standard (GDPR, EU servers, no ad tracking) sets the bar our app must meet to be credible in this market."
```

**Finding ID assignment**: MR-2026-02-14-003 (quality category: data protection expectation from German mental health app market)

---

### Example B — Add market-research-sourced `scope_exclusions` to a persona

**Target**: `requirements_user_needs/personas/dr_sarah/persona.md`

**Rationale**: The Gemini research clearly shows that social/community features have no presence in the successful CBT/DiGA app landscape. No DiGA app includes peer-to-peer community features; the market has not validated them for clinical settings. This is a business exclusion backed by competitor analysis.

**Addition to persona YAML `scope_exclusions`** (Dr. Sarah already has this field in her anti-traits section — the field needs to be added to YAML frontmatter):

Check the actual YAML structure first: Dr. Sarah's `persona.md` currently has no `scope_exclusions` field in the YAML frontmatter (the file ends after `pcd`). The field must be added after `pcd:` block.

```yaml
scope_exclusions:
  - area: "Social/community features (peer support forums, shared progress boards)"
    reason: business
    reason_detail: "No DiGA app or successful CBT app in the German market includes peer community features. Market research shows clinical therapists (like Dr. Sarah) view community features as antithetical to therapeutic relationship and data confidentiality. Finding: MR-2026-02-14-007. Source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md"
    reconsider_in: ""
  - area: "AI chatbot / automated therapeutic conversation"
    reason: business
    reason_detail: "German clinical psychotherapists (VT practitioners) are legally and professionally responsible for therapeutic interventions; AI chatbots conflict with their role and liability structure. While Woebot/Wysa are international self-care tools, they are not positioned as therapist-side workflow tools. Finding: MR-2026-02-14-005. Source: requirements_market_research/2026-02-14_german-mental-health-apps/findings.md"
    reconsider_in: "v3.0"
```

**Version change**: 4.1 → 4.2, `review_status: in_review`, new `review_history` entry.

---

## Findings Extraction Notes

### From Gemini research (`2026-02-14_german-mental-health-apps/findings.md`)

Based on the JSON content, extract these findings (proposed IDs MR-2026-02-14-001 through MR-2026-02-14-008):

| ID | Category | Statement |
|----|----------|-----------|
| MR-2026-02-14-001 | demand | Mood tracking + protocol/homework management is table-stakes in German CBT app market — all DiGA apps include it |
| MR-2026-02-14-002 | demand | Blended care (therapist assigns homework, client tracks, therapist reviews data) is the validated product model; Minddistrict confirms demand |
| MR-2026-02-14-003 | quality | Data protection is the primary non-functional concern for German mental health apps; DiGA certification requires EU server storage, no ad tracking, BfArM audit |
| MR-2026-02-14-004 | demand | German market is moving away from lifestyle/wellness apps toward prescription-backed (DiGA) evidence-based apps — credibility signal is critical |
| MR-2026-02-14-005 | exclusion | AI chatbot-led therapy conversations have no validated place in clinical (therapist-supervised) workflow in Germany; Woebot is self-care only |
| MR-2026-02-14-006 | flow | Therapist-assigns-homework → client-tracks → therapist-reviews session data flow is validated by Minddistrict blended care model |
| MR-2026-02-14-007 | exclusion | Social/community features (peer forums, progress sharing) are absent from all CBT/DiGA apps; no market validation in clinical context |
| MR-2026-02-14-008 | demand | Specialization over generalism: niche apps (e.g. somnio for insomnia, Velibra for anxiety) outperform all-in-one; our CBT protocol focus is validated |

**Confidence levels**: MR-002, MR-003, MR-006 = high (Minddistrict/DiGA evidence is concrete). MR-001, MR-004, MR-008 = medium (market trend inference). MR-005, MR-007 = medium (absence of evidence; valid but not direct proof).

### From Nov 2023 research (`2023-11_initial-market-overview/findings.md`)

Extract simpler findings from the Android app survey:

| ID | Category | Statement |
|----|----------|-----------|
| MR-2023-11-001 | demand | 15 mood tracking apps available in German App Store (Nov 2023); none offer clinical therapist workflow features |
| MR-2023-11-002 | quality | On-device-only storage is a differentiating privacy feature (MyMood, some others) vs. cloud storage with trackers (Bearable, Mood Chonk) |
| MR-2023-11-003 | demand | Multi-dimensional mood tracking (3+ axes) is standard in competitor apps for clinical use (uMore); single-dimension only serves journal/diary use case |

---

## Risks / Open Questions

### Risk 1: Finding ID assignment
The plan assigns finding IDs speculatively (MR-2026-02-14-001 etc.). During implementation, the implementer must assign these IDs by reading the actual Gemini JSON in order. The IDs in the example applications (Part 4) must be updated to match the final assigned IDs.

**Mitigation**: Assign IDs in findings.md first, then update Part 4 example references before writing to persona/requirement files.

### Risk 2: Dr. Sarah's persona YAML structure
The plan assumes `scope_exclusions` needs to be added to the YAML frontmatter. The current file ends after the `pcd:` block with no `scope_exclusions` field. The implementer must verify this before writing and use the correct YAML position (after `pcd`, before closing `---`).

**Mitigation**: Read `persona.md` fully before editing.

### Risk 3: `feat_database_encryption/requirements.md` YAML schema
This requirement uses a different YAML style (flat, with `trackable_items` array) compared to user_needs requirements. The `market_research_refs` field must be appended without breaking existing fields.

**Mitigation**: Read the file's current YAML fully; append `market_research_refs` as a new top-level YAML key after the existing last field (`depends_on`/`blocks`).

### Risk 4: Skill file line count for `apply-market-research`
New skills must be token-efficient. The skill should stay under 60 lines. If Modes A and B together would exceed this, consider a more compact table-driven format.

### Open Question: Should the `apply-market-research` skill also update the `findings.md` `Applied to` field automatically?
The plan says yes (both modes should mark findings as applied). This requires writing back to findings.md. This is low-risk but the implementer should confirm the user wants this behavior before finalizing.

### Open Question: Migration strategy — copy or move?
The raw files currently live in the completed explore task folder (`2026-02-14_explore-requirements (completed)/`). The plan is to **copy** them (not delete from original location), preserving the explore task's integrity. The implementer should confirm this preference.
