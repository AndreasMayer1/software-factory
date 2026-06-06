---
id: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: active
effort: M
stakeholder: developer
created: 2026-04-26
updated: 2026-06-01
after: [REQ-PROC-009]
blocks: []
market_research_refs: [] # No relevant findings identified
target_package: ""  # internal process tooling — unassigned
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Every `epic_*` folder whose anchor file has a status other than `draft` contains at least one `feat_*` subfolder."
    - id: AC-02
      text: "Every `feat_*` folder contains a `requirements.md` file."
    - id: AC-03
      text: "No `feat_*` folder is a direct child of a top-level category folder (`functional/`, `non-functional/`, `process/`); it must be nested at least one level deeper inside a grouping folder or epic."
    - id: AC-04
      text: "No `epic_*` folder is nested inside another `epic_*` folder."
    - id: AC-05
      text: "Every `id:` value in any requirements.md frontmatter under `requirements_tasks/` appears as an entry in `requirements_tasks/_meta/id_registry.md`."
    - id: AC-06
      text: "The structural validation script enforces AC-01 through AC-05 and AC-10 through AC-17 in addition to the existing epic body line limit and feature-folder presence checks."
    - id: AC-07
      text: "The `release-begin-impl` skill Phase 0 pre-flight invokes the structural validation script and aborts when violations are reported."
    - id: AC-08
      text: "The `requ-explore` skill quality-check phase invokes the structural validation script against any newly written or modified requirement; the task cannot be closed while violations exist."
    - id: AC-10
      text: "Every `epic_*` folder contains a `requirements.md` file."
    - id: AC-11
      text: "A cross-reference completeness detection mechanism exists that, given a target requirement under `requirements_tasks/`, returns the set of semantically related requirements not already cross-referenced by that target. The mechanism derives 2–4 search terms from the target requirement's topic (domain nouns, action verbs, component names), greps across `requirements_tasks/functional/`, `requirements_tasks/non-functional/`, and `requirements_tasks/process/`, and excludes any hit whose REQ-ID already appears in the target's `after:` chain, `blocks:` chain, or `## Related Requirements` body section. The mechanism is invoked by `requ-explore` Phase 1.4 (overlap detection during authoring) and by `task-derive-from-requ` Phase 1.5 (cross-reference completeness gate before task creation, per REQ-PROC-058 AC-17). The choice between a script implementation and inline skill instructions is left to implementation tasks."
    - id: AC-12
      text: "Every folder under `requirements_tasks/` that contains semantic sub-folders carries an anchor file. Semantic folder anchors are `requirements.md` (for `epic_*` and `feat_*` folders); grouping folder anchors are `README.md`. `tasks/` and `plans_and_protocols/` are non-semantic and do not require anchor files."
    - id: AC-13
      text: "Every anchor file contains a `## Inclusion Criteria` section (what kinds of requirements or sub-folders this folder accepts) and a `## Anti-Scope` section (what it explicitly does not accept, including the names of adjacent clusters that legitimate-looking-but-not-belonging requirements would otherwise drift toward). Grouping folder anchors additionally contain a `## Sub-Axis` section naming the single dimension along which their immediate children are clustered."
    - id: AC-14
      text: "At every hierarchy level inside `requirements_tasks/`, the immediate child folders of any one folder are clustered along a single axis declared in that folder's anchor file. The set of axes available to each top-level category is enumerated in section `## Sanctioned Top-Level Axes` of this requirement. Folders whose immediate children would require multiple axes to describe them do not exist."
    - id: AC-15
      text: "Placement of a new requirement under `requirements_tasks/` is determined by a deterministic walk from the relevant top-level category, descending at each level into the unique child folder whose `## Inclusion Criteria` matches the new requirement and whose `## Anti-Scope` does not exclude it. The walk produces either a single destination folder or halts with no match. Ad-hoc placement under a folder whose `## Inclusion Criteria` does not match is disallowed."
    - id: AC-16
      text: "Resolution of a halted placement (AC-15) follows one of three named paths: (a) refine the `## Inclusion Criteria` of an existing folder so the new requirement now matches, (b) introduce a new sub-axis or sibling cluster under an existing axis through modification of this requirement and the affected anchor files, (c) introduce a new top-level axis through modification of this requirement's `## Sanctioned Top-Level Axes` section. Paths (b) and (c) require explicit user authorization recorded in the modifying commit."
    - id: AC-17
      text: "The top-level categories `functional/`, `non-functional/`, and `process/` each have exactly one declared axis governing their immediate children, as enumerated in section `## Sanctioned Top-Level Axes`. No top-level category mixes axes at the same level."
    - id: AC-18
      text: "`requ-explore` performs a reactive restructuring analysis after the location is confirmed (Phase 2.1a) and before writing any files. The location approval message (Phase 2.1a) explicitly notifies the user that this analysis will follow, so the user does not preemptively do the work manually. Three cases are detected in the authored requirement's neighborhood: (A) sibling-bundling — existing `feat_*` siblings in the same grouping share the new requirement's primary domain concept; (B) feature-oversize — the authored or extended `feat_*` requirement has more than 10 acceptance criteria; (C) obsolescence — an existing requirement's full scope is subsumed by the new content. Each detected case is presented to the user in a separate approval gate before writing. Cases A and B are Path B events (SEC-06); case C transitions the obsoleted requirement to `deprecated` with a `superseded_by: [new-REQ-ID]` field in its frontmatter. Silent when no case is detected."
  sections:
    - id: SEC-01
      name: "Naming Conventions"
      heading: "## Naming Conventions"
    - id: SEC-02
      name: "Folder Shapes and Anchor Files"
      heading: "## Folder Shapes and Anchor Files"
    - id: SEC-03
      name: "Sanctioned Top-Level Axes"
      heading: "## Sanctioned Top-Level Axes"
    - id: SEC-04
      name: "Epic Demarcation"
      heading: "## Epic Demarcation"
    - id: SEC-05
      name: "Placement Algorithm"
      heading: "## Placement Algorithm"
    - id: SEC-06
      name: "Governance: Changing the Taxonomy"
      heading: "## Governance: Changing the Taxonomy"
    - id: SEC-07
      name: "LLM Judgment Checklist"
      heading: "## LLM Judgment Checklist"
    - id: SEC-08
      name: "Cross-Reference Completeness Detection"
      heading: "## Cross-Reference Completeness Detection"
    - id: SEC-09
      name: "Reactive Restructuring Analysis"
      heading: "## Reactive Restructuring Analysis"
