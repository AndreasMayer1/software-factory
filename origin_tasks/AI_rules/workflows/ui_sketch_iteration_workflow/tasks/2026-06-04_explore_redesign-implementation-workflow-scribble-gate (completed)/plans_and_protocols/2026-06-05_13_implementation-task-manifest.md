# Implementation task manifest — the actual tasks to create

Task: TASK-PROC-032-29. Date: 2026-06-05.
Answers the developer ask: *create a document with the actual tasks that need to be created to implement
everything.* This is the work-breakdown for the whole redesign + fixture + migration, organised by the STEP
A→E plan (`10`) and the S1→S4 staging, refined by `11` (resolutions) and `12` (contingencies).

## How to read this

Two kinds of task appear:
- **[SEED]** — created **by hand** now/soon (via `task-create` / `requ-explore` / `claude-create-skill`).
  These are the requirements-authoring tasks, the fixture, the one prerequisite bugfix, and the migration.
- **[DERIVED]** — **not** hand-created; `task-derive-from-requ` will generate these impl tasks *after* the
  relevant requirement lands. Listed here so scope and coverage are visible (and so `14` can verify the
  requirements will cover them). Do **not** pre-create them by hand — that would re-introduce the
  "decompose before the spec exists" defect the redesign exists to remove.

Handles (T-*) are local to this manifest; real `TASK-…` IDs are allocated at creation time. "Creator" = the
skill that creates the task or authors the artifact. Each row traces to its source doc/decision.

**Skill vs agent (ground-truth, round-3 verified).** The scribble machinery is split across `.claude/skills/`
and `.claude/agents/`. Targets that are **agents** (modified via `claude-modify-agent`, created via
`claude-create-agent`): `ui-scribble-generator` (+ its `.contract.yaml`), `ui-scribble-cross-feature-checker`,
`ui-scribble-rule-reviewer`, `ui-scribble-persona-walker`, `ui-scribble-heuristics-reviewer`,
`ui-scribble-feedback-classifier`, `ui-scribble-handoff-emitter`. Targets that are **skills** (via
`claude-modify-skill`): `ui-scribble-iterate`, `ui-scribble-auto-review`, `ui-scribble-feedback-classify`,
`ui-scribble-approve-handoff`, `ui-create-scribble-improve`. Do not conflate `feedback-classify` (skill) with
`feedback-classifier` (agent).

---

## Phase A — Author the redesign requirements  (STEP A; requ-explore; no code)

These are **[SEED]** tasks. They produce the requirement ACs that everything downstream is derived from.
Order: A1 (spine) before A2 (consistency) — A2's SCI edges need A1's two-wave model.

| Handle | Task (requ-explore) | Requirements touched | Must encode (ACs) | Source | After |
|--------|--------------------|----------------------|-------------------|--------|-------|
| **T-A1** | Author the two-wave orchestration spine | REQ-PROC-035, REQ-PROC-058 | two-wave split (presentation wave / code wave); scribble-gate terminal; `release-derive-code` skill spec; rename `release-begin-impl-finalize`→`release-finalize-impl`; **skill-design trade-off-record AC** (B4); **registry routing-contract** extension (C5/file11); bisection as a **hard** requirement (B2) with per-design-unit escape (D-2); **session/token cut map** as ACs (P-D / `10`§6) | `10`§2-3,§6, `11`B1/B2/B4/C5, R1§8.1-4 | — |
| **T-A2** | Author the consistency & scribble-layer model | REQ-PROC-032 | **SCI invariant + audit**; the **5-edge rot-graph** (C1/file11) incl. domain-code→scribble; loopback-as-task (L1–L6); **lazy-wavefront cascade + 2-stage width breaker** (B6); **L3 coverage assertion**; entry-context spine (PROP-8) incl. container **dimension** (R2§2); coverage/ordering (PROP-9/11); **domain→design conditional edge + AC facet-tagging** (B3/C2); staleness/refresh (PROP-12); `ui-verify-flutter` **hard-block on stale** + override (B5) | `10`§1,4,5, `11`B3/B5/B6/C1-C4/C6, R1§1-6 | T-A1 |
| **T-A3** | Author the generator carrier-format & review-layer | REQ-PROC-032 (AC-22/29/27) | replace nested HTML-comment carrier with a flat **JSON `<script>` carrier** (kills the comment-nesting leak); PROP-1 human review layer; PROP-13C findings overlay; PROP-4 per-reviewer persistence; **PROP-3 reviewer-guide reusable component** | R2§1/§7, R1 PROP-1/3/4/13C | T-A1 (parallel to T-A2) |
| **T-A4** | Author the auto-review control model | REQ-PROC-032 (AC-31/32) | sequential reviewer execution (R2§2); gate-on-convergence default (R2§2); selective-skip rule PROP-7; severity-driven stop + circuit-breaker PROP-13B; **PROP-6 trim `question.md` by audience** | R2§2, R1 PROP-6/7/13 | T-A1 (parallel) |
| **T-A5** | Author the flow-viewer requirement (PROP-14) | REQ-PROC-032, REQ-PROC-060 | script-driven MD→HTML flow viewer; **client-side vendored renderer** (B7) → dependency-admission entry | R2§3, `11`B7 | T-A2 (lowest priority) |

