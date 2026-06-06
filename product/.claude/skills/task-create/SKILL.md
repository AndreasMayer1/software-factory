---
name: task-create
description: Initialize task workspace in requirements_tasks/. THIS SKILL MUST BE USED TO CREATE TASKS.
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You are a task workspace initializer.

## Operating Modes

**Standalone mode** (default, no plan entry provided): Full workflow with interactive coverage-asking and user confirmation. Redirect logic applies (see §3c below).

**Plan-driven mode** (activated when a plan entry is passed as input): Called by `task-derive-from-requ` Phase 5 or `release-begin-impl` Phase 2c. Skips: step 3b coverage-asking, step 3.4 package prompting, step 4 user location-confirmation. Uses plan values directly for goal.md frontmatter.

### Plan entry format (YAML, inline or file path)

```yaml
task_name: "descriptive name"
req_path: "path/to/requirements.md"
requirements_version: "abc1234"
covers_acs: [AC-01, AC-02]
effort: M
layer: domain
after: []
task_type: impl
implementation_notes: "context for implementer"
opus_recommended: false
target_package: "PKG-X"
```

Pass as: inline YAML block in the skill argument, OR a file path to a YAML file, OR via env var `TASK_CREATE_PLAN_ENTRY=<path>`. Presence of a plan entry activates plan-driven mode automatically.

## Core Responsibility
Your PRIMARY goal is to ensure requirements are placed in the **correct location** within the `requirements_tasks/` folder structure AND to generate proper task metadata including unique task IDs and coverage tracking. Organization is critical - take time to investigate and reason about the right place.

## The Three Main Categories
Every requirement MUST be in one of these three categories:

| Category | Purpose | Key Question |
|----------|---------|--------------|
| `functional/` | Features from end-user's perspective | WHAT should the app do? |
| `non-functional/` | Technical/quality requirements spanning multiple features | HOW should the app be built? |
| `process/` | Development process, workflow, AI behavior definitions | HOW do we work? |

## Decision Tree for Classification
Use this to determine the correct category:

### Q1: Does it describe a feature that a user (client/therapist) can directly see or use?
- **YES** → `functional/` (then determine: client, therapist, or shared)
- **NO** → Go to Q2

### Q2: Does it describe technical specs, quality requirements (performance, security), or design system rules for many features?
- **YES** → `non-functional/` (then determine: architecture, ui_ux_design_system, etc.)
- **NO** → Go to Q3

### Q3: Does it describe HOW we work, document, communicate, or how the AI should behave?
- **YES** → `process/`
- **NO** → The requirement is unclear. Ask user to clarify.

## Workflow

### 1. Understand the Requirement (if not provided)
Ask the user:
- What is the high-level objective?
- Is this a new feature, technical guideline, or process definition?

### 2. Classify Using Decision Tree
**MANDATORY**: Work through the decision tree questions with the user or by analyzing the requirement description.

### 3. Investigate Existing Structure
**CRITICAL**: Before suggesting a location, investigate what already exists:

a) List the subcategories in the target category:
   - For `functional/`: Check roles (client, therapist, shared) and epics
   - For `non-functional/`: Check themes (architecture, ui_ux_design_system, etc.)
   - For `process/`: Check subtypes (ai_rules, documentation_rules, etc.)

b) Read relevant existing requirements to understand:
   - How similar requirements are organized
   - What naming conventions are used
   - Whether this requirement fits into an existing group

c) Look for related requirements:
   - Search for keywords in requirement names
   - Check if there's a broader category this belongs to
   - Identify if this should be grouped with existing items

### 3b. Requirements Coverage Check (MANDATORY)

**Before creating any task**, verify that `requirements.md` (single source of truth) covers the task scope.

#### Case A: No parent requirements.md exists yet (NEW requirement needed)

