---
id: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: app_provider
created: 2026-05-21
updated: 2026-05-21
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  sections:
    - id: SEC-01
      name: "Lookup Principle"
      heading: "### The Lookup Principle"
    - id: SEC-02
      name: "Preferred Mechanism"
      heading: "### The Preferred Lookup Mechanism"
    - id: SEC-03
      name: "When a Lookup Is Required"
      heading: "### When a Lookup Is Required"
    - id: SEC-04
      name: "Per-Technology Specificity"
      heading: "### Per-Technology Specificity"
    - id: SEC-05
      name: "Scope of Application"
      heading: "### Scope of Application"
  acceptance_criteria:
    - id: AC-01
      text: "The lookup policy applies uniformly to every technology the LLM writes code against in this repository — Dart and Flutter framework, third-party Dart packages, the Python tooling and its libraries, native build files (Android Gradle, iOS Podfile/Xcode), shell and PowerShell, configuration schemas (YAML, JSON, `.arb`), platform CLI tools, and any future-introduced stack. The policy text itself names no specific technology; technology-specific trigger heuristics are permitted to differ but live in `doc/` and in the skill definitions, not in the acceptance criteria of this requirement."
    - id: AC-02
      text: "Default rule: before an LLM agent emits a call into an API surface — a framework class or method, a package symbol, a platform SDK feature, a CLI flag, a configuration key — the agent consults the technology's official documentation at the project's pinned version. The default is skipped only when *external evidence* already establishes the current shape of the call. Recognized external evidence: (a) an existing call site in the project's `lib/`, `test/`, `integration_test/`, `scripts/`, `packages/`, or build-file tree that the agent has read inside the current task, uses the same API in the same way, AND whose containing file the toolchain (analyzer, lint, type-checker, build) currently passes clean at the pinned version with no deprecation, unknown-symbol, or signature-mismatch signal on the call — the *toolchain-clean signal*, not the call site's provenance, is what makes it evidence (a legacy call written before this requirement existed counts iff its surface is still clean against today's pinned-version analyzer); (b) a documentation lookup already performed inside the current task covering the same API at the same pinned version, recorded so downstream agents in the same task chain can see it (this clause is also the deduplication mechanism that prevents the same lookup firing twice when a skill and its spawned agent both reach the same authoring decision); (c) a toolchain run inside the current task (analyzer, build, test, native compile) that exercised the same call and produced no contradicting signal. Self-assessed confidence — the agent feeling sure about a call from its training data — is *not* recognized external evidence and does *not* skip the default. The pinned version is read from `pubspec.lock` for Dart, the Python tooling's pinned constraint for `scripts/`, the platform SDK version named in the build files for native code, and the equivalent canonical source for any other stack."
    - id: AC-03
      text: "`context7` (https://context7.com/docs/overview) is the preferred lookup mechanism. When `context7` indexes the technology being looked up, the agent uses `context7` and does not use raw `WebFetch` or `WebSearch` for the same lookup. When `context7` does not index the technology, the agent falls back to the technology's official documentation site (e.g. `flutter.dev`, `dart.dev`, `pub.dev` package pages, `developer.android.com`, the package's GitHub README at the pinned tag). Raw `WebSearch` is the last-resort channel, used only when neither `context7` nor an identifiable official source covers the question — and the agent records the reason in the task's `plans_and_protocols/`."
    - id: AC-04
      text: "Lookups beyond what AC-02 requires are out of scope. Reading documentation as a session warm-up, pre-loading docs for technologies the current task does not touch, re-reading docs that the same task already covered, or browsing changelogs for libraries whose APIs are not called by the change — these consume context budget without authoring value and are not authorized by this requirement. The framing is symmetric to AC-02: a lookup happens when AC-02 triggers it; a lookup does not happen otherwise. The concrete per-skill and per-technology calibration of *what counts as 'covered by an AC-02 trigger'* lives in the skill definitions and in `doc/`."
    - id: AC-05
      text: "When a lookup yields version-relevant information — a deprecation, a replacement API, a behavioral change across versions — the agent acts against the version pinned by the project (`pubspec.lock` for Dart, the Python tooling's pinned constraint, the platform SDK version named in the build files, the equivalent for any other stack). When the replacement API is *already available at the pinned version* (the old API is deprecated *within* the pinned release), the agent writes the call against the replacement directly; the deprecated API is not re-introduced even as a shim. When the replacement API exists only in a *future version the project has not yet adopted*, the agent emits the call against the pinned version's semantics and records the upgrade path as a `// TODO(<technology> <version>): <one-line description of replacement>` adjacent to the call site so the future bump remains discoverable. A behavioral change that already affects the pinned version is treated as an active correctness signal — the agent updates the call to match the pinned behavior, not to match remembered behavior from an earlier version."
    - id: AC-06
      text: "Test code is subject to the same lookup policy as production code. When test code calls into a testing framework's API surface — `package:test`, `package:flutter_test` matchers and finders, `package:integration_test`, `package:glados` property-test combinators, `package:mutation_test` operators, `pytest` fixtures and parametrization, equivalents in other languages — the AC-04 triggers apply identically. The fact that a call is in `test/` rather than `lib/` is not, by itself, a reason to skip the lookup or to skip the AC-05 version targeting."
    - id: AC-07
      text: "Every code-producing authoring chain in the project — `code-simple`, `code-complex`, `code-test`, `code-bugfix`, the `implementation-engineer` and `test-engineer` agents, and any future skill or agent that produces or modifies code under `lib/`, `test/`, `integration_test/`, `scripts/`, `packages/`, the native build files, or the `.arb` localization files — passes through *exactly one* documentation-lookup checkpoint per authoring decision, placed at the step closest to where the code is written. When a skill spawns a downstream agent for the actual authoring, the checkpoint lives at the agent, not at the orchestrating skill (the skill records the *task-scope lookup log* used by AC-02 evidence (b); the agent consults it before deciding whether the default applies). The checkpoint applies the AC-02 default rule and respects the AC-04 anti-reflex constraint; on a triggered lookup it routes through the AC-03 mechanism chain and appends the result to the task-scope lookup log so later agents in the same chain see it as cached evidence. The exact placement of the checkpoint inside each chain, the format of the task-scope lookup log, and the per-skill heuristics are defined in the skill's own `skill.md` and (where shared) in `doc/`, not in this requirement."
