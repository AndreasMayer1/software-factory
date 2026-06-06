---
name: verify-quality
description: Run the project quality gates (REQ-PROC-046 / REQ-PROC-002 / REQ-PROC-052) as blocking checks. Refuses completion on RED, enforces the five-cycle back-pressure bound, escalates to the developer via pending_feedback at cycle 5. THIS SKILL MUST BE USED BEFORE COMMITTING OR COMPLETING ANY TASK THAT TOUCHED `lib/`, `test/`, OR `integration_test/`.
tools: ["Bash", "Read", "Edit", "Write", "Skill", "Agent"]
---

You run the project's quality gates as **blocking** checks. The protocol is
defined by REQ-PROC-046 AC-10 (inherited by REQ-PROC-002 AC-07 and
REQ-PROC-052 AC-09): code that fails any active gate is never declared
complete; failures trigger revision; five cycles cap escalation.

## Modes

| Mode | Flag | Gates run |
|------|------|-----------|
| Per-change (default) | none | analyzer, tests, aggregate gate runner, critical-path coverage |
| Release-cadence | `--release` | per-change + bundle size + test determinism |
| Audit-only | `--audit` | spawn quality-checker agent only (no script runs); used by hooks when full runs would be too slow |

## Bypass

Two distinct mechanisms exist.

**Auto-bypass (no authorization required).** The pre-commit hook auto-skips
the gate run when zero files in the staged set live under `lib/`, `test/`,
or `integration_test/`. The gates are Dart-code-only by REQ-PROC-046 scope —
docs-only / scripts-only / requirements-only commits have nothing the gates
can measure, so the hook prints `[verify-quality] SKIPPED for git commit (no
staged files under lib/, test/, or integration_test/ — auto-bypass per
REQ-PROC-046 scope)` to stderr and exits 0. No commit-message annotation
required.

**Cache fast-skip (no authorization required).** After a GREEN gate run,
this skill writes the current tree's `git stash create -u` hash to
`.git/quality_green_hash`. On the next pre-commit-hook invocation, if the
current tree hash matches the stored hash, the hook skips the gate run with
`[verify-quality] SKIPPED for git commit (tree hash <SHA> already GREEN —
fast-skip per .git/quality_green_hash)`. The cache is identity-based
(content, not time) — any edit invalidates it. A PRE/POST atomicity check
inside this skill ensures the cache is only written when the tree state was
stable across the gate run (no concurrent-session edit raced into the
verified window). The cache covers the `task-complete` → commit flow
(`verify-quality` runs in step 2a, the pre-commit hook fires in step 5's
commit) so the gates are not re-run twice on the same state.

**Manual bypass (explicit user authorization required).**
`SKIP_QUALITY_GATES=1` in the environment short-circuits the skill with a
**warning written to stderr**. Use only with explicit user authorization; the
commit author is responsible for noting the bypass in the commit message.
This is the override for cases where code files *are* in scope but the
developer has accepted a known gate failure.

## Pre-flight: working-tree state

Before running gates, verify the working tree is in an expected state:

```bash
git status --porcelain
```

Treat as **clean enough** if every change either:
- is part of the active task's expected file set (read goal.md to know which
  files), or
- lives under `plans_and_protocols/` of the active task, or
- is a regenerated artifact listed in `CLAUDE.md` §11.

If the tree contains unrelated dirty files: print the offending paths and
**refuse to run** unless `--allow-dirty` is supplied. (Closes the
"stale-artifact false-green" pitfall in REQ-PROC-046 §Common Pitfalls.)

## Step 1 — Locate the active task

```bash
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ --include="goal.md" | head -1)
TASK_ID=$(grep -m1 "^task_id:" "$GOAL" | awk '{print $2}')
TASK_DIR=$(dirname "$GOAL")
CYCLE_FILE="$TASK_DIR/plans_and_protocols/cycle_state.json"
```

If `GOAL` is empty: there is no active task. Run gates anyway in
**stateless mode** (no cycle counter is maintained; RED still blocks).

## Step 2 — Read or initialize the cycle counter

```bash
if [ -f "$CYCLE_FILE" ]; then
  COUNT=$(jq -r '.cycle_count' "$CYCLE_FILE")
else
  COUNT=0
fi
```

If `COUNT >= 5`: **STOP** without running gates. Go directly to Step 6
(escalation). The fifth failure already triggered escalation; further
invocations would loop.

## Step 3 — Run gates

### 3.1 — Determine which gate set applies

