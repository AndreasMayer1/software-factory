# Rubric Re-run — Wave 3 Remaining Skills (TASK-PROC-044-05)

**Date:** 2026-05-30 · **Task:** TASK-PROC-044-05 · **Session:** 997adaa1 (web, automated, Sonnet)

## Rubric (from `claude-create-skill` §"Phase Split Decision")

| # | Signal | YES if… |
|---|--------|---------|
| S1 | Independently invocable? | Callable without manufacturing parent-held context |
| S2 | Coordinates ≥ 2 agents? | Real fan-out — one agent + wait is a wrapper, not orchestration |
| S3 | Natural human-review point? | Developer pauses/approves at this boundary |
| S4 | File-based artifact crosses boundary? | Producer writes, consumer reads — file is the contract |

**Split if ≥ 2 YES → sub-skill. < 2 YES → agent (collapsed into parent).**

---

## claude-* Family (15 skills)

### claude-commit

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invoked by users and skills ("MUST be used to commit changes").
- **S2**: No agent fan-out — reads staged diff, writes commit message, runs git.
- **S3**: No pause; automated commit after message generation.
- **S4**: Produces the git commit object (immutable once pushed); side-effects on the repository.

---

### claude-route

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | NO | **2/4** | Sub-skill ✓ |

- **S1**: Entry point for "Do [task]" or "/claude-route" — standalone invocation.
- **S2**: Routes to another skill but does not coordinate multiple agents simultaneously.
- **S3**: Interactive mode asks user which skill to use (AskUserQuestion). Automated mode skips.
- **S4**: No file produced; dispatches to a downstream skill which produces files.

---

### claude-create-skill

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invoked ("MUST be used to create new skills").
- **S2**: No agent fan-out; single-pass authoring.
- **S3**: Creates new skill requiring developer review before it enters rotation.
- **S4**: Produces SKILL.md + contract.yaml + INDEX.md entry crossing to all future agents.

---

### claude-modify-skill

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Mandatory path for all skill edits ("MUST be used to modify existing skills").
- **S2**: No agent fan-out; direct edit + INDEX/factory_flows sync.
- **S3**: Changes to skills affect all future sessions — developer naturally reviews the diff.
- **S4**: Produces modified SKILL.md + updated INDEX.md consumed by every subsequent session.

---

### claude-write-script

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: "MANDATORY for EVERY edit to scripts/**/*.py" — standalone guard.
- **S2**: Runs quality gates inline, no agent spawning.
- **S3**: Gates pass/fail is automatic; no human pause.
- **S4**: Produces/modifies Python scripts that are executable quality-gate runners.

---

### claude-optimize

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Invoked by user ("Use claude-optimize skill") or automation.
- **S2**: Produces one task — no multi-agent coordination.
- **S3**: The generated task is queued for later; no immediate developer pause.
- **S4**: Produces a goal.md (the improvement task) that is consumed by subsequent sessions.

---

### claude-optimize-audit

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Borderline — keep as sub-skill |

- **S1**: Standalone invocable ("Score the optimizer loop's effectiveness").
- **S2**: No agents; deterministic rubric scoring.
- **S3**: Outputs a report but no human approval step.
- **S4**: Produces a score report as text output, not a file artifact that crosses skill boundaries.

**Note:** 1/4 score is surprising for a skill that exists specifically for audit tracking. It survives as a sub-skill because (a) users invoke it by name, (b) the rubric is for determining split priority, not existence. No refinement proposed.

---

### claude-log

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| NO | NO | NO | YES | **1/4** | Keep as sub-skill (always invoked by other skills) |

- **S1**: Never directly invoked by users — always called at the end of another skill ("use claude-log skill").
- **S2**: No agents.
- **S3**: No human review; pure write-to-file operation.
- **S4**: Produces protocol.md / log files in plans_and_protocols/ consumed by future sessions.

**Note:** The 1/4 score matches the "agent-like" pattern (subordinate, no independent invocation) but since it's used as a Skill invocation in other skills, it must remain a sub-skill. This is a known limitation of the rubric when applied to subordinate utility skills. No refinement proposed.

---

### claude-automated-mode

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (context loader) |

- **S1**: Invoked at session start.
- **S2–S4**: No agents, no human pause, no file produced (loads rules into context only).

**Note:** Pure context-loader; exists as a skill for the Skill-tool invocation pattern. Rubric correctly identifies it as minimal-interface; keeping it a sub-skill is the right call since the rules must be loaded before any other action.

---