**If task type is `explore`** (the task's purpose IS to create the requirement):

Do NOT block. Instead, pre-allocate a requirement ID so the task has a valid `parent_requirement` and a correct task ID derived from it:

1. Determine the parent container (one directory level above the proposed requirement path).
2. Read the parent container's `requirements.md` to get its `id:` (e.g. `REQ-FUNC-007`).
   - If no `requirements.md` exists in the parent container (new top-level epic): use the category prefix as `--parent-id` (`REQ-FUNC`, `REQ-NFUNC`, `REQ-PROC`).
3. Allocate a requirement ID atomically:
   ```bash
   python3 scripts/requirements/allocate_req_id.py \
     --parent-id [PARENT-REQ-ID] \
     --parent-path [path-to-parent-container]
   ```
   This reserves the next free REQ-ID (e.g. `REQ-FUNC-007-06`) and creates a `.reserve-REQ-FUNC-007-06` marker in the parent directory.
4. Use the returned ID as `parent_requirement` in goal.md.
5. Continue to Task ID Generation (step 3) using this reserved REQ-ID — `allocate_task_id.py` will allocate `TASK-FUNC-007-06-01`.
   - Tasks on epic-level requirements are valid (e.g. explore/define tasks): `TASK-FUNC-007-01`, `TASK-FUNC-007-02`, ...
6. Leave `requirements_version`, `covers` empty in goal.md — no requirements.md exists yet.

**If task type is NOT `explore`** (impl, bugfix, define, etc.):

**STOP. Do NOT write requirements.md manually.**

Invoke the `requ-explore` skill first:
```
Use requ-explore skill to define [requirement name] at [proposed path]
```
Wait for `requ-explore` to complete and the `requirements.md` to exist. Only then continue with task creation.

#### Case B: Parent requirements.md exists

1. **Read parent requirements.md** — check acceptance criteria, sections, and scope
2. **Assess coverage**: Does every aspect of this task map to existing ACs or sections?
3. **If gaps found** (task adds or changes requirements):
   - Show the user what is missing or would change
   - Update `requirements.md` to reflect the correct current state first
   - **Never add history or log entries** — current state only (git handles history)
   - Re-read to confirm `requirements.md` now fully covers the task
4. **If fully covered** → proceed to step 4

**Why**: Tasks must be grounded in requirements. If reality diverges, fix requirements first — not the task.

### 3c. Redirect Logic (AC-10) — Standalone Mode Only

**Skip entirely if ANY of these apply**:
- Plan-driven mode is active (plan entry provided)
- Task type is `bugfix`, `explore`, `define`, `analyze`, or `review`

**Trigger** (all three must be true):
1. Standalone mode
2. Task type is `impl` or `verify`
3. Parent requirement has `trackable_items.acceptance_criteria` AND ≥ 1 AC has zero task coverage

**Check uncovered ACs** — compare `trackable_items.acceptance_criteria` IDs against `covers.acceptance_criteria` fields of all tasks whose `parent_requirement` matches:
```bash
python3 scripts/requirements/coverage_report.py 2>/dev/null | grep -A 20 "REQ-XXX"
```

**Redirect action**: Stop task creation. Print:
```
This requirement has N uncovered ACs: [AC-XX, AC-YY, ...].
Routing to task-derive-from-requ for holistic decomposition.
```
Then invoke `task-derive-from-requ` skill with the requirement path.

**Override**: If the user explicitly passes `--standalone-override` as an argument, skip the redirect and continue. In automated mode (`CLAUDE_AUTOMATED_MODE=1`): never auto-override — always redirect. Log the override in the goal.md Notes section when used.

### 3d. Existing Task Overlap Check (MANDATORY — Standalone Mode)

**Skip if**: plan-driven mode is active OR task type is `bugfix`.

Before proposing a location, check for existing tasks with similar scope to avoid duplicates. Run both sub-checks; surface any hits together.

#### Sub-check 1 — Same-requirement task scan (structural, highest signal)

List every existing task folder under the **same requirement** as the proposed new task:
```bash
ls requirements_tasks/[category]/[requirement]/tasks/ 2>/dev/null
```
For each existing task folder, read its `goal.md`:
- The task title (`# Goal:` line)
- `status:` and `type:` from YAML frontmatter
- First 5 lines of `## Objective`

This is the most likely place for duplicates — always run it, no keyword derivation needed.

#### Sub-check 2 — Broader keyword grep (semantic, cross-requirement)

Derive 2–4 search terms from the task name and description. Use key domain nouns and concepts; avoid generic words (`task`, `impl`, `explore`, `define`, `fix`, `update`).

Search across the requirements tree:
```bash
grep -rl "term1\|term2\|term3" requirements_tasks/ --include="goal.md" 2>/dev/null | head -20
```
Exclude hits already found in Sub-check 1. For each new match, read title, `status:`, and the first 5 lines of `## Objective`.

#### Classification and output

Classify every hit from both sub-checks:
- **Duplicate**: same goal, same deliverable → stop; tell user
- **Overlap**: same domain but narrower or complementary scope → note relationship
- **False positive**: unrelated content that shared a keyword → discard

**No hits from either sub-check**: continue to Step 4 silently.

**Hits found**: present a short list (path, status, one-line objective). Ask:
> "Found potentially overlapping tasks — [list]. Is this new task a duplicate, an extension, or genuinely independent?"
- **Duplicate** → abort; point the user to the existing task.
- **Extension** → continue; add to `related_tasks_refs`: `{path_to_goal_md, reason: "scope boundary — covers [X]; this task covers [Y]"}`. No `## Notes` entry needed — `## Related Tasks` in goal.md captures this.
- **Independent** → continue normally.

### 4. Reason and Propose Location
Based on your investigation:
- Explain your reasoning (which category and why)
- Show the proposed full path
- Explain how it relates to existing requirements
- **ASK USER TO CONFIRM** before proceeding

**Plan-driven mode**: Skip user confirmation. The plan's `req_path` determines the requirement location; the task folder is derived from it. Log: "Location auto-accepted (plan-driven mode): [proposed path]".

Example:
```
Based on the decision tree, this is a non-functional requirement because it describes
a UI/UX design system rule that applies to many features.

I found existing UI/UX design system requirements at:
- requirements_tasks/non-functional/ui_ux_design_system/responsive_layout_master_detail/
- requirements_tasks/non-functional/ui_ux_design_system/reusable_evaluation_view/

Proposed location:
requirements_tasks/non-functional/ui_ux_design_system/ui_navigation_layers/

This groups it with other UI/UX design patterns. Does this look correct?
```

### 5. Create Task Workspace
Once location is confirmed:
a) Create directory structure:
   - `requirements_tasks/[category]/[subcategory]/[requirement]/tasks/[YYYY-MM-DD]_[mode]_[name]/`
   - `plans_and_protocols/` subfolder

