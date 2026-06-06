# Skill Interface Contracts — Exploration

Date: 2026-05-29
Author: explore-session for TASK-PROC-032-10
Status: synthesis (not a plan; informs the parent task)

---

## §0 — Goal-task draft

A dedicated exploration task is justified. The findings below confirm a systemic problem (implicit-interface pain spans ≥6 skill families, not only scribble), span both *factory infrastructure* and *factory product* layers, and would need a multi-day design study to converge on conventions, tooling, and migration. Folding it into TASK-PROC-032-10 would re-scope that task away from its scribble–coder objective.

Draft `goal.md` (placeholder TASK-ID; parent requirement suggestion: a new sibling under `requirements_tasks/process/AI_rules/factory_infrastructure/` named `skill_interface_contracts`, or attach as a new feature under the existing `workflows/` epic — final placement is a developer decision):

```yaml
---
task_id: TASK-PROC-TBD-01
type: explore
parent_requirement: REQ-PROC-TBD   # new requirement: skill_interface_contracts
urgency: 3
urgency_reason: U3-FRICTION
impact: 5
impact_reason: I5-ENAB
status: planned
effort: L
opus_recommended: true   # cross-cutting; spans all skill families; design-thinking-heavy
writes_requirements: false
---
```

```markdown
# Goal: Explore Explicit Interface Contracts for Factory Skills

## Objective

Define if and how our ~70 skills should declare interface contracts (inputs, outputs, preconditions, side-effects, error contracts, ordering) — and what mechanism (frontmatter schema, sidecar manifest, lint, registry) is the right fit for our project. The current factory grew organically; many skill-to-skill interactions are implicit conventions that work today but produce a transparency, modifiability, and debuggability tax.

## Background

TASK-PROC-032-10 surfaced concrete instances while exploring the scribble–coder contract — most notably that `ui-create-scribble` writes to a folder convention that ≥4 downstream skills read without anyone declaring the contract. The developer's framing: *"transparency becomes an issue. Maybe we need a requirement that dictates some rules regarding that... can we somehow apply divide and conquer? modules? smaller skills with clear boundaries and interface contracts?"*

Pre-work inventory in `2026-05-28_08_skill_interface_exploration.md` (this file's siblings) identifies at least seven pain categories spanning code-*, ui-*, ux-*, requ-*, task-*, doc-* families. The pattern is general, not scribble-specific.

## How to Approach This

Design thinking. Empathize first: walk through three concrete real-world scenarios where the implicit contract caused (or would have caused) silent failure. Diverge before converging — survey 4+ external prior-art patterns (LangGraph TypedDict, CrewAI args_schema, OpenAI strict-mode JSON Schema, Semantic Kernel KernelFunction descriptors, Anthropic Agent Skills progressive-disclosure design) before recommending. Resist the temptation to import the heaviest mechanism (full JSON Schema everywhere) — our token budget and developer-velocity constraints differ from a production SDK.

## Seeds

1. **What's the smallest declared contract that catches the most failures?** If skills declared only (input_files_expected, output_files_produced, invokes_skills), would a static lint catch most of today's implicit-interface bugs? Or do we also need data-shape (frontmatter keys, YAML schemas) declarations?

2. **Where does the contract live?** Inline frontmatter in `SKILL.md` (compact, one place to read) vs. sidecar `manifest.yaml` (clean separation, machine-checkable) vs. registry file in `.claude/contracts/` (cross-skill view, easier diff). Trade-offs: token cost at skill load, ease of update via `claude-modify-skill`, lint affordance.

3. **What counts as a "side-effect"?** Today many skills mutate shared state (e.g. `concept_canon.yaml`, `requirements.md`, `metadata.yaml`, `cycle_state.json`, `automation/pending_feedback/`) without declaring it. Should the contract list write-targets?

4. **Bidirectional feedback channels.** The user named three back-flows: coder→scribble ("can't implement"), reviewer→flow ("scribble reveals flow flaw"), visual-validation→scribble ("Flutter drifted"). Are these one pattern (a generic "needs-revision" channel via a status field + named originator), or three different patterns?

5. **Skill granularity.** When does "split into sub-skills" beat "add a phase inside one skill"? `ui-create-scribble` is 286 lines, 5 phases — would generator / auto-reviewer / handoff-emitter as separate skills be clearer, or just shift the coordination cost up to the orchestrator?

6. **Lint vs. runtime check.** A pre-commit lint (`scripts/quality/check_skill_contracts.py`) is cheap and catches drift. A runtime guard (skill refuses to start if input precondition unmet) is stronger but costs an extra Bash call per skill. Which buys us more, given automation-mode reliability concerns?

7. **What is the migration story?** Even a clean schema is worthless if it can't be incrementally adopted. Can we adopt skill-by-skill, with `contract_version: 0` meaning "unmanaged"?

8. **Are there skills that genuinely should stay bundled?** Some skills are coherent units precisely because their phases share intermediate state (`requ-explore`, `ux-create-flow`). The contract effort should not fragment these.

## Execution Model

Multiple rounds. Round 1: complete the inventory (this file is a starter, not the whole list). Round 2: prototype each of the candidate mechanisms (frontmatter schema, sidecar, registry) on 2–3 representative skills to see the actual cost. Round 3: synthesize a recommendation, including a migration sequence and a *minimal viable contract* for a single skill family (probably `ui-*` since the scribble pipeline is the catalyst).

Web research: ≤10 fetches. Subagents only if needed for inventory fan-out across all ~70 skills.

## Output

A future implementer can answer:
- Which mechanism we adopt and why (one of: frontmatter schema | sidecar manifest | registry file | hybrid)
- The minimal contract fields every skill MUST declare
- How violations are detected (lint, CI, runtime guard) and where they're reported
- Which skills get split into sub-skills, which stay bundled, and the criteria for that decision
- The bidirectional-feedback pattern (one or many)
- The migration sequence — which skill family adopts first, what the rollout looks like

## Acceptance Criteria

- [ ] Inventory: ≥15 concrete examples of today's implicit interfaces, each citing file_path:line
- [ ] External-pattern survey: ≥4 systems compared on the same axes
- [ ] Prototype on ≥2 skills showing the proposed contract in concrete YAML
- [ ] Lint script proof-of-concept (≤80 lines) demonstrating one violation it catches
- [ ] Bidirectional-feedback pattern recommendation with at least one worked example
- [ ] Honest list of what the contract will NOT catch (so we don't oversell it)
```

