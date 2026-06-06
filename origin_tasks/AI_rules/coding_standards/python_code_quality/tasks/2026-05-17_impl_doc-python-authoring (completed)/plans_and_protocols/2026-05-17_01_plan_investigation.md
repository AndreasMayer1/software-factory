---
type: plan
task_id: TASK-PROC-051-03
created: 2026-05-17
agent_id: main-session-opus-4-7
related_task: 2026-05-17_impl_doc-python-authoring
---

# TASK-PROC-051-03 — Investigation & Drafting Plan

## 1. Predecessor State

Both prerequisite tasks completed:

- **TASK-PROC-051-01** (exploration) — created REQ-PROC-051 at
  `requirements_tasks/process/AI_rules/coding_standards/python_code_quality/requirements.md`.
  Also updated `doc/README.md`'s "Language Scope" section to state the
  Dart-default convention and list `doc/python/` as the Python folder
  (AC-14 partially satisfied; routing-table row currently has the
  parenthetical "*(authored by the REQ-PROC-051 impl task)*").
- **TASK-PROC-051-02** (mechanism) — landed the tooling at
  `pyproject.toml`, the central YAML helper at
  `scripts/util/yaml_frontmatter.py`, the G4 / G5 gate scripts at
  `scripts/quality/check_no_handrolled_yaml.py` and
  `scripts/quality/check_print_discipline.py`, and the runner at
  `scripts/quality/check_python_gates.sh`. Tier annotation convention
  is **`# tier: A|B|C` header comment immediately after the module
  docstring** (no folder rule; per-module). Three POC modules already
  carry it: `orchestrate.py` (A), `yaml_frontmatter.py` (B),
  `goal_preview.py` (C).

This task fleshes out `doc/python/` and finalises `doc/README.md`'s
Python row. It does NOT migrate or clean up existing code — that is
TASK-PROC-051-04.

## 2. Canonical Code Anchors (file:line citations)

Every canonical pattern in REQ-PROC-051 (AC-04 .. AC-09) must cite an
existing implementation; no re-derived prose. Anchors verified during
phase 1:

| AC | Pattern | Anchor |
|---|---|---|
| AC-04 | Substitutable-boundary dataclass-of-callables (`OrchestratorDeps`) | `scripts/automation/orchestrate.py:1587-1617` (class definition + field list) |
| AC-05 | Clock read through boundary (`get_now_utc` / `get_now_local` fields) | `scripts/automation/orchestrate.py:1614-1615`; production default `datetime.now(timezone.utc)` |
| AC-06 | Context-manager invariant — `active_session(...)` | `scripts/automation/orchestrate.py:750-770` (`@contextmanager` block clearing `state.active_session` on enter and `__exit__` whether the body returns or raises) |
| AC-07 | Named outcomes — `PromoteResult` Enum | `scripts/automation/orchestrate.py:1157-1177` (four-member enum with `is_success` property; replaced a former `bool` return) |
| AC-08 | Central YAML helper — single allow-listed module | `scripts/util/yaml_frontmatter.py:1-60` (module docstring is the contract; entry points `read_frontmatter`, `update_frontmatter`, `frontmatter_session`) |
| AC-09 | Print discipline — protocol vs internal logging | Current state: protocol prints at `scripts/automation/orchestrate.py:143, 261, 274, 295, 483`; **no named helper exists yet**. Doc must describe the destination (single named helper) while honestly noting the orchestrator's current state. TASK-PROC-051-04 lands the helper. |

Anti-pattern incidents to anchor `anti_patterns.md` (per AC-12 / goal note):

- **Hand-rolled YAML**: three orchestrator state machines that shared a
  bug surface (cited in REQ-PROC-051 §Purpose). Reference also the
  TASK-PROC-051-02 plan §"Hand-rolled YAML parser sites confirmed for
  G4" listing 4 confirmed sites; G4 discovered 21 in total.
