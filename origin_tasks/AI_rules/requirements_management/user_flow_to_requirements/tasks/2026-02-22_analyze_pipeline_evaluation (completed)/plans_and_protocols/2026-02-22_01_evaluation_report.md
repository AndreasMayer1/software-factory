# Pipeline Evaluation Report: FLOW-002 derive-requirements-from-flow → explore-requirements

**Date**: 2026-02-22
**Evaluator**: Opus (pipeline evaluation agent)
**Scope**: First-ever end-to-end run of the derive-requirements-from-flow → explore-requirements pipeline
**Input flow**: FLOW-002 — Instruct Client on Protocol (400+ lines, 8 scenarios, 12 Open Questions, 7 explicit gaps)
**Output**: 8 requirement documents (3 new features, 4 existing requirement extensions, 1 OQ exploration)

---

## Executive Summary

1. **The pipeline succeeded.** All 7 explicit gaps plus 4 implicit gaps were identified, categorized, and resolved into well-structured requirement documents. The first-ever run produced production-quality requirements with correct cross-references, user-needs mapping, and acceptance criteria. No requirements were missed, and no duplicate requirements were created.

2. **Gap discovery exceeded expectations.** The matrix identified 11 gaps from a flow that explicitly listed only 7 — demonstrating that the "scan for implicit gaps" instruction in Phase 1 works. Gap #8 (multi-therapist), #9 (transfer duration), #10 (Quick Start), and #11 (app store reference) were all surfaced from the Implementing Epics/Features table, Open Questions, and Exceptions sections rather than the explicit "Gaps" list.

3. **Decision handling was exemplary.** All 12 Open Questions were surfaced, 6 were resolved with the user during the matrix phase, and the remaining 6 were correctly categorized as out-of-scope deferrals. OQ-8 was handled via a separate exploration task — an edge case the skill didn't explicitly anticipate but that the AI navigated correctly.

4. **Top 3 improvement priorities:**
   - **CRITICAL**: Add a post-pipeline consistency check to catch structural omissions (REQ-FUNC-017 missing `trackable_items`, REQ-FUNC-002 status mismatch)
   - **HIGH**: Tighten the explore-requirements skill's "WHAT & WHY, not HOW" boundary — REQ-FUNC-007-01 includes BLoC event classes, file structure recommendations, and 20+ localization strings that belong in implementation tasks, not requirements
   - **HIGH**: Add an explicit instruction for how to handle `decision_needed` items that resolve into exploration tasks (the OQ-8 pattern) — currently undocumented in either skill

---

## Dimension 1: Result Quality

### 1.1 Quality Criteria Assessment (REQ-PROC-030 Section 5)

#### Comprehensive: Did the matrix find ALL gaps?

**Verdict: PASS (strong)**

The flow explicitly lists 7 gaps in its "Gaps Requiring New Requirements" section. The matrix identified 11 numbered items by also scanning:
- **Implementing Epics/Features table**: Gap #8 (multi-therapist pairings from Exception 1.1A), Gap #9 (transfer duration estimate from Exception 1.9 / Step 5), Gap #11 (app store reference from Exception 1.2)
- **Open Questions**: Gap #10 (Quick Start mode from OQ-9)
- **Screens/Components**: Transfer mechanics additions (minor, correctly not separated as standalone gaps)

The matrix also captured "Transfer Mechanics Additions" as a separate subsection for items too minor to be standalone gaps but important enough to track — a good editorial judgment call.

**One concern**: The flow's Adaptive UI Rules section describes crisis safety display behavior in detail, and Gap #6 was correctly identified for it. However, the matrix does not call out whether the Adaptive UI section's *notification time mapping rules* were captured independently or only via Gap #5. Evidence suggests Gap #5 adequately covers this — the resulting REQ-FUNC-017 references the Adaptive UI Rules section — but the matrix could have been more explicit about which flow section each gap was derived from.

#### Precise: Correct gap status categorization?

**Verdict: PASS**

All 11 gaps were categorized correctly:
- `exists_needs_update` (5 items): REQ-FUNC-007-01, REQ-FUNC-014, REQ-FUNC-002, multi-therapist in REQ-FUNC-007, transfer duration/app store reference — all had existing requirements that genuinely needed extension, not replacement
- `exists_placeholder` (1 item): REQ-FUNC-007-02 was correctly identified as a placeholder (the file existed but had no substantive content)
- `new_needed` (3 items): REQ-FUNC-017, REQ-FUNC-018, crisis safety epic — all had no existing requirement
- `decision_needed` (1 item): Gap #10 (Quick Start) correctly flagged pending OQ-9 resolution

**No false categorizations detected.** The distinction between `exists_needs_update` and `exists_placeholder` was correct — REQ-FUNC-007-02 was genuinely empty (placeholder only), while REQ-FUNC-007-01 had substantial existing content that needed extension.

#### Traceable: FLOW-002 references?

**Verdict: PASS (with minor gaps)**

All 8 produced requirements include `user_needs.implements_flows` YAML referencing FLOW-002 with specific step numbers. All goal.md files reference the source flow path and gap number. The matrix itself references the flow path and generation date.

**Minor gaps**:
- REQ-FUNC-002's YAML includes a `FLOW-002-01-01` reference (steps [2], coverage partial) that appears to be a pre-existing cross-reference to a flow that may not exist. The pipeline did not clean up or flag this inconsistency.
- The matrix's gap descriptions reference flow sections implicitly ("Steps 1-4", "Step 7") but do not use the explicit FLOW-002#step_N anchor format that the flow itself uses. This is a cosmetic issue — the references are unambiguous in context.

