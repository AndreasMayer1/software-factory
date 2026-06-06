---
id: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: active
effort: XL
stakeholder: developer
created: 2026-03-04
updated: 2026-03-26
after: [REQ-PROC-009]
blocks:
  - REQ-PROC-035
  - REQ-PROC-036
market_research_refs: [] # No relevant findings identified
trackable_items:
  sections:
    - id: SEC-01
      name: "Package Definition"
      heading: "## Package Definition"
    - id: SEC-02
      name: "Release Definition"
      heading: "## Release Definition"
    - id: SEC-03
      name: "Assignment Rules"
      heading: "## Assignment Rules"
    - id: SEC-04
      name: "User Flow Integration"
      heading: "## User Flow Integration"
    - id: SEC-05
      name: "AI Skill Behavior"
      heading: "## AI Skill Behavior"
    - id: SEC-06
      name: "Script Behavior"
      heading: "## Script Behavior"
    - id: SEC-07
      name: "Dependency Validation"
      heading: "## Dependency Validation"
---

# REQ-PROC-034: Release Package Management

## Overview

Defines how deliverable work is grouped into **release packages**, how packages are prioritized in a backlog, and how packages are assigned to **release versions** for shipping.

### Purpose

Release planning operates at three levels:

- **Packages** answer: *"What goes together?"* — named groups of related deliverables
- **Backlog ordering** answers: *"What comes first?"* — relative priority across all packages
- **Release versions** answer: *"What ships under which version number?"* — assigned when ready, changed in one place

Version numbers are never stored in requirements or tasks. Requirements and tasks reference package names. The version is derived through the package → release mapping in RELEASES.md.

### When to Use

- When creating new requirements or tasks (assign a `target_package`)
- When writing user flows (define packages in `## Release Scope` section)
- When planning releases (assign packages to versions via `release-plan` skill)
- When checking progress (view items grouped by package or release)

### When NOT to Use

- For git branching strategy (separate concern)
- For changelog generation (handled by `release` skill)
- For sprint planning within a package (use task priority instead)

---

## Package Definition

### What Is a Package?

A **release package** is a named group of related deliverables that should ship together. Packages are the atomic unit of release planning — you assign packages to releases, not individual requirements or tasks.

Examples:
- `"Data Transfer Core"` — the happy path of FLOW-003
- `"Transfer Error Recovery"` — exception bundle from FLOW-003
- `"Database Encryption"` — a technical enabler from REQ-FUNC-006
- `"Accessibility Standards"` — non-functional work from REQ-NFUNC-002

### Package Naming Rules

#### Structure

Every package name follows the pattern: **[Subject] [Capability] [Qualifier?]**

| Slot | Required | Description | Examples |
|------|----------|-------------|----------|
| Subject | YES | Who/what this is about — a role, entity, or system concern | Client, Therapist, Plan, Transfer, QR, Data, Storage |
| Capability | YES | What it does — an action, screen, or outcome | Entry, Print, Encryption, Management, Navigation |
| Qualifier | NO | Disambiguator when subject+capability alone is not unique | Core, Full, Settings, Audit |

#### Rules

| # | Rule | Example | Rationale |
|---|------|---------|-----------|
| 1 | 2–4 words | `"Data Transfer Core"` | 1 word is too vague; 5+ is too long to use as a reference |
| 2 | Start with the subject | `"Client Data Entry"` not `"Entry Client Data"` | Subject-first enables alphabetical grouping and instant scope recognition |
| 3 | Use nouns and adjectives, not verb-first phrasing | `"Client Data Print"` not `"Print Client Data"` | Consistent subject-first structure; verbs are fine as capability words in non-leading position |
| 4 | No timing or phase words | `"Transfer Core"` not `"Phase 2 Transfer"` | Names must remain valid when priorities shift |
| 5 | No implementation jargon | `"Client Data Entry"` not `"BLoC Refactor Phase 2"` | Forbidden primary words: BLoC, Repository, Cubit, Widget, Provider, Mixin, Service |
| 6 | Globally unique | — | Names serve as identifiers; checked against RELEASE_BACKLOG.md at creation |
| 7 | Similarity check before creation | — | If an existing package shares 2+ content words (excluding stop words), justify coexistence or adjust |
| 8 | Descriptive of delivered capability | `"Therapist Plan Management"` | A stakeholder reading just the name should understand what ships |
| 9 | Splittable | `"Data Transfer Core"` → `"QR Transfer Send"` + `"QR Transfer Receive"` | Names must allow future subdivision by changing the qualifier |