b) Task naming modes:
   - `impl_` - Implementation tasks (writing code)
   - `explore_` - Exploration/research tasks (gathering info, understanding)
   - `define_` - Definition tasks (breaking down epics into features)
   - `review_` - Review tasks
   - `analyze_` - Analysis tasks

   The `[name]` slug is concise kebab-case (verb-first where natural). Canonical
   epic/feature/task naming rules live in `requ-explore` → "Naming Conventions"
   (do not duplicate them here).

b.5) Run propose_after.py to detect dependencies (after directory created, before writing goal.md):
   ```bash
   python3 scripts/tasks/propose_after.py \
     --path "[new task folder path]" \
     --metadata '{"type":"[task type]","parent_requirement":"[REQ-ID]"}'
   ```
   The script outputs one `TASK-ID   reason` line per proposal (exits 0 always).
   - **No output**: skip silently; use `after: []`.
   - **Script fails**: warn ("Dependency proposal failed, continuing without proposals."); use `after: []`.
   - **Has proposals**:
     - **Interactive mode**: Present to user: "Proposed `after:` entries:\n  TASK-XXX — reason\nAccept / drop any / add others?" Write confirmed list to `after:` in goal.md. For each confirmed entry, add to `related_tasks_refs`: `{path_to_goal_md, reason: "predecessor — executor should read what was delivered"}`.
     - **Automated mode** (`CLAUDE_AUTOMATED_MODE=1`): auto-accept proposals whose reason contains "same-package"; skip all others silently. Add auto-accepted entries to `related_tasks_refs`.

c) Create `goal.md`:
   - Capture current git commit hash of requirements.md: `git log -1 --format=%h -- [path/to/requirements.md]`
   - **If type is `explore`**: use the Explore Goal Template (see below). Ask:
     1. "What problem space should this exploration enter? What is not yet known?"
     2. "What are 2–5 seeds — entry points or tensions where exploration might begin? These can be rough; the exploration will discover more."
     Then save the user's raw input verbatim (typos and all) to `plans_and_protocols/[YYYY-MM-DD]_00_user_initial_input.md` and reference it from the Background section of goal.md with the framing: "Read it as a seed bed, not a spec."
     Do NOT ask for In Scope / Out of Scope. Do NOT generate a detailed AC checklist — use the four standard explore ACs from the template. Leave `release_description` blank. The Execution Model section of the template includes web research guidance (delegate to general-purpose agent; never run WebSearch inline).
   - **All other types**: Ask user for goal content if not provided; use the Standard Goal Template (see below).
   - **If type is `impl`**: draft a `release_description` suggestion (max 25 words, English, user-benefit perspective) based on the requirement/goal content, then ask user to confirm or adjust. Example: "Allows users to track mood trends over time." Leave blank if user skips.
   - **If type is `bugfix`**: collect bug report info and add a Bug Report section to goal.md (see Bugfix Task Handling below).
   - **Declare the sizing signals**: set `expected_tool_calls` and/or `skill_chain_depth` (at least one — AC-01); add `synthesis_dependent: true` + a one-line `synthesis_justification` when the session must hold multiple input domains at once (AC-02), else omit both.
   - **Set `opus_recommended`** (see Opus Recommendation Check below).
   - **Apply the Sizing Gate** (see Sizing Gate below) before writing goal.md.

d) Check for previous tasks in this requirement - if exists, ask if user wants to copy context (rollover)

d.5) Emit `## Related Tasks` section in goal.md if `related_tasks_refs` is non-empty. One table row per entry: relative path to goal.md and one-sentence reason. Place after `## Dependencies`. Omit the section entirely when the list is empty.

e) Output: "Workspace ready at [path]. Read goal.md to understand the task."

### Bugfix Task Handling

**When task type is `bugfix`**:

**Title format** (mandatory): `"Ensure that AC [XY] of [requirement name] works correctly"`
- Example: `"Ensure that AC-03 of REQ-FUNC-007 works correctly"`
- If multiple ACs are affected: `"Ensure that AC-02 and AC-04 of REQ-FUNC-007 work correctly"`

