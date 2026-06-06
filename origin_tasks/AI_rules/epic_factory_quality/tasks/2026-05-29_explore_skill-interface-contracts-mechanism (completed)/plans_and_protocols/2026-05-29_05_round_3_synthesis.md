# Round 3 Synthesis — Resolving the 6 OPEN Decisions

**Task:** TASK-PROC-044-02 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Reads:** kickoff (`01`), web research (`02`), Round 1 (`03`), Round 2 prototype summary (`04`)

> Round 3 resolves the 6 OPEN decisions from kickoff §4, codifies the migration sequence, maps the mechanism to REQ-PROC-044's ACs, and documents what the mechanism deliberately does NOT promise. Each decision is framed clearly enough for the user to confirm or revise in Phase 3.

---

## D-1 — Sub-skill split for the scribble pipeline

**Question (goal.md §"Decisions to Resolve" #1):** Confirm or revise file 09 §7.1's 4-sub-skill cut, applying the sub-skill-vs-agent rubric.

### Decision

**Adopt the revised 3-sub-skill + 1-agent shape** from Round 1 §3.3:

```
ui-scribble-iterate (thin orchestrator, owns the iteration loop + version tracking)
├── agent: scribble-generator             (was: ui-scribble-generate sub-skill; rubric score 1/4)
├── sub-skill: ui-scribble-auto-review    (rubric score 3/4 — fan-out + review point)
│       ├── agent: scribble-auto-reviewer
│       ├── agent: scribble-ux-protocol-reviewer
│       └── agent: persona-embodiment-reviewer
├── sub-skill: ui-scribble-feedback-classify  (rubric score 3/4)
│       ├── agent: scribble-feedback-classifier
│       └── may invoke: requ-explore, doc-update-guidelines, ux-validate-rule
└── sub-skill: ui-scribble-approve-handoff   (rubric score 2/4, lean split because handoff IS the contract)
        └── agent: scribble-handoff-emitter
```

### Why this differs from file 09 §7.1

`ui-scribble-generate` failed the rubric (1/4). It spawns a single agent with no fan-out, no natural human review point at its boundary, and no orchestration value beyond wait-for-agent. Per Hermify's "don't rebuild CrewAI inside an agent" warning (file 02 §Q3), it should be an agent invoked by the parent, not a sub-skill. Scenario C in Round 1 §2 illustrates the maintenance trap a fake-split creates.

The other three (auto-review, feedback-classify, approve-handoff) earned their split via the rubric.

### Action

The SCRIBBLE-SPLIT rollout task (file 09 §11 bundle) implements this shape. The decision is final at this level of granularity; the executor of SCRIBBLE-SPLIT may discover deeper refinements that don't conflict.

---

## D-2 — Contract mechanism

**Question (goal.md §"Decisions to Resolve" #2):** Pick one of: sidecar `contract.yaml` / inline frontmatter / registry / hybrid. Justify against token budget + developer's transparency goal.

### Decision

**Adopt sidecar `contract.yaml` per skill, with a project-wide `.claude/schemas/` for shared artifact shapes — and a 5-line bash pre-condition check at the top of every consumer skill.** This is a *three-component* mechanism, not just a sidecar.

#### Component 1 — Sidecar `contract.yaml`

Location: `.claude/skills/<skill-name>/contract.yaml`

Field set (PRINCE2-aligned 4-field minimum, file 02 §Q4, **amended by Round 2 prototype findings** §"Discoveries 1, 4"):

```yaml
contract_version: 1
purpose: "One-line description (may reference SKILL.md description)"
derived_from:
  required:
    - path_or_field: "<path glob or frontmatter field>"
      source: external | skill:<producer-name>   # MANDATORY (added per Round 2)
      schema: ".claude/schemas/<artifact>.yaml"   # optional reference
      reason: "Why this skill needs it"
  optional:
    - path_or_field: "..."
      source: external | skill:<producer-name>   # MANDATORY
      schema: "..."
      condition: "human-readable when this is read"
produces:
  required:
    - path_or_field: "..."
      schema: "..."
  conditional:
    - path_or_field: "..."
      condition: "when this is emitted"
quality_criteria:
  - "verifiable acceptance bullet (PRINCE2-style measurable criterion)"
may_invoke:
  - <skill-name>
  - <skill-name>
side_effects:
  - target: "<shared-state path>"
    action: write | append | delete | regenerate   # enum added per Round 2
    note: "human-readable description of the mutation"
preconditions:
  - "human-readable condition asserted by pre_check at skill entry"
postconditions:
  - "human-readable condition that quality_criteria collectively verify"
```

##### Why `source:` is mandatory (Round 2 finding)

Without distinguishing `external` (developer-owned inputs like `requirements.md`, `id_registry.md`, image seeds) from `skill:<producer-name>` (declared cross-skill dependency), the lint produces ~10 false-positive violations even on just 3 contracts. The annotation is two values + an undeclared default:
- **`source: external`** — input is provided by the developer / filesystem / user, not by another skill
- **`source: skill:<name>`** — input is the output of a named producer skill; the lint cross-references that skill's `produces:` block
- **Undeclared** — lint treats as `skill:` and tries to match against producers; emits an error if no match

##### `skill:` annotation verification

Round 2 PoC's lint **skips** `source: skill:<name>` items rather than verifying the named skill actually declares the path. Round 3 decision: **add named-producer verification in Wave 1** of the rollout (FU-1). The PoC simplification was a time-box; production lint must verify, otherwise `skill:` becomes a trust-based bypass identical to `external`.

#### Component 2 — Project schemas at `.claude/schemas/<artifact>.yaml`

Centralize shapes of artifacts shared across ≥2 skills. Initial set (Round 2 prototyped the first two):
- `scribble_metadata.yaml`
- `goal_metadata.yaml`
- `flutter_handoff.yaml`
- `concept_canon_entry.yaml`
- `requirements_frontmatter.yaml`

Schema dialect: flat YAML with `required:`, `optional:`, `enums:` blocks (file 02 §Q6 — adopt the discipline, reject OpenAI-strict-mode rigidity). **NOT full JSON Schema** (Round 2 finding §"Discoveries 7"): the YAML dialect is human-readable, lower authoring cost, and serves as documentation + lint-augmented check, not a runtime validator. The Wave 2 runtime pre-check (component 3 below) implements `validate_against_schema.py` against this dialect, not against JSON Schema tooling.

#### Component 3 — Runtime pre-check at consumer skill entry

A 5-line bash assertion at the top of every consumer skill's invocation logic:

```bash
# Example: at the top of code-simple's body
[ -f "${SCRIBBLE_PATH}/metadata.yaml" ] || { echo "ERR: missing scribble metadata at ${SCRIBBLE_PATH}/metadata.yaml — required input per contract.yaml"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${SCRIBBLE_PATH}/metadata.yaml" .claude/schemas/scribble_metadata.yaml || exit 2
```

PwC's 7× number (file 02 §Q7) argues this verification leg carries the largest measurable win.

### Why not the alternatives

| Alternative | Why rejected |
|---|---|
| **Inline frontmatter in SKILL.md** | Anthropic's 500-line ceiling + 1024-char description limit makes a rich contract impossible inline. Inline contract steals tokens at every skill invocation (file 02 §Q5). |
| **Central registry at `.claude/contracts.yaml`** | Single point of contention for `claude-modify-skill` edits; harder to scope per-skill ownership. Round-1 §1.3 audience analysis: contract.yaml's audience is the lint + the author of that one skill — co-location wins. |
| **Hybrid (mix of all three)** | Defeats the transparency goal — readers don't know where to look. One mechanism, three components, each with one location. |

##### Folder-level path matching (Round 2 finding §"Discoveries 2")

The lint's folder-level matching (e.g. consumer claims `scribbles/v{n}/`, producer declares `scribbles/v{n}/index.html`) is necessary but introduces template ambiguity. Round 2 PoC uses freeform `{n}`, `<feature>`, `<task>` placeholders that work for human reading but are opaque to automated tooling. Round 3 specifies: **freeform stays for v1**; if Wave 2 finds the ambiguity creates real-world bugs, FU-2 adds a canonical glob syntax (e.g. brace expansion or shell-style `**`). Treat as a known v1 risk.

### Why this combination satisfies the developer's transparency goal

- **One file per skill** for skill-level contract → `claude-modify-skill` updates exactly one sidecar
- **One file per shared artifact** for schemas → schema changes have a single home + ripple via the lint
- **5-line pre-checks** are inline and grep-able → no hidden runtime magic

### Action

Prototype validated (Round 2). Rollout sequence in D-5 codifies the migration.

---

## D-3 — Bidirectional feedback channel structure

**Question (goal.md §"Decisions to Resolve" #3):** Unified-channel (revision_requests as subfolder of pending_feedback) or separate channels with orchestrator update?

### Decision

**Unified channel under `automation/pending_feedback/{TASK_ID}/` with a typed responder discriminator.** No second channel; no orchestrator-scan change.

#### Structure

```
automation/
  pending_feedback/
    {TASK_ID}/
      question.md           ← existing; developer-facing questions
      answer.md             ← existing; developer reply
      revision_target.yaml  ← NEW; structured skill→skill revision requests
  cycle_state.json          ← existing; 5-cycle counter from CLAUDE.md §7
```

`revision_target.yaml` schema (Round 2 prototype: `prototypes/example_revision_target.yaml`):

```yaml
originator: <skill name producing the request>
target_skill: <skill name owning the upstream artifact>
target_phase: <phase ID in the target skill, optional>
artifact: <path to the upstream artifact needing revision>
reason: structural | rule_conflict | infeasible | flow_flaw | drift | other
responder_required: human | skill | either
detail: |
  <prose explanation>
suggested_action: <one-line proposal>
blocks_completion_of: <task ID(s)>
cycle_count: <integer; 5-cycle escalation per CLAUDE.md §7>
```

#### Why one channel, not two

Microsoft Magentic (file 02 §Q2) is the canonical evidence: `MagenticPlanReviewRequest` is one typed channel handling both agent→agent and agent→human, distinguished by `responder_required` (Magentic uses `is_stalled` + responder enum). The documented failure mode of two-channel designs is exactly the developer's concern in file 14: the orchestrator scans only one, the other goes silent.

#### Why this doesn't conflict with the `factory/` improvement channel

`.factory/optimize/events/*.json` serves a different lifecycle: **event-driven, retrospective, non-blocking**. It feeds `claude-optimize` which produces auto-blocked improvement tasks. The `pending_feedback/` channel is **session-driven, current-blocking**. Different cadence, different consumer, different urgency. They legitimately stay separate; nesting them would conflate two distinct decision rhythms.

#### Action

`pending_feedback/README.md` (currently exists per `automation/pending_feedback/README.md` from §kickoff inventory) gets a new sub-section documenting the `revision_target.yaml` schema + the `responder_required:` discriminator. Orchestrator scan logic is **unchanged** — it already finds the right folders. This is a NEW rollout task: "Pending-feedback structure for skill→skill revision requests" (see Phase 4 follow-up tasks).

---

## D-4 — `revision_request` vs creating a task taxonomy

**Question (goal.md §"Decisions to Resolve" #4):** Final rule for when each applies.

### Decision

Codify file 12 §4.5's taxonomy, sharpened by file 14's "tasks ARE the backlog" principle:

| Work to do | Channel | Why |
|---|---|---|
| Standalone work needed (e.g. regenerate scribble v(n+1) reflecting coder feedback) | **`task-create`** | Real artifact change requires a task; orchestrator picks up via normal ordering; the task is the only durable backlog. |
| Decision/review needed before any work (e.g. "is this drift intentional or correct?") | **`revision_target.yaml`** | Lightweight; doesn't pollute the task list with non-actionable items. May resolve to a task OR to "no action needed." |
| Developer question with no autonomous resolution path | **`question.md` in pending_feedback** | Existing channel; orchestrator pauses, developer answers, session resumes. |

The receiving end (the upstream skill, or its owning agent) decides which path applies when it processes the request. The rule:
- If the request implies work that takes ≥ 1 commit-cycle to do → create a task
- If the request is a decision/yes-or-no/review → `revision_target.yaml`
- If the request is something only the developer can answer → `question.md`

#### Escalation

The same 5-cycle protocol as `verify-quality` (CLAUDE.md §7) applies:
- A `revision_target.yaml` that bounces ≥ 5 times (originator and target keep disagreeing) automatically converts to a `question.md` for the developer
- The `cycle_count:` field on `revision_target.yaml` tracks this

### Why no exceptions

The temptation is to create a fourth "lightweight" channel for "informational FYI" items. Resist. Per file 14: tasks ARE the backlog. Any "FYI" that doesn't fit one of the three categories above either becomes a task (if actionable) or is silently dropped (if not). Don't expand the channel surface.

### Action

Document the taxonomy in `pending_feedback/README.md`. The same rollout task that adds the `revision_target.yaml` schema in D-3 carries this documentation.

---

## D-5 — Migration sequence

**Question (goal.md §"Decisions to Resolve" #5):** Which skill family adopts first; what `contract_version: 0` opt-out looks like; how stale duplicates are removed.

### Decision

#### Adoption sequence (3 waves, family-ordered)

**Wave 1 — Producers of widely-shared artifacts** (highest leverage):
- `task-create` (produces `goal.md` — consumed by ~10 skills)
- `requ-explore` (produces `requirements.md` — consumed by ~15 skills)
- `ui-create-scribble` (produces `scribbles/v{n}/*` — consumed by 4+ skills)
- `ux-write-canon-concept` (produces/maintains `concept_canon.yaml` — consumed by ~6 skills)

**Wave 2 — Heavy consumers** (paired with their producer migrations):
- `code-simple`, `code-complex`, `code-bugfix`, `code-test`
- `ui-verify-flutter`, `ui-improve-flutter`
- `task-derive-from-requ`, `task-create-code`, `task-complete`

**Wave 3 — Rest** (claude-*, doc-*, release-* families; mostly already lower interface-dependency):
- All remaining skills

Why families, not single skills: file 02 §Q3 LangGraph evidence — splitting consumer from producer (or producer from co-consumer) creates the FM-1.4 (loss of conversation history) failure mode during the migration window. Migrating in family-grouped waves ensures producer + main consumers commit together.

#### `contract_version: 0` opt-out

A skill with `contract_version: 0` (or no contract.yaml at all) is **unmanaged** by the lint:
- Lint emits a one-line WARNING per Wave-1 commit ("skill X has no contract.yaml; will be migrated in Wave Y")
- Lint emits an ERROR if a `contract_version: 1` skill references an unmanaged skill in `may_invoke:` (because the cross-skill check can't run)

**Sunset target**: `contract_version: 0` is removed from the lint's allowlist 60 days after Wave 3 begins. Before that date, all skills must declare `contract_version: 1` or the build fails. The 60-day window absorbs solo-developer cadence variance.

#### Stale duplicate cleanup (file 14 §4.4 obligation)

For every `.claude/schemas/<artifact>.yaml` added:
1. Identify the prose specification(s) it replaces (typically a section of a folder-root README or SKETCHES_README)
2. Diff: anything in the schema that's not in the prose, or vice versa, is a reconciliation item
3. After reconciliation: **delete** the prose specification. Replace with a one-line reference: `> See `.claude/schemas/<artifact>.yaml` for the canonical structure.`
4. Commit the deletion in the same commit as the schema introduction (atomic move)

**No dual maintenance phase.** The schema becomes the single source of truth at the moment it lands. Skills updated to validate against the schema are part of the same wave's commit set.

#### Order within a wave

For each wave: (1) author the schemas for the artifacts that wave touches; (2) author contract.yaml for each skill in parallel; (3) add the 5-line pre-checks; (4) delete duplicated prose; (5) run lint; (6) commit.

### Action

Each wave becomes a follow-up task (see Phase 4). Wave 1 is the first one to seed.

---

## D-6 — Does REQ-PROC-044 need new ACs?

**Question (goal.md §"Decisions to Resolve" #6):** Propose additions via `requ-explore` (separate follow-up) if yes.

### Per-AC mapping (the mechanism vs REQ-PROC-044 ACs)

| AC | What it asserts | How the proposed mechanism satisfies it | Gap? |
|---|---|---|---|
| **AC-01** | Every skill has a documented, reachable output; no silent failure | `contract.yaml.produces:` declares all outputs; lint catches drift; pre-checks catch malformed inputs that would cause silent producer failure | None |
| **AC-02** | Artifact pipeline traceable end-to-end | `derived_from:` + `produces:` form a producer-consumer graph the lint can render; `may_invoke:` makes skill-to-skill traceable | None — the lint becomes the trace tool |
| **AC-03** | New task type/artifact/skill added without modifying unrelated skills | `contract_version: 0` opt-out + schemas referenced by name (not by inline content) means a new skill is added by writing 1 contract.yaml + 0 edits to unrelated skills | None |
| **AC-04** | Malformed/missing inputs cause visible warning or graceful stop | 5-line pre-checks at consumer skill entry; lint catches declared drift; runtime `validate_against_schema.py` reports specific actionable errors (file 02 §Q5 anti-punting rule) | None |
| **AC-05** | LLM non-determinism isolated; deterministic steps reproducible | The lint, schemas, and pre-checks are 100% deterministic. The `contract.yaml` itself is human-authored (a frozen artifact), not LLM-generated at runtime | None |
| **AC-06** | Active skills + artifact dependencies + ordering rules documented in single authoritative location | After migration: `.claude/skills/<name>/contract.yaml` is the per-skill authoritative location; the lint can produce a global graph view from contract.yaml's; `.claude/factory_flows.md` continues to serve the human-readable overview | **Partial** — see below |

### Gap and recommendation for AC-06

AC-06 requires a **single authoritative location**. Today, ordering rules live in `.claude/task_ordering_rules.yaml`; skill capabilities live across 60 `SKILL.md`s; artifact dependencies (post-migration) live across 60 `contract.yaml`s + ~10 schemas. The single-location property is satisfied **per dimension**, not globally.

This isn't a defect of the proposed mechanism — it's a property of how the factory naturally decomposes. The honest statement is: AC-06 is satisfied if "single authoritative location" means "single per dimension, discoverable by greppable index." It is NOT satisfied if it means "one literal file containing everything."

**Recommendation**: do not modify REQ-PROC-044's AC text from this task. Instead, the rollout task that lands the lint should also produce a new "factory map" script (`scripts/factory/render_factory_map.py`) that reads all contract.yaml + schemas + factory_flows.md and emits a single readable artifact (Markdown or HTML). That artifact becomes the AC-06 single-location interpretation. If that interpretation is rejected by the user, then a follow-up `requ-explore` can refine AC-06.

### Decision

**No new ACs needed on REQ-PROC-044.** The 6 existing ACs are satisfiable by the proposed mechanism + the factory-map render script (a small rollout artifact). If user rejects the interpretation of AC-06, a single follow-up `requ-explore` on REQ-PROC-044 addresses it; no broader scope change.

---

## §7 — Honest list of what the mechanism does NOT promise

Per goal.md AC: "The output is honest about what remains uncertain."

1. **The contract will not catch an LLM agent disobeying it** (MAST FM-1.1 / FM-1.2; file 02 §Q1, §Q7). If a code-simple agent reads the scribble contract correctly and chooses to deviate, no static or runtime check stops it. The mitigation is `ui-verify-flutter` (a separate skill) — that's outside the contract mechanism's promise.
2. **The lint catches drift, not disobedience.** The lint asserts that producer's `produces:` matches consumer's `derived_from:`. It does not assert that the producer's actual output conforms to its declared schema at every invocation — that's the pre-check's job, and pre-checks can be bypassed if a developer comments them out.
3. **Bidirectional-feedback at scale is unproven**, beyond the Magentic precedent. Three failure types (coder→scribble, validator→scribble, scribble→flow) are covered; novel patterns may not fit the `responder_required` discriminator cleanly. Plan to revise the schema after observing 5+ real revision_target.yaml in production.
4. **`contract_version: 0` opt-out enables permanent bifurcation.** The 60-day sunset is a target, not a guarantee. If 2-3 obstinate skills stay at `version: 0` past sunset, the lint either gets a permanent exception list (drift opportunity) or blocks all builds (developer-hostile). User reviews the situation at the 60-day mark and decides.
5. **The `factory-map` interpretation of AC-06** (D-6 above) is an interpretation. The user may reject it and require a literal single file — in which case a follow-up exploration would be needed.
6. **Token-cost of contract.yaml + schemas is theoretically zero** at skill invocation (sidecar, L3 progressive disclosure). In practice, if `claude-route` or `claude-modify-skill` start loading them frequently, this needs measurement (file 08 §6 gap, still open).
7. **The rubric (D-1) was validated on one pipeline** (scribble). It may not generalize to all skill families. Re-run the rubric per-family during Wave 2/3 migration; expect refinements.
8. **The cleanup obligation (delete-after-replace)** assumes the schema's coverage perfectly matches the prose's coverage. If a prose spec contains additional context the schema can't express (worked examples, rationale paragraphs), that context must move to a new location (typically the schema file's leading comment block, or a `<artifact>_design_notes.md` companion) before deletion. The migration must NOT delete information.

9. **`source: external` is trust-based** (Round 2 finding §"Honest" #4). The lint cannot verify that an `external` annotation is honest. A skill author could mark a cross-skill dependency as `external` to silence a violation. Mitigation: code review at PR-equivalent time; the rollout-task ACs include a "no `source: external` for paths obviously produced by another skill" review checklist item. Long-term mitigation: factory-map render script (D-6, FU-7) makes `external` annotations visible in the global graph; pattern-checking script could flag suspicious `external` annotations heuristically.

10. **Schema validation of real artifact files is a Wave-2 deliverable, not a Round 2 prototype.** The prototype produced human-readable schema YAML but did NOT implement `validate_against_schema.py`. Wave 2 (FU-2) writes that validator script in tandem with adding the 5-line bash pre-checks. Until then, schemas are documentation + lint-augmented producer/consumer declaration; not runtime-enforcing.

11. **Skill-vs-agent rubric scales to all skill families is unproven beyond scribble.** Validated only on `ui-create-scribble` in Round 1 §3.2. Wave 2 + Wave 3 will hit cases where a skill has phases that are borderline 2/4 — expect refinements to the rubric's signal weights. Plan to revise the rubric documentation after Wave 2 produces 3-5 real applications.

---

## §8 — Cycle plan after Round 3

| Round | Status | Next |
|---|---|---|
| Round 1 | ✅ Complete | — |
| Round 2 | (Filled by `04_round_2_prototype_summary.md`) | — |
| Round 3 | ✅ Complete (this file) | — |
| Phase 3 | Pending | Present synthesis to user; iterate per feedback |
| Phase 4 | Pending | Create follow-up rollout tasks via `task-create`; tick ACs; `task-complete` |

---

## §9 — Follow-up tasks to create in Phase 4

Per goal.md S-3 ("tasks are the only real integration mechanism"). Each line below becomes ONE `task-create` invocation.

| # | Task title | Parent REQ | Type | Effort | Notes |
|---|---|---|---|---|---|
| FU-1 | Wave 1: contract.yaml + schemas for producer skills (task-create, requ-explore, ui-create-scribble, ux-write-canon-concept) | REQ-PROC-044 | impl | L | Includes lint script productionization + factory-map render script |
| FU-2 | Wave 2: contract.yaml for consumer skill families (code-*, ui-verify/improve, task-derive/create-code/complete) | REQ-PROC-044 | impl | L | Blocked by FU-1; adds runtime pre-checks |
| FU-3 | Wave 3: contract.yaml for remaining skills (claude-*, doc-*, release-*, misc) | REQ-PROC-044 | impl | M | Blocked by FU-2; sunset `contract_version: 0` 60 days after start |
| FU-4 | Add `revision_target.yaml` schema + `responder_required:` discriminator to `pending_feedback/` channel | REQ-PROC-044 | impl | S | Documentation + minimal schema; orchestrator unchanged |
| FU-5 | SCRIBBLE-SPLIT: refactor `ui-create-scribble` into thin orchestrator + 3 sub-skills + agents per Round 1 §3.3 | REQ-PROC-044 (or REQ-PROC-032 if developer prefers) | impl | L | Blocked by FU-1 (needs the contract mechanism to declare sub-skill interfaces); replaces TASK-PROC-032-10's SCRIBBLE-SPLIT bundle from file 09 §11 |
| FU-6 | Codify sub-skill-vs-agent rubric in `claude-create-skill` AND `claude-modify-skill` | REQ-PROC-044 | impl | S | Per Round 1 §3.4 — rubric must live in both skills |
| FU-7 | Factory-map render script + AC-06 interpretation document | REQ-PROC-044 | impl | S | Per D-6 — produces the single-location read for AC-06 |

(FU-1..FU-3 + FU-7 are the core mechanism rollout. FU-4 lands the bidirectional channel. FU-5 is the SCRIBBLE-SPLIT downstream that this exploration unblocks. FU-6 codifies the rubric for future skill creation.)

The 10 original deferred bundles from TASK-PROC-032-10's file 09 §11 (Q2-CONTRACT, Q1-AGENTS, NEW-SKILL, etc.) get **partially absorbed** by FU-1..FU-7:
- Q2-CONTRACT scope is now distributed across FU-1, FU-2, FU-4 (the contract mechanism replaces Q2-CONTRACT's per-artifact contract decisions)
- NEW-SKILL stays (it's the `claude-create-agent` + `claude-modify-agent` pair, not affected by this exploration)
- Q1-AGENTS stays (the agents are content; the contract mechanism gives them an interface to declare)
- SCRIBBLE-SPLIT → FU-5
- DOMAIN-VOCAB stays (independent vocabulary work)
- VISUAL-VALIDATE, BREAKPOINTS, INSPIRATION, PREBRIEF, CROSS-FEATURE stay as originally scoped

A follow-up note to TASK-PROC-032-10 (the parent exploration) will reconcile its deferred bundles against FU-1..FU-7. That reconciliation is part of TASK-PROC-032-10's iteration 6, not this task.