#### Flow-Derived Naming

| Package Type | Pattern | Example |
|-------------|---------|---------|
| Happy path | `[Flow-Subject] [Core-Capability]` | `"Data Transfer Core"` |
| Exception bundle | `[Flow-Subject] [Exception-Theme]` | `"Transfer Error Recovery"` |
| Named variant | `[Flow-Subject] [Variant-Name]` | `"Transfer Notifications"` |

#### User-Facing vs. Technical Packages

No explicit category field is needed. The naming pattern itself distinguishes:

- **UI-specific**: Subject is a UI context term — `"Client Data Entry"`, `"Therapist Navigation"`
- **Technical/enabler**: Subject is a system concern — `"Transfer Encryption"`, `"Storage Security"`, `"GDPR Compliance"`

#### Role Terms Refer to UI Context, Not Personas

When "Client" or "Therapist" appears as the subject, it refers to the **UI surface** where the feature lives — not to the user persona or user group.

| Subject term | Meaning |
|---|---|
| `Client` | Feature is part of the **Client UI** (Klientenoberfläche) |
| `Therapist` | Feature is part of the **Therapist UI** (Therapeutenoberfläche) |

This distinction matters because:
- A therapist can switch to the Client UI to test data entry — but that feature is still called "Client Data Entry" because it lives in the Client UI
- A self-user (Selbstnutzer) primarily uses the Client UI — features they access are named with "Client", not "Self"
- Future personas that use the same UI surface inherit the same subject term

**Consequence**: If a feature is visible or used in **both** UIs, do not use a role term as subject. Use the data entity instead (e.g., `"Plan Data Visualization"` rather than `"Client Data Visualization"`).

| Feature scope | Subject to use | Example |
|---|---|---|
| Only in Client UI | `Client` | `"Client Data Entry"` |
| Only in Therapist UI | `Therapist` | `"Therapist Plan Management"` |
| In both UIs (same data, same view) | Data entity | `"Plan Data Visualization"` |

Both follow the same `[Subject] [Capability] [Qualifier?]` structure. The `source.type` field in RELEASE_BACKLOG.md already captures origin (flow, requirement, standalone).

**Important**: When "Client" or "Therapist" is the subject, the Capability word must alone be specific enough to pass U5 (Scope Boundary Test). If the capability is too generic to distinguish from other same-UI features, add a qualifier.

#### Examples and Anti-Examples

| Name | Verdict | Reason |
|------|---------|--------|
| `"Client Data Entry"` | GOOD | Role subject + capability |
| `"Data Transfer Core"` | GOOD | Domain subject + qualifier indicating happy path |
| `"Storage Security"` | GOOD | System concern subject + capability |
| `"Print"` | BAD | Single word, no subject |
| `"Phase 2 Print"` | BAD | Timing word |
| `"BLoC Refactor"` | BAD | Implementation jargon |
| `"Transfer"` | BAD | Single word, too broad |

#### Grandfathering

Existing packages in RELEASE_BACKLOG.md at the time of this convention's adoption are not renamed. New packages created after adoption must follow these rules. When an existing package triggers a similarity check against a proposed new name, the new name must differentiate clearly.

#### How to Derive a Good Package Name

This subsection provides the generative counterpart to the rules above. Follow these steps to arrive at a name — whether you are an LLM executing a skill or a human naming a package manually.

##### Step-by-Step Process

