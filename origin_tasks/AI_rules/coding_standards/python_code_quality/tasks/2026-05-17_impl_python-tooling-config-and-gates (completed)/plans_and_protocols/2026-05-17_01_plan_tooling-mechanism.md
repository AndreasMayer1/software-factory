---
type: plan
task_id: TASK-PROC-051-02
created: 2026-05-17
agent_id: architecture-advisor-2026-05-17-unknown
---

# TASK-PROC-051-02 — Python Tooling Mechanism Plan

## Context

TASK-PROC-051-02 lands the *capability* to enforce REQ-PROC-051 (Python code quality):
configuration, custom G4/G5 gate scripts, central YAML helper, tier-annotation
convention, and a single gate-runner. It does NOT clean up existing `scripts/`
code — that is TASK-PROC-051-04. The gates may (and will, by design) fail on
`develop` after this task lands.

Cross-cutting constraints from CLAUDE.md / REQ-PROC-043:
- `scripts/util/` is capped at 5 files. Current count: 2
  (`find_devcontainer.py`, `should_use_agents.py`). Headroom: 3.
- Domain folders are mandatory; nothing new at `scripts/` top level except the
  existing `validate_scripts_org.py`.
- Dart-side quality gates live under `scripts/quality/` with the runner
  `scripts/quality/check_quality_gates.sh` plus `_lib.sh`. The Python side must
  be *structurally consistent* with that pattern, not parallel.
- `claude-install-os-tool` skill exists for adding OS-level tooling; new
  package-manager / linter installs go through it (devcontainer-aware).
- `analysis_options.yaml` is the Dart authority; the Python authority should
  be the equivalent single file (`pyproject.toml`).
- `PyYAML` is already a transitive dev dep (used by
  `scripts/quality/check_critical_path_coverage.py`).

Hand-rolled YAML parser sites confirmed for G4 — at least:
- `scripts/automation/orchestrate.py` (≥4 distinct `--- ... ---` state machines
  around lines 336–353, 685–710, 1131–1140, 1223–1235)
- `scripts/artifacts/generate_status_overview.py` (lines 226–290, custom
  `parse_frontmatter` with hand-split keys)
- `scripts/artifacts/generate_id_registry.py` (lines 37–60, `parse_yaml_frontmatter`)
- `scripts/requirements/reconcile_dependencies.py` (lines 37–55 + 121–197;
  uses both raw line walking *and* PyYAML, the mixed pattern G4 must still
  catch the raw half of)

All share the same signature: `in_frontmatter`/`in_fm` boolean flag, `---`
delimiter sentinel string, line-by-line iteration, key parsing by
`split(":", 1)`. G4's pattern set targets that signature precisely.

---

## A. Python tooling configuration

**Tool choices**

| Role | Tool | Justification |
|---|---|---|
| Linter | **`ruff`** | Fastest currently available (Rust-backed). Single binary, replaces flake8 + isort + pyupgrade + pep8-naming + bugbear + comprehensions in one run. AC-02 minimum coverage (pyflakes + bug patterns + import order + modernization) is achievable through a single `[tool.ruff.lint]` selection. |
| Formatter | **`ruff format`** | Ships in the same binary; behaviorally compatible with Black. One install, one config block. |
| Type checker | **`mypy`** | Most mature, best stdlib support, well-understood strict mode. Pyright is faster but its config story is split between `pyrightconfig.json` and `pyproject.toml`; mypy fits cleanly in `pyproject.toml`. |
| Test runner | **`pytest`** | Already the standing tool — `scripts/automation/tests/test_orchestrate.py` is invoked as `python3 -m pytest …`. No migration. |
| YAML lib | **`ruamel.yaml`** | The helper's comment-preserving / atomic-update API mandates round-trip mode; PyYAML cannot do that. PyYAML stays usable for read-only call sites that do not need round-trip; the helper itself uses ruamel. See section D for the trade-off. |

