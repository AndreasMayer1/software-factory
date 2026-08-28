---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - claude-commit
  - task-complete
---

# Protocol — Walking Skeleton Implementation
Task: TASK-PROC-068-04
Agent: a4e3cfd1333c6e617
Started: 2026-06-27

## Environment Analysis

### Containment environment findings (SG-04)
- `unshare` is blocked by Docker seccomp profile (even with sudo NOPASSWD: ALL)
- `bwrap` blocked (same reason — needs user namespaces)
- `chroot` blocked (effective CAP_SYS_CHROOT not granted)
- Workspace is mounted world-writable (drwxrwxrwx) — OS-user isolation ineffective
- `AppArmor` kernel present but no `aa-exec` user-space tool
- **Decision**: Implement fail-safe containment:
  1. `containment.py` wraps child cmd in `unshare --user --mount` 
  2. Probes at import time whether unshare is available; if not → raises `ContainmentUnavailable`
  3. Default mode: refuse to launch uncontained (fail-safe = CON-04 is closed by refusing)
  4. `PLAYGROUND_ALLOW_UNCONTAINED=1` env-var bypass for dev/test mode
  5. AC-09 test verifies the fail-safe raises when containment unavailable
  6. Secondary defense: environment scrubbing (HOME, XDG_* → harness dir) limits data-write scope

### SG-02 (cost capture) — reuse path
`claude -p --output-format json` → parse `.total_cost_usd` + `.duration_ms` from JSON envelope.
Verified PASS in TASK-PROC-073-01-01; not re-verified here.

### Test harness location
`test_harness_app/` at repo root is the harness. deploy.py snapshots `.claude/skills/` into it.

## Module layout (finalized)

```
scripts/playground/
  __init__.py          — package marker (empty)
  containment.py       — OS-level containment: unshare-wrap + fail-safe probe (tier: B)
  deploy.py            — snapshot .claude/skills/ → harness .claude/skills/ (tier: B)
  reset.py             — git-reset harness to HEAD; verify clean state (tier: B)
  cost_ledger.py       — parse JSON envelope, accumulate cost+duration, max_budget_usd cap (tier: B)
  launch_adapter.py    — child-session launcher: Popen + hung-detection (JSONL path parameterized) (tier: B)
  run_skeleton.py      — orchestrates deploy→run→reset→cost for single fixture (tier: C CLI)
scripts/tests/
  test_playground_containment.py   — AC-09 test
  test_playground_deploy.py        — deploy/reset tests (AC-07)
  test_playground_cost_ledger.py   — cost ledger + cap test (AC-08)
  test_playground_launch_adapter.py — launch adapter unit tests
  test_playground_run_skeleton.py  — integration test (mocked subprocess)
```

## Progress

### Phase 1: containment.py — [ ] TODO
### Phase 2: deploy.py + reset.py — [ ] TODO
### Phase 3: cost_ledger.py — [ ] TODO
### Phase 4: launch_adapter.py — [ ] TODO
### Phase 5: run_skeleton.py — [ ] TODO
### Phase 6: tests — [ ] TODO
### Phase 7: Python gates — [ ] TODO

## AC Coverage Plan
- **AC-07** (F/MEDIUM clean-state-after-reset): `test_playground_deploy.py` — deploy writes marker file → reset → verify marker gone
- **AC-08** (C/MEDIUM cost+duration ledger): `test_playground_cost_ledger.py` — parse JSON envelope → ledger entry → cap enforcement
- **AC-09** (S/HIGH OS-level containment): `test_playground_containment.py` — without PLAYGROUND_ALLOW_UNCONTAINED, ContainmentUnavailable raised when unshare blocked; with mock unshare, child cmd prefix verified

---

## Phase 8: Python Gates → ALL GREEN (2026-06-27)
Agent: claude-sonnet-4-6 (spawned by orchestrator for gate-fix pass)

### Fixes per gate

**G1 (ruff lint) — 17 errors → 0**
- `containment.py:120,147` — removed dead `# noqa: S603` (S603 not enabled in ruff config; RUF100)
- `reset.py:104` — removed dead `# noqa: S603` (same reason; RUF100)
- `run_skeleton.py` — removed unused `SessionConfig` import (F401); fixed import block sort (I001 × 2 after adding `LaunchRequest` + `Any`); removed dead `# noqa: PGH003` and `# noqa: T201` (RUF100 × 2)
- `test_playground_containment.py` — removed unused `tempfile` import + `_TEMPFILE_USED` hack (F401 + dead RUF100); removed 3 dead `# noqa: S603`; fixed import sort (I001)
- `test_playground_run_skeleton.py` — fixed import sort (I001); merged 3-level nested `with` into single `with (...)` (SIM117)
- `test_playground_cost_ledger.py` — fixed import sort (I001)
- `test_playground_deploy.py` — fixed import sort (I001); merged nested `with patch / pytest.raises` into single `with (...)` (SIM117)

**G2 (mypy) — 1 error → 0**
- `run_skeleton.py:run_single_fixture` return type changed from `dict[str, object]` to `dict[str, Any]`; added `from typing import Any`. This makes `"advisory" in result` and `result["run_count"]` type-check in `test_playground_run_skeleton.py:171`.

**G3 (pytest) — already PASS; confirmed still PASS after all changes**
- 2609 passed, 17 skipped, 6 xfailed

**G6 (complexity PLR0913) — 1 violation → 0**
- `launch_adapter.py:run_with_hung_detection` had 6 params (`cmd, env, session_uuid, jsonl_dir, *, config, deps`).
- Added `LaunchRequest` dataclass bundling the 4 positional identity params (`cmd, env, session_uuid, jsonl_dir`).
- Signature reduced to 3 params: `(request: LaunchRequest, *, config, deps)` — within PLR0913 ≤ 5.
- Updated call sites: `run_skeleton.py` (1 site), `test_playground_launch_adapter.py` (4 sites).
- WHY comment in `LaunchRequest` docstring explains the PLR0913 motivation.

**G4, G5, G7 — already PASS; confirmed still PASS**

### Final gate SUMMARY
```
  PASS   G1 lint
  PASS   G2 type
  PASS   G3 tests
  PASS   G4 no-handrolled
  PASS   G5 print-discip.
  PASS   G6 complexity
  PASS   G7 canonical-lib
All Python quality gates PASSED.
```

### AC evidencing tests (post-gate-fix)
- **AC-07** (clean-state-after-reset): `scripts/tests/test_playground_run_skeleton.py::test_run_single_fixture_resets_harness_after_run` — asserts `git reset` is called in the skeleton loop after every child session.
- **AC-08** (cost ledger): `scripts/tests/test_playground_run_skeleton.py::test_run_single_fixture_returns_ledger_with_advisory` — asserts ledger dict carries `advisory`, `run_count`, `total_cost_usd`, `total_duration_ms`.
- **AC-09** (OS-level containment — real jail): `scripts/tests/test_playground_containment.py::test_real_jail_host_tree_unreachable` (skipped when userns unavailable; runs and must pass when userns is available per TASK-PROC-054-12). Structural evidence (always runs): `test_wrap_raises_when_no_containment_available` — asserts `ContainmentUnavailable` raised when neither bwrap nor unshare is available and bypass env var is unset.