---

# Requirements Structure Quality

## Overview

A consistent folder, naming, and metadata structure for requirements is a quality property of the factory itself. When the structure is uniform, both human readers and LLM sessions can navigate `requirements_tasks/` reliably and reach the right place to add or look up a requirement. When it drifts — when clusters along different axes coexist at the same level, when grouping folders carry semantics only in their names, when overlapping categories silently legitimise the same content in two places — navigation errors compound and downstream automation degrades silently.

Rules split into two classes: **script-checkable** (acceptance criteria) and **convention / LLM-judgment** (sections). Both classes are enforced at workflow boundaries.

## Purpose

Make requirements structure a continuously enforced quality property — not an aspirational guideline. The folder tree is a finding device: at every level a reader (human or LLM) can read a single, explicit anchor file, decide where a new requirement belongs, and have that decision be the same one a different reader would make from the same evidence. Mechanical checks run automatically at requirement authoring (`requ-explore`) and release start (`release-begin-impl` Phase 0), so structural drift is caught at the point it would be introduced.

## Scope

**In scope**: folder hierarchy and shapes; naming conventions; epic / feature / standalone classification; the single-axis-per-level rule and the set of sanctioned axes; anchor files and their required sections; the placement algorithm a new requirement follows; the governance gate for changing the taxonomy; ID registry consistency; integration of validation into authoring and release workflows.

