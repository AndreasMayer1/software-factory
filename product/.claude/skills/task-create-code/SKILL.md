---
name: task-create-code
description: Create Dart code task for lib/, test/, or integration_test/ changes. THIS SKILL MUST BE USED TO CREATE CODE TASKS.
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You create Dart code tasks that bridge functional requirements to implementation. **Use this skill only when the task will change files in `lib/`, `test/`, or `integration_test/`** — i.e. the goal routes to `code-simple`, `code-complex`, or `code-test`. For process/doc/script tasks, use `task-create` instead.

**Factory position**: `REQ → task-create-code (this) → TASK → task-start → claude-route → code-simple/code-complex → CODE`

**Philosophy**: Tasks contain WHAT to implement, not HOW.
- **Requirements** define WHAT & WHY
- **Tasks** define WHAT to implement + context for sizing
- **Plans** (created at implementation time) define HOW
- **Code** is the authoritative documentation

**Why**: concrete code changes in tasks become outdated; the plan is created fresh at implementation time.

---

## Input

- Standard: `"Use task-create-code skill for [requirement_path]"`
- **Zero-parameter** (auto-pick): `"Use task-create-code skill"` — discovers the next missing impl task for the active package (Phase 0).

Optional: user may provide extra details (design specs, sketches, …).

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — when a requirement path is given, fail loudly if its requirements.md is missing or off-schema. (Zero-parameter auto-pick discovers the requirement in Phase 0, so the guard is skipped when no path is passed.)
```bash
REQ_INPUT="${1:-}"; REQ_FILE="${REQ_INPUT%/}"; [ -d "${REQ_FILE}" ] && REQ_FILE="${REQ_FILE}/requirements.md"
[ -z "${REQ_INPUT}" ] || [ -f "${REQ_FILE}" ] || { echo "ERR: no requirements.md at ${REQ_INPUT} (required input per contract.yaml)"; exit 2; }
[ -z "${REQ_INPUT}" ] || python3 scripts/quality/validate_against_schema.py "${REQ_FILE}" .claude/schemas/requirements_frontmatter.yaml || exit 2
```

---

## Redirect Logic (AC-10) — Standalone Mode Only

**Skip entirely if ANY of these apply**:
- Plan-driven mode is active (plan entry provided via `plan_path` or `TASK_CREATE_PLAN_ENTRY`)
- Task type is `bugfix`, `explore`, `define`, `analyze`, or `review`

**Trigger** (all three must be true):
1. Standalone mode (no plan entry)
2. Task type is `impl` or `verify`
3. Parent requirement has `trackable_items.acceptance_criteria` AND ≥ 1 AC has zero task coverage

**Check uncovered ACs**:
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

---

## Phase 0: Discovery (skip if a requirement path was provided)

Goal: pick the next package to create an impl task for, then resolve it to a requirement path.

**IMPLEMENTATION ORDER PRINCIPLE**: When an approved task creation plan exists (`plan_path`
set in the orchestration task), the plan's execution order is authoritative — do NOT use
RELEASE_BACKLOG `priority_within_source` to pick the package. The plan encodes architectural
dependencies (domain → data → presentation). Business priority is secondary.

### Phase 0A: Plan-Driven Discovery (when orchestration task has plan_path)

**Check plan_path FIRST** — before any RELEASE_BACKLOG scanning.

1. Find the orchestration task's goal.md (the session entry point — routed via `Do [TASK-ID]`).
   Extract `plan_path` from its YAML frontmatter.

2. **If plan_path is non-empty**: run `--next-uncreated` to get the next task the plan expects:
   ```bash
   python3 scripts/tasks/parse_task_creation_plan.py \
     --plan [plan_path] \
     --next-uncreated \
     --format json
   ```
   Output: JSON with `target_package`, `req_path`, `task_name`, `covers_acs`, `effort`,
   `layer`, `after`, `task_type`, `implementation_notes`, `opus_recommended`.

