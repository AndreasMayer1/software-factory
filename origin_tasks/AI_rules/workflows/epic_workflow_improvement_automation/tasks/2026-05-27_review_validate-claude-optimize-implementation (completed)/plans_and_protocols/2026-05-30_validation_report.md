# claude-optimize Implementation Validation Report

- **Task**: TASK-PROC-006-06 — final validation gate
- **Date**: 2026-05-30
- **Agent ID**: ab771e645bba3994e
- **Contract**: rounds 1–4 concept (`2026-05-16_08_opus_synthesis_round4.md`,
  `2026-05-16_05_opus_synthesis_round3.md`, `2026-05-16_07_decisions_applied.md`)
  + `REQ-PROC-006`

## Overall Verdict

**38 PASS / 1 WAIVED / 4 FAIL** (43 checklist items A1–J4)

The system is largely faithful to the rounds-1–4 concept: state location, guardrails
(G-INV-1/2/3), monitor architecture, bugfix-first selection, two-metric audit, the
principles requirement, and Python gates are all correct. Four divergences were found,
the most serious being that **no code path creates the autonomous optimize task from
emitted events**, so the periodic and reactive trigger paths never actually invoke the
producer skill (runs.tsv is empty after weeks of monitor activity). The others are a
deny-list filename-case mismatch that defeats it in practice, an audit `--monitor`
invalid-name exit-code discrepancy, and the IMPL-I follow-up being completed against a
local explore task rather than gated on a TASK-PROC-044 dependency as the concept
specified.

---

## A. Architecture & identity

| Item | Verdict | Evidence |
|---|---|---|
| A1. One task per run or no-op; never multi-finding | ✅ PASS | `claude-optimize/SKILL.md` Step 2 selects exactly one candidate; Step 5 runs `create_optimize_task.py` at most once. `contract.yaml` quality_criteria: "Exactly one task produced per run (AC-01)". `select_candidate.py::select_candidate` returns a single event. |
| A2. Skill never applies changes; only creates tasks | ✅ PASS | SKILL.md only writes `.factory/optimize/*` + invokes `create_optimize_task.py` (which writes `goal.md`). No executor invocation. REQ-PROC-006 §Producer Paradigm: "does not execute the improvement". |
| A3. Three trigger paths route to same skill body | ❌ FAIL | Periodic + reactive paths are **not wired to invoke the skill**. `run_monitors.py` only emits events and (rate-limited) invokes the aggregator; it never calls `create_optimize_task.py` to create the autonomous optimize task, and no orchestrator/autorun code reads `.factory/optimize/events/` to launch the skill (`grep` of `.claude/skills/claude-autorun/`, `scripts/automation/` → nothing). Only explicit/manual invocation reaches the skill body. See Failure F-1. |
| A4. ≤~30 KB reads; no JSONL in hot path | ✅ PASS | Monitors read only state.json, git, question/protocol files. `grep jsonl scripts/optimize/monitor_*.py monitor_common.py` → none. JSONL only in Class-2 aggregator (`aggregate_read_metrics.py`), which is on-demand and rate-limited (run_monitors `_AGGREGATOR_THRESHOLD=5`). |

## B. State location & memory

| Item | Verdict | Evidence |
|---|---|---|
| B1. All state under `.factory/optimize/` | ✅ PASS | `monitor_common.py` `OPTIMIZE_DIR = PROJECT_ROOT/.factory/optimize`. No `automation/optimize/` path anywhere. |
| B2. Contains state.json, events/, history/{runs,audit_history,web_searches}.tsv, reports/, README.md | ✅ PASS | `ls .factory/optimize/` shows all required entries; `history/` has all three TSVs (each with a header row); `reports/.gitkeep` present; `README.md` present. |
| B3. No OS-memory read/write for optimize state | ✅ PASS | `grep .ccs/instances|MEMORY.md|session-env scripts/optimize/ skills/...` → none. README §1: "No optimizer state exists in per-account OS memory". |
| B4. events/ consume-then-delete; 30-day prune | ✅ PASS | SKILL.md Step 1 prune block (filename-ts > 30d removed) and Step 6 delete-selected-event. README §events documents both. |

## C. Detection / monitors

