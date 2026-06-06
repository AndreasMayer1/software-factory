---
id: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: L
stakeholder: app_provider
created: 2026-05-17
updated: 2026-05-17
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "All Python sources under `scripts/` produce zero violations from the project's static-lint gate, zero errors from the type-check gate, and zero failures from the test gate, against the configuration named in the project's Python tooling configuration. Each gate is binary (pass / fail) and measurable from a clean checkout."
    - id: AC-02
      text: "The Python tooling configuration — the linter rule selection, the type-checker strictness per tier, the test-collection contract, and pinned versions of every tool used by the gates — is authoritative, version-controlled in the repo, and reproducible: a fresh dependency install on any developer machine that has the supported Python version produces the same gate pass/fail result as the CI baseline. When the configuration and this requirement disagree, the configuration is the authority for tool behavior and is corrected if it drifts; this requirement is the authority for what the gates measure."
    - id: AC-03
      text: "Every Python module under `scripts/` has a documented tier — TIER A (long-lived stateful tool that maintains in-memory state across user-facing sessions, depends on wall-clock advancement, or owns invariants across try/except boundaries), TIER B (generator, validator, or reusable library imported by other modules), or TIER C (one-shot CLI utility ≤ 100 SLOC with no imported callers). The tier of every module is determinable without ambiguity — either explicit on the module itself or implied by a folder-level convention documented in `doc/python/`."
    - id: AC-04
      text: "Every TIER A module abstracts its side-effecting operations — subprocess calls, file I/O, network I/O, clock reads, sleep, process-identity reads, environment-variable reads, and any external system access — behind a substitutable boundary, so that tests can replace any boundary with a fake without resorting to module-level monkey-patching of stdlib symbols. The production default for each boundary is the real implementation. The substitution is local to a test, not process-wide."
    - id: AC-05
      text: "Every read of wall-clock time in a TIER A module, including indirect reads through helper functions, goes through the substitutable clock boundary of AC-04. Tests running on a frozen clock never drift against real wall-clock time. The orchestrator's session, account, and rate-limit logic, and any future TIER A module that branches on wall-clock advancement, satisfies this property."
    - id: AC-06
      text: "Every invariant in a TIER A module that must hold across an exception or early-return path — for example, an active-session reference that must be cleared whether the launch returns or raises, or a temp directory that must be removed — is enforced by a single language-level construct that guarantees cleanup (a context manager or equivalent). The same invariant is not re-implemented at multiple call sites through hand-rolled try / finally / cleanup sequences."
    - id: AC-07
      text: "Functions and methods that can return three or more meaningful outcomes return a named-outcome value (an enum or equivalent tagged union), not `bool`. Functions whose answer is genuinely yes-or-no return `bool`. Callers branch on the named outcome, not on truthiness."
    - id: AC-08
      text: "No file under `scripts/` contains a hand-rolled YAML frontmatter parser — a state machine that walks lines tracking `---` boundaries and parses keys by string splits. All YAML reads use a standard YAML library. If a use-case requires preserving comments or in-place atomic updates, the parsing is centralized in a single shared helper module and reused by every call site; the helper itself is the only place such parsing exists."
    - id: AC-09
      text: "In non-CLI modules — modules that are imported by other code rather than executed directly — internal status and debug output uses the project's logging facility, not unstructured `print()`. CLI modules may use `print()` for their documented user-facing output stream, and the contract (which stream, which downstream consumer, which format) is named in the module's top-level docstring. Modules that play the dual role of CLI entry point and public-protocol producer route their protocol output through a single named helper, so the protocol surface is greppable and replaceable; the helper's name does not matter, its existence does."
    - id: AC-10
      text: "Every Python module reused by import — modules that other Python files import from, regardless of tier — has at least one direct test. TIER C one-shot CLI scripts with no imported callers are exempt. TIER A modules are not exempt regardless of import status: their behavior is contract whether or not other Python imports them, because they are entry points consumed by external systems."
    - id: AC-11
      text: "Code that fails any active gate in this requirement is never declared complete: every gate failure triggers a revision cycle under the back-pressure protocol defined in REQ-PROC-046 §Back-Pressure Protocol — five-cycle bound, automation Q&A escalation via the project's pending-feedback channel. This requirement does not redefine the protocol; it inherits and applies it. The `quality-checker` agent reads `doc/python/` alongside the Dart `doc/` folders so judgment-level rules surface from the same place."
    - id: AC-12
      text: "The active set of Python gates, the tier classification rule, the canonical pattern set referenced by AC-04 through AC-09, and the called-out anti-patterns are documented in `doc/python/` — and nowhere else under `doc/`. `doc/python/README.md` is the entry point. The Dart-oriented folders under `doc/` (`architecture/`, `testing/`, `linter/`, `presentation/`, `domain/`, `cross_cutting_standards/`, `general/`) contain zero Python-specific guidance. A contributor or LLM agent looking for Python guidance reaches `doc/python/` via `doc/README.md`'s routing table without traversing Dart folders."
    - id: AC-13
      text: "Every active suppression of a Python lint or type-check rule (`# noqa: <code>`, `# type: ignore[<code>]`, or any tool-specific per-line disable directive) is accompanied by an adjacent inline comment naming why the rule does not apply to the specific case. Bare suppressions without a code list, and module-level blanket suppressions without justification, are themselves violations."
    - id: AC-14
      text: "`doc/` is organized with Dart as the default language and every non-Dart language isolated to its own subfolder (`doc/python/`, and any future `doc/<lang>/`). The Dart-oriented folders do not include language-disambiguation prose; they assume Dart. `doc/README.md` makes the default explicit and lists the dedicated non-Dart folders so the rule is discoverable from the documentation entry point."
    - id: AC-15
      text: "Every change to a Python module under `scripts/` reaches the gate runner of AC-01 before the change is declared complete. The invocation is mediated by project-level mechanisms — a skill, a hook, a pre-commit trigger, or any equivalent — that operate outside the agent's discretion, layered so that a bypass of the primary invocation path is caught by at least one independent backstop. A configuration in which the only thing preventing a Python edit from skipping the gates is the agent's memory or a documentation note does not satisfy this AC. The specific surfaces are an implementation choice; the layered, non-discretionary property is the requirement."