**Out of scope**: user-needs structure under `requirements_user_needs/` (governed by REQ-PROC-010); per-requirement content quality (covered by `requ-explore` Phase 2.5 quality checklist); the order and timing of converting any specific existing folder to the structure described here — that is task-level work, not part of this requirement.

## Naming Conventions

**Theoretical basis.** Two principles drive every naming decision.

*DDD ubiquitous language*: names come from the vocabulary that users and domain experts actually use — not from technical or implementation terms. "Plan management" rather than "CRUD for treatment protocols". A reader of the folder tree recognises the concept names from their own domain. For `functional/` the authoritative source for this vocabulary is the user flow library under `requirements_user_needs/user_flows/`. For `non-functional/` and `process/` the vocabulary comes from the artifact, system concern, or rule topic itself, expressed in the same plain-language form.

*Semantic cohesion (ontology design)*: a well-named cluster predicts its contents. A reader who sees `epic_data_transfer` can predict `feat_qr_data_transfer`, `feat_file_data_transfer`, `feat_transfer_notifications` without opening the folder. A reader who sees `process/requirement_rules/` can predict the contents are rules about how requirements themselves are authored, structured, and reviewed. If a child's name surprises a reader given the parent's name, either the child is misplaced or the parent is misnamed.

**Naming rules.**
- Folder names are lowercase, snake_case, English only.
- A folder name is valid only if it would be self-explanatory to a reader who has never seen the codebase. Single-character names, generic abbreviations (`feat_misc`, `epic_a`, `feat_tmp`), and lifecycle markers (`wip`, `v2`, `2026_q2`) are forbidden.
- The `epic_` and `feat_` prefixes are reserved structural markers — never used decoratively or as part of a domain concept.
- The folder name alone is never the sole carrier of placement semantics. The folder's anchor file (SEC-02) is. The name is a memorable handle for what the anchor file says in full.

**Sub-grouping threshold.** When ≥ 4 sibling clusters in the same parent share a sub-concept, a sub-grouping folder collects them, with the parent's declared sub-axis governing whether the sub-grouping is admissible. The threshold of four comes from cognitive load research (Miller's Law): four items is roughly the point at which a list can no longer be scanned at a glance.

## Folder Shapes and Anchor Files

Three legitimate folder shapes exist under `requirements_tasks/`. Every folder is one of these three; no fourth shape is permitted.

| Shape | Anchor file | Allowed children | Purpose |
|---|---|---|---|
| **Atomic requirement** | `requirements.md` with acceptance criteria and/or sections | `tasks/` only | Holds a single flat requirement that does not decompose into sub-features. |
| **Epic** | `requirements.md` with `## Inclusion Criteria`, `## Anti-Scope`, and the standard epic body | `feat_*/` (and `tasks/`, `plans_and_protocols/`) | Holds a coherent cluster of features sharing one user goal or one quality concern. |
| **Grouping** | `README.md` with `## Inclusion Criteria`, `## Anti-Scope`, and `## Sub-Axis` | `epic_*/`, standalone `feat_*/`, or further grouping folders | Organises semantic clusters along a single declared axis. Carries no acceptance criteria of its own. |

`tasks/` and `plans_and_protocols/` are non-semantic infrastructure subfolders and require no anchor.

**Epic anchor — required sections.** In addition to the existing Epic Size Gate (90-line body limit, allowed section set), every epic's `requirements.md` contains:

- `## Inclusion Criteria` (positive predicates): the concrete kinds of features the epic accepts. Written as descriptive statements a reader can evaluate against a candidate feature, not as a list of feature names. Example: *"Features that govern how the LLM agent decides where in the artifact tree a new requirement belongs"* (not *"placement algorithm, anchor files, governance"*).
- `## Anti-Scope` (negative predicates): the concrete kinds of features the epic refuses, naming by REQ-ID the adjacent clusters a misplaced feature would otherwise drift toward. Example: *"Rules about how individual requirement content is written (covered by REQ-PROC-049 language coherence) are not in scope here, even when the misplacement seems natural."*

