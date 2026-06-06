---
task_id: TASK-PROC-056-02
type: explore
parent_requirement: REQ-PROC-056
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
started: 2026-05-26
completed: 2026-05-26
session_completed_at: 2026-05-26T16:51:44Z
effort: L
created: 2026-05-21
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Validate and refine the gap analysis around dependency lifecycle (updates, deprecations, replacements) and admission (new dependencies, package-level safety beyond REQ-PROC-056). Decide the correct requirement decomposition, then author each via requ-explore."
release_description: ""
opus_recommended: true   # reason: cross-cutting research, security/privacy domain, explicit trade-off analysis required (split-vs-merge decision over multiple requirements)
writes_requirements: true
requirements_version:
  commit: 416b9055
  file: ../requirements.md
session_id: e6e07dc5-df69-4fa1-8db1-d96a5e27098b
session_account: gmail
---
# Goal: Validate Gap Analysis and Author Dependency Lifecycle + Admission Requirements

## Objective

REQ-PROC-056 covers a single slice of dependency policy: which **version** of an
already-decided dependency may enter the repository, at the moment it enters.
That slice leaves several adjacent policy questions unanswered — when an existing
dependency gets refreshed, how to handle deprecations, when a new dependency may
be added at all, and what package-level (not version-level) safety properties are
required.

This task does **two** things, in order:

1. **Discovery pass** — re-enter the problem space, validate or refute the
   assistant's first-pass four-requirement decomposition (preserved in
   `plans_and_protocols/2026-05-21_00_user_initial_input.md`), surface dimensions
   the first pass missed, and decide whether the natural shape is one
   requirement, two, four, more — and along which seams.
2. **Authoring pass** — for each requirement the discovery pass concluded should
   exist, invoke `requ-explore` to write it. **Never edit `requirements.md` files
   directly** — the `requ-explore` skill is mandatory for adding or modifying
   requirements (per project convention).

The discovery pass must complete and be reviewed by the user *before* the
authoring pass begins. The user's confirmation of the decomposition is the gate
between the two pass types.

## Background