1. **Describe the delivery** — Write one sentence: "After this ships, a stakeholder can ___." Do not think about naming yet.
2. **Extract the Subject** — Who is affected or what entity is central? Try in order: (a) Role (Client, Therapist), (b) Domain entity (Plan, Transfer, QR), (c) System concern (Storage, Privacy, Accessibility). Use a compound subject (e.g., "Client Data") if a single word is ambiguous.
3. **Extract the Capability** — What new ability does this deliver? Use a noun or noun phrase (Print, Entry, Encryption), not a verb phrase.
4. **Test uniqueness** — Combine Subject + Capability. Check RELEASE_BACKLOG.md for exact duplicates and 2+ word overlaps. If overlap exists, justify coexistence or merge.
5. **Add a Qualifier only if needed** — When Subject + Capability alone is not unique, or the package is part of a flow decomposition (happy path → "Core"; exception → theme word), or it covers a variant/subset ("Full", "Settings", "Audit").
6. **Apply word-form rules** — 2–4 words, subject-first, nouns/adjectives, no timing words, no implementation jargon.
7. **Run the Stakeholder Understandability Tests** — All 5 must pass.

##### Stakeholder Understandability Tests

| # | Test | Question | Pass Criterion |
|---|------|----------|----------------|
| U1 | Picture Test | Can a non-technical stakeholder picture what this delivers within 3 seconds? | The name evokes a concrete screen, action, or capability |
| U2 | Disambiguation Test | Is this name distinguishable from every other name in RELEASE_BACKLOG.md? | Differs from every other package by at least Subject or Capability |
| U3 | Completion Test | Can a stakeholder finish: "When [Name] ships, users will be able to ___"? | A non-developer can fill the blank correctly on the first try |
| U4 | Recollection Test | Could someone recall this name correctly 24 hours after seeing it once? | Uses common domain words in a natural phrase |
| U5 | Scope Boundary Test | Can a reader tell what is NOT included? | Specific enough that related-but-different capabilities are clearly outside |

If any test fails, return to the corresponding step (2–5) and revise.

#### Package Granularity Guidelines

**When to create a new package** (all three must hold):
1. The ACs describe a capability that can ship independently of existing packages
2. The capability has a distinct demo story (a stakeholder can see what changed)
3. Adding the ACs to an existing package would blur that package's description

**When to join an existing package**:
- The new ACs are a natural extension of an existing package's scope
- Adding them does not require changing the package name to stay accurate
- The combined package stays within the 3–18 impl task size range

**Preventing oversized packages**: When a package exceeds 18 impl tasks (adjusted estimate), split along a capability boundary. The naming convention supports this: specific names can be subdivided by changing the qualifier (e.g., "Data Transfer Core" → "QR Transfer Send" + "QR Transfer Receive"). When the Shared UI Surface Constraint prevents a clean split, document the package as an exception (acceptable range up to 22). See `requirements_tasks/package_assignment_rules.md` for current documented exceptions.

**Initial sizing philosophy — err on the broader side**: When creating a package for the first time, it is better to cut it slightly broader than too narrow. The reason: merging two packages later is painful (backlog entries, references, and release assignments must be reconciled), while splitting is well-supported by Rule 9 (splittable names) and the 18-task size trigger. In practice: size the initial package so it satisfies the 3–18 task range given what is *known today*. Future requirements that fit the name and keep the package within range join it organically; requirements that would push it over 18 tasks or blur the name trigger a split. Over-engineering the initial cut — splitting preemptively before any requirements exist — creates unnecessary overhead and fragments the backlog.

**Adjusted task estimation**: raw AC counts overstate impl burden — non-functional specs bundle many ACs into one task. Use the weighted formula in `requirements_tasks/package_assignment_rules.md → Package Size Guidelines` before checking against the threshold.

**Shared UI Surface Constraint**: When two features that share the same primary screen or component are assigned to different packages, the *earlier* package must include the full UI skeleton for all known modes of that surface — layout, mode-switching controls, and navigation entry points — even if later-mode functionality is not yet implemented. A later package may wire functionality into existing UI entry points but must not require restructuring the screen's layout or navigation.

> **Corollary**: If pre-building the skeleton significantly expands the earlier package's scope, treat that as a signal to reconsider whether the features should be in the same package instead.

> **Scope**: Applies only when both features are known at design time and the shared screen uses distinct operating modes (not merely additive content appended below existing layout). In alpha PoC releases (0.0.x) the screen layout may remain provisional; the constraint applies from the first Beta (0.1.x) onward when the shared screen is intended as the shipping UI.

