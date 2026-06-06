---
task_id: TASK-PROC-031-03
type: impl
parent_requirement: REQ-PROC-031
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-DEV-EFFICIENCY
status: completed
effort: L
created: 2026-05-10
started: 2026-05-14
completed: 2026-05-14
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01]
scope_description: "Eliminate mid-session model switching. Move model decision upfront — orchestrator via --model flag, manual sessions via routing-time user warning. Simplify all skills accordingly."
release_description: ""
opus_recommended: true   # reason: cross-cutting redesign of model strategy across orchestrator, routing, skills, and agents — strategic judgment required
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: a9eb6506
  file: ../requirements.md
---

# Goal: Eliminate Mid-Session Model Switching

## Objective

Replace the current pattern of mid-session model switching (via `claude-switch-opus`) with **upfront model selection**. Mid-session switching never saved money — prompt caching is model-specific, so switching mid-session forces Opus to re-read all accumulated Sonnet context at full Opus input prices, costing ~60% more than starting fresh in Opus.

The new architecture decides the model **before any work begins**:
- **Automated mode**: orchestrator launches the claude session with `--model opus` if the task is `opus_recommended`
- **Manual mode**: `claude-route` detects `opus_recommended: true`, instructs the user to run `/model opus` (context is preserved across model switch, so the user simply continues without re-invoking)
- **Agents**: defaults reflect each agent's primary purpose; spawn-site override is available when a skill needs a different model for a specific phase

## Background

### The cost finding

Pricing (Anthropic API, May 2026):

| Model | Input | Cache Read | Output |
|---|---|---|---|
| Sonnet 4.6 | $3/MTok | $0.30/MTok | $15/MTok |
| Opus 4.7 | $5/MTok | $0.50/MTok | $25/MTok |

Prompt cache is model-specific. When `claude-switch-opus` runs inside a Sonnet session, Opus reads the entire accumulated context at full $5/MTok — there are no cache hits from Sonnet's prior turns. A 100k context that Sonnet gathered costs $0.30 on the Sonnet side and another $0.50 on the Opus side ($0.80 total). Had Opus started fresh: $0.50.

### Pre-switch Sonnet work has no real value

A skill-by-skill analysis showed that the Sonnet work performed before calling `claude-switch-opus` is in every case one of:
1. **Mechanical file reads** (Opus can read just as well)
2. **Script execution** (model-agnostic)
3. **Sub-agent spawning** (each agent has its own context, independent of main model)

Crucially, the memory `feedback_requ_explore_opus_mode_flaw.md` already documents that Sonnet must NOT synthesize before Opus takes over in `requ-explore`. Sonnet's pre-switch role is essentially just reading — work that doesn't justify the double-read cost.

### Implications for agents

The current convention (set by the 40-day-old `feedback_never_spawn_agent_with_opus_model.md` memory) is to spawn ALL agents with `model: sonnet` and let them internally call `claude-switch-opus` when they need Opus. That memory's premise was that direct `model: opus` "burns Opus quota". But the internal switch uses Opus quota anyway — and adds a double-read penalty. The memory is superseded by this finding.

## Scope

### In Scope

**Orchestrator (`scripts/automation/orchestrate.py`)**
- Refactor task selection to happen BEFORE session launch:
  1. Run `scripts/tasks/next_tasks.py --count 1` to pick the next task
  2. Read its `goal.md` to check `opus_recommended`
  3. Launch claude session with `--model opus` if true, default otherwise
  4. Pass task ID directly so the session doesn't re-pick

**Routing skill (`claude-route`)**
- When a task has `opus_recommended: true` and the user has not opted in via "use claude-switch-opus" or similar in the prompt: read goal.md, detect the flag, and instruct the user to switch model. The instruction makes clear that context is preserved across `/model` — the user simply types `/model opus` and "continue" (or nothing — Claude Code persists the conversation).
- Remove the existing logic that forwards "use claude-switch-opus" to the matched skill.

