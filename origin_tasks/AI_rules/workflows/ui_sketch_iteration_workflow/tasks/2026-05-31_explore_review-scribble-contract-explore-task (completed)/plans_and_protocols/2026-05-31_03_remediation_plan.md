# Remediation Plan — recover the lost strand + create agent skills + harden verification

**Task:** TASK-PROC-032-16 · **Date:** 2026-05-31 · **Model:** Opus 4.8
**Driver:** developer decision in `2026-05-31_02_feedback.md` — implement the COMPLETE plan (drop nothing); create `claude-create-agent`/`claude-modify-agent` first; fold DOMAIN-VOCAB capability into those skills; widen the verify task.

> This plan does three things: (1) modify REQ-PROC-032 (new ACs for the accidentally-lost strand), (2) create the prerequisite agent-authoring skills + new scribble tasks, (3) modify existing tasks (fix broken skill refs + dependencies, widen the verify task). Nothing here is executed yet — it is the actionable plan for approval.

---

## A. Requirement modifications

### A1. REQ-PROC-032 — add 5 ACs (AC-37..AC-41) for the recovered strand

Run a focused `requ-explore` pass on REQ-PROC-032 that adds these acceptance criteria (next free id is AC-37) and the matching body prose. Each recovers a decision that was adopted in TASK-PROC-032-10 but encoded nowhere.

| New AC | Name | End-state (description seed) | Recovers |
|---|---|---|---|
| **AC-37** | Scribble storage mirrors `lib/features/` | Scribbles live at `requirements_tasks/scribbles/<feature_path>` mirroring `lib/features/` (and `lib/core/` → `_core/`), 1:1 by name/hierarchy; the existing scribble is migrated there; a parity check flags divergence; `ui-scribble-generator`/`-iterate` and the consumers (`ui-verify-flutter`, `code-simple`/`-complex` Sketch Gate) discover scribbles via the `feature_path` mirror. | D33–D36 |
| **AC-38** | Per-flow navigation captured | Each flow a scribble participates in has a `flow_navigation.yaml` (edges, triggers, escape paths, back-stack policy) in the flow folder; `ui-scribble-handoff-emitter` emits/updates it; `flutter_handoff.yaml` points to it; `ui-verify-flutter` and the coder consume it. | D20 |
| **AC-39** | Per-flow walk validation | Before approval, `ui-scribble-auto-review` walks the scribble screens in each participating flow's step order and verifies each step's intent is supported; a flow flaw is routed upstream via the revision channel; the auto-review brief carries one-line human walk instructions (which file to open, which screens in which order) per flow. | D39 |
| **AC-40** | Approval trail | On approval, an `APPROVAL_TRAIL.md` aggregates the decision history across versions (rejected alternatives, key trade-offs, the "why" behind locks) by synthesizing the per-version `feedback.md` + auto-review briefs + diffs; emitted by `ui-scribble-approve-handoff`. | D43 |
| **AC-41** | Contributing-requirements / participating-flows discovery | A script auto-discovers `contributing_requirements` (primary + cross-cutting) and `participating_flows` for a scribble from `feature_path` + `requirements_matrix.md` + UI-scope heuristic (no new frontmatter fields — D41/D42 stay dropped), populates `scribble_metadata.yaml`, and flags ambiguities for review rather than silently emptying; a consistency lint requires the primary contributing requirement to match `feature_path`. | D29, D30, D40 |

Body work in the same `requ-explore` pass: extend the relevant `## Storage and Organization` / contract sections; add `sections` entries if a new heading is introduced; keep the "What a Scribble Commits To" section (AC-21) as the single normative contract source.

**Note on AC-37 dependency:** the `lib/features/` structure/naming policy is itself underspecified (flagged in TASK-PROC-032-10 file 11 / iteration 5 §5.3). Two ways to handle — see open decision O2.

### A2. NEW requirement — "Factory capability-authoring skills" (DECIDED: O1)

