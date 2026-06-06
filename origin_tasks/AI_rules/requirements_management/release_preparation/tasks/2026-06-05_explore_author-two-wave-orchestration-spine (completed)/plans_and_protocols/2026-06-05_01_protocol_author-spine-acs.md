---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - requ-explore
  - task-complete
  - claude-commit
---

# Protocol — Author the Two-Wave Orchestration Spine (T-A1)

Task: TASK-PROC-035-21. Date: 2026-06-05.
Agent ID: acf53a7319de15642

This task encoded the settled scribble-gate-redesign spine (TASK-PROC-032-29) as requirement ACs/sections into
REQ-PROC-035 (orchestration spine) and REQ-PROC-058 (plan format). Design was settled; this was disciplined,
additive AC authoring, not exploration. No existing content was restructured.

## Substrate read

- goal.md `## Objective` (the 7-item spec)
- `2026-06-04_02_round_1_synthesis.md` §0 (decomposition-time defect), §2 (two-wave topology, gate scope D-2),
  §8 (change-list / split)
- `2026-06-05_10_synthesis_next-steps-plan.md` (verdicts; T5 trade-off-record; staging)
- `2026-06-05_11_synthesis_resolve-open-questions.md` B1 (D-0 bug), B2 (bisection hard), B4 (fused-only
  trade-off trigger), C2 (facet tags / wave separability), C5 (registry routing-contract)
- `2026-06-05_13_implementation-task-manifest.md` row T-A1 (AC scope) + T-C1..C7 (derived impl tasks the ACs
  must be sufficient for)

## REQ-PROC-035 — new sections (sections-based file)

All registered under `trackable_items.sections` with `target_package: "Transfer Data Model"` (copied from
siblings). `updated:` bumped to 2026-06-05.

- **SEC-08 Two-Wave Decomposition** — Wave 1 (`release-begin-impl`) holds only scribble + basis entries for
  Presentation units and full coding entries for pure-domain units; no Presentation coding entry exists at end
  of Wave 1; Wave 2 (`release-derive-code`) coding entries exist only after scribble approval. Defines
  "design-unit" and "pure-domain unit" (no Presentation-layer artifact in output set) checkably. States the
  bisection as a hard requirement. Carries an inline trade-off record for the per-design-unit boundary.
  Encodes: R1§0/§2.4, B2, D-2.
- **SEC-09 Scribble-Gate Terminal** — the scribble-gate terminal and the `_VALIDATION` terminal compose as a
  sequence; scribble-gate precedes/gates Wave-2 code derivation; `_VALIDATION` remains release-readiness and is
  reached only after the Wave-2 coding chain completes. Notes `task_type: scribble` resolves to
  `ui-scribble-iterate` (folds D-0/B1). Encodes: R1§2.2.
- **SEC-10 release-derive-code Skill** — Wave-2 orchestrator end-state responsibility: per approved-scribble
  Presentation requirement, run `task-derive-from-requ --scope code` reading the approved scribble +
  `flutter_handoff.yaml`; inject SCI coding edge; spawn coding chain. Encodes: R1§2.2.
- **SEC-11 release-finalize-impl Skill** — end-state name is `release-finalize-impl` (rename expressed as
  resulting state, no transition word); runs the finalize phases and gains the SCI audit in its Phase-1
  coverage audit (asserts each coding task's covered scribble is approved and not stale). Encodes: R1§2.2/§4.2.
- **SEC-12 Session and Token Allocation** — orchestrator vs spawned-agent vs new-task end-state allocation;
  orchestrator never reads requirements.md wholesale; per-requirement decomposition in both waves is spawned
  background agents; scribble→code hand-off via `flutter_handoff.yaml` is the read-once point. Encodes: R1§6 /
  `10`§6.

## REQ-PROC-058 — new ACs + sections (explicit-AC file)

`updated: 2026-06-05` added to frontmatter (field did not previously exist).

ACs (registered under `trackable_items.acceptance_criteria`, appended to `## Acceptance Criteria` body):
- **AC-18** — `task-derive-from-requ --scope {presentation,code}` mode; every plan entry carries `wave:` +
  `scope:` tags; pure-domain requirement = single presentation-scope run, all entries `wave: code`, no scribble
  entry. Encodes: C2 (facet/wave separability), goal bullet 6.
- **AC-19** — fused-responsibility skills (>1 artifact-in→artifact-out pair OR a mode flag) carry a trade-off
  record; single-responsibility skills carry only the one-sentence responsibility. Encodes: B4 / T5.
- **AC-20** — every plan-entry `task_type` resolves to a registered consumer skill in
  `.factory/registry/artifacts.yaml`; an unresolvable `task_type` is detectable/rejected (closes D-0 class).
  Encodes: C5 / B1.

Sections (registered under `trackable_items.sections`):
- **SEC-05 Skill-Design Trade-off Record** — normative body for AC-19; includes the `--scope` skill's own
  trade-off record (fused moded skill vs split presentation/code decomposers).
- **SEC-06 Registry Routing Contract** — normative body for AC-20; one registry governs both routing resolution
  and the AC-19 trade-off trigger.

Unified Plan Format extended with `wave:` and `scope:` plan-entry fields + a "Wave-tagged entries" paragraph
(additive to SEC-04 body; SEC-04 already registered).

## Trade-off notes encoded (per requ-explore rule on recommendation resolutions)

- Per-design-unit gate boundary (D-2): chosen for cross-unit parallelism, traded away release-global
  simplicity + needs the design-unit map. (REQ-PROC-035 SEC-08, inline.)
- Fused `--scope` skill (B4): chosen for shared decomposition machinery + single coverage-matrix authority,
  traded away the simpler single-responsibility boundary. (REQ-PROC-058 SEC-05.)

## Self-check (requ-explore §2.3/§2.5)

- End-state language: all ACs/sections describe the finished system. The rename is stated as "the Wave-2
  finalize skill is named `release-finalize-impl`" (resulting state), not "rename X to Y".
- Transition words (replace/update/migrate/add/convert/remove/change/refactor/rename) checked — none used in
  normative AC statements.
- Abstraction: factory-level; skill names, artifact field names, section headings, registry path permitted;
  no internal skill step-logic described.
- No forbidden sections added (no Testing Requirements / Open Questions / Version History / Roadmap).

## Uncertain / judgment calls

- REQ-PROC-058 had no `updated:` field; I added one (2026-06-05) rather than skip the bump.
- The `wave`/`scope` plan-entry tag names are my naming from goal bullet 6's "`wave:` / `scope:` tag" wording;
  the substrate did not fix exact field names. C2's facet tag (`presentation|behaviour|both`) is an AC-level
  concept that belongs to T-A2 (REQ-PROC-032), so I encoded only the entry-level `wave`/`scope` tags here, not
  the AC facet tag — keeping the REQ-PROC-058 scope to the plan format per the goal split.
- The scribble-gate terminal wording deliberately keeps `_VALIDATION` as the release-readiness terminal and
  the scribble-gate terminal as per-design-unit, matching R1§2.2; the substrate did not spell out the exact
  template string for the new terminal, so I left it at the behavioural end-state (gate reached → run
  `release-derive-code`).