**Grouping anchor — required sections.** Every grouping folder's `README.md` contains:

- `## Inclusion Criteria` (same shape as epic) — what kinds of clusters belong inside.
- `## Anti-Scope` (same shape as epic) — what kinds of clusters do not, naming adjacent groupings.
- `## Sub-Axis` — the single named dimension along which immediate child folders are clustered, drawn from the sanctioned axes for the relevant top-level category (SEC-03). One axis per grouping; multi-axis groupings are not legitimate.

## Sanctioned Top-Level Axes

Each top-level category in `requirements_tasks/` clusters its immediate children along exactly one declared axis. The axes are:

| Top-level category | Axis | Allowed axis values (immediate children) |
|---|---|---|
| `functional/` | **WHO–WHAT** (persona scope × domain concept) | `client/`, `shared/`, `therapist/` — each a grouping folder whose own sub-axis is the domain concept (epic / feat names) |
| `non-functional/` | **system concern category** | `architecture/`, `branding/`, `integration_tests/`, `ui_ux_design_system/` and other sanctioned non-functional concerns; each is itself a grouping folder declaring its own sub-axis |
| `process/` | **artifact type** | `persona_rules/`, `scenario_rules/`, `flow_rules/`, `requirement_rules/`, `task_rules/`, `code_rules/`, `doc_rules/`, `skill_and_workflow_rules/`, `tooling_rules/`, `cross_artifact_rules/`, `meta_rules/` |

The "artifact type" axis under `process/` is the set of artifact kinds the factory authors or maintains. Rules about LLM-specific artifacts (skills, prompts, agent configurations) live under `skill_and_workflow_rules/` because those artifacts are themselves artifact kinds the factory produces — the distinction "rule for human author / rule for LLM author" is orthogonal and lives in YAML frontmatter (`applies_to:` tag), not in folder structure.

`cross_artifact_rules/` is the bounded exception bucket for rules that genuinely span multiple artifact types with no single primary artifact (release readiness, end-to-end chain integrity, factory quality umbrella). It is not a fallback for cases where placement is uncertain; uncertainty is resolved through the governance gate (SEC-06), not by absorbing the requirement into the exception bucket.

`meta_rules/` holds rules about how the rule-set itself is governed — this requirement, REQ-PROC-049 (language coherence), the factory's purpose and operating principles. It is the only place that may contain rules about rules.

Each sub-grouping folder declares its own sub-axis in its `README.md`'s `## Sub-Axis` section, drawn either from the sanctioned axes above (when reused at a deeper level) or from an axis specific to its content. Sub-axes do not need to be enumerated in this requirement, but they do follow the single-axis-per-level rule and the governance gate for changes.

## Epic Demarcation

What makes an epic boundary correct depends on the category. The boundary tests differ because the kind of value epics deliver differs.

### Functional epics

Three tests; all three must pass.

1. **Independent user value test.** End users get meaningful value from Epic A without Epic B being complete. If not, A and B belong in the same epic.
2. **Domain entity test.** All features of an epic operate on the same primary domain entity or serve the same coherent user goal. Features spanning two unrelated domain entities belong in separate epics.
3. **Parallel development test.** Epic A and Epic B can be handed to two developers to build in parallel with minimal coordination. If significant daily coordination would be required, the boundary is wrong.

### Non-functional and process epics

Three tests; all three must pass. These differ from the functional tests because non-functional and process epics deliver value to the *system* or *the development workflow*, not directly to end users — so the independent-user-value test does not apply.

1. **Conceptual coherence test.** The epic concerns one identifiable system concern, workflow, or quality axis. A reader can describe the epic's purpose in one sentence without an "and" connecting two unrelated concerns.
2. **Independent improvement test.** Features inside the epic can be improved independently of sibling epics. Improvement work on one does not require coordinated changes elsewhere in the same release window.
3. **Stable boundary test.** The epic's `## Inclusion Criteria` describe a scope that is stable over time. New candidate requirements either clearly belong (the criteria match) or clearly do not. The boundary does not need renegotiation each time a new requirement arrives.