---

## §1 — Implicit-interface pain inventory (cited)

### 1.1 Folder convention as undeclared contract (the scribble pipeline)

`ui-create-scribble` writes to `[requirement]/scribbles/v{n}/` and emits `flutter_handoff.yaml` on approval. No skill declares this as its contract; the path appears as a literal string in *every* consumer:

- `ui-verify-flutter/SKILL.md:15` — *"look in `[requirement-path]/scribbles/` for the folder whose `metadata.yaml` has `status: approved`"*
- `ui-verify-flutter/SKILL.md:17` — *"Check for `flutter_handoff.yaml` in the approved version folder. If present, use it… If absent, fall back to parsing component mapping blocks"*
- `ui-improve-flutter/SKILL.md:18` — *"If `[requirement-path]/scribbles/flutter_review/comparison.md` exists: read it…"*
- `code-simple/SKILL.md:32–34` — *"Check goal.md for `skip_scribble: true`… check `[requirement]/scribbles/` for `status: approved` version… invoke `ui-create-scribble` skill"*
- `code-complex/SKILL.md:21` — same pattern
- `ui-create-scribble-improve/SKILL.md:69, 223` — has to override the convention for its test workspace, exposing how brittle the literal-path coupling is

If `ui-create-scribble` ever renamed the folder or split the handoff file, every consumer would silently miss it.

### 1.2 Optional output as undocumented switch

`flutter_handoff.yaml` is optional — `ui-verify-flutter:17` falls back to HTML parsing. Behavioral difference (precision, screen coverage, what counts as a "match") is undocumented in either skill. A user who skips a scribble step gets a quieter but materially different verification.

### 1.3 Shared frontmatter keys without a declared schema

The `goal.md` YAML frontmatter is the universal data carrier across `task-create`, `task-derive-from-requ`, `task-create-code`, `code-simple`, `code-complex`, `release-begin-impl`, `task-complete`. Fields like `covers`, `after`, `awaiting`, `opus_recommended`, `target_package`, `writes_requirements`, `requirements_version`, `skip_scribble`, `draft_generator` are produced by some skills and consumed by others — there is no single declared schema.

- `task-create/SKILL.md:321` — *"Add to the YAML frontmatter (after `scope_description`)…"* (adds fields specific to cascade tasks)
- `task-derive-from-requ/SKILL.md:351, 369` — passes fields by name into `task-create` (plan-driven mode); breaks silently if either drifts
- `code-simple/SKILL.md:32` — reads `skip_scribble: true` (no skill registers that field as part of the goal.md schema; only the consumer documents it)
- `ui-create-scribble/SKILL.md:31` — reads `draft_generator` field; same problem