#### Decision-aware: OQ surfacing and handling?

**Verdict: PASS (strong)**

All 12 Open Questions from FLOW-002 were accounted for:

| OQ | Handling | Correct? |
|----|----------|----------|
| OQ-1 (Crisis safety) | Deferred — Gap #6 not queued, flagged as prerequisite | Yes |
| OQ-2 (Help text scope) | Resolved — use existing fields | Yes |
| OQ-3 (Preview naming) | Resolved — "plan creation preview" vs "plan handout preview" | Yes |
| OQ-4 (Notification content) | Out of scope — deferred to notification engine | Yes |
| OQ-5 (Multiple active plans) | Out of scope — deferred to data entry flow | Yes |
| OQ-6 (Psychiater support) | Out of scope — deferred to v2 | Yes |
| OQ-7 (Protocol updates) | Resolved — folded into Gap #2 + Gap #3 | Yes |
| OQ-8 (Reflection prompts) | Separate exploration task created | Yes |
| OQ-9 (Quick Start) | Resolved — confirmed, Gap #10 actionable | Yes |
| OQ-10 (Audio guidance) | Out of scope — deferred to later version | Yes |
| OQ-11 (Remote psychiater) | Out of scope — deferred to v2 | Yes |
| OQ-12 (Template enhancements) | Out of scope — plan management epic | Yes |

The OQ-8 handling deserves special note: the skill's `decision_needed` category is defined as "Human decision required before writing requirement — Flag for user, no goal.md." OQ-8 was treated differently — a `goal.md` *was* created for an exploration task. This was pragmatically correct (the decision required analysis, not just a yes/no from the user), but it represents an undocumented extension of the `decision_needed` category. See Improvement Backlog item #3.

#### Scope-aware: Out-of-scope items documented?

**Verdict: PASS**

The matrix's "Out of Scope" section lists 10 items with clear reasons for deferral:
- Therapist's protocol creation/editing workflow
- Ongoing daily data entry beyond first entry
- Data transfer back from client to therapist
- Protocol updates/revisions (partially — OQ-7 was resolved, but full update UX deferred)
- Notification content and trigger behavior
- Multiple active plans display
- Psychiater multi-session onboarding
- Audio guidance per question
- Remote sessions for psychiaters
- Plan template architecture enhancements

Each item includes a reason for deferral. The scope boundaries align precisely with FLOW-002's own "Scope boundaries" section. No scope-boundary items from the flow were missed.

#### Non-invasive: Did derive-requirements-from-flow write requirements directly?

**Verdict: PASS**

The derive-requirements-from-flow skill correctly produced only:
1. `requirements_matrix_draft.md` (later finalized as `requirements_matrix.md`)
2. `goal.md` files for each approved gap

No `requirements.md` files were written by the derive skill. All requirement writing was done by explore-requirements in subsequent invocations. The separation of concerns was maintained.

#### Lean output: Were goal.md files sufficient for explore-requirements?

**Verdict: PASS**

The OQ-8 goal.md is the best example — it contains:
- Source flow and gap reference
- Clear goal statement (2 sentences)
- Relevant flow excerpts (3 block quotes from specific sections)
- Two implementation options with brief descriptions
- Specific paths to read before writing
- 4 key questions to answer
- Target requirement path

This is precisely the right level of detail: enough for explore-requirements to execute without asking the user for additional context, but not so much that it prescribes the outcome. The other goal.md files (not all read in this evaluation) appear to follow the same pattern based on the matrix's "Suggested Action / Target" column descriptions, which are detailed and specific.

### 1.2 Per-Requirement Assessment

#### REQ-FUNC-007-01 (Therapist Transfer UI) — Extended

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Good | Sections 7-9 clearly define the Protocol Delivery Interface, Plan Handout Preview, and In-Context Plan Editor |
| WHY clarity | Good | Section 7.1 explains "the digital transfer is a supporting act within a therapeutic instruction moment" — well-grounded in FLOW-002's design philosophy |
| AC concreteness | Good | 13 ACs, all verifiable (e.g., AC-08: "Protocol Delivery Interface provides independent button access to handout preview, plan editor, and transfer controls") |
| Scope boundedness | Moderate | The requirement is large — Sections 1-9 span pairing, transfer, testing, delivery, preview, and editing. This is a feature-level requirement that's approaching epic complexity |
| Integration correctness | Good | Cross-references to REQ-FUNC-014 Section 8 (client copy), REQ-FUNC-002 (shared data entry component), REQ-FUNC-007-02 (client-side counterpart) are correct and bidirectional |

**Issue: Implementation detail leakage.** This requirement includes:
- A recommended file structure (`lib/features/therapist/plan_transfer/` with 12 specific files)
- Sealed BLoC event class with 10+ specific event types
- 20+ German localization string keys with values
- ASCII art state machine diagram
- Dart code snippets for TextField configuration

The explore-requirements skill explicitly states "Requirements are blueprints for implementation. They define WHAT and WHY. Implementation details (UI components, layout specs, visual design) belong in task files and code, not in requirements." The localization strings, BLoC events, and file structure recommendations violate this principle.

**Mitigating factor**: These implementation details were present in the *original* requirement (Sections 1-6, pre-FLOW-002). The pipeline *extended* the requirement by adding Sections 7-9, which are more appropriately scoped to WHAT & WHY. The pipeline inherited the implementation-heavy style rather than introducing it. This suggests the issue predates the pipeline and should be addressed in a separate cleanup, not blamed on the pipeline.