3. Use the plan entry's `req_path` as the resolved requirement path. Use all plan values as
   **authoritative defaults** for subsequent phases:
   - `covers_acs` → `covers.acceptance_criteria` in goal.md (Phase 3.3c)
   - `effort` → accepted as baseline; Phase 2 still runs to refine (AC-15)
   - `layer` → Scope Overview (Phase 3.3)
   - `after` → dependency list (see §propose_after interaction below)
   - `task_type` → routing hint
   - `implementation_notes` → appended to `## Additional Details`
   - `opus_recommended` → accepted as baseline; Phase 2 may promote to `true` if mismatch found (AC-15)
   - `requirements_version` → commit hash from plan entry; used for stale-plan detection (step 3.5)

3.5 **Stale plan check (AC-12 consumer)**: Compare the plan's `requirements_version.commit` against the current git hash of requirements.md:
   ```bash
   CURRENT_HASH=$(git log -1 --format=%h -- "[req_path]/requirements.md")
   ```
   - If `CURRENT_HASH` ≠ plan's `requirements_version.commit`:
     - **Interactive mode**: warn — "Plan was created against commit [X], but requirements.md is now at [Y]. Plan may be stale." Ask user: proceed / abort / re-plan.
     - **Automated mode**: write `question.md` in `automation/pending_feedback/<TASK_ID>/` describing the hash mismatch; stop.
   - If equal: continue silently.

4. Print confirmation and proceed to Phase 1:
   ```
   Using plan execution order: [task_name] for [target_package]
     req_path: [req_path]
     covers_acs: [AC-01, AC-02, ...]
     effort: [M]  layer: [domain]  after: [...]
   Proceeding (plan approved — RELEASE_BACKLOG priority bypassed).
   ```

5. **In automated mode** (`CLAUDE_AUTOMATED_MODE=1`):
   - If `parse_task_creation_plan.py` exits non-zero or returns zero tasks: write `question.md`
     with the error and stop (do not proceed to Phase 1).
   - If `--next-uncreated` returns no entry (all plan tasks already created): stop. Chain-end
     validation is the orchestration task's responsibility — `create_orchestration_task.py`
     auto-detects all-covered state and emits a validation orch task (no `--mode` flag).

6. **In interactive mode**: user may say `--override-plan` to discard plan defaults and
   fall through to Phase 0B (RELEASE_BACKLOG discovery).

**Skip Phase 0B entirely** when plan-driven discovery succeeds.

---

### Phase 0B: RELEASE_BACKLOG Discovery (when plan_path is absent)

Used when no approved task creation plan exists. Picks the highest-priority missing package.

1. **Active package via ranker**:
   ```bash
   python3 scripts/tasks/next_tasks.py
   ```
   Capture the `Next package: [id]` line. If absent, fall back to the `Next release: [V]` line.

2. **Read `requirements_tasks/RELEASE_BACKLOG.md`** — parse YAML frontmatter. Filter `packages[]`
   to those matching the active release version. Preserve list order (= global priority).

3. **Classify each package**:
   - Skip if `source.type` is `flow` or `standalone` (flow-derived packages need `requ-derive-from-flow` first).
   - For `source.type: requirement`, grep **only functional tasks**:
     ```bash
     grep -rl 'target_package: "[pkg-id]"' requirements_tasks/functional/ | xargs grep -l 'type: impl'
     ```
     The package is **missing** if *zero non-terminal* impl tasks exist (terminal = completed /
     cancelled / superseded / deprecated). A blocked task still counts as existing.

4. **Pick the candidate**:
   - Sort missing packages by `priority_within_source` ascending (treat `null` as 999); tiebreak by backlog list position.
   - If no missing packages for the active release: ask user "All packages for release [V] have impl tasks. Proceed with next release?" and re-run for the next version.
   - If nothing found: stop and tell the user.

5. **Resolve to requirement path**:
   - Read `requirements_tasks/_meta/id_registry.md` for `source.ref` (REQ-ID) → path mapping.
   - If `source.scope` mentions `feat_*` folders, narrow to the matching feature's `requirements.md`.
   - If multiple candidates remain, list them and ask the user to pick.

6. **Confirm with user**:
   ```
   Proposed next impl task:
     Package: [pkg-id]  (priority [N])
     Source:  [REQ-ID] — [source.scope]
     Requirement: [resolved path]

   Proceed? (yes / pick another / stop)
   ```