**Collect bug report** from user with these fields:

```
Bug Report

Steps to reproduce:
1. [first step]
2. [second step]
...

Expected behavior:
[What should happen]

Actual behavior:
[What actually happens — be specific: error message, wrong value, crash, etc.]

Environment (optional):
[Device / OS version / app version]

Logs (optional):
[Relevant log output, stack traces, error messages]
```

**Add to goal.md** as a dedicated `## Bug Report` section (after Objective, before Scope).

**Do NOT prompt for `release_description`** on bugfix tasks — leave blank.

### Priority Determination (SEC-LIFECYCLE Reference)

**MANDATORY**: Before setting urgency/impact values in goal.md, read the parent requirement's `requirements.md` to check for existing priority values.

**Priority Inheritance Rule**:
1. Read parent requirement's YAML frontmatter for `urgency`, `urgency_reason`, `impact`, `impact_reason`
2. **Default**: Inherit these values directly into the task
3. **Override**: Only if task has genuinely different urgency (e.g., blocking other work), document the reason

**If parent requirement has no priority** (pre-migration):
- Refer to the priority decision trees in `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md` (SEC-13: Meta Information Lifecycle)
- Ask user the guiding questions:
  - Urgency: "Why must this happen NOW? What happens if we wait?"
  - Impact: "What value does this create for users or development?"

**Effort Estimation** (tasks max out at `XL` — `XXL` is for epic requirements only):
| Size | Typical Scope |
|------|---------------|
| `XS` | < 1 hour: Fix typo, simple config |
| `S` | 1-4 hours: Add simple function |
| `M` | 1-2 days: New component |
| `L` | 3-5 days: Multi-file feature |
| `XL` | > 1 week: Architectural change |

### Opus Recommendation Check

After determining type and scope, decide whether to escalate the model. **Splitting is always the preferred response to high volume or broad scope** (REQ-PROC-001 §"Signals recap"); model escalation is reserved for *irreducible reasoning complexity*. Set `opus_recommended: true` (and log the reason) only if **any** of these apply:

| Criterion | When it applies |
|---|---|
| **Synthesis that cannot be split** | Multiple domains must be held simultaneously AND splitting would lose the synthesis value (architectural trade-off across layers; design decision needing all context at once). |
| **Cross-cutting invariant** | Task edits ≥3 files and every file must be changed with awareness of all others at once (API rename, layer-boundary change, shared-constraint enforcement). |
| **Architectural judgment** | Touches a domain boundary, dependency-injection wiring, or a layer-purity rule in `doc/architecture/`. |
| **Explicit decision task** | Type is `define`, or goal text contains "evaluate options", "decide approach", "architectural decision", "trade-off", "compare approaches". |
| **Security / privacy / compliance domain** | Subtle reasoning errors have large consequences. |
| **Prior model failure** | A previous attempt drove the `verify-quality` cycle counter to ≥3 — escalate on the retry rather than exhausting the remaining budget. |

**Default**: `opus_recommended: false`. If the task is large but not complex — **split it instead**.

**After evaluating**, write a brief comment next to the field:
```yaml
opus_recommended: true   # reason: cross-cutting invariant — API rename across 4 files
```
or leave the comment blank for `false`.

### Sizing Gate (REQ-PROC-001 AC-03)

After `opus_recommended` is set, apply the creation-time sizing gate to the new `goal.md`. The gate acts on the S1 signals declared in frontmatter (see REQ-PROC-001 §"Signals recap" for S1–S4):

**Trigger**: `expected_tool_calls > 60` OR `skill_chain_depth >= 4`.

**When triggered**, the task MUST satisfy at least one of these end states — else the gate fails:
1. `opus_recommended: true`, or
2. the task has been split into child tasks (declared in goal.md / `after:` chain), or
3. `goal.md` body contains a **named fan-out plan** describing which agents are spawned, what each distills, and what it returns.

**On failure**:
- **Interactive mode**: warn the user, show the three end states, and ask which to apply before writing goal.md.
- **Automated mode** (`CLAUDE_AUTOMATED_MODE=1`): block — do not write the high-volume goal.md as-is. Either split into child tasks or add the named fan-out plan to the goal.md body. Prefer splitting.

### Cascade Task Detection

**After Step 2 (classification) and before proposing a location**, check if this is a user needs cascade task.

**Trigger conditions** (any one sufficient):
1. Task description contains keywords: `persona`, `scenario`, `user needs`, `accessibility`, `cascade`, `propagate`
2. Type is `impl` and parent requirement is REQ-PROC-027 or related user needs process requirement
3. User describes work spanning multiple artifact types (personas + scenarios, or scenarios + flows)

**When detected**, ask:
> "This looks like a user needs cascade task. Should I structure it as a multi-pass task (persona → scenario → flow → requirements)? (y/n)"

