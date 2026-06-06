# Opus Plan: ux-* Skill Family Cascade Redesign

## Objective

Redesign the ux-persona and ux-scenario skill family so that every create/modify operation on a user needs artifact automatically surfaces the correct downstream actions — including flow review recommendations and a final reminder to re-run `requ-derive-from-flow` (incremental) when flows are updated.

Retire `ux-update` (generic, three-type handler). Replace with `ux-persona` and `ux-scenario` (each handles create + update for one artifact type, with built-in cascade). Address the flow modification gap separately.

---

## Design Decision: Where Does Cascade Detection Live?

**Decision: Each skill performs its own cascade scan at the end of its workflow.**

Rationale:

Session context persists within a conversation — the user's insight is correct. But session context is *conversational*, not *persistent across sessions*. Relying on downstream skills to "inherit context" from a prior skill invocation is fragile: the user might call `ux-scenario` standalone tomorrow, not immediately after `ux-persona`. The cascade scan must work correctly in both cases.

Therefore: **each skill is self-contained**. It performs its own cascade scan regardless of how it was invoked. When skills are chained in sequence, the scans are complementary — `ux-persona` gives a broad flow impact overview, `ux-scenario` narrows to specific flow coverage for the scenario just created. Neither depends on the other being called first.

This also means: the cascade output in `ux-persona` is a recommendation ("run ux-scenario next"), not an invocation. The user controls the chain.

---

## Analysis Summary

### What ux-update contains that must be absorbed

| ux-update capability | Absorbed by |
|---|---|
| Persona modification + impact analysis | `ux-persona` (UPDATE mode) |
| Scenario modification + index maintenance | `ux-scenario` (UPDATE mode) |
| Flow modification (reset review_status, notify scenarios) | **GAP — needs new `ux-flow-update` skill** |
| CHANGE_PROPAGATION.md cascade rules | Both new skills must read this file |
| Bidirectional reference updates | Already in `ux-create-scenario`; carry into new skills |
| Version incrementing strategy | Carry into both new skills |
| scope_exclusions handling | Already in `ux-create-scenario`; carry into both |

### What exists in current skills that must be preserved

- `ux-create-persona`: READMEs list, Opus delegation for persona.md authoring, checklist validation, ID registry regeneration, PCD + VCD derivation
- `ux-create-scenario`: READMEs list, scope exclusion check, category + gold standard designation, SCENARIO_INDEX.md maintenance, bidirectional flow reference update, Opus delegation for scenario.md authoring

### Token budget concern

Each skill is loaded into agent context on every invocation. Current `ux-create-persona` ≈ 105 lines. Adding cascade + UPDATE mode will push toward 200+ lines. Mitigation: compress boilerplate (README tables, repetitive warnings, step preambles) without losing correctness. Target: ≤ 180 lines per skill.

---

## Execution Plan

### One agent handles all four deliverables sequentially.

---

### Step 1: Create `ux-persona` skill

**File**: `.claude/skills/ux-persona/skill.md`

**Description** (frontmatter): `Create or update a persona — with cascade scan for scenario and flow impact`

**Structure**:

#### A. Mode Detection (2 lines)
Check whether a persona folder/file already exists at the target path. If yes: UPDATE mode. If no: CREATE mode. No verbose section needed — inline detection.

#### B. Read Guidelines (parallel)
Same READMEs as current `ux-create-persona`:
`README_3, README_6, README_7, README_10, README_12, README_15, README_17` + `CHANGE_PROPAGATION.md`