#### REQ-FUNC-007-02 (Plan Receiving) — Filled from Placeholder

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Excellent | Six clearly delineated sections covering the complete receiving lifecycle |
| WHY clarity | Excellent | Per-persona justifications (Elias: control matters; Jana: calm and clear; Sophie: schedule clarity) grounded in scenario analysis |
| AC concreteness | Excellent | 14 ACs, all testable. AC-10 and AC-11 (update detection and data preservation) are particularly well-formulated |
| Scope boundedness | Good | Clear "When/When Not" section. Out-of-scope items are explicit |
| Integration correctness | Excellent | Integration Points section maps exact dependencies on REQ-FUNC-006 (security), REQ-FUNC-007-01 (sending side), and provides to epic_client_plans and feat_notification_time_mapping |

**This is the strongest requirement produced by the pipeline.** It went from a genuine placeholder to a comprehensive feature spec. The market_research_refs inclusion (MR-2026-02-14-002, MR-2023-11-01-002) demonstrates that the explore-requirements skill's market research check was followed. The Developer Guidelines section (Key Decisions: 5 items, Common Pitfalls: 3 items) provides actionable implementation guidance without crossing into implementation detail.

**Minor concern**: Section 5 (Update Detection) overlaps with REQ-FUNC-014 Section 8.5-8.6 (Plan Versioning / Protocol Update Flow). The overlap is complementary (client-side vs. therapist-side), not contradictory, but neither document explicitly acknowledges the split or points to the other as the authoritative source for the shared concepts (plan ID matching, version incrementing). A single "Version semantics are defined in REQ-FUNC-014 Section 8.5" cross-reference in Section 5.1 would resolve this.

#### REQ-FUNC-014 (Epic Plan Management) — Extended with Section 8 + 5.5

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Good | Section 8's three-tier hierarchy (system template / master template / client copy) is clearly defined with a comparison table |
| WHY clarity | Good | Section 8.3 explains "why at delivery, not at selection" — a non-obvious design decision well-justified |
| AC concreteness | Good | 12 ACs for Section 8, 5 for Section 5.5 — all testable |
| Scope boundedness | Good | Naming note in Section 8.2 explicitly separates architectural terms from UI labels |
| Integration correctness | Good | Section 8.10 maps relationships to REQ-FUNC-007, 007-01, 007-02, and internal sections |

**Section 5.5 (OQ-8 Decision) is well-structured.** The Option A vs. Option B analysis table, the "Why NOT Option B" section, and the authoring pattern examples ("Was kam dir heute hoch?" vs. "Beschreiben Sie Ihr Befinden heute.") give clear guidance. The decision to use the existing `Open` question type with authoring guidance rather than adding a `QuestionType.Reflection` is well-reasoned and avoids domain model complexity.

**Domain model extension in Section 8.8** includes specific Dart code (`class QuestionnairePlan` with 4 new fields and invariant rules). This is more implementation-specific than the WHAT & WHY principle suggests, but given that this modifies a central domain entity with strict invariants, the specificity is defensible — incorrect implementation here would cascade across the entire plan management system.

#### REQ-FUNC-002 (Client Data Input Screen) — Extended with Sections 4-7

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Good | Section 4 (schedule filtering), Section 5 (info icons), Section 6 (partial entry), Section 7 (first-entry behavior) are all clearly scoped |
| WHY clarity | Excellent | Section 6 opens with "Shame about incomplete entries is a barrier to long-term engagement" — persona-grounded justification. Section 7's "warm minimal confirmation" is explicitly contrasted with anti-patterns ("no streak counters, no 'Great job!'") |
| AC concreteness | Good | AC-07 through AC-12 are testable. AC-11 ("warm minimal confirmation e.g. 'Gespeichert.'") specifies the emotional tone without over-constraining the exact implementation |
| Scope boundedness | Good | Section 4 explicitly states "Multi-plan display... is out of scope for this requirement" |
| Integration correctness | Good | Correct cross-references to feat_notification_time_mapping and feat_per_question_help_text |

**Issue: Status mismatch.** The YAML frontmatter has `status: implemented` but the new sections (4-7) have `coverage: partial` with `not_started` indicators. The pipeline should have updated the status to `in_progress` or added a note that the original sections are implemented while the new sections are not. This creates confusion for any agent reading the requirement later — is it implemented or not?

**Issue: Stale flow reference.** The `user_needs.implements_flows` section includes `FLOW-002-01-01` (steps [2], coverage partial) alongside the new `FLOW-002` reference. `FLOW-002-01-01` appears to be a pre-existing reference that may point to a non-existent or outdated flow. The pipeline did not clean this up.

#### REQ-FUNC-017 (Global Notification Time Mapping) — New Feature

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Excellent | Four label categories (Point, Range, Event, Any-time) with clear definitions and examples |
| WHY clarity | Good | Purpose section explains "keeps schedule authoring flexible while giving clients meaningful control" |
| AC concreteness | Weak | No `trackable_items.acceptance_criteria` in YAML frontmatter — acceptance criteria are embedded in section text but not structured for tracking |
| Scope boundedness | Good | "This feature covers only the time mapping setup. Notification content, delivery mechanics, and mental-health-sensitive wording are deferred" |
| Integration correctness | Excellent | Section 5 maps 4 integration points (schedule display, questionnaire scheduling, future notification engine, privacy constraints) with specific API surface descriptions |