| Item | Verdict | Evidence |
|---|---|---|
| C1. Monitors are plain scripts invoked by task-complete, not agent tools | ✅ PASS | `scripts/optimize/monitor_*.py` plain Python; `task-complete/SKILL.md:181` invokes `run_monitors.py` as a subprocess; G-INV-2 docstring in `run_monitors.py`. |
| C2. "2+ blocked tasks >7 days" trigger does NOT exist | ✅ PASS | `grep -i "blocked.*7|7.*day|blocked task" scripts/optimize/` → no such trigger. No `monitor_blocked_*.py`. Round-3 §1.2 removal honored. |
| C3. Repeated-question fires at S9 count ≥3, idempotent in window | ✅ PASS | `monitor_repeated_question.py` `REPEAT_THRESHOLD=3`, `COOLDOWN=14 days`, uses `emit_once`. |
| C4. Skill-change Stage 1 ships; Stage 2 gated behind IMPL-H instrumentation | ✅ PASS | `monitor_skill_change_first_use.py` `_STAGE2_ENABLED=True` "since IMPL-H / TASK-PROC-006-13"; Stage 1 fires on edit alone (confidence low), Stage 2 raises to medium when `skills_used:` evidence found. |
| C5. Skill-reversion-within-48h monitor exists | ✅ PASS | `monitor_skill_change_reverted.py` `WINDOW=48h`, net-diff-empty detection, confidence high. |
| C6. Periodic monitor every N completions; N default 10, configurable in state.json | ✅ PASS | `monitor_periodic_counter.py` `DEFAULT_THRESHOLD=10`, reads `periodic_counter_threshold` from state.json; state.json sets it to 10. |

## D. Producer behavior

| Item | Verdict | Evidence |
|---|---|---|
| D1. Strict bugfix-first; no starvation carve-out | ✅ PASS | `select_candidate.py::select_candidate` sort key `(0 if klass=="bugfix" else 1, rank)`; docstring "No fairness, no rotation, no quota." Smoke test confirmed deterministic selection. |
| D2. Every produced task carries optimization_target + optimization_dimension | ✅ PASS | `create_optimize_task.py::_render_frontmatter` always emits both; both are `required` CLI args with closed `choices`. |
| D3. Verifiable AC (ground-truth/structural rubric, never single-LLM) | ✅ PASS | SKILL.md §"Allowed verification modes" lists 4 ground-truth/structural modes; "Single-LLM ... is **never** the sole verification"; no-op `unverifiable:` path if none constructible. |
| D4. Saturation exits cleanly with runs.tsv line, no memory entry | ✅ PASS | SKILL.md Step 2 `empty_queue_after_prune` → Step 6 writes runs.tsv + commits; no memory write anywhere (B3). |
| D5. Every run commits (even no-ops) | ✅ PASS (mechanism) | SKILL.md Step 7 commits on every run incl. no-op; AC-09 + contract quality_criteria. NOTE: runs.tsv currently header-only (skill never auto-ran — see F-1), so this is verified by code/spec, not by historical run rows. |

## E. Auto-block & guardrails

