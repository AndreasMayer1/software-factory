---
name: release-begin-impl
description: Begin implementation of a release: verify scope, create holistic task plan, activate release, create first orchestration task
tools: "*"
model: inherit
---

> This skill covers scope verification and planning only. Task creation runs in autorun.
> `/release-begin-impl-finalize` handles post-creation review.
> This skill never reads a feature's requirements.md in the orchestrator's main context —
> only Phase 2 epic agents and the Phase 2c per-requirement `task-derive-from-requ` agents do.

## Inputs

- `release_version`: e.g. "0.0.1" (required)
- `task_path`: path to the release prep explore task folder (for writing questions/ and task_creation_plan.md)

## Decision Domains (Read This Before Anything Else)

Three kinds of questions surface during release prep. Each has a designated
phase. Mixing them up wastes user time and burns context.

| Domain | Examples | Where it belongs |
|--------|----------|------------------|
| Scope — does X belong in this release? | "Transfer Notifications in 0.0.1?", "Move AC-28–36 to 0.2.0?" | Phase 2 ONLY. Once Phase 2 ends, scope is frozen for this iteration. |
| Coverage — does in-scope work have requirements + impl tasks? | "Does feat_pairing have an impl task?" | Phase 2c Planner. Agents create tasks or flag blockers, never scope questions. |
| Investigation — answer obtainable by reading more files? | "Are these 2 open analyze tasks still relevant?", "Does this task cover AC-28?" | Inside the agent. NEVER escalate to user. Read the files first. |

Phase 2b and Phase 2c must NOT contain Scope-domain questions. If a Phase 2c
agent identifies scope ambiguity, it flags it as a Phase 2 reopener — the
orchestrator re-runs Phase 2 for that epic before the plan can be finalized.

## Phase 0 — Bootstrap (you, main context)

1. Ask user: "Are you preparing by package ID or by release version?"
   - By package: ask for package ID (e.g. `PKG-0.0.1-core`)
   - By release: ask for release version (e.g. `0.0.1`)

2. **If by package**:
   Run `python3 scripts/artifacts/generate_status_overview.py --package [pkg_id]`
   Read `requirements_tasks/RELEASE_BACKLOG.md` — extract package `name`, `description`, version scope.

   **If by release**:
   Run `python3 scripts/artifacts/generate_status_overview.py --release [release_version]`
   Read `requirements_tasks/RELEASES.md` — extract `scope_boundaries.includes` and `packages:` list.