**Config file shape**

Single `pyproject.toml` at repo root:
```
[tool.ruff]
[tool.ruff.lint]
[tool.ruff.lint.per-file-ignores]
[tool.ruff.format]
[tool.mypy]
[[tool.mypy.overrides]]   # TIER A: strict
[[tool.mypy.overrides]]   # tests: relaxed
[tool.pytest.ini_options]
```

No `setup.py` / `setup.cfg` / `mypy.ini` proliferation — `pyproject.toml` is
PEP-518 standard and matches the "single authoritative file" property of
`analysis_options.yaml`.

**Linter rule selection — AC-02 minimum**

```toml
[tool.ruff.lint]
select = [
    "E", "W",   # pycodestyle (style)
    "F",        # pyflakes (correctness: undefined names, unused imports)
    "B",        # flake8-bugbear (common bug patterns)
    "I",        # isort (import ordering)
    "UP",       # pyupgrade (modernization)
    "SIM",      # flake8-simplify
    "C4",       # flake8-comprehensions
    "RET",      # flake8-return
    "RUF",      # ruff-native rules
]
ignore = [
    "E501",     # line length — defer to formatter
]
```

Comparison-to-singleton (`E711`/`E712`) is in `E`; mutable-default-args
(`B006`) and broad-except (`B902`/`BLE`) come from `B`. AC-13 suppressions
are visible in plain text (`# noqa: <code> — reason`) — no extra config.

**Type-checker per-tier strictness**

```toml
[tool.mypy]
python_version = "3.9"
# default = TIER B / TIER C baseline (lenient: not strict, but real)
warn_unused_ignores = true
warn_redundant_casts = true
warn_unreachable = true
no_implicit_optional = true
check_untyped_defs = false
disallow_untyped_defs = false

[[tool.mypy.overrides]]
# TIER A — full strict
module = [
    "scripts.automation.orchestrate",
    # extended in TASK-PROC-051-04
]
strict = true
disallow_untyped_defs = true
disallow_any_generics = true
warn_return_any = true

[[tool.mypy.overrides]]
# Tests: skip return-type checks
module = ["scripts.*.tests.*", "scripts.tests.*"]
disallow_untyped_defs = false
check_untyped_defs = false
```

Tier-to-module mapping is enumerated explicitly per module (header convention,
see C). Glob-by-folder is not used because tiers are descriptive, not
folder-derived.

**Test collection roots**

```toml
[tool.pytest.ini_options]
testpaths = [
    "scripts/automation/tests",
    "scripts/tests",
]
python_files = ["test_*.py"]
addopts = "-ra --strict-markers"
```

**Decision:** `pyproject.toml` at repo root; ruff + mypy + pytest configured
in single-source-of-truth blocks; rule set as enumerated above; TIER A modules
listed explicitly in a `[[tool.mypy.overrides]]` stanza.

**Why:** One file, one authority, mirrors `analysis_options.yaml`. Explicit
tier enumeration in config matches AC-03's "determinable without ambiguity"
property and avoids implicit folder-rule drift.

---

## B. Dependency pinning / reproducibility (AC-02)

**Strategy choice: `uv` + `uv.lock` + `requirements-dev.txt` (compiled, hashed)**

| Option | Verdict | Why |
|---|---|---|
| `pip` + `requirements-dev.txt` (hand-edited) | Reject | Hand-pinning transitive deps is error-prone; AC-02 reproducibility is structural. |
| `pip-tools` (`pip-compile`) | Acceptable fallback | Mature, hash-locking works. Slower than uv; same UX. |
| `uv` + `uv.lock` | **Recommended** | Fastest install, native cross-platform lockfile with content hashes, no Python bootstrap dance, growing standard. Single binary; the orchestrator's CI minutes matter. |
| `poetry` | Reject | Heavier, opinionated about project layout; this repo is not a Python package and never will be — `pyproject.toml` here is config-only. |

