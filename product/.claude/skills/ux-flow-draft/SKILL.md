---
name: ux-flow-draft
user-invocable: false
description: "[Internal — use ux-create-flow] Author or iterate a user flow draft"
tools: Read, Write, Bash, Glob, Grep, Agent
model: inherit
---

⚠ STOP — INTERNAL SKILL. Entry point is `ux-create-flow`.

If the **user** invoked this skill directly (not delegated here by `ux-create-flow`):
**Do NOT proceed with any steps below.** Instead call `Skill("ux-create-flow")` with the user's original message as args, then stop.

---

You author or iterate a user flow draft. The dispatcher (`ux-create-flow`) has already determined the mode (NEW or CONTINUE) — do not re-run mode detection.

## MANDATORY: Read ALL Required Guidelines

**BEFORE doing anything else**, read these files **simultaneously**:

| README | Content |
|--------|---------|
| `README_5_USER_FLOW_DEFINITION.md` | Template, exception model, checklist |
| `README_6_PCD_LAYER.md` | Resource cost column, suffizienz |
| `README_7_META_INFO_STANDARDS.md` | YAML frontmatter, IDs, evidence markers |
| `README_8_CROSS-REFERENCING_SYSTEMS.md` | Bidirectional epic/feature links |
| `README_10_WRITING_GUIDELINES.md` | Language, tone |
| `README_12_REVIEW_STATUS.md` | Review workflow, review_history |
| `README_13_CROSS_REFERENCE_NOTATION.md` | Reference notation, YAML user_needs |
| `README_14_DEVIATION_DOCUMENTATION.md` | Deviation tables |
| `README_15_TECHNOLOGY_NEUTRALITY.md` | Technology-agnostic language |

All files are in `requirements_user_needs/`.

**You MUST follow all rules from these READMEs. DO NOT proceed without reading them first.**

---

## Mode

Check whether this is **NEW** (no existing flow.md) or **CONTINUE** (flow.md exists).
- NEW → run Steps 1–5 then Step 6.
- CONTINUE → run Context Loading then Step 6.

---

## NEW MODE: Steps 1–5

### 1. Gather Flow Information

Ask user for:
- **Flow name**: Descriptive approach name (will be converted to snake_case)
  - Example: "Quick Night Entry via Voice" → quick_night_entry_voice
- **Flow approach**: How does this flow solve scenario goals?
  - What makes this approach different from alternatives?
  - Example: "Voice-to-text for hands-free entry when user has low energy"
- **Which scenario(s) will this flow serve?**: Provide scenario IDs or paths (e.g., SCEN-002-01, SCEN-003-01)
  - Allow multiple scenarios
  - For each scenario, ask:
    - Relationship: `primary` | `alternative` | `supporting`
    - Coverage: `full` | `partial` | `minimal`
    - Notes (optional)

For each scenario, read and validate its YAML frontmatter:
- Extract: `scenario_id`, `persona_id`, `persona_name`, `name`, `review_status`
- Read **Success Criteria** section (flow must address these)

**If any scenario is not approved**:
```
Warning: Scenario [NAME] has review_status: [STATUS] (not approved)
Creating flows for non-approved scenarios may require rework.
Proceed anyway? (y/n)
```

After per-scenario warnings, if multiple scenarios are not approved, add:
```
N of M scenarios are not approved. Flows based on non-approved scenarios may require rework. The more non-approved scenarios, the higher the rework risk.
```

**Multi-perspective flows**: If the flow serves scenarios from different user roles (e.g., therapist AND client), it is a multi-perspective flow. Additional considerations:
- Use a Swimlane column in the happy path table to identify the acting role at each step
- Consider splitting into phases if the flow spans different locations or time periods
- Identify handoff moments (where control/data passes between roles) as critical design points
- Scope exceptions to specific phases where applicable (e.g., "Phase 1 Exceptions", "Phase 2 Exceptions")

### 1b. Scan Existing Flows (Duplicate Guard + Design Context)

After scenario IDs and personas are known:

