# Analysis Report: Market Research Quality & Workflow Evaluation
## TASK-PROC-029-03 | 2026-02-14

---

## Executive Summary

This report evaluates two market research batches (`2026-02-14_german-mental-health-apps` and `2023-11_initial-market-overview`) produced by TASK-PROC-029-02, assessing data quality, workflow soundness, and folder organisation. The overall verdict is: **the workflow structure is sound and well-designed, but the underlying data is weak in source provenance, and a significant gap exists in how `flow` findings are routed through the skill**. A total of 9 specific issues were identified across three evaluation areas. Three consolidated follow-up tasks are proposed: one for data quality governance (HIGH), one for filling coverage gaps (HIGH), and one for workflow and organisation fixes (MEDIUM).

---

## 1. Market Research Data Quality

### 1.1 Source Provenance Assessment — Most Significant Concern

This is the single most important quality issue in the current dataset.

**Batch 1: `2026-02-14_german-mental-health-apps`**

The raw source is a single Gemini 3 Pro conversation export (`raw/Copy of App Marktanalyse.json`). Although the run settings show `"enableSearchAsATool": true`, the model's thinking trace (marked `"isThought": true` in the JSON) reveals the model reasoning entirely from training knowledge:

> "I am now zeroing in on Cognitive Behavioral Therapy apps in German... I've formulated search terms to identify apps used clinically or highly rated as self-help tools based on CBT principles."

This is the model planning what to say, not citing retrieved web documents. No URL, publication, dataset reference, or timestamp is attached to any claim in the output. The findings.md itself correctly marks the source as "LLM (from Gemini 3 Pro research conversation)," which is accurate — but this means every finding from this batch is an **LLM-synthesized market opinion**, not market research in the verifiable sense.

**Batch 2: `2023-11_initial-market-overview`**

The raw source is a manual Android App Store survey (`raw/initial research november 2023.md`) with direct observations of 15 apps. This is methodologically stronger: observations are grounded in what the researcher actually saw. However, the survey is shallow: only 6 of the 15 listed apps (MyMood, uMore, Bearable, Mood Chonk, Reflexio, and one unnamed app in the notes) have substantive notes. The remaining 9 apps are listed by name only.

**Verdict**:

| Batch | Source Type | Verifiability | Depth | Methodological Strength |
|-------|-------------|---------------|-------|------------------------|
| 2026-02-14_german-mental-health-apps | LLM synthesis (Gemini) | None — no URLs, no citations | 8 findings | WEAK — no external validation |
| 2023-11_initial-market-overview | Manual App Store survey | Partial — direct observation | 3 findings, 6/15 apps with data | MODERATE — verifiable but shallow |

Neither batch would pass peer review as market research. Neither constitutes a primary source. This does not make the batches worthless — the content is plausible and useful as an initial orientation — but it means every finding carries an implicit caveat about unverified provenance.

**Recommendation**: Establish minimum source quality standards (see Task C below).

---

### 1.2 Coverage Analysis

The two batches together cover 8 distinct topic areas, all partially. The table below shows what is and is not covered, with gap severity for product decisions.