- **Frozen-clock leak (2026-05)**: a clock read that bypassed the
  boundary, causing frozen-clock tests to drift against wall-clock
  advancement. Cited in REQ-PROC-051 §Purpose ¶2.
- **Dual-tracker (TASK-PROC-046-03, 2026-05)**: two parallel tracker
  fields updated independently; forgetting one was the failure mode.
  Cited in REQ-PROC-051 §Purpose ¶2.

## 3. File-by-File Authoring Plan (doc/python/)

All files stay ≤ 600 lines per REQ-PROC-048. Cross-link via relative
markdown links.

### `doc/python/README.md`
- **Role**: entry point; orientation for first-time readers and
  routing target for `doc/README.md`'s Python row.
- **Content**:
  - 1-paragraph framing: REQ-PROC-051 governs `scripts/` (~30 kLOC,
    ~60 files); gates live at `scripts/quality/check_python_gates.sh`;
    tooling at `pyproject.toml`.
  - Tier table (A/B/C) with the **defining property** of each, mapped
    to the canonical example: orchestrate.py (A), yaml_frontmatter.py
    (B), goal_preview.py (C). State the tier-annotation form: `# tier:
    X` header comment immediately after the module docstring.
  - "How to add a tier to a new module" — one-line rule + a one-block
    example.
  - Pointer table to the rest of the folder.
  - Pointer that `pyproject.toml`, `scripts/quality/check_*.sh`, and
    the AST gates are *authoritative for tool behavior*; this folder
    is authoritative for *judgment-level rules and the why*.

### `doc/python/style.md`
- What G1 (ruff) enforces, **by rule category** not by every code:
  pycodestyle (E/W), pyflakes (F), bugbear (B), isort (I), pyupgrade
  (UP), simplify (SIM), comprehensions (C4), return (RET), ruff-native
  (RUF). Cite `pyproject.toml:20-34`.
- Format conventions: double quotes, trailing commas (ruff format,
  Black-compatible); `pyproject.toml:41-44`.
- Module docstring conventions: every module starts with a one-line
  purpose docstring; TIER C and protocol-producing CLIs add an
  `Output:` contract line (cite `scripts/tasks/goal_preview.py` and
  `scripts/util/yaml_frontmatter.py` as examples).
- Naming: stdlib-conventional snake_case for functions/variables,
  CamelCase for classes; no project-specific naming rules.
- Line length: ignored by ruff (`E501` disabled — see pyproject.toml
  `ignore = ["E501"]`) — the formatter handles wrapping; do not
  preformat manually.
- Tier-annotation header form documented as the authoritative
  convention.

### `doc/python/type_hints.md`
- G2 strictness model: `[tool.mypy]` baseline (lenient but real —
  `warn_unused_ignores`, `warn_redundant_casts`, `warn_unreachable`,
  `no_implicit_optional`) for TIER B / TIER C; `[[tool.mypy.overrides]]
  strict = true` for TIER A modules (cite pyproject.toml:60-69).
- Tests get `check_untyped_defs = false` (cite pyproject.toml:71-75) —
  rationale: tests are deliberately concise.
- When `# type: ignore[<code>]` is acceptable: only with an adjacent
  inline justification (REQ-PROC-051 AC-13). Cite the AC-13 example
  from `requirements.md:149-153`. Bare `# type: ignore` (no code list)
  is itself a violation.
- Pattern for stub-less stdlib / third-party calls: `# type:
  ignore[import-untyped]` with a one-line reason; promote to a typed
  shim only if the call recurs in TIER A.
- Future-proofing: when promoting a TIER B module to TIER A, add it to
  the strict override list in `pyproject.toml`.

### `doc/python/dependency_injection.md`
- The substitutable-boundary rule (AC-04 / AC-05) with the orchestrator
  as canonical reference.
- Cite `OrchestratorDeps` at `scripts/automation/orchestrate.py:
  1587-1617` — what each callable abstracts (`run_subprocess`,
  `read_file`, `get_now_utc`, `sleep`, etc.).
