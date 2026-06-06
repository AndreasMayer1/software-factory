# Opus Plan: Improve `release-begin-impl` Skill Based on Session Failures

## Objective

Fix structural issues in `.claude/skills/release-begin-impl/SKILL.md` that caused
the current session to:
1. Ask the user questions that an agent could resolve by reading more files.
2. Re-ask scope decisions in Phase 3/5 that were already settled in Phase 2.
3. Tempt the orchestrator into doing task-creation work in the main context
   (which doesn't fit the context window for large feature requirements).
4. Confuse the order of phases — inline edits done in main context that
   should have been agent-dispatched, Phase 4 skipped, Phase 5/6 entangled.

## Analysis Summary — What Went Wrong in This Session

### Mapping session events to skill phases

| Session Event | Skill Phase | Outcome |
|---------------|-------------|---------|
| User chose "by release" mode | Phase 0 | Worked (after script fix) |
| `--release 0.0.1` returned 0 reqs | Phase 0 | **Skill bug — script fix needed first**; now resolved |
| `scope_boundaries.includes` empty for 0.0.1 | Phase 1 | Phase 1 reported "no includes" — useless; should have checked `packages:` instead |
| Phase 2 found Transfer Notifications contradiction | Phase 2 | OK — surfaced correctly |
| User decided to move Transfer Notifications → 0.2.0 | Phase 2b | I did the RELEASES.md / RELEASE_BACKLOG.md edits inline in main context instead of dispatching an agent. The skill says "spawn an agent" but for a 2-line edit that's overkill — skill should allow trivial inline edits |
| Phase 3 agents flagged "AC-28–36 may belong elsewhere" | Phase 3 | **Skill bug** — that's a scope decision; should have been asked/answered in Phase 2 |
| Phase 3 agents flagged "2 open analyze tasks may be obsolete" | Phase 3 | **Skill bug** — agent should have READ the tasks to determine, not asked user |
| Skipped Phase 4 (Gap Verification) | Phase 4 | I went straight from Phase 3 to asking user — never re-ran the status script |
| I asked user "should missing features get tasks?" | Phase 5 (sort of) | **Redundant** — those features have requirements assigned to 0.0.1, so yes obviously. Phase 2 already settled this |
| I started reading 250-line `feat_pairing_management/requirements.md` in main context to prepare goal.md creation | Phase 3 | **Context-blowing mistake** — but the skill *does* say agents should create the tasks (item 3 of Phase 3). I countermanded that when spawning Phase 3 agents (told them "do NOT auto-create — just flag"). Skill instructions are right; my prompt was wrong, but the skill doesn't make this strong enough |
| Never reached Phase 6 (activation) | Phase 6 | Workflow stalled |

### Root causes

1. **No clear distinction between "investigate-able" vs. "user-only" questions.**
   Phase 3 instructions say "flags in questions file" for "gaps or open decisions"
   but doesn't define which decisions belong to user vs. agent. Result: agents
   over-escalate.

2. **Phase 2 vs Phase 3 vs Phase 5 question domains overlap.** The user pointed
   out: "scope decisions were already made in the previous phase". The skill
   currently allows scope-style questions to leak into Phase 3 and Phase 5.

3. **Phase 1 is mismatched to package-based scope model.** The skill checks
   `scope_boundaries.includes` but this project (and likely all current releases)
   uses `packages:` lists. `includes` is often empty — Phase 1 then does nothing
   useful.

4. **Phase 2b "always spawn an agent" is wasteful for trivial edits.**
   Updating two lines in RELEASES.md doesn't need a whole agent.

5. **Phase 3 task-creation instruction is ambiguous about HOW.** It says
   "creates `goal.md` in feature's tasks/ folder using task-create-code
   conventions" but doesn't tell the agent to invoke the `task-create-code`
   skill explicitly, nor what to do when the requirement has *known* in-scope
   ACs but they span multiple ACs (one task vs. multiple tasks per feature?).

6. **Phase 5 "user gate" is redundant.** It asks for approvals that
   Phase 2 already settled. It also presents files the orchestrator was told
   not to read — making the orchestrator unable to summarize meaningfully.

7. **The orchestrator is implicitly tempted to do work that belongs to agents.**
   The skill never says "if you find yourself reading a feature
   requirements.md, you've already lost". The session showed exactly that
   failure.

8. **Phase 4 is gated on outputs of Phase 3 but the skill doesn't enforce the
   sequence.** I jumped over it.

9. **Orchestration task purpose isn't explained.** User asked "do we even need
   `create_orchestration_task.py`?" — the skill never says: "the orchestration
   task is the autorun handoff; if you do everything in this skill, autorun has
   nothing to drive and the script returns Exit 3, which is fine."

---

## Execution Plan

This is a **single-file edit** to `.claude/skills/release-begin-impl/SKILL.md`.
One implementation agent can do it. The plan below specifies exactly which
sections to rewrite and how.

### Agent 1: Skill Rewriter

The agent will read `.claude/skills/release-begin-impl/SKILL.md` and apply the
following targeted edits. It MUST preserve the overall phase structure (0–6)
and the "Inputs" / "Key Constraints" sections, only rewriting the marked
sub-sections.

#### Edit 1 — Add a new "Decision Domains" section after `## Inputs`

Insert before Phase 0 a new section that defines what kinds of questions go
where. This is the single most load-bearing fix — it prevents leakage of
Phase-2 questions into Phases 3 and 5.

Content (verbatim):

```markdown
## Decision Domains (Read This Before Anything Else)

Three kinds of questions surface during release prep. Each has a designated
phase. Mixing them up wastes user time and agent context.

| Domain | Examples | Where it belongs |
|--------|----------|------------------|
| **Scope** — does X belong in this release? | "Transfer Notifications in 0.0.1?", "Move AC-28–36 to 0.0.2?" | **Phase 2 only.** Once Phase 2 ends, scope is frozen for this iteration. |
| **Coverage** — does the in-scope work have requirements + impl tasks? | "Does feat_pairing have an impl task?" | **Phase 3.** Agents either resolve (create tasks) or escalate via Phase 5 if blocked by an *implementation-approach* ambiguity. |
| **Investigation** — can the answer be obtained by reading more files? | "Are these 2 open analyze tasks still relevant?", "Does this existing task cover AC-28?" | **Inside the agent.** Never escalate to user. Agents must read the cited files before flagging. |

**Phase 3 and Phase 5 must NOT contain Scope-domain questions.** If a Phase 3
agent identifies a scope ambiguity, it must surface it as a *Phase 2 reopener*
(see Phase 4) — not as a Phase 3 user question.
```

#### Edit 2 — Rewrite Phase 1 to be package-aware

Replace the current Phase 1 section. New content:

```markdown
## Phase 1 — Scope Coverage Check (spawn 1 agent)

Agent reads ONLY (3 files max):
- `requirements_tasks/RELEASES.md`
- `requirements_tasks/STATUS_NEXT_RELEASE.md`
- `requirements_tasks/RELEASE_BACKLOG.md`

Agent task — verify both:

1. **Package coverage**: every package listed in the release's `packages:`
   array (RELEASES.md) has at least one requirement assigned to it
   (via `target_package` in STATUS_NEXT_RELEASE.md or in RELEASE_BACKLOG.md).
2. **Includes coverage** (only if non-empty): every `scope_boundaries.includes`
   item maps to ≥1 requirement assigned to the release.
3. **Contradiction check**: for every package in `packages:`, verify the
   package's *theme* does not appear in `scope_boundaries.excludes`. (E.g.,
   `Transfer Notifications` package in `packages:` while "Notifications" is in
   `excludes:` — surface as a contradiction.)

If `scope_boundaries.includes` is empty: that's fine — the `packages:` list
*is* the scope. Note this explicitly in the report (don't claim "nothing to
check").

Output: `[task_path]/questions/iteration_[NN]/phase_1/scope_gaps.md`
```

#### Edit 3 — Rewrite Phase 2b to allow inline trivial edits

Replace Step 2 of Phase 2b. New content:

```markdown
### Step 2 — Classify each gap and dispatch work

For each gap or user-approved action, choose the right execution path:

**Inline (orchestrator does it directly, no agent)** — when ALL hold:
- The change touches a single file
- The change is ≤5 lines
- The exact diff is already specified in the user's answer
- Examples: removing a package from RELEASES.md `packages:` list,
  flipping `assigned_release` in RELEASE_BACKLOG.md

**Spawn an agent** — when ANY hold:
- The change requires writing a new requirements.md from a draft
- The change spans multiple files
- The change involves ≥6 lines of edits
- Any judgment is required (the prompt cannot fully specify the diff)

Agents that hit a blocker write to
`[task_path]/questions/iteration_[NN]/phase_2b/[topic]_questions.md` and
terminate.

After each agent spawn, record `agentId` → work item in
`[task_path]/questions/iteration_[NN]/phase_2b/_agent_state.md`.
```

(Steps 3–5 of Phase 2b stay as-is.)

#### Edit 4 — Rewrite Phase 3 to be unambiguous about task creation and escalation

Replace the Phase 3 section. New content:

```markdown
## Phase 3 — Feature Agents (spawn 1 per feature, in parallel)

**Scope is frozen.** Phase 2 already decided which packages are in this
release. Phase 3 only deals with Coverage (do impl tasks exist?) and
Investigation (resolvable by reading files).

Each agent reads ONLY (max 5 files — increased from 3):
- The feature's `requirements.md`
- The feature's `tasks/` folder listing (use ls/glob, plus optionally read up
  to 2 task `goal.md` files if needed to resolve "is this task obsolete?"
  questions)
- `requirements_tasks/RELEASES.md` (scope section only)

Each agent must:

1. Identify all ACs/SECs whose `target_package` is in the release's
   `packages:` list. These are the **in-scope items**.
2. For each in-scope item, check whether an existing impl task in the
   feature's `tasks/` folder covers it. **If unsure whether an existing task
   covers it, READ that task's `goal.md`** — do not escalate the question.
3. **For in-scope items with no covering task**: invoke the `task-create-code`
   skill (or write a `goal.md` following its conventions) to create exactly
   one impl task per coherent group of ACs (group by domain layer when ACs
   touch the same entity; otherwise one task per AC). Use today's date and
   a descriptive name.
4. Only flag in `[task_path]/questions/iteration_[NN]/phase_3/feat_[REQ_ID]_questions.md`
   when:
   - The implementation approach is genuinely ambiguous (multiple valid
     architectures, requires user choice), OR
   - The agent suspects the AC was added after Phase 2 scope-freeze and
     should be reconsidered (mark as **"Phase 2 reopener — scope question"**).
   Do NOT flag:
   - "Should we create a task for this AC" (yes — it's in scope)
   - "Is this old task still relevant" (read it and decide)
   - "Does this feature need impl tasks" (yes if it has in-scope ACs)

Output: created task files (one per feature, possibly more) +
optional `feat_[REQ_ID]_questions.md`.
```

#### Edit 5 — Add Phase 4 enforcement guard

Replace Phase 4. New content:

```markdown
## Phase 4 — Gap Verification (spawn 1 agent — MANDATORY)

**Do not skip this phase.** Phase 5 reads only Phase 4's summary.

Agent reads (max 10 small files):
- All `[task_path]/questions/iteration_[NN]/` phase files (phases 1–3 and 2b)
- Re-runs `python scripts/generate_status_overview.py --release [release_version]
  --output requirements_tasks/STATUS_NEXT_RELEASE.md`, then reads updated
  `requirements_tasks/STATUS_NEXT_RELEASE.md`
- `requirements_tasks/RELEASES.md`

Agent verifies:
- Every in-scope package has ≥1 feature requirement
- Every in-scope AC has ≥1 impl task (or is flagged in Phase 3 questions
  as a Phase 2 reopener)
- No Phase 2 reopeners are unresolved

Output: `[task_path]/questions/iteration_[NN]/phase_4/final_coverage_check.md`
with explicit verdict: `READY_TO_ACTIVATE` / `BLOCKED_BY_REOPENERS` /
`BLOCKED_BY_MISSING_TASKS`.
```

#### Edit 6 — Rewrite Phase 5 to not duplicate Phase 2 questions

Replace the Phase 5 section. New content:

```markdown
## Phase 5 — Present Final Verdict (you, main context)

The orchestrator MAY read `phase_4/final_coverage_check.md` to obtain the
verdict and the list of any unresolved escalations. (This is the one Phase 5
file the orchestrator is allowed to read.)

Three possible outcomes:

1. **Verdict `READY_TO_ACTIVATE` and no Phase 2 reopeners**:
   - Tell user: "Release prep complete. N impl tasks created. Ready to
     activate. Proceed to Phase 6?"
   - On user confirmation: go to Phase 6.

2. **Verdict `BLOCKED_BY_REOPENERS`**:
   - List the Phase 2 reopener questions verbatim (these are the only
     questions the user should see at this stage).
   - On user answers: re-enter Phase 2b (Scope category) for any scope
     changes, then re-run Phases 3–4 only for affected features.
   - Do **not** ask the user about coverage/task creation — those were
     resolved by agents in Phase 3.

3. **Verdict `BLOCKED_BY_MISSING_TASKS`**:
   - This indicates a Phase 3 agent failed silently. Re-run Phase 3 for the
     affected features. Do not bother the user.

Phase 5 must NOT ask:
- "Should we create impl tasks for X" (Phase 3 already did)
- "Is X in scope" (Phase 2 already decided)
- "Are these old tasks still relevant" (Phase 3 agent should have resolved)
```

#### Edit 7 — Add note to Phase 6 explaining orchestration task purpose

In Phase 6 step 3, add this note before the exit code handling:

```markdown
**Why this script exists**: The orchestration task is the handoff to
`/autorun`. If Phase 3 successfully created all needed impl tasks,
`create_orchestration_task.py` will return Exit 3 ("nothing to do") —
that's the success path, not an error. The orchestration task is only
needed when impl tasks remain to be created iteratively (e.g., in
package-mode or when Phase 3 escalated some features for later).
```

#### Edit 8 — Update "Key Constraints" table

Update the table to reflect new agent file limits:

```markdown
| Agent | Max files read |
|-------|---------------|
| Orchestrator Phase 0 | 3 |
| Scope check Phase 1 | 3 |
| Each epic agent Phase 2 | 5 |
| Orchestrator Phase 2b Step 1 | phase_2/ files only |
| Each remediation agent Phase 2b | 5 |
| Each feature agent Phase 3 | 5 (was 3 — bumped to allow agents to read up to 2 existing task goal.md files when resolving "is this obsolete" questions) |
| Gap verification Phase 4 | 10 (small files) |
| Orchestrator Phase 5 | 1 (final_coverage_check.md only) |
```

Add a new constraint at the bottom of the file:

```markdown
- **The orchestrator never reads a feature's `requirements.md` file.** If you
  catch yourself doing this, stop and dispatch an agent. Feature requirements
  are routinely 200+ lines and exhaust main-context budget.
- **The orchestrator never invokes `task-create-code` directly.** Task
  creation happens inside Phase 3 agents.
```

---

## Quality Criteria

- [ ] Phase 1 explicitly handles empty `scope_boundaries.includes` and
      checks the `packages:` list instead.
- [ ] Phase 1 detects contradictions between `packages:` and `excludes:`.
- [ ] Phase 2b allows inline trivial edits without an agent for ≤5-line
      single-file changes.
- [ ] Phase 3 explicitly forbids scope-domain questions to the user.
- [ ] Phase 3 explicitly tells agents to READ existing task goal.md files
      before flagging "is this obsolete?" questions.
- [ ] Phase 3 task creation is unambiguous (one task per coherent AC group,
      via `task-create-code`).
- [ ] Phase 4 is marked MANDATORY with an explicit verdict format.
- [ ] Phase 5 reads only `final_coverage_check.md` and does not re-ask
      Phase 2 questions.
- [ ] Phase 6 explains why the orchestration task script may legitimately
      return Exit 3.
- [ ] New "Decision Domains" section gates the entire skill.
- [ ] Constraint table forbids orchestrator from reading feature
      requirements.md or invoking `task-create-code`.

## Risks

- **Risk: Edit breaks existing automation.** Mitigation: skill is invoked
  manually via `/release-begin-impl`; no automated callers depend on the
  exact prompts. Run `release-status` after the edit to check no scripts
  reference removed phrasing.
- **Risk: Phase 3 agents now have more autonomy and might create the wrong
  shape of impl task.** Mitigation: Phase 3 task creation explicitly delegates
  to the `task-create-code` skill, which has its own conventions and
  validation. The agent only chooses the AC grouping.
- **Risk: "One task per coherent AC group" is fuzzy.** Mitigation: include
  the heuristic ("group by domain layer when ACs touch the same entity;
  otherwise one task per AC") in the agent prompt template embedded in
  Phase 3.
- **Risk: Phase 4 mandatory gate slows the workflow when everything is
  already done.** Mitigation: the gap verification agent is one cheap call
  (10 small files); it's worth it to avoid Phase 5 confusion.

## Execution

**One agent**: `implementation-engineer` to apply Edits 1–8 to
`.claude/skills/release-begin-impl/SKILL.md`. The agent should use Edit/Write
tools precisely on the marked sections, preserving the rest of the file
verbatim.

After the agent completes, the orchestrator should:
1. Read the modified SKILL.md and verify all 8 edits are present.
2. Show the user the diff or a summary.
3. Wait for user approval before any further use of the skill.