### claude-autorun

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: User invokes "start/stop/status" automation orchestrator.
- **S2**: Controls the orchestrator process but doesn't itself coordinate ≥2 agents.
- **S3**: Start/stop are explicit developer decisions with operational consequences.
- **S4**: Writes/reads automation state files (`.automated_mode`, orchestrator PID).

---

### claude-install-os-tool

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Invoked before any OS-level installation.
- **S2**: No agents.
- **S3**: Installation is automatic once invoked.
- **S4**: Modifies the devcontainer OS state — a persistent side effect crossing session boundaries.

---

### claude-modify-ordering-rules

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invoked for task ordering changes.
- **S2**: No agents.
- **S3**: No review pause; applies changes directly.
- **S4**: Produces/updates `.claude/task_ordering_rules.yaml` consumed by `next_tasks.py`.

---

### claude-ask

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (research utility) |

- **S1**: Invocable for research questions.
- **S2–S4**: Single-model query, no agents, no file artifact.

**Note:** 1/4 utility skill; kept as sub-skill by convention (Skill-tool invocation pattern). Correct classification.

---

### claude-resume-agent

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | NO | **2/4** | Sub-skill ✓ |

- **S1**: Used when a background agent is killed or stops unexpectedly.
- **S2**: Resumes one agent; no multi-agent coordination.
- **S3**: Developer decides whether/how to resume — explicit invocation is itself the review.
- **S4**: No dedicated file artifact produced.

---

### claude-save-checkpoint

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Invoked to save context for session restart.
- **S2**: No agents.
- **S3**: No review pause.
- **S4**: Produces a checkpoint file in plans_and_protocols/ consumed by the next session.

---

## doc-* Family (4 skills)

### doc-update-guidelines

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Invoked after any task that discovered a doc/ gap.
- **S2**: No agents.
- **S3**: Updates to `doc/` guidelines are law — developer reviews before accepting.
- **S4**: Produces updated `doc/` files consumed by every future implementation task.

---

### doc-update-tokens

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invocable for design token management.
- **S2**: No agents.
- **S3**: Token value decisions require developer approval (affect all UI).
- **S4**: Produces `tokens.g.dart` / `animation_tokens.g.dart` consumed by all presentation code.

---

### doc-lookup-dependencies

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (mandatory guard) |

- **S1**: Mandatory before emitting dependency calls — standalone invocable.
- **S2–S4**: Inline lookup; no agents, no human pause, no file output (lookup_log.jsonl is a side effect written by the consuming task, not by this skill).

**Note:** Despite 1/4, it must remain a sub-skill because it is the enforcement point for REQ-PROC-053 AC-02. The rubric correctly flags it as a thin utility; no structural change proposed.

---

### doc-split

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Invocable when a doc/ file exceeds 600 lines.
- **S2**: No agents.
- **S3**: Split decisions (how to divide the file) require developer review.
- **S4**: Produces new doc/ files + updates cross-references consumed by all future sessions.

---

## release-* Family (5 skills)

### release

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Final release orchestration — directly invoked with `/release`.
- **S2**: No multi-agent fan-out; sequential steps.
- **S3**: Explicit user gate at smoke-test step; push to remote requires confirmation.
- **S4**: Produces release notes, git tags — permanent artifacts.

---

### release-begin-impl

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invoked to start a release implementation phase.
- **S2**: No agent fan-out.
- **S3**: Creates orchestration task that developer reviews.
- **S4**: Produces orchestration goal.md + activates release state.

---

### release-begin-impl-finalize

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Post-autorun finalization — directly invoked.
- **S2**: No agents; sequential checks.
- **S3**: Coverage audit + user gate before `/release` proceeds.
- **S4**: Updates RELEASE_BACKLOG.md + after-chain consumed by release.

---

### release-plan

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invoked for package-to-version assignment.
- **S2**: No agents.
- **S3**: Package assignments are developer decisions requiring review.
- **S4**: Produces RELEASE_BACKLOG.md consumed by release-begin-impl and next_tasks.py.

---

### release-status

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (info utility) |

- **S1**: Directly invocable at any point.
- **S2–S4**: Read-only; outputs status to console; no agents, no pause, no file artifact.

**Note:** Pure read-and-report utility. Same pattern as claude-optimize-audit. Correct classification.

---

## Misc (4 skills)

### brb

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (keepalive utility) |

- **S1**: Invocable via "brb"/"afk" trigger.
- **S2–S4**: Loop/keepalive mechanism; no agents, no pause, no file artifact.

**Note:** Pure session utility. The rubric correctly identifies it as minimal-interface. No refinement.

---

### codegraph

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (analysis utility) |

- **S1**: Used for code exploration before Glob/Grep.
- **S2–S4**: Read-only analysis; no agents, no pause, no persistent file output.