- The rule: any side-effecting call — subprocess, file I/O, network,
  clock, sleep, process-identity, env-var — goes through the dataclass.
  Pure functions do not.
- The corollary: "if you reach for module-level stdlib monkey-patching
  in TIER A, add the call to the boundary instead." Module-level
  patching of stdlib symbols scopes the fake to the whole test process
  and leaks; the boundary scopes it to a single call.
- Production-default vs test-fake wiring: every field's default is the
  real stdlib call (e.g. `sleep = time.sleep`); tests construct
  `OrchestratorDeps(...)` with fakes only for boundaries they care
  about, leaving the rest as real. Note that defaults are wired at
  construction time, not as field defaults on the dataclass.
- Promotion criterion (judgment rule): a TIER B module accumulates
  side-effecting calls or wall-clock dependence ⇒ candidate for TIER A
  + boundary.

### `doc/python/testing.md`
- Test runner: pytest; collection roots `scripts/automation/tests` and
  `scripts/tests` (cite pyproject.toml:81-87). Co-located tests
  preferred when the module is in a domain folder
  (`scripts/automation/tests/`); central `scripts/tests/` for
  cross-cutting helpers (e.g. `scripts/util/yaml_frontmatter.py` →
  `scripts/tests/test_yaml_frontmatter.py`).
- AC-10 restated: every imported module needs a direct test; TIER C
  one-shot CLIs with no imported callers are exempt; TIER A modules
  are never exempt.
- Frozen-clock pattern — through the boundary. Bad: `freezegun` /
  `mock.patch("module.datetime.now")`. Good: construct
  `OrchestratorDeps(get_now_utc=lambda: datetime(2026,5,17, …))`. Cite
  AC-05 and the 2026-05 incident.
- Coverage stance: no global threshold; AC-10 is the structural
  minimum. Adding a test because "coverage dropped" is wrong; adding a
  test because "an imported module had none" is right.
- Naming and structure: `test_*.py` files; `test_<behavior>` function
  names; class grouping permitted when many tests share fixtures.

### `doc/python/architecture.md`
- The three-tier model with anchored examples:
  - **TIER A** — `scripts/automation/orchestrate.py` (3330 LOC,
    long-lived, owns `state.active_session` invariant, depends on
    wall-clock advancement). Required: AC-04..AC-07, strict typing,
    tests.
  - **TIER B** — `scripts/util/yaml_frontmatter.py` (306 LOC, imported
    by multiple call sites). Required: AC-08, AC-09, AC-10, AC-13;
    AC-04..AC-07 recommended.
  - **TIER C** — `scripts/tasks/goal_preview.py` (small one-shot CLI).
    Required: AC-01, AC-02, AC-13; AC-09 with `Output:` contract.
- Tier-annotation form (authoritative): `# tier: A|B|C` header comment
  immediately after the module docstring. Show a 4-line code block
  illustrating.
- Promotion criterion: when a TIER B helper acquires in-memory state
  across sessions, owns an invariant across try/except boundaries, or
  starts reading the wall clock, promote to TIER A — and add it to the
  strict override list in `pyproject.toml`.
- Context-manager-for-invariants rule: any invariant that must hold
  across an exception belongs in one `@contextmanager` block, not in
  hand-rolled try/finally at multiple call sites. Cite
  `active_session` at `scripts/automation/orchestrate.py:750-770`.
- Named-outcomes rule: when a function has three or more meaningful
  outcomes, return an enum (or tagged union), not `bool`. Cite
  `PromoteResult` at `scripts/automation/orchestrate.py:1157-1177`.

### `doc/python/anti_patterns.md`
- Each anti-pattern leads with the incident or concrete risk; the rule
  follows.
- **Hand-rolled YAML**: lead with the orchestrator's three independent
  state machines that shared a bug surface (cite
  `requirements.md:60`). Rule: AC-08 — use `scripts/util/yaml_frontmatter.py` or
  `yaml.safe_load`. G4 enforces.