---

# External Documentation Lookup Policy for LLM Coding Agents

## Overview

This requirement defines *when* and *how* an LLM coding agent in this
project consults the official documentation of a used technology. It
exists as the preventive counterpart to REQ-PROC-046 §6, which captures
non-obvious fixes into `doc/` *after the fact*: this requirement intends
to keep many of those non-obvious fixes from being authored in the first
place. The policy is technology-agnostic — it applies to Dart, Python,
native build files, shell, configuration schemas, and any future stack —
while explicitly permitting the *concrete trigger heuristics* to differ
per technology and per code type.

## Purpose

The app provider (PERSONA-015) is a single solo developer maintaining a
mental-health application alongside a full-time job, on the values of
*longevity over velocity* and *the codebase must survive periods where
the creator has no time to touch it*. The system / maintenance
constraints (PERSONA-004) compound this: the app must run reliably on
2017-era Android hardware and must never silently lose mental-health
entries. Every defect that reaches `main` becomes the solo developer's
personal maintenance burden.

In a project where most code is now produced by LLM agents, *the
training data underneath every agent is, by nature, outdated.* Flutter
ships breaking changes every few releases, pub.dev packages deprecate
APIs faster than any model's training window, platform SDKs revise
behavior in minor versions, and Python tooling evolves continuously. An
agent that emits a call confidently — based on an internal pattern
learned six or eighteen months before the current pinned version of the
library — produces code that compiles, sometimes even passes tests, and
quietly carries a deprecation seed or, worse, calls into a renamed API
whose old name still exists as a no-op shim. These defects are
expensive to find later because they look correct on the page, and they
accumulate exactly where the solo developer has the least bandwidth to
audit them: the long tail of small features and tests.

