---
name: opus_synthesis_round_3
description: Round-3 synthesis. Addresses the user's feedback in 2026-05-15_04_feedback.md. Removes the OS-memory dependency, tightens detection rules, designs the auto-block default, the web-research integration, the periodic-execution mechanism without OS hooks, and the analysis companion skill.
created: 2026-05-16
type: design_synthesis
author: claude-opus
session: TASK-PROC-006-02 round-3
references:
  - 2026-05-07_01_opus_synthesis.md
  - 2026-05-07_02_web_research_external_knowledge.md
  - 2026-05-07_03_opus_synthesis_round2.md
  - 2026-05-15_04_feedback.md
---

# Round-3 Synthesis: Refining Detection, Removing the Memory Dependency

> Delta against rounds 1 & 2. Things not mentioned here are unchanged (the task-producer reframe in §1 of round-1 still holds, the producer/executor split in §A of round-2 still holds, the ground-truth-first verification preference still holds).

The opening of your feedback is the most important sentence in this round: *"Ich denke, gerade die Erkennung, ob ein Task anzulegen ist, braucht noch Verbesserungen."* — the detection step (deciding *whether* to create a task at all) is the weak link in rounds 1 & 2. This round treats detection as the central design problem, not a side note.

---

## Part 1 — Hard reversals forced by your feedback

These flip earlier decisions completely. They cascade through the rest of the design, so they come first.

### 1.1 OS-level memory is unusable as substrate

**Round-1 §3 / round-2 §B4** assumed `MEMORY.md` and the `memory/feedback_*.md` files were both an input *and* an output for claude-optimize. That assumption is broken: the factory rotates across three Claude accounts (`web`, `aiwiz`, `aiwiz1` — visible from the per-account paths under `/home/vscode/.ccs/instances/<account>/`), and each account's memory directory is **separate and never synchronized**. Whichever account happens to launch the next session sees a different MEMORY.md than the previous one wrote.

Concrete consequence: the saturation-tracking output (round-2 §B4, D11), the "what feedback hasn't been codified yet" Tier-0 input, and the no-op trend tracking all fail silently. They appear to work in the session that writes them, then disappear from the next session's view.

**Decision (proposed): claude-optimize neither reads from nor writes to the per-account OS memory.** Everything that round-1/2 treated as "memory" moves to a project-local, committed location:

```
automation/optimize/
├── state.json             # mutable state: last_run_ts, completions_since_last_run,
│                          #   no_op_streak, last_run_commit_sha
├── events/                # candidate events written by monitors (see §2.2)
│   ├── 2026-05-16T08-12-pending-question-S9-<fp>.json
│   ├── 2026-05-16T09-30-skill-changed-first-used-<sha>.json
│   └── ...
├── history/               # one-line summary per run, append-only, human-readable
│   └── runs.tsv           # ts \t outcome \t target \t dimension \t notes
└── README.md              # what's in here and why; pointer to the skill
```

This is committed to the repo, so all three accounts see the same state. It is also the foundation for the analysis companion skill (§2.5), which reads `history/runs.tsv` plus git history to report on the optimizer's own effectiveness.

There is a maintenance cost (the user flagged: "wieder Wartungsaufwand, da die sich dann periodisch auch wieder löschen müssen"). The mitigation:

- `events/` is **consumed-then-deleted** by each optimize run. Stale events older than 30 days are pruned at run start. There is never a long-lived events backlog.
- `history/runs.tsv` is append-only and intended to grow — but each row is ~100 bytes. 1000 runs is 100 KB. Not a concern.
- `state.json` is small and overwritten in place. No growth.

So the only "memory pollution" risk is in `events/`, and the consume-then-delete pattern bounds it.

### 1.2 The "blocked task >7 days" trigger is removed

You're right: the project deliberately defers many tasks. The factory's blocked queue is in the dozens at any moment and has been for weeks. A trigger that fires whenever 2+ tasks are blocked >7 days would fire every single time, drown signal in noise, and erode trust.

**Decision (proposed): D3's trigger set drops the blocked-task rule entirely.** What remains:

| Trigger | Status | Notes |
|---|---|---|
| Same pending question fingerprint repeated 3+ times (S9) | **Kept** | Strongest reactive signal — the system is literally re-asking the same thing |
| Skill change followed by first use of that skill | **Kept, refined** | See §2.2 — the "first use" part is the key refinement |
| Skill change reverted within 48 hours | **Kept** | A reversion is a stronger signal than a change (someone tried and undid it) |
| Blocked task >7 days | **REMOVED** | Too many false positives in this factory's normal mode |
| Periodic safety net (every N completed tasks) | **Kept** | N starts at 10, configurable (your call) |

The set is now narrower but every remaining trigger is high-signal.

### 1.3 Produced tasks are auto-blocked by default (not "first 30 days")

Your feedback on §8 and D10 collapses them into one rule:

> *"Gefährlich wird es aber dann, wenn der Autoran aktiv ist und diese Tasks ausgeführt werden, ohne dass der Nutzer anwesend ist."*

The round-2 "proposal-only mode for the first 30 days" was a graduation plan. You're asking for a permanent default: every task claude-optimize creates is born **blocked**, with an explicit `awaiting:` entry that requires you to remove it. The autorun never picks the task up until you've consciously unblocked it.

**Decision (proposed): every claude-optimize-produced task has frontmatter:**

```yaml
awaiting: [user_unblock_optimize_proposal]
awaiting_note: "Created by claude-optimize <run-id> on <date>. Review proposal and remove this awaiting entry to queue."
```

This uses the factory's *existing* blocking mechanism (`next_tasks.py` already excludes tasks with non-empty `awaiting:`). No new infrastructure is needed.