REQ-PROC-056 (Dependency Supply-Chain Safety) was authored 2026-05-21 in the
same conversation that produced this task. Its scope is deliberately narrow:
intake gates (age + advisory) for a version pin landing in a manifest. The
requirement's own text acknowledges what it does not cover — re-evaluation
cadence, the prior question of whether a dependency should exist at all,
deprecation handling, replacement decisions. That acknowledged gap is the
seed for this task.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-21_00_user_initial_input.md`

Read it as a seed bed, not a spec. The assistant's preliminary four-requirement
proposal is included in that file for transparency — treat it as one candidate
shape, not as the answer.

For the parent requirement at task creation time:
```
git show 416b9055:requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/requirements.md
```

Current requirements: ../requirements.md

Sibling requirements worth reading early to understand the existing policy
posture: `../../codegraph_integration/requirements.md`,
`../../roo_code_deprecation/requirements.md`, and the three sibling gate
requirements that REQ-PROC-056 inherits its back-pressure protocol from:
`../../../coding_standards/code_quality/requirements.md`,
`../../../coding_standards/testing/requirements.md`,
`../../../coding_standards/privacy_and_security/requirements.md`.

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge
before converging, let questions lead, iterate. A single pass through the
material will not be enough. Surface surprises — the most valuable discoveries
are the ones that were not anticipated.

The exploration has a **security-design + governance** flavor. Be skeptical of
decompositions that look clean on paper — ask where the seams will actually
cut when an LLM agent meets them in practice. A four-requirement split that
forces an agent to consult three files before adding a single dependency may
fail in a different way than a single mega-requirement that nobody reads.
Conversely, a single requirement that conflates "should this package exist"
with "is this version safe" may hide one failure mode behind the other.

**Critical method note**: the assistant's first-pass decomposition (in the
user-input file) is offered as a starting target. The exploration must be
willing to **reject it** — fully, partially, or by reshaping the seams. A
synthesis that simply confirms the first guess is suspect; if confirmation is
the genuine outcome, the exploration must show *why* the alternatives were
rejected.

## Seeds

The seeds below are entry points, not a workplan. Expect some to lead nowhere
and others to open new threads.

### S1 — Decomposition seams

The first-pass proposal splits dependency policy into four requirements:
update lifecycle, deprecation/replacement, new-dep admission, package-level
safety. Other plausible cuts:

- **One** requirement: "Dependency Lifecycle Policy" with sections for each
  concern. Pro: one file to read; con: hard to evolve sections independently.
- **Two**: admission (does this dep exist? at what version?) vs. lifecycle
  (how does it evolve over time?). Pro: matches the temporal split; con:
  collapses safety dimensions into both halves.
- **Five**: split package-level safety into licensing-compliance and
  capability-conflict-with-privacy-stance. Pro: legal and capability concerns
  are genuinely different; con: more files.
- **By stakeholder**: which slices the LLM owns autonomously, which require
  human pre-authorization, which are forbidden. Cross-cuts all the above.

What does the right cut look like? On what axis are the decisions actually
independent of one another, and on what axis are they entangled?

### S2 — The LLM-autonomy taxonomy

Across all candidate requirements, the recurring question is: *what may the
LLM do without explicit human authorization?* — version bump within
pre-approved package, version bump across major boundary, new dependency,
package replacement, deprecation migration, …

This taxonomy may be its own deliverable — a shared classification table that
each candidate requirement references — or it may be embedded inside each
requirement's ACs. Which serves the LLM agent better at point-of-decision?

The existing REQ-PROC-056 AC-07 already defines an override path (explicit
recorded developer authorization). Does the lifecycle space need the same
mechanism, a different mechanism, or both?

### S3 — Trigger and cadence design space

When does an update *start*? Candidates: time-based (weekly, monthly,
per-release), event-based (advisory disclosed, deprecation warning surfaced,
build failure), opportunistic (next time the file is touched anyway),
manual-only (human says "go").

Each has a failure mode: time-based ignores risk signals, event-based misses
silent rot, opportunistic correlates with unrelated edits, manual-only
underflows when humans are absent. A real policy probably layers several.

What is the right layering for *this* project — where the AI agent runs
autonomous sessions on most days, the human reviews intermittently, and the
app is privacy-sensitive?

### S4 — Regression-confirmation contract for updates

REQ-PROC-046 / REQ-PROC-002 catch breakage on any change. Is that sufficient
for dependency updates, or does an update workflow need *additional*
confirmation — integration tests that exercise the updated package's API,
golden-image smoke tests, manual user verification on a release-candidate
build?

The cost-benefit shifts with the change class: a patch bump of a transitive
dep has different risk than a major bump of `flutter_bloc`. Should the
required confirmation depth scale with the change class?

### S5 — Deprecation handling: signal sources and response

`dart fix --apply` surfaces deprecation warnings. So does
`flutter pub outdated`. So does a maintainer's CHANGELOG entry. So does
"this package has had no release in 14 months" — silent rot is also a
deprecation, in a sense.

How does the policy aggregate these signals? When does a deprecation warrant
immediate work, when does it batch into a migration task, when is it
acceptable to ignore until forced?

### S6 — Replacement-package selection

When `package:foo` is abandoned or no longer fits, what is the rule for
picking `package:bar`?

Candidate signals: download count, maintainer activity, license, transitive
footprint, capability surface (does it pull in `dart:io.HttpClient` and
implicitly threaten SP1?), API stability history (number of major bumps in
the last two years), test coverage, governance model (corporate vs.
individual maintainer).

Are these signals weighted equally? Are some disqualifying (e.g. any
GPL-licensed dep for a closed-source app)? Does the LLM apply them
autonomously or propose-then-confirm?

### S7 — Justification gate for new dependencies

The strongest supply-chain defense is *not* adding the dependency in the
first place. When is it acceptable to add a new top-level dep vs. write
the functionality inline?

Candidate thresholds: LoC saved, domain complexity (e.g. always pull a
crypto library, never write your own — but always write your own date
parser?), security-critical-domain check, transitive footprint impact.

What is the LLM's autonomy here? Can the agent add a new dep on its own
authority if it satisfies REQ-PROC-056 + the new safety gates, or does
every new top-level dep require human pre-authorization?

### S8 — Package-level safety dimensions beyond version

REQ-PROC-056 trusts the package once a safe version exists. Real
supply-chain risk also includes:

- **Maintainer takeover** — a 1-maintainer package whose maintainer recently
  changed is a known attack vector (`event-stream` 2018).
- **License compatibility** — a GPL transitive dep landing in an app
  intended for closed distribution.
- **Capability surface** — a package that *could* call the network even if
  the current code doesn't, undermining SP1's structural guarantee.
- **Abandonment** — no releases, no maintainer responses; an attacker who
  acquires the namespace inherits the package's trust.

Which of these belong in the policy? Which can be checked mechanically and
which require human judgment? Which interact with REQ-PROC-052's existing
SP1–SP6 gates and which are net-new?

### S9 — Industry prior art

What do other privacy-sensitive Flutter apps do? What does Signal's
dependency policy look like? What about Tutanota, Standard Notes, Bitwarden?
What can be learned from `crev` (cargo's web-of-trust), `socket.dev`,
`snyk advisor`, `deps.dev`? Are there published dependency-management
policies for AI-agent-driven projects that have already wrestled with the
LLM-autonomy question?

This seed is the one where web research is most clearly justified.

### S10 — The "we already have it" check

Before authoring anything new, the discovery pass must verify that the
proposed material isn't already covered by an existing requirement. Likely
overlaps to verify:

- `REQ-PROC-052` SP1 / SP2 may already preempt some capability-surface
  concerns.
- `REQ-PROC-046` G1 (analyzer + `dart fix --apply`) already catches some
  deprecations.
- `release_workflow/` requirements may already define a per-release dep
  cadence.
- `dev_environment/` requirements may already define what the agent is
  allowed to install at the OS level.

A finding of "already covered by X" is just as valuable as a finding of
"new requirement needed."

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and
anomalies. Synthesize iteratively; multiple gathering rounds may be needed
before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`,
Sonnet otherwise). No mid-session model switching.