7. On confirmation, continue into Phase 1 with the resolved path.

#### propose_after.py interaction when plan entry exists (Phase 0A)

- **Do NOT call `propose_after.py`** for full dependency detection. The plan's `after:`
  list is the authoritative cross-task dependency source; re-deriving risks false additions.
- **Do call `propose_after.py`** for the `requirement_then_implementation` heuristic only:
  ```bash
  python3 scripts/tasks/propose_after.py \
    --path "[new task folder path]" \
    --metadata '{"type":"impl","parent_requirement":"[REQ-ID]","target_package":"[pkg]"}' \
    --heuristic requirement_then_implementation
  ```
  (If `--heuristic` flag is not implemented, run normally and filter to lines whose `reason`
  contains "requirement" — discard the rest.)
- **Merge**: start with plan's `after:` list; append any propose_after results whose TASK-ID
  is not already in the plan's list.
- Write merged list to goal.md `after:` field.

When no plan entry exists (Phase 0B): call `propose_after.py` normally with full heuristic set.

---

## Phase 1: Understand Requirement

### 1.1 Read Requirement
Read the requirement file:
- Extract Goal / User Story
- Extract Acceptance Criteria
- Note dependencies

### 1.2 Gather Additional Details
Ask user for supplementary info:
- Visual design / UI sketches
- Business rules not documented
- Edge cases

(Details supplement, don't replace, the requirement.)

---

## Phase 2: Scope Estimation (Quick Scan)

### 2.1 Identify Affected Areas
Questions: which layers, how many files, existing patterns, obvious dependencies?

### 2.2 Automated Structural Check (deterministic — no agent)

Replaces the old LLM Quick-Explore-Agent estimate, which disagreed across runs on the same
input. Derive the file count **deterministically** from the proposed scope instead.

1. Assemble the candidate file set from two deterministic sources:
   - **Explicit paths**: every concrete `lib/…`, `test/…`, `integration_test/…` path named in
     the requirement scope, plan entry (`implementation_notes`), or user-provided details.
   - **Scope globs**: glob patterns for the affected layer + feature (e.g.
     `lib/features/<feat>/domain/**`, `test/features/<feat>/**`).
2. Count distinct existing files matched (new files the task will *create* are added to this count
   from the explicit-path list, since `git ls-files` only sees tracked files):
   ```bash
   # SCOPE_GLOBS / SCOPE_PATHS: space-separated patterns + explicit paths from step 1.
   git ls-files -- $SCOPE_GLOBS $SCOPE_PATHS | sort -u | wc -l
   ```
   Add the count of explicit new-file paths not yet tracked. The result is `file_count`.
3. Record `file_count` and the path/glob list in the protocol — this is the reproducible basis
   for the tier in 2.3, replacing the agent's guess.

When a plan entry is active, its `layer` + `implementation_notes` seed the path/glob list; when no
plan entry exists, derive globs from the requirement's affected layer(s).

### 2.3 Estimate Size (two co-equal signals)

The tier is driven by **two co-equal signals** — the structural `file_count` from 2.2 (**S1, file
volume**) and `skill_chain_depth` (heavy-skill invocations the task's execution chain will make:
e.g. `code-simple`/`code-complex` + optional `code-test` + `verify-quality` + `task-complete`).
**Either signal crossing its threshold triggers the higher tier** — take the max.

| Size | File count | Skill-chain depth | Action |
|------|------------|-------------------|--------|
| **Small** | 1-3 files, single layer | ≤ 2 | Single task |
| **Medium** | 4-8 files, 1-2 layers | 3 | Single task (may split later) |
| **Large** | 8+ files, multi-layer | ≥ 4 | Split NOW |

(At execution time, `claude-route` picks `code-simple` vs `code-complex` automatically — no need to decide here.)

Carry both numbers forward: `file_count` informs `expected_tool_calls` and the chosen depth becomes
`skill_chain_depth` in the goal.md frontmatter (Phase 3.3, AC-01).

**Plan-driven mode escalation (AC-15)**: If a plan entry is active and file analysis reveals the task is significantly larger than the plan estimated (e.g., plan effort is `S` or `M` but analysis estimates `Large` — 8+ files, multi-layer → Split NOW):
- **Interactive mode**: ask user — "Plan estimated [effort] but file analysis shows Large (8+ files). Split this task? Promote to Opus? Override?"
- **Automated mode**: write `question.md` in the task's `plans_and_protocols/` folder and stop. Do not create the task.

**Market research backing**: Note whether the feature has market research support (`requirements_market_research/*/findings.md`) or explicitly lacks it.

---

## Phase 3: Create Task

### 3.1 Location
`[requirement_path]/tasks/[YYYY-MM-DD]_impl_[name]/` — match sibling dates if they set ordering.

### 3.2 Structure
```
[path]/tasks/[date]_impl_[name]/
├── goal.md
└── plans_and_protocols/
```

### 3.2.5 Dependency Proposal (`after:` field)

Before writing goal.md, run propose_after.py to detect dependencies:

```bash
python3 scripts/tasks/propose_after.py \
  --path "[new task folder path]" \
  --metadata '{"type":"impl","parent_requirement":"[REQ-ID]","target_package":"[pkg]"}'
```

The script outputs one `TASK-ID   reason` line per proposal (exits 0 always).

- **No output**: skip silently; write `after: []`.
- **Script fails**: warn ("Dependency proposal failed, continuing without proposals."); write `after: []`.
- **Has proposals**:
  - **Interactive mode**: Present to user:
    ```
    Proposed after:
      TASK-XXX — reason: same package, earlier step
      TASK-YYY — reason: same scope, earlier layer
    Accept / drop any / add others?
    ```
    Write confirmed list to `after:`. For each confirmed entry, add to `related_tasks_refs`: `{path_to_goal_md, reason: "predecessor — executor should read what was delivered"}`.
  - **Automated mode**: see table in the Automated Mode section below. Add auto-accepted entries to `related_tasks_refs`.

### 3.3 Write goal.md

Gather values:

**a) Task ID** — regenerate registry, then allocate atomically:
```bash
python3 scripts/artifacts/generate_id_registry.py --requirements
python3 scripts/tasks/allocate_task_id.py --req-id [REQ-ID] --req-path [path-to-requirement-folder]
```
After writing goal.md, delete the reserve marker: `rm [req-path]/tasks/.reserve-[TASK-ID]`.
If the script exits non-zero, surface stderr and stop.