**If user confirms (multi-pass mode)**:

Add to the YAML frontmatter (after `scope_description`):
```yaml
cascade_type: user_needs
cascade_status: pass-1-pending
```

Add a "## Cascade Passes" section to goal.md (after Scope, before Acceptance Criteria):
```markdown
## Cascade Passes

This task propagates changes through the user needs hierarchy across multiple sessions.
**Read `plans_and_protocols/cascade_log.md` before starting any pass.**

| Pass | Level | Skill | Status |
|------|-------|-------|--------|
| 1 | Persona | ux-write-persona | pending |
| 2 | Scenario | ux-write-scenario | pending |
| 3 | Flow | ux-create-flow | pending |
| 4 | Requirements | requ-derive-from-flow --incremental | pending |

**Pass 3 requires three sub-steps** (all must complete before Pass 3 is done):
1. `ux-flow-draft` — update each affected flow with the required changes
2. `ux-flow-complete` — content-complete each updated flow (moves to `aligned`)
3. `ux-flow-approve` — joint-approve the full cluster (moves all to `approved`)

**Resuming**: Check cascade_log.md status field → execute the next incomplete pass.
**Completing**: Task is done after Pass 4 (requirement-update goal.md files created).
```

Update Acceptance Criteria to include per-pass criteria:
```markdown
- [ ] Pass 1: Personas created/modified, cascade_log.md Pass 1 written
- [ ] Pass 2: Scenarios addressed (created, updated, or explicitly skipped), cascade_log.md Pass 2 written
- [ ] Pass 3: Flows updated AND re-approved (content-complete + joint-approve for the full cluster), cascade_log.md Pass 3 written
- [ ] Pass 4: requ-derive-from-flow run, requirement-update goal.md files created → DONE
```

After creating the task workspace, also create `plans_and_protocols/cascade_log.md` with:
```markdown
# Cascade Log: [TASK-ID]

**Origin**: [What was created/modified — fill in after Pass 1 begins]
**Started**: [YYYY-MM-DD]
**Hierarchy**: Persona → Scenario → User Flow → Requirements
**Status**: pending

---

## Pass 1 — Pending

### Completed
(none yet)

### Pending → Pass 2 (Scenario Level)
(to be filled after Pass 1)

### Artifacts Flagged
(to be filled after Pass 1)
```

**cascade_log.md status accuracy rule**: When an agent writes flow statuses into cascade_log.md, it MUST read the actual `review_status` field from each flow.md frontmatter at the time of writing — never copy from FLOW_INDEX.md (which may be stale) and never rely on memory. Run `python3 scripts/user_needs/sync_flow_index.py` first, then read flow.md frontmatter directly.

**If user declines multi-pass**: proceed with standard goal.md (no cascade fields added).

---

### goal.md Template — Explore Tasks

YAML frontmatter is identical to the Standard template. Only the body differs.

```markdown
---
[same YAML frontmatter as Standard template]
---

# Goal: [Task Title]

## Objective

[What problem space are we entering? What do we NOT yet know that this exploration should discover? Write in terms of questions and uncertainty, not deliverables.]

## Background

[Why are we here? What exists today and why is it insufficient? Context a future agent needs to understand the starting point.]

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/[YYYY-MM-DD]_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
\`\`\`
git show [hash]:[path/to/requirements.md]
\`\`\`

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

[3–8 open-ended entry points for the exploration. These are NOT tasks to complete — they are lenses to look through. Frame each as a question or a tension, not an instruction. Expect some to lead nowhere and others to open new threads. Leave room for the exploration to discover its own questions.]

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"how do self-improving LLM systems detect diminishing returns?"* rather than *"LLM self-improvement diminishing returns"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

[Qualitative description of what "done" looks like — not a deliverable checklist. What should a future implementer understand from reading the output?]

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The user has approved the final synthesis and stated what to do next
- [ ] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Related Tasks
<!-- Omit this section if related_tasks_refs is empty -->

| Task | Reason |
|------|--------|
| [TASK-XXX](../path/to/goal.md) | Predecessor — executor should read what was delivered |
```

---

### goal.md Template — Standard (impl / bugfix / define / review / analyze)

The goal.md MUST include YAML frontmatter with task metadata. Use the template below:

```markdown
---
task_id: TASK-[CATEGORY]-[REQ_NUM]-[TASK_NUM]
type: impl | bugfix | explore | define | review | analyze
parent_requirement: REQ-[CATEGORY]-[REQ_NUM]
urgency: [0-5]
urgency_reason: U[0-5]-[CODE]
impact: [0-5]
impact_reason: I[0-5]-[CODE]
status: pending
effort: XS | S | M | L | XL
created: [YYYY-MM-DD]
expected_tool_calls: [int]   # AC-01: estimated Bash + Read + Edit calls at runtime (S1). Declare this OR skill_chain_depth — at least one is required.
skill_chain_depth: [int]     # AC-01: count of heavy-skill invocations. Declare this OR expected_tool_calls.
# synthesis_dependent: true        # AC-02 (S3): include ONLY when the session must hold multiple input domains at once. Omit entirely when false (the default).
# synthesis_justification: "..."    # AC-02: one-line reason; required when synthesis_dependent is true.
# discovery_command: ""             # optional, open-scope (S2) tasks only: shell command whose stdout integer is the runtime work-item count (e.g. "flutter analyze 2>&1 | grep -c error"). Omit when scope is closed. Consumed by execution skills (TASK-PROC-001-10).
after: []             # task IDs this task must wait for — next_tasks.py checks these dynamically against completed status
awaiting: []          # EXTERNAL blockers ONLY (e.g. "waiting for design decision") — NEVER put task IDs here; next_tasks.py treats any non-empty awaiting as a permanent block regardless of those tasks' status
awaiting_note: ""     # plain-text explanation of the external blocker; required when awaiting is non-empty
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Brief summary of what this task implements"
release_description: ""  # max 15 words, English, user-benefit perspective; required for impl tasks
opus_recommended: false  # true: define tasks, cross-cutting explore, security/privacy, explicit trade-off analysis
writes_requirements: false  # set true for explore tasks that write/update requirements (keeps them on critical path in next_tasks.py even without target_package); set automatically by requ-derive-from-flow
worktree_path: ""  # set by code-bugfix on first run; bugfix tasks only
requirements_version:
  commit: [7-char hash]
  file: ../requirements.md
---

# Goal: [Task Title]

## Objective

[Clear description of what needs to be done]

## Bug Report
<!-- Only present for bugfix tasks. Remove this section for other task types. -->

**Steps to reproduce:**
1. [step]

**Expected behavior:**
[what should happen]

**Actual behavior:**
[what actually happens]

**Environment:** [device / OS / app version — optional]

**Logs:** [relevant log output — optional]

## Requirements Summary

[Brief summary of relevant requirements at task creation]

For complete requirements at task creation time:
\`\`\`
git show [hash]:requirements_tasks/[path/to/requirements.md]
\`\`\`

Current requirements: ../requirements.md

## Scope

### In Scope
[What this task covers]

### Out of Scope
[What this task does NOT cover]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-xxx | pending | Depends on X |

## Related Tasks
<!-- Omit this section if related_tasks_refs is empty -->

| Task | Reason |
|------|--------|
| [TASK-XXX](../path/to/goal.md) | Scope boundary — covers X; this task covers Y |

## Notes

[Additional context]
```

### Regenerate ID Registry (Just-in-Time)

**MANDATORY**: Before generating task IDs or looking up requirements in the registry, regenerate it (ensures IDs are always current):

```bash
python scripts/artifacts/generate_id_registry.py --requirements
```

This ensures `requirements_tasks/_meta/id_registry.md` reflects the current state of all requirements.

### Task ID Generation

To generate a unique task_id:

1. **Read the parent requirement's ID** from `requirements.md` YAML frontmatter
   - Example: `REQ-FUNC-005`

2. **If parent requirement has no `id:` field** (pre-migration or new requirement):
   - Look up the requirement in `requirements_tasks/_meta/id_registry.md`
   - **If found (exactly one match)**: use that ID, continue
   - **If not found or multiple matches**: **HARD STOP** — do not generate a task ID
     ```
     Cannot generate task ID: [path]/requirements.md has no `id:` field and
     the registry lookup returned [0 / N ambiguous] results.

     Fix first: add `id: REQ-[CATEGORY]-[NUM]` to the requirements.md frontmatter,
     then re-run task-create.
     ```
     Do NOT fall back to counting tasks at a parent level or guessing an ID.

3. **Allocate the task ID atomically** using the allocation script:
   ```bash
   python3 scripts/tasks/allocate_task_id.py --req-id [REQ-ID] --req-path [path-to-requirement-folder]
   ```
   - The script counts existing tasks + permanent reserve markers, picks the next free
     slot, creates a `.reserve-TASK-*` marker file inside the lock, then returns the ID.
     The marker persists indefinitely — it holds the slot even if this session is slow
     or resumed days later.
   - **If the script exits non-zero**: surface its stderr message to the user and stop.
   - **Do NOT** count goal.md files manually or construct the ID by hand.

4. **After writing goal.md**: delete the reserve marker:
   ```bash
   rm [req-path]/tasks/.reserve-[TASK-ID]
   ```
   The goal.md file is now the permanent record; the marker is no longer needed.

### Coverage Tracking (covers field)

**CRITICAL**: Before generating goal.md, check if the parent requirements.md has `trackable_items`:

**Plan-driven mode**: Skip user interaction. Use `covers_acs` from plan entry directly for `covers.acceptance_criteria`. Log: "Coverage auto-set from plan: [covers_acs list]". Skip to goal.md creation.

