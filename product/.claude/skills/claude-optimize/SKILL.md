---
name: claude-optimize
description: Produce one improvement task per optimize event (auto-blocked)
tools: Read, Bash, Edit, Write
model: sonnet
---

You consume candidate events from `.factory/optimize/events/`, select **one**
highest-priority candidate, and produce **either** one auto-blocked improvement
task **or** a documented no-op. Every run commits `runs.tsv` and `state.json`.

Authority: REQ-PROC-006 (§Producer Paradigm, §Candidate Selection Priority,
§Commit Behavior, SEC-02, SEC-03, SEC-04). The producing chokepoint is
`scripts/optimize/create_optimize_task.py` (G-INV-1 auto-block lives there, not
here). You never call monitors or modify state outside `.factory/optimize/`.

## Steps

### 1. Setup

```bash
cd "$(git rev-parse --show-toplevel)"
NOW_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_ID="OPT-$(date -u +%Y%m%dT%H%M%SZ)"
EVENTS_DIR=.factory/optimize/events
STATE=.factory/optimize/state.json
RUNS=.factory/optimize/history/runs.tsv
```

Prune stale events (filename timestamp older than 30 days):
```bash
python3 - <<'PY'
import os, re
from datetime import datetime, timedelta, timezone
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
pat = re.compile(r"^(\d{8}T\d{6}Z)-")
for n in os.listdir(".factory/optimize/events"):
    m = pat.match(n)
    if not m: continue
    ts = datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    if ts < cutoff:
        os.remove(f".factory/optimize/events/{n}")
PY
```

List remaining events (sorted, oldest first within each type):
```bash
ls "$EVENTS_DIR"/*.json 2>/dev/null
```

### 2. Classify and select (AC-07)

Selection is deterministic and lives in a tested helper — do not re-implement
the rule in the LLM step:

```bash
SEL=$(python3 scripts/optimize/select_candidate.py --events-dir "$EVENTS_DIR")
echo "$SEL"   # JSON: selected, outcome, event_path, event_type, klass, dimension, payload, ...
```

The helper applies AC-07 (**bugfix candidates strictly first**; no fairness or
rotation) and the intra-class priority order, using this classification table
(mirrored in `scripts/optimize/select_candidate.py::classify` — the single
source of truth; keep both in sync if the rule changes):

| event_type | class | dimension if bugfix | dimension if optimization |
|---|---|---|---|
| `repeated_question` | bugfix | `bugfix` | — |
| `skill_change_reverted` | bugfix | `bugfix` | — |
| `skill_changed_and_used` | bugfix iff `payload.broken == true`, else optimization | `bugfix` | `clarity` (confidence=medium) / `trigger_accuracy` (confidence=low) |
| `periodic` | optimization | — | `alignment` |
| `high_read_file` | optimization | — | `token_cost` (payload `optimization_candidates` has `cache`) / `clarity` (otherwise) |

Priority order within each class: `repeated_question` > `skill_change_reverted`
> `skill_changed_and_used` > `periodic`.

If `outcome == "no-op"` (empty queue) → jump to Step 6 with reason
`empty_queue_after_prune`. Otherwise carry `event_path`, `event_type`,
`klass`, `dimension`, and `payload` forward.

### 3. Derive target / dimension / approach

`optimization_target` (SEC-02) is determined by the event's payload path:

| Payload signal | optimization_target |
|---|---|
| Path under `.claude/skills/*/skill.md` | `skill_body` |
| Path is a skill `description:` line | `skill_description` |
| Path under `doc/` | `doc_guideline` |
| Path = `.claude/task_ordering_rules.yaml` | `ordering_rule` |
| Path under `.claude/hooks/` | `hook` |
| Path under `scripts/` | `script` |

`optimization_dimension`: use the `dimension` field from the Step 2 helper output.

**Web-research approach (SEC-03, first match wins):**

| Match | recommended | reason |
|---|---|---|
| dimension=`bugfix` AND target ∈ {skill_body, script, doc_guideline, ordering_rule} | `false` | "Answer is in the repo" |
| dimension=`bugfix` AND payload references external CLI/library/API | `true` | "May be a known upstream issue" |
| target=`skill_description` AND dimension=`trigger_accuracy` | `true` | "Anthropic publishes guidance on skill descriptions" |
| target=`skill_body` AND dimension ∈ {alignment, clarity, layer_order} | `true` | "Rich prior art in agent orchestration" |
| target=`doc_guideline` | `false` | "Internal style, no external authority" |
| target=`ordering_rule` | `false` | "Project-specific" |
| otherwise | `false` | "default: internal change" |

If `recommended=true`, also write a focused `web_research_query` (one sentence,
quotes the friction from the event payload).

### 4. Compose objective and target_path

Pick the file the produced task proposes to modify (from event payload) as
`target_path`. Write a 1–2 sentence `objective` naming the friction and the
proposed direction. Keep it short — the developer reviews on unblock.