**Lockfile layout**
- `pyproject.toml` declares dev dependencies under `[dependency-groups]` (PEP 735)
  or `[tool.uv]` group.
- `uv.lock` committed at repo root — cross-platform manifest.
- `requirements-dev.txt` exported from `uv export --format requirements-txt
  --no-hashes=false` — committed as the human-readable / `pip install -r`
  fallback for any environment without uv installed.

**Reproducibility property (AC-02)**
- Fresh checkout → `uv sync` (or `pip install -r requirements-dev.txt --require-hashes`)
  → `scripts/quality/check_python_gates.sh` produces identical gate behavior
  as CI.
- Hashes pin the exact wheel; rebuilding cannot drift.

**Install workflow for new contributors / dev environments**
- Invoke `claude-install-os-tool` skill once to install `uv`
  (`curl -LsSf https://astral.sh/uv/install.sh | sh` — also adds to
  devcontainer.json `postCreateCommand`).
- Then `uv sync` (no further user-level prompts).
- The `pip`-fallback path needs no extra OS tool.

**Decision:** `uv` is the chosen package manager; `uv.lock` committed;
`requirements-dev.txt` exported (with hashes) as the no-uv fallback;
`claude-install-os-tool` adds `uv` install line to `devcontainer.json`
`postCreateCommand`.

**Why:** `uv` collapses install + lock + run into one fast tool, matches CI
minutes-budget property, and lock+hash gives AC-02's reproducibility
structurally. `requirements-dev.txt` keeps the door open for environments
where uv is unwanted. **Flagged for user confirmation** (Open question 1)
because package-manager choice has long tail; `pip-tools` is acceptable
fallback.

---

## C. Tier annotation system (AC-03)

**Options**

| Option | Pro | Con |
|---|---|---|
| Header comment `# tier: A` | Self-documenting, greppable, file-local, survives moves | Requires touching every file (POC ≤3 here, full pass in -04) |
| Folder-level rule documented in `doc/python/` | One config | `doc/python/` doesn't exist yet (TASK-PROC-051-03); fragile — moving a file silently changes its tier; doesn't help an LLM reading the file alone |
| `pyproject.toml` enumeration | Single config | Splits "what is this module" from the module itself; encourages forgetting |

**Decision:** **Header comment** `# tier: A | B | C` placed on the line
immediately after the module docstring (or first line if no docstring), with
optional trailing rationale.

```python
"""scripts/automation/orchestrate.py — session orchestrator..."""

# tier: A  # long-lived stateful, owns invariants across try/except
```

The convention is documented in this task's plan and in the helper module's
docstring; TASK-PROC-051-03 will lift it into `doc/python/` verbatim.

**POC scope — 3 modules tagged in this task**

| Tier | Module | Why this module |
|---|---|---|
| A | `scripts/automation/orchestrate.py` | Canonical TIER A reference; named in REQ-PROC-051 §References |
| B | `scripts/util/yaml_frontmatter.py` (new helper, see D) | Library imported by ≥10 future call sites; AC-08's hub |
| C | `scripts/tasks/goal_preview.py` | ≤100 SLOC, no imported callers, one-shot CLI |

**Discovery of tier from file**: a tiny helper inside the gate-runner
parses the first 20 lines of each `scripts/**/*.py` looking for `# tier: <X>`.
Files without the annotation default to TIER B + emit a WARNING (not
FAIL — TASK-PROC-051-04 owns the full-pass annotation).

**Decision:** Header comment immediately after the module docstring; three
POC modules tagged; mypy `[[overrides]]` stanza for TIER A lists modules by
fully-qualified path.

**Why:** Header comment survives file moves; greppable for the gate-runner;
LLM reading a single file in isolation sees the tier without needing to
cross-reference `doc/python/`. Folder-rule was rejected because the same
folder mixes tiers (e.g. `scripts/automation/` has TIER A `orchestrate.py`
and a TIER B test helper).