### Depth via grouping, not via nested epics

Epics never nest inside other epics (AC-04). When a domain concept or system concern is large enough that its features cluster into sub-concepts, those sub-concepts become **separate sibling epics under a shared sub-grouping folder** — not child epics. Example: `data_movement/epic_backup/` and `data_movement/epic_transfer/` are siblings under a sub-grouping; neither is a child of the other.

### Anti-patterns

- Two epics with no features that could be developed independently → merge.
- One epic whose features span two unrelated user goals or system concerns → split.
- An epic named after a technical layer (`epic_database_layer`, `epic_api_calls`) → rename to the domain concept the layer serves, or move to `non-functional/`.
- An epic with one feature that mirrors the epic name → the epic is unnecessary; collapse into a standalone feature.

### Standalone features

A `feat_*` folder may sit directly under a grouping folder with no enclosing epic when it shares no domain concept or system concern with any sibling and there is no plausible second feature to add. When a second related feature is later needed, an epic is introduced and both move under it. A grouping folder may host any mix of `epic_*` folders and standalone `feat_*` folders, subject to the parent's declared sub-axis.

## Placement Algorithm

When a new requirement is created or an existing one is restructured, its destination folder is determined by the following deterministic walk.

1. **Identify the top-level category** by reading the new requirement's content against `functional/`, `non-functional/`, and `process/` anchor `README.md` inclusion criteria. Exactly one matches; if none match or more than one match equally, halt and apply governance (SEC-06).
2. **Descend one level** by reading each immediate child folder's anchor file `## Inclusion Criteria` and `## Anti-Scope`. Exactly one child matches the new requirement and is not excluded by its anti-scope. Enter that child.
3. **Recurse step 2** until reaching either an `epic_*` folder whose inclusion criteria match (create a new `feat_*` inside it) or a grouping leaf with no matching epic (create a new standalone `feat_*` or, if appropriate, a new `epic_*` per the demarcation tests).
4. **Halt with no match at any level** is a legitimate outcome. It signals one of three resolutions, each handled by governance (SEC-06): refine the inclusion criteria of an existing folder, introduce a new sub-axis cluster, or introduce a new top-level axis. Ad-hoc placement under a folder whose inclusion criteria does not match the new requirement is disallowed.
5. **At each level the choice is unique.** Two folders matching equally well at the same level is a violation of the single-axis-per-level rule (AC-14) — either the axis declaration is wrong, or one of the inclusion criteria is incorrect, or a new sub-axis is needed.

## Governance: Changing the Taxonomy

The taxonomy itself — what axes exist, what their allowed values are, what each cluster's inclusion criteria and anti-scope say — is governed material. Changes happen only through explicit, recorded paths.

### Three resolution paths for a halted placement

When the placement walk (SEC-05) halts because no folder's inclusion criteria match the new requirement, one of the following resolutions applies. The author surfaces the situation to the user and selects a path; the chosen path is recorded in the commit message that resolves the placement.

- **Path A — Refine inclusion criteria.** An existing folder's `## Inclusion Criteria` is updated so the new requirement now matches. Used when the criteria were under-specified and the new requirement clearly belongs to that cluster's intent.
- **Path B — Introduce a new sub-axis cluster.** A new `epic_*` or grouping folder is added under an existing parent, following the parent's declared sub-axis. The new folder's anchor file declares its inclusion criteria and anti-scope. Used when the new requirement reveals a coherent cluster that did not previously exist within the existing axis.
- **Path C — Amend the sanctioned axes.** The `## Sanctioned Top-Level Axes` section of this requirement is modified to add, retire, or restructure an axis. Used only when the new requirement reveals a structural problem with the axis itself — when no inclusion-criteria refinement could reasonably accommodate it.

### Authorisation

Paths A and B may be authorised within a normal `requ-explore` session. Path C requires explicit user authorisation: a `requ-explore` session that proposes a Path C change halts and surfaces the proposed amendment for user decision before applying any folder changes.

