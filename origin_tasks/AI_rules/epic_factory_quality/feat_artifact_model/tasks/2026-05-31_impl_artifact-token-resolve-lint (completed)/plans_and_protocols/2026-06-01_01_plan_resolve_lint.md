# Plan: Artifact-Token Resolve Lint

Date: 2026-06-01
Task: TASK-PROC-044-02-02
Session: 204d7317-a4e4-4c0d-9607-818acadda368

## Approach

Inline — all context gathered in the main session. No sub-agents.

## Investigation findings

**Registry:** `.factory/registry/artifacts.yaml` (created by TASK-PROC-044-02-01, status DRAFT
pending developer ratification). Has 46 tokens across 9 categories. YAML keys = token names.

**Contract formats:**
- Skill contracts (`.claude/skills/*/contract.yaml`): structured dict with `produces.{required|conditional}[]`
  and `derived_from.{required|optional}[]` — each item has a `path:` field (currently free-text file paths).
- Agent contracts (`.claude/agents/*.contract.yaml`): simple lists — `produces: [...]`, `derived_from: [...]`,
  `consumes: [...]` — list items are strings (file paths or globs).

**Target state (post-TASK-PROC-044-02-03):**
  Contract path/list values will be token names (e.g. `protocol`, `plan`, `goal`) instead of file paths.
  The resolve lint checks these values equal registry tokens.

**Current state:** Values are file paths → lint will flag all of them → baseline suppresses.

**Agent naming:** REQ-PROC-044-01 AC-01 defines `{expertise}-{role}` where role ∈
{writer, transformer, reviewer, classifier}. Expertise = registry token.
Currently most agents don't follow the scheme → lint surfaces them → baseline suppresses.

**Closed role set:** writer, transformer, reviewer, classifier

**Existing gate pattern:** `check_ac06_error_handling.py` uses `--baseline` arg to suppress known violations.
Identical pattern applied here.

## Deliverables

1. `scripts/quality/check_artifact_token_resolve.py` — the lint (tier: B)
2. `scripts/quality/artifact_token_baseline.txt` — initial baseline of all current violations
3. `check_quality_gates.sh` — new gate entry + GATE_EXTRA_ARGS entry

## Lint algorithm

### Check (c) — registry duplicates
  Load artifacts.yaml with a dup-detecting YAML loader.
  Any duplicate token key → violation, stop (duplicate detection first).

### Check (a) — contract token resolution
  For each skill contract:
    Extract path values from produces.{required,conditional}[*].path
    Extract path values from derived_from.{required,optional}[*].path
    Check each value against the token set.

  For each agent contract:
    Extract string items from produces (list or nested dict)
    Extract string items from derived_from (list or nested dict)
    Extract string items from consumes (list) — for completeness
    Check each value against the token set.

### Check (b) — agent name expertise segments
  For each .claude/agents/*.md (filename without .md = agent name):
    If name ends with -writer/-transformer/-reviewer/-classifier:
      Extract expertise = name stripped of last "-{role}" segment
      Check expertise against token set.
    Else:
      Report as non-conforming name (does not follow {expertise}-{role} scheme).

### Baseline suppression
  A violation string that exactly matches a baseline line is suppressed.
  `--baseline <file>` argument; missing file = no suppression (verbose mode).

### Output
  PASS — N contract(s), M agent(s) checked, 0 violations.
  FAIL — K violation(s) after baseline: <list>
  Exit 0 (PASS) or 1 (FAIL).

## Gate wiring

Add to GATES array in check_quality_gates.sh (boundary-contract-lint family, after arch-imports):
  "artifact-token-resolve | check_artifact_token_resolve.py"

Add to GATE_EXTRA_ARGS:
  GATE_EXTRA_ARGS["check_artifact_token_resolve.py"]="--baseline ${SCRIPT_DIR}/artifact_token_baseline.txt"