| Topic | Covered? | Batch | Confidence | Gap Severity |
|-------|----------|-------|------------|-------------|
| Competitor feature sets (DiGA/CBT apps) | Partial | 2026-02-14 | Medium | Low — adequate for v1 orientation |
| Competitor feature sets (mood tracking apps) | Partial | 2023-11 | Medium | Low — 6/15 apps have data |
| DiGA regulatory landscape | Yes | 2026-02-14 | Medium* | Medium — no primary BfArM source |
| Data protection expectations | Yes | Both | Medium* | Low — consistent signal across batches |
| Blended care model validation | Yes | 2026-02-14 | Medium* | Low — Minddistrict is real |
| Market direction (DiGA vs. wellness) | Yes | 2026-02-14 | Medium* | Low — plausible trend claim |
| Scope exclusions (AI chatbots, community) | Yes | 2026-02-14 | Medium | Low — absence-of-evidence noted |
| Multi-dimensional tracking as standard | Yes | 2023-11 | Medium | Low |
| **Pricing / business models** | **No** | — | — | **HIGH** |
| **User demographics / therapy experience** | **No** | — | — | **HIGH** |
| **Retention / churn data** | **No** | — | — | **HIGH** |
| **Therapist workflow needs (beyond Minddistrict)** | **Minimal** | 2026-02-14 | Low | **HIGH** |
| **App Store ratings / user satisfaction** | **No** | — | — | **MEDIUM** |
| **Accessibility requirements** | **No** | — | — | **MEDIUM** |
| **Market size / TAM** | **No** | — | — | **MEDIUM** |
| **Regulatory trajectory (DiGA process changes)** | **No** | — | — | **MEDIUM** |

*Confidence downgraded from "high" in findings.md because source is LLM-synthesized, not primary research.

The HIGH-severity gaps — pricing, demographics, retention, therapist needs — are all topics where product strategy decisions cannot be made from the current data. These need a dedicated primary-source research round.

---

### 1.3 Confidence Level Calibration

Three findings in the 2026-02-14 batch are marked "high" confidence. This section reviews whether each rating is defensible.

| Finding | Stated Confidence | Stated Justification | Assessment |
|---------|------------------|---------------------|------------|
| MR-2026-02-14-002 (blended care validation) | high | "Minddistrict is a concrete, operating platform" | **Overstated.** Minddistrict exists, but the description of its workflow comes from Gemini's training data, not from Minddistrict's own documentation, user interviews, or official materials. Should be **medium**. |
| MR-2026-02-14-003 (data protection / DiGA) | high | "DiGA certification requirements are regulatory fact" | **Defensible but incomplete.** DiGA requirements are publicly documented by BfArM. The specific claims (EU-only storage, no ad tracking) are consistent with known regulatory facts. This can retain "high" *only if* verified against the BfArM primary source. Pending verification: treat as **medium**. |
| MR-2026-02-14-006 (therapist-assigns-homework flow) | high | "Minddistrict is a concrete operating platform confirming this exact flow" | **Overstated for the same reason as MR-002.** The evidence for this flow comes from the same Gemini-synthesized description of Minddistrict. Should be **medium**. |

**Principle violated**: Confidence should reflect source quality, not just claim plausibility. An LLM asserting a fact about the market is not "high confidence" regardless of whether the claim is plausible. High confidence requires a verifiable, primary source backing the claim.

---

### 1.4 Categorization Quality

The findings use four categories: `demand`, `quality`, `flow`, `exclusion`. These are well-assigned:

| Category | Findings | Assessment |
|----------|----------|------------|
| demand | MR-2026-02-14-001, 002, 004, 008; MR-2023-11-001, 003 | Correctly assigned — all describe what the market shows demand for |
| quality | MR-2026-02-14-003; MR-2023-11-002 | Correctly assigned — both describe non-functional quality signals |
| flow | MR-2026-02-14-006 | Correctly assigned — validates a specific workflow pattern |
| exclusion | MR-2026-02-14-005, 007 | Correctly assigned — both document market-absent patterns |

No misclassifications found. The taxonomy works well for the content. The `exclusion` findings correctly acknowledge their "absence of evidence" basis at medium confidence, which is methodologically honest.

---

### 1.5 Source Diversity

Current source types: LLM conversation (batch 1), manual App Store browse (batch 2). Both are single-source-type batches.

**Missing source types that would strengthen the evidence base**:
- BfArM DiGA directory (primary source for all regulatory claims in MR-2026-02-14-003)
- App Store ratings and user reviews (primary source for user satisfaction data)
- Published peer-reviewed studies on CBT app efficacy in Germany
- Industry reports (e.g., Statista, McKinsey Health, BKK Dachverband digital health reports)
- Competitor company documentation (Minddistrict product pages, HelloBetter pricing, etc.)
- Therapist interviews or survey data

