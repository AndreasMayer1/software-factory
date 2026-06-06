# Synthesis — Task Sizing for the 200K-token Sonnet Budget

Date: 2026-05-19
Session: 14f805ee-3a21-4f6c-a86b-c7696850c2b7 (Opus)
Skill: requ-explore

## 0. The Question (restated)

What does it take for *every* task in this repo to be executable in a single
~200 K-token Claude Code session on Sonnet, without

- (a) blindly splitting tasks whose parts share an unwritten mental model
  that would be lost across folder boundaries, or
- (b) reflexively fanning out to subagents that re-read the same files and
  waste tokens?

## 1. Anatomy of the Two Failures (what the goal asked first)

| | TASK-PROC-049-08 | TASK-PROC-052-04 |
|---|---|---|
| Type | `impl` | `analyze` |
| Effort | S | S |
| `opus_recommended` | false | false |
| Failure wall-clock | ~7 min | ~4 min |
| JSONL size at failure | ~588 KB | ~287 KB |
| Scope shape | **Multi-deliverable** (README + CLAUDE.md edits + N×requ-explore) | **Open-ended breadth scan** (audit all `lib/` for key material) |

These are **two distinct size drivers**, not one:

1. **Compound-skill detonation** (049-08): the task drove a heavy skill
   (`requ-explore`) 4–5 times. Each `requ-explore` invocation is itself a
   multi-phase read pass: doc/, parent + sibling requirements, keyword-grep
   across `requirements_tasks/`, code search in `lib/`. The token cost
   scales with N × per-skill baseline. None of that is visible in the
   scope text as "files touched". It hides in the *skill chain*.

2. **Open-ended breadth scan** (052-04): the task did not name files. It
   named a *pattern* (`*Key`, `*KeyMaterial`, `*MasterKey`, …) and
   instructed "trace each lifecycle". The actual file set is whatever
   `lib/` happens to contain matching that pattern, plus their imports
   and call sites. Token cost scales with codebase breadth, not with
   anything written in the goal.

Crucially, **neither failure mode is captured by structural scope-text
metrics**:

- Deliverable-count heuristic ("N independent deliverables → split"):
  052-04 had ONE deliverable. Would not have triggered.
- Files-named-in-scope heuristic: 049-08 names ~3 requirement files; the
  *real* read set is far larger because each `requ-explore` recursively
  reads sibling + parent requirements. 052-04 names zero files.
- `should_use_agents.py` 30 KB / 5-files threshold: built for
  `release-begin-impl` which scans release-level requirement files. Its
  signature is `--release VERSION` or `--single-file FILE_PATH`. It
  cannot answer "is this *task* sized to fit?".

### What both failures share

- `effort: S` despite invisible-to-creator runtime depth.
- `opus_recommended: false` despite the scope shapes being the exact two
  patterns that benefit most from Opus's larger working memory.