---

### product-intake

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Entry point for new product information — directly invoked.
- **S2**: Routes to requ-explore/ux-* but doesn't coordinate multiple agents simultaneously.
- **S3**: Product decisions always require developer confirmation before propagating down the chain.
- **S4**: Produces requirements.md / scenario / flow updates consumed by task creation.

---

### verify-quality

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | NO | **3/4** | Sub-skill ✓ |

- **S1**: Mandatory pre-commit gate — standalone invocable.
- **S2**: Spawns `quality-checker` agent (audit-only mode) → real agent fan-out.
- **S3**: RED exit blocks task completion; developer must review and fix before proceeding.
- **S4**: No dedicated file artifact (`.git/quality_green_hash` is a cache marker, not a data artifact).

---

## requ-* Remaining (5 skills)

### requ-apply-market

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Invocable to apply market research findings.
- **S2**: No agent fan-out.
- **S3**: Market-to-requirement mapping requires developer review.
- **S4**: Produces updated requirements.md consumed by task creation.

---

### requ-assign-packages

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invocable for bulk package assignment.
- **S2**: No agents.
- **S3**: Automated assignment using 4-signal heuristics; no human pause.
- **S4**: Updates `target_package` in requirements.md files and propagates to tasks.

---

### requ-derive-from-flow

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invocable to analyze user flows for requirement gaps.
- **S2**: No agents.
- **S3**: Reads developer-provided notes.md for intent — inherently requires developer input.
- **S4**: Produces new requirements.md or updates existing ones consumed downstream.

---

### requ-merge

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| NO | NO | NO | YES | **1/4** | Keep as sub-skill (utility, called by task-complete) |

- **S1**: Not directly user-invoked — called internally by task-complete.
- **S2–S3**: No agents, no human pause.
- **S4**: Produces merged requirements.md (generated artifact).

**Note:** Similar to claude-log's 1/4 pattern — a subordinate utility that must remain a skill because it's invoked via the Skill tool. No refinement proposed.

---

### requ-verify-flow-coverage

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Standalone invocable after exploration tasks.
- **S2**: No agents.
- **S3**: Coverage gaps require developer remediation decisions.
- **S4**: Updates flow coverage tracking files consumed by downstream verification.

---

## task-* Remaining (4 skills)

### task-complete-bugfix

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invoked to close bugfix tasks.
- **S2**: No agents.
- **S3**: Cleanup (remove debug artifacts) is automated.
- **S4**: Produces task completion state + commit consumed by release tracking.

---

### task-repair-meta

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invocable for metadata audits.
- **S2**: No agents.
- **S3**: Repairs are applied directly; no human review gate.
- **S4**: Updates goal.md frontmatter files consumed by all task-management scripts.

---

### task-resolve

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Fallback for open-ended impl tasks — directly invocable.
- **S2**: May spawn general-purpose agents for investigation/drafting phases.
- **S3**: Agent-assisted mode has explicit user review points between phases.
- **S4**: Produces plans_and_protocols/ + deliverable artifacts (skills, docs, requirements) crossing session boundaries.

---

### task-unblock-check

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (investigation utility) |

- **S1**: Directly invocable to investigate blocked tasks.
- **S2–S4**: Read-only analysis + report; no agents, no human pause, no file artifact produced.

**Note:** 1/4 — pure read-and-report. Kept as sub-skill because users invoke it by name. Correct.

---

## ux-* Family (7 skills)

### ux-create-flow

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Entry point for all new flow work — directly invocable.
- **S2**: Dispatches to ux-flow-draft, ux-flow-complete, ux-flow-approve (sub-skill fan-out).
- **S3**: Flow approval is an explicit developer gate.
- **S4**: Produces flow.md artifacts consumed by requ-derive-from-flow + requirement tasks.

---

### ux-flow-draft (internal)

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| NO | NO | NO | YES | **1/4** | Borderline — internal sub-skill |

- **S1**: INDEX.md marks this internal ("do not call directly"). Not standalone.
- **S2–S3**: No agents, no human pause (draft is automated).
- **S4**: Produces draft flow.md consumed by ux-flow-complete.

**Note:** The 1/4 score correctly identifies this as agent-territory, but the Skill-tool invocation pattern forces it to be a sub-skill. The INDEX.md "internal" label is the right engineering response to this rubric result — it discourages direct invocation while keeping the Skill-tool pattern. No further action needed.

---

### ux-flow-complete (internal)

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| NO | NO | NO | YES | **1/4** | Borderline — internal sub-skill |

- Same analysis as ux-flow-draft. Fills out the draft into a complete flow.md.

---