The motivation is therefore not "use the docs in general." It is
specific: every time an agent is about to call an API surface it cannot
demonstrably name the *current* shape of, the agent looks it up — at
the right moment, through an efficient channel, against the project's
pinned version. The user has identified `context7`
(https://context7.com/docs/overview) as the preferred channel: it
serves up-to-date, LLM-indexed documentation efficiently and avoids the
cost and latency of raw web search.

The cost dimension matters as much as the benefit. Reading
documentation as a reflex on every call would inflate context and
slow iteration past the point of usefulness; the published research
that grounds REQ-PROC-046's five-cycle bound (LLMLOOP, ICSME 2025) also
reports that LLMs degrade unrelated context when overloaded with
auxiliary reading. The policy therefore frames lookups as
*conditional* — performed when AC-02 triggers them, not otherwise.
The per-technology and per-skill calibration of the trigger lives in
the skills and in `doc/` so it can evolve as the technology landscape
shifts without rewriting this requirement.

Self-assessed confidence is explicitly *not* the gate that fires a
lookup. An LLM does not reliably know what it does not know — a
renamed API or a behaviorally-changed call that the agent feels
certain about from training data is the most common failure mode this
requirement targets. AC-02 is therefore framed around *external
evidence* (an existing in-repo call site read in the current task, a
prior lookup in the current task, a toolchain run that exercised the
call) and the default is to consult docs unless one of those
external evidences holds.

## When This Requirement Applies

- Any LLM agent producing or modifying code under `lib/`, `test/`,
  `integration_test/`, `scripts/`, `packages/` (forked / patched
  upstream packages maintained in-tree), `android/`, `ios/`, `windows/`,
  or any other code-bearing directory in the repository.
- Any LLM agent producing or modifying configuration that the
  toolchain executes against — `pubspec.yaml`, `analysis_options.yaml`,
  `.arb` localization files, `pyproject.toml` / `requirements.txt`
  equivalents, Gradle / Podfile / Xcode project files, GitHub Actions
  workflow YAML, shell or PowerShell scripts under `scripts/`.
- Any LLM agent producing tests in any of the above locations.
- Both single-file work (via `code-simple`, `code-bugfix`) and
  multi-file work (via `code-complex`, `code-test`).

## When This Requirement Does NOT Apply

- Pure documentation work under `doc/`, `requirements_tasks/`,
  `requirements_user_needs/`, `.claude/` (skill / agent markdown,
  plans, protocols). These artifacts are prose, not code that the
  toolchain executes.
- Mechanical refactors that do not change API call sites — pure
  renames, formatting, comment edits, import reorderings.
- Reading or summarizing the project's own internal `doc/` files. The
  policy targets *upstream* documentation of *used technologies*, not
  the project's own guidelines (which `doc/` already authoritatively
  carries).
- Process-only artifacts produced by exploration / planning agents
  that do not emit code (e.g. an `architecture-advisor` writing a
  plan markdown).

## Behavior

### The Lookup Principle

The default rule is to consult upstream documentation before emitting
a call into an API surface; the default is skipped only when external
evidence inside the current task already establishes the call's shape
at the pinned version. The question the agent answers is not "have I
read the docs for this library?" and not "do I feel confident about
this call?" — it is "what external evidence inside this task confirms
the current shape of this call?" Absence of doubt is not presence of
evidence.

The principle is technology-agnostic. The same lookup discipline
governs a Flutter widget call, a `package:sqlite3` query, a Python
`pathlib` method, a GitHub Actions step, an Android Gradle plugin
configuration, and a `glados` property-test combinator. What differs
between these technologies is *how often* the default lookup actually
fires — Flutter APIs change more often than POSIX shell, third-party
packages more often than first-party SDKs, so the cached
external-evidence skips of AC-02 cover more of the call surface for
some technologies than for others. That per-technology calibration
lives in the skills and in `doc/`, not in this requirement.