---

# Python Code Quality Standard (LLM Back-Pressure Gates)

## Overview

This requirement defines what "good code quality" means for Python in this repository — the `scripts/` tree, ~30 000 lines across ~60 files covering the autorun orchestrator, requirement/task tooling, generators, validators, the concept-canon audit, the release pipeline, and supporting utilities. Quality is enforced through the same back-pressure mechanism as the Dart side (REQ-PROC-046): an LLM agent or contributor cannot declare a Python change complete while any per-change gate is failing.

REQ-PROC-051 is a sibling to REQ-PROC-046 (Dart) and REQ-PROC-052 (Privacy & Security). The three requirements share the back-pressure protocol; each names its own gates.

## Purpose

The app provider (PERSONA-015) is a solo developer maintaining a mental-health application. The user-facing product is Flutter / Dart, but the *factory* that produces, governs, and releases it is Python. The orchestrator alone is several thousand lines with a multi-thousand-line test suite; surrounding tooling adds an order of magnitude more.

The cost of leaving Python ungoverned is concrete and already observable. Three independent functions in the orchestrator hand-rolled the same YAML-frontmatter state machine and shared a bug surface — a fix in one did not propagate. Ten more files across the artifacts, release, and requirements toolchains repeat the pattern. A real incident in 2026-05 traced to two parallel tracker fields being updated independently — forgetting one was the failure mode. Another incident in 2026-05 traced to a clock read that bypassed the substitutable boundary, so tests running on a frozen clock drifted out from under wall-clock advancement. None of these were exotic — they were the predictable result of patterns being learned in one file and not codified.

The Python codebase has also accumulated useful patterns that emerged from real refactors: substitutable side-effect boundaries enabling local fakes; a frozen-clock testing discipline that lives in test setup, not in production code; a context-manager invariant that turned five hand-rolled set/save/clear sequences into one cleanup-guaranteed block; a helper that turned two parallel mutations into one method; an enum that replaced a `bool` whose `False` conflated three distinct outcomes; factory functions that centralised the common shape of records produced at many sites. These patterns work for this repo; they need to be findable by a future agent who has not seen the conversation that produced them.