1. Read `requirements_user_needs/user_flows/FLOW_INDEX.md`
2. From the "Existing Flows" section, identify entries that share any of the current scenario IDs or personas
3. **Duplicate check**: If an existing flow already serves the exact same scenario(s) with the same approach → stop and ask: "FLOW-NNN already covers this scenario with a similar approach. Did you mean to iterate on that flow instead?"
4. **Related flows**: If overlapping flows exist (same persona/scenario, different approach):
   - List them: "Existing flows for these scenarios: FLOW-NNN ([name]) — [purpose from index]"
   - Ask user: "Should I read any of these for design context before creating the new flow?"
   - If yes → spawn a **subagent** (Agent tool):
     - Provide: list of `flow.md` paths and instruction: "Read each flow.md. For each, extract and return: flow ID, name, trigger condition, happy path in max 5 steps, and 2–3 key design decisions. Return only these summaries, not the raw file content."
     - Do NOT read raw `flow.md` files in the main session — use only the summaries returned by the subagent
5. Carry the concise flow summaries into Step 3a analysis as "Existing Flow Context"

### 2. Gather Additional Metadata

Ask user for:
- **Evidence level**: grounded | proto_persona | hypothesis
- **Initial implementation status**: not_started | partial | complete
  - Most new flows will be "not_started"

**Release Scope** (optional — skip if unknown):
- Ask: "How should this flow be chunked for release? Which steps/exceptions/variants belong together as releasable units?"
- Rules:
  - Happy path is always priority **1** (highest)
  - Named Variants can join an existing chunk or get their own chunk
  - Priority is an **integer**: 1 = first to release; higher number = lower priority; multiple chunks may share the same number; no maximum defined
  - No names required — labels are descriptive only; no mapping to RELEASE_BACKLOG.md needed
- AI should propose chunks based on flow content; user confirms or adjusts
- Store as structured YAML in flow.md frontmatter:
  ```yaml
  release_scope:
    - label: "Core Transfer"
      covers: "Happy path Steps 1–6"
      priority: 1
    - label: "File Transfer Alternative"
      covers: "Exception 4.3, Named Variant: File Transfer"
      priority: 2
    - label: "Remote Sessions"
      covers: "Exceptions 4.4, 4.5"
      priority: 2
    - label: "Edge Cases"
      covers: "Exceptions 5.1, 6.1"
      priority: 3
  ```
  Omit `release_scope` entirely if user skips.

**Optional** (can be refined when writing flow):
- Preconditions (user state, system state)
- Specific screens/components involved
- Known edge cases

### 3. Investigate Existing Requirements

If instructed or the information provided suggests it:
- List the folders below requirements_tasks/functional and below requirements_tasks/non-functional.
- Read the requirement files that seem to be relevant.

### 3a. Analysis Phase (optional — for complex flows)

**Trigger**: Run this phase if ANY of the following: multiple personas, dual-perspective flow (different user roles), existing requirements to reconcile.

Produce a structured analysis document:

```
## Analysis: [Flow Name]
1. What existing requirements assume about this interaction
2. What scenarios describe as the real user context
3. Gaps: requirement elements with no scenario support
4. Tensions: requirements that conflict with scenario reality
5. Missing: user need moments not addressed by requirements
6. Synthesis: recommendations for the flow (happy path, exceptions, priorities)
7. **Value Conflicts** (VCD check — required for multi-persona flows):
   - Read `vcd:` YAML blocks for all personas this flow serves
   - List any primary/secondary value conflicts between serving personas
   - If conflicts exist → flow.md must include a `## Value Trade-offs` section
   - Use the `vcd-log-tradeoff` skill to document each conflict record
