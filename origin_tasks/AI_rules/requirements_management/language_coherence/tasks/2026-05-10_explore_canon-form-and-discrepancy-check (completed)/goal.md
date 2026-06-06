---
task_id: TASK-PROC-049-01
type: explore
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
effort: M
created: 2026-05-10
started: 2026-05-14
completed: 2026-05-15
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05]
  sections: []
scope_description: "Design canon form, schema, discrepancy check, bootstrap strategy for REQ-PROC-049"
release_description: ""
opus_recommended: true   # reason: explore task with explicit trade-off analysis across multiple options; cross-cutting (artifacts, code, translation pipeline)
writes_requirements: false
requirements_version:
  commit: f4672821
  file: ../../requirements.md
---

# Goal: Design canon form and discrepancy check for REQ-PROC-049

## Objective

Design the implementation form for REQ-PROC-049's canonical concept canon and the discrepancy check that satisfies AC-05. The requirement deliberately specified only *what good looks like*, not *how* it is achieved. This exploration produces the option space, evaluates trade-offs, and recommends a concrete shape — without yet committing to implementation.

What we do NOT yet know:

- Whether the canon should live as a single hand-authored markdown file, a generated artifact aggregated from per-feature fragments, structured YAML/JSON consumed by tooling, code annotations harvested into a derived view, or some hybrid.
- What the canon's schema must capture per concept to support the four reference points (requirement bodies, UI labels, `translation_context`, user-facing `lib/` identifiers) without becoming a maintenance sink.
- How the discrepancy check produces a deterministic pass/fail signal across four heterogeneous artifact types — pure-text artifacts, structured YAML entries, and Dart source files.
- How to bootstrap the canon from the current repository without a costly retrofit.
- What the concrete shape of REQ-NFUNC-013 AC-08 `translation_context` entries is *before* and *after* the canon exists, and how much duplication actually disappears.

## Background

REQ-PROC-049 is an active living-document requirement created in this session. It states what coherence means and how it must be detectable; it does not prescribe the canonical source's form. PERSONA-015's grounded values (longevity over velocity, simplicity as survival strategy for solo-developer maintenance) are the dominant constraint on whatever form is chosen — a canon that requires manual per-feature sync is worse than no canon.

REQ-NFUNC-013 AC-08 is the primary downstream consumer: every UI text entry must store a `translation_context` description covering user situation, UI element type, and wording rationale. Without a shared canon, every entry redescribes the same nouns, verbs, and states across hundreds of labels — duplicated effort, inconsistent results.

The Layers of Product Design framework's `/layers-conceptual-model` skill (Sophia Prater OOUX, Daniel Rosenberg semantic IxD) is the conceptual origin. It is *one possible inspiration*, not the prescribed implementation.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-10_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show f4672821:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize with PERSONA-015's longevity/simplicity bind before defining, diverge across canon-form options before converging, let the AC-08 integration question lead the schema design. A single pass through `lib/`, the requirements tree, and the existing translation infrastructure will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What does an AC-08 `translation_context` entry look like before and after a canon exists?** Pick one feature area (e.g. `epic_data_transfer/feat_therapist_transfer_ui/`), draft three to five `translation_context` entries by hand without a canon, then redraft them assuming a canon. Where does the duplication concentrate? Is the duplication concept-level (noun/verb/state descriptions) or label-level (which surface, which audience)? Quantify the reduction.

2. **What is already implicitly in `lib/`?** Walk the user-facing identifiers in `lib/features/*/domain/` and `lib/features/*/presentation/`. How much of a canon could be derived from them automatically? Which concepts surface in the UI but are *not* named in code? Which code names diverge from UI labels?

3. **The verb-precision question.** For each generic verb currently in user-facing language (Edit, Delete, Update, Add, Create, Remove, Save, Submit), enumerate its actual operations in the current product. Where does AC-03's decomposition test fail today? Are there cases where the divergence is invisible until a translator asks?

4. **Maintenance cost vs. duplication cost.** What is the minimum ongoing cost of maintaining a canon that satisfies AC-01–AC-04? Compare to the duplication cost of *not* having one (estimated AC-08 entries × per-entry redundant prose). At what canon size does the cost balance flip?

5. **The discrepancy check across heterogeneous artifacts.** A check that scans markdown requirement bodies, YAML translation entries, and Dart user-facing identifiers needs a unified concept of "reference to a canonical name." What does that abstraction look like? Is it a single tool, three coordinated tools, or a composite linter?

6. **REQ-PROC-046 alignment.** REQ-PROC-046 establishes a binary pass/fail back-pressure pattern for code quality. AC-05 names a similar pass/fail signal. Should the discrepancy check be a literal G6 gate alongside G1–G5, a separate process gate, or both? What does the LLM agent see when the check fails?

7. **What the layers-skills framework gets right and wrong here.** `/layers-conceptual-model` produces an object map + state diagrams + ubiquitous language as Mermaid + markdown. That format is designer-facing. What changes when the consumer is also LLM tooling and Dart code? Where does the framework's prescription stop being useful?

8. **The existing UX infrastructure question.** `ux-create-flow`, `ux-write-persona`, `ux-write-scenario` exist but have not been used in practice. Does the canon's authoring leverage that infrastructure, sit adjacent to it, or replace some of it? Be honest about whether adding another UX-shaped artifact is a net win.

## Execution Model

Gather raw material — read `lib/` user-facing identifiers, walk current `epic_data_transfer` requirements and existing UI label entries, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: Where seeds 6 and 7 require external knowledge — published examples of vocabulary/glossary/canon implementations in OSS projects, prior art on linting cross-artifact terminology consistency, what others have tried with LLM-consumed concept canons — delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Frame queries as questions rather than keyword bags.

## Output

A future implementer reading this task's protocol should be able to start an `impl` task without having to redo the design work. Specifically, they should be able to:

- Pick a canon location and form with the trade-offs already laid out and a recommendation justified against PERSONA-015's grounded values.
- Pick a discrepancy-check architecture with the four artifact types covered and a pass/fail integration story for REQ-PROC-046's back-pressure pattern.
- Bootstrap the canon for one feature area without redesigning the schema first.
- Update REQ-NFUNC-013 AC-08 entries to the post-canon form using a worked example.

The output is honest about what remains uncertain — open product decisions are framed for the user to decide, not papered over.

## Acceptance Criteria

- [x] Exploration produced at least one Opus synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation (in particular: the maintenance-cost vs. duplication-cost balance, and the cross-artifact discrepancy-check architecture)
- [x] At least two viable options compared for each major decision (canon location, schema, discrepancy check, bootstrap), with the recommendation justified against PERSONA-015 grounded values (longevity, simplicity, single-developer maintenance)
- [x] A concrete worked example showing one feature's `translation_context` entries before and after the canon exists, with the duplication reduction estimated
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] Sized for follow-up implementation: an `impl` task can be derived from the plan without further design work

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-049 existence | done | Created in this session |
| REQ-NFUNC-013 AC-08 link | done | Added in this session (§8.4 + §11) |
| REQ-PROC-050 sibling | done | Independent dimension; not a blocker |

## Notes

- This is a process-side requirement (REQ-PROC). `target_package` is omitted (process tasks have no release package per task-create skill rules).
- No flow/scenario reference — process improvement, no end-user flow.
- `opus_recommended: true` because the task is explicitly an option-space comparison with cross-cutting scope (artifacts, code, translation pipeline).
- Investigation has NOT begun — task workspace only.