### Cluster kinds and axes are enumerated, not inferred

The set of axes available at each top-level category is enumerated in `## Sanctioned Top-Level Axes`. New axes are not introduced silently through new folders; introducing a folder that would require a new axis is itself a Path C event. This is what prevents the slow drift that arises when multiple axes accumulate at the same level without anyone noticing.

## LLM Judgment Checklist

Before finalizing any new or restructured requirement, the authoring agent answers each question affirmatively. Any uncertainty is surfaced to the user before writing.

**Naming and cohesion**
1. Is the folder name a domain noun or noun-phrase a reader would recognise without seeing the codebase?
2. Name three features (or sibling clusters) expected to live inside this folder. Do they match what is actually there?
3. Read the sibling folders side by side. Do related siblings visually cluster, and do unrelated ones look distinct?

**Anchor files**
4. Does this folder carry the anchor file its shape requires (atomic / epic / grouping)?
5. Does the anchor file's `## Inclusion Criteria` describe what belongs in positive predicates, not as a list of names?
6. Does the anchor's `## Anti-Scope` name the adjacent clusters a misplaced requirement would drift toward (by REQ-ID where applicable)?
7. For grouping folders: does the `## Sub-Axis` declaration name exactly one axis drawn from the sanctioned set?

**Placement walk**
8. Did the placement walk produce a unique destination at every level?
9. If the walk halted, was the resolution recorded as Path A, B, or C — and was the chosen path authorised at the appropriate level?

**Demarcation**
10. For functional epics: do the three functional tests pass?
11. For non-functional and process epics: do the three category-appropriate tests pass?
12. If a same-named epic exists under another grouping, is the shared name still the right scope?

**Hierarchy**
13. Is a sub-grouping folder needed under the parent's declared sub-axis? (≥ 4 sibling clusters share a sub-concept → introduce one.)
14. For a standalone feature: is there truly no sibling feature today that would justify creating an epic?

**Reactive restructuring** (run after location is confirmed, before writing — see SEC-09)
15. Do any `feat_*` siblings in the destination grouping folder share the new requirement's primary domain concept? (→ Case A: propose a new enclosing `epic_*`, Path B under SEC-06)
16. Does the authored or extended `feat_*` requirement have more than 10 acceptance criteria? (→ Case B: propose a feature split and epic promotion, Path B)
17. Is any cross-reference candidate from Phase 1.4 fully subsumed by the new content — all its ACs addressed? (→ Case C: propose marking it `deprecated` with `superseded_by: [new-REQ-ID]` in its frontmatter)

Any "yes" to Q15–17 triggers a user-facing finding before files are written. "No" to all three is the common case and is silent.

## Cross-Reference Completeness Detection

Requirements link to one another through three channels:

- `after:` YAML field — hard dependencies (this requirement assumes the listed ones are already in place).
- `blocks:` YAML field — inverse hard dependencies (this requirement, when introduced, requires the listed ones to be updated).
- `## Related Requirements` body section — semantic relationships short of hard dependency (siblings, shared concepts, sibling enforcement layers).

When a new requirement is authored or an existing one is decomposed into implementation tasks, the set of cross-references it carries must be checked against what *should* be there. Gaps in any of the three channels degrade navigability and lead to siloed decisions. The detection mechanism defined by AC-11 surfaces these gaps deterministically rather than relying on the authoring agent's memory.

**Detection contract.** Given a target requirement, the mechanism produces a list of candidate cross-references: REQ-IDs whose requirements.md contains content that semantically overlaps with the target but whose ID is not already present in the target's `after:` chain, `blocks:` chain, or `## Related Requirements` section.

**Inputs.**
- The target requirement's `requirements.md` file (topic source, plus the three reference channels to exclude from results).
- 2–4 search terms derived from the target's topic: domain nouns (the entities the requirement is about), action verbs (the operations it governs), and component names (skills, scripts, gates it interacts with). The derivation is a one-shot extraction from the requirement's title, overview, and acceptance criteria.
- The search corpus: every `requirements.md` under `requirements_tasks/functional/`, `requirements_tasks/non-functional/`, and `requirements_tasks/process/`.