**Implication for the deny-list (D9):** the deny-list shrinks in importance once auto-block is default. The deny-list was the round-2 hard guardrail against the optimizer neutering its own oversight in autonomous mode. With auto-block, the user is *always* in the loop before execution, so even a malicious proposal is caught at review time. The deny-list becomes a defense-in-depth measure, not the primary control. It still belongs (cheap to enforce, prevents the optimizer from generating obvious garbage proposals you'd just reject anyway), but it is no longer load-bearing.

Round-2's decision D8 ("can claude-optimize ever modify CLAUDE.md?") collapses cleanly: yes, it may propose CLAUDE.md changes, but those proposals are auto-blocked like everything else and require your explicit unblock.

### 1.4 Skill-change trigger requires *first-use-after-change* detection

You accepted skill changes as a trigger but added the right constraint: a skill change isn't a real signal until something actually runs the new version. A skill edited and never used is a dead-letter office — the optimizer wasting cycles checking whether it works is pointless.

This is a non-trivial detection problem. §2.2 below works it out in detail. The short answer: it requires either parsing session JSONL files (expensive, fragile) or instrumenting protocol files to log `skills_used:` (cheap, requires a small `claude-log` change). The latter is the recommended approach but introduces a **chicken-and-egg**: claude-optimize needs the instrumentation to detect first-use; the instrumentation requires its own task to land first.

**Decision (proposed): the skill-change-with-first-use trigger ships in two stages:**

- **Stage 1 (initial release of claude-optimize):** skill-change trigger fires *as soon as the commit lands*, not waiting for first use. This will produce false-positive runs (the skill picks up the recent change, fails to find evidence of misbehavior, exits as no-op). False-positives are *cheap* (cost of one no-op run) and *visible* (logged in `history/runs.tsv`).
- **Stage 2 (after the instrumentation task lands):** the trigger fires only when at least one session has used the changed skill. The instrumentation task is queued as a normal task, not blocking claude-optimize itself.

This avoids the chicken-and-egg without losing the trigger.

### 1.5 Bugfix-first is strict — no fairness rule

Round-1 §7 / D4 proposed a fairness rule ("defer optimization after 2 consecutive runs"). You said: *"Nein, immer Bugfixes zuerst."*

**Decision (proposed): D4 is updated. Strict bugfix-first.** If any bugfix candidate exists, the optimizer picks it. Optimization candidates only ever fire when the bugfix queue is empty. There is no "fairness" / "starvation prevention" carve-out.

The downside (real optimizations may be deferred indefinitely if bugs keep being introduced) is accepted as a feature: it means the bug-introduction rate is the natural pacing signal for whether optimizations should happen at all. If we are still finding bugs, we are not ready to optimize.

---

## Part 2 — New design elements added in this round

### 2.1 `automation/optimize/` — the project-local memory replacement

Detailed in §1.1 above. The relevant *new* surface area is summarized here for the implementer:

| Path | Purpose | Lifecycle | Read/written by |
|---|---|---|---|
| `automation/optimize/state.json` | counters, last-run ts, no-op streak | overwritten each run | claude-optimize, monitors |
| `automation/optimize/events/*.json` | one file per detected trigger event | consumed-then-deleted; 30-day prune | written by monitors, read+deleted by claude-optimize |
| `automation/optimize/history/runs.tsv` | one-line append-only log of every run | append-only, never pruned | written by claude-optimize, read by the analysis skill (§2.5) |
| `automation/optimize/README.md` | human-readable overview | static, edited rarely | one-time write |

Critically, `events/` files are written by the *monitors* (small scripts described in §2.2), not by claude-optimize. The skill body's job is to drain the events folder, pick one, and produce a task. This separation matters: monitors run cheaply on every task-complete; the LLM-driven skill runs only when there is something to do.

### 2.2 Detection mechanism v2 — monitor scripts produce candidate events

This is the structural change that addresses your "Erkennung braucht Verbesserungen" concern.

**Round-1 had the skill itself do all detection.** Every claude-optimize run had to re-discover candidates from raw signals. This conflates two jobs: cheap continuous monitoring vs. expensive single-shot selection. Splitting them is cleaner and more inspectable.

**Round-3 architecture: monitors → events → skill picks one.**

```
              ┌─────────────────────────────────┐
              │   task-complete (existing hook) │
              └───────────────┬─────────────────┘
                              │ every time a task finishes
                              ▼
         ┌────────────────────────────────────────────┐
         │  scripts/optimize/run_monitors.py          │ ← cheap, runs every time
         │  (fast: <2s; pure Python, no LLM)          │
         │                                            │
         │  Runs each monitor in turn:                │
         │    • monitor_repeated_question.py          │
         │    • monitor_skill_change_first_use.py     │
         │    • monitor_skill_change_reverted.py      │
         │    • monitor_periodic_counter.py           │
         │                                            │
         │  Each writes events/<name>.json on hit.    │
         └───────────────┬────────────────────────────┘
                         │ if events/ non-empty AND no claude-optimize
                         │ task already pending → create one
                         ▼
         ┌────────────────────────────────────────────┐
         │  scripts/optimize/create_optimize_task.py  │ ← creates the goal.md
         │  (sets awaiting: [] — the optimize task    │
         │   itself runs autonomously; only its       │
         │   downstream proposals are auto-blocked)   │
         └───────────────┬────────────────────────────┘
                         │ next orchestrator iteration
                         ▼
         ┌────────────────────────────────────────────┐
         │  claude-optimize skill (the LLM step)      │
         │                                            │
         │  1. Read events/*.json — pick highest-     │
         │     priority candidate (bugfix > optim;    │
         │     S9 > skill-change-first-use > periodic)│
         │  2. Tier-0 + Tier-1 read for that one      │
         │     candidate only                         │
         │  3. Produce one of: improvement task       │
         │     (auto-blocked), or saturation note     │
         │  4. Touch state.json + history/runs.tsv    │
         │  5. Delete consumed events/*.json          │
         │  6. Commit (§2.6)                          │
         └────────────────────────────────────────────┘
```

The monitors are the part the user can audit and trust. They are individually small, easy to test, and produce structured events. The LLM only runs when at least one monitor has fired.

#### 2.2.1 monitor_repeated_question.py

Reads `automation/state.json` (which already tracks question fingerprints per S9). When a fingerprint hits count ≥ 3, writes:

```json
{
  "type": "repeated_question",
  "trigger": "S9",
  "fingerprint": "<hash>",
  "first_seen": "<ts>",
  "task_ids": ["TASK-...", "TASK-..."],
  "skill": "<skill name from question.md frontmatter>",
  "question_text_excerpt": "<first 200 chars>"
}
```

Idempotent: refuses to write a second event for the same fingerprint within 14 days.

#### 2.2.2 monitor_skill_change_first_use.py — the tricky one

This is the monitor the user explicitly flagged as hard. The design has two layers:

**Layer A (Stage 1, ships immediately):** detect skill changes via git, fire immediately.

```python
# Pseudocode
recent_commits = git log --since="14 days ago" -- .claude/skills/
for commit, files in recent_commits:
    if commit_already_recorded_in(history/runs.tsv): continue
    for skill_file in files:
        write event { type: skill_changed, commit, skill, files }
```

This is the trivial version. False positive rate: high — many skill changes don't need optimizer attention because the change was already verified by the change author.

**Layer B (Stage 2, ships after the instrumentation task lands):** add the first-use gate.

The instrumentation task — call it `TASK-PROC-006-NN-instrument-protocol-skills-used` — modifies `claude-log` (or `task-complete`) to append a line like:

```
skills_used: claude-route, requ-explore, claude-log, task-complete
```

…to every protocol file at session close. With that in place, the monitor becomes:

```python
recent_skill_commits = git log --since="30 days ago" --name-only -- .claude/skills/
for commit_sha, skill_paths in recent_skill_commits:
    if event_already_written_for(commit_sha): continue
    if not any_protocol_file_after(commit_ts, has_skills_used_containing=skill_paths):
        continue   # not yet used → skip
    write event { type: skill_changed_and_used, commit_sha, skill, sessions }
```

Cost: grepping protocol files for a literal substring is ~milliseconds. The instrumentation task is ~30 lines of Dart-style edits to one skill file. Total runway cost: low.

**Why this works:** the user's intuition that "wir müssen schauen, ob das funktioniert hat" maps directly to *first* needing to detect that a real session actually exercised the changed skill. Without that, "did it work?" is unanswerable.

There is a residual problem: even after first-use is detected, *what does claude-optimize actually check?* That is §3 below.

#### 2.2.3 monitor_skill_change_reverted.py

Cheap: walks git log for `.claude/skills/*` and looks for a file diff that matches a recent revert pattern (file X edited at time T, then edited again at T+δ < 48h to substantially undo the change). Heuristic: a commit whose message starts with `revert`/`fix`/`hotfix` and that touches the same file as a commit in the last 48h, where the net diff is < 30% of the original change. Writes an event.

This is the strongest signal class. A reversion means the original change was wrong in a way that the change author *and* a reviewer (you, in this factory) caught. The skill's job here is usually "ensure the lesson learned is codified somewhere" — typically a follow-up task to update doc/, a test, or another skill that should have prevented the bad change.

#### 2.2.4 monitor_periodic_counter.py

Counts `completed` task folders. When `(current_count - last_optimize_run_count) >= N` (N=10 default, in `state.json`), writes a periodic event. This is the safety net: it guarantees the optimizer runs at least every N tasks even when nothing else triggers.

The periodic trigger event is the *weakest*. It is always sorted last in the priority order, so it only "wins" if no other event fired. Most periodic events will result in saturation no-ops at steady state. That is expected and healthy (round-2 §C1: target 30–60% no-op rate).

### 2.3 Web research is per-produced-task, not per-optimize-run

You asked: *"wie ist das mit der Webrecherche für Best Practices, wenn man irgendwelche Probleme findet?"*

The cleanest answer: **claude-optimize itself never does web research.** Web research happens (or doesn't) in the **downstream task** that claude-optimize produces, and the produced task declares whether research is part of its execution.

The mechanism: each produced `goal.md` carries an `optimization_approach` block:

```yaml
optimization_approach:
  web_research_recommended: true | false
  web_research_query: "<one focused question to ask>"   # only if true
  reason: "<one line explaining why research is/isn't worth it>"
```

When the downstream executor (`claude-modify-skill`, `code-bugfix`, `requ-explore`, `task-resolve`) reads the goal.md, it sees the recommendation and acts on it. None of those executor skills need to *decide* whether to research — claude-optimize already decided.

#### Heuristics for the recommendation

You noted, fairly: *"Das ist natürlich super schwer. … man weiß erst dann, wenn man eine Websuche gemacht hat, ob sie es gelohnt hat oder nicht."*

True. So the heuristic should err on the side of "yes" only when the cost-of-research is clearly justified by the nature of the candidate. Proposed rules (the skill picks the first rule that matches):

| Candidate type | `web_research_recommended` | Reason |
|---|---|---|
| Bugfix where the discrepancy is fully internal (skill says X, did Y, code is right there) | **false** | The answer is in the repo; web research adds noise. |
| Bugfix that mentions an external dependency (a CLI tool, a library, an API surface) | **true** | The bug may be a known issue; check before re-deriving. |
| Skill-description trigger-accuracy optimization | **true** | Anthropic publishes guidance on skill descriptions; worth a look. |
| Skill-body workflow / orchestration redesign | **true** | Prior art in agent-orchestration is rich and worth scanning. |
| Doc guideline rewrite | **false** | Internal style; no external authority. |
| Ordering-rule change | **false** | Project-specific; no external authority. |
| Anything matching "regression suite", "eval harness", "prompt optimization" | **true** | Mature external field. |

This is a starting taxonomy, deliberately conservative on "true." The user can edit the rule table later as evidence accumulates. The rules live in the skill body, not in a separate config file (one place to change them, no config drift).

#### Why not in claude-optimize itself?

Two reasons. **First**, claude-optimize is supposed to be a small, fast, idempotent producer — adding web search to its loop bloats its cost and makes runs less predictable. **Second**, when an executor task runs web research, it has the full context of *what it's about to change*. claude-optimize at proposal time only has the "what to change" framing. The executor is in a better position to ask a focused question.

### 2.4 Periodic execution: piggyback on `task-complete`, not OS hooks

Your concerns about portability (PC restart, VSCode start, dev-env swap) are real. The cleanest answer is to make the trigger *intrinsic to the factory* rather than extrinsic to the OS.

**Decision (proposed): the monitors run as the *last step* of `task-complete`.** Specifically: at the end of `task-complete`'s commit phase, call `scripts/optimize/run_monitors.py`. The script returns fast (target <2s), produces events to disk if any monitor hit, then optionally creates the optimize task (if events exist and no optimize task is currently pending).

This means:
- No OS hook needed
- No VSCode-specific hook needed
- No git commit hook needed (your hesitation about that was right — git hooks are not committed by default and don't survive a fresh clone)
- Works identically in autorun mode and interactive mode (both go through `task-complete`)
- Survives PC restart and dev-env swap (it's just a script call inside a skill that's already in the repo)

The trade-off: every task-complete becomes ~1–2s slower. Acceptable, especially since the monitors mostly do nothing and exit fast.

There is one edge case: a session that ends *without* `task-complete` (crash, kill, manual abandon). For those, the next successful `task-complete` will pick up the slack — completions are counted from git, not from a counter that increments per call, so nothing is lost.

### 2.5 The analysis companion skill — name and shape

You explicitly asked for a separate skill that audits the optimizer's effectiveness. Your suggested name `claude-analyze-optimizer` works; an alternative that fits the existing `claude-*` skill family is `claude-optimize-report` or `claude-optimize-audit`. The choice between them is cosmetic; I'll use `claude-optimize-audit` in the rest of this document, noting that the final naming is your call (recorded as N-D-2 in §5).

**What it does** (single invocation, on user demand):
1. Read `automation/optimize/history/runs.tsv` to enumerate every claude-optimize run.
2. Pull git history for each run's commit SHA: was a task created? Was that task executed? Was the execution accepted (merged) or reverted?
3. Compute aggregates:
   - run count, no-op rate, task-created rate
   - of tasks created: how many ran, how many were accepted, how many reverted, how many still blocked (user never unblocked)
   - mean lag from "task created" to "user unblocked"
   - per-monitor breakdown (which monitors are producing the most useful tasks vs. the most rejected proposals)
4. Output: a human-readable report (markdown) in `automation/optimize/reports/<date>_audit.md` plus a one-line summary printed to stdout.

This is **not** the same skill as claude-optimize, and it does not run on a trigger — the user invokes it when they want a checkup. It deliberately has no LLM-judgment role; it's pure reporting on what already happened.

The most important metric it produces is **"user-unblock rate"** — the fraction of created tasks that you eventually unblocked (vs. left dormant or deleted). If that rate is 70–90%, claude-optimize is well-calibrated. If it's 20–30%, the optimizer is generating mostly garbage and the trigger rules need tightening. If it's 100%, the bar is too low — every proposal is being accepted, which means the optimizer is too conservative.

The fact that this skill exists is part of why §2.6 (no-op commits) matters — without commits, this audit skill has no data.

### 2.6 No-op commits — forcing a paper trail

You asked: even when claude-optimize produces no task (saturation), it should commit. Reason: the audit skill (§2.5) reads git history; a run that left no git trace is invisible to the audit.

**Mechanism: the skill always writes `automation/optimize/history/runs.tsv` (append) and `automation/optimize/state.json` (overwrite), then commits both files**. On a no-op run, the runs.tsv line documents why it was a no-op:

```
2026-05-16T08:12Z  no-op  -  -  candidates_evaluated=2 rejected_reason=already_attempted_within_30d
2026-05-16T09:30Z  created  skill_body  bugfix  task=TASK-PROC-NNN-XX skill=requ-explore
2026-05-16T11:45Z  no-op  -  -  candidates_evaluated=0 trigger=periodic
```

The commit message follows the convention:

```
chore(optimize): run <id> [created|no-op] [<dimension>]
```

The state.json + runs.tsv touch is enough to make every commit non-empty. You suggested an alternative ("im Skill-Ordner eine Datei temporär anlegen") — that's also workable, but writing to `automation/optimize/` is cleaner because the audit skill already needs to read that folder.

### 2.7 TASK-PROC-044 Tier-0 source — explicit follow-up task

Your point on §12 is correct: the new observability data from TASK-PROC-044 doesn't appear automatically in claude-optimize once that task lands. There needs to be an explicit follow-up task that *extends* claude-optimize to read the new source.

**Decision (proposed):** create a follow-up task in the same task folder (`requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-MM-DD_impl_optimize-add-observability-source/`) with `after: [TASK-PROC-044-NN]`. It sits blocked until TASK-PROC-044 lands, then becomes runnable.

This is exactly the pattern the factory already uses for cross-cutting dependencies. No special handling needed.

---

## Part 3 — Detection mechanism — strengthening confidence

The user's opening concern needs a direct answer: *why should we believe this detection design will actually find good improvement opportunities?*

### 3.1 The honest assessment of what the round-2 design could detect

Looking at the round-2 trigger set with cold eyes:

| Trigger | What it would have caught in past factory operation? |
|---|---|
| Same question 3x | YES — the existing S9 monitor has caught real instances |
| Skill change reverted | YES — past `chore(skills): revert X` commits exist |
| Recent fix(skill) commit pattern | MAYBE — only if the fix didn't fully cover the bug |
| Blocked >7d | NO (false positives dominate) |
| Periodic | LOW VALUE — would mostly no-op |

So **2 of 5 triggers were reliably valuable, 1 was situational, 2 were noise.** That is the basis for your skepticism, and it is legitimate.

### 3.2 Tightened trigger set with explicit confidence labels

Round-3 carries each trigger with an explicit confidence label and a "what would the produced task look like" example. The user can scan this and judge whether the high-confidence triggers are worth shipping with.

| Trigger | Confidence | Produced-task example |
|---|---|---|
| Repeated question (S9 ≥3) | **High** | "Skill X's question phrasing is ambiguous (asked 3 times in 7 days about <topic>); rewrite question.md template to remove ambiguity. Acceptance: rerun under the original triggers; question not re-asked." |
| Skill change reverted within 48h | **High** | "Skill X commit <SHA1> was reverted in <SHA2>. Codify the reason: add a guideline note in doc/ or a precondition in the skill itself so the next change doesn't repeat the mistake." |
| Skill changed AND first-used (after instrumentation) | **Medium** | "Skill X was modified <date> and first executed in <session>. Verify the session output matches the documented behavior of the change; if not, file a follow-up." |
| Skill changed (Stage 1, no first-use gate) | **Low** | Same as above but most often no-op (no usage signal yet). Cost is acceptable. |
| Periodic (N completions) | **Low** | Mostly no-op. Catches drift the other triggers missed. |

The expected distribution: most run-time value comes from the High triggers. The Medium/Low triggers are net-positive but mostly produce no-ops or low-stakes tasks.

### 3.3 A safety valve: every produced task is auto-blocked anyway

Even if detection is too eager, the auto-block default (§1.3) means false positives are visible to the user as auto-blocked tasks. The user can spend 30 seconds reviewing a proposal and deleting it. That's a tolerable cost.

This means the *operational* failure mode of bad detection is "the user has to triage a few useless proposals per week," not "the system silently corrupts itself."

### 3.4 A measurement strategy that doesn't require a regression suite

The audit skill (§2.5) tracks the **user-unblock rate** as the primary signal of whether detection is calibrated. After 4–6 weeks of operation, the user runs the audit skill and either:
- Sees a healthy unblock rate (50–80%) — keep shipping.
- Sees a low unblock rate (<30%) — adjust trigger thresholds (e.g., bump S9 from 3 to 5).
- Sees an extremely high unblock rate (>90%) — consider loosening triggers (the optimizer is too conservative).

This replaces the regression-suite question (round-2 §B6) for the time being. A real regression suite (replayable task fixtures + LLM-judged outcomes) is still a worthwhile future investment, but it is not needed to ship a useful first version of claude-optimize.

---

## Part 4 — Updated answers to D1–D11 (with your input applied)

| Decision | Round-2 proposal | Your answer | Round-3 status |
|---|---|---|---|
| **D1** Reframe (task-producer) | Yes | Yes — but we also need an analyzer companion (§2.5) | **Accepted**; add `claude-optimize-audit` as separate skill |
| **D2** Cadence N | 10 | 10 to start, must be configurable | **Accepted as 10, configurable via `state.json` field `periodic_n`** |
| **D3** Reactive triggers | repeated-q + blocked + reverted | reject blocked; keep repeated-q; refine skill-change to require first-use | **Revised — see §1.2, §2.2** |
| **D4** Bugfix-first | with fairness rule | strict, no fairness rule | **Revised — strict** (§1.5) |
| **D5** Bootstrap now vs. wait for TASK-PROC-044 | bootstrap now | bootstrap now AND create explicit follow-up task | **Accepted with follow-up task** (§2.7) |
| **D6** Two-field taxonomy | yes | OK | **Accepted unchanged** |
| **D7** Saturation policy | exit cleanly; memory after 4th | exit cleanly; **no memory entry at all** | **Revised — saturation written to runs.tsv, not memory** (§1.1) |
| **D8** CLAUDE.md modifications | subsumed by D9 | proposals allowed, user must approve | **Resolved by auto-block default (§1.3)** |
| **D9** Write-surface deny-list | hard prohibition | accepted but no longer load-bearing once everything auto-blocks | **Accepted as defense-in-depth** (§1.3) |
| **D10** Proposal-only 30 days | 30 days then autonomous | **Auto-block always, never transition** | **Revised — permanent default** (§1.3) |
| **D11** Saturation memory entries | only on 4th consecutive | no memory ever | **Revised — runs.tsv only** (§1.1) |

The decision space is much smaller after this round. Most D-decisions are resolved.

---

## Part 5 — New decisions opened by this round

These are the choices that round-3 introduces and need your sign-off (or pushback) before implementation.

**N-D-1. Project-local state location.** Proposed: `automation/optimize/`. Alternatives: `.factory/optimize/`, `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/_state/`. Your call. I propose `automation/optimize/` because it lives next to the other automation state the user already maintains (`state.json`, `pending_feedback/`, etc.).

**N-D-2. Audit skill name.** Options: `claude-optimize-audit` (verb-noun, matches `claude-modify-skill`), `claude-optimize-report` (your suggestion: noun-noun), `claude-analyze-optimizer` (your suggestion). All fine; I have a mild preference for `claude-optimize-audit` because "audit" precisely captures what it does (look at history, judge effectiveness), whereas "report" or "analyze" are vague. Your call.

**N-D-3. Stage 1 vs. Stage 2 timing for skill-change-first-use detection.** Proposal in §1.4: ship Stage 1 immediately (false-positive-prone), queue the instrumentation task that enables Stage 2 as a follow-up. Alternative: block claude-optimize entirely until instrumentation lands. Trade-off: shipping Stage 1 starts producing value (and learning data) sooner but at the cost of some noisy no-op runs.

**N-D-4. Web research heuristics table (§2.3).** The 7-row table is a starting point. Your feedback noted that "you only know after the search whether it was worth it." If you want to be even more conservative (e.g., default web_research_recommended to false everywhere), that's a one-line change. Conversely, if you want it more liberal ("default true for any bugfix dimension"), also a one-line change.

**N-D-5. Auto-block awaiting tag.** Proposed: `awaiting: [user_unblock_optimize_proposal]`. Alternative: existing convention may have a tag like `user_review` or `user_approval`. I haven't audited the existing `awaiting:` vocabulary in this codebase. Pick the tag that fits your conventions.

**N-D-6. Whether the audit skill's report file should be committed.** Proposed: yes, committed under `automation/optimize/reports/<date>_audit.md`. This makes audit history part of the git record. Alternative: write to `/tmp/` and let the user save manually. Committing is probably right (mirrors `automation/reports/`).

---

## Part 6 — What remains uncertain and probably needs round 4

Honest list of things I am still unsure about:

**U-1. Will the high-confidence triggers actually fire often enough?** Repeated-question events have happened historically — but how often? If S9 fires twice a month, the optimizer mostly runs on the periodic trigger and produces mostly no-ops. The audit skill (§2.5) is the right tool to answer this empirically after a few weeks, but we can't know in advance. If the user has a sense of S9 frequency from the existing monitoring, that would update my estimates.

**U-2. The instrumentation chicken-and-egg.** Stage 1 vs. Stage 2 in §1.4 / N-D-3 is a real trade-off. I've leaned toward Stage 1 (ship now, instrument later) but the user may prefer the opposite.

**U-3. The web research heuristics in §2.3 may be wrong.** They are derived from intuition, not data. After 6 weeks of operation, if some "web_research_recommended: true" tasks produced low-value research and some "false" tasks would have benefited, the table needs revision.

**U-4. Whether the auto-block default eliminates the need for the deny-list.** Conceptually it should — the user is the final gate either way. But the deny-list is also a *correctness* signal (a proposal targeting `task-complete` is almost certainly wrong regardless of who reviews it). I've kept the deny-list as defense-in-depth; if the user prefers to drop it entirely once auto-block is in place, that's defensible.

**U-5. Whether the audit skill's "user-unblock rate" is the right north-star metric.** It conflates "the proposal was good" with "I had time to act on it" — a backlog of unblocked-but-not-acted tasks pollutes the metric. May need refinement (e.g., distinguish "deleted" from "kept blocked"). This is the kind of thing the audit skill itself can evolve once it has data.

**U-6. The exact shape of the `optimization_approach` block in produced tasks (§2.3).** I've sketched a YAML structure but haven't verified it composes cleanly with the existing `task-create` skill's frontmatter handling. An implementation pass will probably need to negotiate this.

**U-7. Whether monitors should be in `scripts/optimize/` or in `scripts/automation/`.** Both are defensible. `scripts/automation/` matches the existing `automation/` folder convention; `scripts/optimize/` keeps optimization-specific code together. Cosmetic but should be decided before scripts are scaffolded.

---

## Part 7 — Recommended path from here

If you accept this round:

1. **Confirm N-D-1 through N-D-6** in your next answer file. Each one is a small choice; the synthesis is unlikely to change based on them.
2. **Optionally request a round-4 synthesis on specific U-points** if any of them feel like real blockers (most are not — they can be resolved by the implementation tasks themselves).
3. **Then close this exploration task** with `task-complete` and proceed to the implementation phase, which now has these distinct work items:
   - **IMPL-A.** Rewrite REQ-PROC-006 per round-1 §16 + round-2 §E + round-3 §1.3, §2.1, §2.3 (auto-block, project-local state, web-research-per-task).
   - **IMPL-B.** Build `automation/optimize/` scaffolding (state.json schema, events/ folder, README.md, history/runs.tsv).
   - **IMPL-C.** Build the four monitor scripts (`scripts/optimize/monitor_*.py`) and the orchestrator `scripts/optimize/run_monitors.py`.
   - **IMPL-D.** Build the create-optimize-task script (`scripts/optimize/create_optimize_task.py`) with the auto-block default.
   - **IMPL-E.** Rewrite the `claude-optimize` skill body (event consumer + Tier 0/1 reads + task-create + commit).
   - **IMPL-F.** Wire `scripts/optimize/run_monitors.py` into `task-complete`'s tail end.
   - **IMPL-G.** Build the `claude-optimize-audit` skill (§2.5) — read runs.tsv + git, compute aggregates, write the report.
   - **IMPL-H.** Instrument protocol logging with `skills_used:` (enables Stage 2 of monitor_skill_change_first_use); add `after:` dependency from a follow-up monitor upgrade task.
   - **IMPL-I.** Create the blocked follow-up task `after: [TASK-PROC-044-NN]` for the observability Tier-0 source extension.

That is a clean impl backlog of 9 distinct tasks, each small enough to fit in one session.

---

## Part 8 — One-sentence summary of the design after round 3

**claude-optimize is a small skill driven by an event queue: cheap monitor scripts populate `automation/optimize/events/` after every task-complete; the skill consumes events, produces one auto-blocked improvement task (or a no-op note) per run, and commits its own runs.tsv so a separate audit skill can later judge whether the whole loop is paying for itself.**
