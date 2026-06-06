---
name: requ-explore
description: End-to-end workflow for exploring and documenting requirements. THIS SKILL MUST BE USED TO ADD OR MODIFY REQUIREMENTS.
tools: "*"
model: inherit
---

You execute a requirements exploration and documentation workflow.

**Philosophy**: Requirements are the foundation - "garbage in, garbage out".
Requirements are blueprints for implementation. Tasks are derived from them.

**Timeless End-State Rule**: Every requirement statement must read as true (or false) independent of when it is read. A requirement describes the world as it IS when the system is compliant — never what changed, what currently needs to change, or how it got there. Temporal language ("currently", "will be", "after the migration") and transition verbs (*replace, migrate, add to, convert, refactor, change, update*) are forbidden in ACs, Behavior, and Developer Guidelines.

**User invokes**: "Use requ-explore skill for [task path]"

---

## Naming Conventions

FORMAT rules for all artifact folders under `requirements_tasks/`:

| Level | Folder pattern | Notes |
|-------|---------------|-------|
| Epic | `epic_<snake_case>` | Concise noun phrase naming the grouping |
| Feature | `feat_<snake_case>` | Concise noun phrase naming the deliverable. 6 legacy unprefixed features in the therapist epic are grandfathered — do NOT rename them (path churn breaks target_package + cross-refs). |
| Task | `<YYYY-MM-DD>_<mode>_<kebab-case-name>` | mode ∈ {impl, explore, define, review, analyze, bugfix, verify}; name is a concise, verb-first-where-natural kebab-case slug |

**Deliberate casing split**: requirement folders use snake_case; task name slugs use kebab-case. Do NOT unify — renaming requirement folders would churn target_package fields and path cross-references.

---

## Phase 1: Investigation

All investigation happens in the current session. No files are written during this phase - everything stays in context.

### 1.2 Read Goal
**Skip if invoked without an existing task folder** (invoked with a description, not a path) — objective comes from the user's invocation argument; workspace will be created in §2.1b after location is approved.

Read `goal.md` to understand the specific objective.

**Developer Intent check**: If goal.md contains a `## Developer Intent` section, read each tagged item:
- `[PREFERENCE]` — user expressed a technology/component wish; carry into Developer Guidelines as a default constraint (implementer may deviate with documented justification in the task plan)
- `[CONSTRAINT]` — user expressed a hard rule ("must not", "never"); carry into Developer Guidelines as a non-negotiable invariant

Keep these items in working memory for Phase 2.3. They do not change WHAT the requirement specifies — they inform HOW Developer Guidelines constrain the implementation.

**Background Check**: Note whether goal.md contains a clear background or motivation (why this requirement exists, what triggered it). If absent, flag for Phase 1.7.

### 1.3 Read Documentation
Read relevant guidelines from `doc/` subdirectories:
- `doc/architecture/` - Overall architecture principles
- `doc/presentation/` - If UI/UX related
- `doc/domain/` - If domain logic related
- `doc/testing/` - Testing requirements
- `doc/general/` - General guidelines

Read relevant guidelines from `requirements_user_needs` folder:
- `requirements_user_needs/*.md` - User needs guidelines

**Think**: Which guidelines directly apply to this requirement? What patterns or standards must be followed?