**Two distinct phases — do not blur them**:

1. **Discovery synthesis** — the output is a plan in `plans_and_protocols/`
   that names the recommended requirement decomposition, justifies it
   against rejected alternatives, identifies user-decision points, and
   stops short of authoring requirements. The user reviews and approves
   (or redirects) before phase 2 begins.

2. **Authoring** — for each requirement the approved plan calls out,
   invoke the `requ-explore` skill. Do **not** edit `requirements.md` files
   directly under any circumstance (per project rule:
   `feedback_requ_explore_for_modifications`). `requ-explore` owns
   requirement authoring even when the content seems clear.

If discovery surfaces a finding that the existing REQ-PROC-056 needs to be
**modified** (rather than complemented by siblings), that modification also
goes through `requ-explore` against REQ-PROC-056 — never as a direct edit.

**Web research**: For seeds S6, S7, S8, S9 (and any others that hit external
knowledge), use web search. Always delegate web research to a spawned
`general-purpose` agent with a focused question; never run WebSearch inline.
Raw web content inflates the gathering agent's context window fast with
irrelevant results; the subagent returns only a distilled summary while the
raw content stays in its own context.

Frame search queries as questions rather than keyword bags. Examples:
- *"What dependency-management policies do privacy-sensitive open-source projects (Signal, Tutanota, Standard Notes, Bitwarden) publish in 2025/2026?"*
- *"How do existing AI-coding-agent governance frameworks treat the autonomy boundary for adding a new package dependency?"*
- *"What signals does socket.dev / snyk advisor / deps.dev expose that go beyond version-level CVE checks, and how reliable are they for Dart pub.dev packages specifically?"*
- *"What is the documented history of supply-chain incidents caused specifically by maintainer-account takeover (event-stream, ua-parser-js, others) — what was the warning-signal-to-compromise latency?"*

When a snippet is insufficient, instruct the subagent to use WebFetch to
read the full page before summarising.

## Output

A two-part output, produced in order:

**Part 1 — Discovery synthesis (this task's primary deliverable)**:

A document in `plans_and_protocols/` that:
- Names a **concrete recommended decomposition** of dependency policy into
  N requirements (where N may be 1, 2, 4, 5, …). Each named requirement
  gets a working title, a one-paragraph scope description, and an
  explicit boundary statement vs. its siblings.
- Documents the **rejected alternatives** with the reasoning that ruled
  them out — future readers must understand the design space, not just
  the choice. The assistant's first-pass four-way split must be either
  endorsed (with reasoning) or replaced (with reasoning).
- Identifies the **LLM-autonomy taxonomy** — what the agent may do
  autonomously, what requires recorded evidence, what requires human
  pre-authorization, what is forbidden. This may be a shared table or
  embedded per-requirement; the synthesis says which and why.
- Flags **decisions still requiring user input** — and frames them
  clearly enough that the user can decide in one round.
- Is **honest about what remains uncertain** — gaps in ecosystem
  coverage, attacker capabilities not defended against, signals whose
  reliability is unknown.
- Identifies any **finding that the existing REQ-PROC-056 needs to be
  modified** (vs. extended by siblings).

**Part 2 — Authoring** (occurs only after user approval of Part 1):

For each requirement the approved synthesis calls out, run `requ-explore`
to author it. Each `requ-explore` invocation produces one
`requirements.md` at the right path under `process/AI_rules/ai_tool_management/`
(or wherever the synthesis determines).

The authoring phase is the **second** part of this task — not a follow-up
task — because keeping discovery and authoring in the same workspace
preserves the rationale (`2026-05-21_00_user_initial_input.md` +
synthesis doc) that each authored requirement should reference.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] User approved (or redirected) the recommended requirement decomposition before any authoring began
- [x] Each requirement the approved synthesis called out has been authored via `requ-explore` (never via direct `requirements.md` edit)
- [x] If the synthesis concluded REQ-PROC-056 itself needs modification, that modification was routed through `requ-explore` against REQ-PROC-056

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-056 | active | Parent requirement — sets the existing intake-only boundary that this exploration extends beyond. |
| TASK-PROC-056-01 | pending | Sibling explore task on REQ-PROC-056 enforcement mechanism. Not a hard blocker — runs in parallel — but findings from either task may inform the other's scope. |