**Output.** A list of hits, each carrying enough context (REQ-ID, matching file path, matching snippet) for a downstream consumer to classify the relationship. Classification (hard dependency, semantic relationship, or unrelated) is *not* part of detection — it is performed by the invoking caller, either interactively (`requ-explore`) or via a separate gate (`task-derive-from-requ` Phase 1.5).

**Invocation points.**

| Caller | Phase | Purpose |
|---|---|---|
| `requ-explore` | Phase 1.4 — overlap detection during authoring | Reveal semantic overlaps the author may not know about before the requirement is written or extended |
| `task-derive-from-requ` | Phase 1.5 — cross-reference completeness gate before task creation | Block decomposition until missing hard dependencies are recorded and missing semantic relationships are acknowledged (per REQ-PROC-058 AC-17) |

**Implementation latitude.** The mechanism may be realised as a script (preferred per REQ-PROC-058 Developer Guidelines: deterministic-first) or as inline skill instructions executed by the calling agent. Both implementations must satisfy the detection contract above. The choice is made by implementation tasks; this requirement does not prescribe one over the other.

## Reactive Restructuring Analysis

`requ-explore` evaluates structural implications for neighboring requirements whenever a new requirement is created or an existing one is extended. The location approval message (Phase 2.1a) explicitly tells the user that this analysis follows next, so the user does not preemptively reason about restructuring before the AI presents its findings. The analysis itself runs after location is confirmed and before any files are written. When cases are detected, a separate approval gate is presented — the user approves or defers each finding independently before writing proceeds. Three cases are defined.

### Case A — Sibling Bundling

**Trigger**: Two or more `feat_*` folders in the same grouping folder address the same primary domain concept. The "same primary domain concept" means the features operate on the same domain entity or serve the same coherent user goal — the demarcation test from SEC-04 applied to a sibling pair rather than an epic boundary.

**Detection**: After determining the destination grouping folder, the authoring agent reads each sibling `feat_*` folder's `requirements.md` and compares primary domain concepts. LLM judgment; no script-checkable threshold.

**Resolution**: Propose creating an enclosing `epic_*`. Handled as a Path B event under SEC-06 (introduction of a new cluster within an existing axis). Requires user approval before any files are written.

### Case B — Feature Oversize

**Trigger**: A `feat_*` requirement has more than 10 acceptance criteria after authoring or extension.

**Detection**: Count `trackable_items.acceptance_criteria` entries in the requirement's YAML frontmatter. Script-checkable; threshold is 10.

**Resolution**: Propose splitting into multiple `feat_*` folders under a new `epic_*`. Handled as a Path B event under SEC-06. Requires user approval.

### Case C — Obsolescence

**Trigger**: An existing requirement's scope is fully subsumed by the new or extended requirement — every acceptance criterion of the existing requirement is addressed by the new content.

**Detection**: Review cross-reference candidates surfaced during Phase 1.4 (cross-reference gap detection). For each candidate, compare its ACs to the new content. "Fully subsumed" means no AC of the existing requirement extends beyond the new requirement's scope.

**Resolution**: Propose marking the existing requirement `deprecated` with a `superseded_by: [new-REQ-ID]` field added to its frontmatter. This is a lifecycle transition, not a taxonomy change; it does not require a Path C governance event. Requires user approval before applying.

**`superseded_by:` field**: An optional frontmatter field on the deprecating requirement recording which REQ-ID made it obsolete. Distinct from bare `deprecated` (which signals "no longer relevant" for any reason). The `status: deprecated` is the machine-checkable signal; `superseded_by:` carries the traceability.

### Authorization Summary

| Case | SEC-06 Path | User gate |
|---|---|---|
| A — Sibling bundling | Path B | Required |
| B — Feature oversize | Path B | Required |
| C — Obsolescence | Not a taxonomy change | Required |