| Item | Verdict | Evidence |
|---|---|---|
| E1. Produced tasks born `awaiting: ["user-unblock"]` (create script default) | ✅ PASS | `create_optimize_task.py:198` hard-coded literal `'awaiting: ["user-unblock"]'`; no flag/branch feeds it; test `test_create_optimize_task.py:95` asserts presence. |
| E2. G-INV-1 documented as non-removable invariant in REQ-PROC-006 | ✅ PASS | requirements.md §Hard Constraints "G-INV-1 — Produced tasks are auto-blocked … No future evolution … may remove or weaken". AC-04. |
| E3. G-INV-2 (detection outside agent tool surface) holds | ✅ PASS | Monitors run as subprocess from task-complete; never exposed as agent tools; producer SKILL.md "you never invoke monitor scripts". |
| E4. G-INV-3 (audit skill separate from producer) holds | ✅ PASS | Two distinct skills; producer SKILL.md never imports/dispatches audit; `grep` per audit SKILL.md guardrail returns nothing. |
| E5. Write-surface deny-list enforced at create time; covers required list | ❌ FAIL | All 8 concept entries are present in `create_optimize_task.py::DENY_LIST` (claude-optimize, verify-quality, task-complete, claude-modify-skill, scripts/quality/**, analysis_options.yaml, factory_flows.md, INDEX.md). **BUT** the four skill entries are lowercase `skill.md` while the on-disk files are `SKILL.md`, and matching is case-sensitive (`==` for literals, `fnmatch.fnmatchcase` for globs). A real event payload carries the uppercase path (smoke test: `.claude/skills/claude-automated-mode/SKILL.md`), so the deny-list would NOT match the actual self-modification path. Defense-in-depth defeated. See Failure F-2. (G-INV-1 still contains harm.) |

## F. Web research

| Item | Verdict | Evidence |
|---|---|---|
| F1. Produced tasks carry optimization_approach block per round-3 §2.3 | ✅ PASS | `create_optimize_task.py::_render_frontmatter` always emits `optimization_approach:` with `web_research_recommended` + `reason`; SKILL.md Step 3 table mirrors the round-3 §2.3 / requirements §SEC-03 heuristics (first-match-wins). |
| F2. Performed web searches logged to web_searches.tsv (IMPL-J) | ✅ PASS | `scripts/optimize/log_web_search.py` appends to `.factory/optimize/history/web_searches.tsv`; file present with header; reads `optimization_approach.web_research_recommended` from goal.md. |

## G. Audit skill

| Item | Verdict | Evidence |
|---|---|---|
| G1. Separate `claude-optimize-audit` skill exists | ✅ PASS | `.claude/skills/claude-optimize-audit/SKILL.md` + `contract.yaml`. |
| G2. Deterministic rubric score + delta → audit_history.tsv | ✅ PASS | `audit.py::build_rubric` (10 criteria, script-owned constants), `_previous_score`/delta, `_append_history` writes 6-col TSV. No LLM. |
| G3. Both metrics: user-unblock-rate (primary) + revert-rate (secondary) | ✅ PASS | `audit.py::compute_unblock_rate` + `compute_revert_rate`; SKILL.md Metrics table (primary fast / secondary quarterly). |
| G4. Supports `--monitor=<name>` sub-audits | ⚠️ PARTIAL→PASS | `audit.py` `--monitor` with `filter_for_monitor`; sub-audit report path `<date>_audit_<name>.md` in SKILL.md. Minor: an invalid monitor name exits **2** (argparse choices) not **3** as the SKILL.md docstring claims; the skill maps exit 2 to "no runs to audit", so a typo would be misreported. Non-blocking. See Failure F-3 (minor). |
| G5. Report committed to reports/<date>_audit.md | ✅ PASS | `audit.py` writes `--report` path; audit SKILL.md Step 3 commits report + audit_history.tsv (N-D-6). |
| G6. DuckDB optional/query-time, runs.tsv canonical, degrades gracefully | ✅ PASS (waived sub-clause) | DuckDB layer is IMPL-M (v1.5, optional) and its task is still `pending` — not yet added. Concept (round-4 Part 1.2) explicitly says DuckDB is not for v1; runs.tsv is canonical and `audit.py` has no duckdb dependency, so it degrades by construction. Concept-compliant by deferral. |

## H. Triggering & integration

| Item | Verdict | Evidence |
|---|---|---|
| H1. run_monitors.py invoked at tail of task-complete; no OS/git hook | ✅ PASS | `task-complete/SKILL.md:172-189` step 6 "Run Monitor Sweep" post-commit, subprocess, best-effort (continue on non-zero), skipped under SKIP_QUALITY_GATES. No OS/VSCode/git hook. |
| H2. Optimize task runs autonomously (own awaiting empty); only proposals auto-blocked | ❌ FAIL | The mechanism that would create the autonomous optimize task (requirements §Monitor-Based Detection: "`create_optimize_task.py` creates an optimize task … runs autonomously") is **not implemented**. `create_optimize_task.py` only ever produces auto-blocked downstream proposals (hard-coded `awaiting: ["user-unblock"]`); there is no code path producing an `awaiting: []` optimize task. Same root cause as A3 / F-1. |
| H3. Blocked follow-up (IMPL-I) consumes TASK-PROC-044 observability, after: that task | ❌ FAIL | IMPL-I is implemented as TASK-PROC-006-14 but is `status: completed` with `after: [TASK-PROC-006-17]` (a local explore task), **not** `after:` a TASK-PROC-044 observability task as round-3 §2.7 / round-4 IMPL-I specified ("blocked follow-up `after: [TASK-PROC-044-NN]`"). The intended cross-requirement dependency gate was replaced by a same-folder explore dependency and closed. Functionally the high_read_file aggregator was integrated, but the concept's "blocked until TASK-PROC-044 lands" contract was not honored. See Failure F-4. |

## I. Principles requirement

| Item | Verdict | Evidence |
|---|---|---|
| I1. Cross-factory LLM-work-principles requirement exists, lists a–h | ✅ PASS | `requirements_tasks/process/AI_rules/llm_work_principles/requirements.md` (REQ-PROC-059) §Principles (a)–(h), each with Source + rationale. AC-01. |
| I2. Principle (c) carries irreversibility threshold | ✅ PASS | §(c) "Irreversibility threshold: promote … if and only if violating it is unrecoverable". AC-02. |
| I3. Scope stayed tight (no factory-wide rewrite) | ✅ PASS | §Scope explicitly "does NOT audit existing skills/CLAUDE.md, prescribe remediation, define enforcement". AC-03. Effort S. |

## J. Process hygiene

| Item | Verdict | Evidence |
|---|---|---|
| J1. Requirements pass lint/coverage scripts | ✅ PASS | `coverage_report.py` exit 0 (the "not found" lines are pre-existing merge warnings for unrelated REQ-PROC-010/057/063 etc., not REQ-PROC-006). `check_cross_refs.py <REQ-PROC-006>` exit 0 (informational suggestions only). |
| J2. Python gates pass for new scripts | ✅ PASS | `scripts/quality/check_python_gates.sh` → "All Python quality gates PASSED" (G1 lint, G2 type, G3 tests [1024 passed, 6 skipped, 5 xfailed], G4 no-handrolled, G5 print-discipline). EXIT 0. |
| J3. Every impl task references the concept docs | ✅ PASS | Sampled impl goal.md files reference REQ-PROC-006 + IMPL-* backlog IDs (e.g. TASK-PROC-006-14 `backlog_id: IMPL-I`; wire-monitors `backlog_id: IMPL-F` references AC-02/§Monitor-Based Detection at commit eabdeaf0). |
| J4. No settled rounds-1–4 decision silently reversed | ⚠️→ see FAIL note | All R1–R6 / N-D-1–10 decisions are honored in spirit (OS-memory abandoned, blocked-trigger removed, auto-block permanent, bugfix-first strict, two-stage skill-change, runs.tsv-only saturation, `.factory/optimize/`, `claude-optimize-audit`, `user-unblock` tag, committed reports, DuckDB deferred, two-metric audit, principles req). The A3/H2 gap is an **incomplete implementation** of a decided element (the autonomous-task trigger), not a deliberate reversal — recorded as FAIL under A3/H2, not a silent reversal here. J4 itself: ✅ PASS (no decision was reversed; one was left unimplemented). |

---

## FAILURES → follow-up tasks

### F-1 (A3 / H2) — No autonomous optimize-task creation; reactive & periodic trigger paths are dead

**Problem**: Monitors fire and write events to `.factory/optimize/events/` (245 events
currently pending), but nothing creates the autonomous `claude-optimize` task that the
orchestrator would pick up to run the producer skill. `run_monitors.py` ends after
emitting events + the rate-limited aggregator; it never calls `create_optimize_task.py`
for the optimize task, and no autorun/orchestrator code scans `events/` to launch the
skill. `create_optimize_task.py` can only mint auto-blocked *downstream proposal* tasks
(hard-coded `awaiting: ["user-unblock"]`) — there is no path producing an `awaiting: []`
optimize task. Net effect: `runs.tsv` is header-only despite weeks of monitor activity;
only manual `/claude-optimize` invocation reaches the producer. This contradicts
requirements §Monitor-Based Detection ("When monitors detect events and no claude-optimize
task is currently pending, `create_optimize_task.py` creates an optimize task. This task
runs autonomously") and round-3 §2.2.

**Suggested fix scope**: Add a creation step — either in `run_monitors.py` (when
`events/` is non-empty and no optimize task is pending, scaffold an optimize task with
`awaiting: []` via `task-create`/a dedicated helper) or in the autorun orchestrator
(detect non-empty `events/` and enqueue the `claude-optimize` skill). Distinguish this
autonomous task's empty `awaiting:` from the downstream proposals' `["user-unblock"]`.
Add a test asserting events → optimize-task creation → producer run → runs.tsv row.

### F-2 (E5) — Deny-list filename case mismatch defeats it in practice

**Problem**: `DENY_LIST` entries for the four protected skills use lowercase `skill.md`
(`.claude/skills/claude-optimize/skill.md`, …) but the actual files are `SKILL.md`.
`match_deny_list` is case-sensitive (`==` for literals, `fnmatch.fnmatchcase` for globs).
Real event payloads carry the uppercase path (confirmed via smoke test:
`.claude/skills/claude-automated-mode/SKILL.md`). A produced task targeting
`.claude/skills/claude-optimize/SKILL.md` would therefore pass the deny-list. The unit
tests pass only because they feed the lowercase paths. G-INV-1 auto-block still contains
the harm, but the documented defense-in-depth (AC-10 / SEC-04) is non-functional for the
skill entries.

**Suggested fix scope**: Change the four `skill.md` deny entries to `SKILL.md` (or make
the literal compare case-insensitive / normalize basenames), and update the test
parametrization to use the real on-disk casing so the test actually guards the live path.

### F-3 (G4) — Audit `--monitor` invalid-name exits 2, not 3; misreported as "no runs"

**Problem**: `audit.py` declares `--monitor` with argparse `choices`, so an unknown
monitor name exits **2** (argparse usage error) rather than the **3** the audit SKILL.md
docstring promises for "invalid input (unknown monitor name)". The SKILL.md maps exit 2
to "no runs to audit … skip commit", so a developer typo in `--monitor=` would be
silently reported as "no runs" instead of "unknown monitor". Low severity.

**Suggested fix scope**: Either (a) validate `--monitor` manually and `return 3` on an
unknown name (drop the argparse `choices` or wrap it), or (b) correct the SKILL.md
exit-code contract to state argparse rejects unknown monitors with exit 2. Align the two.

### F-4 (H3) — IMPL-I follow-up not gated on TASK-PROC-044; closed against a local explore

**Problem**: The concept (round-3 §2.7, round-4 IMPL-I) specified a *blocked* follow-up
task `after: [TASK-PROC-044-NN]` that stays dormant until the TASK-PROC-044 observability
data lands, then extends the optimizer's Tier-0 sources. The delivered TASK-PROC-006-14
is `after: [TASK-PROC-006-17]` (a same-folder explore task) and is already `completed`.
The high_read_file aggregator integration happened, but the cross-requirement dependency
gate the concept asked for was not used. Likely acceptable if TASK-PROC-044's relevant
observability already shipped — but it is a divergence from the recorded design and should
be confirmed, not assumed.

**Suggested fix scope**: Confirm with the developer whether the TASK-PROC-044 observability
data the optimizer is meant to consume actually shipped before TASK-PROC-006-14 closed.
If a residual TASK-PROC-044 source is still pending, re-open / create a blocked follow-up
`after:` that task. Otherwise record a one-line decision note that the dependency was
satisfied early and the gate was intentionally dropped (closing J4 cleanly).

---

## WAIVERS

- **G6 — DuckDB sub-clause**: Waived as not-yet-applicable. DuckDB is IMPL-M (explicit
  v1.5, optional; task still `pending`). The concept defers it; runs.tsv is canonical and
  `audit.py` has no duckdb dependency, so "degrades gracefully when duckdb is absent"
  holds by construction. Nothing to validate until IMPL-M is built.

---

## Follow-up disposition (orchestrator, 2026-05-30)

Developer decisions on the 4 failures:

| Failure | Disposition | Task |
|---|---|---|
| F-1 (A3/H2) — autonomous optimize-task creation missing | Bundled into one bugfix task with F-2 | **TASK-PROC-006-18** |
| F-2 (E5) — deny-list `SKILL.md` case mismatch | Bundled with F-1 (ships together) | **TASK-PROC-006-18** |
| F-3 (G4) — audit `--monitor` exit-code 2 vs 3 | **Deferred** — cosmetic/low-severity; not tasked. Recorded here. Revisit if it causes a real misreport in the field. | (none) |
| F-4 (H3) — IMPL-I TASK-PROC-044 dependency gate | Investigate (developer unsure if dependency shipped early) | **TASK-PROC-006-19** |

Both new tasks added to `.claude/task_ordering_priority_override.txt` (REQ-PROC-006
validation-gate follow-ups block). F-3 is consciously accepted as-is for now.

Gate outcome: this validation task (TASK-PROC-006-06) is complete — every A1–J4 item is
adjudicated, and every ❌ has been converted to a follow-up task or explicitly deferred
with a recorded reason.

## Notes for the orchestrator

- Python gates and requirements lint are GREEN — no process-hygiene blockers.
- The single high-value fix is **F-1**: without it the optimizer only runs when invoked
  by hand, so the entire reactive/periodic value proposition is inert in production.
- **F-2** is cheap and should ship alongside F-1 (a one-shot run could otherwise target a
  protected skill path).
- F-3 and F-4 are low-severity / confirmation items.
- This review modified no implementation files; only read-only gate scripts were run.