### 1.4 Read Requirement Hierarchy
Navigate the requirement folder structure:
1. **Parent requirements** - Walk up the folder tree, read requirements.md files
2. **Sibling requirements** - Read requirements at same level for context
3. **Cross-reference gap detection** — Run `python3 scripts/requirements/check_cross_refs.py <path-to-requirements.md>` (pass the target requirement's `requirements.md` path). The script greps `requirements_tasks/functional/`, `non-functional/`, and `process/` using 2–4 derived search terms, excludes already-referenced IDs, and outputs a JSON list of candidates. Read each candidate to identify semantic overlaps. Use `--terms term1 term2` to override the derived terms if the default terms are too generic. This detection is the primary overlap-detection mechanism; the folder-walk provides supplementary structural context.

**Think**: How does this requirement fit into the bigger picture? What dependencies exist? What gaps are there? Does an Epic already exist for this area? What semantic overlaps did the keyword-grep reveal?

**Market research**: Before finalizing requirements for functional features, check `requirements_market_research/*/findings.md` for relevant findings > add `market_research_refs` YAML if found (see README.md in that folder for format). If no relevant findings exist, add `market_research_refs: [] # No relevant findings identified` to YAML.

### 1.5 Analyze Implementation
Search for existing implementations in `lib/` and `test/`:

**CodeGraph First** (skip if `.codegraph/` is missing):
```bash
codegraph context "<requirement topic>" --max-nodes 20
```
Use results to narrow which files to Read.

**Use Glob and Grep**:
- Find relevant files by pattern
- Search for key terms
- Read identified files

**Minimum search scope**: Execute at least 2–3 grep passes on `lib/` for key domain terms before concluding that no existing implementation exists for the requirement topic.

**Orphaned-implementation check**: After identifying relevant code in `lib/`, verify that an existing requirement covers the observed behavior. Search `requirements_tasks/functional/` and `requirements_tasks/non-functional/` for the concept. If code implementing the feature is found but no requirement covers it, record this gap explicitly in the protocol before proceeding — do not silently continue.

**Think**: What patterns exist in the codebase? What are concrete examples with file:line references? What variations and edge cases are handled? What anti-patterns should be avoided? Is there orphaned implementation that lacks requirement coverage?

### 1.6 Map User Needs (for epics/features)

When exploring requirements for epics/features:

**MANDATORY: Read user needs guidelines first** (in parallel):
| README | Content |
|--------|---------|
| `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` | Bidirectional links |
| `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md` | Reference notation, YAML user_needs |

**Use Grep** to search `requirements_user_needs/` for mentions of epic/feature:
- Search personas: `requirements_user_needs/personas/*/persona.md`
- Search scenarios: `requirements_user_needs/personas/*/scenarios/*/scenario.md`
- Search flows: `requirements_user_needs/user_flows/*/flow.md` (NEW LOCATION - flows are shared, not nested)

**Think**: Which personas does this serve? Which scenarios does it address? Which user flow steps does it implement? What gaps exist between user needs and this requirement?

**System Maintenance Check**: Read `requirements_user_needs/personas/system_maintenance/persona.md` (PERSONA-004). Check if this requirement touches any of its constraint areas:
- Data integrity / data loss prevention
- Device compatibility (old hardware: 2017 Android, 2015 Windows)
- Energy / battery sensitivity
- Background operations / automatic maintenance
- GDPR / data deletion

If YES → add `PERSONA-004` to `personas_served` in YAML and reference the specific constraint in the requirement's Purpose or Developer Guidelines section.

**VCD Analysis** (for requirements serving multiple personas):
- For each persona in `personas_served`, read their `vcd:` YAML block
- Identify value conflicts between serving personas
- If conflicts exist → add `## Value Trade-offs` section to the requirement body
- Document each conflict using the template in `requirements_user_needs/_meta/value_tradeoff_record_template.md`

**Output**: Add `user_needs` section to epic/feature requirements.md per README_13 format.

### 1.7 Background Elicitation

**Only if background/motivation was flagged absent in 1.2.**

Using context gathered in Phase 1 (user needs, flows, hierarchy, market research), draft a concise motivation statement covering:
- The user problem or need this addresses
- What triggered this requirement (research, user feedback, technical constraint)
- Why it matters now

Present the draft to the user:
> "I didn't find an explicit background for this requirement. Based on the context gathered, I'd suggest:
> *[draft]*
> Is this accurate? Please correct or expand."

Incorporate the confirmed motivation into the `## Purpose` section in Phase 2.3.

---

## Phase 2: Synthesis & Writing

> **Timeless End-State Rule** — enforce before writing a single line: Phase 1 analyzed the current state and what differs from the goal. Now shift perspective entirely. You are NOT describing what needs to change. You are describing **what the world looks like when the requirement is fully met — permanently, at any point in time**. A reader who has never seen the current codebase, reading this a year after delivery, must be able to verify compliance by inspecting the final product alone. Every sentence must describe the destination, not the journey. Temporal language and transition verbs are forbidden (see Philosophy).

### 2.0 Pre-allocated ID Check

Before determining scope, check whether a requirement ID was pre-allocated by `task-create`:

1. Read goal.md `parent_requirement` field (e.g. `REQ-FUNC-007`).
2. Derive the expected requirements.md path from that ID and the task folder location.
3. **If requirements.md does NOT exist at that path**:
   - `[parent-path]` = the **parent requirement's folder** (e.g. `requirements_tasks/functional/shared/epic_data_transfer`), NOT the feature folder being created.
   - Check that directory for a `.reserve-[parent_requirement]-NN` marker file.
   - **If marker exists**: the REQ-ID was pre-allocated by `task-create`. Extract the ID from the filename (e.g. `.reserve-REQ-FUNC-007-05` → `REQ-FUNC-007-05`). Use it as-is when writing requirements.md — do NOT call `allocate_req_id.py`. After writing requirements.md, delete the marker:
     ```bash
     rm [parent-path]/.reserve-[REQ-ID]
     ```
   - **If no marker**: call the allocation script to atomically reserve the next ID — **do NOT derive the ID manually**:
     ```bash
     REQ_ID=$(python3 scripts/requirements/allocate_req_id.py \
       --parent-id [parent_requirement] \
       --parent-path [parent-path])
     ```
     The script prints the allocated ID (e.g. `REQ-FUNC-007-05`) to stdout and creates a `.reserve-[REQ-ID]` marker file inside a file lock, preventing race conditions with concurrent sessions. Use `$REQ_ID` in requirements.md, then delete the marker:
     ```bash
     rm [parent-path]/.reserve-$REQ_ID
     ```

     **Creating a feature inside an existing epic**:
     - `--parent-id` = the epic's REQ-ID (e.g. `REQ-NFUNC-018`), NOT the category prefix
     - `--parent-path` = the epic's folder (one level above the new feature folder)
     - Result: child gets a derived ID, e.g. `REQ-NFUNC-018-01`
     - No `parent_epic:` field needed in the child's YAML — folder hierarchy implies membership

     **Creating a new epic** (no existing parent epic, incl. when features already exist at flat IDs):
     - `--parent-id` = the category prefix, e.g. `REQ-FUNC`, `REQ-NFUNC`, `REQ-PROC`
     - `--parent-path` = the specific subdirectory where the new epic folder will be created, e.g. `requirements_tasks/functional/client`
     - The registry (`requirements_tasks/_meta/id_registry.md`) deduplicates IDs across subdirectories, so passing any one sibling directory is sufficient.
     - Example: `python3 scripts/requirements/allocate_req_id.py --parent-id REQ-FUNC --parent-path requirements_tasks/functional/client`
     - Note: existing features at flat IDs keep their IDs — no renumbering needed
4. **If requirements.md already exists**: skip this check entirely, proceed normally.

### 2.1 Determine Scope and Structure

Based on investigation, determine what needs to be created:

#### Epic vs Feature Decision (for functional requirements)

| Criterion | Epic | Feature |
|-----------|------|---------|
| **Size** | Large, spans multiple distinct pieces | Specific, focused functionality |
| **Implementable** | NO - too high-level | YES - can derive tasks directly |
| **Naming** | `epic_<name>` prefix required, snake_case | `feat_<name>` prefix required, snake_case |
| **Tasks allowed** | Only `explore`, `define`, `review`, `analyze` | All task types including `impl` |

**Decision Tree**:
1. Is this requirement directly implementable as a single coherent piece?
   - **YES** → Create a **Feature**
   - **NO** → Continue to question 2
2. Does this span multiple distinct functionalities that could be implemented separately?
   - **YES** → Create an **Epic** with **Features** inside
   - **NO** → Break down further until you can answer YES to question 1

#### What to Create

**Scenario A: Requirement is a Feature (directly implementable)**
- Create `requirements.md` in the feature folder
- Ready for implementation tasks

**Scenario B: Requirement is too large, no Epic exists**
1. Create Epic folder with `epic_` prefix
2. Create Epic-level `requirements.md` (high-level, NOT implementable)
3. Create Feature folders inside the Epic (use `feat_<name>` prefix)
4. Create Feature-level `requirements.md` for each (implementable)

**Scenario C: Epic exists, need to add Feature**
- Create Feature folder inside existing Epic (use `feat_<name>` prefix)
- Create Feature-level `requirements.md`

**Scenario D: Multiple requirement files needed**
- For non-functional/process requirements without Epic structure
- Create multiple `requirements.md` files in appropriate folders

**Scenario E: Extending an existing requirement** (`exists_needs_update` / `exists_placeholder`)
1. Read entire existing document first
2. **Upstream impact check** (before writing anything): Does the change affect any `implements_flows` references in the YAML?
   - YES → Show the user which flows are affected and ask: "This change may affect [FLOW-XXX]. Should I run `ux-create-flow` on the flow(s) before or after updating the requirement? Or use `product-intake` to cascade the full change top-down?"
   - NO / no `implements_flows` present → continue
3. Add new sections or targeted corrections; do NOT rewrite or restructure existing content beyond what the change requires. If existing content must change (e.g., because the update contradicts it), show the diff to the user before applying.
4. Update YAML `status` if new sections change overall coverage:
   - If requirement has `status: active` → leave as `active` (do not revert to `in_progress`)
   - If requirement has `status: implemented` → changing content means coverage may be incomplete → revert to `in_progress`
5. Check for stale `implements_flows` references; clean up or flag them

#### Epic Size Gate (mandatory after drafting any epic)

After drafting an epic-level `requirements.md`, apply this gate before Phase 2.2:

**MEASURE**: Count non-YAML body lines (all lines after the closing `---` of frontmatter).

**LIMIT**: Epic body must not exceed **90 lines**.

**Content-type rule** (applies regardless of line count):

| Belongs in Epic | Belongs in Feature |
|---|---|
| Cross-cutting invariants affecting ALL features equally | One feature's specific behavior or constraints |
| WHY this grouping exists as a unit | Technical specs, file formats, platform details |
| Relationship *between* features (how they compose) | Testing requirements |
| Scope exclusions for the entire epic | Step-by-step user scenarios |
| Glossary terms shared across multiple features | Implementation details, examples |

**Allowed sections** (any other header requires explicit justification):
- `## Overview` — what this group does (max 5 lines)
- `## Purpose` — why this epic exists (max 3 lines)
- `## Scope` — included and explicitly excluded (max 6 lines)
- `## Features` — index only; max 2 lines per feature + link
- `## User Needs` — personas, flows, scenarios (max 5 lines)
- `## Dependencies` — other epics/requirements (max 6 lines)
- `## Cross-Feature Invariants` — constraints applying to ALL features (max 8 lines)
- `## Value Trade-offs` — VTR records (`<!-- vcd-record -->` blocks) where persona values conflict; mandatory when Phase 1 VCD analysis finds conflicts (see VCD Analysis above); no line limit — use as many VTR blocks as needed
- `## Glossary` — shared terms (only if genuinely needed)
- `## References` — links only, no prose

**When limit exceeded or wrong-level content found:**

1. Identify each block that belongs in a feature (content-type rule above).
2. For each block:
   - `feat_[name]/` folder exists → merge content into that feature's `requirements.md`
   - No folder exists → create `feat_[name]/requirements.md` with full content + `status: placeholder`; **immediately** create a follow-up explore task via `task-create` skill (type: explore, urgency: 3, body: "Complete requ-explore quality gate for auto-created feature [feat_name]: user needs mapping, trackable_items, market_research_refs, package assignment.")
3. Remove block from epic; replace with 2-line entry in `## Features` + link.

> Auto-created features skip the full quality gate (no user needs mapping, no trackable_items, no market_research_refs). The follow-up explore task is **mandatory**.

#### Initial Status for New Requirements

When writing a new requirement, choose the initial status based on type:

| Requirement Type | Initial Status | Examples |
|-----------------|----------------|---------|
| Feature / concrete deliverable | `defined` | Any functional feature, UI component, API endpoint |
| Living document / continuous rule | `active` | Coding standards, testing rules, AI workflow rules, process guidelines |

A requirement is a **living document** when ALL of these apply:
- It describes a process, standard, or guideline (not a concrete deliverable)
- It is expected to spawn improvement tasks over time
- "All tasks done" would never truly end the evolution of this requirement

Set `status: active` directly — do NOT use `status: defined` and then wait for tasks.

### 2.1a Location Approval Gate

**Skip when** (proceed directly to 2.2):
- User's original prompt named the target folder or file path explicitly, OR
- User's original prompt asked to modify/update/extend a specific requirement by REQ-ID or file path.

**Otherwise** — before writing any file, present the planned location to the user:

**New requirement:**
> I plan to create [Epic | Feature | Epic + Features]:
> - `requirements_tasks/[category]/[path]/requirements.md`
> *(Scenario B — sub-features)*: `...epic/feat_X/requirements.md`, `...epic/feat_Y/requirements.md`
>
> After you approve the location, I will check neighboring requirements for restructuring opportunities (sibling bundling, feature oversize, obsolescence) and present any findings for a separate approval before writing anything.
>
> Approve this location, or redirect me?

**Extension to existing requirement:**
> I plan to extend `requirements_tasks/[...]/requirements.md` (id: REQ-XX-YY).
> Changes: [1–2 sentence summary of what will be added/changed].
>
> After you approve, I will check neighboring requirements for restructuring opportunities and present any findings for a separate approval before writing anything.
>
> Approve, or redirect me?

If the user rejects or redirects: adjust the plan and re-present. Never write files until approved.
Note: The restructuring text is currently not acted on. There will be a phase added for that in the future, just ignore it until that phase lands. 

### 2.1b Initialize Workspace

Call `task-create` skill with the approved requirement path from §2.1a. The user already confirmed the location — auto-confirm `task-create`'s Step 4 location-confirmation prompt on the user's behalf. After workspace creation, continue with §2.2.

---

### 2.2 Write Requirements

Think through these questions before writing:
- What is the core purpose of this requirement?
- Who are the stakeholders (users, developers)?
- What rules/guidelines should be followed?
- What exceptions exist?
- What examples illustrate proper usage?
- What anti-patterns should be avoided?
- Is this an Epic or Feature?

**YAGNI evidence gate** (before committing ACs or scope items):

For each planned acceptance criterion or scope item, apply:
- **Gate 1 — inclusion**: cite ≥ 1 piece of real evidence: (a) user-described need, (b) named direct dependency, (c) existing code path that breaks without it, (d) regulation in effect today, or (e) documented incident / fired alert / measured metric. Hypotheticals ("for future flexibility", "best practice says", "when we scale") do not qualify.
- **Gate 2 — shape**: when evidence justifies inclusion, prefer the strictly simpler version that satisfies the same evidence.

Items failing Gate 1 go to a `## Deferred (YAGNI)` section (omit section entirely when no items are deferred). Format per item:
- `### {item name}` / `**Why deferred:** [missing evidence]` / `**Reopen when:** [named trigger — specific future event providing evidence]` / `**Source:** [where the hypothetical originated]`

User override: any single deferral can be overridden; note the rationale inline in the requirement body.

Then write requirement file(s) following structure in section 2.3.

**Canon check**: When writing introduces a user-facing noun/verb/state not in `concept_canon.yaml`, invoke `ux-write-canon-concept`.

### 2.3 Requirement Document Structure

Requirements are **blueprints for implementation**. They define WHAT and WHY. Implementation details belong in task files and code, not in requirements.

**NOT acceptable in requirements**:
- BLoC event class definitions, file structure trees, localization string values, Dart widget configuration snippets
- Testing requirement sections (unit/widget/integration test lists) — testing strategy belongs in `doc/testing/`; test specifics in task plans. A feature requirement may state *testability constraints* in Developer Guidelines (e.g. "must be testable without network") but must not enumerate test cases. **Testing sections rule**: when encountered, apply this routing:
  - *Unit/widget tests* → discard; these emerge naturally from implementation and are the impl engineer's responsibility
  - *Integration tests* → create **1 test task** (type: `impl`, use `code-test` skill) in the relevant feature's `tasks/` folder with `awaiting: [impl-task-TBD]`; the placeholder is updated once the impl task is created. Use `python3 scripts/tasks/allocate_task_id.py` to assign the ID.
- `## Open Questions`, `## Version History`, `## Implementation Roadmap` sections — version history is tracked by git; roadmaps belong in task plans. Open questions must be actively resolved, not left in the file — see rule below.
- **Open questions rule**: When encountering open questions during requirement work, do NOT leave them in a `## Open Questions` section. Instead, use the `task-create` skill to create exploration tasks. **Max 1 task per category** — bundle all questions of the same type into one task, not one task per question. Two levels:
  - *UX/product questions* (affect user experience, screen design, or flow structure) → **1 exploration task at flow level** bundling all UX questions:
    - Task folder: `requirements_tasks/process/AI_rules/requirements_management/user_needs_content/user_flows/tasks/YYYY-MM-DD_explore_[name]/goal.md`
  - *Technical questions* (implementation-only, no visible UX impact) → **1 exploration task at requirement level** bundling all technical questions:
    - Task folder: inside the relevant epic/feature `tasks/` folder
    - Parent requirement: the relevant REQ-ID
  - If it is unclear which applies, default to flow level — UX implications are easily missed and costly to retrofit.
- Step-by-step user interaction sequences ("1. User opens dialog, 2. System shows X…") — these duplicate user_flows/. If a flow exists, reference it by FLOW-ID. Behavior descriptions answer "what does the system do when X?" not "first A, then B, then C."

**ASCII diagrams**: permitted only to illustrate a behavioral state machine or data flow essential to understanding the WHAT. Maximum 10 lines. Architectural overview diagrams belong in `doc/architecture/`; implementation-sequence diagrams belong in task plans.

**Requirements vs Tasks**: Requirements describe the desired end state. Tasks describe the steps to reach it. Each AC must pass this test: *"Would this AC be true even if a completely different development path had been taken to reach the same result?"* If it reads like a to-do step, it belongs in the task plan, not the requirement.

**Transition-language warning**: If an AC contains words like *replace, update, migrate, add to, convert, remove from, change, refactor* — it almost certainly describes a transition step, not an end state. Rewrite it as the resulting state.

- BAD AC: "Replace all `print()` calls with logger calls" — transition step
- GOOD AC: "No raw `print()` or `debugPrint()` calls exist in `lib/`" — verifiable end state
- BAD AC: "Add validation to all form fields" — transition step
- GOOD AC: "All user-facing form fields validate input before submission and display an error message on invalid input" — verifiable end state
- BAD AC: "Migrate authentication to use JWT tokens" — transition step
- GOOD AC: "All authenticated API requests use JWT bearer tokens with a 24-hour expiry" — verifiable end state
- BAD AC: "Update the routing module to support deep links" — transition step
- GOOD AC: "The app handles deep links to all primary screens and restores the correct navigation state" — verifiable end state

#### Epic-Level Requirements

Epics are high-level and NOT directly implementable:

```markdown
# Epic: [Name]

## Overview
[High-level description of this group of features]

## Purpose
[WHY does this epic exist? What user problem does it solve?]

## Scope
[What is included and what is explicitly excluded]

## Features
[List of features that belong to this epic - may be incomplete initially]
- Feature 1: [Brief description]
- Feature 2: [Brief description]

## User Needs
[Which personas, scenarios, flows does this epic address?]

## Dependencies
[What must exist before this epic can be fully implemented?]

## References
- doc/[relevant].md
- Related epics/features
```

#### Feature-Level Requirements

Features are specific and implementable:

```markdown
# [Feature Name]

## Overview
[Brief description - what is this feature?]

## Purpose
[WHY does this exist? Cover:
- The user problem or need it solves
- What triggered this requirement (research insight, user feedback, technical constraint, business need)
- Why it matters to the product now]

## When to Use
<!-- Include only when this feature represents a choice or alternative.
     Omit for always-on, foundational, or infrastructure features (data models,
     serialization pipelines, encryption). Use ## Scope instead if boundary
     clarification is needed. -->
[Clear rules for when this feature/pattern applies]
- Rule 1

## When NOT to Use
<!-- See When to Use — omit together when not applicable. -->
[Clear rules for when to use alternatives]
- Alternative situation 1 → Use [X] instead

## Behavior
<!-- Describe observable states and system responses — not step-by-step
     interaction sequences. If a user flow exists, reference it by FLOW-ID.
     Answer "what does the system do when X?" not "first A, then B, then C." -->
[What should happen? User-facing behavior, not implementation details]

## Examples
[Concrete examples with code references to existing implementations]

**Example 1: [Name]**
- Location: `lib/path/file.dart:123`
- Description: [What it demonstrates]

## Developer Guidelines

> **Rule**: This section describes **constraints and invariants** that the final implementation must satisfy. It must NOT contain migration steps, to-do instructions, or descriptions of what currently needs to change. Every statement must describe a property of the finished system. (Lives here because no task exists yet; task plans hold the concrete HOW.)

> **Developer Intent translation** (if goal.md had a `## Developer Intent` section):
> Translate each item into an end-state constraint here. Rules:
> - `[PREFERENCE]` → state as the default: "The overlay is rendered as a modal bottom sheet *(developer intent: FLOW-NNN notes.md)*" — an implementer may deviate with documented justification in the task plan
> - `[CONSTRAINT]` → state as a hard rule: "The notification system must NOT use Firebase Cloud Messaging *(developer intent: FLOW-NNN notes.md)*"
> - Drop items that do not apply to this specific requirement
> - Always include the `*(developer intent: …)*` source reference

### Key Decisions
[Architectural/design constraints that any valid implementation must respect — stated as rules, not steps]

### Common Pitfalls
- Pitfall 1: [What the wrong end state looks like and how to recognize it]

## Related Requirements
<!-- All semantically related requirements found via the section 1.4 keyword-grep must be listed here.
     An empty Related Requirements section is only acceptable if the keyword-grep returned no relevant hits. -->
- [Link to related requirements]

## References
- doc/[relevant].md
- Existing implementation: lib/path/file.dart
```

#### YAML Frontmatter

Include for all requirements:
```yaml
---
id: REQ-[CATEGORY]-[NUMBER]
status: defined
release_chunk: "chunk label"   # optional — only when derived from a flow with release_scope; copied from goal.md suggested_release_chunk
# For features in functional/:
user_needs:
  implements_flows:
    - id: FLOW-001-01-01
      steps: [1, 2, 3]
      coverage: partial
  addresses_scenarios: [SCEN-001-01]
  personas_served: [PERSONA-001]
---
```

**For epic requirements** (`epic_` prefix): `trackable_items.acceptance_criteria` lists one AC per feature in `## Features`. AC text: "`feat_[name]/requirements.md` has `status: defined` or `status: active`." A task that promotes a placeholder feature sets `covers.acceptance_criteria: [AC-XX]`. Do NOT list structural sections (Overview, Purpose, Scope, Dependencies) — they are never trackable on an epic.

### 2.4 Release Chunk + Package Assignment

**When**: After requirement document is drafted (Phase 2.3), before quality check.

**Step 1 — Propagate release_chunk** (only when requirement was created from a `requ-derive-from-flow` goal.md):
- Read goal.md YAML for `suggested_release_chunk`
- If present → write `release_chunk: "[value]"` into requirement YAML frontmatter
- If absent (requirement was not derived from a flow, or flow has no `release_scope`) → omit the field entirely; do not prompt the user

**Step 2 — Package Assignment**

**Purpose**: Assign each trackable item (acceptance criterion or section) to a target package, then compute top-level `target_package` as the package of the earliest-versioned item.

**Process**:

1. **Read assignment rules**: Read `requirements_tasks/package_assignment_rules.md` — it contains the canonical when-to-ask vs. auto-assign decision table, the Shared UI Surface Constraint, and the "earliest" determination rules. Apply these rules throughout this phase.

2. **Read RELEASE_BACKLOG.md**: Parse `packages` from `requirements_tasks/RELEASE_BACKLOG.md` YAML frontmatter. Build a flat list of all package entries: `(id, name, version)`.

3. **For each trackable item** (AC or section) in the new requirement:
   - If requirement is **existing** AND item already has `target_package`: preserve; do not prompt again
   - If requirement is **new** OR item has no existing `target_package`:
     - **If the item involves a UI element** (selector, display field, input, mode-switch): **always ask** — the Shared UI Surface Constraint requires human judgment (see `package_assignment_rules.md`)
     - **Auto-assign without prompting** when ALL three hold: (a) no UI elements involved, (b) all new items depend on exactly one existing package's infrastructure, (c) the package description explicitly covers this content — log the assignment and reason inline
     - **Otherwise ask**: present the flat package list grouped by version and ask "Which package should this item target? (or 'unassigned/skip')"
     - Add `target_package: "PKG-x.y.z-name"` to that item in YAML

3. **Compute top-level `target_package`**: Set requirement's top-level `target_package` to the package whose version is earliest (using semver ordering of the associated version) among all assigned items. If a tie exists (multiple items in the same version), use the one that appears first in RELEASE_BACKLOG.md. If no items assigned, omit top-level field.

   Note: The first-listed package per version in RELEASE_BACKLOG.md serves as the fallback `target_package` for cross-cutting requirements that do not fit any scoped package — assign these to the first-listed package of the relevant version.

4. **Do NOT back-propagate to the originating task**: If the goal.md that triggered this exploration has `source_gap:` in its frontmatter, never write or update `target_package` on that goal.md file — even if packages were just assigned to the requirement's ACs. Flow-derived explore tasks must stay unpackaged (see `task-create` Package Inheritance guard).

5. **Sync covering tasks**: After assigning packages to all items in this requirement, run:
   ```bash
   python3 scripts/requirements/sync_task_packages.py --requirement [path-to-requirement-folder] --apply
   ```
   Log the script output to the user. Tasks with empty `covers` are automatically skipped.

**YAML structure** (IDs are illustrative — actual values come from RELEASE_BACKLOG.md, e.g. `"Data Transfer Core"` not `"PKG-0.0.1-core"`):
```yaml
target_package: "Data Transfer Core"   # top-level: package with earliest version (computed)
trackable_items:
  acceptance_criteria:
    - id: AC-01
      target_package: "Data Transfer Core"  # assigned
    - id: AC-02
      target_package: "Plan Transfer Full"
    - id: AC-03
                                           # absent = not yet assigned
  sections:
    - id: SEC-01
      target_package: "Plan Transfer Full"
```

**Skip Conditions**:
- Requirement is purely internal process tooling AND user indicates "unassigned" → skip without error
- `requirements_tasks/RELEASE_BACKLOG.md` not found → warn user and skip package assignment
- No existing package fits → note the requirement ID. After all items are processed, if any were noted: create one task via task-create skill (type: impl, urgency: 5, body: "Run `release-plan → Action 4`. No package found for: [req IDs].").

**Behavior Reference**: See `requirements_tasks/package_assignment_rules.md` for the canonical decision table and Shared UI Surface Constraint. The key rule: if an item touches UI, always ask.

### 2.5 Quality Check

Before proceeding, verify:
- [ ] All investigation areas from goal.md addressed
- [ ] Focus on WHAT & WHY, not detailed HOW
- [ ] `## Purpose` includes background, motivation, and origin of the requirement (not just a one-liner)
- [ ] **End-state test**: Each AC passes — *"Would this be true even if a completely different implementation path had been taken?"*
- [ ] **Transition-language test**: No AC contains *replace, update, migrate, add to, convert, remove from, change, refactor* — if found, rewrite as the resulting state
- [ ] **Abstraction-level test** (REQ-PROC-062 AC-08/09/10): Epic ACs — no screen, field, YAML key, class, method, artifact section, or skill phase named (capability vocabulary only). Feature ACs for app codebase — no class, method, widget, or BLoC state class named (screen names and domain entity names are permitted). Feature ACs for factory — no internal skill step logic or agent reasoning described (artifact field names, section headings, folder patterns, and script output are permitted).
- [ ] **Developer Guidelines test**: No sentence in Developer Guidelines describes a step or migration — only constraints/invariants of the finished system
- [ ] **No forbidden sections**: No `## Testing Requirements`, `## Open Questions`, `## Version History`, `## Implementation Roadmap` — if found, remove or relocate
- [ ] **Developer Intent**: All `[PREFERENCE]` and `[CONSTRAINT]` items from goal.md `## Developer Intent` either appear in Developer Guidelines (translated to end-state language with source reference) or are explicitly dropped with a note explaining why they don't apply to this requirement
- [ ] **No step-by-step scenarios**: Behavior section describes states/responses, not numbered interaction sequences — if a flow exists, FLOW-ID is referenced instead
- [ ] **ASCII diagrams**: max 10 lines, behavioral/state-machine only — architectural or sequence diagrams moved to `doc/` or task plans
- [ ] **WHEN/WHEN-NOT**: present only if feature represents a choice; omitted for always-on/foundational features
- [ ] Clear WHEN/WHEN-NOT rules (for patterns/features)
- [ ] Concrete examples with code references
- [ ] Actionable developer guidelines
- [ ] Cross-references to doc/ and related requirements
- [ ] Epic vs Feature distinction is correct
- [ ] Epic requirements are NOT directly implementable
- [ ] Feature requirements ARE directly implementable
- [ ] YAML: `trackable_items.acceptance_criteria` present if ACs exist in body; for epics specifically, one AC per feature (condition: feature's `requirements.md` has `status: defined` or `status: active`)
- [ ] YAML: `trackable_items.sections` contains only sections a future task will realistically own — sections completed in this requ-explore run must NOT appear; for epics, structural sections (Overview, Purpose, Scope, Dependencies) are almost never trackable; omit `trackable_items.sections` entirely when nothing qualifies
- [ ] YAML: `status` is consistent with actual coverage state — `active` for continuous/living requirements; `defined` for concrete deliverables; never `implemented` from this skill
- [ ] YAML: no stale `implements_flows` references
- [ ] YAML: `market_research_refs` present (even if `[] # No relevant findings identified`)
- [ ] System Maintenance: PERSONA-004 checked; added to `personas_served` if constraint areas are touched
- [ ] `release_chunk` written if goal.md had `suggested_release_chunk`; omitted otherwise
- [ ] Package assignment complete: all trackable items have `target_package` or explicitly unassigned

---

## Phase 3: Review & Iteration

### 3.1 Present to User
Present key findings and ask for specific feedback:
- "Does the WHEN/WHEN-NOT logic match your expectations?"
- "Are there use cases I missed?"
- "Is the Epic/Feature structure appropriate?"
- "Should any features be split or merged?"

### 3.2 Iterate Based on Feedback
If user provides feedback, update the requirement file(s).

---

## Phase 4: Completion

### 4.1 Verify and Tick Acceptance Criteria

Read goal.md's `## Acceptance Criteria` section. For each `- [ ]` entry, verify the AC is actually met by the work done in Phases 1-3. Convert verified entries to `- [x]` via Edit. Do NOT tick an AC that is not genuinely met — surface it to the user and address before completing. `complete_task.py` (invoked by task-complete) refuses to close a task with unchecked ACs, so any remaining `- [ ]` will block completion.

### 4.2 Complete Task
Use `task-complete` skill (marks task completed and commits).

---

## Key Principles

1. **Timeless End-State** — Requirements define WHAT & WHY as a permanent, timeless truth — not steps, not HOW, not current-state descriptions. Every statement must be verifiable by inspecting the finished system at any point after delivery. (See **Timeless End-State Rule** in Philosophy.)
2. **Epic vs Feature** - Epics group related features; only Features are implementable
   - Epic tasks: `explore`, `define`, `review`, `analyze` only
   - Feature tasks: All types including `impl`
3. **Code as Documentation** - Implementation details belong in task files and code, NOT in requirements
   - **Why**: Separate specs create maintenance burden when designs evolve
   - **Tasks** document the change history
   - **Code** documents the current state (authoritative source)
4. **Read, Think, Write** - Investigation in context, only final document(s) written
5. **Thoroughness** - Cross-reference doc/, requirements, implementation
6. **WHEN/WHEN-NOT rules** - Clear decision criteria
7. **Concrete examples** - Abstract rules + file:line references
8. **Single Session** - All investigation in current session, no intermediate files
9. **Quality over Speed** - Opus mode adds deeper thinking for better requirements