```bash
CHANGED=$(git diff --name-only HEAD)
DART_CHANGED=$(echo "$CHANGED" | grep -E '^(lib|test|integration_test)/' || true)
SCRIPTS_CHANGED=$(echo "$CHANGED" | grep -E '^scripts/.*\.(py|ps1|sh)$' || true)
CONTRACTS_CHANGED=$(echo "$CHANGED" | grep -E '^\.claude/(skills/[^/]+/contract\.yaml|schemas/.*\.yaml|contracts/external/.*\.yaml)$' || true)
```

### 3.1b — Capture PRE-run tree hash (for cache fast-skip)

```bash
PRE_HASH=$(git stash create -u 2>/dev/null)
[ -z "$PRE_HASH" ] && PRE_HASH=$(git rev-parse HEAD 2>/dev/null)
```

This hash identifies the exact tree state about to be verified. If the
gate run produces GREEN AND the tree did not change during the run, Step 4
will persist this hash so the next pre-commit-hook invocation can fast-skip
the gate re-run for the same state.

### 3.2 — Dart per-change gates (when `DART_CHANGED` non-empty)

Run the analyzer and gate scripts directly in the container (no host bridge — see REQ-PROC-054):
```bash
flutter analyze
bash scripts/quality/check_quality_gates.sh
python3 scripts/quality/check_critical_path_coverage.py 2>/dev/null || true
```

### 3.3 — Python per-change gates (when `SCRIPTS_CHANGED` non-empty)

```bash
bash scripts/quality/check_python_gates.sh
```

### 3.3b — Skill-contract gate (when `CONTRACTS_CHANGED` non-empty)

Fires on any `.claude/skills/*/contract.yaml` or `.claude/schemas/*.yaml` change
(REQ-PROC-044). Verifies derived_from/produces cross-references, named-producer
resolution, may_invoke existence, and schema references:
```bash
python3 scripts/quality/check_skill_contracts.py
```
Non-zero exit = gate failure (RED). WARNINGs (unmanaged skills) do not fail the gate.

### 3.3c — Boundary-contract gate (when `CONTRACTS_CHANGED` non-empty)

Fires on any `.claude/contracts/external/*.yaml` change (REQ-PROC-044 AC-08).
Validates check→script resolution, schema references, kind/interface fields,
and `input_modality:` enum compliance:
```bash
python3 scripts/quality/check_boundary_contracts.py
```
Non-zero exit = gate failure (RED). `input_modality:` absent defaults to `file` — not a violation.

### 3.4 — Release-cadence add-ons (when `--release` was passed)

```bash
python3 scripts/release/check_bundle_size.py
bash scripts/quality/check_test_determinism.sh
```

### 3.5 — Aggregate exit status

Capture every gate's exit code. RED if any gate returned non-zero. Cache the
full output of failing gates for the developer.

### 3.6 — Spawn quality-checker agent for the deeper review

Use the **Agent** tool with `subagent_type: quality-checker`. Pass the changed
file list and the cycle count. The agent's job is structural review
(architecture, WHY comments, persona alignment) — orthogonal to the scripted
gates. Treat the agent's RED as a gate failure.

## Step 4 — On GREEN

```bash
rm -f "$CYCLE_FILE"
```

Capture the POST-run tree hash and write the cache **only if no edit raced
in during the gate run** (PRE_HASH from Step 3.1b must equal POST_HASH):

```bash
POST_HASH=$(git stash create -u 2>/dev/null)
[ -z "$POST_HASH" ] && POST_HASH=$(git rev-parse HEAD 2>/dev/null)
if [ -n "$POST_HASH" ] && [ "$PRE_HASH" = "$POST_HASH" ]; then
  echo "$POST_HASH" > .git/quality_green_hash
else
  echo "[verify-quality] tree changed during gate run — not caching" >&2
fi
```

The pre-commit hook in `.claude/settings.json` reads `.git/quality_green_hash`,
recomputes `git stash create -u` for its current view, and fast-skips the
gate run on match. Concurrent sessions on the shared worktree degrade
safely: a race during the gate run results in `PRE_HASH != POST_HASH` and
the cache write is skipped; the next stable run writes a fresh hash.

Print `verify-quality: GREEN — all gates passed.` and exit 0.

## Step 5 — On RED (cycles 1–4)

Increment the counter and persist:
```bash
NEW_COUNT=$((COUNT + 1))
jq -n --arg id "$TASK_ID" --argjson c "$NEW_COUNT" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{task_id: $id, cycle_count: $c, last_result: "RED", last_red_at: $ts}' \
  > "$CYCLE_FILE"
```

Write a structured failure summary to the caller (LLM or hook):

```
verify-quality: RED — cycle $NEW_COUNT of 5.
Failing gates:
  - <gate name>: <one-line summary>
  - ...
Next step: fix the issues and re-invoke verify-quality. Do not declare
the task complete while RED.
```