> Note: A1–A2 may each be one requ-explore run or split if `doc-lookup-dependencies` budget-caps. A3/A4/A5 can
> run in parallel with A2 since they touch disjoint REQ-PROC-032 sections.

## Phase B — The instrumented fixture  (STEP B)

| Handle | Task | Type / creator | Notes | After |
|--------|------|----------------|-------|-------|
| **T-B0** | **TASK-PROC-066-03 — author playground epic + now-slice features** | explore (ALREADY CREATED) | add the **instrumentation ACs** from `12` (the six measurement probes) so the fixture is measurable by construction | — |
| **T-B1** | Set up the web (React/Angular) toolchain + `doc/` surface + quality gates | [SEED] impl; `task-create-code`-analog for web | new toolchain the factory lacks for web (lint/test/build gates, web architecture guidelines) — the cost flagged in `06`/`10`-Q2; **routes through REQ-PROC-060 dependency-admission** (large dependency addition — developer-authorized) | T-B0 |
| **T-B2** | [DERIVED] Build the now-slice features (dashboard hub + 2–3 dependent feature screens + 1 validation-heavy form) | derived from T-B0 requirements via the **new** workflow | this is the first real exercise of the redesigned chain | T-A2, T-B1 |
| **T-B3** | [DERIVED] Wire the six measurement probes (stall report, cascade log, salvage diff, facet-tag audit, graph-stats dump) | derived from T-B0 instrumentation ACs | makes E1/E2/E5 + leading indicators emit numbers | T-B2 |

## Phase C — Implement the redesigned skills, validated on the fixture  (STEP C)

**T-C0 is [SEED] and FIRST** (it unblocks any scribble task at all). The rest are **[DERIVED]** from the
Phase-A requirements (`task-derive-from-requ` on REQ-PROC-035/058/032 → these impl tasks). Grouped by spine /
consistency / generator to mirror A1/A2/A3.

