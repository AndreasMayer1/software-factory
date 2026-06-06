---
name: opus_synthesis_round_1
description: First Opus synthesis pass on the claude-optimize redesign problem space. Reframes the skill, walks each exploration thread, surfaces decisions for the user.
created: 2026-05-07
type: design_synthesis
author: claude-opus
session: 7e90a3be-126e-4e21-ab14-78cd3f18d323
---

# Synthesis: What claude-optimize Should Actually Be

> This is a problem-space exploration, not a specification.
> Companion document (web research, runs in parallel): `2026-05-07_02_web_research_external_knowledge.md`.

---

## 1. The One-Sentence Reframe

**`claude-optimize` is not an analysis skill. It is a *structured improvement-task generator* — a skill whose only output is one well-scoped task in the factory's existing task pipeline.**

The current framing ("analyze the last 5–10 tasks and produce an optimization report") tries to put both the *finding* and the *fixing* into one skill. That is what makes the design feel intractable: it forces the skill to read large amounts of data, synthesize patterns, propose changes, and somehow track whether changes worked — all in one step, in the limited context window of a single LLM call.

The factory already has a powerful improvement engine: itself. It has skills for modifying skills (`claude-modify-skill`), creating skills (`claude-create-skill`), modifying ordering rules, splitting docs, fixing bugs (`code-bugfix`), exploring requirements (`requ-explore`), updating doc/ guidelines (`doc-update-guidelines`). It has a task pipeline that orders, prioritizes, and executes work. It has Opus for synthesis and Sonnet for execution. It has memory, plans, protocols, status registries.

What it is missing is **a producer that points the engine at the right thing to improve next.**

`claude-optimize` should be that producer. It should answer one question per run: *"Given everything that has happened recently, what is the single most valuable improvement task to add to the queue right now?"* Then it creates that task — using `task-create` — and stops. The factory does the rest.

This single reframing dissolves most of the original problems:

| Original problem | Dissolved how |
|---|---|
| Token cost of reading 10 protocols | Don't read 10. Read 1–3 high-signal sources. Output is one task, not a report. |
| Context window overflow | The skill produces a small file (a `goal.md`), not a big synthesis. |
| Measurement of improvement | Each improvement task declares its own success criterion at creation; verification is the *follow-up* skill's job, not claude-optimize's. |
| History of past improvements | Git log + the existence of completed improvement tasks. No new data structure needed. |
| Re-improving the same thing | Search for completed improvement tasks before creating a new one (just a grep). |
| Apply vs propose vs report | Producing a task IS proposing — the user/orchestrator decides when to execute it. The autonomy decision moves out of claude-optimize. |
| Ripple effects of skill changes | Specified in the task's `goal.md`, evaluated by whichever skill executes the task. |
| Cross-cutting concerns | The improvement task's `type` and `parent_requirement` route it appropriately. |

The rest of this synthesis works through that reframe in detail.

---

## 2. The Identity Problem (resolved)

**Decision (proposed): claude-optimize is a *one-shot, idempotent task-producer skill*.**

Three legitimate trigger sources, all converging on the same output (one improvement task):

1. **Periodic** — auto-created by a small Python script after every N completed tasks (configurable, e.g. 10). The mechanism is the same `create_orchestration_task.py` pattern the user already cited as inspiration. The script writes a `goal.md` for `claude-optimize` itself, with `awaiting:` set so it doesn't show in `next_tasks.py` until something unblocks it (e.g., the script also runs the unblock check — "have N completions accumulated since the last optimize run?").
2. **Reactive** — a tiny set of monitor patterns auto-create the task: e.g., the same pending question repeated 3+ times across runs (S9 in MONITORING_CRITERIA.md), 2+ blocked tasks waiting >7 days, a skill change reverted within 48 hours. These are explicit pattern triggers, not an LLM-driven scan.
3. **Explicit** — the user runs `Use claude-optimize`. Same skill, same output, no special path.

The autonomous orchestrator **does not change** as a result. It just sees one more task in its queue when the trigger fires, runs it like any other task, and the task produces another task — which then queues normally.