### The Preferred Lookup Mechanism

The mechanism chain, in order of preference:

1. **`context7`** — https://context7.com/docs/overview. An LLM-indexed
   documentation service that exposes up-to-date docs through a
   compact, structured interface designed for agent consumption. When
   `context7` indexes the technology being looked up, the agent uses
   `context7` and does *not* parallel-route through raw web search for
   the same question.
2. **Official documentation site** of the technology, when `context7`
   does not cover it. Examples: `flutter.dev` / `api.flutter.dev`,
   `dart.dev` / `api.dart.dev`, `pub.dev` package pages, Python
   `docs.python.org` and the package's PyPI page, `developer.android.com`,
   the package's GitHub README at the pinned tag.
3. **Raw `WebSearch`** — last resort, when neither `context7` nor an
   identifiable official source covers the question. The agent records
   in `plans_and_protocols/` why the fallback was needed (so the
   coverage gap can be tracked for `context7` or for a future official
   source).

The integration mechanism — MCP server, CLI proxy, prompt convention,
or other — lives in the skill definitions and the project's tooling
configuration. This requirement fixes the *channel preference*; it
does not name the wiring.

### When a Lookup Is Required

A lookup is required by default (AC-02), and additionally surfaced
explicitly by these *active signals* — situations where the call is
guaranteed-suspect even if the agent has cached external evidence:

- The toolchain has surfaced a deprecation warning, an "unknown symbol"
  error, or a behavioral mismatch (`flutter analyze`, `dart fix`,
  `mypy`, package-specific lints, native build output, test runner
  diagnostics).
- A quality gate (REQ-PROC-046 / 002 / 052) has failed in a way that
  points to an API-contract mismatch rather than a logic error.
- The agent is about to introduce a new dependency or modify the
  pinned version of an existing dependency in `pubspec.yaml`,
  `requirements.txt` / `pyproject.toml`, or the equivalent for any
  other stack.
- The test approach depends on a framework behavior whose semantics
  vary by version — e.g. how `pumpAndSettle` interacts with a specific
  widget, how `glados` shrinks a custom generator, how `pytest`
  parametrize composes with fixtures.

A lookup is *not* performed:

- For a call whose shape is established by AC-02 external evidence
  (existing in-repo call site read in this task, prior in-task lookup,
  toolchain run inside this task that exercised the call without
  contradicting signal).
- As a reflex outside the AC-02 default and the active-signal list
  above. Reading documentation that does not feed the current
  authoring decision is the AC-04 anti-reflex case — context tax
  without authoring value.

The "required-but-not-too-often" balance is therefore not a hand-wave:
it is the composition of the AC-02 default (consult unless cached) and
the AC-04 anti-reflex (do not consult beyond the trigger). The
operational calibration of *what counts as the same call*, *what
counts as a contradicting signal*, and *how long external evidence
remains valid inside a task* lives in the skill definitions and in
`doc/`.

### Per-Technology Specificity

The *policy* is uniform across technologies. The *concrete heuristics*
that operationalize the policy are explicitly permitted — and
expected — to differ per technology and per code type:

- Flutter framework changes faster than Dart core; the trigger
  threshold for Flutter widget calls is therefore tighter than for
  `dart:core` calls.
- Third-party pub.dev packages with active development require lookups
  more often than long-stable packages at "1.x" with steady releases.
- Python standard-library calls in `scripts/` rarely need lookups; calls
  into third-party Python tooling that the project upgrades aggressively
  do.
- Test-framework APIs need lookups when behavior is subtle
  (async pumping, matcher composition, fixture scoping) but not when
  the call is a vanilla `expect`.

