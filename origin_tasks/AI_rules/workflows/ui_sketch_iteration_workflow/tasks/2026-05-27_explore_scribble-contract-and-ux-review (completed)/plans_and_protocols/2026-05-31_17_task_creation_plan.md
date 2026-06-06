---
requirement: REQ-PROC-032
requirements_version: b58e7cca
created: 2026-05-31
mode: full
---

# Task Creation Plan for REQ-PROC-032 (AC-21–AC-36)

Derived from the TASK-PROC-032-10 exploration (iterations 1–6 + consolidation file 16).
All tasks are process/skill/doc edits — no `lib/` code, no `target_package` (process requirement).
Edits to existing skills go through `claude-modify-skill`; the one new skill through
`claude-create-skill`; agent edits through `claude-modify-agent`.

Producers already exist (shipped by the REQ-PROC-044 program): `ui-scribble-iterate`,
`ui-scribble-auto-review`, `ui-scribble-feedback-classify`, `ui-scribble-approve-handoff`
(skills); `ui-scribble-generator`, `ui-scribble-rule-reviewer`, `ui-scribble-heuristics-reviewer`,
`ui-scribble-persona-walker`, `ui-scribble-feedback-classifier`, `ui-scribble-handoff-emitter`
(agents). Tasks EDIT these — they do not recreate them.

## Tasks

- task_name: "scribble-contract-doctrine-and-producer-surfacing"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-21, AC-22, AC-23, AC-26, AC-27]
  effort: L
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    Author the single-source contract doctrine and wire the producers to emit it.
    - SKETCHES_README.md: add "What a Scribble Commits To" section with the two disjoint
      sets LOCKED-IN (L1–L15) and RE-DERIVE (D1–D8) per REQ-PROC-032 SEC-15. This is the
      ONLY place the enumerated lists live (no restatement elsewhere). [AC-21]
    - ui-scribble-generator agent (claude-modify-agent): emit a CONTRACT BLOCK at the top of
      index.html + a compact per-screen variant, dual reviewer/coder framing, verbatim from
      the SKETCHES_README contract. [AC-22] Change persona-derived sizing from literal
      `min-height:48px` to a NAMED TOKEN reference (e.g. var(--min-tap-target)); the literal
      resolves from the token registry. Add accessibility-INTENT to generated output (semantic
      element, ARIA role identity, alt-text obligation, accessible-name); keep a11y
      IMPLEMENTATION deferred. [AC-26] Emit a machine-readable rule-application audit trace
      (which T1/T2 rule applied to which element). [AC-27]
    - ui-scribble-handoff-emitter agent (claude-modify-agent): add a top-level `contract:`
      block (locked_in / re_derive item keys + source pointer to SKETCHES_README) to
      flutter_handoff.yaml. Update .claude/schemas/flutter_handoff.yaml to validate it. [AC-23]
    Verification: open a generated scribble, confirm CONTRACT BLOCK present with both framings;
    confirm flutter_handoff.yaml validates against the updated schema with the contract block.

- task_name: "scribble-contract-consumers-sketchgate-and-verifier"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-24, AC-25]
  effort: M
  layer: process
  after: ["scribble-contract-doctrine-and-producer-surfacing"]
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    Make the downstream consumers honor the contract that task 1 establishes.
    - code-simple + code-complex (claude-modify-skill): rewrite the Sketch Gate step so the
      implementer reads flutter_handoff.yaml's `contract:` block, implements locked-in items as
      shown, and re-derives the re_derive items from doc/presentation/ + tokens.json regardless
      of whether the scribble depicts them. [AC-24]
    - ui-verify-flutter (claude-modify-skill): anchor the finding taxonomy to the contract —
      a locked-in divergence is a coder defect; a re-derive item is classified out_of_contract
      (not opined on against the scribble). Every finding states which side of the contract it
      is on. [AC-25]
    Depends on task 1 because the contract doctrine + handoff `contract:` block must exist first.

- task_name: "scribble-review-doctrine-reconcile-and-cycle-aids"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-28, AC-29, AC-30, AC-31]
  effort: L
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    - doc/presentation/heuristics/: remove the PROVISIONAL marker; reconcile the Nielsen /
      Universal Design / microinteraction / dark-pattern / motion-as-function checks with the
      Q1 design (TASK-PROC-032-10 iterations 1–4) and confirm no double-ownership with
      persona-walker or rule-reviewer. ui-scribble-heuristics-reviewer then applies it as
      canonical (drop the "PROVISIONAL" caveat in the agent). [AC-28]
    - ui-scribble-auto-review (claude-modify-skill): after even-version regeneration, produce an
      auto-review brief (what to focus on) + an inter-version structural diff; the diff is
      viewable via a toggle in the scribble HTML that highlights changed elements; the brief
      links to the diff. [AC-29]
    - persona-conflict surfacing: when persona-walker/heuristics review finds a screen-level
      two-persona conflict, mark the conflict point and link a DDR — or route upstream via the
      revision channel when resolution implies a flow/VCD change. [AC-30]
    - ui-scribble-iterate (claude-modify-skill): add an iteration-fatigue rail (past a version
      threshold without convergence → recommend pausing to run requ-explore on the underlying
      requirement). [AC-31]