3. Read `requirements_tasks/STATUS_NEXT_RELEASE.md` — extract all requirements targeting this package/release.
4. Build work list: `(req_id, path, status, has_impl_tasks)` — split into epics vs. features.
5. Record `explore_task_id` (the TASK-ID from this task's goal.md frontmatter — needed in Phase 6).
6. **Check for in-progress prior session**: scan the release_preparation tasks folder for an explore task
   with `target_release` matching the current release AND `status: in_progress`.
   If found, offer: "A prior release-begin-impl session is in progress ([TASK-ID]).
   Resume it, or abandon and start fresh?"
   - Resume: read existing `questions/` folder, count `iteration_NN/` folders, set `current_iteration` accordingly, proceed.
   - Abandon: set prior task `status: cancelled`, start fresh as below.
7. Determine current iteration: count `[task_path]/questions/iteration_NN/` folders; set `current_iteration = count + 1` (zero-padded, e.g. `01`).
8. Create `[task_path]/questions/iteration_[NN]/` folder.

## Phase 1 — Scope Coverage Check (inline or 1 agent)

**First**: call `python3 scripts/util/should_use_agents.py --release [version]` (or `--package [pkg_id]`).
- Result `orchestrator_direct` (≤30KB and ≤5 files): run the checks below inline.
- Result `agents_required`: spawn 1 agent with the same instructions.

**Checks** (3 checks total):

1. **Package coverage**: every package in the release's `packages:` array has ≥1 requirement assigned via `target_package`.
2. **Includes coverage**: only if `scope_boundaries.includes` is non-empty. Each item maps to ≥1 requirement. If `includes` is empty: valid — `packages:` IS the scope. Note this explicitly in output (do NOT say "nothing to check").
3. **Contradiction check**: any package whose theme appears in `scope_boundaries.excludes` → surface as explicit contradiction.

Files to read (max 3):
- `requirements_tasks/RELEASES.md`
- `requirements_tasks/STATUS_NEXT_RELEASE.md`
- `requirements_tasks/_meta/id_registry.md`

Output: `[task_path]/questions/iteration_[NN]/phase_1/scope_gaps.md`

Output quality standard: file must begin with `## Summary for User` (≤3 bullets + numbered open questions).

## Phase 2 — Epic Agents (spawn 1 per epic, in parallel)

Each agent reads ONLY (max 5 files):
- The epic's `requirements.md`
- Its direct child feature `requirements.md` files
- `requirements_tasks/RELEASES.md`

Each agent checks: do release-scoped trackable items have feature-level requirements?
- If missing feature: write draft requirement content + flag gap.

Output per agent: `[task_path]/questions/iteration_[NN]/phase_2/epic_[REQ_ID]_findings.md`

Each findings file MUST start with a `## Summary for User` section containing:
- 2-3 bullet points max summarizing what was found
- A `### Open Questions` subsection listing decisions the user must make, numbered

**USER APPROVAL GATE**: After Phase 2 completes, tell the user the findings files are ready
and list their full paths under `[task_path]/questions/iteration_[NN]/phase_2/`.
Instruct the user to read the files directly and answer the open questions. Do NOT read the files yourself.
Wait for the user's answers before proceeding to Phase 2b.

## Phase 2b — Remediation (you, main context + spawned agents)

Once the user signals they have answered the Phase 2 questions, read and act on those answers.

### Step 1 — Read user answers (orchestrator reads phase_2/ files only)

Read all files under `[task_path]/questions/iteration_[NN]/phase_2/`. Extract user answers
and dispatch remediation work. Do NOT read underlying requirement files.

### Step 2 — Classify each gap and dispatch agents

For each gap or user-approved action, spawn one agent per work item (parallel where independent).
Pass each agent a self-contained prompt with the exact target file path and draft content.

Work item types:
- **Missing requirement (user approved)**: agent writes new `requirements.md` to given path with draft content.
- **Scope boundary update**: agent updates only the relevant section of `requirements_tasks/RELEASES.md`.
- **Requirement metadata fix**: agent fixes frontmatter of the specific file(s).
- **No action (user said skip)**: log it, no agent spawned.

Each remediation agent reads max 5 files and writes to a pre-assigned output path:
`[task_path]/questions/iteration_[NN]/phase_2b/gap_N/output.md`

If an agent hits a blocker it cannot resolve, it writes questions to
`[task_path]/questions/iteration_[NN]/phase_2b/[topic]_questions.md` and terminates.

### Step 3 — Wait for all agents to complete

Scan for output files at `[task_path]/questions/iteration_[NN]/phase_2b/gap_N/output.md`.
An agent is done when its output file exists. (No agent-ID tracking needed — output-file polling only.)

### Step 4 — Handle blockers and open questions

Check for unanswered question files under `[task_path]/questions/iteration_[NN]/phase_2b/`
(exclude `gap_N/output.md` files).

If unanswered files exist: list their paths to the user, wait for answers.
Once answered: spawn a fresh agent with the answered question + original context. Do NOT resume by agent ID.

Repeat until no open question files remain.

### Step 5 — Proceed to Phase 2c

Only when all phase_2b question files are answered (or none exist): proceed.

## Phase 2c — Task Creation Planner (delegation orchestrator)

Phase 2c does NOT decompose requirements itself. Per REQ-PROC-035 SEC-05 and
REQ-PROC-058 AC-14 it delegates per-requirement decomposition to
`task-derive-from-requ` (one agent per in-scope feature requirement), then
assembles the per-requirement plans into the release plan and layers
release-level concerns on top.

### Step 1 — Identify in-scope feature requirements

Read `requirements_tasks/STATUS_NEXT_RELEASE.md` (already gathered in Phase 0).
Extract every requirement targeted at this release whose `requirements.md` has
at least one acceptance criterion. Epic requirements (no own ACs) are skipped —
their child features are the delegation targets. Per REQ-PROC-035 SEC-02 epics
are exempt from impl task coverage.

For each surviving REQ-ID, capture: `req_id`, `req_path`,
`requirements_version` (run `git log -1 --format=%h -- <req_path>`),
`target_package`.

Write the work list to `[task_path]/questions/iteration_[NN]/phase_2c/work_list.md`.

### Step 2 — Spawn per-requirement decomposition agents

For each work-list entry, spawn one `task-derive-from-requ` agent.

**Default: serial dispatch.** Each agent is heavy (Phase 1.5 cross-ref gate may
itself spawn a subagent; full mode can exceed 5 minutes). Serial dispatch keeps
a single 4:30 heartbeat sufficient (CLAUDE.md §2). Large-release escape hatch:
if work-list size > 8, dispatch the first 2 in parallel as a smoke test; if
either stalls (no output file after 10 min), fall back to serial for the rest.

Each agent must be spawned with `run_in_background: true` and the main session
starts a 4:30 heartbeat loop after the first long-running dispatch:

```
/loop 4m30s Output the single word Okay and nothing else. Do not run any tools. Do not invoke any skills.
```

Stop the heartbeat when the last agent completes.

**Output convention**: each per-requirement plan is written to
`[task_path]/per_requirement_plans/<REQ-ID>/plan.md`. The orchestrator polls
for the presence of `plan.md` for each REQ-ID (output-file polling — no
agent-ID tracking).

**Spawn prompt template** (replace bracketed values per requirement):

```
You are invoking the task-derive-from-requ skill on a single requirement on
behalf of release-begin-impl Phase 2c.

Inputs:
  requirement_path: [req_path]
  requirements_version: [commit_hash]
  release: [release_version]
  target_package: [target_package]
  output_plan_path: [task_path]/per_requirement_plans/[REQ-ID]/plan.md

Run task-derive-from-requ in FULL mode against the requirement at
[req_path]. Override the default plan output location: write the plan to
[output_plan_path] in the unified format (REQ-PROC-058 SEC-04). Do NOT write
to your own task's plans_and_protocols/ — this invocation is on behalf of a
release-level planner, not your own task.

Required behaviors:
  - Phase 1.5 cross-reference completeness gate MUST run. If a residual gap
    remains after Apply, write question.md per the automated-mode pause
    procedure and terminate.
  - Coverage matrix MUST be 100% (every AC of [REQ-ID] mapped to at least one
    plan entry). Zero-coverage AC is a blocking error.
  - Verification task MUST be present per AC-02.
  - Sizing signals (S1-S4) MUST be computed per AC-03; opus_recommended set
    from S1-S4 composition.
  - Already-implemented ACs (detect via
    scripts/requirements/check_requirement_implementation.py --requirement
    [REQ-ID]) → set task_type: verify.
  - target_package on every plan entry: [target_package] unless the AC's own
    target_package overrides at AC-level.

Do NOT spawn `task-create-code` / `task-create` — Phase 5 of task-derive-from-requ
is skipped here. The release-begin-impl orchestrator owns task creation via the
self-perpetuating orchestration chain (REQ-PROC-035 SEC-05).

When the per-requirement plan is written and validated, exit. The output file
itself signals completion.

If an irrecoverable error occurs, write a failure note to
[task_path]/per_requirement_plans/[REQ-ID]/FAILED.md with the reason and
terminate. Do NOT write plan.md on failure.
```

### Step 3 — Wait for all per-requirement agents to complete

Output-file polling. An agent is done when its
`per_requirement_plans/<REQ-ID>/plan.md` OR `FAILED.md` exists.

When the last agent completes, omit the next `ScheduleWakeup` call to end the
heartbeat loop.

If any `FAILED.md` exists: the affected REQ-ID's decomposition is incomplete.
List the failures, surface them to the user as a Phase 2c blocker (interactive)
or pause via question.md (automated). Do not proceed to Step 4 until every
work-list entry has a `plan.md`.

### Step 4 — Assemble release plan

Read every `per_requirement_plans/<REQ-ID>/plan.md`. Produce
`[task_path]/task_creation_plan.md` in the unified format (REQ-PROC-058 SEC-04).

The assembled release plan contains:

- YAML frontmatter (release-level): `plan_id`, `release`, `created`,
  `status: draft`, `explore_task`, `per_requirement_plans` (list of REQ-ID →
  path), `total_tasks`
- `## Layer Dependency Rules` section
- `## Execution Order` section — ordered list of packages (release-level
  concern, see Step 5)
- `## Architecture Notes` section
- `## Per-Requirement Plans` index section — bullet list of REQ-ID →
  `per_requirement_plans/<REQ-ID>/plan.md`
- `## Planned Tasks` section — entries concatenated from every per-requirement
  plan, regrouped by `target_package` under `### PKG-...` headings. Each entry
  carries the same YAML block its source plan produced (`task_name`,
  `req_path`, `requirements_version`, `covers_acs`, `effort`, `layer`,
  `after`, `task_type`, `opus_recommended`, `target_package`,
  `implementation_notes`). The per-entry rationale prose is preserved.
- `## Coverage Matrix` section — union of all per-requirement coverage matrices,
  grouped by REQ-ID then by package

Do NOT recompute coverage matrices, sizing, or verification tasks — they are
authoritative from the per-requirement plans (REQ-PROC-058 AC-15
"compute once, trust downstream").

### Step 5 — Add release-level concerns

Three release-level passes on top of the assembled plan:

**5a. Package execution ordering.** Determine the order in which packages
should be materialized. Sources of truth:
- `RELEASE_BACKLOG.md` package definitions (look for explicit ordering hints)
- Cross-package `after:` edges in plan entries (a package containing a task
  whose `after:` references a task in another package must come after that
  package)
- Layer dependency: infrastructure packages before consumer packages

Write the ordered package list to `## Execution Order`.

**5b. Cross-requirement after-chain reconciliation.** Per-requirement plans
only see their own ACs; the previous monolithic agent had implicit cross-
visibility. Recover that here:

1. For each plan entry whose `implementation_notes` (or `task_name`) explicitly
   names a concept owned by another in-scope requirement, locate the latest
   covering task in that requirement's plan and inject it into this entry's
   `after:` list.
2. For each requirement whose frontmatter `after:` references another in-scope
   REQ-ID, add cross-requirement edges from the dependent requirement's "first
   task" to the depended-on requirement's "verification task" (logical
   ordering: cannot start consuming a requirement before it is verified-ready).