These per-technology calibrations live in the skills' own `skill.md`
files and in `doc/` where they cross-cut multiple skills — never in
this requirement, which deliberately stays at the policy level so it
does not have to be rewritten every time the technology landscape
shifts.

### Scope of Application

Every code-producing skill in the project includes a
documentation-lookup checkpoint at the workflow step where the
authoring decision is made. The set of skills currently in scope —
non-exhaustive, will evolve as new skills are added:

- `code-simple` (single-file work)
- `code-complex` (multi-file architectural changes)
- `code-test` (TDD workflow)
- `code-bugfix` (slim and worktree variants)
- The `implementation-engineer` subagent
- The `test-engineer` subagent
- Any future code-producing skill

AC-07 fixes the *property* that every code-producing skill carries
such a checkpoint. The exact placement of the checkpoint inside each
skill, the per-skill heuristics, and any shared library of trigger
detectors live in the skill files themselves and in `doc/`.

## Examples

**Example 1: Default lookup fires (AC-02, AC-03)**

An agent working under `code-simple` is about to add a `ListView` with
a non-trivial `controller` configuration to a screen. The same
configuration is not present at any in-repo call site the agent has
read in the current task; no prior in-task lookup has covered the
`ListView` controller surface; no toolchain run inside this task has
exercised the call. AC-02's external-evidence skips do not apply, so
the default lookup fires. The agent queries `context7` for the
Flutter `ListView` API at the pinned Flutter version; reads the
current signature; emits the call. Reading `flutter.dev` directly
would also satisfy AC-03 but `context7` is preferred per the
mechanism chain.

**Example 2: External evidence skips the default lookup (AC-02, AC-04)**

The same agent later writes `final items = users.map((u) => u.name).toList();`.
The same call shape exists in many in-repo sites the agent has already
read inside the current task, and the analyzer has produced no
contradicting signal on those calls. AC-02 external evidence (a)
applies — the default lookup is skipped. AC-04's anti-reflex prevents
a "just to be safe" extra lookup. This is what the "not too often"
half of the balance looks like in practice: every call is gated by
the default rule; cached external evidence makes the gate cheap.

**Example 3: Toolchain-surfaced deprecation (AC-02, AC-05)**

A `code-bugfix` run produces a `flutter analyze` deprecation warning:
*"The argument type 'Color' can't be assigned to the parameter type
'MaterialColor' — the API was renamed in Flutter 3.x"*. The agent
queries `context7` for the current API; confirms the rename; updates
the call against the *pinned* Flutter version in `pubspec.lock`; if
the pinned version still supports the old name as a deprecated shim,
the agent updates anyway because the warning is the trigger. The
agent does *not* speculatively chase deprecations that the toolchain
did not surface.

**Example 4: Test code is in scope (AC-06)**

A `code-test` run is writing a `glados` property test for a value
object's round-trip serialization. No in-repo call site has used
`Generator.combine` in a comparable way in the current task; no prior
in-task lookup has covered its semantics at the pinned `glados`
version. AC-02's external-evidence skips do not apply. The agent
queries `context7` (or, if `context7` does not index `glados` yet,
the `pub.dev` page for the pinned `glados` version). The lookup
happens because the default rule applies — being in `test/` rather
than `lib/` does not exempt the call.

**Example 5: Coverage gap routed to last resort (AC-03)**

An agent is wiring a niche internal CLI tool that `context7` does not
index and whose official docs are sparse. The agent uses
`WebSearch` to find the upstream `README` and changelog; reads them;
emits the call; records in
`plans_and_protocols/[YYYY-MM-DD]_NN_lookup_note.md`: *"`context7` does
not index `<tool>` at this version; fell back to `WebSearch`; found
canonical README at `<URL>`."* The gap report is what makes the
fallback path observable so it can be closed later (by
adding the tool to `context7`, or by switching to a different tool).

**Example 6: Future deprecation noted but not acted on (AC-05)**