Exit code: **1** (so commit hooks and task-complete halt).

## Step 6 — On RED at cycle 5 (escalation)

This branch fires either when Step 3 just produced the fifth RED, or when
Step 2 detected `COUNT >= 5`.

### 6.1 — Pre-condition checks

The task MUST have `status: in_progress` and a `session_id`. If not: this
session was not routed through `task-start`. Print the precondition
warning and exit 2 — do **not** create a pending_feedback entry, because the
orchestrator can't resume a session it doesn't know about.

### 6.2 — Write `question.md`

```bash
FEEDBACK_DIR="automation/pending_feedback/$TASK_ID"
mkdir -p "$FEEDBACK_DIR"
SESSION_ID=$(grep -m1 "^session_id:" "$GOAL" | awk '{print $2}')
ASKED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ACCOUNT="${CLAUDE_SESSION_ACCOUNT:-unknown}"
```

Write `$FEEDBACK_DIR/question.md` using `automation/pending_feedback/TEMPLATE_question.md`
as the frontmatter source of truth. Fill:
- `task_id: $TASK_ID`
- `session_id: $SESSION_ID`
- `account: $ACCOUNT`
- `status: awaiting_answer`
- `asked_at: $ASKED_AT`
- `skill: verify-quality`

In the body include:
- the cycle count (always 5)
- the list of failing gates with their last summary
- the proposed next steps (e.g. "revisit the design", "widen the gate",
  "split the task")

### 6.3 — Copy the answer template

```bash
cp automation/pending_feedback/TEMPLATE_answer.md "$FEEDBACK_DIR/answer.md"
```

**DO NOT** write anything into `answer.md`. The template keeps the
`<!-- AWAITING_HUMAN_ANSWER -->` sentinel; the orchestrator uses that sentinel
to detect "not yet answered".

### 6.4 — Terminate

```bash
bash scripts/automation/terminate_session.sh
```

The active task stays `in_progress`, its `session_id` is preserved, and the
orchestrator's pending-feedback machinery (`scripts/automation/orchestrate.py:find_answered_feedback`
and `scripts/tasks/next_tasks.py:load_pending_feedback_ids`) keeps the task off
the queue until the developer fills `answer.md`. On resume, the new session's
first verify-quality invocation will see no `cycle_state.json` (the file was
left intact but the developer's answer is expected to either fix the violation
or delete the file) and start fresh from cycle 1 if RED recurs.

## Step 7 — Smoke test (self-check)

To verify the chain end-to-end:

1. Introduce a deliberate violation under `lib/` (e.g. a forbidden direct
   `import 'package:flutter/material.dart'` in a feature file).
2. Run `verify-quality`. Expect: exit 1, cycle_state.json with
   `cycle_count: 1`.
3. Attempt `git commit`. Expect: PreToolUse hook blocks the commit and prints
   the gate summary.
4. Invoke `task-complete`. Expect: refusal with the same gate summary.
5. Revert the violation; run `verify-quality` again. Expect: exit 0,
   cycle_state.json removed.

## Counter-reset rules (mandatory)

- **Task transition**: the counter file lives in the active task's
  `plans_and_protocols/`. A new task has its own folder ⇒ fresh counter.
- **Explicit user clear**: `rm <task-folder>/plans_and_protocols/cycle_state.json`.
- **GREEN result**: Step 4 deletes the file automatically.

## Notes on hook integration

The `PreToolUse(Bash:"git commit*")` hook invokes the gate runner
(`scripts/quality/check_quality_gates.sh`) directly when a commit is
attempted. It runs the **per-change** gate set. Hook behaviour is documented
in `.claude/settings.json`. Two scope-derived auto-bypasses (zero
Dart-files staged; cache-hash fast-skip after a recent GREEN) short-circuit
the hook before the gate runner; an explicit `SKIP_QUALITY_GATES=1` overrides
all of them (with explicit user authorization).

The `task-complete` skill invokes this `verify-quality` skill from step 2a
(see `.claude/skills/task-complete/skill.md`); that path runs the full
per-change gates **plus** the `quality-checker` agent for structural review
(architecture, WHY comments, persona alignment). The pre-commit hook does
not spawn the agent — its job is to block the commit on scripted-gate
failure only.

There is no `Stop` hook. The previous end-of-turn hook was removed by
TASK-PROC-046-17 because it could not distinguish session-modified files
from pre-existing dirty working-tree files, and re-triggered every turn
including one-word LLM acknowledgments — entering an infinite oscillation
on any session that opened against an already-dirty tree. The two remaining
trigger points (`task-complete` step 2a + the pre-commit hook) preserve
REQ-PROC-046 AC-10's "never declared complete while RED" invariant.