1. **Read requirements.md** and look for `trackable_items` in YAML frontmatter
2. **If trackable_items exists**:
   - List available acceptance_criteria and sections to the user
   - Ask: "Which items does this task implement?"
   - Populate the `covers` field with user's selection
3. **If no trackable_items** (pre-migration):
   - Leave `covers` with empty arrays
   - Add a note: "Coverage to be added after requirements migration"

Example interaction:
```
The parent requirement REQ-FUNC-005 has these trackable items:

Acceptance Criteria:
- AC-01: Displays questionnaire results over time
- AC-02: Simple Mode shows basic charts
- AC-03: Advanced Mode adds tabs and filters
...

Sections:
- SEC-01: Chart Visualization Logic
- SEC-02: Detail Interaction & Editing

Which items will this task implement? (e.g., "AC-01, AC-02, SEC-01")
```

### Package Inheritance (target_package field)

**MANDATORY**: After `covers` field is populated, determine `target_package` using these rules:

**Skip this entire section (leave `target_package` absent) if ANY of the following apply**:
- Task category is `process/` — process tasks have no release package
- `source_gap:` in goal.md — task was created by `requ-derive-from-flow`; package is determined later
- `verification_task: true` — verification tasks must stay unpackaged so they rank alongside the explore tasks they verify in `next_tasks.py`

**Plan-driven mode**: If plan entry includes `target_package`, use it directly. Skip rules 1–4. Log: "target_package auto-set from plan: [value]". Proceed to rule 5 (write to frontmatter).

1. **Read parent requirement's trackable items** — extract `target_package` from each referenced AC/section
2. **All covered items assigned**: Inherit the package of the earliest-versioned item (semver comparison on the associated version). Log the inherited value to the user.
3. **Some items unassigned or `covers` is empty**: Prompt user — "Covered items have mixed/no package assignments. Which package should this task target?" Load available packages from `requirements_tasks/RELEASE_BACKLOG.md` and present options grouped by version.
4. **RELEASE_BACKLOG.md not at canonical path**: Search for it — `find . -name "RELEASE_BACKLOG.md" -not -path "./.git/*" 2>/dev/null | head -3` — and use the first result found. Only if the search also returns nothing: warn the user and skip (do not fail task creation).
5. **Write `target_package`** to task's YAML frontmatter in goal.md, after the `covers` field:
   ```yaml
   covers:
     acceptance_criteria: [AC-01, AC-02]
     sections: []
   target_package: PKG-0.0.1-core   # omit field entirely if user skipped
   ```

**Example interaction**:
```
Inherited target_package: PKG-0.0.1-core (from AC-01, AC-02)

OR

Covered items have no package assignments.
Available packages from RELEASE_BACKLOG.md:
v0.0.1:
  PKG-0.0.1-core  — Core Data Transfer
  PKG-0.0.1-ui    — UI Polish
v0.1.0:
  PKG-0.1.0-mvp   — Beta MVP

Which package does this task target? (enter package ID or skip)
```

### User Needs Reference Check

**When creating tasks that implement user flows:**

**MANDATORY: Read user needs guidelines first** (in parallel):
| README | Content |
|--------|---------|
| `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` | Bidirectional links |
| `requirements_user_needs/README_12_REVIEW_STATUS.md` | Review status rules |
| `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md` | Reference notation |

1. **Check if epic/feature has user_needs field**:
   - Read parent epic/feature requirements.md YAML
   - Look for `user_needs.implements_flows[]`

2. **If user_needs exists**:
   - List the flows this epic/feature implements
   - Ask: "This epic/feature implements these user flows: [list]. Does this task relate to any of them?"
   - If yes, add to goal.md:
     ```yaml
     related_flows: [FLOW-001, FLOW-002]
     ```
   - **Note**: Flow IDs now use format `FLOW-NNN` (3-digit, e.g., FLOW-001) not hierarchical `FLOW-XXX-XX-XX`

3. **Check flow review_status** (per README_12):
   - Resolve flow ID to path: Search `requirements_user_needs/user_flows/*/flow.md` for matching ID
   - Read flow.md YAML frontmatter
   - Warn if referenced flows are not `approved`:
     ```
     Warning: FLOW-001 has review_status: draft
     Implementing non-approved flows may require rework.
     Proceed? (y/n)
     ```

4. **Suggest flow reference if missing**:
   - If epic has no user_needs field, suggest:
     ```
     Note: The parent epic has no user_needs references.
     Consider running `requ-explore` to identify which user flows this epic serves.
     ```

### File Naming Validation

**CRITICAL**: After creating the task workspace, validate file naming to prevent common mistakes:

#### Check 1: requirements.md Naming
```bash
# Check if the parent requirement file uses correct naming
ls -la requirements_tasks/[path]/requirement.md 2>/dev/null
```
- **If found**: File is incorrectly named (singular)
- **Action**: Warn user and offer to rename:
  - `git mv requirement.md requirements.md`
  - Update task's `requirements_version.file` reference