While looking up a Dart `package:foo` API at the pinned version
`2.4.0`, the agent notices that the API is marked deprecated in the
*unreleased* `3.0.0` version. The pinned version still supports the
API natively. The agent emits the call against `2.4.0` semantics and
adds an adjacent comment: `// TODO(package:foo 3.0): replaced by Y in
3.0 — revisit when bumping major.` No package upgrade is initiated
inside this task; the future deprecation is captured but does not
distort the immediate change.

## Developer Guidelines

> Constraints and invariants the final implementation must satisfy.
> These describe the destination, not the path to it.

### Key Decisions

- **The policy is technology-agnostic; the heuristics are
  technology-specific.** This split is deliberate. The requirement
  text fixes *that* lookups happen and *how* they are routed; it does
  not name a single technology. Per-technology trigger calibration
  lives in the skill files and in `doc/` so the requirement does not
  need a rewrite every time the project adopts a new stack. *Source:
  user message 2026-05-21, AskUserQuestion answers.*
- **`context7` is the named channel, but the integration mechanism is
  not.** AC-03 binds the policy to a *preferred channel*. The
  mechanics — MCP server, CLI proxy, prompt convention — live in the
  skill definitions and the project's tooling configuration. A change
  to the integration mechanism does not require a change to this
  requirement so long as the channel preference holds. *Source: user
  message 2026-05-21 ("preferred mechanism: context7").*