### 1.4 Implicit ordering ("X must run before Y")

- `release-status` workflow diagram in `INDEX.md:131` is the only place the global ordering is declared. Individual skills don't say "must come after release-begin-impl" — the orchestrator (you) has to know.
- `code-simple` → `task-complete` (line 78) → which itself invokes `verify-quality`, `requ-merge`, commit hook. The chain is documented in CLAUDE.md §4 prose, not in declared `invokes:` fields.
- `ui-create-scribble/SKILL.md:256` ends with *"Proceed to implementation. After implementation, use `ui-verify-flutter`…"* — a hand-off recommendation in a sentence, not a contract.

### 1.5 Concept-canon write-target propagated across families

`concept_canon.yaml` is written by `ux-write-canon-concept` and read/depended-on by ≥5 skills:

- `code-simple/SKILL.md:51`, `code-complex/SKILL.md:71` — *"Canon alignment: prefer canonical names from `concept_canon.yaml`… when a new user-facing concept is introduced, invoke `ux-write-canon-concept` first"*
- `ui-create-scribble/SKILL.md:116` — *"Consult `requirements_user_needs/user_flows/concept_canon.yaml`"*
- `ux-create-flow/SKILL.md:105`, `ux-write-scenario/SKILL.md:73`, `requ-explore/SKILL.md:304` — same pattern

No skill declares "I produce concept_canon.yaml entries"; no skill declares "I read them". A schema change in concept canon would propagate as silent quality loss.

### 1.6 Fan-out to agents without contract on what the agent returns

`ui-create-scribble` spawns a Phase 1 agent (line 46) with a 100+-line embedded prompt. There is no schema for what the agent must return; the next phase (auto-review) just inspects the filesystem. If the agent partially fails, the failure is invisible until reviewer or coder hits it.

Same pattern in `code-complex/SKILL.md:24` (architecture-advisor), `code-simple/SKILL.md:46` (implementation-engineer), `ui-verify-flutter/SKILL.md:21` (per-screen agents).

### 1.7 The `claude-modify-skill` registry sync is a manual contract

`claude-modify-skill/SKILL.md:25–36` requires the *editor* to remember to sync `INDEX.md` and `factory_flows.md`. No machine enforcement; relies on convention plus the skill's prose. The same risk applies to keeping consumer skills' literal path strings in sync with a producer skill that renames an output.

---

## §2 — External patterns (web research distilled)

1. **TypedDict / Pydantic schema as contract (LangGraph, CrewAI args_schema)** — the call site declares input shape with Python types; the runtime catches mismatches as InvalidUpdateError. Cheap when there's a runtime; for us, the equivalent is a YAML schema validated by a lint script.
2. **JSON-Schema with strict mode (OpenAI Assistants / Function calling)** — `strict: true` requires `additionalProperties: false` and *every* property listed in `required`. Adapted to us: a `contract.yaml` per skill listing every frontmatter field the skill reads, with no "implicit/optional/unknown" sneak path.
3. **Function descriptors with explicit return description (Semantic Kernel `[return: Description(...)]`)** — every parameter AND the return value carry semantic description so the LLM knows how to use them. Adapted: every skill output (file, frontmatter mutation, side-effect) carries a one-liner of what consumers should expect.
4. **Message types + HandoffMessage (AutoGen Swarm)** — handoffs aren't a free-text "next step" recommendation; they're a typed message carrying both the target and the context to pass. Adapted: structured `handoff:` blocks in skill output (instead of *"use X next"* prose).
5. **Progressive disclosure (Anthropic Agent Skills design guide)** — only name+description loads into context; bodies load on demand. Important for us because our budget is *real*: a heavy contract format that loads on every skill invocation is a net loss even if it improves correctness.
6. **Design by Contract — preconditions/postconditions** — caller is responsible for preconditions; callee guarantees postconditions; violations are different bug classes. Adapted: skill declares preconditions ("approved scribble exists OR skip_scribble=true"); CI lint enforces; runtime guard returns a typed error rather than silently doing the wrong thing.

The unifying lesson: every mature system treats *interface metadata* as code, validated mechanically. Our metaphor today is informal prose.

---

## §3 — Recommended mechanisms (3–5)

### 3.1 Sidecar `contract.yaml` per skill (RECOMMENDED for the first migration wave)