Using at least two different source types per batch, with at least one primary source, should be the minimum bar.

---

## 2. Workflow Soundness

### 2.1 Output Channel Coverage

The README defines four channels. The `apply-market-research` skill implements them via two modes.

| Channel | Category | README Target | Skill Implementation | Assessment |
|---------|----------|--------------|---------------------|------------|
| Feature priorities | `demand` | `requirements_tasks/functional/` | Mode A: Grep in `requirements_tasks/` | GOOD — clear, navigable path |
| Quality/design influence | `quality` | `requirements_tasks/non-functional/` | Mode A: Grep in `requirements_tasks/` | GOOD — clear, navigable path |
| User flow refinement | `flow` | `requirements_user_needs/user_flows/` | Mode A: Grep in `requirements_tasks/` | **BROKEN — skill targets wrong folder** |
| Scope exclusions | `exclusion` | `requirements_user_needs/personas/` or `scenarios/` | Mode B: asks which persona/scenario | GOOD — clear, integrates with README_17 schema |

**The `flow` channel gap is concrete**: Finding MR-2026-02-14-006 is categorized `flow` and its primary output channel is "flow > user flow validation." But if Mode A of the skill is used, it will search `requirements_tasks/` for candidates — not `requirements_user_needs/user_flows/`. The finding has no clear skill pathway to its correct destination. This is the most actionable workflow fix in this report.

**3 of 4 channels work correctly. The `flow` channel is misdirected.**

---

### 2.2 Friction Assessment

The skill integrations added in TASK-PROC-029-02 are reviewed for friction:

| Integration Point | Assessment |
|------------------|------------|
| `apply-market-research` skill — two clear modes | Low friction. The two-mode structure is clean and the key rules section prevents common errors. |
| Market research as 3rd flow in README | Low friction. The four-channel table in README.md is clear and immediately useful as a reference. |
| `market_research_refs` YAML field in requirements | Low friction. Field is additive, doesn't break existing schema. |
| `scope_exclusions` integration with README_17 schema | Low friction. Follows established convention exactly. |
| Conflict surfacing (not auto-resolving) | Appropriate constraint. Risk of skipping is low because Mode A explicitly checks for contradictions. |

The skill additions are minimal, well-placed, and unlikely to be skipped. The conflict check in Mode A step 5 is particularly well-designed: it is a checkpoint, not a full procedure.

---

### 2.3 Conflict Handling — Operational Gap

The README describes conflict handling at a conceptual level: do not auto-resolve, create a decision record, note which flow won. This is the right policy. However, the implementation is incomplete:

- **No decision record template**: Where do decision records live? What fields do they contain? The README mentions "create a decision record" but does not specify a location (in the research batch folder? in a `decisions/` subfolder? as a separate file?), fields (conflicting claims, resolution, who decided, date), or naming convention.
- **No conflict detection heuristic**: What constitutes a "contradiction" is not defined. Is it when a market finding says "no demand" but a persona includes a feature? Or only when two findings make opposing explicit claims? Without a heuristic, different agents will apply the conflict check inconsistently.

Both issues reduce the conflict handling process from "operational" to "aspirational." A concrete template would resolve both gaps.

---

### 2.4 Reevaluation Mechanism — Trigger Gap

The README describes the reevaluation process clearly: new findings reference old ones, old findings get "Superseded by" notes, downstream requirements are reviewed. This is correct and sufficient as a procedure.

However, two operational gaps remain:

- **No trigger**: When should reevaluation occur? The process describes *how* to reevaluate but not *when*. Is it triggered by the addition of any new batch? On a schedule? When a finding reaches a certain age? Without a trigger, reevaluation only happens if a team member actively remembers to do it.
- **No staleness indicator**: A finding from November 2023 (MR-2023-11-001 through 003) has no "review by" date. The DiGA landscape changes frequently — new apps receive DiGA certification, others lose it, regulations update. A 2-year-old LLM-synthesized finding about the market can go stale silently with no signal to the team.