- The signal that *would* have flagged them is not structural ("N files,
  K bytes") but **semantic-about-runtime-shape**:
  - "this scope invokes a heavy skill N times" → 049-08
  - "this scope is an open-ended breadth scan with no fixed file set" → 052-04

## 2. The Counterweights (what the goal asked second)

The user's nuance is decisive: not every task should be split, not every
task should fan out. Where do these counterweights bite?

### 2.1 Shared-mental-model tasks (splitting hurts)

A task benefits from monolithic execution when **the trade-offs across
its parts are themselves the deliverable**. Examples in this repo:

- This very task (`TASK-PROC-001-02`): the synthesis must hold the failure
  anatomies, the success contrasts, the counterweights, and the framework
  in one head simultaneously. Splitting it into "study failures",
  "study successes", "draft framework" produces three reports that each
  re-establish baseline context (re-read goal.md, re-read failing tasks,
  re-read CLAUDE.md §7) before they can think — a 3× baseline-cost
  multiplier on a problem whose true cost is the *thinking*, not the
  reading.

- Cross-cutting `explore` tasks under `process/AI_rules/`: the audit
  produces follow-up tasks for *several* skills; you need to see all of
  them at once to avoid contradicting yourself.

The signal here is **"the output is a synthesis whose claims reference
multiple input domains"** — not a structural metric.

### 2.2 Agent-rereads-everything tasks (fan-out wastes tokens)

A task wastes tokens on fan-out when **the main session must see the
material anyway** to produce the deliverable. Examples:

- `requ-explore` synthesising new acceptance criteria: the main session
  must see the failure shapes AND the existing ACs AND the proposed
  language. Delegating "read the failures" to an agent that returns a
  summary just adds an extra round-trip; the summary loses the texture
  the synthesis needs.

- `task-resolve` and `code-simple` working a single-file edit: there is
  no "breadth scan" component, so an agent would just re-read what the
  main session is about to edit.

The signal here is **"the deliverable's quality depends on direct,
unsummarised access to the input"** — also not a structural metric.

## 3. The Framework (signals, not just thresholds)

Three orthogonal signals decide sizing:

### S1 — Skill-chain depth (creation-time, predictable from scope text)

How many *invocations of heavy skills* will this task make at runtime?

A "heavy skill" is one whose own per-invocation token cost is
non-trivial — currently `requ-explore`, `task-create`,
`ux-create-flow`, `release-begin-impl`. (Empirical calibration target;
see §5.)

| Predicted invocations | Action |
|---|---|
| 0 or 1 | OK |
| 2–3 | Add explicit `opus_recommended: true` OR split |
| ≥ 4 | **MUST split** — one heavy invocation per child task |

049-08 had 4–5 `requ-explore` invocations and `opus_recommended: false`.
Either signal alone would have caught it.

### S2 — Scope openness (creation-time, predictable from scope text)

Is the file set the task will read *named* in scope, or is it
*pattern-defined* (open-ended)?

- **Closed scope**: named files / named requirements / a fixed
  test set. Cost is bounded by what's named.
- **Open scope**: glob/grep patterns ("all types named `*Key`", "every
  feature in `feat_*`"). Cost is bounded only by codebase breadth.

Open-scope tasks **MUST** specify an upfront agent-fan-out plan (which
agents are spawned, what they distill, what they return) — or be split
by code partition (e.g. one task per package) before they're scheduled.

052-04 was open-scope with no fan-out plan. The plan should have been:
spawn one general-purpose agent to inventory key-material candidates and
return a distilled list, then the main session reads only the candidates.

### S3 — Synthesis-dependency (creation-time, requires judgement)

Does the deliverable require the main session to hold all inputs at
once, or can parts be distilled and composed?

- **Synthesis-dependent**: trade-offs across pieces are the deliverable.
  → Keep monolithic. Use Opus. Agents only for breadth surveys that
  return distilled summaries; *not* for deliverable-shaped work.
- **Composable**: pieces don't inform each other.
  → Split freely, or fan out to agents that produce parts independently.

This is the signal that says "this task should ignore the defaults
because deep context produces better results" — it's the user's
explicit nuance, made into a checkable field.

### How the three signals compose

```
                     S2 closed scope        S2 open scope
S1 low + S3 composable   monolithic, Sonnet    split by code partition
S1 low + S3 synth-dep    monolithic, Sonnet    monolithic, Opus, plan agents
S1 high + S3 composable  split by deliverable  split by deliverable + plan
S1 high + S3 synth-dep   monolithic, Opus      monolithic, Opus, plan agents
```

S1 high + S3 composable is the 049-08 case → should have been split.
S1 low + S3 composable + S2 open is the 052-04 case → main session
should have spawned a survey agent; if that wasn't planned upfront, the
task should have been split by file-partition before scheduling.

## 4. Where Does the Rule Live?

Three placements, each with different failure modes:

### 4.1 Creation-time gate (in `task-create` / `task-create-code`)

S1 (skill-chain depth) and S2 (scope openness) are **detectable from
scope text** by a deterministic checker. They belong here.

- `task-create-code` already has Small/Medium/Large rules. Extend with
  S1 + S2 checks at the same stage.
- `task-create` (general) has no equivalent gate today. Add one.
- The gate must propose splits OR mark `opus_recommended: true` OR
  insist on an agent-fan-out plan being part of the goal.

S3 (synthesis-dependency) is **judgement** — the creator notes it
explicitly in goal.md frontmatter (`synthesis_dependent: true|false`).
Default false; require justification when true.

### 4.2 Runtime gate (in heavy skills + `claude-route`)

Even with a creation-time gate, the runtime can still surprise. A
runtime gate inside heavy skills (`requ-explore`, `task-resolve`,
`task-create`, `release-begin-impl`) measures actual read budget before
fanning out:

- If the skill is about to read > N requirement files OR > M KB, defer
  to agents for the read pass and synthesise the distilled summaries.
- The existing `should_use_agents.py` is a candidate but its signature
  is release-scoped. Either generalise it (add `--paths f1,f2,…` mode)
  or build a sibling helper.

CLAUDE.md §7 today *mandates* the runtime check across all skills
reading requirement files; in practice only `release-begin-impl` does it.
Either enforce the mandate (audit + fix every skill) or weaken the
mandate to match reality. The audit (§7 below) should decide which.

### 4.3 CLAUDE.md (the doctrine)

The framework itself — three signals, the composition table, the
"shared mental model is not free token waste" caveat — lives in
CLAUDE.md so every agent sees it. This becomes new content under §7
("Context-Window Rule").

## 5. What Remains Uncertain

(Honest about gaps.)

- **The "heavy skill" list is empirical.** I have not measured per-skill
  baseline token cost. Calibration target: median JSONL growth per
  invocation, sampled from the session-profile agent's output.

- **The 200 K ceiling is the model's, not the orchestrator's.** Sonnet's
  context window can change. The framework should be expressed in
  *relative* terms ("≥ 4 heavy invocations") not in absolute KB until
  we have real measurements.

- **Opus is not free.** Promoting to Opus is the orchestrator's safety
  net but the user wants Sonnet to handle the bulk. The framework
  should escalate to Opus only when S3 (synthesis-dependent) is true
  OR S1 ≥ 4 AND splitting would lose mental model. Otherwise split.

- **`should_use_agents.py`'s current threshold (30 KB / 5 files)**: the
  release-level use case may genuinely be the right boundary there. The
  *per-task* problem needs a different gate, not a reused threshold.

## 6. Concrete Output (what this task produces)

### 6.1 New acceptance criteria for REQ-PROC-001

End-state form (no "replace", no "migrate"):

- **AC-01**: Every new task's `goal.md` declares two creation-time
  signals: `skill_chain_depth` (count of heavy-skill invocations the
  task will make) and `scope_openness` ("closed" if all file/requirement
  reads are named in scope; "open" if reads are pattern-defined).
- **AC-02**: Every new task whose deliverable depends on the main
  session holding multiple input domains simultaneously declares
  `synthesis_dependent: true` in `goal.md`, with a one-line
  justification.
- **AC-03**: No task with `skill_chain_depth ≥ 4` has
  `opus_recommended: false` and no fan-out plan. (Either Opus, or split,
  or planned fan-out — at least one must be true.)
- **AC-04**: No task with `scope_openness: open` lacks a documented
  agent-fan-out plan in its goal.md (which agents, what they return).
- **AC-05**: Heavy skills that read requirement files defer to agents
  when read budget exceeds the per-task gate (separate from the
  release-level `should_use_agents.py` threshold).
- **AC-06**: CLAUDE.md §7 documents the three signals (S1, S2, S3) and
  the composition table, so every agent applies them consistently.

(REQ-PROC-001's existing User Story / Design Decision sections are
kept; the new ACs go into a new `## Acceptance Criteria` block.)

### 6.2 Follow-up tasks (one per skill needing changes)

Confirmed by the skill audit. Create via `task-create`, one task each:

- **`requ-explore`** — add a **re-entry guard** at Phase 1 entry: if the
  current session has already invoked `requ-explore` once, refuse and
  instruct the caller to spawn a fresh agent per invocation. Also add a
  Phase 1 read-budget gate (defer big read passes to an agent that
  returns a distilled summary).
- **`task-resolve`** — replace the LLM-driven ">4 source files" check
  in Step 2 with an automated structural check via the per-task gate
  helper (see below).
- **`task-create-code`** — replace the Quick-Explore-Agent estimate in
  Phase 2.3 with an automated structural check; add S1 (predicted
  heavy-skill invocations) as a co-equal signal alongside file count.
- **`task-create`** (general) — currently has no sizing gate. Add a
  creation-time check for S1 (skill-chain depth) and S2 (scope
  openness) that runs against the goal.md text before the task is
  finalised.
- **`code-bugfix`** — at resume time, if `plans_and_protocols/`
  contains more than N protocol files or > M KB, spawn a
  summarisation agent rather than reading each file inline.
- **CLAUDE.md §7** — replace the current Context-Window Rule (30 KB /
  5 files, only enforced in one skill) with the three-signal framework
  + composition table from §3, so every skill applies it consistently.
- **`scripts/util/should_use_agents.py`** — extend with a per-task
  mode (`--paths f1,f2,…` or `--task-goal PATH`) so the skills above
  can call it without reframing their input as a release scan.

Each follow-up task should have `parent_requirement: REQ-PROC-001`
and `after: [TASK-PROC-001-02]` so they chain off this exploration.

## 7. Skill-Audit Results (folded in)

Per the `skill-audit` agent's findings (2026-05-19):

### 7.1 Who calls `should_use_agents.py` today
- **Only `release-begin-impl/skill.md`** (Phase 1 and Phase 2c).
- It is the reference template — strictest budgets in the system
  (Phase 0 max 3 files; Phase 1 ≤30 KB / 5 files inline; Phase 2 epic
  agents max 5 files; Phase 2c splits at >100 KB).

### 7.2 Who has their own size heuristics today

| Skill | Existing gate | Weakness |
|---|---|---|
| `task-create-code` | Phase 2.3: Small ≤3 / Medium 4–8 / **Large 8+ → Split NOW** | Relies on a "Quick Explore Agent" estimate; no automated structural check. Misses tasks whose goal enumerates *N requirements* not *N files*. |
| `task-resolve` | Step 2: >4 source files → agent-assisted | LLM-driven, not script-driven. Inline mode invites unbounded Read/Grep/Glob. |
| `code-simple` | 1–3 files, single layer, clear pattern, low risk → simple | Qualitative; mis-classification at step 2 invisible. |
| `code-complex` | Step 3: >10 files / all 3 layers / >1 session → split. **Step 5b implementation batches max 3 source files per agent.** | Indicator table is qualitative. |
| `requ-explore` | **Epic Size Gate** (90-line body limit, auto-splits oversized epic into features) | Only structural gate is for *output* size, not *input* read budget. Phase 1 has ~10 read categories. **No re-entry guard.** |
| `task-create` (general) | None (only effort tiers XS–XL) | The gap. |
| `code-test` | None | TDD naturally bounded by test files. |
| `code-bugfix` | Mode-detection split (slim vs worktree) | Resume reads ALL protocol files chronologically — balloons on multi-session bugs. |

### 7.3 What the audit confirms (and adds)

**Primary culprits for compound blowup** (in order):

1. **`requ-explore`** — confirmed primary cause of TASK-PROC-049-08.
   Phase 1 does ~10 categories of reads (doc/, parent + sibling
   requirements, market research, user-needs READMEs, persona/scenario/
   flow files, codegraph, `lib/` greps). Designed to run *once per
   session*. **No re-entry guard.** Called 4–5× in one session = the
   detonation pattern. Each call also re-reads guidelines (no
   "already loaded this session" cache).

2. **`task-resolve` (inline mode)** — fallback skill; inline mode has no
   automated file-count check, so an LLM under-estimate evaporates the
   budget. Chains into `claude-log` + `doc-update-guidelines` +
   `task-complete` at the end.

3. **`code-bugfix` resume** — full chronological protocol-file replay
   scales with session count; potential blowup on long-running bugs.

**New insight from audit (added to §3 framework)**: The S1 signal needs
a sub-signal — **chain-accumulation cost vs single-call cost**. Each
`requ-explore` invocation adds ~20–30 KB on its own; four invocations
in one session add ~100 KB *plus* the orchestrator overhead and the
deliverable work. The right per-task signal is closer to
`expected_skill_invocations × per_invocation_footprint`, not just
"≥ 4 invocations". The "≥ 4" threshold is a practical proxy; the real
budget is cumulative bytes.

## 8. Session-Profile Results (and an important correction)

The `session-profile` agent's findings (2026-05-19) revise the picture:

### 8.1 The two named failures completed

The JSONLs at `c3480d6b…` (TASK-PROC-049-08) and `60f63438…`
(TASK-PROC-052-04) **completed successfully**. They are the
**second-attempt Opus runs** after the orchestrator's auto-promotion
path triggered on the first attempt's "Extra usage required for 1M
context" error. The first-attempt JSONLs were not inspected (likely
overwritten or stored elsewhere).

This does **not invalidate** the user's diagnosis — the first attempts
did fail on context, otherwise auto-promotion would not have fired —
but it means the byte sizes the user cited (~588 KB and ~287 KB) are
the *second-run* sizes on Opus, not the first-run failure sizes.

### 8.2 Real context-window overflows on 2026-05-16

The agent identified **6 sessions** that day with genuine
`CTX_OVERFLOW`:

| JSONL size | Task / skill chain | Tool-call signature |
|---|---|---|
| 1.21 MB | TASK-PROC-046-03 (code-complex) | 56 Bash, 9 TaskCreate, 10 Agent, 9 WebFetch, 522 entries, 181 KB tool-result |
| 1.20 MB | TASK-PROC-049-07 (task-create + commit) | 81 Bash, 22 Read, 13 Edit, 514 entries, 164 KB tool-result |
| 995 KB | TASK-PROC-006-02 (claude-modify-skill) | 78 Bash, 21 Read, 19 Edit, 187 KB tool-result, **single biggest result = 37.6 KB** |
| 856 KB | TASK-PROC-035-08 (requ-explore + opus-switch) | 60 Bash, 251 entries, 170 KB tool-result |
| 554 KB | claude-commit only | 25 KB single tool-result |
| 546 KB | task-resolve | 36 Bash, 16 Read, 269 entries, 100 KB tool-result |

The smallest overflow (546 KB JSONL, 36 Bash, 100 KB tool-result) and
the largest successful run (`d21d0913`, 800 KB JSONL, 8 distinct
skills, no overflow) **overlap in size**. The cliff is **not** a
clean byte threshold.

### 8.3 What actually predicts overflow

The dominant pattern is **cumulative tool-result volume from iterative
Bash + Read loops** — not one giant Read. The 6 overflow cases all
share: 36–81 Bash calls, 100–187 KB of tool-result content, 250–520+
JSONL entries. The single largest one-shot tool result observed across
ALL sessions was 37.6 KB — so "one massive file read" is not the
detonator.

The agent's empirical proposal: split tasks whose expected
**Bash + Read count exceeds ~60** OR whose **doc-update / verify-
quality loop is likely to iterate**, regardless of an `effort: S`
label.

### 8.4 Framework adjustment

S1 (skill-chain depth) was incomplete on its own. The corrected signal
is **tool-call volume × iteration depth**:

- **S1′ (revised)** — Expected tool-call volume:
  count of Bash + Read + Edit calls the task is likely to make at
  runtime. Calibrated bands:

  | Expected tool calls | Action |
  |---|---|
  | < 30 | OK |
  | 30–60 | Add `opus_recommended: true` if also has iteration loops |
  | > 60 | **MUST split** OR plan agent fan-out OR Opus |

  Heavy skill invocations are a proxy for this volume:
  one `requ-explore` ≈ ~20 Bash + Read calls; one `task-resolve`
  iteration ≈ ~15; one verify-quality cycle ≈ ~10. So "≥ 4 heavy-skill
  invocations" maps to "≥ 60 tool calls" — the two formulations agree.

- **S2** (scope openness) — unchanged.

- **S3** (synthesis-dependency) — unchanged.

- **S4 (new)** — Iterative-fix loop: tasks that hand off to
  `verify-quality` and then iterate on RED → fix → re-verify drive
  much higher tool-call volume than their goal.md suggests.
  `code-bugfix`, `code-complex`, and any `impl` that touches `lib/`
  with quality gates on are high-iteration. Tasks with S4 = true
  should default to Opus unless the change is genuinely 1-file
  scope.

### 8.5 Updated ACs (overriding §6.1)

ACs in §6.1 stand with these adjustments:

- AC-01: declare `skill_chain_depth` **OR** `expected_tool_calls`
  (whichever the creator can estimate). Either ≥ 4 invocations or
  ≥ 60 tool calls trips the gate.
- AC-03: trigger is "S1 high OR S4 true" → must have Opus, split, or
  fan-out plan.
- New AC-07: Tasks driving a `verify-quality` loop on `lib/` changes
  default to `opus_recommended: true` unless the change is named and
  ≤ 3 files.

### 8.6 Open uncertainty

- The first-attempt JSONLs for the two user-named failures were not
  inspected. The framework should still catch them by S1 (049-08:
  4–5 `requ-explore` invocations) and S2 (052-04: open scope) without
  needing the empirical byte data.
- The 546 KB overflow at task-resolve with only 36 Bash calls is a
  data point that 60-tool-call threshold may still be too generous.
  Calibration should be revisited after the follow-up tasks land and
  produce more measurement data.
- One overflow case (`0749460a`, 554 KB) is just `claude-commit`. That
  suggests the commit step itself, when running on an already-large
  session, can be the straw that breaks the budget. **The commit step
  must always run on a fresh agent budget**, not the same session
  that did the implementation. CLAUDE.md §4 step 5 wording supports
  this (task-complete OWNS the commit and is invoked at end of task)
  — but in practice the same session may execute task-complete + the
  commit. Worth checking in the follow-up.