This is the only judgment step. Everything else is mechanical.

### 5. Produce the task (AC-01, AC-08)

Mint a task_id: `TASK-OPT-$(date -u +%Y%m%d)-<short>` where `<short>` is the
first 8 chars of the event fingerprint.

Compose `--scope` so the produced goal.md's body declares the verification
mode — one of these, never single-LLM judgment alone:

- "Verify: `<cmd>` exits 0" (script exit code)
- "Verify: `flutter analyze` reports zero new findings" (static analysis)
- "Verify: `flutter test test/<file>` passes" (test pass/fail)
- "Verify: structural rubric in `<file>` scores ≥ N/M"

Invoke the chokepoint:
```bash
TASK_DIR=requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/$(date -u +%Y-%m-%d)_impl_${SHORT_SLUG}
python3 scripts/optimize/create_optimize_task.py \
  --event "$EVENT_PATH" \
  --task-dir "$TASK_DIR" \
  --task-id "$TASK_ID" \
  --target-path "$TARGET_PATH" \
  --optimization-target "$OPT_TARGET" \
  --optimization-dimension "$OPT_DIM" \
  ${WEB:+--web-research --web-research-query "$WEB_QUERY"} \
  ${WEB:+--web-research-reason "$WEB_REASON"} \
  ${WEB:- --no-web-research --web-research-reason "$REASON_NO_WEB"} \
  --objective "$OBJECTIVE" \
  --scope "$SCOPE_WITH_VERIFICATION_MODE"
```

Exit codes:
- `0` → captured stdout = produced goal.md path. Continue.
- `2` → deny-list rejected. Treat as no-op with `notes=denylist:<pattern>`; skip
  to Step 6 but still commit.
- `3` → invalid input. Halt: emit a `pending_feedback` question (do not commit
  a half state — the run aborts and the developer fixes the trigger).

### 6. Consume events, update state, append runs.tsv (AC-09)

Delete the events selected in Step 2 (regardless of created vs deny-list no-op;
`empty_queue` no-op deletes nothing). For created runs, delete only the
selected event — other pending events survive for the next run.

Overwrite `state.json`:
```json
{
  "last_run_ts": "$NOW_UTC",
  "last_run_commit_sha": null,
  "total_runs": <prev + 1>,
  "no_op_streak": <0 if created else prev+1>,
  "completions_since_last_run": 0,
  "periodic_counter_threshold": <prev value, default 10>
}
```

Append one line to `runs.tsv` (tab-separated):
```
<NOW_UTC>	<RUN_ID>	<outcome>	<target_or_dash>	<dimension_or_dash>	<notes>
```
- `outcome` = `created` | `no-op`
- `target` / `dimension` = `-` for no-op
- `notes` = produced `task_id` (created) | reason (`empty_queue_after_prune` |
  `denylist:<pattern>`)

### 7. Commit (AC-09 — every run commits)

Stage exactly:
- `.factory/optimize/state.json`
- `.factory/optimize/history/runs.tsv`
- the deleted/created event files (`git add -A .factory/optimize/events/`)
- on `created`: the entire produced task folder

Invoke `claude-commit` with:
- type: `chore`
- scope: `optimize`
- subject: `run <RUN_ID> <outcome> <dimension_or_dash>`

Single commit per run, no chaining `add && commit`.

## Allowed verification modes (AC-08)

The produced task's body MUST cite at least one of these as its sole or primary
verification:
1. **Script exit code** — `<cmd>` exits 0.
2. **Static analysis clean** — `flutter analyze` / `dart analyze` reports no
   new finding.
3. **Test pass/fail** — a named test in `test/` or `integration_test/` passes.
4. **Structural scoring rubric** — a deterministic N-point rubric (criteria and
   pass threshold spelled out in the goal body).

Single-LLM "is this better?" is **never** the sole verification method. If you
cannot construct one of the four above for a candidate, no-op with
`notes=unverifiable:<event_fingerprint>` and skip task production.

## Guardrails (do not weaken)

- **G-INV-1** — auto-block lives in `create_optimize_task.py`. This skill never
  writes a goal.md directly.
- **G-INV-2** — you never invoke monitor scripts. Events are produced by the
  post-task-complete hook, outside this skill's tool surface.
- **G-INV-3** — you never compute the optimizer's health score. Scoring lives
  in `claude-optimize-audit`.
- **One task per run** (AC-01) — Step 5 runs at most once; Step 2 picks
  exactly one candidate.
- **Bugfix strictly first** (AC-07) — no fairness, no rotation, no quota.

## When to run

Triggered by the orchestrator when `events/` contains at least one event and no
prior `claude-optimize` task is pending. On manual invocation: same logic; an
empty queue produces a no-op with `notes=empty_queue_after_prune`.