PERSONA-015's grounded value of *"longevity over velocity"* and *"the codebase must survive periods where the creator has no time to touch it"* applies as strongly to the Python factory as to the Dart product. PERSONA-004's system-maintenance perspective compounds this: the orchestrator runs unattended and produces the daily flow of work for the LLM; a failure there does not lose a debug session, it stops the factory.

Like REQ-PROC-046, this requirement encodes quality as machine-checkable gates because there is no human capacity to review every Python change consistently. The LLM that writes most of the Python is structurally constrained to satisfy the gates before declaring work complete. The gates do not chase universal "good Python" style; they encode the specific lessons this repo has already paid for.

## When This Requirement Applies

- Any change to Python code under `scripts/` produced by an LLM agent or a human contributor.
- Before a task is marked complete (via `task-complete` or otherwise).
- Before a commit is created on `develop`.
- Authoring or modifying the project's Python tooling configuration.

## When This Requirement Does NOT Apply

- Dart code under `lib/`, `test/`, `integration_test/` — governed by REQ-PROC-046.
- Generated Python files (none today; the exclusion is stated for symmetry with REQ-PROC-046).
- PowerShell scripts under `scripts/windows/` — not Python; governed by ad-hoc convention (no formal requirement exists today).
- Documentation under `doc/python/` itself — governed by REQ-PROC-048 (file organization).
- One-off automation `.py` files outside `scripts/` (none today; the exclusion is stated so that a future ad-hoc location does not silently inherit the gate set).

## Behavior

### Tiers

Every Python module under `scripts/` is classified into one of three tiers. The tier determines which rules apply.

| Tier | Defining property | Required by |
|---|---|---|
| **TIER A** — long-lived stateful | Maintains in-memory state across user-facing sessions, depends on wall-clock advancement, or owns invariants across try/except boundaries. The autorun orchestrator is the canonical example. | AC-04, AC-05, AC-06, AC-07 (strongest pattern set), strict type checking, tests |
| **TIER B** — generator / validator / reusable library | Imported by other Python modules. Includes generators that produce repo artifacts, validators, parsers, and any helper exposed via `import`. | AC-08, AC-09, AC-10, AC-13; default type checking; pattern set of AC-04–AC-07 is recommended but not mandatory |
| **TIER C** — short one-shot CLI | ≤ 100 SLOC, no imported callers, single-purpose invocation. | Lint and type-hint hygiene (AC-01, AC-02, AC-13). The pattern set is not mandatory but is still recommended where it fits naturally. |

The set of three tiers is closed. Adding or removing a tier is a change to this document.

### The Quality Gates

Five gates are active. Each is binary (pass / fail) and measurable from a clean checkout. The implementation of each gate (which specific tools, which check scripts, which CLI invocation) is the responsibility of the project's Python tooling configuration; this requirement names what each gate measures.

| Gate | What it measures | Cadence |
|---|---|---|
| **G1 Style + lint** | Zero violations from the project-configured static-lint tool. The configured rule set covers, at minimum: pyflakes-level correctness (undefined names, unused imports), common bug patterns (mutable default arguments, comparison-to-singleton, exception-handling smells), import ordering, and Python-modernization rules. | per-change |
| **G2 Type check** | Zero errors from the project-configured type checker. TIER A modules are checked under strict mode; TIER B and TIER C use the default configuration. Missing third-party stubs may be silenced with adjacent justification per AC-13. | per-change |
| **G3 Test correctness** | Zero failures and zero errors from the project-configured test runner over the configured collection roots. AC-10 is the *structural* requirement (which modules must have tests); G3 is the *correctness* requirement (the tests must pass). | per-change |
| **G4 No hand-rolled YAML** | Zero matches for the hand-rolled YAML-frontmatter parser pattern (line-by-line `---` state machines) outside the centralized helper module that AC-08 implies. | per-change |
| **G5 print() discipline** | Zero `print()` calls in non-CLI modules. CLI modules may use `print()` only when their top-level docstring documents the output contract; protocol-producing CLI modules route protocol output through a single named helper. | per-change |

The gate set is closed. Adding or removing a gate is a change to this document and the tooling configuration together. G4 and G5 are repo-specific gates that exist because of the documented bug history in the Purpose section; no off-the-shelf tooling implements them.

### Back-Pressure Protocol