| Handle | Impl task | Skill/script touched | Creator | Source AC | After |
|--------|-----------|----------------------|---------|-----------|-------|
| **T-C0** | **Fix D-0 routing bug** `scribble → ui-scribble-iterate` | `create_orchestration_task.py` L276 | [SEED] `code-bugfix` (slim) | R1§9 D-0 | — |
| T-C1 | `task-derive-from-requ` `--scope {presentation,code}` mode | `task-derive-from-requ` | claude-modify-skill | T-A1 | T-C0 |
| T-C2 | `release-begin-impl` Ph2c → Wave-1 (presentation + pure-domain only) | `release-begin-impl` | claude-modify-skill | T-A1 | T-C1 |
| T-C3 | New skill `release-derive-code` (Wave 2) + emit quarantine→re-derive **salvage diff** (E3 probe) | new skill | claude-create-skill | T-A1 | T-C1 |
| T-C4 | Rename `release-begin-impl-finalize`→`release-finalize-impl` + add SCI audit | finalize skill | claude-modify-skill | T-A1, T-A2 | T-C3 |
| T-C5 | Scribble-gate terminal in the orchestration chain | `create_orchestration_task.py` | claude-write-script | T-A1 | T-C0 |
| T-C6 | Registry routing-contract extension + encapsulation check (also closes D-0 class) | `.factory/registry/artifacts.yaml` + check script | claude-write-script | T-A1 | T-C0 |
| T-C7 | Skill-design trade-off records for fused skills (e.g. `--scope`) | doc + REQ-PROC-035 anchors | claude-modify-skill | T-A1 | T-C1 |
| T-C8 | SCI: set `stale_since` on requirement edit + auto-create scribble-refresh task + SCI edges + `check_scribble_currency.py` + emit **stall report** (E1 probe) | `requ-explore`/`task-derive-from-requ`, new script | claude-modify-skill + claude-write-script | T-A2 | T-C2 |
| T-C9 | `ui-verify-flutter` hard-block on stale scribble + advisory override | `ui-verify-flutter` | claude-modify-skill | T-A2 (B5) | T-C8 |
| T-C10 | Loopback-as-task (stop inline requ-explore; create blocking tasks L1–L4) | `ui-scribble-feedback-classify` | claude-modify-skill | T-A2 | T-C8 |
| T-C11 | Lazy-wavefront cascade detector + 2-stage width breaker + **PROP-10 mode-independent entry-reference integrity check & bounded recovery** + emit **cascade log** (E2 probe) | `ui-scribble-cross-feature-checker` (**agent**), `ui-scribble-auto-review` (skill) + refresh tasks | **claude-modify-agent** (checker) + claude-modify-skill (auto-review) | T-A2 (B6/PROP-10) | T-C8 |
| T-C12 | Entry-context spine (PROP-8): emit + reviewers check + bounded reconciliation + `flow_positions` fields + container dimension | `ui-scribble-generator` + reviewers (**agents**), `ui-scribble-auto-review` (skill) | **claude-modify-agent** (generator+reviewers) + claude-modify-skill (auto-review) | T-A2 | T-C8 |
| T-C13 | Coverage/ordering (PROP-9/11): flow→scribble coverage report; auto `task_type:scribble` for presentation/both ACs; task-ordering soft-pref; **L3 coverage assertion** + **L3 chain-length alert** (C6); emit **graph-stats dump** (leading-indicator probe) | new report script, `task-derive-from-requ`, ordering rules | claude-write-script + claude-modify-skill | T-A2 | T-C1 |
| T-C14 | Domain→design conditional edge + data-bound detector + AC facet-tagging + emit **facet-tag audit** (E5 probe) | `task-derive-from-requ`, `requ-explore` | claude-modify-skill | T-A2 (B3/C2) | T-C13 |
| T-C15 | Generator carrier-format change (JSON `<script>`) + PROP-1 review layer + findings overlay + PROP-4 persistence + **PROP-3 review-guide component consume** + **PROP-5 small-multiples state variants** | `ui-scribble-generator` (**agent** + its `.contract.yaml`) + overlay script + `_scribble_components/` | **claude-modify-agent** (generator + contract) + claude-write-script (overlay) | T-A3 | T-C0 |
| T-C16 | Auto-review control: sequential exec + gate-on-convergence default + selective-skip + severity stop + **PROP-6 `question.md` trim (Phase-3 gate emitter)** | `ui-scribble-auto-review`, `ui-scribble-iterate` | claude-modify-skill | T-A4 | T-C15 |
| T-C17 | Design-unit map emission + **two-tier entry-seam `foundation_gap` detection** (Tier A `requ-derive-from-flow` / Tier B `requ-verify-flow-coverage --all`) + create the **app-shell / feature-launch-map requirement** (PROP-11 R4 / F12–F14) | `requ-derive-from-flow`, `requ-verify-flow-coverage` | claude-modify-skill | T-A2 (PROP-11 R4 / R1§6.1) | T-C1 |
| T-C18 | PROP-14 flow viewer (script MD→HTML, vendored renderer) | generator helper script | claude-write-script (+ REQ-PROC-060 auth) | T-A5 | T-C15 |