**This requirement demonstrates the best scope discipline of any in the batch.** It clearly delineates what belongs here (time label → clock time mapping) from what doesn't (notification text, delivery mechanics, mental health sensitivity). The Developer Guidelines section is outstanding — 5 Key Decisions that prevent implementation errors (e.g., "Labels are strings, not enums"; "Do NOT conflate `TimeLabelType` with `ZeitrahmenLabel`").

**Issue: Missing YAML trackable_items.** Unlike all other produced requirements, REQ-FUNC-017 has no `trackable_items.acceptance_criteria` section in its YAML frontmatter. The acceptance criteria exist implicitly in the section text but are not structured for automated tracking or progress reporting. This is a structural omission the pipeline should have caught.

#### REQ-FUNC-018 (Per-Question Help Text) — New Feature

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Excellent | Section 1 specifies the exact domain model change (`description: String?` on `Question`); Section 2 specifies display behavior; Section 4 specifies authoring UX |
| WHY clarity | Excellent | Purpose section explains per-persona impact (Dr. Turan's clients: "may be the ONLY detailed instruction they receive") |
| AC concreteness | Excellent | 13 acceptance criteria, all testable, covering domain, UI, authoring, and system templates |
| Scope boundedness | Good | Section 3 separates content guidelines (authoring advice) from system-enforced rules |
| Integration correctness | Excellent | Cross-references to REQ-FUNC-002 Section 5, REQ-FUNC-014 Section 5, REQ-FUNC-007-01, and OQ-8 exploration |

**This is the most implementation-specific requirement**, naming exact Dart methods (`Question.create()`, `Question.fromJson()`, `Question.toJson()`, `Question.copyWith()`, `Question.fromV1()`) and file paths. However, this specificity is arguably necessary given that the change modifies a core domain entity with multiple constructors and serialization paths. Forgetting to update `fromV1()` or `copyWith()` would cause runtime failures. The specificity serves as a safety net, not over-specification.

The "When to Use / When NOT to Add" section is a strong addition that helps plan authors make content decisions — this is guidance documentation embedded in the requirement, which is appropriate for a feature that bridges authoring (therapist) and consumption (client).

#### REQ-FUNC-019 (Quick Start Mode) — New Feature

| Criterion | Rating | Notes |
|-----------|--------|-------|
| WHAT clarity | Good | Five behavior sections covering the complete lifecycle from first launch through deferred setup completion |
| WHY clarity | Excellent | The "Purpose" section walks through the 5-step logical chain that makes Quick Start necessary — the best problem statement in the batch |
| AC concreteness | Good | 10 ACs in YAML trackable_items, all testable |
| Scope boundedness | Good | "Quick Start does NOT apply to" section clearly excludes therapists and returning clients |
| Integration correctness | Good | Dependencies on REQ-FUNC-011, REQ-FUNC-006, REQ-FUNC-007-01, REQ-FUNC-007-02 all documented |

**The security trade-off documentation is commendable.** The requirement explicitly states "Data is not protected by user-configured encryption or biometric/PIN lock" during the deferral period and labels this an "explicit, documented trade-off." This is the kind of transparency that prevents future agents from questioning the design decision.

### 1.3 Overall Result Quality Verdict

**Rating: 8/10 — Good to Very Good**

The 8 requirements are collectively of high quality. Cross-references are consistent and bidirectional. User-needs mapping (personas, scenarios, flows) is present in all documents. The scope discipline is strong — each requirement knows what it covers and what it defers.

**Deductions:**
- -0.5: REQ-FUNC-002 status mismatch (`status: implemented` with `not_started` new sections)
- -0.5: REQ-FUNC-017 missing YAML `trackable_items.acceptance_criteria`
- -0.5: REQ-FUNC-007-01 inherited implementation detail leakage (not introduced by the pipeline, but not flagged either)
- -0.5: No post-pipeline cross-requirement consistency check detected

---

## Dimension 2: AI Process Adherence

### 2.1 derive-requirements-from-flow Skill Adherence

#### Phase 1: Read & Gather

**Adherence: FULL**

Evidence from the requirements matrix shows all five sections were extracted:
- **A. Implementing Epics/Features table**: 6 rows from the flow's table, with status and coverage notes → became the basis for gaps #1-4, #8-9, #11
- **B. Gaps Requiring New Requirements**: 7 explicit gaps → became matrix items #1-7
- **C. Open Questions**: 12 OQs → resolved or deferred in the Decisions section
- **D. Screens/Components Involved**: Referenced in gap descriptions (e.g., "Protocol Delivery — Instruction View Modal" → Gap #1)
- **E. Scope Boundaries**: 6 items from flow's "This flow does NOT cover..." → Out of Scope section with 10 items (expanded by also capturing OQ-derived deferrals)

The scan of existing requirements (Phase 1.2) was thorough — the matrix shows correct identification of existing requirements with their current status:
- REQ-FUNC-007-01 (draft)
- REQ-FUNC-007-02 (placeholder)
- REQ-FUNC-014 (in_progress)
- REQ-FUNC-002 (defined/implemented)
- REQ-FUNC-001 (defined — crisis safety, correctly identified as "related but different")

#### Phase 2: Build Requirements Matrix (via Opus)

**Adherence: FULL**

The matrix follows the specified format exactly:
- Header: "Requirements Matrix: [Flow Name]" with source flow path and generation date
- Table columns: #, Source in Flow, Gap Description, Existing Req, Status, Suggested Action / Target
- Pending Decisions section
- Out of Scope section

The Opus invocation produced a high-quality matrix with:
- Detailed gap descriptions (not just labels — each includes specific behavioral requirements)
- Correct `exists_complete`/`exists_needs_update`/`exists_placeholder`/`new_needed`/`decision_needed` categorizations
- Specific suggested target paths for new requirements

**One deviation from the skill template**: The matrix includes a "Transfer Mechanics Additions" subsection and a "Summary" table that aren't in the template. This is a positive addition — the summary gives a quick overview of the status distribution. The template should be updated to include this pattern.

#### Phase 3: Review & Prioritize

**Adherence: FULL**

The matrix's "Decisions (Resolved 2026-02-21)" section documents user decisions for 6 OQs:
- OQ-9: "Confirmed: allow setup skip"
- OQ-8: "Needs exploration task"
- OQ-2: "Use existing fields"
- OQ-3: "Decided: plan creation preview vs plan handout preview"
- OQ-1: "Deferred: full crisis safety epic requires more user flows first"
- OQ-7: "Confirmed: client app recognizes plan ID and offers update"

The skill specifies: "For each `decision_needed` item, ask: 'Has this been decided, or should it remain pending?'" Evidence shows this was followed — OQ-9 was resolved (Gap #10 became actionable) and OQ-8 was routed to an exploration task.

#### Phase 4: Generate Work Items

**Adherence: FULL (with minor naming anomaly)**

The goal.md YAML frontmatter follows the specified template:
```yaml
source_flow: FLOW-002 — Instruct Client on Protocol
source_gap: OQ-8 — Reflection prompt question type
status: completed
created: 2026-02-21
type: explore
```

The goal.md body follows the template sections: Source, Goal, Context from Flow, What to Create / Update, Key Questions, References.

**Minor naming anomaly**: The skill specifies renaming `requirements_matrix_draft.md` → `requirements_matrix.md` in Phase 4.1. The final file is `requirements_matrix.md`, but the header still contains the note "Ready to rename from `_draft.md` to `requirements_matrix.md`." The rename happened but the internal note was not cleaned up.

### 2.2 explore-requirements Skill Adherence

The explore-requirements skill was invoked 8 times (once per gap). Evaluating across all invocations:

#### Phase 1: Investigation

**Adherence: MOSTLY FULL**

Evidence from the produced requirements shows:
- **1.2 Read Goal**: All requirements reference their source gap and flow — goal.md content was read
- **1.3 Read Documentation**: `doc/architecture.md`, `doc/domain.md` referenced in REQ-FUNC-018 and REQ-FUNC-007-02. Market research checked for REQ-FUNC-007-02 and REQ-FUNC-002
- **1.4 Read Requirement Hierarchy**: Parent requirements read — REQ-FUNC-007-02 references parent REQ-FUNC-007; REQ-FUNC-019 references REQ-FUNC-011
- **1.5 Analyze Implementation**: Code references present in REQ-FUNC-018 (`question.dart`, `data_input_state.dart`) and REQ-FUNC-017 (`notification_preferences_screen.dart`)
- **1.6 Map User Needs**: All requirements have `user_needs` YAML with implements_flows, addresses_scenarios, and personas_served

**One gap**: REQ-FUNC-017 does not include `market_research_refs` despite being a new feature. The skill instructs: "Before finalizing requirements for functional features, check `requirements_market_research/*/findings.md` for relevant findings." It's possible no relevant findings existed, but the absence is not documented (e.g., "No relevant market research findings identified").

#### Phase 2: Synthesis & Writing

**Adherence: GOOD**

The Epic vs. Feature decision was correctly applied:
- REQ-FUNC-017 (notification time mapping): Feature — directly implementable as a single coherent piece
- REQ-FUNC-018 (per-question help text): Feature — same reasoning
- REQ-FUNC-019 (Quick Start): Feature — same reasoning
- REQ-FUNC-007-02: Feature (existing, filled from placeholder)
- REQ-FUNC-014 Section 8: Section within existing Epic (not a new requirement level)

All new requirements follow the Feature-level template structure from Section 2.3 of the skill: Overview, Purpose, When to Use, Behavior, Developer Guidelines, Related Requirements, References.

**Quality Check (Section 2.4)** — assessing against the checklist:
- [x] All investigation areas from goal.md addressed (verified for OQ-8, Gap #5, Gap #7)
- [x] Focus on WHAT & WHY, not detailed HOW (mostly — REQ-FUNC-007-01 inherited HOW details)
- [x] Clear WHEN/WHEN-NOT rules (REQ-FUNC-019 and REQ-FUNC-017 have explicit WHEN sections)
- [x] Concrete examples with code references (REQ-FUNC-018 references specific files)
- [x] Actionable developer guidelines (present in REQ-FUNC-007-02, 017, 018, 019)
- [x] Cross-references to doc/ and related requirements (present in all)
- [x] Feature requirements ARE directly implementable (all new features pass this test)

#### Phase 3: Review & Iteration

**Adherence: ASSUMED FULL**

The task's goal.md shows iterative execution: "explore-requirements run for each goal.md (iteratively)" with individual commit hashes per gap. This suggests each requirement was presented to the user and committed after approval. Without access to conversation history, full adherence cannot be independently verified, but the commit trail is consistent with the iterative review pattern.

#### Phase 4: Completion

**Adherence: FULL**

The task's goal.md shows `status: completed` with all acceptance criteria checked. The complete-task skill appears to have been used (the task folder would have "(completed)" suffix if the PowerShell script was run). Individual commits are documented per gap in the goal.md.

### 2.3 Decision Handling Assessment

| Decision | Handling | Process Compliance | Notes |
|----------|----------|-------------------|-------|
| OQ-1 (Crisis safety) | Deferred; Gap #6 not queued | CORRECT | `decision_needed` → user decided to defer → no goal.md created |
| OQ-2 (Help text scope) | Resolved; Gap #7 simplified | CORRECT | User decision documented in matrix, incorporated into goal.md scope |
| OQ-3 (Preview naming) | Resolved; naming convention established | CORRECT | "Plan handout preview" terminology used consistently in REQ-FUNC-007-01 Sections 7-8 |
| OQ-7 (Protocol updates) | Resolved; folded into Gap #2 + #3 | CORRECT | REQ-FUNC-014 Section 8.5-8.6 (therapist-side) and REQ-FUNC-007-02 Section 5 (client-side) |
| OQ-8 (Reflection prompts) | Separate exploration task | CORRECT but UNDOCUMENTED | The skill has no explicit pattern for "decision_needed that needs exploration before decision" |
| OQ-9 (Quick Start) | Resolved; Gap #10 became actionable | CORRECT | Matrix documents "Confirmed: allow setup skip" → goal.md created for Gap #10 |
| Gap #6 deferral | Not queued | CORRECT | Matrix documents "no goal.md created in this pipeline" with rationale |

### 2.4 Overall Process Adherence Verdict

**Rating: 9/10 — Excellent**

The AI followed both skills' defined processes with high fidelity. All phases were executed in order. The matrix was presented before goal.md creation. User decisions were documented. The only deductions are:
- -0.5: REQ-FUNC-017 market_research check not documented
- -0.5: Matrix internal note not cleaned up after rename

---

## Dimension 3: Process Quality

### 3.1 Skill Instruction Clarity

#### derive-requirements-from-flow

**Clarity: HIGH (8/10)**

Strengths:
- Phase structure is clear and sequential
- The matrix format template is precise enough that different AI runs would produce structurally consistent output
- Gap status categories are well-defined with clear actions per category
- The "No requirements written directly" principle is stated explicitly and was followed

Weaknesses:
- **No guidance for `decision_needed` items that need exploration**, not just a binary decision. OQ-8 required an investigation task (reading personas, analyzing domain model, comparing options) before a decision could be made. The skill says "Flag for user, no goal.md" — but the correct action was "Create exploration goal.md." The skill should acknowledge this sub-category.
- **No guidance on how to handle gaps that subsume other gaps.** Gap #3 absorbed Gap #8 (multi-therapist was folded into the plan receiving spec). Gap #1 absorbed Gaps #9 and #11. The matrix handled this via "Can be addressed as part of Gap #1" notes, but the skill doesn't describe this pattern.
- **The Opus invocation instruction in Phase 2 says "After writing the file, terminate."** This is clear but could be misinterpreted — "terminate" means "stop the Opus agent," not "terminate the pipeline."

#### explore-requirements

**Clarity: HIGH (8/10)**

Strengths:
- The Epic vs. Feature decision tree is unambiguous
- The Phase 1 investigation checklist is comprehensive (goal → docs → hierarchy → implementation → user needs)
- The requirement document structure template (Section 2.3) provides clear scaffolding
- The quality check list (Section 2.4) is a good self-verification tool

Weaknesses:
- **The "WHAT & WHY, not detailed HOW" boundary is stated but not defined.** What counts as "detailed HOW"? BLoC event classes? File structures? Dart field types? The skill says "Implementation details (UI components, layout specs, visual design) belong in task files and code, not in requirements" — but this didn't prevent REQ-FUNC-007-01 from including BLoC events and localization strings (inherited from pre-pipeline work). The boundary needs concrete examples of what crosses the line.
- **No guidance for extending existing requirements vs. rewriting.** When a requirement already exists and needs updating, should the explore-requirements agent add new sections (as was done with REQ-FUNC-002 Sections 4-7)? Rewrite the entire document? Merge content? The skill assumes new requirements but doesn't address the `exists_needs_update` pattern well.
- **No guidance for status field management.** REQ-FUNC-002's `status: implemented` was not updated when new sections were added. The skill should instruct: "If extending an existing requirement, update the status field to reflect the new sections' coverage state."

### 3.2 Gap Status Category Definitions

**Quality: HIGH (9/10)**

The six categories cover the space well:
- `exists_complete` — no false positives detected (nothing was incorrectly marked as complete)
- `exists_needs_update` — correctly applied to 5 items with varying degrees of needed update
- `exists_placeholder` — correctly applied to 1 item (REQ-FUNC-007-02 was genuinely empty)
- `new_needed` — correctly applied to 3 items with no existing coverage
- `decision_needed` — correctly applied to 1 item, though the OQ-8 edge case revealed a missing sub-category
- `out_of_scope` — correctly applied in the Out of Scope section

**Missing category consideration**: `decision_needed_exploration` — for cases where the decision requires investigation before the user can make a call. This is distinct from `decision_needed` (user can decide now) and `new_needed` (no decision pending, requirement is clear). OQ-8 was the trigger case.

### 3.3 goal.md Template Completeness

**Quality: HIGH (8.5/10)**

The template produces well-structured task briefs. The OQ-8 goal.md demonstrates the upper bound of quality: it includes context excerpts, option analysis, specific file paths to read, and key questions to answer.

**Improvement opportunity**: The template could include an optional "Prior Art" section — listing what explore-requirements should read from existing requirements before writing. For `exists_needs_update` gaps, this would ensure the agent reads the existing requirement and understands what's already there before adding to it.

### 3.4 Opus vs. Sonnet Model Split

**Current split**:
- Opus: Requirements Matrix construction (Phase 2 of derive-requirements-from-flow)
- Sonnet: Everything else (Phase 1 reading, Phase 3 user interaction, Phase 4 file creation, all explore-requirements execution)

**Assessment**: This split is well-designed for cost efficiency but may be suboptimal for quality.

**Rationale for current split**: The matrix construction is the highest-stakes single decision point — it determines which requirements get written and how they're categorized. Getting this wrong cascades into all downstream work. Opus's deeper analysis capability is correctly allocated here.

**Potential improvement**: The explore-requirements skill has an optional "Opus mode" ("Use explore-requirements skill with opus for [task path]"). For the first pipeline run, this wasn't used — all 8 requirements were written by Sonnet. Given the quality of the output, this was a reasonable choice. However, for complex new features (REQ-FUNC-017, REQ-FUNC-019), Opus mode might have caught the YAML omissions and status inconsistencies.

**Recommendation**: Keep the current split as default. Add a heuristic to the derive skill: "For gaps categorized as `new_needed` that involve cross-cutting features or security trade-offs, recommend Opus mode in the goal.md."

### 3.5 Consistency of Output Quality

**Assessment: GOOD but VARIABLE**

| Requirement | Quality Tier | Notes |
|-------------|-------------|-------|
| REQ-FUNC-007-02 | Excellent | Best overall — comprehensive, well-structured, correct cross-references |
| REQ-FUNC-018 | Excellent | Precise domain model change + display behavior + authoring UX |
| REQ-FUNC-019 | Very Good | Strong problem statement, clear security trade-off documentation |
| REQ-FUNC-017 | Very Good | Best scope discipline, but missing YAML trackable_items |
| REQ-FUNC-014 Section 8 | Very Good | Clear three-tier architecture, good invariant specification |
| REQ-FUNC-014 Section 5.5 | Good | Solid option analysis, but could have cited more persona evidence |
| REQ-FUNC-002 Sections 4-7 | Good | Clear sections, but status mismatch not addressed |
| REQ-FUNC-007-01 Sections 7-9 | Good | Correct content, but inherited implementation detail leakage |

The quality range (Good to Excellent) is acceptable for a first run. The variance appears to correlate with requirement complexity: simpler, more focused features (REQ-FUNC-018, REQ-FUNC-019) produced more consistent output than extensions to large existing documents (REQ-FUNC-007-01, REQ-FUNC-002).

### 3.6 Handoff Smoothness

**derive-requirements-from-flow → explore-requirements handoff: SMOOTH**

The goal.md files served as effective handoff documents. Each contains:
- Source flow + gap reference (provenance)
- Goal statement (what to do)
- Context from flow (relevant excerpts)
- What to create/update (specific instruction)
- Key acceptance criteria from flow (success metrics)
- References (related artifacts)

No evidence of explore-requirements needing to ask the user for additional context that should have been in the goal.md. The handoff is clean.

**explore-requirements → user handoff: SMOOTH**

Each requirement was committed individually (separate git commits per gap documented in the task's goal.md). This allows the user to review each requirement independently and provides clear rollback points.

### 3.7 Requirements Matrix Usefulness

**Assessment: HIGH**

The matrix serves as both a planning artifact and a traceability document:
- **Planning**: The status summary table (5 exists_needs_update, 1 exists_placeholder, 3 new_needed, 1 decision_needed) gives an immediate overview of the work ahead
- **Traceability**: Each row links a flow section to a requirement path with a specific action — this is the bridge artifact that REQ-PROC-030 was designed to create
- **Decision log**: The Decisions section documents OQ resolutions with dates — this has archival value beyond the immediate pipeline run

**Improvement opportunity**: The matrix should include a "Pipeline Status" column or section that tracks which goal.md files were created and their completion status. Currently, this information lives in the task's goal.md (TASK-PROC-030-02), not in the matrix itself. Adding it would make the matrix a self-contained status dashboard.

---

## Improvement Backlog

| # | Priority | Skill | What to Change | Why |
|---|----------|-------|----------------|-----|
| 1 | **CRITICAL** | explore-requirements | Add a post-write consistency check: verify YAML frontmatter has `trackable_items.acceptance_criteria` if ACs exist in the body; verify `status` field is consistent with `coverage` in `user_needs`; verify no stale cross-references | REQ-FUNC-017 missing trackable_items; REQ-FUNC-002 status mismatch; REQ-FUNC-002 stale FLOW-002-01-01 reference. These are mechanical errors a checklist would catch. |
| 2 | **HIGH** | explore-requirements | Define the "WHAT & WHY, not HOW" boundary with concrete examples: (a) acceptable: domain model field definitions, AC lists, behavior rules, integration point APIs; (b) unacceptable: BLoC event classes, file structure recommendations, localization string values, UI layout ASCII art, Dart code snippets for widget configuration | REQ-FUNC-007-01 Sections 1-6 contain BLoC events, file structures, and localization strings. While inherited from pre-pipeline work, the explore-requirements agent should flag existing violations when extending a requirement. |
| 3 | **HIGH** | derive-requirements-from-flow | Add a `decision_needed_exploration` sub-category to the gap status definitions: "Human decision required, but the decision itself requires investigation (reading additional artifacts, analyzing trade-offs) before the user can make an informed call. Action: Create an exploration goal.md that frames the decision and its options." | OQ-8 was handled correctly but via improvisation, not by following a defined pattern. Future runs should have explicit guidance for this common case. |
| 4 | **HIGH** | derive-requirements-from-flow | Add instruction for gap absorption: "When multiple gaps address the same requirement, consolidate them. In the matrix, mark the absorbed gap with the primary gap number (e.g., 'Addressed as part of Gap #1'). In the goal.md for the primary gap, list all absorbed gaps." | Gaps #9 and #11 were absorbed into Gap #1; Gap #8 into Gap #3. The matrix handled this with notes, but the pattern should be explicit. |
| 5 | **MEDIUM** | explore-requirements | Add guidance for extending existing requirements: "When extending an `exists_needs_update` or `exists_placeholder` requirement: (a) Read the entire existing document first. (b) Add new sections rather than rewriting existing ones. (c) Update the YAML `status` field if new sections change the overall coverage state. (d) Update the `version_history` section with the change date and source reference. (e) Check for and clean up stale cross-references in the existing YAML." | REQ-FUNC-002's status was not updated; version history was not added for new sections. The skill assumes new requirements but 5 of 8 pipeline outputs were extensions. |
| 6 | **MEDIUM** | derive-requirements-from-flow | Add a "Pipeline Status" row or column to the requirements matrix template that tracks goal.md creation and completion status per gap | The matrix is the central planning artifact but currently loses its value after goal.md files are created — it doesn't track whether they've been completed. The task goal.md (TASK-PROC-030-02) carries this information, but it should also live in the matrix for self-contained traceability. |
| 7 | **MEDIUM** | derive-requirements-from-flow | Clean up the `requirements_matrix_draft.md` → `requirements_matrix.md` rename: add explicit instruction to remove the "Status: ready to rename" header note from the final version | Minor housekeeping — the lingering note is confusing for future readers. |
| 8 | **MEDIUM** | explore-requirements | Add instruction: "If no relevant market research findings are found during Phase 1.4 (market research check), document this explicitly: `market_research_refs: [] # No relevant findings identified`" | REQ-FUNC-017 has no market_research_refs and no documentation of whether the check was performed. Explicit "no findings" is better than ambiguous absence. |
| 9 | **LOW** | derive-requirements-from-flow | Add a summary table template to the matrix format: "Status | Count | Items" breakdown | The current matrix includes this as an ad-hoc addition. Making it part of the template ensures consistency across future pipeline runs. |
| 10 | **LOW** | explore-requirements | For Opus mode recommendation: add a heuristic in goal.md — "Recommended: Opus mode" for cross-cutting features, security-related features, or features with complex stakeholder trade-offs | REQ-FUNC-019 (security trade-off) and REQ-FUNC-017 (cross-cutting) would have benefited from Opus-level analysis. Currently the user must decide; a recommendation in the goal.md would help. |
| 11 | **LOW** | derive-requirements-from-flow | Add explicit FLOW-002#step_N anchor format requirement for matrix gap descriptions (instead of implicit "Steps 1-4" references) | Improves machine-parseability of the matrix for future automated traceability tools. |

---

## Conclusion

### Did the First Run Succeed?

**Yes, unequivocally.** The derive-requirements-from-flow → explore-requirements pipeline successfully processed a complex, 400+ line user flow with 12 Open Questions and produced 8 requirement documents that are:
- Traceable to their source flow and gaps
- Cross-referenced with user needs (personas, scenarios, flows)
- Properly scoped with clear boundaries
- Structured consistently (with minor YAML omissions)
- Actionable for downstream implementation tasks

The pipeline found 11 gaps from a flow that listed only 7 — validating the "comprehensive" quality criterion. All 12 Open Questions were surfaced and correctly handled (6 resolved, 6 deferred). No requirements were written directly by the derive skill — the non-invasive principle held. No duplicate requirements were created.

### Confidence Level for Future Runs

**HIGH (8/10) with the following caveats:**

1. **Simpler flows will work out of the box.** Flows with fewer OQs, fewer gaps, and less pre-existing requirement content will produce even more consistent output. The issues identified (status mismatches, YAML omissions) are mostly related to extending existing complex requirements — a scenario that smaller flows encounter less.

2. **The OQ-8 pattern needs codification.** Future flows with exploration-dependent decisions will hit the same ambiguity. Implementing Improvement Backlog item #3 (`decision_needed_exploration` sub-category) would raise confidence to 9/10.

3. **The WHAT/WHY boundary needs tightening.** As the requirement corpus grows, the risk of implementation detail leakage increases. Implementing Improvement Backlog item #2 (concrete boundary examples) is important for long-term quality.

4. **Post-write consistency checks are non-negotiable.** Implementing Improvement Backlog item #1 (YAML validation checklist) would prevent the mechanical errors identified in this run from recurring.

### What Went Right

- The two-skill split (derive → explore) maintained clean separation of concerns
- The Requirements Matrix is a genuinely useful planning and traceability artifact
- The goal.md template produced effective handoff documents
- The Opus model allocation to the matrix phase was well-targeted
- User decisions were documented and incorporated correctly
- Gap #6 (crisis safety) was correctly deferred without creating work items
- The pipeline handled both new features and existing requirement extensions

### What Needs Work

- YAML frontmatter consistency (trackable_items, status fields)
- The boundary between requirements and implementation specs
- Guidance for extending (not just creating) requirements
- Handling of decision-dependent exploration tasks
- Post-pipeline consistency verification

---

*Report generated by Opus pipeline evaluation agent, 2026-02-22.*
*Source artifacts: 14 files read in full across skills, process requirements, flow, matrix, goal.md, and 8 produced requirements.*