---

## D. Central YAML helper module

**Path:** `scripts/util/yaml_frontmatter.py`

This brings `scripts/util/` to 3 of 5 files — within budget.

**Public API**

```python
# scripts/util/yaml_frontmatter.py
"""
Central YAML-frontmatter helper (REQ-PROC-051 AC-08).

THIS MODULE IS ALLOW-LISTED FOR G4 — it is the *only* place hand-rolled
boundary handling is permitted; every other call site must import from here.

Three use cases, three entry points:

1. read_frontmatter(text_or_path) -> FrontmatterDoc
   Read-only parsing. Returns FrontmatterDoc(metadata: dict, body: str,
   raw_yaml: str). Uses ruamel round-trip loader so subsequent updates
   preserve comments and key order.

2. update_frontmatter(path, updates: dict, *, remove_keys: list[str] = ())
   One-shot read-modify-write. Atomic (write to .tmp, fsync, rename).
   Comment-preserving. Existing key order preserved; new keys appended.

3. with frontmatter_session(path) as doc:
       doc.metadata['status'] = 'done'
       doc.metadata.setdefault('audit', []).append('2026-05-17')
   Context manager for non-trivial read-modify-write. On __exit__ (no
   exception): atomic write. On exception: nothing written. Acquires an
   advisory fcntl lock on the file for the duration of the block.

Tier: B
"""

from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from ruamel.yaml import YAML, CommentedMap

@dataclass
class FrontmatterDoc:
    metadata: CommentedMap      # mutable, comment-preserving
    body: str                   # the markdown body after the closing ---
    raw_yaml: str               # original YAML text, for diagnostics

    @property
    def has_frontmatter(self) -> bool: ...

def read_frontmatter(source: str | Path) -> FrontmatterDoc: ...
def update_frontmatter(
    path: Path, updates: dict, *, remove_keys: list[str] = (),
) -> None: ...

@contextmanager
def frontmatter_session(path: Path) -> Iterator[FrontmatterDoc]: ...
```

**Why ruamel.yaml**
- `CommentedMap` is the only mainstream Python data structure that preserves
  comments + key order through round-trip.
- Goal note line 106 explicitly requires "preserves comment ordering".
- PyYAML alone cannot satisfy that requirement; mixing the two within one
  helper is straightforward.

**Test file:** `scripts/tests/test_yaml_frontmatter.py`

Minimum test cases:
1. `read_frontmatter` on file with frontmatter → metadata + body extracted
2. `read_frontmatter` on file without frontmatter → metadata empty, body=full
3. `read_frontmatter` on file with malformed frontmatter → raises typed error
4. `update_frontmatter` preserves trailing comments
5. `update_frontmatter` preserves key order; appended keys go at end
6. `update_frontmatter` is atomic (simulate crash mid-write → original intact)
7. `frontmatter_session` writes on clean exit
8. `frontmatter_session` does NOT write on exception
9. `frontmatter_session` releases lock on exception
10. `update_frontmatter` removes keys from `remove_keys`

**G4 allow-list mechanism**
- The helper module is listed by absolute path in G4's allow-list constant
  (in `scripts/quality/check_no_handrolled_yaml.py`).
- Single source of truth; not via `# noqa` comment (a typo in a comment
  would silently let the pattern leak elsewhere).

**Decision:** New module at `scripts/util/yaml_frontmatter.py` using
`ruamel.yaml`; three-entry-point API (read / one-shot update / context
manager); tests at `scripts/tests/test_yaml_frontmatter.py`; G4 allow-lists
the helper by absolute path.

**Why:** Three entry points match the three real call patterns observed in
the survey (read-only parse, one-shot field update, multi-field session).
`ruamel.yaml` is non-negotiable given the comment-preservation requirement.
Atomic write via tmp-rename matches the established pattern in
`orchestrate.py`.

---

