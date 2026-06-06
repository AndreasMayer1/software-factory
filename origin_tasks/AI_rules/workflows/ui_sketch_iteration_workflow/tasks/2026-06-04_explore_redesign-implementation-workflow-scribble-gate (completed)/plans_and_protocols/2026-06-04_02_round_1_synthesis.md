# Round 1 Synthesis — Redesign of the End-to-End Implementation Workflow Around a Scribble Gate

Task: TASK-PROC-032-29 (explore/design). Date: 2026-06-04.
Inputs read & grounded against (file + what was extracted):
- Substrate: eval task Round-1 (`2026-06-04_02_round_1_evaluation.md`, F1–F16, PROP-1…13, PROP-R1/R2) and
  Round-2 (`2026-06-04_04_round_2_evaluation.md`, §1 comment-leak, §2 resolved inputs, §4 P-A…P-F, PROP-14).
- User seeds: `00_user_initial_input.md` (verbatim German feedback F15/F16 + "rethink the whole workflow"),
  `01_clean-rerun-decision.md` (no backward-compat with pilot artifacts).
- **Skills read end-to-end** (grounding, per goal "do not design in the abstract"):
  `release-begin-impl` (Phase 0–6), `release-begin-impl-finalize` (Phase 0–5), `task-derive-from-requ`
  (6-phase + 1.5 cross-ref gate + modes), `ui-scribble-iterate` (Phase 0–5 + iteration pattern),
  `ui-scribble-auto-review` (fan-out + per-flow walk + diff), `ui-scribble-feedback-classify`,
  `ui-scribble-approve-handoff`, head of `requ-derive-from-flow`.
- **Script read**: `scripts/tasks/create_orchestration_task.py` (the self-perpetuating chain + `task_type`
  routing table at L272–284).
- REQ-PROC-032 AC list (AC-01…AC-41) + section list, for anchoring.

This record is self-contained. A future implementer can decompose it into impl tasks without replaying the
session. Where a choice is the developer's, it is marked **[DEV-DECISION]**.

---

## 0. The single most important grounded finding (changes the framing)

**The current pipeline ALREADY has scribble tasks and coding tasks as distinct, routable task types.**
`create_orchestration_task.py` L272–284 routes plan entries by `task_type`:
`scribble → ui-create-scribble` *(NOTE: this string is a latent bug — see §9 D-0; the real skill is
`ui-scribble-iterate`)*, `scribble_to_flutter`/`impl` → `task-create-code`, `verify`/`explore` →
`task-create`. The orchestration chain materialises tasks **one per session**, sequenced by `after:` edges.

So P-A is **not** "scribbles don't have a layer." The real defect is in **when the coding-task *plan entries*
are authored**, not when they execute:

> `release-begin-impl` Phase 2c calls `task-derive-from-requ` in FULL mode **once**, producing the *entire*
> plan — scribble entries **and** coding entries — in a single decomposition, **before any scribble exists**.
> The coding entries' grouping (`covers_acs`), count, `effort`, `after`, and `implementation_notes` are
> frozen at that moment. The orchestration chain later *materialises* each coding `goal.md` from a plan entry
> that was authored **blind to the scribble outcome**. An `after:` edge can make the coding task *run* after
> its scribble task, but the coding task's **decomposition was already decided** before the UI review could
> change anything.

That is exactly the developer's complaint: "if coding tasks already exist they are invalidated." They are
invalidated not because they *ran* too early but because they were **decomposed** too early.

**Consequence for the whole design:** the structural move is to **bisect the per-requirement decomposition
into two waves separated by the scribble gate** — Wave 1 authors only the scribble (and basis) plan entries;
Wave 2 authors the coding plan entries *after* scribbles are approved, reading the approved scribble +
`flutter_handoff.yaml` as input. Everything else (loopbacks, consistency, session cuts) follows from this.

---

## 1. Seed 1 resolved — the reconciling mechanism for "hard gate" vs "mid-release edits"

The AC demands we **name the actual reconciling mechanism**, not restate the tension. Here it is.

P-A says: *coding tasks must not exist until scribbles are approved.*
P-E says: *requirements (hence scribbles) are edited **during** implementation (something proves
technically unworkable).*

These cannot both be an absolute one-time temporal gate. **Resolution: it is not a gate, it is a
continuously-enforced invariant.** Name it:

### The Scribble-Currency Invariant (SCI)
> **No coding task may be in a *runnable* state while the scribble of any requirement it covers is missing,
> unapproved, or stale relative to that requirement's current committed version.**

