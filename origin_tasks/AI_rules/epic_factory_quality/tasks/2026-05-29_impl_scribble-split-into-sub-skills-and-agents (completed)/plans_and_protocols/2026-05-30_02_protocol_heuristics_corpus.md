# Protocol — UX Heuristics Corpus Authoring

**Agent ID**: a6a78f8c10f49efe9
**Date**: 2026-05-30
**Task**: 2026-05-29_impl_scribble-split-into-sub-skills-and-agents
**Subtask**: Author the UX-heuristics doc corpus that `ui-scribble-heuristics-reviewer`
will consume (amendment A-2 scope: Nielsen 10, Universal Design 7, Saffer, dark patterns,
motion-as-function).

## Files created

All under `doc/presentation/heuristics/`:

1. `README.md` — Corpus index. States purpose (source material for the reviewer agent),
   the explicit overlap-avoidance table (persona/T1-T2/accessibility owners), the file map,
   and the uniform three-part entry shape (Principle / What to check in a scribble / Red
   flag).
2. `nielsen_usability.md` — Nielsen's 10 heuristics (H1–H10), each rewritten as a
   wireframe-answerable check + red flag, with a reviewer quick-checklist.
3. `universal_design.md` — The 7 Principles of Universal Design (UD1–UD7), inclusive-design
   framing at the screen/flow level, with overlap pointers to accessibility and T1/T2.
4. `microinteractions.md` — Saffer's four-part model (Trigger / Rules / Feedback / Loops &
   Modes) as a structural-completeness check for every meaningful interaction.
5. `dark_patterns.md` — Current deceptive-pattern taxonomy (sneaking, fake urgency/scarcity,
   obstruction, preselection, confirmshaming, visual interference/trick wording, nagging,
   disguised ads/fake credibility, comparison prevention) as wireframe checks, plus a
   product-specific emphasis block for the mental-health/sensitive-data context.
6. `motion_as_function.md` — Motion as function (state / causality / hierarchy / continuity,
   M1–M4) plus a "decoration test", scoped to *declared motion intent in annotations* since
   a static scribble has no animation.

Protocol note (this file):
`requirements_tasks/.../plans_and_protocols/2026-05-30_02_protocol_heuristics_corpus.md`.

## Sources used (with URLs)

- Nielsen's 10 usability heuristics — NN/g:
  - https://www.nngroup.com/articles/ten-usability-heuristics/
  - https://www.nngroup.com/articles/visibility-system-status/ (H1)
  - https://www.nngroup.com/articles/consistency-and-standards/ (H4)
- 7 Principles of Universal Design — NC State Center for Universal Design (1997):
  - https://design.ncsu.edu/wp-content/uploads/2022/11/principles-of-universal-design.pdf
  - https://universaldesign.ie/about-universal-design/the-7-principles
- Saffer's microinteractions — Dan Saffer, *Microinteractions* (2013):
  - https://www.oreilly.com/library/view/microinteractions/9781449342760/
  - https://medium.com/@productandrew/microinteractions-dan-saffer-2013-ed12086b1ac9
- Dark / deceptive patterns:
  - https://www.deceptive.design/types (Brignull canonical taxonomy)
  - https://www.deceptive.design/
  - https://www.nngroup.com/articles/deceptive-patterns/
- Motion as function — Material Design 3:
  - https://m3.material.io/styles/motion/overview/how-it-works
  - https://m3.material.io/styles/motion/transitions/applying-transitions
  - https://m3.material.io/styles/motion/easing-and-duration/tokens-specs

All sourced via WebSearch on 2026-05-30 (current taxonomy verified, not training-data
recall).

## Overlap-avoidance decisions

Before writing, read: `doc/presentation/README.md`, `design/README.md`,
`design/t2_destructive_actions.md`, `design/t1_interaction_budget.md`,
`accessibility/README.md`, `accessibility/accessibility_guidelines.md`,
`navigation/README.md`.

Decisions:
- **Persona traits + T1/T2 rules** (touch-target dp values, destructive-action placement,
  interaction tap budgets, crisis-mode targets) are owned by `rule-reviewer` /
  `persona-walker` and `doc/presentation/design/`. The corpus states only the *general*
  principle and points to the owning rule for binding detail. Concrete examples: H3/H5/UD5
  reference `t2_destructive_actions.md` for placement; H7/UD6 reference
  `t1_interaction_budget.md` for the tap budget; UD7 references `t1_touch_targets.md` /
  `t2_crisis_mode_targets.md` for dp values.
- **Accessibility specifics** (WCAG contrast, `Semantics` labels, focus order, reduced
  motion) are owned by `doc/presentation/accessibility/`. UD4 (perceptible info) checks the
  *structural* single-channel problem (meaning by color/icon alone) but defers contrast to
  accessibility; `motion_as_function.md` only *points to* the reduced-motion owner.
- **Navigation patterns** are owned by `doc/presentation/navigation/`; H4 consistency
  cross-references it rather than restating routing rules.
- The README contains an explicit "What this corpus is NOT" overlap table so the reviewer
  agent does not double-report concerns owned elsewhere.

## Judgment calls

- **Scribble scoping**: Every check was written to be answerable from a static low-fidelity
  HTML wireframe (presence/absence of screens, states, exits, annotated labels, structural
  relationships). Live-app-only nuances were deliberately excluded.
- **Motion section**: A static scribble has no animation, so the file was reframed around
  *declared motion intent in annotations* (does the scribble call out the meaning-bearing
  transitions, and is any called-out motion functional?) rather than timing/easing review.
  This is the load-bearing adaptation that keeps the section actionable at wireframe stage.
- **Dark patterns taxonomy**: Used the current deceptive.design / Brignull category names
  (the modern taxonomy) plus the NN/g framing. Added a product-specific emphasis block
  (consent defaults, deletion friction, decline copy, notification nagging) because the
  product handles sensitive mental-health data for vulnerable personas — high-value checks.
- **Universal Design vs. accessibility**: Drew the line at "structural inclusivity" (UD) vs.
  "WCAG conformance" (accessibility) to keep the two non-overlapping.

## Thin sections

None. All five corpus areas had strong, current primary/authoritative sources (NN/g, NC
State CUD, Saffer/O'Reilly, deceptive.design, Material 3). No section was padded or left
under-sourced.

## Constraints honored

- Touched only `doc/presentation/heuristics/**` and this protocol file.
- No `.claude/` skill/agent edits, no code, no `requirements.md` edits.
- No `///` WHY comments in doc content.
- No git commit performed.