**What.** A new file `.claude/skills/<name>/contract.yaml`. Token cost is zero at skill-load time (Claude only loads `SKILL.md`). Read by lint and by `claude-route` / `claude-modify-skill`.

```yaml
# .claude/skills/ui-create-scribble/contract.yaml
contract_version: 1
inputs:
  required:
    - path: "{requirement_path}/requirements.md"
      frontmatter_keys: [user_needs, target_package]
    - path: "requirements_user_needs/user_flows/{flow_id}/flow.md"
      condition: "requirements.md has user_needs.flow_id"
  optional:
    - path: "{requirement_path}/inputs/sketch.{png,jpg,pdf}"
    - path: "{requirement_path}/inputs/reference.{png,jpg}"
    - frontmatter_key: "goal.md::draft_generator"
      values: [none, claude_design, stitch]
outputs:
  produces:
    - path: "{requirement_path}/scribbles/v{n}/index.html"
    - path: "{requirement_path}/scribbles/v{n}/NN_*.html"
    - path: "{requirement_path}/scribbles/v{n}/metadata.yaml"
      schema: ".claude/schemas/scribble_metadata.yaml"
    - path: "{requirement_path}/scribbles/v{n}/feedback.md"
    - path: "{requirement_path}/scribbles/v{n}/flutter_handoff.yaml"
      condition: "phase 5 (approval) reached"
      schema: ".claude/schemas/flutter_handoff.yaml"
side_effects:
  writes:
    - "requirements_user_needs/user_flows/{flow_id}/scribble_index.html (phase 5a, conditional)"
  may_invoke:
    - requ-explore (on requirement-gap feedback)
    - doc-update-guidelines (on T1/T2 rule anchor)
    - ux-validate-rule
    - ux-write-canon-concept
preconditions:
  - "parent requirement has Presentation Layer scope"
  - "doc/presentation/design/ exists and is readable"
postconditions:
  - "EITHER scribbles/v{n}/metadata.yaml.status=draft AND awaiting user review"
  - "OR scribbles/v{n}/metadata.yaml.status=approved AND flutter_handoff.yaml emitted"
error_contract:
  no_presentation_scope: "report and exit; do not create scribbles/ folder"
  no_personas_for_requirement: "warn; proceed with empty personas_applied list"
```

**Why.** Cheap (no token cost at skill load), expressive enough for static checks, doesn't bloat `SKILL.md`. Compatible with progressive disclosure.

**Cost.** One new file per skill. `claude-modify-skill` learns to update it. ~80-line lint script (`scripts/quality/check_skill_contracts.py`) catches the common bugs: literal path used by a consumer that doesn't appear in any producer's `outputs:`; frontmatter key read by a consumer that no producer lists in `outputs.frontmatter_mutations`; declared `may_invoke` skill that doesn't exist.

**Risk.** Drift — a `SKILL.md` edit forgets to update `contract.yaml`. Mitigated by adding contract-presence to `claude-modify-skill` checklist and lint failing on missing contract for any skill above a `contract_version: 0` floor.

**Interaction.** Replaces the need for some prose in `SKILL.md` ("output is `scribbles/v{n}/`…" can be referenced as `see contract.yaml`).

### 3.2 Project-wide schemas folder `.claude/schemas/`

**What.** Centralize repeated shapes (goal.md frontmatter, metadata.yaml, flutter_handoff.yaml, concept_canon entry). Skills reference them by name in `contract.yaml`.

**Why.** Today the goal.md frontmatter is *the* shared interface across ~10 skills and has no schema anywhere. A single source of truth makes drift impossible.

**Cost.** Initial inventory of fields. Estimated 5–8 schema files. No token cost (lint-time only).

**Risk.** Over-engineering if applied to fields that legitimately vary by skill. Mitigation: schemas are descriptive (allowed keys list), not prescriptive.

### 3.3 Pre-commit lint `scripts/quality/check_skill_contracts.py`

**What.** Adds to `verify-quality` per-change gates. Checks:
- Every skill at `contract_version >= 1` has a valid `contract.yaml`.
- No skill reads a literal `[requirement]/scribbles/...` path unless it appears either as a producer in its own contract or as an input from a declared producer.
- Every `may_invoke` references an existing skill.
- Every produced frontmatter key is consumed (warning) and every consumed key is produced (error).

**Why.** Catches drift on every commit; failures block.

**Cost.** ~80 lines Python. Add to G-series gate definition.

**Risk.** False positives during migration — solved by `contract_version: 0` opt-out for un-migrated skills.