- At **release start**, SCI is satisfied *temporally* — Wave 1 creates scribbles, the gate withholds coding
  decomposition until approval. This is the "hard gate" the developer asked for; it is just the **initial
  establishment** of the invariant.
- **Mid-release**, when a requirement is edited (P-E / L6), SCI is **re-violated** for the affected scribble.
  The recovery is mechanical: mark the scribble `stale_since:<commit>` (the field already exists per AC-17 /
  F15, nothing sets it today), auto-create a **scribble-refresh task**, and **block the dependent coding
  tasks** on it (inject the refresh task into their `after:`; if a dependent is already `in_progress`, SCI is
  actively violated → surfaced at the `release-finalize-impl` gate and at `verify-quality`).

**So "the gate" and "the discrepancy-window governance" are the same mechanism observed at two different
times.** P-A is SCI at t=release-start; P-E is SCI maintained at t=mid-release. That collapses two of the six
sub-problems into one invariant. This is the load-bearing synthesis of the whole task.

**Honest residual (Seed 1 was real):** SCI does **not** eliminate the tension, it *relocates* it to a
throughput question — a mid-release requirement edit can stall a wide set of coding tasks while scribbles
re-approve. SCI guarantees *correctness* (no code is written against a stale design) but not *liveness*
(it can serialise). The liveness knob is the **gate scope** (§2.4, [DEV-DECISION D-2]): global vs per-design-
unit. SCI is correct under either; scope only changes how much parallelism survives an edit.

---

## 2. Skill topology (the cut points; names convey call-order)

### 2.1 The chain today (grounded)
```
approved flow
  → requ-derive-from-flow      creates requ-explore goal.md tasks; Tier-A foundation_gap detection
  → requ-explore               authors/edits requirements.md
  → requ-verify-flow-coverage --all   Tier-B global reconciliation / foundation-gap dedup
  → release-plan               assigns requirements→packages→version
  → release-begin-impl         Ph0-2b scope/epic/remediation; Ph2c = task-derive-from-requ per req (FULL,
                               Phase 5 skipped) → assembles plan (scribble + coding entries TOGETHER) →
                               Ph6 activate release + ONE orchestration task
  → /autorun (create_orchestration_task.py)   self-perpetuating chain materialises tasks 1/session by
                               task_type routing; runs scribble tasks AND coding tasks interleaved by after:
  → ui-scribble-iterate        per scribble task (pre-brief→v1→v2 auto-review→gate→…→approve-handoff→
                               flutter_handoff.yaml)
  → code-simple/complex        per coding task (Sketch Gate reads flutter_handoff.yaml — AC-24)
  → release-begin-impl-finalize  coverage audit, after-chain reconcile, semantic validation, user gate
```

### 2.2 The redesigned chain (the bisection)
```
approved flow
  → requ-derive-from-flow      UNCHANGED front; ADDS: emit a provisional design-unit map (§5) as a cheap
                               by-product of its existing cluster analysis (Phase 0). Tier-A foundation_gap
                               unchanged (re-validated below).
  → requ-explore / requ-verify-flow-coverage --all / release-plan   UNCHANGED
  → release-begin-impl         RESHAPED. Ph0-2b unchanged. Ph2c becomes **Wave-1 / Presentation-only
                               decomposition**: per-requirement task-derive-from-requ runs in new
                               `--scope presentation` mode → emits ONLY scribble tasks (+ PROP-11 basis/
                               coverage/foundation tasks) for Presentation design-units, PLUS full coding
                               tasks for pure-domain design-units (no scribble). Activates release. Spawns the
                               **scribble** orchestration chain. Name kept — "implementation begins with design."
  → [SCRIBBLE GATE]            the scribble orchestration chain runs all scribble tasks to convergence
                               (completed + approved). The chain's terminal orchestration task (today's
                               "validation" terminal, create_orchestration_task.py _VALIDATION template)
                               instead emits a **gate-reached** terminal that instructs: run `release-derive-code`.
  → release-derive-code        **NEW middle skill** (runs DURING an already-begun implementation; verb
                               "derive … code" conveys it comes after design). Trigger: scribble gate reached.
                               Re-runs per-requirement task-derive-from-requ in `--scope code` mode for the
                               Presentation design-units, reading the APPROVED scribble + flutter_handoff.yaml
                               (not raw Presentation requirement text). Spawns the **coding** orchestration chain.
  → code-simple/complex        UNCHANGED per-task (Sketch Gate AC-24 already consumes flutter_handoff.yaml)
  → release-finalize-impl      = today's release-begin-impl-finalize, RENAMED for the bracket symmetry.
                               Behaviour unchanged; ADDS an SCI audit (§4) to its Phase-1 coverage audit.
```