Developer decision: create a **new requirement that bundles all skills which modify/extend the factory's capabilities** — the meta-skills whose quality directly determines factory quality (`claude-create-skill`, `claude-modify-skill`, `claude-create-agent`, `claude-modify-agent`, `claude-write-script`, `claude-modify-ordering-rules`, …). **REQ-PROC-044 (Software Factory Quality Properties) is the likely parent** (related at minimum).

Run a `requ-explore` to author this requirement (new REQ-PROC id, parented under/related to REQ-PROC-044, status `active` — it is a living-document family). It owns at least these ACs:

- **Agent authoring exists and is governed.** Creating/modifying a `.claude/agents/*.md` file is done through `claude-create-agent` / `claude-modify-agent`, which enforce: a naming scheme (collision-checked against built-ins, Han imports, existing agents), an `allowed_tools` heuristic by intent class (no bare `*` without justification), a when-to-create-an-agent gate (disqualifying questions vs. extending an existing skill/agent), the required structural sections (≤50-token role identity, `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`), and an agent-vs-session suitability check (TASK-PROC-032-10 file 13 §5).
- **Domain-Vocabulary authoring aid.** The skill pair produces 10–25 expert-tier terms passing the "15-year practitioner test" (instruction-driven, optionally web/research-sourced — these are book/research terms, rare on the web; the skill must push the LLM past shallow vocabulary). This is the home of capability D9.
- **Migrate existing meta-skills under this requirement (DECIDED):** `claude-create-skill`, `claude-modify-skill`, `claude-write-script`, `claude-modify-ordering-rules` (and `claude-create-agent`/`claude-modify-agent` once built) are owned by this requirement. The N0 `requ-explore` records the ownership; existing ACs about those skills (e.g. REQ-PROC-044 AC-03 split rubric) are referenced/cross-linked, not duplicated.

**Epic wrinkle (NEW — needs a sub-decision).** Your O1 answer was "a feature under the REQ-PROC-044 epic," but **REQ-PROC-044 is currently a flat requirement, not an epic** (no `epic_` prefix, no `feat_*` children). To place a feature under it, either:
- **(E1) Promote REQ-PROC-044 to an epic** (`epic_factory_quality`): its 7 cross-cutting ACs are good epic-level invariants; the new "capability-authoring skills" becomes `feat_capability_authoring_skills/` under it. Cleanest conceptually; a `requ-explore` restructure.
- **(E2) Create the new requirement as a related sibling** (new REQ-PROC id) that references REQ-PROC-044 as related, no epic restructure. Lighter; slightly less tidy than your stated intent.

This requirement (whichever shape) must exist before N1 can be created (N1 needs a parent).

---

## B. New tasks to add

### Prerequisite wave (factory infrastructure — must precede the scribble agent-editing tasks)

| # | Task (folder name) | Type | Parent | Effort | After | Covers / does |
|---|---|---|---|---|---|---|
| **N0** | `explore_factory-capability-authoring-skills` (the A2 requirement-authoring pass) | explore | REQ-PROC-044 (parent) | M | — | `requ-explore` that authors the new "factory capability-authoring skills" requirement + its ACs (agent authoring governed; Domain-Vocabulary aid; scope of existing meta-skills). Produces the parent REQ for N1/N2. |
| **N1** | `impl_create-claude-agent-authoring-skills` | impl | NEW requirement (A2) | M–L | N0 | Create `claude-create-agent` + `claude-modify-agent` via `claude-create-skill`. Bake in: naming scheme, `allowed_tools` heuristic, when-to-create gate, required sections, **Domain-Vocabulary + Anti-Pattern authoring aid (D9 capability)**, agent-vs-session suitability check. Update INDEX.md + factory_flows.md. |
| **N2** | `impl_port-domain-vocabulary-to-existing-agents` | impl | NEW requirement (A2) | S–M | N1 | Use `claude-modify-agent` to add `## Domain Vocabulary` + `## Anti-Patterns` to the 6 existing agents (architecture-advisor, implementation-engineer, opus-advisor, quality-checker, setup-optimizer, test-engineer). This is D9, executed *through* the new skill. |