### 3.4 Structured `handoff:` block in skill output

**What.** When a skill ends with "use X next", emit a structured block instead of prose:

```yaml
handoff:
  next: ui-verify-flutter
  context: { requirement_path: "..." }
  reason: "approved scribble emitted; proceed to flutter implementation then verify"
  back_channel: "if verification fails with rule_violation, return here with target=phase4"
```

**Why.** Bidirectional feedback (see §5). Makes orchestration grep-able and lint-able.

**Cost.** A few lines per skill. Trivial unless we want auto-routing on it (out of scope for v1).

**Risk.** None if treated as recommendation; only a contract if we add a lint.

### 3.5 Split-vs-bundle decision rubric in `claude-create-skill`

**What.** Add a checklist to `claude-create-skill` for "would this be cleaner as 2 skills with a contract between them, or 1 skill with 2 phases?" Criteria: (a) phases share intermediate state that escapes context if split → bundle; (b) phases plausibly invoked independently → split; (c) phase boundary is a natural human review point → split; (d) phase outputs are file-based → split is cheap.

**Why.** Today skills grow organically and the question never gets asked. Adding it to creation-time avoids retrofitting.

**Cost.** Documentation only.

**Risk.** Becomes a checklist nobody reads — mitigation: surface in `claude-route` when proposing a new skill.

---

## §4 — Divide-and-conquer applied to the scribble pipeline

Apply §3 mechanisms to `ui-create-scribble` (5 phases, 286 lines, ≥3 spawned agents). Proposed split:

| Proposed sub-skill | Inputs | Outputs | Notes |
|---|---|---|---|
| **ui-scribble-generate** | `requirements.md`, personas, T1/T2 rules, optional `inputs/`, optional `flow_context`, `flow_scope`, `implementation_notes` | `scribbles/v{n}/index.html`, `NN_*.html`, `metadata.yaml`, `feedback.md` | Today's Phase 0 + Phase 1. Pure generation. Stateless w.r.t. previous versions. |
| **ui-scribble-auto-review** | `scribbles/v{n}/` (n odd), same upstream context | `scribbles/v{n+1}/` with gap fixes; `auto_review_report.md` | Today's Phase 2 + Component auto-promotion. |
| **ui-scribble-feedback-classify** | `scribbles/v{n}/feedback.md`, T1/T2 rule corpus | classifications.yaml ({per-item: missing-rule \| requirement-gap \| existing-rule-missed, tier, scope}); spawns `requ-explore` / `doc-update-guidelines` / `ux-validate-rule` as appropriate via declared `may_invoke` | Today's Phase 4. Currently the most rule-heavy phase; isolating it makes the rule corpus a declared input. |
| **ui-scribble-approve-handoff** | approved `scribbles/v{n}/` | `flutter_handoff.yaml` (schema-validated), `scribble_index.html` (flow composite), `metadata.yaml.status=approved` | Today's Phase 5 + 5a. The handoff file becomes the formal contract output. |

**What stays bundled inside `ui-create-scribble`.** The *orchestrator* (the iteration loop v1 → v2 → user feedback → v3 → … → approval). Splitting that out gains nothing — it's the shared-state phase boundary. The renamed orchestrator becomes `ui-scribble-iterate` and is thin: dispatch + version-tracking + user-handoff prose.

**What becomes explicit.**

1. The folder convention `scribbles/v{n}/` moves from literal-path-in-prose to `.claude/schemas/scribble_layout.yaml` referenced by every sub-skill's `contract.yaml`.
2. `flutter_handoff.yaml` gets a schema in `.claude/schemas/flutter_handoff.yaml`. `ui-verify-flutter` declares it as a *required* input (not optional fallback); the optional fallback can stay but is documented as degraded mode.
3. `skip_scribble: true` becomes a declared field in the goal.md frontmatter schema. `code-simple` and `code-complex` declare they *read* it; `ui-scribble-iterate` declares it as an opt-out precondition.
4. `feedback.md`'s shape becomes a schema (today free-form), enabling `ui-scribble-feedback-classify` to validate.
5. `metadata.yaml`'s `status` field gets an enum (`draft | reviewed | approved | superseded | stale`); the implicit `stale_since` / `pending_rules` extension becomes part of the schema.

**Cost.** Four new SKILL.md files (mostly extracted from existing prose, not new logic). Two new schemas. One updated orchestrator. Existing consumers (`ui-verify-flutter`, `ui-improve-flutter`, `code-simple`, `code-complex`) gain a one-line edit each to point at the new producer name.

