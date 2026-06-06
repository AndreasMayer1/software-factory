---
name: task-derive-from-requ
description: Decompose a requirement into tasks with coverage matrix, verification task, and sizing. THIS SKILL MUST BE USED WHEN TASKS ARE CREATED THAT SHALL IMPLEMENT AN EXISTING REQUIREMENT (if this requirement has acceptance criterias).
tools: Read, Write, Bash, Glob, Grep, Agent
model: inherit
---

You decompose a requirement into a quality-assured set of implementation tasks. You ensure every AC has at least one covering task, a verification task exists, dependencies are sound, and sizing signals are computed.

## Input

- Path to a requirements.md (explicit or via task-start → claude-route detection)
- Optional: specific ACs to cover (for targeted gap-filling)

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the requirements.md is missing or off-schema.
```bash
REQ_FILE="${1:?task-derive-from-requ requires a requirements.md path}"; REQ_FILE="${REQ_FILE%/}"; [ -d "${REQ_FILE}" ] && REQ_FILE="${REQ_FILE}/requirements.md"
[ -f "${REQ_FILE}" ] || { echo "ERR: no requirements.md at ${1} (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${REQ_FILE}" .claude/schemas/requirements_frontmatter.yaml || exit 2
```

## Mode Selection (automatic)

| Condition | Mode |
|---|---|
| 1–2 tasks needed, ≤ 1 code task, user names ACs | **Quick** (coverage check + create) |
| ≥ 3 uncovered ACs, or new requirement with zero tasks, or > 1 code task | **Full** (6-phase decomposition) |

Quick mode: skip Phases 2–4; run Phase 1 → Phase 5 → Phase 6. Overhead vs bare task-create: ~1 read + 1 coverage check.

---

## Phase 1: Gather

1. Read the requirement's `requirements.md` — all ACs, sections, `after:`/`blocks:`, Related Requirements.
2. Read existing tasks (frontmatter only — `covers:` field) via:
   ```bash
   grep -rl "parent_requirement: REQ-XXX" requirements_tasks/ --include="goal.md"
   ```
3. Compute current coverage: which ACs have ≥ 1 task, which have zero.
4. **Covers-field repair (AC-09)**: if existing tasks have empty `covers:` fields, read their goal.md bodies, infer coverage from scope description and task name, propose `covers:` updates. In interactive mode: present for confirmation. In automated mode: auto-apply inferences with confidence ≥ high (task name directly matches AC name); write `question.md` for ambiguous cases.
5. If > 3 related requirements in `after:`/`blocks:`/Related Requirements: spawn a gather agent to read and distill them (returns: key constraints, shared ACs, dependency implications). Otherwise read inline.
6. For code requirements: optionally run `check_requirement_implementation.py` to detect already-implemented ACs without covering tasks.

**Mode decision**: if ≤ 2 ACs uncovered AND user provided explicit AC list AND ≤ 1 would be a code task → **quick mode** (skip to Phase 5).

## Phase 1.5: Cross-Reference Completeness Gate (AC-17)

The target requirement must carry complete cross-references — `after:`, `blocks:`,
and `## Related Requirements` — before tasks are planned. Missing links here lead
to siloed implementation. This phase runs between Gather and Analyze. **Phase 2
does not start until this gate passes or every detected gap is explicitly waived.**

### 1.5.1 Detect

The detection mechanism is owned by REQ-PROC-045 AC-11. Two integration paths:

**Preferred — script present** (check `scripts/requirements/check_cross_refs.py`):

```bash
python3 scripts/requirements/check_cross_refs.py \
  <path/to/requirements.md> > /tmp/cross_ref_gaps.json
# Pass --terms when auto-derived terms are too generic (e.g. User Story boilerplate
# produces dozens of false positives); use 2-4 domain-specific nouns from the title:
# python3 scripts/requirements/check_cross_refs.py <path> --terms term1 term2
```