### 2.3 Why 2 orchestrator skills + finalize, not the developer's mooted "3"
The developer floated "split Begin Implementation in 2, maybe 3" — the third being a loopback handler. **The
loopback handler is not an orchestrator skill in this design** (§3): loopbacks are handled by *task creation
inside the scribble skills* + the orchestrator's existing `after`-chain machinery. Making loopback a third
top-level skill would re-centralise complexity the developer explicitly wants distributed. So:
- `release-begin-impl` (design wave) — **keeps its name** (the developer's "only the first is Begin Implementation").
- `release-derive-code` (code wave) — new.
- `release-finalize-impl` — rename of the existing finalize.
The verbs **begin → derive → finalize** read as call-order. The scribble gate is the unnamed state between
the first two (a *state the chain reaches*, not a skill — symmetric with how today's chain reaches the
"all packages covered" validation terminal).

### 2.4 Gate scope — the one structural choice the bisection forces  **[DEV-DECISION D-2]**
Is the scribble gate **release-global** (no coding decomposition for ANY requirement until ALL scribbles in
the release approve) or **per-design-unit** (coding decomposition for requirement R proceeds once R's
design-unit's scribbles approve)?
- A **design-unit** = a set of requirements coupled by **shared flows / shared entry surfaces** (the SAME
  coupling that drives the P-F cascade, §5). A pure-domain requirement is a trivial single-member unit with
  no scribble.
- **Global** (developer's literal mental model): simplest, maximally safe, but serialises all backend work
  behind all UI design and makes every mid-release edit stall the whole release's coding wave.
- **Per-design-unit** (recommended): coding for unit U is derived as soon as U's scribbles approve; pure-
  domain units get their coding tasks in Wave 1 immediately (in `release-begin-impl`). Preserves parallelism;
  SCI stays correct. Cost: needs the design-unit map (cheap — §5).
**Recommendation: per-design-unit.** Flag for confirmation; it is the liveness knob from §1.

---

## 3. Loopback taxonomy & task-lifecycle model (Seed 3 / P-C)

### 3.1 The unifying rule (answers "new task vs in-session" for every loopback)
> **A loopback that mutates a *normative upstream* artifact (flow, requirement) ALWAYS spawns a NEW task in
> a fresh session — never inline. A loopback that only refreshes the *derived* artifact (the scribble) within
> the same requirement stays in-session as the next version bump.**

Two grounded reasons it must be a new task when crossing the artifact-type boundary:
1. **Token/session (P-D):** `ux-create-flow` and `requ-explore` are heavy; running them inside a scribble
   session blows its context (this is already why `task-derive-from-requ` Phase 1.5.3 spawns requ-explore in
   a *delegated background agent*, never inline — grounded precedent).
2. **Orderability:** SCI's blocking edges and the gate need a **task ID** to point `after:` at. An inline edit
   produces no schedulable, `after`-orderable unit.

### 3.2 The full loopback table
| # | Loopback | Trigger (grounded) | Owner skill | New task or in-session | Anti-infinite-loop |
|---|----------|--------------------|-------------|------------------------|--------------------|
| **L1** | Flow re-adjust at the scribble gate | Developer at `ui-scribble-iterate` Phase-3 gate says the flow itself is wrong | `ui-scribble-feedback-classify` → `ux-create-flow` | **NEW** flow-revision task (the revision sub-procedure ALREADY exists — `ui-scribble-auto-review` step 1.5 emits `reason: flow_flaw, target_skill: ux-create-flow, blocks_completion_of: <scribble-task>`). On flow re-approval, re-run `requ-derive-from-flow` for the delta. | Human-gated flow approval bounds it |
| **L2** | Requirement edit at the scribble gate | Feedback classified `requirement_gap` | `ui-scribble-feedback-classify` → `requ-explore` | **CHANGE FROM TODAY:** today it invokes requ-explore *inline* (Phase 4). Redesign: emit a **NEW** requirement-edit task that `blocks_completion_of` this scribble task; the scribble task stays open (un-approved) and resumes at v{n+2} when the edit lands. | requ-explore evidence gate + human approval |
| **L3** | Entry missing in another requirement (the seam owner) | PROP-8 requirement-source check: generator cannot *source* the entry from the requirement | scribble generator flags → `feedback-classify` `requirement_gap` | **NEW** requ-explore task against the **seam-owner** requirement (F12), `blocks` this scribble | Seam owner is depth-1; the source check does not recurse |
| **L4** | Auto-review non-convergence | MEDIUM+ gaps persist past v6 circuit-breaker (AC-31 fatigue) | `ui-scribble-iterate` Phase-3 fatigue check → `requ-explore` | **NEW** requ-explore task (requirement ambiguity); scribble pauses | Fixed v6 threshold (already implemented) |
| **L5** | Cross-requirement UI cascade | A scribble's *outward entry surface* changes on approval | PROP-10 integrity check / cascade detector (§5) | **NEW** scoped scribble-refresh task(s) for depth-1 dependents | Lazy wavefront + visited-set (§5) |
| **L6** | Mid-release requirement edit (technical unworkability) | A coding task discovers the requirement is technically wrong | `code-*` / `verify-quality` back-pressure → `requ-explore` | **NEW** requirement-edit task → fires SCI (§1) → **NEW** scribble-refresh task → blocks dependent coding | back-pressure 5-cycle bound + human |

### 3.3 The developer's explicit P-C question, answered crisply
> "On a re-run, are NEW scribble tasks created, or are existing un-approved scribbles updated in place?"

**It depends on whether the scribble was ever approved — and the rule is mechanical:**
- **Un-approved scribble** (the loopback happened *before* approval, L1–L4): **NO new scribble task.** The
  original scribble task is *still open* — it was merely **blocked** on the upstream flow/requirement edit
  task. When that edit lands, `ui-scribble-iterate` **resumes the same task** and generates the next version
  (v{n+2}) against the revised input. "Updated in place," as a version bump, same task.
- **Approved-then-invalidated scribble** (mid-release edit, L5/L6): the original scribble task is **terminal
  (completed)** — you cannot reopen a completed task — so a **NEW scribble-refresh task** is created, scoped
  to the changed screens/ACs (PROP-12 scoped regen). It supersedes the approved version with a new approved
  version, and re-fires the SCI blocking edges onto dependent coding tasks.

So: **un-approved ⇒ same task, new version. approved-then-stale ⇒ new refresh task.** One sentence, covers
every loopback.

### 3.4 Task-creation timeline (when each task type comes into existence)
1. `requ-derive-from-flow`: requ-explore tasks (requirements authoring). + provisional design-unit map.
2. `release-begin-impl` (Wave 1): **scribble tasks** (Presentation design-units) + **basis/coverage tasks**
   (PROP-11 R2/R3) + **coding tasks for pure-domain units** (no scribble). + foundation requirement tasks if
   Tier-A/B raised any (PROP-11 R4, via requ-explore — pre-gate).
3. During scribble execution: loopback tasks (L1–L4) created on demand, each `blocks` its scribble.
4. `release-derive-code` (Wave 2, post-gate): **coding tasks for Presentation design-units**, decomposed
   from approved scribbles.
5. Mid-release: scribble-refresh tasks (L5/L6) + their downstream coding-block edges, on demand.

### 3.5 The `after:`/blocking edges that enforce ordering
- **Basis edge (PROP-11 R2/G2):** scribble(openee) `after` scribble(opener) — **primary entry path only**
  (forward flow direction). Back/close/cross-nav edges are NOT ordering edges (else cycles). Depth-1 only (G3).
- **Loopback block edge:** scribble task `after` its L1–L4 upstream-edit task (so the edit lands first).
- **SCI coding edge:** coding task `after` the scribble task(s) of every requirement it covers — injected by
  `release-derive-code` at decomposition time, and re-injected mid-release by L5/L6 refresh.
- **Cascade edge (L5):** dependent scribble-refresh `after` the origin scribble-refresh (the wavefront, §5).

---

## 4. Consistency model — discrepancy window (P-E) & the SCI audit

### 4.1 The discriminator for blocking-edge vs transparency-flag
The developer asked: is a transparency flag enough, or do downstream readers need blocking `after` edges, and
*which* readers? **Clean rule:**
> **A requirement-reader that would *generate a downstream artifact* from a stale scribble BLOCKS (gets an
> `after` edge on the refresh task). A reader that merely *displays/references* the scribble gets a
> TRANSPARENCY FLAG (`stale_since`).**

Enumerated readers (the full set P-E asked for):
| Reader | Generates or references? | Treatment |
|--------|--------------------------|-----------|
| **Coding task** covering the requirement (consumes flutter_handoff.yaml as UI contract, AC-24) | Generates code | **BLOCK** — refresh task in its `after`; if already in_progress → SCI violation surfaced at finalize + verify-quality |
| **Dependent scribble** sharing the entry surface (P-F, §5) | Generates a wireframe | **BLOCK** — cascade edge (L5) |
| **`ui-verify-flutter` / `ui-visual-validate`** (compares built screen ↔ approved scribble) | Generates a pass/fail verdict against the scribble | **BLOCK** — don't verify against a stale target until refresh |
| **Flow composite index** / `scribble_index.html` (AC-18), release notes, APPROVAL_TRAIL (AC-40) | References/displays the scribble | **FLAG** — render with a `stale_since` banner; no block |
| **`requ-verify-flow-coverage` / coverage report** | References coverage state | **FLAG** — list as stale-pending |

This makes P-E's governance fully determined: *generative readers block, referential readers flag.*

### 4.2 The SCI audit (new, cheap, script-driven)
Add to `release-finalize-impl` Phase 1 (and runnable standalone): for every coding task, resolve the scribble
of each covered requirement; assert it is `approved` AND its `contributing_requirements` commit ≥ the
requirement's current commit. Any coding task whose covered scribble is missing/unapproved/stale = **SCI
violation** → blocks finalize. This is the standing detector for the rot path P-E opens. (Extends, does not
replace, `check_scribble_parity.py`, which only catches orphaned *paths* — F15.)

---

## 5. Cross-requirement UI cascade (P-F) — detector + recovery, no global graph

### 5.1 What detects it
The cascade is **scribble-level, not requirement-level**: a dashboard's interaction model changes → dependent
features' *entry points moved* → their scribbles' **entry-context (PROP-8 Tier-1)** is stale, though their
requirements are unchanged. The dependency signal is therefore **shared entry surface**, not shared
requirement. The substrate already records the edges: PROP-8 Tier-1 = "opener screen = scribble screen at the
*predecessor* flow step"; `flow_positions` records `step_number` + `requirement_id`; `ui-scribble-cross-
feature-checker` already owns sibling scribbles sharing a flow (AC-35). **The entry-reference edges ARE the
cascade graph** — no new graph is introduced.

### 5.2 Why NOT a precomputed global graph (the PROP-10 rot concern, made concrete)
A materialised whole-app UI-dependency graph rots because every scribble regenerates independently (F10). So
**never materialise it.** Resolve the cascade **lazily, one hop at a time, at approval**:

> **Lazy wavefront cascade.** When a scribble S re-approves *with a changed outward entry surface*, query its
> **direct (depth-1)** dependents = scribbles whose Tier-1 entry reference resolves to a screen of S (from
> *live* `flow_positions`, never a cache). Create a scoped scribble-refresh task for each, `after` S's refresh.
> When such a dependent *itself* re-approves, if *its* outward entry surface changed, it enqueues *its* depth-1
> dependents — the wave advances one hop per approval. **Termination:** most refreshes are entry-context-only
> and do **not** move the dependent's own outward surface → the wave dies on that branch. **Cycle guard:** a
> per-cascade `visited` set (keyed on cascade-origin) — a scribble already refreshed in this wave is never
> re-enqueued (same shape as PROP-11 G2 cycle guard).

This gives multi-step cascade ordering (P-F's "how are multi-step cascades ordered") **without** a global
topo sort over a rotting graph: the order is just the wavefront's BFS, materialised one live depth-1 query at
a time. Detector = PROP-10 integrity check run every generation+review; recovery = scoped refresh tasks
(bounded, depth-1, visited-set) — exactly PROP-10's "bounded recovery; never unbounded auto-create," now with
a termination proof.

### 5.3 "Outward entry surface changed" — the precise trigger
A scribble's *outward entry surface* = the screen(s) other features name as their opener (its role as a
Tier-1 target). It "changed" when, between the superseded and new approved version, the opener screen's
identity, route, or entry affordance moved (detectable from the structural diff `ui-scribble-auto-review`
already computes at step 4.5, AC-29). Pure internal edits (copy, a non-entry element) do **not** trigger the
cascade — keeping the wave narrow.

---

## 6. Session / token cut points (P-D) — the whole-chain map

Principle tension the developer named: minimise **total** tokens ("read information twice as rarely as
possible") **and** keep each session holding **only what it needs**. These pull opposite ways. **Resolution:
make the persistent artifacts the hand-off medium, and make each hand-off a *distillation* so re-reads hit
small focused files instead of whole requirements.**

| Stage | Context owner | Cut rationale |
|-------|---------------|---------------|
| `requ-derive-from-flow` | main session (light) + design-unit map by-product | front of chain, already light (reads flows, not requirements.md wholesale) |
| `release-begin-impl` Ph2c Wave-1 | **background agents**, one `task-derive-from-requ` per requirement (existing pattern) | orchestrator never reads requirements.md (grounded constraint, SKILL.md L10/L453) |
| each scribble task | **fresh session** (`ui-scribble-iterate`); each **version a fresh agent** (AC-05, grounded) | scribble session reads requirement + flow + personas ONCE |
| **hand-off scribble→code** | `flutter_handoff.yaml` (small, locked) | **the biggest token win:** the scribble *distills* the requirement's Presentation content (LOCKED-IN set, AC-21) into flutter_handoff.yaml. The Wave-2 coding decomposition and the coding session read the **distilled handoff**, NOT the raw Presentation requirement again. "Read twice rarely" is realised here. |
| `release-derive-code` Wave-2 | **background agents**, one `task-derive-from-requ --scope code` per Presentation requirement | reads non-Presentation ACs + flutter_handoff.yaml (small) |
| each coding task | **fresh session** (`code-simple/complex`) | reads flutter_handoff.yaml + its covered ACs |
| `release-finalize-impl` | script + per-feature agents (existing) | unchanged |

### 6.1 Re-validation of the Round-1 `requ-derive-from-flow` changes (Seed 6 / PROP-11 R4 / F13–F14)
Under the redesign these **still hold, unchanged**: Tier-A `foundation_gap` (provisional, in
`requ-derive-from-flow`) → Tier-B global dedup (`requ-verify-flow-coverage --all`) → PROP-8 scribble-time
requirement-source backstop. The redesign **adds one thing**: `requ-derive-from-flow` also emits the
provisional **design-unit map** (which requirements share entry surfaces) as a by-product of the cluster
analysis it already performs (Phase 0). That map seeds the gate scoping (§2.4) and the cascade neighbourhood
(§5). No different split is warranted — the existing two-tier detection is the right shape.

---

## 7. The comment-nesting render leak — folded-in fix (Round-2 §1 / §7)

**Defect (grounded):** `ui-scribble-generator` wraps reviewer detail in one big `<!-- … -->` block, then emits
inline `<!-- a11y-intent: … -->` comments *inside* it. HTML comments cannot nest → the parser closes the
outer block at the first inner `-->`, leaking the rest as visible wall-of-text (Round-2 §1, line-grounded on
`02_handover_send.{tablet,desktop}.html`).

**Fix locus = how reviewer detail is carried in the artifact** — the SAME locus as PROP-1's human-facing
review layer (which is why the developer folded them together). **Recommendation: stop using `<!-- -->` to
carry multi-line reviewer detail entirely.** Replace with a single, flat, **un-nestable**
`<script type="application/json" id="review-data">…</script>` block per screen:
- It **renders nothing** (so no leak is possible — `<script>` content is never displayed).
- It is **flat and un-nestable** (JSON, not nested comments) — the defect becomes structurally impossible.
- It is **machine-readable** by BOTH audiences: the PROP-13C findings-overlay script reads it to build the
  visible review panel + clickable element markers (PROP-1 human layer); the coder/LLM reads the same JSON
  (component mapping, rule-audit trace AC-27). One carrier, dual audience, zero leak.

This is a concrete must-fix in the **`ui-scribble-generator` agent output contract**, anchored to **AC-22**
(CONTRACT BLOCK present) and **AC-29** (auto-review brief/diff overlay). It is not merely a design abstraction
— it is the carrier-format change that makes PROP-1 implementable and the leak impossible at once.

---

## 8. Which existing skills/artifacts change, anchored to ACs (decomposition seed for impl tasks)

**Spans THREE requirements, not one** — important scoping finding:
- **REQ-PROC-032** (scribble workflow): the scribble-side changes.
- **REQ-PROC-035** (release_preparation / orchestration chain): the Begin-Implementation split + gate.
- **REQ-PROC-058** (unified task-creation plan format): the two-wave `--scope` mode on `task-derive-from-requ`.

| Change | Skill/script/artifact | Anchor AC(s) | New AC needed? |
|--------|-----------------------|--------------|----------------|
| Bisect decomposition into Presentation / code waves | `task-derive-from-requ` (new `--scope {presentation,code}` mode); `release-begin-impl` Ph2c | REQ-PROC-058 (plan format) + REQ-PROC-035 SEC-05 | **NEW AC** in REQ-PROC-035 + REQ-PROC-058 |
| New middle orchestrator `release-derive-code` | new skill (via `claude-create-skill`) | REQ-PROC-035 | **NEW AC** in REQ-PROC-035 |
| Rename `release-begin-impl-finalize` → `release-finalize-impl` | rename (via `claude-modify-skill`) | REQ-PROC-035 | doc-only |
| Scribble gate terminal in the orchestration chain | `create_orchestration_task.py` (new gate-reached terminal alongside _VALIDATION) | REQ-PROC-035 | **NEW AC** |
| Fix `scribble → ui-create-scribble` latent bug → `ui-scribble-iterate` | `create_orchestration_task.py` L276 (§9 D-0) | REQ-PROC-035 | bugfix, no AC |
| Scribble-Currency Invariant + SCI audit | `release-finalize-impl` Ph1; new `scripts/quality/check_scribble_currency.py` | extends AC-17 (stale_since), AC-21/§33 | **NEW AC** in REQ-PROC-032 |
| `stale_since` actually *set* on requirement edit; scribble-refresh task auto-created | `requ-explore` / `task-derive-from-requ` trigger (PROP-12) | AC-17 | **NEW AC** (the trigger; AC-17 only defines the field) |
| Loopback = new-task-not-inline for L2 (requirement edit) | `ui-scribble-feedback-classify` (stop invoking requ-explore inline; create a blocking task) | AC-05, AC-39 revision channel | **NEW AC** |
| Lazy-wavefront cross-requirement cascade | `ui-scribble-cross-feature-checker` (detect) + cascade refresh tasks | AC-35 | **NEW AC** |
| Entry-context spine (PROP-8) emit + review + bounded reconciliation | `ui-scribble-generator`, reviewers, `ui-scribble-auto-review` | AC-16 (flow_positions), AC-27, AC-38 (flow_navigation) | **NEW AC** (entry-surface/multiplicity/back-dest fields) |
| Coverage/ordering/basis (PROP-9/11 R1–R3) | new flow→scribble coverage report; `task-derive-from-requ` auto-`task_type: scribble` for Presentation ACs; task-ordering soft pref | AC-37 parity (distinct) | **NEW AC** in REQ-PROC-032 |
| Comment-leak fix + PROP-1 review layer + findings overlay | `ui-scribble-generator` (JSON carrier) + overlay script | AC-22, AC-29, AC-27 | extends AC-22/AC-29 |
| Design-unit map by-product | `requ-derive-from-flow` | (foundation_gap / cluster) | **NEW AC** in REQ-PROC-053/-flow requirement |
| PROP-14 flow viewer (script-driven MD→HTML) | generator helper script + dependency-admission (REQ-PROC-060) | AC-18, AC-20 | **NEW AC** + **[DEV-DECISION]** dependency |
| Resolved Round-2 §2 inputs (task-start wraps claude-route; sequential reviewers; gate-on-convergence default; container dimension) | `claude-route`/new `task-start`; `ui-scribble-auto-review`; `ui-scribble-iterate`; PROP-2 | AC-05, AC-32 | mixed (some new) |

**Staging recommendation (the exploration may split itself — goal §"Execution Model"):** this is too large for
one impl task. Propose decomposing into **design sub-tasks then impl tasks**, in dependency order:
1. **S1 — REQ-PROC-035/-058 ACs for the two-wave split + gate + `release-derive-code`** (the structural
   spine; everything else hangs off it). Author via `requ-explore`.
2. **S2 — REQ-PROC-032 ACs for SCI + loopback-as-task + cascade + entry-context + coverage/ordering** (the
   consistency layer). Author via `requ-explore`.
3. **S3 — generator carrier-format change (comment-leak + PROP-1 + overlay)** — isolatable, can run parallel.
4. **S4 — PROP-14 flow viewer** — gated on the [DEV-DECISION] dependency; lowest coupling, do last.
Then `task-derive-from-requ` each into impl tasks. S1 before S2 (S2's SCI edges need S1's two-wave task model).

---

## 9. Decisions that still need the developer  **[DEV-DECISION]**

- **D-0 (bugfix, no decision — just flag):** `create_orchestration_task.py` L276 routes `task_type: scribble`
  to a skill string `ui-create-scribble`, which **does not exist** (real skill: `ui-scribble-iterate`; the
  only near-name is `ui-create-scribble-improve`, a different meta-tuning skill). Today's chain would fail to
  run any scribble task. Must be fixed as part of the redesign (or sooner). Grounded at L272–284.
- **D-1 — Confirm the bisection** (§0/§2): "Begin Implementation decomposes ONLY scribble + pure-domain tasks;
  Presentation coding tasks are decomposed only post-approval by `release-derive-code`." Stated by developer as
  intent; confirm as the hard structural requirement.
- **D-2 — Gate scope** (§2.4): release-global vs per-design-unit. *Recommendation: per-design-unit* (preserves
  parallelism; SCI correct either way). This is the liveness knob from Seed 1.
- **D-3 — Skill names** (§2): `release-begin-impl` (kept) → [gate] → `release-derive-code` (new) →
  `release-finalize-impl` (rename). Confirm the names; the bracket verbs begin→derive→finalize convey order.
  Also: go/no-go on the separate `task-start` wrapper over `claude-route` (Round-2 §2 already resolved "both,
  separated" — confirm it lands in this redesign vs its own task).
- **D-4 — SCI blocking vs flagging table** (§4.1): confirm the generative-blocks / referential-flags
  discriminator and the reader list (esp. whether `ui-verify-flutter` should hard-block or advisory-flag on a
  stale scribble — leaning block).
- **D-5 — PROP-14 dependency** (§7 carry / Round-2 §5 Q7): which Markdown→HTML technology, client-side-vendored
  vs build-step (REQ-PROC-060 dependency-admission — developer-authorised, cannot self-add).
- **D-6 — Staging** (§8): accept the S1→S2→(S3∥)→S4 sub-task staging, or decompose differently.

---

## 10. What remains uncertain (honest)

- **Liveness under SCI** (§1 residual): SCI guarantees no code is written against a stale design but can
  serialise a release when a mid-release edit cascades widely. Per-design-unit scoping (D-2) mitigates but does
  not eliminate it. No throughput model exists yet — would need a real multi-requirement release to measure.
- **Cascade termination in practice** (§5): the wavefront terminates *because* most refreshes are entry-context-
  only and don't move the dependent's own outward surface. That is an empirical assumption about how often a
  refresh changes a feature's *own* opener role; unproven until a real cross-feature edit (the dashboard case)
  is run. The visited-set guarantees no infinite loop regardless, but the *width* of a wave is unmeasured.
- **`--scope presentation/code` clean separability** (§2): assumes every AC is cleanly Presentation-scoped or
  not. ACs that are *both* (a backend contract surfaced in UI) may need to appear in both waves or be split —
  the decomposition mode needs a tie-break rule (likely: such an AC's *Presentation facet* is locked by the
  scribble, its *behaviour facet* is a Wave-2 coding task `after` the scribble). Undesigned in detail.
- **flutter_handoff.yaml as sufficient code-decomposition input** (§6): assumes the handoff distils *enough*
  of the requirement's Presentation content that Wave-2 need not re-read the raw requirement. True for layout/
  widgets/copy (AC-21 LOCKED-IN); may be thin for cross-persona constraints the scribble doesn't depict (AC-21
  RE-DERIVE). Wave-2 may still need a *narrow* re-read of RE-DERIVE ACs — bounding that is unverified.
- **PROP-14 colour-highlighting of flow passages** purely from `flow_positions` step numbers, with no LLM re-
  read of the flow (developer's hard constraint) — feasible in principle (substrate exists) but untested.

---

## 11. Acceptance-criteria self-check (this task's goal.md)
- [x] At least one synthesis round produced — this document.
- [x] Defines the problem space in terms not fully known at creation — **the Scribble-Currency Invariant**
  (§1) is the named reconciling mechanism for the hard-gate-vs-mid-release tension (not "there is a tension");
  the **decomposition-time vs execution-time** reframing of P-A (§0); the **generative-blocks/referential-
  flags** discriminator (§4); the **lazy-wavefront** cascade with a termination argument (§5).
- [x] Decisions requiring user input identified and framed to decide — §9 D-0…D-6.
- [x] Honest about what remains uncertain — §10.