(N1 also retro-justifies the `ui-scribble-*` agents shipped ad-hoc by 044-07 — optional checklist item in N1 to bring them under the rubric, not a separate task.)

### lib/features structure policy (DECIDED: O2 — create now; blocks S1)

| # | Task | Type | Parent | Effort | After | Does |
|---|---|---|---|---|---|---|
| **P0** | `explore_lib-features-structure-policy` | explore | presentation/architecture requirement (home TBD — see note) | M | — | Define when a new `lib/features/` feature is created, how features are scoped and named, and the `lib/core/` boundary; codify in `doc/presentation/coding/folder_structure.md` (currently brief/informal). AC-37's scribble mirror enforces parity against this policy, so it must exist first. |

Note: P0's parent is a presentation/architecture requirement (not REQ-PROC-032). If none cleanly fits, P0's `requ-explore` may first need to home it. **P0 blocks S1** (storage mirror).

### Recovered scribble strand (parent REQ-PROC-032 — derived after the A1 `requ-explore`)

Produced by `task-derive-from-requ` on REQ-PROC-032 once AC-37..41 exist. Proposed cut:

| # | Task | Covers | Effort | After | Notes |
|---|---|---|---|---|---|
| **S1** | `impl_scribble-storage-mirror-lib-features` | AC-37 | M | **P0**, N1 | git mv existing scribble → `requirements_tasks/scribbles/therapist/data_transfer/`; path-discovery edits in generator/iterate + verify-flutter + code-simple/complex Sketch Gate; parity lint via `claude-write-script`; SKETCHES_README folder-structure section. **after P0 (policy) and N1 (touches agents).** |
| **S2** | `impl_scribble-flow-navigation-yaml` | AC-38 | M | doctrine task 032-11 (handoff schema) | handoff-emitter emits `flow_navigation.yaml`; schema; verifier + coder consumption. **after N1.** |
| **S3** | `impl_scribble-per-flow-walk-validation` | AC-39 | M | 032-12 (review doctrine) | extend auto-review + persona-walker; walk instructions in the brief; flow-flaw → revision channel. **after N1.** |
| **S4** | `impl_scribble-approval-trail` | AC-40 | S | 032-12, 032-29-handoff | approve-handoff aggregates feedback/brief/diff into APPROVAL_TRAIL.md. |
| **S5** | `impl_scribble-contributing-requirements-discovery` | AC-41 | M | — | discovery script (`claude-write-script`) + generator wiring + consistency lint. |

(O3: whether S3/S4 fold into existing 032-12 / handoff tasks instead of standing alone.)

---

## C. Modifications to existing tasks

### C1. Fix the broken skill references (032-11, -12, -13, -14, -19)

All five say "agent edits through `claude-modify-agent`" (and -19 references `claude-create-agent`). After N1 lands, these references become valid. Two edits per task:
- Keep the `claude-modify-agent` / `claude-create-agent` reference (now real), **and**
- add `after: [<N1 task id>]` to each so they cannot run before the agent-authoring skills exist.

(If O1 is resolved as "do NOT create standalone skills, use claude-create-skill/modify-skill for agents too", then instead rewrite the references to `claude-modify-skill`/`claude-create-skill` and drop the N1 dependency. The feedback says create them — so the default is the dependency route.)

### C1b. Propagate `design_decisions` to the coder (D8 — newly recovered)

`design_decisions` (L14) are captured in `scribble_metadata.yaml` but never reach `flutter_handoff.yaml` (verified: 0 mentions in schema + handoff-emitter), so the implementer never sees them. Amend **AC-23** to include a `design_decisions:` block in `flutter_handoff.yaml`, and widen existing task **032-11** (which already edits `ui-scribble-handoff-emitter` + the handoff schema for the `contract:` block) to emit it. Small, co-located change.

