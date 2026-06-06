---
task_id: TASK-PROC-053-01
type: explore
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-21
effort: S
created: 2026-05-21
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author REQ-PROC-053 — the technology-agnostic policy requiring LLM coding agents to consult official documentation of used technologies at the right time, using context7 as the preferred mechanism."
release_description: ""
opus_recommended: false
writes_requirements: true
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Define LLM Documentation-Lookup Policy for Used Technologies

## Objective

What rule should govern *when* and *how* an LLM coding agent in this project
consults the official documentation of a technology it is writing code
against? The exploration produces one written requirement
(`../../requirements.md`, ID `REQ-PROC-053`) that establishes the policy
without prescribing the per-technology heuristics or the skill-wiring — both
of which are deliberately deferred to a follow-up task.

The exploration must surface and resolve, in the requirement text, three
balances:

- **Coverage vs. cost** — read documentation when it would materially help,
  not so often that context and tokens are wasted.
- **Universality vs. specificity** — the policy itself is
  technology-agnostic, but the trigger heuristics it enables must be free to
  differ per technology and per code type (Dart, Python, shell, native build
  files, …).
- **Policy vs. mechanism** — the policy names `context7`
  (https://context7.com/docs/overview) as the preferred lookup channel, but
  does not yet wire it into any skill.

## Background

The project has no rule today telling the coding agent when — or how — to
consult an upstream technology's documentation. The closest adjacent rule is
REQ-PROC-046 §6, which captures *non-obvious fixes after the fact* into
`doc/` — useful, but reactive. It does nothing to prevent the LLM from
emitting a deprecated API call or filling a training-data gap with a
plausible-but-wrong pattern in the first place.

The user's diagnosis is direct: LLM training data is, by nature, outdated;
the documentation of every framework, package, and platform API the project
uses is the authoritative source for what is current. Quality, error
prevention, and maintainability all benefit when the agent reads that source
at the right moment.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-21_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements: `../../requirements.md` (does not yet exist — this
task creates it).

## How to Approach This

Use design thinking as the guiding process — empathize with the LLM
authoring code under time/context pressure before defining; diverge on
"what triggers a lookup?" before converging on the policy statement; let
the open questions lead. A single pass through the sibling requirements
(REQ-PROC-046 / 052 / context_window / python_code_quality / testing) will
not be enough — read them not to copy, but to understand the *shape* of a
living LLM-facing rule.

Surface surprises. The most valuable discoveries are the trade-offs the
user did not anticipate — e.g. lookup cost during long iterative cycles,
freshness mismatch between context7 and the version pinned in
`pubspec.lock`, what happens for technologies context7 does NOT index, what
"required" means when the LLM is *confident but wrong*.

## Seeds

1. **What signals tell the agent "you should look this up"?** Confidence
   gradient, deprecation warnings from `flutter analyze`, unfamiliar API
   surface, novel framework version, test-shape uncertainty — which of
   these are universal, which are technology-specific?

2. **What signals tell the agent "you are looking it up too often"?**
   Context cost, latency, repeat lookups within the same task — is there a
   simple budget (e.g. per-task, per-file, per-API-surface) that captures
   the "not too often" balance the user asked for?

3. **Coverage of context7.** What is its actual indexing footprint? Which
   used technologies in this repo are covered (Flutter, Dart, Riverpod-ish
   libs, pub.dev packages, `sqlite3`, `glados`, `mutation_test`, …) and
   which are not? When it does not cover a technology, what is the
   fallback — and is that fallback in scope for this requirement or for
   the follow-up?

4. **Version pinning.** `pubspec.lock` pins exact versions. Should the
   policy require the lookup to target the *pinned* version, the *latest*
   version, or both for delta? What does the user expect when a lookup
   returns "this API is deprecated in version > pinned"?

5. **Tests as a distinct lookup site.** The user explicitly noted that
   test code also needs lookups — but the triggers differ (framework
   testing APIs, matcher behavior, async patterns, golden-file tooling).
   Should the policy carve out a test-specific paragraph, or stay uniform?

6. **The "open" agent-scope question.** The user said: *"I need an
   exploration and brainstorming to answer [which agents must comply]."*
   That brainstorming is NOT part of this task — but the requirement must
   acknowledge the question and leave it cleanly open for the follow-up.
   What is the right wording so the follow-up has a well-defined starting
   point?

7. **Relation to REQ-PROC-046 §6.** REQ-PROC-046 captures non-obvious
   fixes after the fact. This requirement is its *preventive* counterpart.
   Make the relationship explicit — and check it does not create a
   redundant or contradictory rule.

8. **"Read when required" — the hardest seed.** The user smiled at this
   themselves: *"not too often … often enough … whatever that means,
   right?"* The requirement must capture the principle as a constraint on
   the finished system without resolving the operational definition. The
   operational definition is the follow-up task's deliverable.

## Execution Model

Gather raw material — read sibling requirements (REQ-PROC-046, 052,
context_window, python_code_quality, testing), skim CLAUDE.md §7, look up
`context7.com/docs/overview` for indexing and access model. Synthesize
iteratively; the goal text above lists three balances that must be
resolved *inside* the requirement — that is the convergence criterion.

The session's model is fixed at launch (`opus_recommended: false` —
Sonnet, single-file requirement writing with strong sibling patterns).