Compress the README table to a single-line list. Remove "DO NOT proceed without reading" warning (redundant if it's step 1).

#### C. Gather / Identify
- **CREATE**: gather name, role, archetype, evidence level, data sources (same as current)
- **UPDATE**: accept persona name or PERSONA-ID; resolve to path; read current state (YAML frontmatter, content, review_status, version, evidence markers)

#### D. Generate / Modify persona.md via Opus
- **CREATE**: same as current (Opus delegates, writes file directly)
- **UPDATE**: Sonnet gathers all downstream artifacts first (scenarios under this persona), then delegates to Opus with full context for impact analysis + modification plan + execution. Opus resets review_status to `in_review`, appends review_history entry, increments version.

Version incrementing rules (from ux-update):
| Change type | Version change |
|---|---|
| Typo/grammar | No change (update `updated` date only) |
| Minor additions | +0.1 |
| Section rewrites | +0.1 |
| Structural changes | +1.0 |

#### E. Validate checklist (post-Opus, Sonnet only)
Run Persona Writing Checklist from README_3. Same as current.

#### F. Cascade Scan (NEW — runs after persona is written/validated)

This is the new section. Two sub-checks:

**F1. Scenario necessity check**

Logic:
1. Read persona.md just created/modified — specifically the `role`, traits, and any constraint-indicating fields.
2. Classify persona:
   - **Constraint persona** (accessibility, system, infrastructure): primary purpose is to carry constraints that affect how the app behaves, not to have a personal journey with the app. Key signals: role is `system`, or the persona's core traits are impairment/constraint-focused with no meaningful "as-is" workflow difference.
   - **Regular user persona**: has a journey, goals, emotions, scenarios that differ from other personas.
3. Output based on classification:
   - Constraint persona → state explicitly: "This persona does not require scenarios (as-is behavior is identical to non-impaired users). Proceed directly to flow scan below."
   - Regular persona (CREATE, no scenarios exist) → "Scenarios needed. Next: use `ux-scenario` to create scenarios for this persona."
   - Regular persona (UPDATE, scenarios exist) → scan each existing scenario for fields affected by the modification; flag any that need updating.

**F2. Flow impact scan**

Logic:
1. Read `requirements_user_needs/user_flows/FLOW_INDEX.md`. Extract all flows with `review_status: approved`.
2. Extract the persona's KEY CONSTRAINT KEYWORDS. These come from the persona's traits, impairments, or environmental constraints. Examples:
   - Photosensitive epilepsy → keywords: `animation`, `animated`, `QR`, `transition`, `flash`, `blink`, `fade`
   - Low vision → keywords: `color`, `contrast`, `text size`, `icon`, `chart`, `visualization`
   - Color blindness → keywords: `color-coded`, `heatmap`, `chart`, `graph`, `color indicator`
   - Motor constraint → keywords: `gesture`, `swipe`, `drag`, `button`, `tap`, `touch`
   - Blindness → keywords: `visual`, `display`, `chart`, `graph`, `image`, `animation`
3. For each approved flow: read flow.md (frontmatter + step names + exception names only — NOT full content). Search for constraint keywords.
4. Flag flows where keywords match.
5. Output: list of flagged flows with which constraint creates a concern.

Note: this is a heuristic keyword scan, not semantic analysis. It may produce false positives. The output acknowledges this.

#### G. Output

```
=== PERSONA [CREATED|UPDATED] ===
[artifact path]
ID: PERSONA-XXX
Version: [old →] new
Status: draft | in_review

=== CASCADE ===

Scenarios:
[One of:]
✓ Constraint persona — no scenarios needed. Proceed to flow scan.
⚠ No scenarios exist yet. Next: use ux-scenario for PERSONA-XXX
  Suggested category: [suggest based on persona role and goals]
✓ Scenarios exist. [If UPDATE:] Check these for alignment: [list of affected scenarios]

Flow impact ([N] approved flows scanned):
[If matches found:]
⚠ [N] flow(s) have surfaces this persona's constraints may affect:
  - FLOW-003 (session_start_data_transfer): keywords matched: animated, QR → photosensitivity risk
  - FLOW-001 (xxx): keywords matched: color-coded → color blindness risk
  Next: use ux-update on each flagged flow to review and add constraints
  [Note: keyword scan — verify each match before modifying]
[If no matches:]
✓ No approved flows flagged by constraint keyword scan.

After updating flows:
  → Re-run: requ-derive-from-flow --incremental on each updated flow
```

---

### Step 2: Create `ux-scenario` skill

**File**: `.claude/skills/ux-scenario/skill.md`

**Description** (frontmatter): `Create or update a scenario — with cascade scan for flow coverage`

**Structure**:

#### A. Mode Detection
Check whether scenario.md exists at target path. CREATE vs UPDATE. Inline.

#### B. Read Guidelines (parallel)
Same READMEs as current `ux-create-scenario`:
`README_4, README_6, README_7, README_10, README_12, README_15, README_17, SCENARIO_INDEX.md` + `CHANGE_PROPAGATION.md`

#### C. Validate Parent Persona
Same as current. If persona not approved: warn, ask to proceed.

#### D. Check Scope Exclusions
Same as current (step 1.5 in ux-create-scenario).

#### E. Gather / Identify
- **CREATE**: same as current (name, goal, context, triggers, frequency, environment, evidence level, optional flow links)
- **UPDATE**: identify scenario by name or SCEN-ID; resolve to path; read current state

#### F. Category + Gold Standard (CREATE only)
Same as current.

#### G. Generate / Modify scenario.md via Opus
- **CREATE**: same as current
- **UPDATE**: Sonnet reads all flows referencing this scenario (`implements_flows`), reads persona, then delegates to Opus for impact analysis + modification. Opus resets review_status to `in_review`, appends review_history, increments version.

#### H. Update SCENARIO_INDEX.md
- **CREATE**: same as current (add new instance entry)
- **UPDATE**: update instance fields if category, gold_status, or outcome changed

#### I. Update parent persona's related scenarios (CREATE only)
Same as current.

#### J. Update flow references (bidirectional)
Same as current (if flows provided by user, update `serves_scenarios` in each flow.md — reference-only change, preserve review_status).

#### K. Cascade Scan (NEW)

**K1. Flow coverage check**

Logic:
1. Read all flow.md files in `requirements_user_needs/user_flows/`. Check each flow's `serves_scenarios` array.
2. Check if the scenario just created/modified (by SCEN-ID) appears in any flow's `serves_scenarios`.
3. Two cases:

**Flow exists**: The scenario is already served by at least one flow.
- **CREATE mode**: Reference-only — flag for awareness that a flow already covers this scenario (or will once bidirectional link is added).
- **UPDATE mode**: Check if scenario changes affect flow assumptions. Heuristic: if the scenario's Act 2 (the core struggle) or success criteria changed significantly, the flow likely needs review.
- Output: list flows, note whether content review is recommended.

**No flow serves this scenario**: Scan FLOW_INDEX.md for candidate flows that might logically serve it (by comparing scenario goal/category to flow purpose descriptions). Flag candidates.
- Output: "No flow serves this scenario. Candidates: [list]. Next: use ux-create-flow, OR defer."

#### L. Output

```
=== SCENARIO [CREATED|UPDATED] ===
[artifact path]
ID: SCEN-XXX-XX
Parent: PERSONA-XXX
Category: [category_id]
Gold: [true|false]
Status: draft | in_review

=== CASCADE ===

Flow coverage:
[One of:]
✓ FLOW-003 already serves this scenario.
  [If UPDATE and significant changes:] Content review recommended.
  Next: use ux-update on FLOW-003 to verify alignment with scenario changes.

⚠ No flow currently serves SCEN-XXX-XX.
  Candidate flows that might serve it:
  - FLOW-003 (session_start_data_transfer): overlapping purpose — [reason]
  Next: use ux-create-flow for this scenario, OR defer to flow backlog.

After creating/updating flows:
  → Re-run: requ-derive-from-flow --incremental on the affected flow(s)
```

---

### Step 3: Create `ux-flow-update` skill (gap filler)

**File**: `.claude/skills/ux-flow-update/skill.md`

**Description**: `Modify an existing approved user flow — resets review status and propagates to scenarios`

This is a minimal skill extracted from the flow modification path in `ux-update`. It handles the case not covered by `ux-create-flow` (which handles draft/iterate/approve, not modifying an already-approved flow).

**Structure** (keep minimal — ~80 lines):
1. Read `CHANGE_PROPAGATION.md`, `README_5`, `README_7`, `README_12`
2. Identify flow (by FLOW-ID or path)
3. Read current flow.md + all scenarios in `serves_scenarios`
4. Present modification intent + impact analysis to user
5. Apply changes, reset `review_status: in_review`, append `review_history`, increment version, update FLOW_INDEX.md
6. Ask: "Notify served scenarios for review?" → if yes, set each scenario to `in_review` (do NOT modify content)
7. Output + cascade tail: "After this flow is re-approved: re-run requ-derive-from-flow --incremental"

---

### Step 4: Update skill registry

Using `claude-modify-skill` conventions (sync INDEX.md and factory_flows.md):

**Add**:
- `ux-persona` — Create or update a persona with cascade scan
- `ux-scenario` — Create or update a scenario with cascade scan
- `ux-flow-update` — Modify an approved user flow

**Retire** (delete skill folders):
- `ux-create-persona` — replaced by `ux-persona`
- `ux-create-scenario` — replaced by `ux-scenario`
- `ux-update` — retired; capabilities split into ux-persona, ux-scenario, ux-flow-update

**Keep unchanged**:
- `ux-create-flow`, `ux-flow-draft`, `ux-flow-approve`, `ux-flow-complete`, `ux-validate-rule`, `vcd-log-tradeoff`

---

## Token Efficiency Targets

Apply these compressions in all three new skills:

| Current pattern | Compressed form |
|---|---|
| Full README table with Content column | Single-line list: `Read (parallel): README_3, README_6, README_7 ...` |
| "DO NOT proceed without reading them first" | Remove (redundant) |
| "This and all following steps must not be performed by the claude-switch-opus skill. The skill must terminate..." | `(Sonnet only — Opus terminates before this step)` |
| Full bash commands for path resolution | Replace with `(find persona.md via Glob or Bash)` |
| Hardcoded Windows paths in ux-create-scenario | Remove entirely (bug — wrong OS) |
| Verbose gold standard explanation | Keep only the designation question; move explanation to inline parenthetical |

---

## Quality Criteria

- [ ] `ux-persona` handles both CREATE and UPDATE correctly
- [ ] `ux-scenario` handles both CREATE and UPDATE correctly
- [ ] Cascade scan in `ux-persona` correctly classifies constraint personas (no scenarios needed) vs regular personas
- [ ] Cascade scan flow keyword matching covers: animation/QR (photosensitivity), color/contrast (low vision/color blindness), gesture/tap (motor), visual/chart (blindness)
- [ ] Cascade output is always actionable: specific skill name + specific artifact, never vague
- [ ] `ux-flow-update` preserves all capabilities from ux-update's flow path
- [ ] All three new skills read `CHANGE_PROPAGATION.md` (currently missing from create skills)
- [ ] Hardcoded Windows paths removed from ux-create-scenario (bug fix)
- [ ] Each new skill ≤ 180 lines
- [ ] `ux-update`, `ux-create-persona`, `ux-create-scenario` retired and removed from INDEX.md

---

## Risks

**Risk 1**: Cascade flow scan produces too many false positives (every flow mentions "button" → every flow flagged for motor constraint personas).
Mitigation: Use more specific keywords per constraint type. For motor: prefer `gesture`, `swipe`, `drag` over `button` (buttons are universal). Output notes: "keyword scan — verify before modifying."

**Risk 2**: UPDATE mode for persona/scenario is harder to get right than CREATE — risk of regression in existing functionality.
Mitigation: Carry ux-update's OPUS MODE structure (Sonnet gathers all downstream artifacts, Opus plans, Sonnet executes). Do not simplify the UPDATE path to Sonnet-only.

**Risk 3**: `ux-flow-update` overlaps with `ux-create-flow` "iterate" mode — confusion about which to use.
Mitigation: Clear description distinction. `ux-create-flow` = new flows + iterating drafts. `ux-flow-update` = modifying approved flows (content changes that require re-approval).

**Risk 4**: Retiring `ux-update` before new skills are verified could break existing workflows.
Mitigation: Create new skills first, verify they work, THEN retire old ones. Do not delete until at least one successful invocation of each new skill is confirmed.

---

## Execution

**One implementation agent** handles all four steps sequentially (Steps 1–4 above).

Dependencies:
- Step 1 and Step 2 are independent — can be written in parallel if agent uses parallel Write calls, but sequential is fine given context window
- Step 3 depends on nothing (standalone skill)
- Step 4 (registry update) must happen after Steps 1–3 are complete

Agent instructions:
1. Read this plan fully before starting
2. Read `CHANGE_PROPAGATION.md` from `requirements_user_needs/` before writing any skill content
3. Read `requirements_user_needs/user_flows/FLOW_INDEX.md` to understand flow structure before writing cascade scan logic
4. Use `claude-modify-skill` skill conventions for all skill file creation/deletion
5. After completing all four steps, run a self-check against the Quality Criteria above

---

# Part 2: Cascade Documentation and Multi-Pass Task Model

## Objective

Define how cascade findings are documented persistently across sessions, how non-existent artifacts are tracked, and how the task execution model supports multi-pass cascade work through the user needs hierarchy.

---

## Decision 1: Canonical Location for "Pending Artifact Creation"

**Two-layer approach.**

### Layer 1 — Task-local (primary working memory)

The full cascade state lives in `plans_and_protocols/cascade_log.md` within the active task folder. This is where all findings, pending work, and pass completions are recorded. It is the authoritative source of truth for the cascade state.

### Layer 2 — Globally discoverable signal (for non-existent artifacts)

For artifacts that do not yet exist (e.g., "create a scenario for persona X"), write a `review_history` entry to the **parent artifact** (the one that already exists):

```yaml
# In persona.md review_history:
- seq: N
  date: 2026-03-30
  from: approved
  to: in_review
  reviewer: LLM
  notes: "Scenario creation pending: [scenario description — what it should cover and why]. Cascade context: task [TASK-ID], cascade_log.md pass 1."
```

**Why this location:**
- `review_history` is already the "state change" mechanism — setting a persona to `in_review` with a note is the existing signal that work is needed
- Any session reading the persona will immediately see the in_review status and the note
- No new file types or fields are introduced
- Does not pollute persona content — review_history is metadata, not persona body
- Cleanup is automatic: when the scenario is created and the persona is re-approved, the review_history entry is the record of what happened (not deleted — it's an audit trail)

**For existing artifacts that need updating** (e.g., FLOW-003 needs a photosensitivity constraint):
- Set `review_status: in_review` with a specific `review_history` note on the flow itself
- FLOW_INDEX.md will show the flow as in_review — discoverable without knowing the task

**Rejected options:**
- `pending_scenarios` YAML field in persona.md: pollutes persona content structure, requires cleanup
- SCENARIO_INDEX.md "needed" list: mixes process metadata into a content registry
- `requirements_user_needs/_meta/pending_cascade.md`: new maintenance burden, ambiguous ownership

---

## Decision 2: Cascade Log Format

**Dedicated `cascade_log.md` per task** — not appended to protocol.md.

Protocol.md is for implementation tracking (what was done step by step). The cascade log tracks propagation state across multiple passes — a different concern. Keeping them separate makes the cascade state unambiguous to find and update.

### cascade_log.md Template

```markdown
# Cascade Log: [TASK-ID]

**Origin**: [What was created/modified that started this cascade — e.g., "Created PERSONA-020 (photosensitive epilepsy)"]
**Started**: [YYYY-MM-DD]
**Hierarchy**: Persona → Scenario → User Flow → Requirements
**Status**: pass-1-complete  # update each pass: pending | pass-N-complete | done

---

## Pass 1 — [YYYY-MM-DD] — Persona Level

### Completed
- Created: [list artifact IDs and paths]
- Modified: [list artifact IDs and paths]
- Set to in_review: [list artifact IDs with reason]

### Pending → Pass 2 (Scenario Level)

| Action | Target | Reason | Priority |
|--------|--------|--------|----------|
| create | Scenario for PERSONA-020 (photosensitivity) | Constraint persona — no scenario needed | skip |
| create | Scenario for PERSONA-021 (low vision) | Regular persona — needs scenario in category [X] | high |
| update | SCEN-002-03 (transfer scenario for Jana) | May need photosensitivity context in Act 2 | medium |

### Artifacts Flagged (review_history written)
- PERSONA-020: in_review — "Scenario creation pending: [note]"
- FLOW-003: in_review — "Photosensitivity constraint review needed: [note]"

---

## Pass 2 — [YYYY-MM-DD] — Scenario Level

### Completed
[same structure]

### Pending → Pass 3 (Flow Level)

| Action | Target | Reason | Priority |
|--------|--------|--------|----------|
| update | FLOW-003 | Photosensitivity constraint from PERSONA-020 | high |
| update | FLOW-001 | Low vision constraint from PERSONA-021 | medium |

### Artifacts Flagged
[list]

---

## Pass 3 — [YYYY-MM-DD] — Flow Level

### Completed
[same structure]

### Pending → Pass 4 (Requirements Level)
- Run requ-derive-from-flow --incremental on: FLOW-003, FLOW-001
- Cluster or solo mode: [specify]

---

## Pass 4 — [YYYY-MM-DD] — Requirements Level (TASK COMPLETE)

### Completed
- requ-derive-from-flow run on: [flows]
- Requirement-update goal.md files created: [list paths]

**Task status: DONE — transition task goal.md to completed**
```

**Rules:**
- Status in the header is always the current state — update it at the start of each pass
- Each pass section is append-only — do not edit previous pass sections
- The Pending table is the PRIMARY handoff to the next pass — it must be complete and specific
- "skip" in Priority means the cascade analysis determined no action is needed; document the reason so future sessions don't re-analyze

---

## Decision 3: Multi-Pass Task Model

### Pass definitions

| Pass | Level | Scope | Exit condition |
|------|-------|-------|----------------|
| 1 | Persona | Create/modify personas that are the cascade source | All target personas done + cascade_log Pass 1 written + parent artifacts set to in_review + user approval |
| 2 | Scenario | Create/modify scenarios from Pass 1 pending table | All scenario work done + cascade_log Pass 2 written + flows flagged + user approval |
| 3 | Flow | Update flows from Pass 2 pending table | All flow work done + cascade_log Pass 3 written + flows in_review + user approval |
| 4 | Requirements | Run requ-derive-from-flow --incremental | goal.md files created for each requirement gap → **TASK COMPLETE** |

### Resume protocol

When an agent opens this task in a new session:
1. Read `goal.md` — understand the overall objective and cascade structure
2. Read `plans_and_protocols/cascade_log.md` — find the **Status** field in the header
3. Status `pending` → start Pass 1
4. Status `pass-N-complete` → read the last Pass N Pending table → execute Pass N+1
5. Status `done` → task is complete, nothing to do

### Completion criterion

The task is complete after Pass 4: `requ-derive-from-flow` has run in incremental mode on all flows changed in Pass 3, and the resulting requirement-update goal.md files have been created. The task goal.md is then marked completed via `task-complete` skill.

**The task does NOT cover executing the requirement-update tasks** — those are separate tasks created by requ-derive-from-flow and executed independently.

---

## Decision 4: task-create Skill Modification

### When to generate multi-pass goal.md

task-create should detect a "user needs cascade task" when ANY of these are true:
1. The task description contains keywords: "persona", "scenario", "user needs", "accessibility", "cascade", "propagate"
2. The task type is `impl` and the parent requirement is REQ-PROC-027 (User Needs Content Creation) or related user needs process requirements
3. The user explicitly describes work that spans multiple artifact types (personas + scenarios, or scenarios + flows)

When detected, task-create asks: "This looks like a user needs cascade task. Should I structure it as a multi-pass task (persona → scenario → flow → requirements)? (y/n)"

### Multi-pass goal.md additions

Add two new sections to the standard goal.md template for multi-pass tasks:

**New YAML fields** (after `scope_description`):
```yaml
cascade_type: user_needs  # signals multi-pass structure
cascade_status: pass-1-pending  # updated by executing agent each pass
```

**New goal.md section** (after Scope, before Acceptance Criteria):

```markdown
## Cascade Passes

This task propagates changes through the user needs hierarchy across multiple sessions.
**Read `plans_and_protocols/cascade_log.md` before starting any pass.**

| Pass | Level | Skill | Status |
|------|-------|-------|--------|
| 1 | Persona | ux-persona | pending |
| 2 | Scenario | ux-scenario | pending |
| 3 | Flow | ux-flow-update / ux-create-flow | pending |
| 4 | Requirements | requ-derive-from-flow --incremental | pending |

**Resuming**: Check cascade_log.md status field → execute the next incomplete pass.
**Completing**: Task is done after Pass 4 (requirement-update goal.md files created).
```

The Acceptance Criteria section should include one criterion per pass:
```markdown
- [ ] Pass 1: Personas created/modified, cascade_log.md Pass 1 written
- [ ] Pass 2: Scenarios addressed (created, updated, or explicitly skipped), cascade_log.md Pass 2 written
- [ ] Pass 3: Flows updated, cascade_log.md Pass 3 written
- [ ] Pass 4: requ-derive-from-flow run, requirement-update goal.md files created → DONE
```

---

## Decision 5: ux-Skill Output Integration

### Core principle: skills are task-agnostic

The ux-persona and ux-scenario skills do NOT write to cascade_log.md directly — they do not know which task they are running under. They produce structured cascade output. The **orchestrating session** (the agent executing the multi-pass task) writes that output to cascade_log.md.

### What the skills DO write directly

Skills write to artifacts they already have access to:

1. **Flagged existing artifacts**: Skills set `review_status: in_review` and append a `review_history` entry on each flagged artifact. (They know the artifact paths — they read them during the cascade scan.)

2. **Non-existent artifact signals**: Skills write a `review_history` entry to the parent artifact (e.g., persona.md) noting "Scenario creation pending: [description]. Tracked in task cascade_log.md." The task ID is not known to the skill — so the note references "the active task's cascade_log.md" without a specific path. This is sufficient: the session has the task context.

### What the orchestrating session does

After the skill completes and outputs its CASCADE section, the orchestrating session:
1. Takes the structured CASCADE output
2. Writes it to `plans_and_protocols/cascade_log.md` as the current pass entry
3. Updates the `cascade_status` field in goal.md YAML

The skill's CASCADE output format (from Plan Part 1) is already structured as a table — it maps directly to the cascade_log.md Pending table format. The orchestrating session reformats and writes it.

### Standalone invocations (no task context)

When a user runs `ux-persona` directly (not under a multi-pass task):
- The skill still outputs the CASCADE section to the terminal
- The skill still writes review_history entries to flagged artifacts
- There is no cascade_log.md to write to — this is fine
- The user sees the cascade output and can act on it manually

The cascade_log.md is only created when running under a multi-pass task. Its absence does not break standalone invocations.

### Implementation note for ux-skill authors

In the ux-persona and ux-scenario skill files, the CASCADE output section should end with:

```
If running under a multi-pass task:
  → Orchestrating session: write the above findings to plans_and_protocols/cascade_log.md
  → Update cascade_status in goal.md to pass-N-complete
```

This instruction lives in the skill output, visible to the orchestrating agent, not embedded in skill logic (keeping skills task-agnostic).

---

## Execution for Part 2

**Same implementation agent as Part 1** — handle after completing the skill files.

Additional steps (append to the Part 1 agent's work):

**Step 5: Update task-create skill**
- Read current `task-create/skill.md`
- Add cascade task detection logic (keyword check + question to user)
- Add multi-pass goal.md template additions (new YAML fields + Cascade Passes section)
- Add cascade_log.md initialization step: when multi-pass mode confirmed, create an empty `plans_and_protocols/cascade_log.md` with the template header

**Step 6: Update CHANGE_PROPAGATION.md**
- Add a section: "Automated Cascade via Skills" documenting the two-layer approach (cascade_log.md + review_history signal)
- Add the cascade_log.md template as a reference
- Update status from "Draft" to "Active"

**Step 7: Initialize cascade_log.md for this task**
- Create `plans_and_protocols/cascade_log.md` for TASK-PROC-027-36 (the accessibility personas task currently in progress)
- Status: `pending` (Pass 1 not yet started)
- This task is itself a multi-pass cascade task

---

## Quality Criteria (Part 2)

- [ ] cascade_log.md template is concrete enough that an agent can fill it without ambiguity
- [ ] Resume protocol is unambiguous: reading cascade_log.md status → knowing exactly what to do next
- [ ] Non-existent artifact problem is solved: review_history entry on parent artifact is sufficient signal
- [ ] task-create skill generates multi-pass goal.md when cascade task is detected
- [ ] ux-persona and ux-scenario skill output ends with the orchestrating session write instruction
- [ ] Skills remain task-agnostic (no hardcoded task paths in skill files)
- [ ] CHANGE_PROPAGATION.md updated to reflect the new automated cascade process
- [ ] TASK-PROC-027-36 (this task) gets its own cascade_log.md initialized