**b) requirements_version commit**:
```bash
git log -1 --format=%h -- requirements_tasks/[path]/requirements.md
```

**c) covers**: Read parent requirements.md for `trackable_items`. Ask user which ACs/sections this task covers. If absent, leave empty.

**d) Priority / effort**: inherit `urgency`, `urgency_reason`, `impact`, `impact_reason` from parent. Estimate `effort` from Phase 2.

**e) release_description**: draft a suggestion (max 25 words, English, user-benefit), user confirms or skips.

**f) related_tasks**: emit `## Related Tasks` section after `## Dependencies` if `related_tasks_refs` is non-empty (built from Phase 3.2.5 confirmed `after:` entries). One table row per entry: relative path to goal.md + one-sentence reason. Omit entirely when list is empty.

**g) opus_recommended**: evaluate after effort is known. The tier feeding `effort` now comes from
the deterministic structural check + skill-chain depth (Phase 2.3) — only the upstream signal source
changed; the mapping below is preserved. Set `true` (with inline reason) if any signal matches;
XS/S always → `false`:

| Signal | Result |
|---|---|
| `effort: XS` or `S` | `false` (override) |
| `effort: XL` | `true # reason: XL effort — architectural planning warranted` |
| Security/privacy domain | `true # reason: security/privacy domain` |
| `urgency ≥ 4` AND `impact ≥ 4` | `true # reason: highest-stakes task` |
| Default | `false` |

**g.1) AC-07 — iterative-fix-loop escalation (REQ-PROC-001 AC-07)**: runs *in addition to*
the table above and can override the `XS/S → false` result. Splitting the task is the preferred
and required first response; Opus escalation is the fallback only when the loop is inherent.