### Package Sources

Packages originate from three sources:

| Source Type | When Created | Example |
|-------------|-------------|---------|
| **Flow-based** | During `ux-create-flow` or `requ-derive-from-flow` | Happy Path → 1 package; exception bundles → additional packages |
| **Requirement-based** | During `requ-explore` for enablers/foundations | Technical prerequisites that multiple flows depend on |
| **Standalone** | Ad hoc, by user decision | Process improvements, non-functional work, bugfix campaigns |

**Flow-based packages** carry a `priority_within_source` field:
- `1` = Happy Path (always the first package from a flow)
- `2` = First exception bundle (most important exceptions)
- `3`, `4`, ... = Subsequent exception bundles, named variants

**Requirement-based and standalone packages** have `priority_within_source: null` (no intra-source ranking; only backlog position matters).

### RELEASE_BACKLOG.md

**Location**: `requirements_tasks/RELEASE_BACKLOG.md`

This file is the single source of truth for all release packages. Skills and scripts discover it at this conventional path.

**Format**: YAML frontmatter (package list) + Markdown body (human-readable descriptions and usage instructions).

**Ordering**: Position in the `packages` list = global priority. First entry = highest priority. To reprioritize, move entries up or down in the list. No numeric index fields — position is the index.

#### Package Entry Schema

```yaml
---
packages:
  - id: "Data Transfer Core"
    source:
      type: flow            # flow | requirement | standalone
      ref: "FLOW-003"       # flow ID, requirement ID, or null
      scope: "Happy Path (Steps 1–8)"  # what part of the source this covers
    description: "QR code data beam between therapist and client devices — unencrypted PoC"
    priority_within_source: 1  # 1 for happy path, 2+ for exception bundles, null for non-flow
    status: planned            # planned | versioned | released
    assigned_release: null     # null (in backlog) or version string (e.g., "0.0.1")

  - id: "Database Encryption"
    source:
      type: requirement
      ref: "REQ-FUNC-006"
      scope: "SEC-02: Local Storage Encryption"
    description: "Encrypt local database at rest using secure key storage"
    priority_within_source: null
    status: versioned
    assigned_release: "0.0.2"
---
```

#### Package Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Human-readable name, max 4 words, globally unique |
| `source.type` | enum | YES | `flow`, `requirement`, or `standalone` |
| `source.ref` | string/null | YES | Source identifier (FLOW-NNN, REQ-XXX-NNN) or `null` for standalone |
| `source.scope` | string | NO | What part of the source this package covers |
| `description` | string | YES | One-line summary of what this package delivers |
| `priority_within_source` | int/null | NO | Intra-flow priority (1 = happy path). Null for non-flow packages |
| `status` | enum | YES | `planned` → `versioned` → `released` |
| `assigned_release` | string/null | YES | `null` if unassigned, or semver version string |

#### Package Lifecycle

```
planned  →  versioned  →  released
```

- **planned**: Package exists in backlog, not yet assigned to a release version
- **versioned**: Package is assigned to a specific release version in RELEASES.md
- **released**: The release containing this package has shipped

Transitions:
- `planned → versioned`: When `release-plan` skill assigns the package to a version
- `versioned → released`: When `release` skill marks the containing release as released
- `versioned → planned`: When a package is removed from a release (unscheduled)

---

## Release Definition

### RELEASES.md

**Location**: `requirements_tasks/RELEASES.md`

RELEASES.md is the single source of truth for release versions and their package composition. It maps version numbers to packages.

**Format**: YAML frontmatter (release list) + Markdown body.

#### Release Entry Schema

```yaml
---
releases:
  - version: "0.0.1"
    name: "Alpha – Data Transfer"
    status: planned            # planned | active | released
    description: "Proof of concept for QR code data transfer"
    planned_date: null         # YYYY-MM-DD or null
    packages:                  # list of package IDs from RELEASE_BACKLOG.md
      - "Data Transfer Core"
    goals:                     # high-level objectives (optional, for human context)
      - "Validate QR data beam concept"
    scope_boundaries:          # kept for high-level excludes
      excludes:
        - "Encryption of any kind"
---
```