---

### 2.5 Application Completeness — Tracking Gap

| Batch | Total Findings | Applied | Unapplied |
|-------|---------------|---------|-----------|
| 2026-02-14_german-mental-health-apps | 8 | 3 (MR-003, MR-005, MR-007) | 5 (62.5%) |
| 2023-11_initial-market-overview | 3 | 0 | 3 (100%) |
| **Total** | **11** | **3 (27%)** | **8 (73%)** |

73% of findings have never been applied to any requirement or persona. The only tracking mechanism is the `Applied to` checklist inside each findings.md file, which requires manual inspection of every batch to assess completeness. There is no summary view, no dashboard, and no mechanism that alerts when findings sit unapplied. The workflow has no enforcement: the `apply-market-research` skill can be called selectively or skipped entirely.

---

## 3. Data Organisation

### 3.1 Folder Structure Assessment

| Element | Convention | Actual | Assessment |
|---------|-----------|--------|------------|
| Root location | Peer with `requirements_tasks/`, `requirements_user_needs/` | `requirements_market_research/` at project root | CORRECT |
| `_templates/` folder | Standard convention | Present | CORRECT |
| `raw/` subfolder per batch | Specified in README | Present in both batches | CORRECT |
| Separation of raw vs. structured | Raw in `raw/`, analysis in `findings.md` | Implemented | CORRECT |
| Scalability | Chronological ordering by date prefix | Works with 2 batches | SOUND — will scale |

The folder structure is well-designed and follows project conventions. The separation of raw source material from structured analysis is the right pattern. No structural changes are needed.

---

### 3.2 Naming Convention Inconsistency

The README states the naming convention as `YYYY-MM-DD_topic-slug/`. The two existing batches do not consistently follow this:

| Batch Folder | Format Used | README Convention | Consistent? |
|-------------|------------|-------------------|-------------|
| `2026-02-14_german-mental-health-apps` | YYYY-MM-DD | YYYY-MM-DD | YES |
| `2023-11_initial-market-overview` | YYYY-MM (no day) | YYYY-MM-DD | **NO** |

This inconsistency propagates into finding IDs: `MR-2023-11-001` vs `MR-2026-02-14-001`. Any automated tooling or Grep-based search that parses IDs by date format will behave differently for the two batches. The fix is to rename the older folder to `2023-11-01_initial-market-overview` (using first-of-month when exact date is unknown) and update finding IDs accordingly.

---

### 3.3 Template vs. Reality Divergence

The `_templates/findings_template.md` shows a flat Markdown format with bold-label fields per finding block. The actual findings files also use flat Markdown with bold labels. This is consistent.

However, two divergences exist:

| Element | Template | Actual Files | Gap |
|---------|---------|-------------|-----|
| File-level header | Not present | Present (`Source batch`, `Raw data`, `Extracted`, `Extracted by`) | Template is incomplete — missing header section |
| Per-finding field labels | `**Category**:`, `**Confidence**:`, etc. | Same format | CONSISTENT — no gap |
| YAML frontmatter | Not used | Not used | CONSISTENT — no gap |

The plan document for TASK-PROC-029-02 mentioned YAML frontmatter per finding, but neither the template nor the actual files use it. The Markdown format is more readable and is correctly consistent between template and reality. The only fix needed is adding the file-level header to the template.

---

### 3.4 Discoverability Gap

The README.md describes the folder structure and workflow but contains no index of existing research batches. Anyone (human or AI agent) arriving at `requirements_market_research/` for the first time must traverse subfolders to understand what research exists, what it covers, and what has been applied.

A Research Batch Index table in README.md would address this:

```markdown
## Research Batch Index

| Batch | Date | Topic | Findings | Applied | Source Type |
|-------|------|-------|----------|---------|-------------|
| 2026-02-14_german-mental-health-apps | 2026-02-14 | German CBT/DiGA app landscape | 8 | 3/8 | LLM synthesis (Gemini 3 Pro) |
| 2023-11_initial-market-overview | 2023-11 | Android mood tracking apps | 3 | 0/3 | Manual App Store survey |
```

This table would also serve as the application completeness dashboard (see Section 2.5), solving two problems with one addition.

---

## 4. Issue Summary

| # | Area | Severity | Issue |
|---|------|----------|-------|
| I-01 | Data Quality | CRITICAL | Batch 1 source is LLM synthesis with no verifiable citations; evidence chain goes through Gemini training data |
| I-02 | Data Quality | HIGH | 4 HIGH-severity coverage gaps: pricing, demographics, retention, therapist workflow needs |
| I-03 | Data Quality | HIGH | MR-2026-02-14-002 and MR-2026-02-14-006 marked "high" confidence; should be "medium" given LLM source |
| I-04 | Data Quality | MEDIUM | Batch 2 survey is shallow: 9/15 apps listed with no substantive data |
| I-05 | Workflow | HIGH | `flow` category in Mode A of `apply-market-research` skill is routed to `requirements_tasks/` instead of `requirements_user_needs/user_flows/` |
| I-06 | Workflow | MEDIUM | Conflict handling policy exists but has no decision record template or conflict detection heuristic |
| I-07 | Workflow | MEDIUM | No staleness trigger or `review_by` field on findings; 2023 findings can age silently |
| I-08 | Workflow | MEDIUM | 73% of findings unapplied with no tracking or enforcement mechanism |
| I-09 | Organisation | LOW | Naming inconsistency: `2023-11_*` vs `YYYY-MM-DD` convention; finding IDs inherit the inconsistency; template missing file-level header; no Research Batch Index in README |

---

## 5. Prioritized Follow-Up Tasks

### Task A (HIGH) — Data Quality Governance
**Name**: `2026-02-14_impl_data-quality-governance`
**Combines**: Issues I-01, I-03, I-07 (source standards, confidence recalibration, staleness tracking)

**Scope**:
1. Add a "Source Quality Standards" section to `requirements_market_research/README.md` defining:
   - Accepted source types: `primary_observation`, `primary_document`, `llm_synthesis`, `academic`, `industry_report`
   - Minimum quality bar per batch: at least one primary or academic source per batch
   - Confidence calibration rule: confidence reflects source quality, not claim plausibility; LLM synthesis caps at "medium" unless independently verified
2. Add `source_type` field to `_templates/findings_template.md`
3. Retroactively update `2026-02-14_german-mental-health-apps/findings.md`:
   - Add `source_type: llm_synthesis` to all findings
   - Downgrade MR-2026-02-14-002 and MR-2026-02-14-006 from "high" to "medium" with note: "Downgraded: source is LLM synthesis. Upgrade to high requires verification against Minddistrict primary documentation."
   - MR-2026-02-14-003 note: "Retain medium pending BfArM primary source verification. Upgrade to high after verification."
4. Add `review_by` field to findings template (suggest: 12 months for `llm_synthesis`, 18 months for primary sources)
5. Add reevaluation trigger to README: "When adding a new batch, scan existing batches for findings past their `review_by` date."

**Effort**: S (half-day — all changes are documentation, no code)

---

### Task B (HIGH) — Primary-Source Research Round
**Name**: `2026-02-14_explore_primary-source-research-round`
**Combines**: Issues I-02, I-08 (coverage gaps, application completeness)

**Scope**:
1. Conduct a new research batch targeting HIGH-severity coverage gaps using verifiable primary sources:
   - **Pricing/business models**: Check HelloBetter, Selfapy, Minddistrict pricing pages directly
   - **User demographics**: Consult published DiGA evaluation studies (BfArM annual reports are publicly available)
   - **Retention/engagement**: Search for published app efficacy studies (PubMed, Google Scholar)
   - **Therapist perspective**: Consult therapist-facing documentation from Minddistrict, MindDoc; if feasible, 2-3 brief informal interviews