3. Where the heuristic is ambiguous (concept name might belong to multiple
   requirements), leave a `# cross_ref_note: ambiguous — review needed` comment
   on the entry and list the entry in `## Cross-Requirement Notes` for Phase 5
   user review.

This step is deliberately conservative — false positives are easier for the
developer to spot at Phase 5 than missing edges discovered mid-implementation.

**5c. Release scope completeness re-check.** Compare:
- Set of `target_package` values across all plan entries
- Set of packages in the release's `packages:` list

Any package with zero plan entries is a scope-coverage gap. This should not
happen if Phase 1 passed, but the assembled view may surface gaps that
single-requirement Phase 1 checks missed (e.g., a package whose only
requirement turned out to have all ACs marked `task_type: verify`).

Gaps go to `## Scope Coverage Re-check` in the release plan. A non-empty
section is a Phase 2 reopener (see below).

### Step 6 — Phase 2 reopener handling

Phase 2c must NOT escalate scope questions to the user directly. If Step 5c
finds gaps, or if a per-requirement agent's plan flags scope ambiguity, write a
reopener note to
`[task_path]/questions/iteration_[NN]/phase_2c_reopeners.md`. The orchestrator
re-runs Phase 2 for the flagged epic before finalizing.

### Output

- `[task_path]/task_creation_plan.md` (assembled release plan)
- `[task_path]/per_requirement_plans/<REQ-ID>/plan.md` (one per in-scope
  feature requirement)