## E. G4 gate (no hand-rolled YAML)

**Approach comparison**

| Approach | Pro | Con |
|---|---|---|
| `ripgrep`/`grep` regex | Trivial to write | High false-positive on docstrings/comments containing `---`; cannot scope to function bodies |
| **Python AST visitor** | Precise — only flags real code patterns | More code; ~150 LOC |
| `ruff` custom rule | Future-proof | Custom plugins are unstable across ruff versions; over-investment for one check |

**Recommended: Python AST visitor.**

**Path:** `scripts/quality/check_no_handrolled_yaml.py`

**Pattern signatures to detect**

A function/module is flagged if it contains BOTH:

1. A string-literal comparison against `"---"`:
   - `node.line.strip() == "---"`
   - `lines[i] == "---"`
   - any `Compare(left=…, ops=[Eq], comparators=[Constant('---')])`

2. Either:
   - A boolean local named `in_frontmatter`, `in_fm`, or `frontmatter_started`
     (any `Name`/`Assign` to one of these), OR
   - A `split(":")` / `split(":", 1)` call on a stripped line within a loop
     that also contains pattern (1).

Both signatures must appear in the same function scope. False positives
(e.g. markdown-rendering code that happens to compare to `"---"`) are
acceptable — they can be suppressed via the per-file allow-list.

**Allow-list:** module-path list constant at top of the gate script;
contains only `scripts/util/yaml_frontmatter.py`.

**Output format:** one line per finding —
`<path>:<line>: hand-rolled YAML-frontmatter parser pattern`
plus a summary line. Exit 0/1/2 per the gate convention.

**Self-test:** the gate is *expected* to fail on develop after this task
lands. The script's docstring states this explicitly; CLAUDE.md states it
too. AC-criterion for this task: the gate fails on
`orchestrate.py`/`generate_status_overview.py`/`generate_id_registry.py`
and passes on `yaml_frontmatter.py`.

**Decision:** AST visitor implementation at
`scripts/quality/check_no_handrolled_yaml.py`; two-signature pattern as
above; allow-list constant lists the helper path.

**Why:** AST visitor is precise enough to avoid the docstring false-positive
trap that regex would hit, while still being a single ~150 LOC file. A
ruff plugin is over-investment; a grep is under-investment.

---

## F. G5 gate (print discipline)

**Approach:** AST visitor — find `Call(func=Name('print'))` nodes.

**CLI vs non-CLI determination**

A module is **CLI** iff it contains a top-level
`if __name__ == "__main__":` block. The vast majority of `scripts/`
follows this convention.

For a CLI module with `print()` calls:
- The module docstring (first triple-string at module level) MUST contain the
  literal substring `Output:` or `Output contract:` (case-sensitive). This
  marks the documented output stream per AC-09.
- If absent → the print call is a violation even in CLI context.

For a non-CLI module (no `if __name__ == "__main__":`):
- Any `print()` call is a violation. Logging (`logging.info(...)`,
  `logging.debug(...)`, etc.) is the alternative.

**Exception — diagnostic helpers**: `sys.stderr` and `sys.stdout.write` are
not `print()` and not flagged. `pprint.pprint` is flagged the same way as
`print` (it produces unstructured output for human consumption).

**Path:** `scripts/quality/check_print_discipline.py`

**Output:** `<path>:<line>: print() in non-CLI module` or
`<path>:<line>: CLI module uses print() but docstring missing 'Output:' contract`.

**Decision:** AST visitor at `scripts/quality/check_print_discipline.py`;
CLI detection by presence of `if __name__ == "__main__":` block; docstring
must contain `Output:` substring for CLI prints to be allowed.

**Why:** `if __name__ == "__main__":` is already the universal CLI marker
in this repo — no ambiguity, no folder rule needed. The `Output:` substring
gate is greppable, ruff-style, and forces a deliberate documentation step.

---

## G. Single Python gate-runner entry point

