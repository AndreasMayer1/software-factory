# Plan: Rewrite `claude-optimize` skill body as thin event consumer

Date: 2026-05-28
Author: claude-modify-skill (session c09e24d5)
Source task: TASK-PROC-006-10 (IMPL-E)

## Scope

Replace the existing `.claude/skills/claude-optimize/SKILL.md` body (currently a
generic "analyse history" prompt, ~30 LOC) with a deterministic event-consumer
that uses the IMPL-C monitors (events at `.factory/optimize/events/`) and the
IMPL-D writing chokepoint (`scripts/optimize/create_optimize_task.py`).

## Algorithm encoded in the skill body

1. **Setup** — list events, drop any whose filename timestamp is older than 30
   days (`rm` consumed-stale files), load `state.json`.
2. **Selection** —
   - Group events into `bugfix` vs `optimization` based on payload semantics
     (see "Classification" below).
   - Within each group, order: `repeated_question` > `skill_change_reverted` >
     `skill_change_first_use` > `periodic`.
   - **AC-07**: pick the first bugfix candidate; only fall back to optimization
     when no bugfix candidate exists.
   - If both groups empty after pruning → no-op.
3. **Derive two-field taxonomy** (SEC-02) — target ∈ {skill_body,
   skill_description, doc_guideline, ordering_rule, hook, script};
   dimension ∈ {bugfix, alignment, latency, …}. Derivation is deterministic
   per event type (table in skill body).
4. **Derive web-research recommendation** (SEC-03 heuristic table, first match
   wins) — produce `web_research_recommended`, `web_research_query`, `reason`.
5. **Compose objective** — short LLM step: write a 1–2 sentence objective and
   pick a `target_path` from the event payload. This is the only judgment call;
   everything else is mechanical.
6. **Compose verification AC** — the produced task body MUST list at least one
   verification mode from the allowed set (test pass/fail, static analysis
   clean, script exit code, structural rubric). Single-LLM judgment is
   forbidden as the sole verification method (AC-08).
7. **Mint a task_id** — `TASK-OPT-<YYYYMMDD>-<short>` (deny-list-safe; no
   collision with TASK-PROC-006-*).
8. **Invoke `scripts/optimize/create_optimize_task.py`** with all flags.
   Exit code 2 → deny-list rejection → treat as no-op with note
   `denylist:<pattern>`. Exit code 3 → invalid input → halt and surface error.
9. **Consume events** — delete the events selected in step 2 (whether or not
   produced; periodic event reset is the responsibility of the periodic
   monitor's counter reset, which happens when we set
   `completions_since_last_run=0` in state.json).
10. **Update `state.json`** — overwrite with: `last_run_ts` = now (UTC ISO),
    `total_runs += 1`, `no_op_streak` = 0 on `created` / `+1` on `no-op`,
    `completions_since_last_run = 0`, preserve `periodic_counter_threshold`.
11. **Append `runs.tsv`** — single line:
    `<ts>\t<run_id>\t<outcome>\t<target>\t<dimension>\t<notes>`.
    `run_id` = `OPT-<YYYYMMDDTHHMMSSZ>`; `outcome` ∈ {`created`, `no-op`};
    `notes` = produced task_id (for `created`) or reason (for `no-op`).
12. **Commit** via `claude-commit` skill — message
    `chore(optimize): run <id> [created|no-op] [<dimension>]`. The commit
    includes the new goal.md (when created), the updated `runs.tsv`,
    `state.json`, and deleted events. **AC-09** — no-op runs commit too.

## Classification (bugfix vs optimization)

A single deterministic table in the skill body keyed on event_type + payload
signal. Examples:

| event_type | bugfix iff | optimization otherwise |
|---|---|---|
| `repeated_question` | always (same friction recurring) | — |
| `skill_change_reverted` | always (revert ⇒ broken edit) | — |
| `skill_change_first_use` | `payload.broken=true` if monitor sets it | `clarity` / `trigger_accuracy` |
| `periodic` | never | dimension = `alignment` |

The classification rule is owned by the skill body so future evolution lives in
one place (heuristics table principle, requirements §"Developer Guidelines").

## Constraint preservation map

| Invariant | Where enforced |
|---|---|
| G-INV-1 (auto-block) | `create_optimize_task.py` (literal in `_render_frontmatter`) |
| G-INV-2 (detection out of agent tool surface) | monitors run from hook; skill never invokes monitors |
| G-INV-3 (scoring separated) | scoring belongs to `claude-optimize-audit`; this skill never scores itself |
| AC-01 (≤1 task/run) | step 8 invoked at most once; step 5 picks exactly one |
| AC-07 (bugfix strictly first) | step 2 selection order |
| AC-08 (verification mode) | step 6 mandatory clause in produced body |
| AC-09 (every run commits) | step 12; no-op branch commits state.json + runs.tsv |
| AC-10 (deny-list) | `create_optimize_task.py` (deny-list rejection → no-op note) |

## Out of scope (explicit, per goal.md)

- Monitor implementation — done in TASK-PROC-006-08.
- `create_optimize_task.py` and the deny-list enforcement — done in TASK-PROC-006-09.
- Hooking `run_monitors.py` into `task-complete` — TASK-PROC-006-11 (IMPL-F).
- Audit skill (`claude-optimize-audit`) — TASK-PROC-006-12 (IMPL-G).

## Token-efficiency target

Soft cap: under ~300 LOC including the heuristics tables and an inline example.
No `///` WHY comments (skills rule). Tables compressed; no preamble.