What a release includes is defined by its `packages` list. `scope_boundaries.excludes` documents what is explicitly *not* in the release.

#### Release Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | YES | Semantic version (`MAJOR.MINOR.PATCH`) |
| `name` | string | YES | Human-readable name |
| `status` | enum | YES | `planned` → `active` → `released` |
| `description` | string | YES | One-line summary |
| `planned_date` | date/null | NO | Target date or null |
| `packages` | list[string] | YES | Package IDs from RELEASE_BACKLOG.md |
| `goals` | list[string] | NO | High-level objectives |
| `scope_boundaries` | object | NO | `excludes` list |

#### Release Status Lifecycle

```
planned  →  active  →  released
```

- **planned**: Release is defined but no task work has started
- **active**: At least one task for a package in this release is `in_progress`
- **released**: All packages in this release are complete and shipped

#### Version Number System

Versions follow **semantic versioning** (`MAJOR.MINOR.PATCH`):

| Range | Phase | Meaning |
|-------|-------|---------|
| `0.0.x` | Alpha | Proof-of-concept, experimental validation |
| `0.x.0` | Beta | Incremental MVP builds |
| `1.0.0+` | Release | Production-ready |

Version comparison uses standard semver ordering: `0.0.1 < 0.1.0 < 0.2.0 < 1.0.0`.

#### No Autonomous Release Creation

The AI must **never** create new release versions or new packages autonomously. Both require explicit user approval. The AI may suggest — e.g., "This feature doesn't fit any existing package. Should I create a new one?" — but must wait for confirmation.

---

## Assignment Rules

### Overview

Requirements and tasks reference **package names** via the `target_package` field (not version numbers). The version number is derived indirectly: package → `assigned_release` in RELEASE_BACKLOG.md → version in RELEASES.md.

### Decision Tree

```
Is this a REQUIREMENT?
├── YES: Does it have trackable_items?
│   ├── YES: Assign target_package per trackable item
│   │   └── Requirement's target_package = earliest-priority among its items
│   └── NO: Assign target_package directly to the requirement
│       └── AI asks user if uncertain
│
└── NO (it's a TASK): Does covers reference trackable items?
    ├── YES: Inherit target_package from the earliest-priority covered item
    │   └── If covered items span multiple packages → use highest-priority (earliest in backlog)
    └── NO: Assign target_package directly to the task
        └── AI asks user if uncertain
```

### "Earliest" Determination

"Earliest" means **highest backlog priority** (earliest position in RELEASE_BACKLOG.md). When comparing packages:

1. If both packages have `assigned_release`: compare by semver (lower version = earlier)
2. If only one has `assigned_release`: the versioned one is earlier (it ships sooner than an unscheduled package)
3. If neither has `assigned_release`: compare by position in RELEASE_BACKLOG.md (lower index = higher priority = earlier)

### Epic Level

- Each trackable item (AC/section) within an epic gets its own `target_package`
- The epic's top-level `target_package` = the **earliest-priority** package among its assigned trackable items
- If no trackable items are assigned yet, the epic's `target_package` is omitted

### Feature Level

- Feature trackable items each get their own `target_package`
- The feature's top-level `target_package` = the **earliest-priority** package among its assigned items

### Task Level

- A task's `covers` field references specific trackable items (ACs or sections)
- The task inherits `target_package` from the **earliest-priority** covered trackable item
- If `covers` is empty, the task gets an individual `target_package`
- The AI assigns automatically when the inheritance is clear; asks the user when ambiguous

### Process / Non-Functional Requirements

- Follow the same rules as features
- Many process requirements will remain unassigned (internal tooling, no user-facing package)

### Cross-Cutting Requirements (Bugfixes, Process Improvements, Small Tasks)

Cross-cutting requirements — such as bugfixes, non-functional improvements, and process tasks — often don't warrant a dedicated package in RELEASE_BACKLOG.md. For these:

- `target_package` may be set directly to any existing package `id` in RELEASE_BACKLOG.md, chosen by the author as the most appropriate home
- There is **no requirement** that RELEASE_BACKLOG.md contains a `ref:` entry pointing back to the requirement or task; a name match is sufficient for validation
- When a version has no scoped package whose `ref` matches the requirement, the **first-listed package for that version** in RELEASE_BACKLOG.md serves as the primary fallback `target_package`

The AI should suggest the primary package for the relevant version as a default when the user has not indicated a preference and no `suggested_package` is available.

### YAML Metadata

#### Requirements (`requirements.md`)

```yaml
---
id: REQ-FUNC-007
target_package: "Transfer Data Model"  # computed: earliest-priority among items
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Therapist can transfer plan to new client"
      target_package: "Transfer Data Model"
    - id: AC-02
      text: "Remote transfer via encrypted file works"
      target_package: "Flexible Transfer Core"
    - id: AC-03
      text: "Self-test mode for therapist"
      # target_package absent = not yet assigned
---
```

#### Tasks (`goal.md`)

```yaml
---
task_id: TASK-FUNC-007-01
target_package: "Transfer Data Model"  # inherited from covered items or assigned directly
covers:
  acceptance_criteria: [AC-01]
  sections: []
---
```

### Summary of States

| State | YAML Representation | Meaning |
|-------|-------------------|---------|
| Not yet assigned | Field absent | No package decision made |
| Assigned | `target_package: "QR Transfer Send"` | Belongs to named package |

---

## User Flow Integration

### Release Scope Section in flow.md

User flows include a `## Release Scope` section that captures the author's intent about which parts of the flow map to which packages. This section is created during `ux-create-flow` and updated during flow iterations.

#### Format

```markdown
## Release Scope

> Authoring intent — canonical package assignments are in requirements.md per-AC `target_package` fields.
> Update this section when the flow is iterated.

| Package | Items | Rationale |
|---------|-------|-----------|
| Flexible Transfer Core | Happy Path (Steps 1–9) | Core path — must ship for Weber use case |
| Transfer Error Recovery | Exceptions 7.2, 8.1 | Important but not blocking initial use |
| Transfer Notifications | Step 1, Exceptions 2.1–2.2, 3.1, 5.1 | Notification-based trigger path |
| TBD | Exception 10.1 (print) | Architecture decisions unresolved |
```

#### Section Placement

Between `## Implementing Epics/Features` and `## Gaps Requiring New Requirements` in flow.md.

#### Authoring Rules

1. **Happy Path = one package** (always). The package name describes the core capability.
2. **Exception bundles**: Group related exceptions into packages. Exceptions that serve the same persona need or address the same technical concern belong together.
3. **TBD is allowed**: Items with unresolved architecture decisions or unclear priority use `TBD` instead of a package name.
4. **NEW marker**: If a needed package does not yet exist in RELEASE_BACKLOG.md, mark it with `**NEW**` in the Package column. The `release-plan` skill (or manual entry) creates it in the backlog.

#### How Packages Flow from Flows to Requirements

```
ux-create-flow
  → Author defines Release Scope section (package names + items)
  → Packages marked **NEW** are noted for later creation

requ-derive-from-flow
  → Reads Release Scope section from flow.md
  → Adds "Suggested Package" column to requirements matrix
  → Writes suggested_package to goal.md frontmatter

requ-explore
  → Reads suggested_package from goal.md (if present)
  → Uses as default when prompting user for target_package
  → User confirms, changes, or skips
```

### Package Creation from Flows

When `ux-create-flow` completes and the Release Scope section contains **NEW** packages:

1. The skill lists the new packages and asks: "Should I add these packages to RELEASE_BACKLOG.md?"
2. If user confirms: add each new package to RELEASE_BACKLOG.md with `status: planned`, `assigned_release: null`, and the flow as source
3. Position in backlog: append at end (user can reprioritize later via `release-plan`)

### When Release Scope Is Optional

The Release Scope section is **recommended but not mandatory**. Flows in early draft status may omit it. The `ux-create-flow` skill asks about it during metadata gathering (Step 2) but accepts "skip" as an answer.

---

## AI Skill Behavior

### Skills and Their Responsibilities