- Optional: `[task_path]/questions/iteration_[NN]/phase_2c_reopeners.md`

## Phase 5 — User Gate (you)

1. Run: `python3 scripts/tasks/summarize_plan.py --plan [task_path]/task_creation_plan.md`
2. Show the 1-page summary output directly to the user.
3. Also provide paths to:
   - Full release plan: `[task_path]/task_creation_plan.md`
   - Per-requirement plans (one per in-scope requirement, contains the per-requirement
     coverage matrix produced by `task-derive-from-requ`):
     `[task_path]/per_requirement_plans/<REQ-ID>/plan.md` — list each one explicitly
   - Cross-Requirement Notes section of the release plan (if non-empty) — items
     flagged for user review by Phase 2c Step 5b
   - All findings files: `[task_path]/questions/iteration_[NN]/`
4. Ask the user to read and approve. The developer reviews per-requirement coverage
   matrices via the per-requirement plan paths (Phase 2c does not duplicate them
   into the release plan beyond the assembled `## Coverage Matrix` section).
5. Wait. Do NOT proceed until the user explicitly says "approved" (or equivalent confirmation).

If user requests revisions: implement or re-run relevant phases as needed, then return to Phase 5.

## Phase 6 — Activate + Hand Off (you)

Only proceed after the user has said "approved" in Phase 5.