This makes the skill a **leaf node in the workflow graph**, not a daemon. Daemons require state, supervision, and shutdown semantics the factory does not have. A leaf-node task-producer needs none of that.

---

## 3. The Signal Problem (the most important problem)

The single most important design decision is *what data the skill consumes per run*. Get this wrong and either the skill is too expensive (reads everything) or too shallow (sees nothing). The right answer is:

> **Cheap signals first. Rich signals only on demand. Never the JSONL files directly.**

Here is the proposed signal hierarchy, ordered from cheap to expensive — the skill walks down this list and stops as soon as it has enough to identify one improvement opportunity:

### Tier 0: Always-cheap structural signals (≤5KB total, always read)

| Source | What it tells you |
|---|---|
| `automation/state.json` (run_count, paused_tasks, question_fingerprints) | Friction patterns: same question repeated, paused tasks |
| `automation/pending_feedback/*/question.md` (recent only) | Where the system gets stuck waiting for humans |
| `requirements_tasks/STATUS.md` (open/blocked counts) | Macro-state: are tasks piling up somewhere? |
| `git log --since="N days ago" --oneline` filtered to `^.*skill\|^fix.*skill\|^chore.*skill` | What was *manually* optimized recently — these are the user's own optimization signals, the strongest training data |
| `automation/orchestrate.log` (tail 200 lines) | Recent friction events (rate limits, hung sessions, repeated resumes) |
| `MEMORY.md` index (already always loaded) | What durable feedback the user has already given Claude |

The git-log filter is particularly underrated. Every recent commit like `chore(claude-switch-opus): remove plan-template bias, make skill output-agnostic` or `chore(skills): fix requ-explore Opus mode` is a record of an optimization the user *had to do manually*. If `claude-optimize` had run, the user wouldn't have had to. **The user's manual interventions are the ground-truth training signal for what claude-optimize should automate.**

### Tier 1: Targeted reads (5–15KB total, read only if Tier 0 reveals a candidate)

| Source | When |
|---|---|
| The skill file mentioned in a recent fix commit | "What was problematic in this skill?" |
| The most recent 1–2 protocol files from a friction-flagged task | "What concretely went wrong here?" |
| `automation/answered_feedback/<task_id>/answer.md` (recent) | The user's actual disambiguation — gold data |
| The blocker file, if one exists in a stuck task's `plans_and_protocols/` | "Why is this stuck?" |

### Tier 2: Web research (only on explicit decision)

External best practices for the specific identified opportunity. Spawned as a subagent with a focused question, summary returned (not raw content). Same pattern this exploration task itself uses.

### Tier 3: Forbidden by default

- Session JSONL files. They are 100KB–1MB each. Reading even one would consume most of the available context window. They are useful for archaeology, not for routine optimization.
- Bulk reading of all 309 completed task folders. The aggregate is too large to be useful.

The skill should never need Tier 3 for routine work.

---

## 4. The "Better" Problem — multi-dimensional optimization needs explicit dimensions

The user is correct that "better for whom, on what timescale" must be answered *per opportunity*. The skill should not have a single optimization function. Instead, every improvement task it creates declares which dimension it optimizes:

```yaml
optimization_dimension: bugfix          # the skill is doing something wrong
                       | latency        # task takes too long / too many sessions
                       | token_cost     # excessive context use
                       | alignment      # skill doesn't match documented intent
                       | clarity        # skill is ambiguous, leading to drift
                       | coverage       # missing capability that's been asked for
                       | safety         # change reduces risk of corruption
```

These dimensions reflect the personas the factory serves:
- **Flutter app users** (via correct/timely features) → optimize for *correctness* and *coverage*
- **Solo developer / app provider** (via efficient development) → optimize for *latency*, *token cost*, *clarity*
- **System maintenance** (via robustness) → optimize for *safety*, *alignment*

The skill picks ONE dimension per task. This is enforced by the YAML field. Tasks that try to optimize multiple dimensions at once get split into separate tasks at next_tasks.py time — the factory already handles this pattern.