REQ-PROC-051 inherits the back-pressure protocol from REQ-PROC-046 §Back-Pressure Protocol. The five-cycle bound, the gate-as-a-set re-run rule after each revision, the pending-feedback escalation mechanism, and the silent-acceptance prohibition all apply unchanged. The only thing this requirement specifies is the gate surface (G1–G5).

The `quality-checker` agent reads `doc/python/` alongside `doc/architecture/`, `doc/testing/`, `doc/linter/`, etc. Judgment-level rules that are not gateable statically (e.g. "when does a TIER B helper warrant promotion to TIER A?") surface from `doc/python/` the same way Dart judgment-rules surface from the existing Dart-oriented folders.

### Gate Invocation Mechanism

Back-pressure only bites when the gates actually run on a change. AC-15 makes that property an explicit AC: gate invocation is project-level and layered, never relying solely on the agent remembering. The end state is two independent surfaces — a primary path that runs the gate suite as part of the script-modification workflow, and a backstop that fires when the primary path is bypassed. Either layer alone is insufficient; both together close the loop.

The realisation at the time this requirement was written is the `claude-write-script` skill (primary — runs `scripts/quality/check_python_gates.sh` after the script work and before the CLAUDE.md sync step) plus a `PreToolUse` hook on `Edit|Write` for `scripts/**/*.{py,ps1}` in `.claude/settings.json` that injects a reminder to invoke the skill (backstop). A future implementation may promote the hook to a deny, replace the skill with a pre-commit trigger, or wire the gate into the autorun orchestrator — what AC-15 governs is the property "the LLM cannot quietly bypass the gates," not the specific tools that realise it.

### What "Complete" Means

A Python change is complete when, against a clean checkout, all per-change gates (G1–G5) pass and any structurally implied requirement (e.g. a new imported module has a test under AC-10) is satisfied. "Complete" is a property of the tree, not a self-assessment.

## Examples

**Example 1: AC-04 / AC-05 — substitutable side-effect boundary**

The orchestrator routes every subprocess call, every file read and write, every clock read, every sleep, and every process-identity read through a Deps object whose fields are callables. Tests construct the Deps with fakes; the production default is the real stdlib call. Coverage of edge cases (rate-limit responses, permission errors, context-overflow detection) is additive — adding a fake to one call does not leak across other tests. The relevant code is the existing `OrchestratorDeps` dataclass in `scripts/automation/orchestrate.py`, which serves as the reference implementation. The requirement is the property "side effects are substitutable per-boundary and the substitution is local to a test"; the dataclass-of-callables is one way to achieve it.

**Example 2: AC-06 — invariant via context manager**

The orchestrator's "the active session is recorded in state and cleared when the launch returns or raises" invariant lives in a context manager: the `__enter__` records, the `__exit__` clears, no call site forgets the cleanup. Before this construct existed, five launch sites hand-rolled the set / save / launch / clear / save sequence; a launch that raised before the clear left state referencing a dead session — the orphan was the bug. AC-06 makes the pattern the rule: invariants across exception boundaries belong in one construct, not duplicated.

**Example 3: AC-07 — named outcomes**

A function that decides "can this task be promoted to a larger model context?" can return five outcomes: promoted, already at max, no promotable field, the goal file was unreadable, the file did not exist. A `bool` would conflate four of those into `False`. The orchestrator returns an enum whose members name each outcome; callers branch by name and log per outcome. The requirement does not name the enum; it names the property.

**Example 4: AC-08 — no hand-rolled YAML**

Three functions in the orchestrator and ten more across the artifacts, release, and requirements toolchains used to walk lines counting `---` boundaries and parse keys by string splits. The end state under AC-08 is one shared helper module that handles parsing and in-place atomic updates with comment preservation where required, and every other call site uses the standard YAML library for read-only access or that helper for read-modify-write. The path the helper lives at is the impl task's choice; the property — "the pattern exists exactly once" — is the requirement.

**Example 5: AC-09 — print discipline**

The orchestrator emits `[orchestrator <timestamp>] ...` lines that are consumed by external monitoring scripts; those lines are the orchestrator's *public protocol*, not internal debug. AC-09 allows the print, requires the docstring to document the contract, and requires a single helper to be the sole producer of the protocol so the format surface is greppable and replaceable. Internal status — values that are not part of the public protocol — goes through the logging facility, where verbosity is configurable. Other generator scripts that emit machine-readable output to stdout document the format in their docstring and follow the same single-producer rule.