### C2. Widen the verify task 032-20 ("the final guard")

- **Coverage:** extend `covers.acceptance_criteria` to AC-21..AC-41 (add AC-37..41).
- **After-chain:** add S1..S5 (and N1/N2 if their outputs are in scope of this verification, or leave N1/N2 to a REQ-PROC-044 verify).
- **Potency upgrades** (write into its goal): audit each AC against the *shipped artifact* not the task's claim; after the location migration, assert **no stale duplicate scribble docs** remain at the old path (the developer's file-14 cleanup caution); assert the parity lint and the contributing-requirements consistency lint actually run and pass; open a generated scribble and confirm CONTRACT BLOCK + flow_navigation pointer + APPROVAL_TRAIL exist; confirm the heuristics corpus PROVISIONAL marker is cleared; file fix-tasks for any gap rather than ticking optimistically.

### C3. Priority override

Per the total-cost / infra-first stance (file 11, iteration 5 §7): add **N1** (and **S1** if the location migration must precede further 0.0.1 UI work) to `.claude/task_ordering_priority_override.txt` so they run before 0.0.1 coding resumes. N2 and the remaining S-tasks can follow.

---

## D. Sequencing (dependency graph)

```
N0 explore (new factory-capability requirement) ─► N1 (create agent skills) ─┬─► N2 (domain-vocab to 6 agents)
                                                                             ├─► 032-11,-12,-13,-14,-19 (unblocked: real agent skills)
                                                                             ├─► S2, S3 (touch agents)
                                                                             └─► S1 (also needs P0)
P0 explore (lib/features policy) ─────────────────────────────────────────► S1 (storage mirror)

A1 explore (REQ-PROC-032 AC-37..41) ─► task-derive ─► S1..S5

032-11 (doctrine) ─► 032-18 (consumers), 032-19 (visual-validate), S2 (handoff schema)
032-12 (review doctrine) ─► S3, S4   (S3/S4 standalone — DECIDED O3)

032-20 (verify, widened) ─► after ALL of: 032-11..-19, S1..S5
```

Critical path: **N0 → N1 → (scribble agent-editing tasks + S2/S3) → 032-20**; S1 also gated on **P0**. A1/derive and P0 run in parallel with N0/N1.

---

## E. Decisions (resolved 2026-05-31)

- **O1 — RESOLVED.** New requirement bundling the factory's capability-authoring skills (meta-skills), REQ-PROC-044 as likely parent; standalone `claude-create-agent`+`claude-modify-agent` confirmed. → A2 / N0.
- **O2 — RESOLVED.** Create the `lib/features/` structure-policy task now. → P0 (blocks S1).
- **O3 — RESOLVED.** S3 (per-flow walk) and S4 (approval trail) are **standalone** tasks.
- **O4 — RESOLVED: ADJUST FIRST.** Execution is held. Nothing is created/modified until the developer approves this updated plan (or directs further changes).

### Remaining adjustment questions surfaced by O1 (for the developer)
- Exact name/id and folder for the new factory-capability requirement (proposed: a feature under the REQ-PROC-044 epic, e.g. `factory_quality/feat_capability_authoring_skills/`). Confirm or relocate.
- Whether existing `claude-create-skill` / `claude-modify-skill` / `claude-write-script` / `claude-modify-ordering-rules` are pulled under the new requirement now, or only referenced as in-scope siblings (recommend: reference now, migrate ownership lazily).
- P0's parent (presentation/architecture requirement home for the `lib/features/` policy) — to be settled at P0 authoring time.

---

## F. Final verification — does the plan cover everything?