---

## §5 — Bidirectional feedback patterns

Three back-flows named by the developer; analysis shows they share one structural pattern with three trigger variants:

**Common pattern: typed "needs-revision" message + named originator + named target-phase.**

Adapted from AutoGen's `HandoffMessage`. Concretely: an artifact (the failing item) gains a status field; the originator skill writes a small structured record to a new well-known location.

```yaml
# .claude/needs_revision/<originator-skill>/<timestamp>_<artifact_id>.yaml
originator: ui-verify-flutter
target_skill: ui-create-scribble
target_phase: phase4_feedback_classify
artifact: requirements_tasks/.../scribbles/v3/
reason: structural
detail: |
  Screen 03 has [NavigationBar] in scribble but Flutter has [TabBar].
  Either scribble was wrong or Flutter drifted.
suggested_action: "ask developer; if scribble wrong, regenerate v4; if Flutter wrong, fix in code"
blocks_completion_of: TASK-FUNC-007-15
```

Three triggers:

| Trigger | Originator → Target | What it carries |
|---|---|---|
| Coder can't implement | `code-simple`/`code-complex` → `ui-create-scribble` | Specific impossible element + which doc/ rule conflicts |
| Reviewer finds flow flaw | `ui-create-scribble` Phase 4 → `ux-create-flow` | Which step / Domain Concept seemed wrong from screen design |
| Visual validation drift | `ui-verify-flutter` → `ui-create-scribble` (or to code) | Which screen, which element, structural vs token vs rule |

**Why one pattern, three triggers.** All three are *escalations from the consumer back to the producer of an upstream artifact*. The information shape ("here's the artifact, here's what's wrong, here's the suggested next step, here's what's blocked") is the same. Differentiation lives in `originator` and `reason`, not in three separate channels.

**Why a file-based channel.** Event-driven pub/sub doesn't fit our orchestrator model (the main session is the only consumer; there's no daemon). Polling fits — `claude-route` can scan `.claude/needs_revision/` at session start and surface unresolved items, exactly like the existing `automation/pending_feedback/` pattern. Reuse the pending_feedback pattern verbatim, with a `revision_requests/` subfolder.

**Escalation discipline.** Same 5-cycle back-pressure protocol as `verify-quality` (CLAUDE.md §7). If a revision request bounces ≥5 times, route to `automation/pending_feedback/` (developer answers; orchestrator resumes).

---

## §6 — Honest gaps and uncertainties

- **The inventory is sampled, not exhaustive.** Seven pain categories from ~10 skills examined; the real number across all ~70 skills is unknown. The exploration task's first deliverable should be the full inventory.
- **Cost-of-contract on token budget unproven.** Sidecar files are free at skill load, but if `claude-route` or `claude-modify-skill` start loading them frequently, the budget impact needs measurement. Recommend baseline + measurement during prototype.
- **Schemas-as-LAW risk.** If the schema bureaucracy slows down skill creation, developers will route around it. The migration sequence must keep `contract_version: 0` (opt-out) viable indefinitely for early-stage skills.
- **Bidirectional feedback at scale untested.** The one-pattern-three-triggers claim is from three named examples. There may be cases (e.g. orchestrator → many skills broadcast, or asynchronous "FYI" without a target_phase) that the pattern doesn't fit cleanly.
- **No prototype yet.** All §3 recommendations are paper designs. The exploration task should prototype each on a real skill before committing.
- **Doesn't solve "skill knows nothing about the orchestrator's state".** Contracts solve the data-shape and side-effect declaration; they don't solve "this skill is part of a workflow that also touches X". For that, the existing `factory_flows.md` diagram remains the source of truth, with one improvement: every `handoff:` block could be verified against an edge in the diagram.
- **External-pattern survey was rapid.** ≤6 web fetches; representative but not deep. Particularly: Anthropic's official Agent Skills design guide deserves a fuller read before committing to a mechanism that conflicts with their progressive-disclosure principle.

---

## Sources

- LangGraph: https://docs.langchain.com/oss/python/langgraph/graph-api
- CrewAI: https://docs.crewai.com/en/learn/create-custom-tools
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- Semantic Kernel plugins: https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/
- AutoGen Handoffs: https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/design-patterns/handoffs.html
- Anthropic Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic Engineering: Equipping agents with Skills: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Design by Contract (Ada example): https://jordansrowles.medium.com/design-by-contract-in-ada-preconditions-postconditions-and-type-safety-cff65dcc0ef3
