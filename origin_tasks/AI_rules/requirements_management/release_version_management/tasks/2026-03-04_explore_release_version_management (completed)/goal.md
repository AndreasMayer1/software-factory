---
task_id: TASK-PROC-034-01
type: explore
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-04
effort: L
created: 2026-03-04
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06]
scope_description: "Explore and design the complete Release Version Management system: definition format, assignment rules, YAML extensions, skill updates, and script extensions."
requirements_version:
  commit: 6208ad5
  file: ../requirements.md
---

# Goal: Release Version Management — Exploration & Design

## Objective

Design a complete system for assigning requirements and tasks to release versions. This exploration produces concrete decisions and a design that can be implemented in subsequent tasks.

## Background & Motivation

As the project grows, we need a way to plan and track *when* specific requirements and tasks will be shipped. The system must:
- Be readable and maintainable by both human and AI
- Integrate into the existing requirements/task structure (YAML frontmatter)
- Be enforced and assisted by AI skills
- Be visible in the status overview script

## Exploration Areas

### 1. Release Definition Document

**Questions to answer:**
- Where does this document live? (e.g., `requirements_tasks/releases/releases.md` or project root?)
- What is the format? (YAML, Markdown, hybrid?)
- What information does each release entry contain? (version, name, description, goals, scope, planned date?)
- How does the AI reference this document? (hardcoded path, convention?)
- How does the document evolve as new releases are planned?

**Known release plan (starting point):**
- `0.0.1` Alpha — Proof of concept for QR code data transfer
- `0.1.0` Beta — MVP: therapist hands over plan, client fills it in and can transfer data back; rudimentary data visualization; no client profile storage on therapist side
- `0.2.0` Beta — TBD
- `1.0.0` — TBD

### 2. YAML Metadata Extensions

**Questions to answer:**
- What field name for release version? (e.g., `target_release`, `release_version`, `milestone`?)
- Where exactly in the frontmatter? (top-level field, or inside `trackable_items`?)
- For trackable items: how is the release version stored per-item?
- For tasks: is it always inherited from the parent trackable item, or can it be overridden?
- How does the AI record "not yet assigned" vs "explicitly unassigned" vs "assigned to X"?

**Affected file types:**
- `requirements.md` (top-level field + per trackable_item field)
- `goal.md` (top-level field)

### 3. Assignment Rules — Full Decision Logic

**Design the decision tree for AI assignment:**

Epic level:
- Epic release = earliest release among its trackable items
- Each trackable item gets individual release version

Feature level:
- Feature implements subset of epic trackable items → inherits their release versions
- Feature release = earliest release among its own trackable items
- Feature trackable items get individual release versions

Task level:
- Task → has parent trackable item? → inherit its release version
- Task → no parent trackable item? → AI reasons from context, or asks user

Dependency constraint:
- `release(X) >= release(dependency_of_X)` must hold for all X
- Violation = blocking inconsistency, must be reported

**Open questions:**
- What if an epic has no trackable items yet? How is the epic release version assigned?
- What if a feature is standalone (not part of an epic)?
- How does the AI detect which release version is "earlier"? (Semantic versioning comparison)

### 4. Skills to Update or Create

**Inventory of existing skills that create/modify requirements or tasks:**

Skills to audit (check which ones modify requirements.md or goal.md):
- `requ-explore` — creates/updates requirements.md
- `task-create` — creates goal.md
- `task-rollover` — copies/updates goal.md
- `ux-create-scenario`, `ux-update` — creates/updates UX artifacts (likely no release assignment needed)
- `requ-merge` — aggregates requirements (read-only?)
- `task-create-impl` — creates goal.md for impl tasks

**Questions to answer:**
- Which skills need release version assignment logic?
- Should there be a shared "release assignment helper" called by multiple skills?
- Where is the release definition document read? (In each skill, or in a shared step?)
- When should the AI ask the user vs. decide autonomously?
- Should a new skill `release-assign` exist for batch-assigning release versions?

### 5. Status Overview Script (`generate_status_overview.py`)

**Current behavior:** Generates STATUS.md with requirements/tasks grouped by category.

**Required extensions:**
- Group by release version (primary sort: release version, secondary: category/requirement)
- Show release description header for each group
- Include "unassigned" group for items without a release version
- Validate dependency-release consistency and report conflicts inline
- Option: `--release 0.1.0` to filter to one specific release

**Questions to answer:**
- Should release grouping replace or augment the current category grouping?
- Where in STATUS.md does the release section appear?
- What does a dependency conflict look like in the output?
- Should the script update the existing STATUS.md or generate a separate RELEASE_STATUS.md?

### 6. Dependency Validation Logic

**Design the validation algorithm:**
- Parse all release versions from all requirements.md and goal.md files
- For each item with `depends_on` or `blocked_by`, compare release versions
- Flag: item assigned to release X, but depends on item assigned to release Y where Y > X
- Output: list of conflicts with item IDs, their releases, and dependency releases

**Questions to answer:**
- Is this validation run only in the script, or also in a pre-commit hook?
- How are "TBD" releases handled in validation? (Skip? Warn? Block?)

### 7. Additional Topics (possibly overlooked)

- **Migration**: How do we assign release versions to the ~68 existing requirements and ~170 existing tasks? Batch process or incremental?
- **Release status tracking**: Do releases have a status field (planned, in-progress, released)? Does this affect how STATUS.md renders them?
- **Changelog generation**: Could the release definition document + task completion data auto-generate a CHANGELOG.md? (Out of scope for now, but worth noting.)
- **Release freeze / scope lock**: Is there a mechanism to lock what's in a release once it starts? (Probably out of scope initially.)
- **Git wokflow**: Do we have to follow a specific git wokflow to avoid any problems, especially if multiple coding agents develop features independently? 
- **Release number system**: How are the version numbers created?

## Acceptance Criteria

- [ ] Release definition document format is decided and documented
- [ ] Release version YAML field names and placement are decided and documented
- [ ] Assignment rules for epic/feature/task levels are fully specified as a decision tree
- [ ] List of skills needing updates is confirmed, with concrete change descriptions per skill
- [ ] Status overview script extension design is documented (what changes, new options)
- [ ] Dependency validation algorithm is designed
- [ ] Migration strategy for existing requirements/tasks is outlined
- [ ] All design decisions are captured in `plans_and_protocols/` for implementation tasks

## Dependencies

None — this is a foundational exploration task.

## Notes

The user has provided an initial release plan:
- 0.0.1 Alpha: QR code data transfer proof-of-concept
- 0.1.0 Beta: MVP with plan handover, client data entry, basic visualization, data transfer back to therapist
- 0.2.0+: TBD
- 1.0.0: TBD

The design must not lock us into decisions that would need to be fully rebuilt for later releases (e.g., avoid hardcoding release names in code; keep the release definition document as the single source of truth).