**Skills that currently invoke `claude-switch-opus`** — remove the invocation entirely. Skills become model-agnostic: they use whatever model the session is running. Specifically:
- `claude-ask` — drop the switch; Opus session means Opus answers
- `claude-modify-ordering-rules` — drop the conditional switch
- `doc-update-guidelines` — drop the switch
- `requ-explore` — drop the switch; the existing "Sonnet must not synthesize" guidance is moot when Sonnet isn't even involved in Opus mode
- `requ-derive-from-flow` — drop the switch from INCREMENTAL and FRESH modes. Sub-agents that do bulk reading can still be explicitly spawned with `model: sonnet` even in an Opus session (saves on bulk-read costs).
- `requ-verify-flow-coverage` — drop the switch. Sub-agents stay Sonnet for bulk extraction even in Opus session.
- `task-resolve` — drop the switch
- `ux-flow-draft` — drop the switch
- `ux-write-persona` — drop the switch (including conditional preanalysis call)
- `ux-write-scenario` — drop the switch
- `task-create` — **remove Opus mode entirely**; the work here is mechanical (scripts), Opus adds no value
- `task-create-code` — **remove Opus mode entirely**; same reasoning

**Workflow skills that spawn agents with internal Opus switching**
- `code-complex` — change agent spawn: spawn `architecture-advisor` directly with `model: opus` for the planning phase (or accept the agent's new default — see below). Implementation-engineer agents stay Sonnet. Remove the "Use claude-switch-opus for planning phase" prompt injection.
- `code-test` — same pattern. Test-engineer can be spawned with `model: opus` for the planning phase override, then `model: sonnet` for execution; OR the skill can run the planning phase in main thread when session is already Opus.

**Agents** — update default models:
- `architecture-advisor`: `model: sonnet` → `model: opus` (primary purpose is architectural reasoning)
- `opus-advisor`: `model: sonnet` → `model: opus` (description already says "Always uses claude-switch-opus")
- `setup-optimizer`: `model: sonnet` → `model: opus` (strategic analysis)
- `implementation-engineer`: keep `model: sonnet`
- `quality-checker`: keep `model: sonnet`
- `test-engineer`: keep `model: sonnet`; skill-side override available
- Remove all "DO NOT RUN WITH OPUS DIRECTLY" warnings from agent descriptions
- Remove "claude-switch-opus mode" instructions from agent descriptions

**Retire skills**
- `claude-switch-opus` — delete (no longer invoked anywhere)
- `claude-workflow-opus` — delete (its workflow is replaced by upfront model selection)

**CLAUDE.md — add new section: "Model Selection Guide"**
- Default session model: Sonnet (cost-efficient default)
- When to use Opus session: `opus_recommended: true` tasks, or explicit user choice for strategic work
- Agent spawn-time model selection:
  - Accept agent defaults in most cases
  - Override with `model: opus` when a Sonnet-session needs an Opus-quality sub-task (rare — usually the whole session should be Opus)
  - Override with `model: sonnet` when an Opus-session spawns an agent for pure execution (saves on bulk output tokens)
- Note that `/model` mid-session is a USER action only; the LLM cannot trigger it

**Memory cleanup**
- Delete or rewrite `feedback_never_spawn_agent_with_opus_model.md` — its premise is superseded
- Delete or rewrite `feedback_requ_explore_opus_mode_flaw.md` — no longer applies if Sonnet pre-gather phase is removed in Opus mode

**INDEX.md and factory_flows.md**
- Update to reflect removed skills (`claude-switch-opus`, `claude-workflow-opus`)
- Update skill descriptions where Opus mode references are removed

### Out of Scope
- Changes to REQ-PROC-031 itself (user story remains valid)
- Changes to `lib/`, `test/`, `integration_test/` files
- Adding new agents or skills (this is a simplification/cleanup task)
- Changing the structure of `next_tasks.py` (only orchestrator wraps it differently)

## Acceptance Criteria

### Code Changes
- [ ] `scripts/automation/orchestrate.py` picks task BEFORE session launch and passes `--model opus` when `opus_recommended: true`
- [ ] `claude-route` warns user to switch model when `opus_recommended: true` in current session is not Opus; no longer forwards "use claude-switch-opus" to skills
- [ ] `claude-switch-opus/` and `claude-workflow-opus/` skill folders deleted
- [ ] Agent default models updated: `architecture-advisor`, `opus-advisor`, `setup-optimizer` → `opus`; others remain `sonnet`
- [ ] All "DO NOT RUN WITH OPUS DIRECTLY" warnings removed from agent descriptions
- [ ] All "claude-switch-opus mode" instructions removed from agent descriptions
- [ ] `code-complex` and `code-test` spawn planning agents with explicit `model` parameter (or rely on new defaults); execution agents remain Sonnet
- [ ] `task-create` and `task-create-code` have no Opus mode references
- [ ] CLAUDE.md contains new "Model Selection Guide" section
- [ ] Outdated memories (`feedback_never_spawn_agent_with_opus_model.md`, `feedback_requ_explore_opus_mode_flaw.md`) either deleted or rewritten to reflect the new architecture
- [ ] INDEX.md and factory_flows.md reflect the removed skills and updated descriptions

### Verification (see "## Verification Strategy" below)
- [ ] All static-check commands return clean (zero unexpected matches)
- [ ] All smoke-test scenarios executed and pass
- [ ] Regression check: orchestrator runs cleanly on a known task in automated mode
- [ ] Manual verification checklist completed and ticked
- [ ] Rollback plan documented in protocol.md before any deletion

## Verification Strategy

**Why this section exists**: this task touches the orchestrator, the routing layer, ~15 skills, 6 agents, CLAUDE.md, and memories. A single missed reference can break the whole skill system silently — a skill might appear to run but produce wrong behavior because a removed branch was load-bearing somewhere. Verification must be both **static** (greppable) and **functional** (run the workflow end-to-end).

### Phased execution (mandatory)

Execute changes in this order. After each phase, run the relevant static checks before continuing. This isolates the source of any breakage.

1. **Phase A** — Agent defaults. Change `model: sonnet` → `model: opus` on three agents. Remove warnings. Static-check. Spawn each updated agent once via a trivial task. Low risk.
2. **Phase B** — Add CLAUDE.md "Model Selection Guide" section. No functional change. Read-back check.
3. **Phase C** — Orchestrator refactor (`orchestrate.py`). Add task pre-pick + `--model` flag. Test in isolation with `automation/tests/` if any exist; otherwise run a dry-run launch on a known opus_recommended task. Verify the constructed `claude` command includes `--model opus`.
4. **Phase D** — `claude-route` change: detect `opus_recommended`, warn user, stop forwarding. Trigger manually with a known opus_recommended task — confirm the warning shows. Also test the negative case (non-opus task → no warning).
5. **Phase E** — Strip Opus branches from skills **one at a time**, in this order (lowest-risk first):
   1. `claude-ask` (simplest)
   2. `doc-update-guidelines`
   3. `task-resolve`
   4. `ux-write-persona`, `ux-write-scenario`, `ux-flow-draft`
   5. `claude-modify-ordering-rules`
   6. `requ-explore`
   7. `requ-derive-from-flow`, `requ-verify-flow-coverage` (sub-agent patterns)
   8. `task-create`, `task-create-code` (remove Opus mode entirely)
   9. `code-complex`, `code-test` (agent-spawn changes)
   
   After EACH skill, run the relevant skill at least once and the static checks. Commit per skill (so rollback per-skill is possible).
6. **Phase F** — Delete `claude-switch-opus` and `claude-workflow-opus` skill folders. ONLY after Phase E confirms no references remain.
7. **Phase G** — Memory cleanup, INDEX.md, factory_flows.md updates.

Each phase ends with a commit. If anything breaks, `git revert HEAD` restores the previous phase cleanly.

### Static checks (must all return clean after Phase F)

```bash
# 1. No skill or agent references claude-switch-opus or claude-workflow-opus
grep -rn "claude-switch-opus\|claude-workflow-opus" .claude/skills/ .claude/agents/

# 2. Skill folders are deleted
test ! -d .claude/skills/claude-switch-opus && test ! -d .claude/skills/claude-workflow-opus

# 3. No agent has "DO NOT RUN WITH OPUS" or "claude-switch-opus mode" in description
grep -n "DO NOT RUN WITH OPUS\|claude-switch-opus mode" .claude/agents/*.md

# 4. Three target agents have model: opus
grep -l "^model: opus$" .claude/agents/architecture-advisor.md .claude/agents/opus-advisor.md .claude/agents/setup-optimizer.md

# 5. Other agents still have model: sonnet (sanity check)
grep -l "^model: sonnet$" .claude/agents/implementation-engineer.md .claude/agents/quality-checker.md .claude/agents/test-engineer.md

# 6. INDEX.md does not reference deleted skills
grep -n "claude-switch-opus\|claude-workflow-opus" .claude/skills/INDEX.md

# 7. factory_flows.md does not reference deleted skills
grep -n "claude-switch-opus\|claude-workflow-opus" .claude/factory_flows.md

# 8. Outdated memories are addressed (deleted or rewritten — verify content)
ls /home/vscode/.ccs/instances/web/projects/-workspaces-private-mood-tracker-flutter-app/memory/feedback_never_spawn_agent_with_opus_model.md 2>/dev/null
ls /home/vscode/.ccs/instances/web/projects/-workspaces-private-mood-tracker-flutter-app/memory/feedback_requ_explore_opus_mode_flaw.md 2>/dev/null

# 9. Orchestrator launch command includes --model when opus_recommended (inspect code)
grep -n "model\b" scripts/automation/orchestrate.py | grep -i "opus\|--model"
```

Document each command's output (or expected-empty result) in `plans_and_protocols/[date]_verification_protocol.md`.

### Functional smoke tests (must all pass)

For each, document the actual observation in the verification protocol — don't just tick the box.

**ST-1**: Pick a known `opus_recommended: true` task. Launch automated mode (orchestrator). 
- Expected: orchestrator constructs `claude --model opus ...`. Session header confirms Opus. No `claude-switch-opus` invocation in session log.
- Failure signal: session runs in Sonnet, OR errors during launch.

**ST-2**: Same task, manual mode. User types "Do TASK-XYZ".
- Expected: `claude-route` responds with the model-switch instruction. After `/model opus`, work continues.
- Failure signal: route silently proceeds in Sonnet, OR re-prompts after switch.

**ST-3**: Pick a known non-opus task. Both modes.
- Expected: normal Sonnet operation, no warnings.
- Failure signal: spurious warnings, OR orchestrator launches with `--model opus`.

**ST-4**: Invoke `code-complex` on a small refactor in an Opus session.
- Expected: planning agent (architecture-advisor) runs in Opus by default. Implementation-engineer agent(s) run in Sonnet. No `claude-switch-opus` call anywhere.
- Failure signal: agents fail to spawn, OR planning runs in Sonnet.

**ST-5**: Invoke each modified skill at least once via a representative case:
- `claude-ask`, `doc-update-guidelines`, `task-resolve`: any simple invocation
- `requ-explore`: trigger a small exploration task
- `task-create`, `task-create-code`: create a trivial new task
- `requ-verify-flow-coverage`: run on a known flow
- `ux-write-persona`, `ux-write-scenario`, `ux-flow-draft`: one of each
- `claude-modify-ordering-rules`: one small rule change

Each must complete without errors and produce expected output.

**ST-6**: Regression — run the autorun orchestrator for 1-2 task cycles. Verify no errors in `automation/orchestrate.log`.

### Manual verification checklist

- [ ] Each modified file's diff reviewed (not just trusted to grep)
- [ ] `claude-route` warning text is clear and tells user exactly what to do
- [ ] CLAUDE.md "Model Selection Guide" section is consistent with the rest of the doc (terminology, structure)
- [ ] Deleted skills don't appear in any other file (broader grep across whole repo, not just `.claude/`): `grep -rn "claude-switch-opus\|claude-workflow-opus" --exclude-dir=.git --exclude-dir=node_modules .`
- [ ] Each modified skill still passes `claude-modify-skill`'s own validation (run it once on a representative skill)
- [ ] Memory files cleaned (no stale references that would mislead future sessions)

### Rollback strategy

Each phase is one or more commits. If verification fails at any phase:
1. Identify which phase introduced the failure (the most recent commit before the symptom)
2. `git revert <commit>` for the offending phase
3. Document the failure and the rollback in `plans_and_protocols/[date]_rollback_note.md`
4. Re-plan the failed phase before retrying

DO NOT proceed to Phase F (deleting skill folders) until Phases A–E are fully verified. Once Phase F is committed, recovering the deleted skills requires `git revert`, which works but is more disruptive than rolling back an Edit.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking task dependencies |

## Notes

### Why M1 (user manually switches) over agent isolation

Considered alternative: spawn an Opus agent from `claude-route` to do the work, avoiding the user's intervention. Rejected because:
- In an agent, the user cannot interact directly (skills like `requ-explore`, `ux-write-persona` rely on asking the user questions)
- The user only sees the final agent report, losing live visibility of the work
- The manual `/model opus` switch preserves context — the user does not need to re-invoke anything

### Sub-agent model selection in Opus sessions

Even when the main session is Opus, sub-agents that do bulk reading (e.g., the parallel extraction agents in `requ-verify-flow-coverage`) should remain Sonnet — each agent has its own context, so there is no double-read penalty when they stay Sonnet. The skill should spawn them with explicit `model: "sonnet"` to make this intentional. Bulk reading at $3/MTok vs $5/MTok is a real saving.

### Skill modification workflow

Use `claude-modify-skill` for every skill change — direct edits without the skill are not permitted per CLAUDE.md.