```

**USER REVIEW CHECKPOINT**:
- **Interactive mode**: Present the analysis and wait for user approval. Do not proceed to Step 4 until confirmed.
- **Automated mode** (`CLAUDE_AUTOMATED_MODE=1` + sentinel): Write `question.md` to `automation/pending_feedback/<TASK_ID>/` with the full analysis as the question body and "Approve analysis to proceed to flow creation, or provide corrections." Copy the answer template, then call `bash scripts/automation/terminate_session.sh`.

After user review, append a **User Review Decisions** section to the analysis documenting each decision:
- Question asked
- User's answer
- Implications for the flow

These decisions are binding for the flow creation phase.

### 4. Regenerate ID Registry and Generate Unique ID

**MANDATORY**: Before generating a flow ID, regenerate the registry:

```bash
python scripts/artifacts/generate_id_registry.py --user-needs
```

Then read `requirements_user_needs/_meta/id_registry.md` for next available FLOW-NNN.

Next ID = FLOW-[NNN] (sequential, 3-digit zero-padded)

### 5. Create Folder Structure

```bash
mkdir -p "requirements_user_needs/user_flows/[flow_name]"
```

→ Proceed to **Step 6**.

---

## CONTINUE MODE: Load Existing Context

### Step 2.0 — Discover Feedback Source

Before reading any other context, resolve the task ID and discover where feedback lives:

```bash
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ | grep goal.md | head -1)
TASK_ID=$(grep -m1 "^task_id:" "$GOAL" 2>/dev/null | awk '{print $2}')
```

Check three locations in priority order:
1. `automation/pending_feedback/$TASK_ID/answer.md` — highest priority (current unresolved)
2. `requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*$TASK_ID*.md` — archived checkpoint (orchestrator merged Q+A here after last resume)
3. `<task_folder>/user_feedback/*.md` — legacy/manual feedback files

Read the first non-empty source into `feedback_text`. Record which source was used (log to protocol.md). If multiple sources have content, use source #1 exclusively.

If none have content: ask interactively "What changes or feedback would you like to incorporate?" — do not proceed until at least one feedback item is known.

**Status reset**: If the flow's current `review_status` is `draft`, `aligned`, or `approved`, set it to `in_review` and add a `review_history` entry:
`seq: [existing entries count + 1], from: [current_status], to: in_review, reviewer: LLM, notes: "User provided feedback — returning to in_review for iteration."`

If the flow is `pending_alignment` and contains **no** `## Pending Impacts` section, also reset to `in_review` the same way (pending impacts may have been addressed manually).

**YOU MUST READ ALL ITEMS BELOW. THIS IS NOT OPTIONAL.**
Skipping scenarios or personas is a known failure mode — without them you may miss success criteria constraints that invalidate your changes. Read all in parallel (single tool call batch):

1. **Existing `flow.md`** (current draft)
2. **Feedback files** (from task's `user_feedback/` folder or user-provided path). If no feedback files are found and the user has not provided feedback in the current session, ask: "What changes or feedback would you like to incorporate in this iteration?" Do not proceed to Step 6 until at least one feedback item is known.

2b. **Classify feedback: flow changes vs implementation intent**

For each feedback item, apply this two-question test:

- **Q1: Would a UX designer (who cannot read code) understand and care about this?**
  - YES → Flow feedback → process in Step 6 as before
  - NO → go to Q2
- **Q2: Does it name a specific technology, framework component, library, code artifact, or internal architecture pattern?**
  - YES → Implementation intent → write to `notes.md`
  - NO → Requirement constraint (functional, no tech named) → include in flow as-is; it will reach requirements.md via the derive pipeline

**Writing implementation intent to `notes.md`**:
1. Check if `notes.md` exists in the flow folder (sibling of `flow.md`)
2. Read existing content if present; append a new dated iteration section; create with YAML frontmatter if new:
   ```markdown
   ---
   flow_id: FLOW-NNN
   flow_name: [flow name]
   ---
   # Developer Notes: [Flow Name]
   Implementation intent captured during flow review. Not UX. Carried forward
   to Developer Guidelines in requirements.md by the requ-derive-from-flow pipeline.
   ```
3. For each implementation intent item, write one line:
   `- **[Step N]** [item] — [brief rationale if user provided one]`
   Use `[General]` when item isn't tied to a specific step.
4. Write/update `notes.md`
5. Tell the user: "I classified N item(s) as implementation notes (written to notes.md): [list]. The remaining M item(s) are flow changes."

**Mixed sentences**: If a feedback item contains both UX rationale and a technology name, split it — UX part to flow feedback, technology name to `notes.md` with a reference to the UX rationale.

**If ALL feedback is implementation intent** (nothing to change in flow.md): skip Step 6. Update `notes.md` only, then commit and output:
> "No flow changes in this feedback round. Implementation notes written to notes.md."

**Include `notes.md` in the Step 11b commit** whenever it was created or modified.

3. **ALL scenarios** referenced in flow's `serves_scenarios` YAML frontmatter — read EACH scenario.md in full, including Success Criteria. DO NOT SKIP THIS.
4. **Persona files** for those scenarios — read EACH persona.md. DO NOT SKIP THIS.
5. **Requirement files** referenced in flow, or based on a new search if it seems useful
6. **`requirements_user_needs/user_flows/FLOW_INDEX.md`** — identify sibling flows that:
   - Were added since the last iteration (new flows sharing same scenarios/personas)
   - Have `review_status: pending_alignment` (contain finalized design decisions that may affect this flow)
   - Reference this flow in a `## Pending Impacts` section (strongest signal — directly queued for this flow)

   For each identified sibling: read its flow.md — but only: frontmatter, steps (names + actor + one-line summary), exceptions list (names + triggers only), scope boundaries, and `## Pending Impacts` section if present. Do NOT read full narrative (context window protection).

   Present to user before proceeding: "Sibling flow FLOW-NNN ([status]) has been read as context for this iteration. [Brief reason: pending_alignment / new overlap / pending impacts]"

   This is NOT optional when sibling flows in `pending_alignment` exist — they contain design decisions that may directly affect the current flow.

**SELF-CHECK before proceeding**: Have you issued parallel Read calls for items 1–6? If not, do it now before continuing.

**Release scope check**: Review `release_scope` in the flow's YAML frontmatter:

- **If `release_scope` is absent**: Analyze the flow content and propose chunks. Happy path = priority 1; group related exceptions and Named Variants into chunks with integer priorities. Present to user: "No release scope defined yet. Based on the flow content, I suggest: [list of label / covers / priority]. Confirm or adjust?" Update YAML only after user confirmation.
- **If `release_scope` exists**: Ask: "Does the release scope still reflect the current flow structure? (current chunks: [label — priority])" — propose changes if this iteration added/removed steps, exceptions, or Named Variants that affect chunking.

**Pending Impacts check**: If flow.md contains a `## Pending Impacts` section, treat each entry as mandatory feedback for this iteration — address it alongside any user-provided feedback. After the iteration is complete and the impacts have been incorporated:
- Remove the `## Pending Impacts` section from flow.md
- Set `review_status: in_review` in flow.md
- Add `review_history` entry: `seq: [N], from: pending_alignment, to: in_review, reviewer: LLM, notes: "Pending impacts incorporated. Ready for user review — signal content complete when satisfied."`
- Commit: `git commit -m "ux(FLOW-NNN): pending impacts incorporated, in review"`

→ Proceed to **Step 6**.

---

## 6. Generate or Improve flow.md

Ensure all relevant context (scenarios, requirements, feedback, sibling flows) has been read in the current session before writing. Write flow.md directly.

**New mode**: Use template from README_5_USER_FLOW_DEFINITION.md exactly. Think deeply about UX realism and development usefulness. Include `release_scope` (structured format with label, covers, priority) in the YAML frontmatter if it was set in Step 2; omit the field if not selected.

**VCD**: If value conflicts were identified in Step 3a, include a `## Value Trade-offs` section at the bottom of flow.md with inline Value Trade-off Records.

**Continue mode**: Analyze feedback point by point. Evaluate against scenario success criteria and README rules. Improve flow.md — preserve what works, fix what doesn't.

**Brevity rule (applies to both modes)**: Write as concisely as possible without omitting content. Every sentence must earn its place — if a point is already clear from context, don't restate it. In Continue mode, actively look for redundancy introduced by previous iterations and remove it while incorporating new feedback. The goal is a file that a developer or designer can read quickly and act on — not a complete record of every design consideration ever discussed.

## 7. Update Scenario References (Bidirectional)

**Continue mode**: If `serves_scenarios` YAML changed since last iteration (scenario added/removed), re-execute Steps 7-9. If unchanged, skip Steps 7-9. Always verify Step 11 (FLOW_INDEX) reflects current state.

**CRITICAL**: For each scenario, update its `implements_flows` YAML field:

1. Read scenario.md
2. Parse YAML frontmatter (capture current review_status)
3. Add to `implements_flows` array (or create if missing):
   ```yaml
   implements_flows:
     - flow_id: FLOW-[NNN]
       relationship: [user choice from step 1]
       coverage: [user choice from step 1]
       notes: "[user notes from step 1]"
   ```
4. Write back scenario.md
5. **PRESERVE** existing review_status (do NOT reset to "in_review" - this is a reference-only change)
6. Add `review_history` entry documenting the reference addition

**Important**: Preserve all existing YAML fields and formatting.

## 8. Populate Flow YAML

Ensure flow.md includes the `serves_scenarios` array in YAML frontmatter. If `release_scope` was updated in the release scope check, also write the updated structured format.

**Continue mode**: Verify/update existing YAML rather than recreate.

## 9. Update Epic/Feature References (Bidirectional)

**Continue mode**: Skip if already handled in previous iteration and `serves_scenarios` unchanged.

For each existing epic/feature that implements steps in this flow (skip TBD entries):
1. Open its `requirements.md`
2. Add/update the `user_needs` YAML section with `implements_flows`, `addresses_scenarios`, and `personas_served` per README_13 format
3. If the epic has no `user_needs` section yet, create one

**Note**: This creates the bidirectional link. Skipping causes asymmetric references (README_8 Rule 2).

## 10. Validate

Validate technology agnosticism and completeness using the **Flow Writing Checklist** from README_5_USER_FLOW_DEFINITION.md.

Additional checklist items:
- [ ] If `release_scope` was set: happy path chunk exists with `priority: 1`
- [ ] If `release_scope` was set: each Named Variant is assigned to a chunk
- [ ] If `release_scope` was set: each entry has `label`, `covers` (non-empty), and `priority` (integer ≥ 1)

## 11. Update FLOW_INDEX.md

**REQUIRED**: Keep flow index in sync.

Read `requirements_user_needs/user_flows/FLOW_INDEX.md`, then:
- **New mode**: Add entry to "Existing Flows" section with flow ID, name, status, purpose, personas, implementation status
- **Continue mode**: Update existing entry if status, personas, or implementation status changed
- Preserve all other sections unchanged

If during flow creation you identified flows that should exist but don't, add them to the "Needed Flows" section of FLOW_INDEX.md with: status, purpose, trigger, key questions, and discovery source.

Then regenerate the ID registry to include the newly created flow:
```bash
python scripts/artifacts/generate_id_registry.py --user-needs
```

## 11b. Commit

Stage and commit all modified flow artifacts:

```bash
git add requirements_user_needs/
git commit -m "ux(FLOW-[NNN]): [new|update] [flow name]"
```

Use `new` for first-time creation, `update` for a continue-mode iteration.

## 12. Output

**New mode**:
```
User flow created: requirements_user_needs/user_flows/[name]/flow.md
ID: FLOW-[NNN]
Serves: [scenario IDs and names]
Status: draft

Next steps:
1. Review happy path and exceptions
2. Provide feedback or signal content complete
3. Link to implementing epics

Release scope: [chunks with priorities if set, or "not defined yet"]

Signal content complete when satisfied:
- "content complete FLOW-[NNN]" or "I'm done with FLOW-[NNN]"
  → Impact analysis runs automatically
  → If no siblings: directly approved
  → If siblings: pending_alignment + CONTINUE reminders created

→ Or reply "yes" to this message to signal content complete immediately.
```

After presenting this output, ask the user: "Are you satisfied with this flow? (y/n)" — if yes, immediately invoke ux-flow-complete for this flow.

**Continue mode**:
```
User flow updated: requirements_user_needs/user_flows/[name]/flow.md
ID: FLOW-[NNN]
Changes: [summary of feedback-driven changes]

Next steps:
1. Review updated flow
2. Provide additional feedback or signal content complete

Signal content complete when satisfied:
- "content complete FLOW-[NNN]" or "I'm done with FLOW-[NNN]"
  → Impact analysis runs automatically
  → If no siblings: directly approved
  → If siblings: pending_alignment + CONTINUE reminders created

→ Or reply "yes" to this message to signal content complete immediately.
```

After presenting this output:
- **If feedback was consumed from `pending_feedback/` (Step 2.0 source #1)**: delete the folder (the orchestrator already wrote the feedback-checkpoint before calling this session):
  ```bash
  [ -d "automation/pending_feedback/$TASK_ID" ] && rm -rf "automation/pending_feedback/$TASK_ID"
  ```
  Include this deletion in the Step 11b commit.
- **Interactive mode**: Ask "Are you satisfied with this flow? (y/n)" — if yes, immediately invoke ux-flow-complete for this flow.
- **Automated mode**: see block below.

**Automated mode end-of-iteration** (skip interactive y/n, run this instead when `CLAUDE_AUTOMATED_MODE=1` + sentinel active):

1. Clean up consumed answer (if feedback came from `pending_feedback/`):
   ```bash
   TASK_ID=<task_id>
   if [ -d "automation/pending_feedback/$TASK_ID" ]; then
     rm -rf "automation/pending_feedback/$TASK_ID"
   fi
   ```
   (The orchestrator already archived Q+A into the task's `plans_and_protocols/` before launching this session.)

2. Write next question.md to `automation/pending_feedback/$TASK_ID/question.md`:
   ```markdown
   ---
   task_id: <TASK_ID>
   session_id: <SESSION_ID>
   account: <$CLAUDE_SESSION_ACCOUNT>
   status: awaiting_answer
   asked_at: <date -u +%Y-%m-%dT%H:%M:%SZ>
   skill: ux-flow-draft
   ---

   # Flow Review Request: FLOW-[NNN]

   This iteration updated [flow name]. Changes made:
   [2-3 bullet summary of what changed]

   Current flow: [path to flow.md]

   Please review and reply with:
   - Feedback for the next iteration, OR
   - "approved" to finalize this flow
   ```

3. Copy answer template:
   ```bash
   cp automation/pending_feedback/TEMPLATE_answer.md automation/pending_feedback/$TASK_ID/answer.md
   ```

4. Include the folder move and question.md in the Step 11b commit (same atomic commit as flow.md).

5. Terminate:
   ```bash
   bash scripts/automation/terminate_session.sh
   ```

Status remains `in_progress` — the `question.md` is the waiting signal. Do NOT write `status: active`.

## Key Principles

All rules are documented in the READMEs listed above. You MUST follow them.

**Critical rules** (violations will be rejected):
- Use exception model (main path + numbered exceptions) from README_5
- Technology-agnostic language per README_15 (no SQLite, Firebase, Flutter specifics)
- Include Resource Cost column for energy-intensive flows per README_6
- Add bidirectional epic/feature links per README_8 and README_13
- Document deviations per README_14 if flow cannot fully satisfy scenario
- Set `review_status: draft` and add `review_history` entry per README_12 (include `seq: [existing count + 1]`)
- `pending_alignment` and `aligned` flows are NOT approved — never reference them in epics/features/tasks
- **Brevity**: Flow files must be as short as possible while remaining complete. No redundancy, no restating what is already clear. Omit no content — but use fewer words.
- **Mode-agnostic feedback**: CONTINUE mode discovers feedback from `pending_feedback/`, task `plans_and_protocols/*feedback-checkpoint*.md`, or `user_feedback/` — works identically whether started by autorun or manually.
- **No `active` status**: Use `in_progress` + `pending_feedback/question.md` as the waiting signal instead.