**Decision (proposed):** the skill never tries to balance multiple dimensions in one improvement. The user (via task ordering rules / priority field) implicitly weights them.

---

## 5. The Measurement Problem — defer it to the executing skill, not claude-optimize

This is the thread where the original framing did the most damage. The instinct is: claude-optimize must somehow verify that its changes worked. But this conflates two roles:

- **Producer of work** (claude-optimize): identifies opportunity, frames task, declares success criterion
- **Executor of work** (downstream skill, e.g. `claude-modify-skill`): applies the change, runs verification

If claude-optimize itself tried to verify its own past changes, it would need to maintain history, schedule re-checks, do A/B comparisons across non-deterministic LLM behavior — the bulk of the complexity in the original framing.

**Cleaner approach**: the improvement task created by claude-optimize includes, in its `goal.md`, an `acceptance_criteria` block where each criterion is verifiable at executor-completion time. Examples:

- Bugfix: *"Skill X no longer produces output Y when input is Z" (verifiable by running the skill once)*
- Latency: *"Task type Q completes with ≤K sessions in autorun (verifiable by orchestrator log over next 10 runs)"*
- Clarity: *"Skill description triggers correctly on prompt set P, fails to trigger on negative set N" (verifiable by skill-creator's eval harness)*

If a criterion cannot be made verifiable, the task is rejected before it's queued — claude-optimize falls back to the next-best opportunity.

The follow-up question — *"are we improving on net?"* — is answered by trend-watching the ratio of `chore(...)`/`fix(skills)` commits over time. That is a separate, lightweight skill (not claude-optimize) that the user could run whenever they want a vibe-check. We should not overload claude-optimize with that role.

---

## 6. The History Problem — solved by what the system already has

The user worried about the skill re-improving things repeatedly and needing a log of past improvements. But:

- **Git log is the improvement log.** Every change to a skill file is a commit. `git log .claude/skills/claude-optimize/skill.md` answers "what has been done to this skill?" perfectly.
- **Completed task folders are the improvement-task history.** Search for past `tasks/*_impl_optimize-*` or `tasks/*_explore_optimize-*` under `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/` and `factory_quality/`.
- **MEMORY.md** holds the user's durable feedback that has *not yet* been codified into skills. This is also a candidate signal for claude-optimize: "this feedback has been saved 3 times — codify it into the skill."

**Decision (proposed): no new data structure for improvement history.** The skill's first action when it picks an opportunity is to grep recent commits and recent task folders for evidence that the same change was already attempted. If found, the candidate is rejected and the next-best is selected. This is bounded and cheap.

Saturation detection (the user's "improvements get smaller and smaller") falls out for free: if 3 of the top-5 candidates are already-attempted, the skill writes a "saturation reached" note and creates no task. This is the natural exit condition.

---

## 7. The Classification Problem — bugfix vs optimization, and what each implies

The user's intuition that there are two paths is correct and consequential. The proposed taxonomy:

### Path A: Bugfix (high-confidence, definition-grounded)

Trigger: clear discrepancy between documented behavior (a skill, a doc/, a requirement) and observed behavior. Examples:
- A skill says "Sonnet must not pre-synthesize" but the recent run shows pre-synthesis in the output (already in MEMORY.md as `feedback_requ_explore_opus_mode_flaw.md` — exactly this case)
- A skill says it must call `claude-log` at the end, but the protocol files show no log entries
- An ordering rule says X before Y, but `next_tasks.py` produced Y before X

Output: a `code-bugfix` task or a small `claude-modify-skill` task. Web research skipped. Success criterion is binary (the discrepancy is gone).

### Path B: Optimization (lower-confidence, judgment-grounded)

Trigger: a pattern that *suggests* improvement but is not a clear violation. Examples:
- The same question is asked repeatedly across tasks (suggests skill ambiguity, not a bug)
- A skill takes 3+ sessions to complete on autorun (suggests phase reorganization)
- A skill description fails to trigger when it should (suggests rewording)

Output: a `requ-explore` (if the optimization needs design) or `task-resolve` task. May include web research as part of execution. Success criterion is harder, often probabilistic.

**Decision (proposed):** the skill prefers Path A whenever a bugfix candidate exists, even if a more interesting optimization candidate exists. Bugfixes are cheap, low-risk, additive in spirit, and produce immediate value. Optimizations are sometimes the right answer — but only when no bugfix is available, OR when the optimization has been deferred 2+ runs already (a fairness rule).

The classifier itself is a Tier 0 decision. The skill checks a small ruleset:
1. Does any commit in the last 5 days mention a skill in passing as having a bug-like issue? → Path A candidate
2. Does any answered_feedback contain the user contradicting a skill's claim? → Path A candidate
3. Does MEMORY.md have a feedback memory from the last 14 days that is not yet codified in the named skill? → Path A candidate
4. Otherwise, fall through to Path B candidate selection

---

## 8. The Autonomy Problem — disappears with the reframe

Original question: should the skill apply changes immediately, propose and wait, or just produce a report? The reframe makes this a non-question:

- **claude-optimize never applies changes.** It produces a task. The task is the proposal.
- **The task is then executed by the existing factory.** In automated mode, the orchestrator picks it up and runs it via the appropriate skill (`claude-modify-skill`, `code-bugfix`, etc.). In supervised mode, the user can review and run it manually.
- **Approval-required changes already pile up as unanswered questions.** The factory already has this pattern. claude-optimize doesn't need to invent a new approval mechanism. If the executor skill needs human input, it writes a `pending_feedback` question. Same as everything else.

This means full autonomy IS safe — but only because the change is gated by the executor skill, which can stop and ask the user. claude-optimize itself only commits to *creating a task*; that's a low-risk action.

The remaining question is whether claude-optimize needs a "dry run" mode where it produces only a recommendation and not a task. Recommended: yes, as a flag (`--no-create`), used when the user is just exploring. Default is to create.

---

## 9. The Scheduling/Trigger Problem — three triggers, one entry point

Already covered in §2. Concretely:

### Mechanism: a tiny Python script auto-creates the optimize task

```
scripts/optimize/create_optimize_task_if_due.py
```

It runs on a hook (e.g., post-task-complete) and checks:
- How many tasks have been completed since the last optimize task ran? If ≥N (default 10), create one.
- Are any reactive trigger patterns active? If yes, create one (with a flag indicating which pattern).

The script writes a `goal.md` under `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/[date]_explore_claude-optimize-cycle-[N]/goal.md`.

The task's `goal.md` body is essentially: *"Run the claude-optimize skill. Produce one improvement task following its protocol."*

When the orchestrator picks the task up, claude-route routes it to `claude-optimize`, the skill runs, produces a child task, and exits. `task-complete` closes the optimize task. The child task is now in the queue.

### Why a hook is better than `awaiting:`

The user's note about `next_tasks.py` not surfacing tasks with `awaiting:` is correct — but it cuts both ways. We *don't want* the optimize task to be queued before it's due. The script approach (only create when due) is cleaner than the awaiting-graph approach (always exists, hidden until unblocked).

### The interaction with autorun is benign

The orchestrator runs whatever the queue gives it. If the optimize task is in the queue, it gets executed. If it's not, the orchestrator runs other tasks. No special handling needed in the orchestrator. The skill is just a regular task.

---

## 10. The Scale/Cost Problem — bounded by design

The reframe makes this trivial. The skill's run consumes:
- Tier 0 reads (~5KB) — always
- Tier 1 reads (~15KB) — if a candidate emerges
- One LLM round of synthesis to choose ONE opportunity
- One LLM round to write the child task's `goal.md`
- One `task-create` call

Total cost per run: comparable to a small `requ-explore` invocation. This is by far the cheapest skill in the system that produces lasting value.

If the skill ever feels expensive, the design is wrong — go back to the Tier hierarchy and constrain harder.

---

## 11. The Ripple Problem — pushed to the executor

claude-optimize doesn't reason about ripples. It identifies a candidate and creates a task. The executor skill (e.g., `claude-modify-skill`) is responsible for ripple analysis when it edits a skill — it already does this via the `factory_flows.md` sync step.

What claude-optimize *can* do, cheaply, is annotate the task with a "blast radius hint":
- If the change targets a skill listed in INDEX.md as Layer 0 (primitives like claude-log) → blast_radius: high
- Layer 1 (artifact workers) → medium
- Layer 2 (orchestrators) → high (touches many)
- Layer 3 (meta) → medium-high (changes the system itself)

This hint feeds the priority/urgency of the resulting task, but does not change what claude-optimize does.

---

## 12. The TASK-PROC-044 Relationship — work without it, leverage it when ready

The factory-quality task identifies an observability layer (Option D) that would extend `claude-log` to record per-skill outcomes, plus an aggregator that claude-optimize could read. This would be a richer Tier 0 signal than what exists today.

**Decision (proposed): claude-optimize ships *now* with the signals that exist today (git log, state.json, pending_feedback, MEMORY.md, orchestrate.log). When TASK-PROC-044 unblocks and Option D ships, claude-optimize gains a new Tier 0 source — but its design does not change.**

This is the additive principle from the factory-quality strategic analysis: don't make the new skill depend on infrastructure that may never ship. Make it work today, and let it grow capabilities as infrastructure becomes available.

The corollary: claude-optimize itself may identify that TASK-PROC-044 should be unblocked. If the same friction patterns keep recurring without metrics, the skill can produce a task whose body says "we need observability data to keep optimizing — recommend unblocking TASK-PROC-044-01."

---

## 13. External Knowledge Reference

A web research subagent is producing `2026-05-07_02_web_research_external_knowledge.md` in parallel. Expected to cover: DSPy / Reflexion / Voyager / Self-Refine patterns, what fails in self-modifying systems, measurement approaches, and skill-creator's specific approach. The synthesis here intentionally does not depend on those findings — they will inform refinements in a possible round 2, not the core architecture.

The most likely transferable insight from prior art: *self-modifying systems consistently fail when they try to reason about themselves with the same model that produces them.* The factory-quality analysis already absorbed that lesson (the "additive not substitutive" principle). The reframe in §1 is consistent with it: claude-optimize doesn't reason about its own outputs — it produces tasks and stops.

---

## 14. The Recommended End-State Walkthrough

A single optimize cycle, end-to-end:

1. **Trigger**: orchestrator completes task #N, post-complete hook runs `create_optimize_task_if_due.py`. Counter says it's been 10 tasks. Script writes a new `tasks/2026-05-15_explore_optimize-cycle-9/goal.md` for `claude-optimize`.

2. **Pick-up**: next orchestrator iteration picks up the optimize task. Routes via `claude-route` → `claude-optimize` skill.

3. **Tier 0 read**: skill reads ~5KB of cheap signals. Emits a small inline summary of friction it observed.

4. **Classification**: skill applies the bugfix-vs-optimization classifier. Picks Path A (bugfix) because git log shows a recent commit `fix(skills): X` that mentions skill Y, and skill Y's protocol file from yesterday's task shows the exact pattern recurring.

5. **Saturation check**: skill greps recent task folders for "skill Y" + "fix" — finds nothing in the last 30 days. Candidate is fresh.

6. **Tier 1 read**: skill reads skill Y's current text and the relevant protocol section. Confirms the discrepancy.

7. **Task creation**: skill invokes `task-create` with:
   - type: impl
   - parent_requirement: REQ-PROC-006
   - body: "Skill Y currently does X but should do W per documented behavior. Apply minimal change to skill Y, verify with [acceptance criterion]."
   - optimization_dimension: bugfix
   - blast_radius: low
   - acceptance_criteria: a single binary criterion

8. **Self-complete**: `task-complete` closes the optimize task. Output line: "Created task TASK-PROC-006-NN; bugfix path; skill Y; verifiable."

9. **Downstream**: orchestrator picks up the new task on next iteration, runs `claude-modify-skill` (or `code-bugfix`) which applies the fix and verifies. If verification fails, the executor task creates a `pending_feedback` question. Loop.

10. **Trend visibility** (separate, occasional): user runs a one-off `Use claude-vibe-check` or similar to see the rate of fix-vs-optimize tasks over the last 30 days. If the trend is improving, the system is working. If not, escalate.

---

## 15. Decisions for the User Before Implementation

These are the decisions that I cannot make from the gathered facts alone — they are user-level product/strategic calls.

**D1. Acceptance of the reframe.** Is "claude-optimize is a task-producer, not an analyzer" the right shape? If the user wants the skill to *also* produce a periodic written report (for human reading, not for downstream tasks), that is a different feature and should probably be a separate skill (`claude-vibe-check` or similar).

**D2. Default trigger cadence.** Every 10 completed tasks is a guess. Should it be 5? 20? Based on session count or task count? The right answer depends on how often the user wants the system to spend tokens on self-improvement.

**D3. Reactive trigger set.** Which monitoring patterns should auto-create an optimize task? Proposed minimal set: same question repeated 3+ times, blocked task >7 days, skill change reverted within 48 hours. The user may want more (or fewer).

**D4. Path-A preference rule.** I propose claude-optimize always prefers bugfixes. The user may want a more balanced policy (e.g., 70% bugfixes, 30% optimizations) or have a specific phase where structural improvements are preferred.

**D5. Bootstrap with what exists vs. wait for TASK-PROC-044.** Proposed: ship claude-optimize now with current signals. The user may prefer to unblock TASK-PROC-044 first to get observability and ship a more capable claude-optimize.

**D6. The optimization_dimension taxonomy.** The seven dimensions proposed in §4 are a starting point. The user may want different categories or a coarser binary (correctness / efficiency) split.

**D7. Saturation policy.** When the skill detects saturation (no fresh candidates), it should write a "saturation note" and exit. Should that note: (a) be a memory entry, (b) be a status file, (c) be a task asking the user to provide direction? Proposed: (a) for the first time, (c) if saturation persists across 3+ consecutive runs.

**D8. Whether claude-optimize should ever modify CLAUDE.md.** CLAUDE.md is the constitution. Proposed: claude-optimize can produce tasks that modify CLAUDE.md, but the executor skill must require user approval (no auto-merge in automated mode). The user may want a stricter rule: never produce CLAUDE.md changes at all, only skill changes.

---

## 16. What REQ-PROC-006 Should Say If Rewritten Today

> **The current REQ-PROC-006 conflates the engine (the optimization mechanism) with the artifact it produces (an "optimization report"). It also embeds metric choices (code coverage, test results, completion time, user surveys) that don't make sense for a skill-improvement system in a one-developer factory.**

A rewritten requirement would say something close to:

```
Title: Continuous, low-overhead improvement of the Software Factory's own skills

User story: As the developer running this factory, I want the system to
periodically and reactively identify the highest-value next improvement to its
own skills, and queue that improvement as a regular task in the factory's
pipeline — so that the factory steadily becomes more reliable, more efficient,
and better aligned with my actual feedback, without me having to monitor it.

The system shall:
- produce one improvement task per run, not a multi-finding report;
- consume only cheap structural signals by default (git log of skill changes,
  state.json, pending_feedback summaries, MEMORY.md, orchestrate.log tail);
- read deeper signals only when a candidate has been identified;
- prefer bugfix candidates (clear behavior discrepancies) over optimization
  candidates (judgment calls);
- declare a verifiable acceptance criterion on every task it produces;
- detect saturation (no fresh candidates) and exit cleanly;
- never apply changes itself — produce tasks for the existing factory pipeline
  to execute.

The system shall NOT:
- maintain its own improvement history (use git log + completed task folders);
- attempt to verify its own past changes (each task verifies itself at
  execution time);
- read session JSONL files in routine operation;
- block on user approval (the executor skills handle approvals, not the
  producer).
```

Acceptance criteria, as end-states:
- A claude-optimize run produces exactly one new task in the factory pipeline.
- The produced task has an `optimization_dimension`, a `blast_radius` hint, and an `acceptance_criteria` block where every criterion is verifiable at execution time.
- A claude-optimize run consumes ≤30KB of file content in routine operation.
- Saturation is detectable: when no fresh candidate exists, the skill exits without producing a task and records the saturation in MEMORY.md.
- The skill is reachable via three triggers: periodic (post-complete hook), reactive (monitor patterns), explicit (user invocation) — all routing to the same skill body.

The current REQ-PROC-006 should be marked superseded; the new requirement is in the same folder with a fresh number.

---

## 17. What Was Ruled Out (and why)

- **A long-running daemon process.** Adds operational complexity (supervision, restart, state). The factory has no daemons; introducing one for self-improvement is disproportionate. Rejected in favor of the task-producer pattern.
- **Reading session JSONL files routinely.** Cost is too high; signal density is too low. The same information is available in summarized form in protocol files and session_outputs. Reserved for archaeology only.
- **A single optimization metric ("the score").** No single metric captures the multi-dimensional nature of factory improvement. A taxonomy of dimensions is honest about the trade-offs.
- **A separate "improvement history" data structure.** Git log and task folders already serve this purpose. New data structures would drift and become liabilities.
- **A "skill changed → re-evaluate the change in 7 days" mechanism inside claude-optimize.** This is a measurement-as-the-skill's-job feature; it would balloon the design. If needed, a separate post-mortem skill should own this.
- **Auto-applying skill changes without an executor task.** The factory's safety model relies on each task having a discrete plan, protocol, and commit. Bypassing that for "small" changes is the start of the slippery slope to silent corruption.
- **A complete rewrite of CLAUDE.md by claude-optimize.** Out of scope. CLAUDE.md is the constitution; constitutional change should remain explicit user work.

---

## 18. Honesty Section: What I Don't Know

- **Whether the proposed Tier-0 signal set is rich enough to identify good candidates often.** It might be that 7 of 10 runs find no candidate and exit. If so, the cadence (D2) needs to drop or the trigger rules need to tighten. Only running it for some weeks will reveal this.
- **Whether the bugfix-first policy will starve real optimizations.** The user may experience the system as "always making tiny corrections, never restructuring." If that happens, D4 needs revision.
- **Whether the verifiability constraint on acceptance criteria is too strict.** Some valid optimizations (clarity rewrites, prompt rewordings) have acceptance criteria that are inherently fuzzy. The skill might reject them and starve a real improvement axis. May need a "judgment-call" criterion type that explicitly accepts fuzziness, with the trade-off documented.
- **Whether the saturation policy works in practice.** If the skill detects saturation but the system is actually still suboptimal in ways we can't see, the saturation note becomes false reassurance. The user should treat saturation as a signal to widen Tier-0 sources, not as proof of perfection.
- **The right interaction with `claude-modify-skill`.** That skill is the most likely executor. It currently expects user direction; it may need a new "executing-from-claude-optimize-task" mode where the goal.md is sufficient direction. This is an implementation detail but a non-trivial one.
- **External knowledge.** The web research subagent's results are not yet incorporated. They may surface concrete prior-art patterns that should change parts of this synthesis (likely §3 signal hierarchy and §5 measurement). A round-2 synthesis after the research is integrated is recommended before writing the requirement.

---

## 19. Suggested Next Steps for the Task

1. **Round 2 synthesis** — incorporate web research findings. Likely a small delta to §3 and §5; the architecture in §1 is unlikely to change.
2. **User review of decisions D1–D8** — these are the gates. Without them, the requirement cannot be written confidently.
3. **Then** write the new REQ-PROC-006 (or a new REQ in the same folder, marking the old one superseded).
4. **Then** the implementation work splits naturally into 3–4 small tasks: (a) the trigger script, (b) the redesigned skill body, (c) optional integration with TASK-PROC-044's observability layer when it lands, (d) the saturation/trend mini-skill.

If the user wants to defer (1) and approve based on what we have, that is also reasonable — the architecture is robust enough that the web research is unlikely to overturn it.