Adversarial cross-check of **every** decision (D1–D47 + redundancy additions R3/R9 + the explore's reject list) against a destination. Categories: **Shipped** (already done by REQ-PROC-044 program), **Encoded** (AC-21..36, tasks 032-11..-20), **Recovered** (new AC-37..41 / tasks N0–N2, P0, S1–S5, C1b), **Dropped-correctly** (user rejected), **Verify** (032-20).

| D | Decision | Destination |
|---|---|---|
| D1 | Q2 contract-explicit (B1–B5) | Encoded AC-21..25 |
| D2 | Position A (single locked set) | Encoded AC-21 |
| D3 | Q1 UX-protocol ports (A–F) | Shipped (heuristics corpus) + Encoded AC-28 |
| D4 | No Han agent import | Shipped (honored) |
| D5 | Execution order | Decided (moot) |
| D6 | L8 sizing as token reference | Encoded AC-26 |
| D7 | L15 a11y intent locked | Encoded AC-26 |
| **D8** | **design_decisions → flutter_handoff** | **Recovered C1b (AC-23 amend + 032-11)** ← newly found |
| D9 | DOMAIN-VOCAB to 6 agents | Recovered N2 (capability in N1) |
| D10 | Accept research gaps | Decided (moot) |
| D11 | Verifier scope = locked-only | Encoded AC-25 |
| D12 | Visual-validate skill (Opus) | Encoded AC-36 / 032-19 |
| D13 | Multi-breakpoint (device classes) | Encoded AC-32 / 032-13 |
| D14 | Reviewer-framed CONTRACT BLOCK | Encoded AC-22 |
| D15 | Structured inspiration inputs | Encoded AC-33 / 032-14 |
| D16 | Three named scribble agents | Shipped (044-07, revised to agents) |
| D17 | Reviewer pre-brief | Encoded AC-34 / 032-15 |
| D18 | Persona-embodiment agent | Shipped (ui-scribble-persona-walker) |
| D19 | Cross-feature consistency | Encoded AC-35 / 032-17 |
| D20 | flow_navigation.yaml | Recovered AC-38 / S2 |
| D21 | Iteration-fatigue detection | Encoded AC-31 / 032-12 |
| D22 | claude-create-agent + modify-agent | Recovered N0 (req) + N1 |
| D23 | (iter3) approval-trail deferred → became D43 | see D43 |
| D24 | Live Flutter preview | Dropped-correctly (rejected) |
| D25 | Inter-version diff | Encoded AC-29 / 032-12 |
| D26 | A/B variant generation | Dropped-correctly (rejected) |
| D27 | Persona-conflict + DDR | Encoded AC-30 / 032-12 |
| D28 | verification_seeds (R3-collapsed into handoff) | Encoded AC-36 |
| D29 | contributing_requirements + primary-owner | Recovered AC-41 / S5 (fields exist) |
| D30 | participating_flows + index | Recovered AC-41 / S5 (+ AC-18 index) |
| D31 | Auto-review "review brief" | Encoded AC-29 / 032-12 |
| D32 | Rule-application audit log | Encoded AC-27 / 032-11 |
| D33 | Scribble location → mirror lib/features | Recovered AC-37 / S1 |
| D34 | _core/ subfolder mirror | Recovered AC-37 / S1 |
| D35 | Scribble–feature parity lint | Recovered AC-37 / S1 |
| D36 | feature_path field | Recovered AC-37 / S1 (field exists) |
| D37 | Spawn skill-interface exploration | Shipped (REQ-PROC-044 program) |
| D38 | Bidirectional revision channel | Shipped (044-06) |
| D39 | Per-flow walk validation | Recovered AC-39 / S3 |
| D40 | Cross-cutting auto-discovery script | Recovered AC-41 / S5 |
| D41 | presentation_layer field | Dropped-correctly (iter5 audit) |
| D42 | serves_requirements field | Dropped-correctly (use requirements_matrix) |
| D43 | APPROVAL_TRAIL.md | Recovered AC-40 / S4 |
| D44 | Inter-version diff HTML toggle | Encoded AC-29 / 032-12 |
| D45 | Persona-conflict → VCD/flow update | Encoded AC-30 / 032-12 |
| D46 | Auto-review brief distinct from diff | Encoded AC-29 / 032-12 |
| D47 | SCRIBBLE-SPLIT | Shipped (044-07) |
| R3 | Collapse verification_seeds into handoff | Encoded AC-36 |
| R9 | claude-modify-agent gap-fill | Recovered N1 |

**Result: every D-decision now has a destination.** Nothing is silently dropped: the rejected items (D24, D26, D41, D42) were killed by explicit developer/audit decision; everything else is shipped, encoded, or recovered. The only items found uncovered during this verification pass were **D8** (now C1b) and the **REQ-PROC-044 epic wrinkle** (now §A2 decision E1/E2).

**Two open sub-decisions before execution — RESOLVED 2026-05-31:**
1. **E1 chosen** — promote REQ-PROC-044 → `epic_factory_quality`; new requirement is `feat_capability_authoring_skills` under it.
2. **Migrate-now confirmed** — the 4 existing meta-skills are brought under the new requirement in N0 (not deferred).

**Developer authorized execution (2026-05-31).** Proceeding in dependency order: requirement work (N0 epic promotion + new feature requirement; REQ-PROC-032 AC-37..41 + AC-23 amend) → task derivation (N1/N2, S1–S5, P0) → existing-task edits (after:N1 on 032-11/-12/-13/-14/-19, fix agent-skill refs, widen 032-20).

---

## G. EXECUTION COMPLETE (2026-05-31)

The plan is implemented (setup/restructure scope — the impl tasks themselves are now queued for the normal execution flow). Commits: `6ece1dc7` (phase 1), `df63b28a` (phase 2/3) + merge/status auto-commits.

| Plan item | Outcome |
|---|---|
| A2 epic promotion | REQ-PROC-044 → `epic_factory_quality` (git mv, IDs stable) |
| A2 new feature requirement | **REQ-PROC-044-01** `feat_capability_authoring_skills` (5 ACs; status active; migrates the 6 meta-skills) |
| A1 REQ-PROC-032 ACs | **AC-37..AC-41** added; **AC-23** amended (design_decisions / D8) |
| N0 | TASK-PROC-044-16 (explore, in_progress — requirement authored) |
| A1 task | TASK-PROC-032-21 (explore, in_progress — ACs authored) |
| N1 / N2 / V | TASK-PROC-044-01-01 / -02 / -03 |
| P0 | TASK-NFUNC-021-01 (lib/features policy, REQ-NFUNC-021; blocks S1) |
| S1..S5 | TASK-PROC-032-22..-26 (AC-37..41) |
| C1 after-wiring | 032-11/-12/-13/-14/-19 + S1/S2/S3/S5 → after TASK-PROC-044-01-01; S1 also after P0; 032-25 standalone |
| C1b D8 | AC-23 amended + 032-11 scope updated |
| C2 verify hardening | 032-20 widened to AC-21..41, after += S1..S5, final-guard checks added |
| C3 override | all new tasks queued in `.claude/task_ordering_priority_override.txt` |

Verification: no dangling after-refs; all override entries resolve; REQ-PROC-044-01 100%, REQ-PROC-032 AC-37..41 covered; stale old-path strings exist only in immutable historical protocol/log files (correctly untouched). The pre-existing REQ-PROC-032 gaps (AC-08..11, SEC-07/08) are out of scope of this remediation.

Remaining (normal queue, not part of this setup): execute N1→N2, P0→S1, S2/S3/S4/S5, the 032-11..-19 content tasks, then the hardened 032-20 verify; complete the in_progress explore tasks N0/032-21.

**Residual risks (low, called out for honesty):**
- Each edited `ui-scribble-*` skill/agent must keep its `contract.yaml` in sync (REQ-PROC-044 mechanism) — fold into each task's done-criteria.
- N0/N1 and P0 should be added to `task_ordering_priority_override.txt` alongside N1/S1 if they must precede 0.0.1 resumption.
- task-derive on the new requirement will emit its own verify task (parallel to 032-20's role for REQ-PROC-032).