## Phase C′ — Fixture validation gate  (end of STEP C)

| Handle | Task | Type | Notes | After |
|--------|------|------|-------|-------|
| **T-CV** | Run the redesigned workflow end-to-end on the fixture; capture the six probes; review against `12`§0.6 pre-registered thresholds; choose Plan A vs branches | [SEED] verify/explore | the decision gate for E1/E2/E5 + compound-failure pivot | T-B3, T-C1…C18 |

## Phase D — Migrate release 0.0.1  (STEP D; task-set reconcile per `11`A1)

| Handle | Task | Type | Notes | After |
|--------|------|------|-------|-------|
| **T-D1** | 0.0.1 task-set reconcile: run flow→scribble coverage over 0.0.1 Presentation reqs; SCI-block the ~6–8 un-started pre-scribble UI tasks (`TASK-FUNC-007-12-01..04` + adaptive-settings); one verdict for `TASK-FUNC-014-06-01`; leave completed + pure-domain untouched | [SEED] impl | NOT delete-all; NOT a plan reclassify (no plan exists) | T-CV |
| **T-D2** | Reset + re-run the pilot `TASK-FUNC-007-01-05` through the new workflow | [SEED] (per `01_clean-rerun-decision`) | clean-rerun already decided | T-CV |
| **T-D3** | E3/E4 branch review (salvage rate + fixture-fidelity surprises) against `12`§0.6 | [SEED] review | may trigger E4-B2/B3 | T-D1 |

## Phase E — Factory extraction  (STEP E; DEFERRED)

| Handle | Task | Status | Notes |
|--------|------|--------|-------|
| **T-E1** | `TASK-PROC-066-01` software-factory-extraction | exists, pending | proceeds *after* the workflow is stable; consumes the factory/project boundary labels accumulated in Phase C + the web fixture (tech-agnosticism). Not created here. |

---

## Critical path & parallelism

```
T-C0 (bugfix, now) ─┐
                    ├─► T-A1 ─► T-C1 ─► T-C2 ─► T-C3 ─► T-C4 ─┐
T-B0 (exists) ─► T-B1 ─────────────────────────────────────── │
                    └─► T-A2 ─► (T-C8…C14) ───────────────────┤
                    └─► T-A3 ─► T-C15 ─► T-C16                 ├─► T-B2 ─► T-B3 ─► T-CV ─► T-D1 ─► T-D2 ─► (T-E1)
                    └─► T-A4 ──────────────┘                  │
                    └─► T-A5 ─► T-C18 ────────────────────────┘
```
- **Now (parallel):** T-C0 (bugfix) and T-B0 (already running) and T-B1 (web toolchain).
- **STEP A (parallel):** T-A1 first; T-A2/A3/A4/A5 fan out after A1.
- **STEP C:** derived from A; spine (C1–C7) gates consistency (C8–C14); generator (C15–C16) parallel.
- **Gate:** T-CV is the single chokepoint before any 0.0.1 work.

## Counts
- **[SEED] to create by hand:** T-A1..A5 (5 requ-explore), T-B1 (1), T-C0 (1 bugfix), T-CV, T-D1, T-D2, T-D3
  (4) = **12 hand-created tasks** (+ T-B0 already created).
- **[DERIVED] (generated by task-derive-from-requ after A lands):** T-C1..C18 minus the seed/script-only
  ones ≈ **15–18 impl tasks**, plus T-B2/B3.
- **Deferred:** T-E1 (exists).

## Immediate next action (STEP A entry)
Create **T-C0** (bugfix, unblocks everything) and **T-A1** (the spine requ-explore) first. Everything else
fans out from those two. T-B1 (web toolchain) can start in parallel.