**Example 6: AC-10 — tests follow imports**

A 50-line module that is imported by two other modules needs a test. A 500-line one-shot CLI that no other Python touches does not (TIER C). A long-lived TIER A module needs tests regardless of whether other Python imports it, because its behavior is contract consumed by external systems (the orchestrator's stdout protocol, for instance, is a contract with the Windows sleep helper). The reason for the rule is reuse risk: imported code's behavior is contract, and contracts need verification.

**Example 7: AC-13 — suppression with justification**

```python
# noqa: B008 — framework requires the default-argument call here (FastAPI Depends)
def get_session(deps: Deps = Depends(provide_deps)) -> Session:
    ...
```

A bare `# noqa: B008` without the explanation, or a module-level blanket suppression covering many rules without a per-rule reason, fails AC-13.

## Developer Guidelines

> Constraints and invariants the final Python code must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Tiers are descriptive, not aspirational.** A module is TIER A because of what it does (long-lived stateful, owns invariants, depends on wall-clock advancement), not because the author hopes to write it that way. Promoting a TIER B utility to TIER A is a real cost; it is justified when the module accumulates the responsibilities, not when it merely grows.
- **Substitutable boundaries are for side effects, not for everything.** The pattern wraps syscalls, stdlib I/O, clock reads, sleep. Pure functions do not go through the boundary. The test is "is it a syscall, stdlib I/O, a clock read, or a sleep?" — if yes, substitutable; if no, called directly.
- **Module-level mocking of stdlib symbols is an anti-pattern in TIER A.** It scopes the fake to the entire test process, leaks across tests, and couples tests to the implementation's import structure. The substitutable-boundary pattern scopes the fake to a single call. When the answer to "how do I mock this?" in TIER A is "patch the stdlib," the right move is to add the call to the boundary.
- **Frozen-clock tests must read time through the substitutable boundary, not bypass it.** A frozen-clock test that reaches around the boundary to the stdlib clock will silently start failing on the day wall-clock advances past whatever date the test asserts against; this has happened. The rule is mandatory in TIER A because the recurrence cost is real and known.
- **Hand-rolled YAML is forbidden because the bugs are reproducible.** A standard YAML library handles every edge case that the parallel parsers in the orchestrator have failed at; the only legitimate reason to hand-parse is comment preservation, and that lives in one helper, not at every call site.
- **`print()` and structured logging are not interchangeable.** `print()` is the CLI output protocol; logging is internal debug. Conflating them locks the protocol's format and prevents log-level control. Protocol-producing CLIs use a named helper so the protocol surface stays greppable; everything else uses logging.
- **Tests follow imports, not lines of code.** A short module that is imported five places needs tests. A long one-shot CLI that no other Python touches does not. The reason is reuse risk: imported code's behavior is contract; one-shot code's behavior is its single invocation. TIER A is the exception — its behavior is contract regardless of import status.
- **Named outcomes instead of `bool` when the answer is not yes/no.** A `bool` return is honest only when the question is binary. Three or more outcomes means three or more callers each interpret `False` differently — the type system stops protecting against the conflation. An enum forces the caller to name the outcome explicitly.
- **Suppressions are visible decisions.** Every suppression is read by the next reviewer; the inline justification is part of the code, not a commit-message footnote. Bare suppressions are themselves violations.
- **Gate-set changes require user approval, not LLM autonomy.** An LLM agent may *propose* a new gate or a tightened rule via `task-create`. It must not silently relax the tooling configuration or the acceptance criteria of REQ-PROC-051 during the same task that triggered the proposal. This mirrors the prohibition in REQ-PROC-046 and prevents the LLM from weakening its own constraints under pressure.
- **The relationship to REQ-PROC-046 is sibling, not specialization.** Both requirements share the back-pressure protocol because the protocol is language-agnostic; everything else differs. The two documents cross-reference under Related Requirements and may be updated independently.
- **`doc/` defaults to Dart; non-Dart languages live in dedicated subfolders.** The project is a Flutter app; the shared `doc/` folders are Dart-oriented by intent. Every non-Dart language gets its own dedicated `doc/<lang>/` subfolder. Python-specific guidance does not appear in shared Dart folders, and Dart-specific guidance does not leak into `doc/python/`. The rule keeps per-language guidance compact and findable. AC-14 makes the rule a property of the documentation tree; AC-12 makes Python's adherence verifiable.

### Common Pitfalls

- **Mocking what should be a substitutable boundary.** A TIER A test that reaches for stdlib monkey-patching is a signal that the call was missing from the boundary. Add it to the boundary, default to the real call, take the fake locally.
- **A clock read that "just slipped in."** A utility added "for one log line" that reads the clock directly is fine until it gets called from a code path running under a frozen clock. The cost of routing through the boundary preventatively is low; the cost of finding the leak later is non-trivial — there has been at least one incident.
- **Catching the broadest possible exception "to be safe."** A blanket `except Exception:` swallows whatever bug just happened. In TIER A the cost is direct: a swallowed exception in the orchestrator's main loop becomes a session that silently doesn't launch. Either name the exception class or let it propagate.
- **Parallel mutation of two fields where one would do.** When two fields encode the same conceptual fact, the mutation belongs in one method. Forgetting one of the two was the root cause of a real incident; the rule it enshrines is "if a mutation must touch two fields, it is one method, not a calling convention."
- **Gates passing locally on stale state.** The gate check is "from a clean checkout." Stale cached bytecode, a dev dependency that disagrees with the pinned lockfile, or an editor-installed plugin can mask real failures. The end-state to verify is what a fresh dependency install plus a gate run produces.

## Related Requirements

- **REQ-PROC-046 (Code Quality Standard — Dart)** — sibling. Shares the back-pressure protocol verbatim; that protocol is defined once in REQ-PROC-046 §Back-Pressure Protocol and this requirement inherits it. The two documents cover disjoint code (Dart `lib/`, `test/`, `integration_test/` vs Python `scripts/`).
- **REQ-PROC-052 (Privacy & Security Hygiene)** — sibling. Defines what code is forbidden from doing for privacy and crypto correctness. Its ACs name Dart paths today; the structural commitments (no telemetry SDKs, no off-device network I/O, no hardcoded secrets) apply conceptually to Python tooling too. A Python-side privacy / security requirement is not in scope here; if needed it will be a separate sibling under `coding_standards/`.
- **REQ-PROC-002 (Test Quality Standard)** — addresses Dart tests; the test-quality dimensions (assertion strength, mutation kill rate, property tests, deterministic-run) are language-specific. AC-10 of this requirement is the structural minimum for Python tests; a future Python-side test-quality requirement could extend it.
- **REQ-PROC-001 (Context Window)** — generic AI-workflow requirement; language-neutral. No direct overlap.
- **REQ-PROC-048 (Guideline File Organization)** — governs `doc/` size limits and split mechanics. The new `doc/python/` files are subject to REQ-PROC-048 the same way Dart-side `doc/` folders are.
- **REQ-PROC-043 (Scripts Folder Organization)** — defines the domain-folder structure inside `scripts/`. REQ-PROC-051 governs what is inside those files; REQ-PROC-043 governs where they live.
- **PERSONA-015 longevity commitment** — the source of the "ungoverned Python factory is a sustainability anti-pattern for a solo dev" framing in the Purpose section.
- **PERSONA-004 system-maintenance commitment** — the orchestrator's role as the unattended factory that produces daily work means a Python-side defect has compounding cost; this requirement protects against the recurrence of patterns that have already produced real bugs.

## References

- `scripts/automation/orchestrate.py` and its test suite — the canonical TIER A reference. Reading the orchestrator alongside `doc/python/` (once authored) is the fastest path to internalising the patterns named in AC-04 through AC-09.
- `analysis_options.yaml` and REQ-PROC-046 — the Dart-side analogue this requirement mirrors structurally.
- `doc/README.md` — the documentation index that routes coding agents per language scope (AC-14).
- `CLAUDE.md` — operational checklist that invokes the quality gates per task; the Python gates fold into the same checklist as the Dart gates.
- REQ-PROC-046 §Back-Pressure Protocol — single source of truth for the back-pressure machinery this requirement inherits.