1. **Detect the iterative-fix loop (S4)**: true when the task's scope touches `lib/` (and/or
   `test/`, `integration_test/`) AND its execution chain will exercise `verify-quality`. Every
   code task routed to `code-simple`/`code-complex`/`code-test` does, since `verify-quality`
   is mandatory before completion. If S4 is false, skip AC-07.
2. **Detect closed vs open scope** from goal.md `## Scope` / `### In Scope`:
   - **Closed**: names ≤ 3 specific `lib/` files as concrete paths (not globs/patterns).
   - **Open**: scope is pattern-defined (globs, "all widgets under X", a whole layer/feature)
     OR names > 3 specific `lib/` files.
3. **Apply**:
   - **Closed (≤ 3 named lib/ files)**: no AC-07 escalation — keep `opus_recommended` as the
     table decided (typically `false`). Do NOT override.
   - **Open OR > 3 files**: apply the **splitting-first principle**. Splitting so each child has
     a closed ≤ 3-file scope is the preferred and required first response.
     - **Interactive mode**: prompt — "Iterative-fix loop task with [open scope | N>3 lib/ files].
       Split into ≤ 3-file child tasks (preferred), or is the loop inherent so it cannot be split?"
       Only when the user confirms splitting is infeasible: set
       `opus_recommended: true # reason: REQ-PROC-001 AC-07 — inherent iterative-fix loop on open/wide lib/ scope`.
     - **Automated mode**: log to protocol.md that splitting is the required first response and
       prefer creating ≤ 3-file child tasks. Set `opus_recommended: true` with the AC-07 reason
       only when the loop is genuinely indivisible (e.g. a single widget tree that cannot be
       split). Record the split-vs-escalate decision and its justification in protocol.md.

   **Auto-escalation without first considering splitting is forbidden** — the splitting-first
   step MUST precede any AC-07 `opus_recommended: true`.

**h) sizing signals (AC-01)**: declare at least one of `expected_tool_calls` (from `file_count` plus
expected Bash/Read/Edit volume) or `skill_chain_depth` (from Phase 2.3). Then **apply the Sizing
Gate** (see below) before writing goal.md.

**Sizing Gate (REQ-PROC-001 AC-03)**: when `expected_tool_calls > 60` OR `skill_chain_depth >= 4`,
the new goal.md MUST satisfy at least one end state — else the gate fails:
1. `opus_recommended: true`, or
2. the task has been split into child tasks (declared in goal.md / `after:` chain), or
3. `goal.md` body contains a **named fan-out plan** describing which agents are spawned, what each
   distills, and what it returns.

On failure: **interactive mode** — warn, show the three end states, ask which to apply before writing
goal.md; **automated mode** (`CLAUDE_AUTOMATED_MODE=1`) — block: do not write the high-volume goal.md
as-is; split into child tasks or add the named fan-out plan (prefer splitting).

**Template**:
```markdown
---
task_id: TASK-[CATEGORY]-[REQ_NUM]-[TASK_NUM]
type: impl | bugfix
parent_requirement: REQ-[CATEGORY]-[REQ_NUM]
urgency: [0-5]
urgency_reason: U[0-5]-[CODE]
impact: [0-5]
impact_reason: I[0-5]-[CODE]
status: pending
effort: XS | S | M | L | XL
created: [YYYY-MM-DD]
expected_tool_calls: [int]   # AC-01 (S1): estimated Bash + Read + Edit calls at runtime. Declare this OR skill_chain_depth — at least one is required.
skill_chain_depth: [int]     # AC-01: count of heavy-skill invocations (Phase 2.3). Declare this OR expected_tool_calls.
after: []             # task IDs this task must wait for (next_tasks.py checks status dynamically)
awaiting: []          # EXTERNAL blockers ONLY — NEVER put task IDs here
awaiting_note: ""     # required when awaiting is non-empty
covers:
  acceptance_criteria: []
  sections: []
# release_chunk: added by 3.3b if parent has it
scope_description: "Brief summary of what this task implements"
release_description: ""  # max 15 words, English, user-benefit; required for impl tasks
opus_recommended: false  # true: XL effort, security/privacy, urgency≥4+impact≥4
requirements_version:
  commit: [7-char hash]
  file: ../requirements.md
---

# Implementation Task: [Name]

## Requirement Reference
- **Requirement**: [relative path to requirements.md]
- **Status**: Not Started

## Goal
[Copy the atomic goal/user story from the requirement]

## Scope Overview
[Brief summary from Phase 2 scan — NOT concrete code changes]

**Affected Layers**: [Domain / Data / Presentation]
**Estimated Files**: ~[X] files
**Patterns to Follow**: [Existing similar implementation]

## Additional Details
[User-provided supplements]

### Visual Design
[UI specs, colors, spacing]

### Business Rules
[Edge cases, validation rules]

### Other Notes
[Extra context]

## Acceptance Criteria
[Copy from requirement]

## Dependencies
[From requirement + discovered during scan]

## Related Tasks
<!-- Omit this section if related_tasks_refs is empty -->

| Task | Reason |
|------|--------|
| [TASK-XXX](../path/to/goal.md) | Predecessor — executor should read what was delivered |

---

**Note**: This task describes WHAT to implement, not HOW. The implementation plan is created fresh at execution time.
```