- **The default is "consult"; skips are evidence-driven.** AC-02
  inverts the naive framing where the agent decides whether to look
  up. The framing is: the default is a lookup; *external* evidence
  inside the current task is what skips it. This addresses the known
  failure mode where an LLM does not notice its own uncertainty.
  *Source: user message 2026-05-21 ("LLMs hallucinate and are usually
  quite confident and do not know what they don't know").*
- **Legacy call sites are evidence only when the toolchain agrees.**
  AC-02 evidence (a) is not "the codebase did it this way before, so
  it must be right." A call site authored before this requirement
  existed carries no lookup provenance. What makes it evidence is the
  *current* toolchain: if `flutter analyze` / `dart fix` / the
  language's type-checker passes clean on the file at the pinned
  version with no deprecation or unknown-symbol signal on the call,
  the call is current at the pinned version regardless of how it got
  there. Legacy without a clean toolchain signal is not evidence.
  *Source: user message 2026-05-21 ("we can assume that for that old
  implementation the lookup was already used, right?" — answer: no,
  but toolchain-clean is the substitute).*
- **Exactly one checkpoint per authoring chain.** AC-07 fixes a
  property that prevents the same lookup firing twice when a skill
  spawns a downstream agent. The checkpoint sits at the step closest
  to the code being written (typically the agent, not the
  orchestrating skill); the skill records the *task-scope lookup log*
  that the agent consults via AC-02 evidence (b). Skills that do not
  spawn agents (e.g. `code-simple` doing direct edits) carry the
  checkpoint themselves. The "exactly one" rule is a property of the
  *chain*, not of the skill — duplicating checkpoints up and down a
  chain is the failure mode this guards against. *Source: user
  message 2026-05-21 ("we need to make sure that the lookup is not
  done twice, for example once in the skill, then again in the
  agent").*
- **The "required" balance is the AC-02 / AC-04 composition.** The
  "not too often, but often enough" balance is the composition of two
  rules: AC-02 (consult unless cached external evidence skips) and
  AC-04 (do not consult beyond what AC-02 requires). The numeric /
  mechanical calibrations — what counts as the same call, what counts
  as a contradicting signal, how long external evidence remains
  valid inside a task — live in the skill definitions and in `doc/`.
  *Source: user message 2026-05-21 ("not too often, but often
  enough — whatever that means").*
- **Tests are not a second-class lookup site.** AC-06 lifts a common
  industry anti-pattern out of this codebase: *we look up docs for
  prod code, we wing it for tests.* Tests are first-class deliverables
  of every code-producing skill; the same trigger logic applies.
- **Version-pinning anchors every lookup.** AC-05 prevents a known
  failure mode where the agent reads "latest" docs for a library the
  project has pinned several versions behind, then proposes an API
  that does not exist at the pinned version. The pinned version
  (`pubspec.lock` for Dart, the Python tooling's pinned constraint, the
  platform SDK named in the build files) is the authoritative reading
  frame.
- **The mechanism chain has a fallback path with observable gaps.**
  AC-03 fixes the chain `context7 → official docs → WebSearch` with a
  recording requirement for the last step. The recording is the
  feedback loop that makes the chain itself improvable — a coverage
  gap that never gets recorded never gets closed.
- **The requirement does not name skills by ID; AC-07 does.** AC-07
  enumerates the skill names that currently exist as code-producing
  surfaces. New code-producing skills inherit the AC-07 requirement
  automatically by virtue of being code-producing; they do not need
  an AC-07 amendment. The check is on the property, not on the list.
- **Gate-failure context is itself a lookup trigger.** The interaction
  with REQ-PROC-046 § back-pressure protocol is: when a gate failure
  message points to an API-contract mismatch (a deprecation, a
  renamed symbol, a signature change), the next revision cycle's
  first move is a documentation lookup, not a guess-and-retry. This
  shortens the cycle count toward the five-cycle bound's *floor*
  rather than its ceiling.

### Common Pitfalls

- **Self-assessed confidence as a lookup gatekeeper.** An LLM does not
  reliably know what it does not know. Confidently emitting a renamed
  or restructured API is the precise failure mode this requirement
  targets. AC-02 is therefore framed around *external* evidence (an
  existing in-repo call site read in this task, a prior lookup in this
  task, a toolchain run that exercised the call) and explicitly
  disqualifies self-assessed confidence as a skip path. The absence of
  doubt is not the presence of evidence.
- **Trusting a legacy call site without toolchain confirmation.**
  *"There is already a similar call in the codebase, so it must be
  right"* is the variant of the previous pitfall most likely to bite
  on a long-lived project. Code authored before this requirement
  existed had no lookup discipline; copying its API shape forward
  without checking whether the analyzer still considers it current
  re-introduces deprecation seeds. AC-02 evidence (a) is gated on the
  toolchain-clean signal precisely so this slip is prevented.
- **Checkpoint duplication across the skill → agent boundary.** If
  both the orchestrating skill (e.g. `code-complex`) and the spawned
  agent (e.g. `implementation-engineer`) run a lookup checkpoint on
  the same authoring decision, the same call surface is looked up
  twice — context tax, latency tax, no benefit. AC-07's "exactly one
  checkpoint per authoring chain" closes this. Implementation
  practice: the checkpoint lives at the agent (the level closest to
  the code being written); the skill records the task-scope lookup
  log; the agent reads the log before reaching its own checkpoint and
  treats earlier entries as cached evidence (AC-02 (b)).
- **Reading documentation as a reflex.** Reading the `flutter.dev`
  homepage at the start of every task, or pre-loading docs for
  libraries the task does not touch, inflates context with material
  that does not feed an authoring decision. AC-04 is the bar; absent
  an AC-02 trigger or an active signal, the cost-benefit goes the
  wrong way.
- **Lookups against "latest" instead of the pinned version.** Reading
  `flutter.dev` docs for the current stable channel while the project
  is pinned three minor versions behind produces API suggestions that
  do not exist at the pinned version. AC-05 makes the pinned version
  the reading frame; the agent confirms the version before consuming
  the lookup result.
- **Skipping the channel chain.** Going straight to `WebSearch`
  because it "feels faster" bypasses the indexed, structured
  `context7` and the deterministic official-docs path. The chain is
  ordered for a reason: each lower step is noisier and more
  context-expensive than the one above it.
- **Treating training-data confidence as a free pass.** An agent that
  *feels* confident about an API because it has seen the pattern
  thousands of times in training is the agent most likely to be wrong
  on a renamed or restructured API. AC-02's "demonstrably name the
  current shape" requires evidence, not confidence — and the evidence
  must be anchored to the pinned version.
- **Cargo-cult lookup notes.** Filing a lookup note in
  `plans_and_protocols/` for every API the agent touched, regardless
  of whether a trigger fired, dilutes the gap-tracking signal. Notes
  are required on the fallback to `WebSearch` (AC-03) — that is the
  gap-coverage feedback loop, not a general activity log.
- **Test-framework calls treated as exempt.** AC-06 exists because
  this is the most common slip. Property-test combinators, async
  pumping semantics, and matcher composition change between framework
  versions and produce flaky or wrong tests when the agent guesses.
- **"Documentation update" mistaken for "documentation lookup".**
  REQ-PROC-046 §6 covers *capturing* non-obvious fix patterns into
  `doc/` after the fact. This requirement covers *consulting*
  upstream docs *before* emitting code. The two are distinct loops:
  one feeds the project's internal `doc/`; the other feeds the
  current authoring decision. They are complementary, not
  overlapping.

## Related Requirements

- **REQ-PROC-046 (Code Quality Standard, LLM Back-Pressure Gates)** —
  the preventive / reactive split. REQ-PROC-046 §6 captures
  non-obvious fixes into `doc/` after the gate failure surfaces them.
  This requirement reduces the *upstream* incidence of those failures
  by making upstream documentation a structured input to authoring
  decisions. Both are part of the LLM-facing code-quality contract;
  neither replaces the other.
- **REQ-PROC-002 (Test Quality Standard)** — sibling. AC-06 of this
  requirement extends the policy explicitly into test code; REQ-PROC-002
  governs what makes a test good once written (assertion strength,
  mutation kill rate, property tests, independence). Together they
  cover *what to consult before writing the test* and *what the test
  must satisfy after writing*.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — sibling. Privacy /
  security policies frequently depend on framework-specific behavior
  (`SharedPreferences` vs. `flutter_secure_storage`, `MessageDigest`
  algorithm names, `dart:io` `HttpClient` configuration). A lookup
  trigger on a security-relevant API is the first line of defense
  against subtle privacy regressions; the SP gates in REQ-PROC-052 are
  the verification layer.
- **REQ-PROC-001 (Context Window)** — orthogonal. Context-window
  budgeting governs how much material an agent reads per task;
  AC-04's "not too often" half of the balance is the lookup-side of
  the same concern (do not consume budget on lookups that do not feed
  the current decision). Per-skill calibration of lookup checkpoints
  respects REQ-PROC-001's per-task budget; the calibration itself
  lives in the skill definitions, not in either requirement.
- **REQ-PROC-048 (Guideline File Organization)** — orthogonal. When a
  lookup yields a non-obvious pattern worth preserving for future
  agents, `doc-update-guidelines` (per REQ-PROC-046 §6) writes it
  into `doc/` under REQ-PROC-048's size and split rules. The lookup
  itself is upstream; the captured-pattern destination is internal.

## References

- `context7` overview — https://context7.com/docs/overview
- `pubspec.lock` — authoritative source for Dart / Flutter pinned
  versions consulted under AC-05.
- `analysis_options.yaml` — produces the deprecation signals that
  feed the active-signal list (Behavior § "When a Lookup Is Required")
  for Dart code.
- REQ-PROC-046 — sibling code-quality contract; §6 is the reactive
  counterpart to this requirement's preventive stance.
- Follow-up task TASK-PROC-053-02 (to be created) — owns the
  operationalization: which skills carry the lookup checkpoint, where
  in each skill it fires, what the concrete per-technology trigger
  heuristics are, and how `context7` is integrated mechanically.
- `.claude/skills/code-simple/`, `code-complex/`, `code-test/`,
  `code-bugfix/` — the code-producing skills enumerated in AC-07;
  each carries an AC-07 documentation-lookup checkpoint at the
  authoring step.