#### Check 2: YAML Frontmatter Field Names
Read the parent requirements.md and verify:
- Uses `id:` (correct)
- Uses `requirement_id:` (incorrect - will not be detected by status scripts)

If incorrect field name found:
- Warn user: "The requirements.md uses 'requirement_id:' but should use 'id:' for script compatibility"
- Offer to fix automatically

#### Check 3: Task goal.md Validation
After creating goal.md, verify:
- File exists at correct path
- Has valid YAML frontmatter
- `task_id` follows pattern: `TASK-[CATEGORY]-[REQ_NUM]-[TASK_NUM]`
- `requirements_version.file` points to `../requirements.md` (not `../requirement.md`)

**Why**: The status overview script (`scripts/artifacts/generate_status_overview.py`) searches for:
- Files named `requirements.md` (plural) - will ignore `requirement.md`
- YAML field `id:` - will ignore `requirement_id:`

Without proper naming, the requirement won't appear in STATUS.md reports.

## Special Cases

### Functional Requirements (Epic-Tasks)
- Epics use `epic_` prefix: `functional/therapist/epic_client_management/`
- Features have NO prefix: `functional/therapist/epic_client_management/client_plan_view/`
- Epic tasks/ folders: ALLOWED for `explore_`, `define_`, `analyze_`, `review_`
- Epic tasks/ folders: **FORBIDDEN** for `impl_` (implementation goes in Feature tasks)

### Non-Functional & Process Requirements
- Flexible hierarchy (no epic/feature structure)
- Can have additional grouping levels as needed
- Example: `non-functional/ui_ux_design_system/layout/responsive_master_detail/`

### Refactorings
- **NOT a standalone requirement**
- Create as a task within the related requirement's `tasks/` folder

## Key Principles
1. **Organization is paramount** - take time to find the right place
2. **Always investigate before deciding** - don't guess
3. **When in doubt, ask the user** - but show your reasoning first
4. **Keep related items together** - check what already exists
5. **Follow existing patterns** - look at similar requirements for guidance

**Important**: This skill enhances native workflow, doesn't replace it.

---

## Creating a Revision-Attached Task

### When to use

A skill (the *originator*) needs a peer skill (the *target*) to asynchronously revise an upstream artifact in a fresh session. The originator cannot fix the artifact itself (it owns a different responsibility) and the fix takes more than a quick same-session call.

Examples:
- `ui-verify-flutter` finds a component mismatch in a scribble → needs `ui-scribble-iterate` to regenerate it
- `code-simple` detects a flow step the scribble never covers → needs `ui-scribble-iterate` to add the missing screen
- `verify-quality` finds a doc gap that requires `requ-explore` to resolve

### Step 1 — Create the revision task normally

Call `task-create` (or `task-derive-from-requ` if requirement coverage is needed) with:
- `type: impl`
- A task name that makes the revision target obvious, e.g. `revise-scribble-v4-component-fix`
- `parent_requirement`: same as the task that triggered the revision
- `after`: the task ID of the originating task (so the revision task is visible immediately after)

The revision task's `goal.md` Objective section should describe what needs to change and why.

### Step 2 — Attach revision_target.yaml

After the task workspace is created, write `revision_target.yaml` into the new task's `plans_and_protocols/`:

```
requirements_tasks/.../tasks/<revision-task>/plans_and_protocols/revision_target.yaml
```

The schema is at `.claude/schemas/revision_target.yaml`. Required fields:

```yaml
originator: <your-skill-name>
target_skill: <skill-that-owns-the-artifact>
artifact: <path-to-artifact-or-folder>
reason: structural | rule_conflict | infeasible | flow_flaw | drift | other
responder_required: skill   # use 'human' only if developer decision is unavoidable
detail: |
  <Complete explanation. The receiving skill has no session history — be self-contained.>
blocks_completion_of: <TASK-ID-of-the-blocked-task>
cycle_count: 1
created: <YYYY-MM-DD>
```

### Step 3 — The lifecycle IS the task

Do NOT write `revision_target.yaml` anywhere else (not in `automation/pending_feedback/`, not at the project root). The task's `status` field gates visibility:

| Task status | Meaning |
|---|---|
| `pending` | Revision is queued; orchestrator will dispatch it |
| `in_progress` | Target skill is executing the revision |
| `completed` | Revision done; `revision_target.yaml` is audit trail |

No separate scanner or polling is needed. The orchestrator's normal task queue processes it.

### Escalation (5-cycle protocol)

If `cycle_count` reaches 5 without resolution, the receiving skill MUST stop the revision loop and write a `question.md` in `automation/pending_feedback/<TASK_ID>/` instead. This is the same 5-cycle escalation used by `verify-quality` (CLAUDE.md §7).