When no case is detected, execution continues silently.

## Developer Guidelines

> Constraints and invariants the final implementation must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Mechanical first, judgment second.** Every rule that *can* be expressed as a script check *is* expressed as one. Convention rules exist only for properties that cannot be mechanically verified.
- **One axis per level.** The single-axis-per-level rule is hard. Two equally-valid clusterings at the same hierarchy level guarantee overlap — the kind of overlap that makes `workflows/` and `requirements_management/` legitimately both claim release-related requirements. The axis is declared explicitly in the parent folder's anchor file; nothing is implicit.
- **Anchor files are the carrier of placement semantics.** The folder name is a memorable handle. The anchor file is the authoritative statement of what the folder contains and refuses. A reader who reads only the name has insufficient information; a reader who reads the anchor file does not.
- **Depth via grouping, not nesting.** When a grouping has too many siblings, the answer is a sub-grouping folder, never a nested epic.
- **Cross-cutting concerns live in their own bounded bucket.** `cross_artifact_rules/` exists for genuinely cross-cutting requirements. It is not a fallback for placement uncertainty.
- **Validation is blocking, not advisory.** A failure aborts the calling workflow. Silent warnings produce drift over time.
- **Changes to the axis itself are user-gated.** Path C in SEC-06 is not optional process — it is the only way a new top-level axis enters circulation.

### Common Pitfalls

- `epic_*` with a single `feat_*` child of the same name → collapse into a standalone feature.
- `feat_*` containing sub-feature subfolders → promote the feature to an epic.
- Naming an epic after its primary screen (`epic_main_screen`, `epic_dashboard`) → rename to the domain concept the screen represents.
- Adding a grouping subfolder to host a single epic → grouping folders exist to organize multiple siblings; remove the unnecessary level.
- Grouping folder with no anchor file → the folder is invalid; its contents are placed without a recorded reason.
- Two child folders of the same parent matching equally well during the placement walk → the parent's declared sub-axis is wrong, or one child's inclusion criteria is over-broad.
- A requirement placed in `cross_artifact_rules/` because no other folder seemed right → invoke governance (Path A or B), don't absorb.

## Related Requirements

- [REQ-PROC-009](../requirements_and_tasks/requirements.md) — high-level folder structure (categories, requirement_name, tasks/ layout) extended by this requirement with epic / feat semantics, the taxonomy mechanism, anchor files, and machine-checkable invariants.
- [REQ-PROC-035](../release_preparation/requirements.md) — `release-begin-impl` Phase 0 pre-flight that hosts the validation integration point (AC-07).
- [REQ-PROC-003](../requirements_writer_mode_flexibility/requirements.md) — authoring modes that `requ-explore` operates in; AC-08 applies equally in both modes.
- [REQ-PROC-049](../language_coherence/requirements.md) — structural-quality sibling that governs the *language* layer above the structural layer. REQ-PROC-045 ensures requirements have valid epic/feature shape and live in the right folder; REQ-PROC-049 ensures the names, states, and operations they describe stay coherent across requirements, flows, ARB, and code.
- [REQ-PROC-058](../implementation_task_planning/requirements.md) — Implementation Task Planning Quality. AC-17 defines `task-derive-from-requ` Phase 1.5 cross-reference completeness gate that invokes the detection mechanism specified by AC-11 of this requirement. REQ-PROC-058 owns the classification gate (interactive prompt / automated answer.md); REQ-PROC-045 owns the detection mechanism.
- [REQ-PROC-044](../../epic_factory_quality/requirements.md) — Software Factory Quality (the umbrella under which structural quality sits as one dimension).

## References

- `scripts/validate_epic_requirements.py` — validation script that enforces the script-checkable acceptance criteria.
- `requirements_tasks/_meta/id_registry.md` — authoritative ID registry referenced by AC-05.
- `.claude/skills/requ-explore/SKILL.md` — authoring workflow integrated by AC-08.
- `.claude/skills/release-begin-impl/SKILL.md` — release pre-flight integrated by AC-07.