| Skill | Responsibility |
|-------|---------------|
| `requ-explore` | Reads RELEASE_BACKLOG.md for available packages. Presents package names to user during assignment (Section 2.4). Accepts `suggested_package` from goal.md as default. Computes top-level `target_package` as earliest-priority package. |
| `task-create` | Reads parent requirement's trackable item packages. Inherits earliest-priority `target_package` from covered items. Validates package name against RELEASE_BACKLOG.md. Prompts user when inheritance is ambiguous. |
| `task-create-impl` | Same as `task-create` for `target_package` inheritance. |
| `requ-prep-release` | Verifies every package in the release's `packages` list has complete requirements and implementation tasks. Checks package coverage instead of scope boundary coverage. |
| `ux-create-flow` | Asks about Release Scope during metadata gathering (Step 2). Includes Release Scope section template for Opus (Step 6). Validates section present (Step 10). Notes **NEW** packages for backlog creation (Step 12). |
| `requ-derive-from-flow` | Extracts Release Scope section from flow.md (Phase 1). Adds "Suggested Package" column to requirements matrix (Phase 2). Writes `suggested_package` in goal.md frontmatter (Phase 4). |
| `release` | After marking a release as released, updates all packages in the release's `packages` list to `status: released` in RELEASE_BACKLOG.md. |
| `release-plan` | Reads RELEASE_BACKLOG.md. Shows unversioned packages to user. Lets user assign packages to existing or new versions. Validates new package names against naming convention (SEC-01). Updates RELEASE_BACKLOG.md (`assigned_release`, `status: versioned`) and RELEASES.md (`packages` list). |

### Shared Logic

Each skill reads `requirements_tasks/RELEASE_BACKLOG.md` directly using the conventional path:

1. Read `requirements_tasks/RELEASE_BACKLOG.md`
2. Parse the `packages` list from YAML frontmatter
3. Present available package names to user when prompting
4. Validate that chosen package name exists in RELEASE_BACKLOG.md

For version lookups (when needed): read `requirements_tasks/RELEASES.md`, find the release whose `packages` list contains the target package.

### When to Ask vs. Decide Autonomously

| Situation | Behavior |
|-----------|----------|
| Task covers trackable items with packages | **Auto-assign** (inherit earliest-priority) |
| Task covers trackable items without packages | **Ask user** |
| Task has empty `covers` | **Ask user** |
| New requirement, `suggested_package` available from goal.md | **Propose** suggested_package as default, ask user to confirm |
| New requirement, no suggestion | **Ask user** with list from RELEASE_BACKLOG.md |
| Existing requirement, item already has package | **Preserve** existing; do not ask |

---

## Script Behavior

### Scripts and Their Responsibilities

| Script | Responsibility |
|--------|---------------|
| `validate_meta.py` | Validates `target_package` as a string matching a package ID in RELEASE_BACKLOG.md. Validates that top-level `target_package` equals the earliest-priority package among trackable items. Runs package-based dependency validation (see Dependency Validation section). |
| `generate_status_overview.py` | Groups items by `target_package`. `--release-summary` mode shows packages within each release. `--package-summary` mode shows all packages with their status, assigned release, and item counts. `--package PACKAGE` flag filters output to items in a specific package. `--release VERSION` flag filters to packages in that release. |
| `next_tasks.py` | Finds the next package to work on: the highest-priority unfinished package in the active release, or the highest-priority unfinished package in the backlog if no release is active. Ranks tasks by package priority. Supports `--package PACKAGE` flag. |
| `generate_technical_release_notes.py` | Collects tasks by `target_package`, matching packages listed in the active release's `packages` list. Groups release note entries by package for structure. |

### Data Model (All Scripts)

All scripts use these fields in their data models:

- `target_package: Optional[str]` on RequirementData and TaskData
- `known_packages: Set[str]` loaded from RELEASE_BACKLOG.md
- `package_priorities: Dict[str, int]` — package name → position index in backlog (for ordering)
- `package_to_release: Dict[str, Optional[str]]` — package name → assigned version (for version-level queries)

---

## Dependency Validation

### Package Ordering Constraint

For any item X that depends on item Y:

```
backlog_position(package(X)) >= backlog_position(package(Y))
```

In words: if X depends on Y, then Y's package must be at least as high-priority (same or earlier position) as X's package. You cannot ship X before Y.

### Version Constraint (When Both Assigned)

When both packages have `assigned_release`:

```
semver(release(package(X))) >= semver(release(package(Y)))
```

The version constraint is derived through the package → release mapping.

### Handling Unassigned Items

- If either X or Y has no `target_package`: **skip** (no validation possible)
- If packages exist but neither has `assigned_release`: use backlog position for ordering check
- Unassigned items appear in a separate "Unassigned" group in reports

### Where Validation Runs

| Location | When | Action on Conflict |
|----------|------|-------------------|
| `generate_status_overview.py` | Every STATUS.md generation | Report in output (warning section) |
| `validate_meta.py` | On `task-complete` and manual runs | Report as validation warning |

### Conflict Output Format

```
## Package-Dependency Conflicts

| Item | Package | Depends On | Dep Package | Conflict |
|------|---------|------------|-------------|----------|
| TASK-FUNC-007-01 | Data Transfer Core | REQ-FUNC-006 | Database Encryption | Dependency package is lower priority in backlog |
```

When both have versions:
```
| TASK-FUNC-007-01 | Data Transfer Core (0.0.1) | REQ-FUNC-006 | Database Encryption (0.0.2) | Dependency ships in later release |
```

---

## Developer Guidelines

### Key Decisions

1. **RELEASE_BACKLOG.md is the single source of truth** for package definitions. Never hardcode package names in skills or scripts — always read from the file.

2. **RELEASES.md is the single source of truth** for version-to-package mappings. Never store version numbers in requirements or tasks.

3. **Trackable items are the atomic unit** of package assignment. Top-level `target_package` is always computed (earliest-priority among items), never set independently.

4. **`target_package` is optional everywhere.** The system degrades gracefully when items are unassigned — they appear in an "Unassigned" group.

5. **Package names are stable identifiers.** Once a package exists in RELEASE_BACKLOG.md and is referenced by requirements/tasks, its name should not change. If renaming is necessary, a find-and-replace across all referencing files is required.

6. **Backlog position is the priority.** No numeric priority fields on packages — position in the YAML list is the priority. Move entries to reprioritize.

### Common Pitfalls

- **Don't set top-level `target_package` without setting trackable item packages.** The top-level field is derived from items, not the other way around.
- **Don't forget dependency validation.** When creating a high-priority package, check that its dependencies are in equal or higher-priority packages.
- **Don't create packages or releases without user approval.** The AI suggests, the user decides.
- **Don't store version numbers in `target_package`.** The field holds a package name (string), never a semver version.
- **Don't confuse backlog priority with urgency/impact.** Backlog position is *product-level* priority (when does this ship?). Urgency/impact on requirements/tasks is *execution-level* priority (within a package, what do we work on first?).

## Related Requirements

- **REQ-PROC-009** (Requirements and Tasks Structure): This requirement extends the metadata standards defined there

## References

- File: `requirements_tasks/package_assignment_rules.md` — **operational extract of this requirement for skills** (auto-assign rules, decision tree, Shared UI Surface Constraint). Any change to assignment rules here must also be applied there. Note this obligation in the commit message.
- File: `requirements_tasks/RELEASE_BACKLOG.md` — package definitions
- File: `requirements_tasks/RELEASES.md` — version-to-package mappings
- Script: `scripts/validate_meta.py` — MetaValidator class
- Script: `scripts/generate_status_overview.py` — RequirementData/TaskData dataclasses, ReleaseSummaryReportGenerator
- Script: `scripts/next_tasks.py` — package-based task ranking
- Script: `scripts/generate_technical_release_notes.py` — package-based release note collection
- Skills: `.claude/skills/requ-explore/`, `.claude/skills/task-create/`, `.claude/skills/task-create-impl/`, `.claude/skills/requ-prep-release/`, `.claude/skills/ux-create-flow/`, `.claude/skills/requ-derive-from-flow/`, `.claude/skills/release/`, `.claude/skills/release-plan/`