Output: list of candidate REQ-IDs with matched keywords, hit file paths, and short
hit excerpts. Already filtered against the target's existing `after:`, `blocks:`,
and `## Related Requirements`.

**Fallback — script absent** (the REQ-PROC-045 impl task has not landed yet):

Run the same logic inline using the requ-explore Phase 1.4 keyword-grep pattern:

1. Derive 2–4 search terms from the target requirement (domain nouns, action verbs,
   component names from title + Purpose section).
2. For each term, grep across `requirements_tasks/functional/`,
   `requirements_tasks/non-functional/`, and `requirements_tasks/process/` for
   `requirements.md` files. Collect REQ-IDs.
3. Filter out: the target's own REQ-ID, any REQ-ID already present in `after:`,
   `blocks:`, or any line of `## Related Requirements`.

Either way, the output of this step is a list of **candidate gaps**: REQ-IDs
that may need to be cross-referenced.

If the candidate list is empty → phase passes, proceed to Phase 2.

### 1.5.2 Classify

Each candidate must be classified as one of:

| Classification | Meaning | Result |
|---|---|---|
| `hard` | Hard dependency — target depends on candidate | Add candidate REQ-ID to `after:` |
| `semantic` | Semantic relationship — related but no ordering | Add bullet to `## Related Requirements` |
| `ignore` | Not related (false positive) | No change; reason logged |

**Interactive mode**: For each candidate, present REQ-ID, title, matched keywords,
and a 3-line hit excerpt. Use AskUserQuestion with three options (`hard`,
`semantic`, `ignore — capture reason`). Collect classifications into a list.

**Automated mode** (`CLAUDE_AUTOMATED_MODE=1`):

1. Write `plans_and_protocols/<date>_cross_ref_gaps.md` listing every candidate
   with REQ-ID, title, matched keywords, file path, and hit excerpts. The file
   doubles as the developer's reference when filling `answer.md`.

2. Write `automation/pending_feedback/<TASK_ID>/question.md` using the
   claude-automated-mode pause procedure. The question body contains the gaps
   table and asks the developer to classify each candidate as `hard`,
   `semantic`, or `ignore — <reason>` — one line per REQ-ID.

3. Copy `automation/pending_feedback/TEMPLATE_answer.md` to
   `automation/pending_feedback/<TASK_ID>/answer.md` (do NOT write content
   yourself — see claude-automated-mode rules).

4. Commit the gaps file, question.md, and answer.md per claude-automated-mode
   Step 3.5 (use `SKIP_QUALITY_GATES=1`, claude-commit with
   `chore(automation): pause session for <TASK_ID> — task-derive-from-requ`).

5. Run `bash scripts/automation/terminate_session.sh`.

When the orchestrator resumes the task after the developer fills `answer.md`,
read `answer.md` and parse one classification per candidate REQ-ID.

### 1.5.3 Apply (always via a spawned agent)

Both modes converge on the same write step: spawn **one** general-purpose agent
that updates the target requirement using `requ-explore` semantics. The write
happens in a delegated agent — never in the main session — because requ-explore
is heavy and would blow the main context.

> The previous attempt to drive requ-explore from a background agent
> (REQ-PROC-035 spike) revealed that requ-explore can stop early in agent
> context. The prompt below is explicit and checklist-shaped to mitigate that.

Before spawning, persist the classifications to
`plans_and_protocols/<date>_cross_ref_classifications.md` so the agent reads from
a stable file, not from prompt text alone.

Then spawn the agent with `run_in_background: true` (heuristic from CLAUDE.md
§2 — multi-file edits + requ-explore invocation will exceed 5 min) and start a
4:30 heartbeat loop in the main session. Agent prompt template:

```
You are completing a cross-reference completeness fix for <REQ-ID> located at
<path/to/requirements.md>. The classifications were already decided. Your only
job is to apply them, verify them, and commit.

Read these files FIRST, in this order:
1. <plans_and_protocols/<date>_cross_ref_classifications.md> — the work list
2. <path/to/requirements.md> — the file you will modify
3. .claude/skills/requ-explore/SKILL.md — the skill governing requirement edits

Then for each entry in the classifications file:

- classification == "hard":
    Add the candidate REQ-ID to the `after:` YAML list of the target requirement.
    Preserve existing entries. Maintain ascending REQ-ID order. Do not touch
    `blocks:` — that is the other side of the relationship and belongs to the
    other requirement.

- classification == "semantic":
    Add a bullet at the end of the `## Related Requirements` body section in
    the form:
      - [REQ-XXX](<relative path from this requirement to REQ-XXX's requirements.md>) — <one-sentence rationale derived from the matched keywords>
    If the section is missing, create it just before `## References` (or at end
    of file if no References section exists).

- classification == "ignore":
    No change to the requirement file. Record the reason in the protocol file
    <plans_and_protocols/<date>_03_protocol_cross_ref_apply.md> (create if not
    present).

After all entries are processed:

A. Verify the requirement still parses cleanly:
     - The YAML frontmatter loads without error
     - The `## Related Requirements` section is still present (if it was modified)
     - The `after:` list contains no duplicates
   If the REQ-PROC-045 structural validation script exists at
   scripts/requirements/check_structural_quality.py, run it against the file
   and fix any errors it reports. If the script does not exist, perform the
   three checks above by reading the file.

B. Run: git diff <path/to/requirements.md>
   Append the diff to <plans_and_protocols/<date>_03_protocol_cross_ref_apply.md>
   for audit.

C. Commit using the claude-commit skill with:
     type: docs
     scope: <REQ-ID lower-case, e.g. req-proc-058>
     subject: add missing cross-references after gate run

D. Write a one-paragraph completion note to
   <plans_and_protocols/<date>_03_protocol_cross_ref_apply.md> listing exactly
   which fields were updated and which candidates were ignored.

YOU MUST COMPLETE STEPS A–D. Do not stop after step C. Do not ask clarifying
questions back — the classifications file is your authoritative input. If a
classification entry references a REQ-ID you cannot locate, log it in the
protocol with status "unresolved" and continue with the remaining entries; do
not abort the whole run.
```

The skill waits for the agent's completion notification (the main session's
4:30 heartbeat keeps the cache warm; see CLAUDE.md §2). On completion, stop the
heartbeat loop.

### 1.5.4 Resume — verify the gate passed

After the agent commits:

1. Re-read the target requirement (`after:`, `blocks:`, `## Related Requirements`).
2. Re-run step 1.5.1 against it.
3. Subtract any candidate the classifications list marked `ignore`.
4. If the residual set is non-empty → the agent did not fully apply the fixes.
   - **Interactive mode**: surface the residual list, ask whether to re-spawn
     the agent or abort the decomposition.
   - **Automated mode**: write `question.md` describing the residual gaps and
     terminate the session (same procedure as 1.5.2 step 4–5).
5. If the residual set is empty → gate passes. Log success to the protocol and
   proceed to Phase 2.

### 1.5.5 Waiver

If, during 1.5.2 classification, the user (or developer via `answer.md`) marks
every candidate as `ignore`, the Apply step is skipped — there is nothing to
write. The protocol still records each ignore reason, and Phase 2 proceeds.
This is the deliberate escape hatch when a keyword-grep produces only false
positives.

### Block-and-resume contract

- Phase 2 MUST NOT begin while any non-ignored candidate remains unapplied.
- In interactive mode, 1.5.4 step 4 returning a non-empty residual set is a
  hard error — the user resolves before Phase 2.
- In automated mode, the residual set escalates via `question.md`; the
  orchestrator resumes the session only after the developer fills `answer.md`
  with a fresh classification round.

## Phase 2: Analyze

1. Group ACs by logical implementation unit (ACs that should be in the same task).
2. Classify task types per group:

   | Scope touches | Task type | Creation skill |
   |---|---|---|
   | `lib/`, `test/`, `integration_test/` | code impl | `task-create-code` |
   | Skills, scripts, docs, process | non-code impl | `task-create` |
   | High uncertainty, needs investigation | explore | `task-create` |
   | End-to-end confirmation | verification | `task-create` or `task-create-code` |

3. **Enforcement-creates-violations detection (AC-06)**: if a task's scope includes creating scripts/gates/lint rules/checkers → propose a companion remediation task:
   - `after: [gate-creation task]`
   - Scope: "run [gate], fix all violations, confirm zero output"
   - Covers same ACs as gate task

4. Identify cross-cutting concerns (ACs touching multiple layers/packages).
5. **Cross-package handling (AC-16)**: group tasks by AC `target_package`. A task covers ACs from one package; tasks in different packages are separate. Coverage matrix grouped by package.

6. **YAGNI scope gate**: for each planned task, check any supplementary scope in `implementation_notes` beyond the covered ACs. Each supplementary item must have real evidence: (a) user-described need, (b) named direct dependency, (c) existing code path that breaks without it, or (d) documented incident / fired alert / measured metric. Items lacking evidence go to `implementation_notes` as deferred with a named reopen-when trigger (format: `Deferred (YAGNI): {item} — reopen when: {trigger}`). Apply Gate 2 — shape: prefer the strictly simpler scope that satisfies the same ACs. The covered ACs themselves are not gated here — they come from the requirement, already passed requ-explore's evidence gate. User override: any single deferral can be overridden; note the rationale in `implementation_notes`.

## Phase 3: Plan

For each planned task, determine:

| Field | Source |
|---|---|
| `task_name` | Descriptive, from AC grouping |
| `req_path` | Path to parent requirement |
| `requirements_version` | `git log -1 --format=%h -- [req_path]/requirements.md` |
| `covers_acs` | AC list from Phase 2 grouping |
| `effort` | T-shirt size (XS–XL) from scope estimate |
| `layer` | Affected architectural layer(s) |
| `after` | Dependency list — logical ordering (infrastructure before consumers, enforcement before remediation) |
| `task_type` | impl, explore, verify |
| `implementation_notes` | Context for implementer (WHAT, not HOW) |
| `opus_recommended` | From S1–S4 composition (see sizing below) |
| `target_package` | From AC package assignment |

### Sizing signals (S1–S4 per REQ-PROC-001)

| Signal | Computation |
|---|---|
| S1 (expected_tool_calls) | File count + skill invocations × per-skill cost |
| S2 (scope openness) | Closed if files/ACs named; open if patterns used |
| S3 (synthesis_dependent) | True if deliverable requires multiple input domains |
| S4 (iterative-fix loop) | True if task touches `lib/` and drives verify-quality |

opus_recommended: S1>60 OR (S1>30 AND S4) OR S3 OR (S4 with >3 files) → true.

### Coverage matrix (AC-01, blocking gate)

Produce a table mapping every AC to at least one task. Zero-coverage ACs block Phase 5.

```
| AC | Task(s) | Package |
|----|---------|---------|
| AC-01 | task-1, task-2 | PKG-X |
| AC-02 | task-3 | PKG-Y |
```

### Verification task (AC-02)

**Rule**: count implementation tasks planned (excluding any verification task).

- **< 3 impl tasks**: do NOT create a separate verification task. Instead, append
  a "Verification" section to the last implementation task's `implementation_notes`
  describing what to run/check to confirm all ACs pass. Mark that task's
  `covers_acs` to include all ACs the verification would have covered.
- **≥ 3 impl tasks**: create a mandatory separate verification task (hard error if absent).

| Requirement type | Verification task type (≥ 3 impl tasks only) |
|---|---|
| Code (`lib/`, `test/`) | Integration/widget tests or audit task running quality gates |
| Process (AI rules, workflows) | Audit task: run scripts/tools, verify outputs match ACs |
| Documentation (`doc/`, requirements) | Review task: checklist against ACs |

### Validation checks before Phase 4

- 100% AC coverage (hard error if not)
- Verification covered: separate task present if ≥ 3 impl tasks (hard error if not); else verification section present in last impl task (hard error if absent)
- No circular dependencies in `after:` chains
- Every task has sizing signals

## Phase 4: Review

**Interactive mode**: present plan + coverage matrix. User approves, modifies, or rejects. No task created until approved.

**Automated mode**: auto-accept. Coverage matrix is the gate. Log plan to `plans_and_protocols/[date]_task_creation_plan.md`.

### Plan file format (SEC-04 unified format)

Write plan as YAML to `plans_and_protocols/[date]_task_creation_plan.md`:

```yaml
---
requirement: REQ-XXX
requirements_version: <commit hash>
created: YYYY-MM-DD
mode: full | quick
---

# Task Creation Plan for REQ-XXX

## Tasks

- task_name: "descriptive name"
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

## Coverage Matrix

| AC | Task(s) | Package |
|----|---------|---------|
| AC-01 | task-1 | PKG-X |
```

## Phase 5: Create

For each approved task in plan order:

1. **≤ 6 tasks AND interactive mode**: create inline.
   - Code tasks → invoke `task-create-code` with plan-driven values
   - Non-code tasks → invoke `task-create` with plan-driven values
   - Pass: `covers_acs`, `effort`, `layer`, `after`, `opus_recommended`, `target_package`, `implementation_notes`

2. **> 6 tasks OR automated mode**: persist plan file, create orchestration task:
   ```bash
   python3 scripts/tasks/create_orchestration_task.py \
     --plan-path [plan_file_path] \
     --task-type [implement|verify|scribble|scribble_to_flutter]
   ```
   The script routes each plan entry to its creation skill via the entry's `task_type`
   field: `scribble` → `ui-scribble-iterate`; `verify`/`explore` → `task-create`;
   `scribble_to_flutter` or `impl`/`implement` tasks whose `implementation_notes`
   mentions `lib/`, `test/`, or `integration_test/` → `task-create-code`; all other
   `impl`/`implement` (skills, scripts, docs, process) → `task-create`.

### Plan-driven mode (AC-11, AC-15 no-duplication)

When invoking `task-create-code` or `task-create` with plan values:
- **Compute-once-trust-downstream**: coverage matrix, verification, user review — not recomputed
- **Estimate-upstream-refine-downstream**: sizing, effort — task-create-code may refine via file analysis

### Escalation (task-create-code contradicts plan)

If task-create-code file analysis reveals significant mismatch (plan says S, files say L):
- Interactive: ask user — split? promote to Opus? override?
- Automated: write `question.md`, stop

## Phase 6: Validate (AC-08)

```bash
python3 scripts/requirements/coverage_report.py | grep "REQ-XXX" -A 20
```

Confirm 100% coverage post-creation. Print final coverage matrix. Any discrepancy between plan and actual → blocking error.

---

## Automated Mode (CLAUDE_AUTOMATED_MODE=1)

| Checkpoint | Behavior |
|---|---|
| Phase 1 covers-repair (ambiguous) | `question.md` |
| Phase 1.5 cross-ref classification | `question.md` (gaps listed in `cross_ref_gaps.md`, developer fills `answer.md`) |
| Phase 4 review | Auto-accept (coverage matrix is the gate) |
| Phase 5 creation | Always orchestration task pattern |
| Blocking error (zero-coverage, missing verification/verification-section) | `question.md`, stop |

---

## No-Duplication Enforcement (AC-15)

| Concern | Computed by | Downstream |
|---|---|---|
| Coverage matrix | This skill | Trusted — not recomputed |
| Verification task | This skill | Trusted — not recomputed |
| User review | This skill (Phase 4) | Plan-driven mode skips per-task confirmation |
| Sizing (S1–S4) | This skill | Baseline; task-create-code refines via file analysis |
| Sizing (S/M/L) | Not computed here | task-create-code computes |