### 6.0 — Pre-checks (no mutations)

- Confirm `explore_task_id` is set (recorded in Phase 0 step 5).
- Confirm `[task_path]/task_creation_plan.md` exists.

### 6.1 — Pre-check: dry-run

Run:
```
python3 scripts/tasks/create_orchestration_task.py --dry-run --after-task [explore_task_id]
```
- Exit 0: proceed.
- Non-zero: show stderr to user, stop. Do not proceed to mutations.

### 6.2 — Mutation: activate release

**If by release**:
- Read `requirements_tasks/RELEASES.md`
- Update `status: planned` → `status: active` for the target release.
- Do NOT commit yet.

**If by package**:
- Read `requirements_tasks/RELEASE_BACKLOG.md`
- Update `status: planned` → `status: active` for the target package.
- Do NOT commit yet.

### 6.3 — Mutation: create orchestration task

Run:
```
python3 scripts/tasks/create_orchestration_task.py \
  --after-task [explore_task_id] \
  --plan-path [task_path]/task_creation_plan.md
```
- Exit 0: note the TASK_ID and TASK_PATH printed to stdout.
- Non-zero: show stderr, stop. Inform user that RELEASES.md was already mutated (step 6.2); they may re-run step 6.3 manually.

Script does NOT commit.

### 6.4 — Mutation: close explore task

Edit `[task_path]/goal.md` inline:
- `status: in_progress` → `status: completed`
- Check all completed ACs (mark `- [x]`)

Do NOT commit yet.

### 6.5 — Atomic commit via task-complete

Call the `task-complete` skill on the explore task (`[task_path]`).
`task-complete` handles: STATUS.md regeneration + ONE atomic commit covering:
- `requirements_tasks/RELEASES.md` (or RELEASE_BACKLOG.md) with active status
- New orchestration task goal.md
- Explore task goal.md with completed status

### 6.6 — Post-success message

Print:
```
Release [version] is now active. Orchestration task [TASK_ID] is ready.
Next: run /autorun to begin distributed task creation, or run `Do [TASK_ID]` manually.
Each autorun session creates exactly one impl task.
```

### Failure Recovery

| Step | Failure | Safe? | Recovery |
|------|---------|-------|----------|
| 6.1 | dry-run fails | Yes | Fix issue, re-run Phase 6 |
| 6.2 | RELEASES write fails | Yes | Re-run Phase 6 |
| 6.3 | script fails | Partial (RELEASES activated, no orch task) | Re-run script manually |
| 6.4 | status edit fails | Yes | Orch task exists but blocked by after-chain; user runs task-complete manually |
| 6.5 | task-complete fails | Yes | Files mutated, uncommitted; `git status` shows all; commit manually |

At no point can the orchestration task execute prematurely (after-chain blocks until explore task is terminal).

## Key Constraints

| Context | Rule |
|---------|------|
| Orchestrator Phase 0 | Max 3 files |
| Phase 1 | Call should_use_agents.py first; inline if ≤30KB/5 files, else 1 agent |
| Each epic agent Phase 2 | Max 5 files; always agents (fan-out) |
| Orchestrator Phase 2b Step 1 | phase_2/ files only |
| Each remediation agent Phase 2b | Max 5 files; output-file polling (no agent-ID tracking) |
| Phase 2c Planner | Delegates to one `task-derive-from-requ` agent per in-scope feature requirement (REQ-PROC-058 AC-14); serial dispatch default, parallel-of-2 smoke test if work-list > 8; output-file polling on `per_requirement_plans/<REQ-ID>/plan.md`; assembles release plan + adds release-level concerns (package ordering, cross-requirement after-chains, scope re-check) |
| Phase 5 | summarize_plan.py output shown directly; per-requirement plan paths surfaced for coverage-matrix review; no requirement files read in main context |
| Phase 6 | Dry-run before any mutation; all mutations committed atomically by task-complete |

- Never read individual requirements files in the main orchestrator context
- `generate_status_overview.py` replaces bulk requirement reading
- Phase 2c must NOT escalate scope questions to user; write Phase 2 reopeners instead
- Phase 2c does NOT decompose requirements itself — it delegates per-requirement
  decomposition to `task-derive-from-requ` and assembles the results
  (REQ-PROC-035 SEC-05 / SEC-06, REQ-PROC-058 AC-14)