- **`print()` for internal status in non-CLI modules**: conflates
  protocol with debug, prevents log-level control. Rule: AC-09; G5
  enforces. CLI modules with an `Output:` docstring are allowed.
- **Parallel mutation of two fields**: lead with the May 2026
  dual-tracker incident (TASK-PROC-046-03) — two parallel tracker
  fields updated independently; forgetting one was the failure mode.
  Rule: a single mutation method, not a calling convention.
- **Blanket `except Exception:`**: swallows the bug just observed; in
  TIER A the cost is direct (orchestrator silently doesn't launch).
  Rule: name the class or let it propagate.
- **Module-level monkey-patching of stdlib in TIER A**: scopes the
  fake to the process, leaks. Rule: AC-04 — add the call to the
  substitutable boundary instead.
- **Clock read bypassing the boundary**: lead with the 2026-05
  frozen-clock-drift incident (cite `requirements.md:60` ¶2). Rule:
  AC-05; every wall-clock read in TIER A goes through
  `OrchestratorDeps.get_now_utc` / `get_now_local`.
- **Bare suppression** (`# noqa`, `# type: ignore` without code +
  reason): rule AC-13 — every suppression carries a code list and an
  adjacent inline justification.

## 4. Updates to `doc/README.md`

- Replace the parenthetical "*(authored by the REQ-PROC-051 impl
  task)*" in the routing table row (line 35) with a clean entry now
  that the target exists.
- Keep the Language Scope table and surrounding prose unchanged —
  they already correctly describe the convention (AC-14 verified).

## 5. Updates to `.claude/agents/quality-checker.md`

- Phase 1 step "Read doc/README.md to find the relevant guideline
  folder for that layer, then read it" already routes via
  doc/README.md, so no logic change needed there — but the prompt
  references only Dart layers ("domain/data/presentation") and adds a
  static-analysis step for Dart projects only. Add an explicit Python
  branch:
  - If any changed file matches `scripts/**/*.py`, read
    `doc/python/README.md` and the linked subpages relevant to the
    change.
  - Replace the Dart-only "Run `dart analyze`" step with a branch:
    Dart changes → `dart analyze`; Python changes → reference
    `scripts/quality/check_python_gates.sh` as the authoritative gate
    runner (do not run it inside the agent — the gate runner is the
    contributor / task-complete responsibility; the agent's role is
    review, not execution).
- Keep the rest of the prompt intact.

## 6. Acceptance-Criterion Mapping

| Goal AC | Satisfied by |
|---|---|
| `doc/python/README.md` exists / entry point | Phase 3a — README.md authored first |
| `doc/README.md` Language Scope consistent + routing row resolves | Phase 3c — strip parenthetical on routing row |
| No Python guidance in Dart `doc/` folders | Verification — grep Dart folders for `python` / `scripts/` references; expected: zero |
| Each `doc/python/` file ≤ 600 lines (REQ-PROC-048) | Verification — `wc -l doc/python/*.md` |
| Every AC-04..AC-09 canonical pattern has a file:line ref | Verification — grep each doc/python/*.md for `:[0-9]` line refs against the anchors in §2 |
| Anti-patterns name real incidents (2026-05 frozen clock; TASK-PROC-046-03 dual-tracker) | Verification — grep `anti_patterns.md` for both anchors |
| `quality-checker` prompt updated for Python | Verification — agent file diff in §5 applied |
| Tier-annotation convention documented as authoritative | Phase 3a (README.md) and Phase 3f (architecture.md) — both state `# tier: X` header form |

## 7. Drafting Mode

Per goal §Notes: spawn a background general-purpose agent (Opus model
inherited) to author the 7 doc/python/ files in one pass, then update
`doc/README.md` and `.claude/agents/quality-checker.md`. Main session
runs a 4:30 heartbeat while the agent works. After the agent reports
completion, main session does the verification pass inline.

The agent's brief is this file (§3, §4, §5 are its specification, §2
is its citation database, §6 is its self-check).