**Path:** `scripts/quality/check_python_gates.sh`

**Shape:** structurally identical to `check_quality_gates.sh` (Dart-side).
Bash, runs each gate as a subprocess, collects per-gate exit codes, prints
summary, exits with the union.

```bash
GATES=(
    "G1 lint           | ruff_check.sh"
    "G2 type           | mypy_check.sh"
    "G3 tests          | pytest_check.sh"
    "G4 no-handrolled  | check_no_handrolled_yaml.py"
    "G5 print-discip.  | check_print_discipline.py"
)
```

Where:
- `ruff_check.sh` → `ruff check scripts/`
- `mypy_check.sh` → `mypy --config-file pyproject.toml scripts/`
- `pytest_check.sh` → `python3 -m pytest -q`

These three thin wrappers live in `scripts/quality/` alongside the custom
gate scripts. Wrappers exit 0/1/2 per the standard convention. (Each tool's
native exit code is normalized to 0/1/2 by the wrapper.)

`scripts/quality/check_python_gates.sh` does NOT touch the Dart-side runner.
Both are independent; a future top-level wrapper can run both if needed.

**Decision:** Shell runner at `scripts/quality/check_python_gates.sh`
mirroring Dart pattern; three thin tool-wrapper shell scripts for G1/G2/G3;
two AST-visitor Python scripts for G4/G5.

**Why:** Shell wrapper matches Dart side ⇒ developers learn one pattern.
Using shell for the orchestration (rather than Python) avoids bootstrapping
issues if mypy/ruff themselves are broken. Thin shell wrappers around the
tools (rather than calling them directly in the runner) keep each gate
independently invocable — same pattern as `check_no_telemetry_sdks.py`
being runnable standalone.

---

## H. CLAUDE.md update

**Insertion point:** Section 7 ("Coding Standards (Summary)"), under the
existing **Quality** subsection (after `dart fix --apply` line), add:

```
**Python gates** (REQ-PROC-051):
- Run before any Python work is declared complete:
    scripts/quality/check_python_gates.sh
- Five gates: G1 lint (ruff), G2 type (mypy), G3 tests (pytest),
  G4 no hand-rolled YAML, G5 print() discipline.
- **Intermediate state**: develop currently FAILS G4 and may fail others —
  the cleanup pass that brings scripts/ to passing is TASK-PROC-051-04.
  Do not block your task on develop's baseline; block on whether YOUR
  change introduces a NEW finding.
- Tier annotation: every Python module under scripts/ carries a
  `# tier: A | B | C` header comment immediately after its docstring.
  See requirements_tasks/.../python_code_quality/requirements.md for tier
  definitions.
- New OS-level tooling installs (e.g. uv): use the `claude-install-os-tool`
  skill.