**Web research**: For seeds 3, 4, and 7, use the web (`context7.com`
overview, Flutter deprecation policy, Dart pub semver conventions). Always
delegate to a spawned `general-purpose` agent with a focused question;
never run `WebSearch` / `WebFetch` inline. Frame queries as questions
("how does context7 expose version-pinned docs?", not "context7 versions
docs").

## Output

A single `requirements.md` at
`requirements_tasks/process/AI_rules/coding_standards/external_documentation_lookup/requirements.md`
that a future agent — or the follow-up task's author — can read once and
understand:

- Why the requirement exists (training-data freshness gap; preventive
  counterpart to REQ-PROC-046 §6).
- What the policy is (technology-agnostic, applies to all code the LLM
  writes against in this repo, balances coverage with cost).
- Which lookup mechanism is named (`context7`) and why it is preferred
  over raw web search.
- Which questions are deliberately deferred — and to which task.
- How the requirement plugs into the existing process-requirement
  ecosystem (relation to REQ-PROC-046, 052, context_window).

The requirement carries `status: active` (living rule, like REQ-PROC-046).

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round before writing
      requirements.md.
- [x] The written requirement defines the documentation-lookup problem
      space in terms that were not fully spelled out at task creation —
      especially the "required vs. excessive" balance (AC-02 default +
      AC-04 anti-reflex composition) and the per-technology specificity
      carve-out (Behavior §"Per-Technology Specificity").
- [x] Decisions requiring user input were resolved inline (scope,
      language coverage, agent-scope deferral via AC-07 end-state,
      version-pinning semantics including direct-switch-at-pinned-version,
      `packages/` inclusion, self-confidence-vs-external-evidence trigger
      framing).
- [x] The output is honest about what remains uncertain — per-skill
      trigger calibration deferred to skills + `doc/`; `context7`
      integration mechanism deferred; dependency-update mechanism flagged
      as a separate user-owned requirement that will be created later.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| —          | —      | No blocking dependencies. The follow-up task that wires lookup into skills depends on THIS task, not the other way around. |

## Notes

- Sibling pattern: REQ-PROC-046 (`code_quality`) and REQ-PROC-052
  (`privacy_and_security`) are both `status: active` living rules with
  trackable ACs and were authored as preventive LLM-facing policies. They
  are the structural model.
- The follow-up implementation task — *"wire documentation-lookup
  heuristics into existing coding skills, integrate context7"* — will be
  created by the user immediately after this requirement is approved.
- This is a `process/` task — `target_package` is intentionally absent.