### ux-flow-approve (internal)

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| NO | NO | YES | YES | **2/4** | Sub-skill (barely) |

- **S1**: Marked internal in INDEX.md.
- **S2**: No agents.
- **S3**: The approval step IS a human review point — the skill exists precisely to gate on developer approval.
- **S4**: Updates flow.md `review_status: approved` consumed by requ-derive-from-flow.

**Note:** 2/4 is the right score — the approval boundary justifies the split despite S1 being NO. No refinement.

---

### ux-validate-rule

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (validation utility) |

- **S1**: Invocable to validate UX proposals against personas.
- **S2–S4**: No agents, no human pause, no file artifact (outputs validation result inline).

---

### ux-write-persona

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invocable for persona creation/modification.
- **S2**: No agents (runs cascade scan inline).
- **S3**: Personas define the product's target users — developer reviews before accepting.
- **S4**: Produces persona YAML files consumed by scenario + flow + requirement work.

---

### ux-write-scenario

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | YES | YES | **3/4** | Sub-skill ✓ |

- **S1**: Directly invocable for scenario creation/modification.
- **S2**: No agents (cascade scan inline).
- **S3**: Scenarios shape flow design — developer reviews.
- **S4**: Produces scenario files consumed by flow + requirement work.

---

## ui-* Wave 3 (1 skill)

### ui-create-scribble-improve

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | YES | YES | YES | **4/4** | Sub-skill ✓ |

- **S1**: Directly invocable to autonomously improve `ui-create-scribble`.
- **S2**: Spawns vision-evaluation agents + iteration agents in a loop — real multi-agent orchestration.
- **S3**: Iteration results are reviewed; the developer can stop the loop at any checkpoint.
- **S4**: Produces improved scribble HTML files consumed by ui-verify-flutter.

---

## Other (2 skills)

### code-run-integration

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | NO | **1/4** | Keep as sub-skill (test runner utility) |

- **S1**: Directly invocable to run integration tests individually.
- **S2–S4**: Test runner; no agents, no human pause, no file artifact.

---

### vcd-log-tradeoff

| S1 | S2 | S3 | S4 | Score | Verdict |
|:---:|:---:|:---:|:---:|:---:|---|
| YES | NO | NO | YES | **2/4** | Sub-skill ✓ |

- **S1**: Directly invocable to document value trade-offs.
- **S2**: No agents.
- **S3**: No human pause; writes trade-off inline in the artifact.
- **S4**: Produces trade-off entries in VCD artifacts consumed by product decisions.

---

## Summary

| Score | Count | Skills |
|:---:|:---:|---|
| 4/4 | 3 | task-resolve, ux-create-flow, ui-create-scribble-improve |
| 3/4 | 13 | claude-create-skill, claude-modify-skill, claude-autorun, doc-update-guidelines, doc-update-tokens, doc-split, release, release-begin-impl, release-begin-impl-finalize, release-plan, product-intake, verify-quality, requ-apply-market, requ-derive-from-flow, requ-verify-flow-coverage, ux-write-persona, ux-write-scenario |
| 2/4 | 11 | claude-commit, claude-route, claude-write-script, claude-optimize, claude-install-os-tool, claude-modify-ordering-rules, claude-resume-agent, claude-save-checkpoint, requ-assign-packages, task-complete-bugfix, task-repair-meta, ux-flow-approve, vcd-log-tradeoff |
| 1/4 | 18 | claude-optimize-audit, claude-log, claude-automated-mode, claude-ask, doc-lookup-dependencies, release-status, brb, codegraph, requ-merge, task-unblock-check, ux-flow-draft, ux-flow-complete, ux-validate-rule, code-run-integration + borderline utilities |

## Refinement Proposals

**No revision_target.yaml warranted.** Findings:

1. **Internal sub-skills (ux-flow-draft, ux-flow-complete) scoring 1/4**: The rubric correctly identifies these as agent-territory. The "internal" label in INDEX.md is the right mitigation — no structural change needed. Signal: the rubric's S1 (independently invocable) effectively captures the "internal vs. external" distinction.

2. **Pure utility skills at 1/4 (brb, codegraph, release-status, task-unblock-check, etc.)**: The rubric is not a gate for _existence_ of a skill, only for whether it should be a sub-skill vs. collapsed into a parent. 1/4 utilities correctly remain as sub-skills because users invoke them by name via the Skill tool.

3. **verify-quality scoring 3/4 (not 4/4)**: It does not produce a file artifact (S4 = NO), but it coordinates the quality-checker agent (S2 = YES) and blocks completion (S3 = YES). This is the correct score — quality gates are a gate mechanism, not a file-producing pipeline stage.
