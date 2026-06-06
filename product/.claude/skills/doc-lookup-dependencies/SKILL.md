---
name: doc-lookup-dependencies
description: Look up API docs before emitting a dependency call (REQ-PROC-053)
tools: [Bash, Read, WebFetch, WebSearch]
model: inherit
---

You look up official API documentation for a dependency before the caller emits a call into it, implementing REQ-PROC-053 AC-02 with dedup, evidence skips, and budget enforcement.

## Arguments (passed via args string)

`--technology <tech>  --api-surface <surface>  --pinned-version <ver>  [--trigger <reason>]`

- `technology`: canonical id — `package:<name>`, `dart:<lib>`, `python:<module>`, `flutter`, etc.
- `api-surface`: dotted-path identifier (e.g. `ListView.builder.itemBuilder`)
- `pinned-version`: version string from `pubspec.lock` / `pyproject.toml` / equivalent
- `trigger`: `default` (omit = default) | `deprecation` | `unknown_symbol` | `gate_failure_api_mismatch` | `version_bump` | `test_framework_subtle`

## Steps

### 1 — Find the task log

```bash
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ --include="goal.md" | head -1)
TASK_DIR=$(dirname "$GOAL")
LOG="$TASK_DIR/plans_and_protocols/lookup_log.jsonl"
touch "$LOG"
```

### 2 — Compute dedup key and check cache

```bash
python3 -c "
import hashlib, sys
k = hashlib.sha256(f'{sys.argv[1]}@{sys.argv[2]}::{sys.argv[3]}'.encode()).hexdigest()
print(k)
" "<technology>" "<pinned_version>" "<api_surface>"
```

Scan `$LOG` for a line where `dedup_key` matches AND `decision` is `looked_up`, `skipped_evidence_a`, or `skipped_evidence_c`.

**Cache hit** → append a `skipped_evidence_b` record (fields: ts, agent, agent_id, chain, step, technology, pinned_version, api_surface, dedup_key, decision=`skipped_evidence_b`, channel=`prior_in_task_lookup`, source_ref=`lookup_log.jsonl:<line-N>`, result_summary=<cached>, trigger, cycle) → **return cached result_summary. Done.**

### 3 — Check AC-02 (a) evidence (skip if trigger is `deprecation`, `unknown_symbol`, or `gate_failure_api_mismatch`)

Fast path: `cat .git/quality_green_hash 2>/dev/null` — non-empty → grant evidence (a).

Slow path: run toolchain probe (5s cap):
- Dart: `timeout 5 dart analyze --no-fatal-warnings --no-fatal-infos <evidence-file>`
- Python: `timeout 3 ruff check <file> && timeout 3 mypy <file> --no-error-summary`
- YAML / native: deny by default.

Exit 0 → append `skipped_evidence_a` record (channel=`in_repo_call_site`) → **return null. Done.**
Exit ≠ 0 / timeout → deny; continue.

### 4 — Check budget

```bash
LOOKED_UP=$(grep -c '"decision": "looked_up"' "$LOG" 2>/dev/null || echo 0)
EFFORT=$(grep -m1 "^effort:" "$GOAL" | awk '{print $2}')
```

Budget: `XS`/`S` → 5; `M` → 10; `L`/`XL` → 25.
At or over budget → append `budget_capped` record → **return sentinel `BUDGET_CAPPED`. Done.**

### 5 — Sanitize query

```bash
QUERY=$(python3 scripts/util/validate_doc_lookup_query.py "<api_surface> API usage <technology>")
```

### 6 — Channel chain: ctx7 → official → WebSearch

**ctx7 (preferred):**
```bash
SLUG=$(ctx7 library --json "<technology-name>" "$QUERY" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" 2>/dev/null)
RESULT=$(ctx7 docs "$SLUG" "$QUERY" 2>/dev/null)
```
Non-empty result → channel=`context7`, source_ref=`context7:<slug>@<pinned_version>`.

**Official docs** (ctx7 empty/error): use WebFetch or `curl -L -s --max-time 15` against official URL (flutter.dev, dart.dev, pub.dev, docs.python.org, etc.).
- channel=`official`, source_ref=`<url>`

**WebSearch** (official unavailable): use WebSearch tool; record `note` explaining why fallback was needed.
- decision=`fallback_websearch`, channel=`websearch`
- If WebSearch tool not available in this context: decision=`fallback_websearch`, note=`WebSearch unavailable in sub-agent context; used training knowledge`, channel=`training_data`

### 7 — Append record and return

Append a single JSON line to `$LOG` (all required fields from `doc/cross_cutting_standards/documentation_lookup.md §3`). Include `dedup_key` field.

Return `result_summary` (1–3 lines) to the caller.

## Schema reference

See `doc/cross_cutting_standards/documentation_lookup.md` for the full record schema, field semantics, budget bands, and per-technology lookup tables.