```

**Decision:** Append the above block to Section 7 of CLAUDE.md.

**Why:** Mirrors the existing Quality block phrasing; calls out the
intermediate-state caveat explicitly so the next agent doesn't waste cycles
trying to "fix" develop's baseline failures.

---

## I. Risk surface + open questions

**Risks**
- `ruamel.yaml` is a heavier dependency than PyYAML (~ 5× install size).
  Acceptable cost for the comment-preservation property.
- `uv` is a non-stdlib install. Mitigated by `requirements-dev.txt` fallback
  + `claude-install-os-tool` skill making the install discoverable.
- G4 false positives are possible on innocuous `"---"` comparisons.
  Mitigated by the two-signature requirement; if needed, per-file allow-list.
- Tier-annotation header convention is enforced only by the gate-runner's
  WARNING (not FAIL). The full-pass annotation is -04; if -04 slips, the
  WARNING never becomes a FAIL and the convention slowly rots. Acceptable
  for now; flag the risk to user.
- `if __name__ == "__main__":` as CLI detector — a future module that splits
  CLI entry into a thin `__main__.py` would defeat the check. Acceptable;
  no such pattern exists today.
- `pyproject.toml` may conflict with future packaging intent. There is no
  packaging intent today; if it changes, separate the config into a
  dedicated `tool/python-quality/pyproject.toml`.

---

## Implementation order

The implementation-engineer agent should produce files in this sequence:

1. **`pyproject.toml`** (root) — ruff + mypy + pytest config blocks; declare
   dev deps including `ruff`, `mypy`, `pytest`, `ruamel.yaml`.
2. **`requirements-dev.txt`** (root, with hashes) — exported from `uv lock`.
3. **`uv.lock`** (root) — generated by `uv sync`.
4. **`devcontainer.json`** — add `uv` install via `claude-install-os-tool`
   skill (post-create command).
5. **`scripts/util/yaml_frontmatter.py`** — the helper module; tier B header.
6. **`scripts/tests/test_yaml_frontmatter.py`** — the 10 test cases.
7. **`scripts/quality/check_no_handrolled_yaml.py`** — G4 AST gate; allow-list
   contains only the helper path.
8. **`scripts/quality/check_print_discipline.py`** — G5 AST gate.
9. **`scripts/quality/ruff_check.sh`** — G1 wrapper.
10. **`scripts/quality/mypy_check.sh`** — G2 wrapper.
11. **`scripts/quality/pytest_check.sh`** — G3 wrapper.
12. **`scripts/quality/check_python_gates.sh`** — single entry point.
13. **`scripts/quality/README.md`** — append Python gates section.
14. **POC tier annotations** — add `# tier: A` header to
    `scripts/automation/orchestrate.py`, `# tier: B` to helper (done in
    step 5), `# tier: C` to `scripts/tasks/goal_preview.py`.
15. **`CLAUDE.md`** — append Python gate block to Section 7.
16. **Smoke run** — `scripts/quality/check_python_gates.sh`; expect G4 to
    fail on the surveyed sites (proof of correctness) and the helper to
    pass G4 (proof of allow-list). Record output in protocol.md.

Total: ~16 new/modified files. Exceeds the architecture-advisor "max 4
files" guideline — but the task is explicitly mechanism-bearing
infrastructure (config + new gate framework + helper + tests), not a typical
feature change. Splitting would only fragment one coherent deliverable.

---

## Open questions for user

1. **Package manager choice (Section B).** Default recommendation is `uv` +
   `uv.lock` + `requirements-dev.txt` fallback. Acceptable alternative is
   `pip-tools` (`pip-compile`) — older, slower, but already familiar.
   Confirm `uv`, or pick alternative.

2. **POC TIER C module (Section C).** Recommendation:
   `scripts/tasks/goal_preview.py`. Any preference? Other candidates:
   `scripts/tasks/is_awaiting_answer.py`, `scripts/tasks/summarize_plan.py`.

3. **`devcontainer.json` install for `uv`.** Confirm we should invoke
   `claude-install-os-tool` to add `uv` to the devcontainer's
   `postCreateCommand` during this task (per the skill's standard flow).
   Alternative: hold off and let TASK-PROC-051-04 do it.

4. **G4 missing-tier behavior** (Section C). Modules without a
   `# tier:` header in this task default to TIER B + WARNING in the
   gate-runner output. Should the WARNING become a FAIL the moment
   TASK-PROC-051-04 lands (its job to annotate everything)? Or stay as
   WARNING permanently to leave room for ad-hoc additions?

5. **G5 CLI marker** (Section F). Confirm `if __name__ == "__main__":` is
   the right CLI detector for this repo. Alternative: a header comment
   `# cli: true`. The `__main__` check matches existing convention; the
   header is more explicit at the cost of touching every CLI file.

6. **mypy strict scope.** The plan starts strict mode for ONE module
   (`orchestrate.py`) in this task; the full TIER A enumeration is -04's
   job. Confirm that's acceptable rather than enumerating known TIER A
   modules now.