2. Create batch folder: `YYYY-MM-DD_primary-source-validation/` using the resolved date
3. Apply all 8 currently unapplied findings before or in parallel with this batch (MR-2026-02-14-001, 002, 004, 006, 008; MR-2023-11-001, 002, 003)
4. Add Research Batch Index table to README.md (proposed in Section 3.4) so application completeness is visible at a glance

**Effort**: M (1-2 days — research requires external sources, not just configuration)

---

### Task C (MEDIUM) — Workflow and Organisation Fixes
**Name**: `2026-02-14_impl_workflow-organisation-fixes`
**Combines**: Issues I-05, I-06, I-09 (flow channel routing, conflict template, naming/template inconsistencies)

**Scope**:
1. Fix `apply-market-research` skill Mode A (`/.claude/skills/apply-market-research/skill.md`):
   - Add sub-step: "For findings with `Category: flow`, search `requirements_user_needs/user_flows/` instead of `requirements_tasks/`"
   - This ensures MR-2026-02-14-006 has a clear application pathway
2. Create conflict decision record template at `requirements_market_research/_templates/decision_record_template.md`:
   - Fields: conflicting finding IDs, what each claims, which flow took precedence, reasoning, human reviewer, date
   - Add reference to this template in the "Handling Conflicts" section of README.md
3. Rename `2023-11_initial-market-overview/` to `2023-11-01_initial-market-overview/` (use first-of-month for unknown exact date)
4. Update finding IDs `MR-2023-11-001`, `MR-2023-11-002`, `MR-2023-11-003` to `MR-2023-11-01-001`, `MR-2023-11-01-002`, `MR-2023-11-01-003` across all files that reference them
5. Update `_templates/findings_template.md` to include the file-level header (`Source batch`, `Raw data`, `Extracted`, `Extracted by`) matching the format in actual findings files

**Effort**: S (half-day — mechanical changes with one skill edit)

---

## 6. What Was Done Well

Before summarizing the gaps, it is worth noting what the TASK-PROC-029-02 implementation got right:

| Element | Assessment |
|---------|------------|
| Folder structure (`requirements_market_research/` as peer flow) | Clean, scalable, follows project conventions |
| README.md quality | Clear, comprehensive, immediately usable as a reference |
| Four-channel model (demand/quality/flow/exclusion) | Well-conceived taxonomy that maps findings to destinations cleanly |
| `market_research_refs` YAML field | Non-invasive, additive to existing requirement schema |
| `scope_exclusions` integration | Follows README_17 schema precisely — no schema drift |
| Conflict surfacing policy (no auto-resolve) | Correct design choice for a human-reviewed requirements process |
| LLM source disclosure | Both findings.md files correctly document "Extracted by: LLM" — the provenance issue is known, not hidden |
| `exclusion` findings with "absence of evidence" caveat | Epistemically honest — correctly notes that MR-005 and MR-007 are provisional |
| Two-mode skill structure | Low friction, clear separation between requirements (Mode A) and scope exclusions (Mode B) |

The foundation is solid. The issues identified in this report are refinements and gap-fills, not fundamental redesigns.

---

*Report written by execution agent for TASK-PROC-029-03.*
*Source files evaluated:*
- `requirements_market_research/README.md`
- `requirements_market_research/2026-02-14_german-mental-health-apps/findings.md`
- `requirements_market_research/2026-02-14_german-mental-health-apps/raw/Copy of App Marktanalyse.json`
- `requirements_market_research/2023-11_initial-market-overview/findings.md`
- `requirements_market_research/2023-11_initial-market-overview/raw/initial research november 2023.md`
- `requirements_market_research/_templates/findings_template.md`
- `.claude/skills/apply-market-research/skill.md`