- task_name: "scribble-multi-breakpoint-from-persona-device-classes"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-32]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    Personas declare the device classes they predominantly use (add to persona schema/docs;
    check README_* for an existing field before adding a new one). A requirement's required
    breakpoint set = union across served personas. ui-scribble-generator + ui-scribble-iterate
    (claude-modify-*): generate per required breakpoint; a screen whose layout is genuinely
    identical across breakpoints is generated once and marked shared, never duplicated. [AC-32]

- task_name: "scribble-structured-inspiration-inputs"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-33]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    Define inputs/inspiration.yaml convention: per-reference use/ignore matrix (use layout:true,
    use colors:false, …), optional screen scope, free-text note. ui-scribble-generator Phase 0
    (claude-modify-agent): pattern the scribble after used aspects, ignore the rest in favor of
    project conventions, annotate each affected screen with its inspiration source. Document the
    convention in SKETCHES_README. [AC-33]

- task_name: "scribble-reviewer-pre-brief-phase-0_5"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-34]
  effort: S
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    ui-scribble-iterate (claude-modify-skill): add a Phase 0.5 pre-brief before first generation
    (≤300 words: screens to be generated, personas+rules applied, out-of-scope, information-model
    boundary, open assumptions). Developer approves / adjusts (regenerate, bounded before
    escalation) / rejects-scope (route to requ-explore). Retain the approved pre-brief as a
    version artifact. Document the ≤300-word content spec + iteration model in SKETCHES_README. [AC-34]

- task_name: "scribble-cross-feature-consistency-check"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-35]
  effort: S
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: |
    Add a cross-feature consistency check (cheap model / script) invoked from ui-scribble-auto-review:
    when a scribble's feature shares a user flow with sibling features that have their own
    scribbles, flag divergent component choices for the same role across siblings (e.g. FilledButton
    vs TextButton for primary confirmation) for human resolution. When it runs inside a per-flow
    walk, integrate with the walk; when standalone, run the fan-out. [AC-35]

- task_name: "ui-visual-validate-skill"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-36]
  effort: L
  layer: process
  after: ["scribble-contract-doctrine-and-producer-surfacing"]
  task_type: impl
  opus_recommended: true
  implementation_notes: |
    New skill ui-visual-validate via claude-create-skill (and claude-create-agent for its vision
    agent if one is warranted — evaluate via the agent-creation rubric). Compares integration-test
    screenshots of implemented Flutter screens against the approved scribble + re-derive sources
    (tokens, accessibility, persona sizing). Advisory (non-blocking) findings report. Uses a
    vision-capable model (Opus). Reads per-locked-item `verification_seeds:` emitted in
    flutter_handoff.yaml — add that emission to ui-scribble-handoff-emitter as part of this task
    (the R3-collapse: verification_seeds live INSIDE flutter_handoff, not a separate file). Scope
    is distinct from ui-verify-flutter (code-only structural) and ui-improve-flutter (human polish).
    after task 1 for flutter_handoff schema coherence. [AC-36]

- task_name: "verify-req-proc-032-scribble-content-acs"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "b58e7cca"
  covers_acs: [AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-28, AC-29, AC-30, AC-31, AC-32, AC-33, AC-34, AC-35, AC-36]
  effort: M
  layer: process
  after: ["scribble-contract-doctrine-and-producer-surfacing", "scribble-contract-consumers-sketchgate-and-verifier", "scribble-review-doctrine-reconcile-and-cycle-aids", "scribble-multi-breakpoint-from-persona-device-classes", "scribble-structured-inspiration-inputs", "scribble-reviewer-pre-brief-phase-0_5", "scribble-cross-feature-consistency-check", "ui-visual-validate-skill"]
  task_type: verify
  opus_recommended: true
  implementation_notes: |
    Audit each of AC-21..AC-36 against the shipped edits (audit-only; file fix tasks for gaps).
    Process-requirement verification: run/read the producers and confirm each AC's end-state holds —
    CONTRACT BLOCK present, flutter_handoff contract+verification_seeds blocks validate, Sketch-Gate
    and verifier anchored, heuristics corpus de-provisionalized, breakpoint/inspiration/pre-brief/
    cross-feature/visual-validate behaviors present. Do not assume implementers were correct.

## Coverage Matrix

| AC | Task(s) |
|----|---------|
| AC-21 | scribble-contract-doctrine-and-producer-surfacing |
| AC-22 | scribble-contract-doctrine-and-producer-surfacing |
| AC-23 | scribble-contract-doctrine-and-producer-surfacing |
| AC-24 | scribble-contract-consumers-sketchgate-and-verifier |
| AC-25 | scribble-contract-consumers-sketchgate-and-verifier |
| AC-26 | scribble-contract-doctrine-and-producer-surfacing |
| AC-27 | scribble-contract-doctrine-and-producer-surfacing |
| AC-28 | scribble-review-doctrine-reconcile-and-cycle-aids |
| AC-29 | scribble-review-doctrine-reconcile-and-cycle-aids |
| AC-30 | scribble-review-doctrine-reconcile-and-cycle-aids |
| AC-31 | scribble-review-doctrine-reconcile-and-cycle-aids |
| AC-32 | scribble-multi-breakpoint-from-persona-device-classes |
| AC-33 | scribble-structured-inspiration-inputs |
| AC-34 | scribble-reviewer-pre-brief-phase-0_5 |
| AC-35 | scribble-cross-feature-consistency-check |
| AC-36 | ui-visual-validate-skill |

All 16 ACs covered. 8 impl tasks + 1 verification task. No circular dependencies.