### 3.3b Release Chunk Inheritance (`release_chunk`)

1. Read parent requirement YAML for `release_chunk`.
2. If present → copy to task's YAML (after `covers`, before `target_package`). Automatic, no prompt.
3. If absent → omit the field.

### 3.4 Package Inheritance (`target_package`)

**Skip entirely** (leave absent) if goal.md has `source_gap:` or `verification_task: true`.

Otherwise, resolve in priority order:

1. **Phase 0 package known** (zero-parameter mode resolved a specific package): write it directly as `target_package` without scanning ACs or prompting. Log: `target_package: "[pkg]" (from Phase 0)`.

2. **Phase 0 package unknown** (requirement path was provided explicitly):
   a. Read parent requirement's `trackable_items` → extract `target_package` from each AC/section in `covers`.
   b. **All covered items assigned to the same package**: inherit that package. Log: `target_package: "[pkg]" (from covers ACs)`.
   c. **Mixed packages across covered items**: prompt user to confirm which package applies.
   d. **covers is empty OR items have no package assignment**: prompt user with available packages from `RELEASE_BACKLOG.md` grouped by version.
   e. **RELEASE_BACKLOG.md missing**: warn and skip (don't fail).

3. Write `target_package` after the `covers` field in every goal.md. Omit entirely only if user explicitly skipped.

**Split scenario (multiple goal.md files created)**: After writing all goal.md files, run:
```bash
python3 scripts/requirements/sync_task_packages.py --requirement [req-path] --dry-run
```
If any task shows `absent →`, run `--apply` immediately and log which tasks were fixed. This acts as a safety net for split tasks where Phase 3.4 may not have been applied consistently.

---

## Phase 4: Verify & Commit

### 4.1 Present
**Plan-driven mode**: skip this step — the plan was reviewed and approved at the planning level (AC-15). Proceed directly to Phase 4.2.

Show goal.md and ask:
- Does this capture everything needed?
- Scope estimate reasonable?
- Split required?

### 4.2 Commit
Use `claude-commit` skill to stage and commit the new task folder.

---

## Phase 6: Plan Conformance Check (skip if no plan_path)

After the commit in Phase 4.2, if `plan_path` was set (from Phase 0 plan-mode override):

```bash
python3 scripts/tasks/check_task_against_plan.py \
  --task [task_id] \
  --plan [plan_path]
```

**Exit codes**:
- **Exit 0** — task conforms to plan entry. Proceed silently.
- **Exit 1** — mismatch detected (wrong ACs, wrong effort tier, wrong layer, wrong package).
  - Interactive mode: show the diff output to the user and ask whether to proceed or fix.
  - Automated mode: write `question.md` in the orchestration task's folder:
    ```
    Plan conformance check failed for [task_id].
    Plan: [plan_path]
    Diff:
    [paste check_task_against_plan.py stderr here]
    ```
    Stop (do not call task-complete on the orchestration task).
- **Exit 2** — no plan entry found for this task's package. Skip silently (off-plan task).

**Conformance rules** (what the script checks):
- `target_package`: exact match required
- `covers_acs`: set equality (order irrelevant)
- `effort`: ±1 size acceptable (XS↔S, S↔M, M↔L, L↔XL) — flagged but does NOT block
- `layer`: exact match required

---

## Output
"Implementation task created at [path]. Run `Do [TASK-ID]` to execute it."

---

## Key Principles

1. **No concrete code changes** — WHAT, not HOW.
2. **Fresh plans at execution** — plans reflect current codebase.
3. **Enough context for sizing** — quick scan suffices.
4. **Split early if large**.
5. **Supplement, don't duplicate** — additional details complement requirement.
6. **Preserve task order** — use sibling date prefix when relevant.
7. **Propose dependencies, don't assume** — user confirms `after:` before it's written.

---

## Automated Mode (CLAUDE_AUTOMATED_MODE=1)

When both `CLAUDE_AUTOMATED_MODE=1` and `automation/.automated_mode` exist, replace interactive checkpoints with auto-accept behavior:

| Checkpoint | Interactive behavior | Automated behavior |
|---|---|---|
| Phase 0.6 — confirm candidate | Ask user to confirm | Auto-accept if heuristic is unambiguous (single candidate, source.type=requirement). Write decision to protocol.md. |
| Phase 0 plan-mode — package vs. plan mismatch | Show mismatch, ask user to confirm or override | Write `question.md` describing mismatch, stop |
| Phase 1.2 — additional details | Ask user | Skip. Proceed with requirement only. |
| Phase 3.2.5 — dependency proposal | Run propose_after.py; present table, ask accept/drop | Run propose_after.py. Auto-accept proposals whose reason contains "same-package"; skip all others silently. Log accepted `after:` list to protocol.md with reasons. |
| Phase 3.3e — release_description | Draft + ask user to confirm | Auto-generate from requirement goal (max 15 words). Log to protocol.md. |
| Phase 4.1 — present goal.md for review | Ask user if correct | Skip. Proceed to commit. |
| Phase 6 — plan conformance exit 1 | Show diff, ask user to proceed or fix | Write `question.md` with diff, stop |
| Redirect (standalone + uncovered ACs) | Ask user or redirect | Always redirect; never auto-override |
| Stale plan check — hash mismatch | Warn, ask proceed/abort/re-plan | Write `question.md` describing mismatch; stop |
| Phase 2.3 — plan-driven size mismatch | Ask user split/promote/override | Write `question.md` in plans_and_protocols/; stop |
| Sizing Gate (Phase 3.3h, AC-03) — high-volume task, no end state | Warn, ask which end state to apply | Block: split into child tasks or add a named fan-out plan (prefer splitting); do not write the high-volume goal.md as-is |
| AC-07 (Phase 3.3g.1) — iterative-fix loop on open/wide lib/ scope | Prompt split vs. inherent-loop, escalate only if inherent | Log splitting-first in protocol.md, prefer ≤ 3-file child tasks; set `opus_recommended: true` (AC-07 reason) only when the loop is indivisible |

**When auto-accept is NOT safe** — use `pending_feedback` instead (see `claude-automated-mode` skill for the question.md procedure):
- Phase 0 finds zero matching candidates (no package to pick)
- Phase 0 finds multiple equally-prioritized packages with ambiguous layer classification
- Phase 2.3 estimates size as Large and suggests splitting
- Script `allocate_task_id.py` exits non-zero
- `parse_task_creation_plan.py` returns non-zero or package not found in plan
- Phase 6 `check_task_against_plan.py` exits 1 (conformance mismatch)
- Stale plan check (step 3.5): plan's `requirements_version.commit` ≠ current requirements.md hash
- Phase 2.3 plan-driven mismatch: file analysis reveals task significantly larger than plan estimated

**After completing** (in automated mode only):
1. Write a summary to `plans_and_protocols/protocol.md`:
   ```
   # Protocol: [date]
   Package: [pkg-id]
   Impl task created: [TASK-ID] at [path]
   after: [list] — reasons: [one line per entry]
   release_description: "[text]"
   Automated: yes
   ```
2. Call `task-complete` skill on the **orchestration task** (the goal.md that this session was routed to — not the newly created impl task). This closes the orchestration task so the bootstrap can create the next one.
