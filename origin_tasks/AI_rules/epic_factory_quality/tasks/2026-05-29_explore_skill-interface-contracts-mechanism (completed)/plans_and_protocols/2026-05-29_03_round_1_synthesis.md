# Round 1 Synthesis — Problem framing + applied rubric

**Task:** TASK-PROC-044-02 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Reads:** kickoff (`01_kickoff.md`), deep web research (`02_web_research_deep.md`), file 08 inventory of TASK-PROC-032-10.

> Round 1 sets the problem space and resolves two prerequisites for Round 2's prototype: (a) three concrete real-world failure scenarios anchoring the *why*; (b) the sub-skill-vs-agent rubric concretely applied to the SCRIBBLE-SPLIT proposal. The 6 OPEN decisions (kickoff §4) are resolved in Round 3 once the prototype validates the mechanism.

---

## §1 — Problem space (sharpened from file 08 + round-2 evidence)

### 1.1 The transparency tax has two distinct origins

File 08's seven pain categories collapse onto two failure modes that need different mechanisms:

| Failure mode | What goes wrong | Mechanism that helps | Mechanism that doesn't |
|---|---|---|---|
| **DECLARATION** (FC1 in MAST, §Q1 of file 02) | Producer changes its output convention; downstream consumers silently miss it. The producer-consumer coupling lives only in literal-path strings inside `SKILL.md` files. | Sidecar `contract.yaml` (file 08 §3.1) + commit-time lint that compares producers' `produces:` with consumers' `derived_from:` | Runtime checks (drift is detected at commit, not at execution) |
| **VERIFICATION** (FC3 in MAST, §Q1 + §Q7 of file 02) | Producer writes a file that *looks* valid but is malformed in a way the consumer can't tolerate. Today the consumer crashes mid-skill or — worse — proceeds with garbage. | Runtime pre-condition check at consumer skill entry (5-line bash assertion + schema validation against `.claude/schemas/`) | Lint alone (the file was correctly *declared* but its *content* drifted) |

PwC's 7× accuracy improvement (file 02 §Q7) came from adding *verification loops*, not from adding *declarations*. The factory should weight verification accordingly: declaration is a write-once cost; verification fires on every consumer invocation.

**Implication for the mechanism**: contracts are necessary but not sufficient. The minimum viable system is **contract.yaml + commit lint + 5-line bash pre-checks**. Three lightweight components; each one without the others has a documented failure mode in the literature (file 02 §Q1).

### 1.2 The bidirectional-feedback channel is structurally one thing

The developer's round-6 question — "should revision_requests be a subfolder of pending_feedback, or a separate channel?" — has a settled answer from Microsoft Magentic (file 02 §Q2). Magentic uses **one typed queue** (`MagenticPlanReviewRequest`) with `approve()` / `revise(feedback)` responders. The same channel handles both agent→agent and agent→human; the difference is a single field on the message. Translated to our system:

```
automation/
  pending_feedback/
    {TASK_ID}/
      question.md            ← existing
      answer.md              ← existing
      revision_target.yaml   ← NEW (Round 2 prototypes this)
      responder_required: human | skill | either   ← field inside question.md or revision_target.yaml
```

This means the orchestrator continues scanning **only** `pending_feedback/` — no second scan. Skills that today emit revision requests via free-form `pending_feedback/<task>/question.md` get a structured discriminator instead. The `.factory/optimize/events/` channel stays separate (it serves a different lifecycle: event-driven improvement suggestions, not blocking work).

This is settled at the structural level in Round 1; Round 2 prototypes the schema; Round 3 codifies the orchestrator update.

### 1.3 Three artifact families, three audiences

Distinguishing these resolves several R-questions from file 10 and file 14 simultaneously:

| Artifact family | Audience | Where it lives | What it MUST NOT do |
|---|---|---|---|
| **`contract.yaml`** (skill interface) | Lint script + human authoring skill | `.claude/skills/<name>/contract.yaml` | Be loaded by Claude at skill invocation; bloat SKILL.md description |
| **`.claude/schemas/<artifact>.yaml`** (shared shapes) | Same lint + author docs | One per shared artifact (goal.md frontmatter, metadata.yaml, flutter_handoff.yaml) | Duplicate prose specs that exist in folder-root READMEs (file 14 §4.4 hard rule) |
| **`pending_feedback/{TASK_ID}/*.{md,yaml}`** (revision channel) | Orchestrator + skills + developer | One subfolder per task | Fragment into multiple channels |

The audiences never overlap, so the three families don't compete for surface area. The schemas folder needs an explicit migration step that **deletes** any folder-root README sections it replaces — Round 2 prototypes one such cleanup as a forcing function.

---

## §2 — Three concrete real-world failure scenarios (Empathize)

Per goal.md "Empathize first — walk through three concrete real-world scenarios where the implicit contract caused or would cause silent failure." Each scenario is drawn from a different pain category in file 08 §1 and shows what the proposed mechanism actually catches.

### Scenario A — The Scribble Folder Rename (Declaration failure)

**Setup**: The next iteration of `ui-create-scribble-improve` decides that `scribbles/v{n}/` should become `scribbles/iteration_{n}/` to be more readable for new contributors. The author edits `ui-create-scribble/SKILL.md`'s prose, regenerates a few test scribbles in the new layout, and pushes.

**What happens today**: `ui-verify-flutter/SKILL.md:15` still looks in `[requirement-path]/scribbles/` for the approved folder. It finds the *old* approved scribbles (left behind from a prior feature) and uses them. The new scribbles produced by the renamed pipeline are invisible to verification. The implementation passes verify-flutter against the wrong scribble; the developer notices only when manual visual review surfaces a mismatch — by which time multiple Flutter features have been built against stale wireframes. **No skill failed; no script returned a non-zero exit; no warning fired.**

**What the mechanism catches**: `ui-create-scribble/contract.yaml.produces:` lists `scribbles/v{n}/` paths. `ui-verify-flutter/contract.yaml.derived_from:` lists the same paths. The commit-time lint asserts every consumer's `derived_from:` matches some producer's `produces:`. When the rename lands, either (a) the consumers' contracts haven't been updated and the lint fails BLOCKING the commit, or (b) the consumers' contracts HAVE been updated and the producer-consumer pair commits together. There is no silent path.

**MAST mode caught**: FM-1.4 (loss of conversation history across handoffs), FM-2.4 (information withholding).

### Scenario B — The Metadata Schema Drift (Verification failure)

**Setup**: `ui-create-scribble` adds a new `phase_2_review_notes:` field to `metadata.yaml` when the auto-reviewer adds promotion notes. The new field is optional (Phase 2 may not produce it). The skill's SKILL.md gets a one-line update.

**What happens today**: `ui-verify-flutter` reads `metadata.yaml` looking for `status: approved`. The new field is harmless — until `ui-improve-flutter` (which runs LATER, on a developer's request) reads `metadata.yaml` to find the "approved version folder." `ui-improve-flutter` was authored before `phase_2_review_notes:` existed; its YAML parser fails on the unexpected field because it uses strict mode. The skill exits with a Python traceback the developer cannot interpret without reading the parser source. **The skill that broke is `ui-improve-flutter`, which had no part in the change**.

**What the mechanism catches**: `.claude/schemas/scribble_metadata.yaml` defines `metadata.yaml`'s shape. The schema declares `phase_2_review_notes:` as optional from the moment it's added. Every consumer's pre-condition check (5-line bash) validates against the schema, not against its own internal parser assumptions. When `ui-improve-flutter` is invoked, its pre-check loads the schema, validates `metadata.yaml` against it, and either succeeds (the schema knows about the new field) or fails with a SPECIFIC error message ("metadata.yaml has key `phase_2_review_notes:` not declared in schema; bump `.claude/schemas/scribble_metadata.yaml` and re-run").

**MAST mode caught**: FM-3.2 (no or incomplete verification), FM-2.5 (ignored other agent's input). The 5-line pre-check is the verification leg PwC's 7× number argues for.

### Scenario C — The Silent Sub-Skill Wrapper (Skill granularity failure)

**Setup**: We adopt the SCRIBBLE-SPLIT proposal as-stated in file 09 §7.1 and create `ui-scribble-generate` as its own skill. The skill body is 60 lines: it loads context, spawns a `scribble-generator` agent with an inlined prompt, waits for the agent, returns the file path.

**What happens later**: A developer wants to tune the generator's prompt. They search for "design system rules" in `.claude/skills/` and find the prompt in `ui-scribble-generate/SKILL.md`. They edit it. Six weeks later, a different developer wants to add an inspiration-input field. They search the same way and find the same prompt — but the `scribble-generator` agent description also has a copy (because file 13 §5 said agents carry their own vocabulary). Now there are two prompts, and the agent's copy wins at runtime because that's what Claude reads when invoking the agent. **The change in `ui-scribble-generate/SKILL.md` had no effect**, but the developer doesn't know that until weeks later when verification surfaces a mismatch.

**What the rubric (§3 below) catches**: applying the 4-signal binary rubric to `ui-scribble-generate` returns 1/4 (file 02 §Q3). The skill fails the rubric → it should be the `scribble-generator` agent invoked directly by the parent (`ui-scribble-iterate`), with the prompt living in *one* place. The sub-skill exists only as a maintenance trap.

**MAST mode caught**: FM-1.2 (disobey role specification — the agent's prompt diverged from its declared sub-skill description), Hermify-style "rebuilding CrewAI inside an agent" anti-pattern (file 02 §Q3).

---

## §3 — Sub-skill-vs-agent rubric: applied to SCRIBBLE-SPLIT

### 3.1 The rubric (from file 02 §Q3, synthesized from LangGraph + CrewAI + Hermify)

A candidate becomes a **sub-skill** if **≥ 2 of these 4 signals are YES**. Otherwise it should be an **agent invoked by the parent skill**, OR an **inline phase** of the parent.

| # | Signal | Why it matters |
|---|---|---|
| **S1** | Can this be invoked outside the parent flow without manufacturing context? | If yes, it deserves its own skill identity for reuse. If no, it's a phase, not a skill. |
| **S2** | Does it coordinate ≥ 2 agents the parent doesn't already see? | Real orchestration value. One agent + wait = a wrapper, not orchestration. |
| **S3** | Is the boundary a natural human-review or decision point? | If yes, the skill identity helps humans pause/resume/approve at the boundary. |
| **S4** | Does a file-based artifact cross the boundary (producer writes, consumer reads)? | If yes, splitting is cheap because the file is the contract. If no, the split requires in-memory state-passing — expensive and brittle. |

### 3.2 Applied to file 09 §7.1's 4-sub-skill proposal

| Candidate sub-skill | S1 | S2 | S3 | S4 | Score | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|---|
| `ui-scribble-generate` (Phase 0 + Phase 1) | NO¹ | NO² | NO³ | YES | **1/4** | **Replace with `scribble-generator` agent.** No orchestration value as a skill. |
| `ui-scribble-auto-review` (Phase 2 + component auto-promote) | NO¹ | YES⁴ | YES⁵ | YES | **3/4** | **Split into a sub-skill.** Real fan-out + natural review point. |
| `ui-scribble-feedback-classify` (Phase 4) | NO¹ | YES⁶ | YES⁵ | YES | **3/4** | **Split into a sub-skill.** Multi-agent classification + natural decision point (which rules to update). |
| `ui-scribble-approve-handoff` (Phase 5 + 5a) | NO¹ | NO² | YES⁷ | YES | **2/4** | **Borderline: lean split.** The handoff is itself the contract artifact (file 02 §Q4 PRINCE2 framing) — splitting makes the contract more legible to consumers. |

¹ All four phases depend on iteration state (current version, prior feedback) held by the parent orchestrator (`ui-scribble-iterate`); none can be invoked standalone without manufacturing that context.
² Single agent (the generator / handoff emitter respectively). Wait-for-agent ≠ orchestration.
³ Phase 1 → Phase 2 transition is not a natural human pause; it's an auto-flow inside one iteration.
⁴ Phase 2 spawns auto-reviewer + ux-protocol-reviewer + persona-embodiment-reviewer (Q1-AGENTS bundle); 3-way fan-out.
⁵ Auto-review and feedback-classify produce structured outputs (`auto_review_report.md`, `classifications.yaml`) that the developer reviews before the next version generates.
⁶ Feedback-classify spawns classifier agents AND invokes downstream skills (`requ-explore`, `doc-update-guidelines`, `ux-validate-rule`) — orchestration value.
⁷ Approval is the canonical human decision point in the pipeline; the handoff emit is the contract-creation moment.

### 3.3 Net SCRIBBLE-SPLIT shape (revised from file 09 §7.1)

```
ui-scribble-iterate (thin orchestrator, owns the loop)
├── invokes agent → scribble-generator           (was: ui-scribble-generate sub-skill)
├── invokes sub-skill → ui-scribble-auto-review
│       ├── invokes agent → scribble-auto-reviewer
│       ├── invokes agent → scribble-ux-protocol-reviewer
│       └── invokes agent → persona-embodiment-reviewer
├── invokes sub-skill → ui-scribble-feedback-classify
│       ├── invokes agent → scribble-feedback-classifier
│       ├── may invoke skill → requ-explore (revision-request triggered)
│       ├── may invoke skill → doc-update-guidelines
│       └── may invoke skill → ux-validate-rule
└── invokes sub-skill → ui-scribble-approve-handoff
        └── invokes agent → scribble-handoff-emitter
```

**Net change vs file 09 §7.1**: 4 sub-skills → 3 sub-skills + 1 agent (collapsed `ui-scribble-generate` per Scenario C). The total surface to author is unchanged in count (3 sub-skills + ~5 agents), but the alignment is correct: each entity earns its category by the rubric.

### 3.4 The rubric must live in TWO skills, not one

File 08 §3.5 proposed adding the rubric to `claude-create-skill` only. Round-2 evidence (file 02 §Q3, Hermify's bidirectional warning) shows the rubric is a **recurring** check, not a one-shot. When `claude-modify-skill` is invoked to add a phase to an existing skill, the rubric should fire again — because the new phase might tip a borderline-2/4 into a clear-3/4 (split) OR drop a 2/4 to 1/4 (collapse into the parent).

**Action for Round 3**: codify the rubric in `claude-create-skill` SKILL.md as the "Phase split decision" sub-section, AND reference it from `claude-modify-skill` SKILL.md with a "Re-evaluate phase split" sub-step.

---

## §4 — What Round 2 must prototype

Round 1 ratifies the design direction; Round 2 validates it by prototyping on real skills.

### Required Round 2 deliverables (from goal.md §"Acceptance Criteria")

1. **Concrete `contract.yaml` on ≥2 representative skills** with YAML that compiles (correct keys, no placeholders). Recommended skills:
   - **`ui-create-scribble`** — the catalyst pipeline; demonstrates the multi-output, conditional-output case (e.g. `flutter_handoff.yaml` only on approval)
   - **`code-simple`** — demonstrates the typical implementer skill consuming `goal.md` + scribble + doc/ guidelines
   - **`task-create`** (optional 3rd) — demonstrates the producer of the `goal.md` shared artifact

2. **≤80-line lint script** at `scripts/quality/check_skill_contracts.py` that catches ≥1 real interface violation. Suggested violation: introduce a literal-path discrepancy between `code-simple/contract.yaml.derived_from:` and `ui-create-scribble/contract.yaml.produces:` (e.g. one says `scribbles/v{n}/` and the other says `scribbles/iteration_{n}/`) and show the lint catches it with a specific actionable error message.

3. **One `.claude/schemas/<artifact>.yaml`** (suggested: `scribble_metadata.yaml`) demonstrating the schema-source-of-truth pattern + DELETING the duplicate prose in the folder-root README (file 14 §4.4 cleanup obligation).

4. **One example `revision_target.yaml`** inside a hypothetical `pending_feedback/<task>/` showing the `responder_required:` discriminator pattern from §1.2.

### What Round 2 must NOT do

- Don't add the lint to `verify-quality` yet (that's a separate rollout task)
- Don't migrate any existing skill beyond the 2-3 prototypes
- Don't author the rubric inside `claude-create-skill` (that's a Round 3 + rollout-task deliverable)

---

## §5 — Open questions for Round 3

Round 3 resolves these in light of Round 2's prototype results:

1. **Migration sequence**: family-by-family (ui-* first, then code-*, then task-*)? Or skill-by-skill ordered by inbound dependency count? Round 2's lint script will reveal which skills' contracts are most-referenced.
2. **`contract_version: 0` (opt-out) longevity**: never sunset, OR set a sunset target like "30 days after the first 3 skill families adopt"? Trade-off: short sunset → migration pressure, long sunset → safe but creates a permanently-bifurcated codebase.
3. **Schema location convention**: `.claude/schemas/<artifact>.yaml` (file 08 §3.2) — confirmed correct per Round 1, but Round 3 should specify the indexing/discovery rule (how a contract.yaml references a schema; how a developer finds the right schema).
4. **Whether to emit a `claude-modify-agent` skill** (R9 gap-fill from file 10). Round 2's prototype phase will tell us whether agent-prompt edits are frequent enough to warrant the skill.
5. **Whether REQ-PROC-044 needs new ACs**. The 6 ACs (AC-01..AC-06) collectively cover declaration, traceability, extensibility, robustness, determinism, and authoritative documentation. Round 3 produces a per-AC mapping; if any AC is unsatisfiable by the proposed mechanism, it gets flagged as a follow-up `requ-explore`.
6. **Bidirectional channel structural details** beyond §1.2: file naming convention, escalation cycle counting, exact discriminator enum values.

---

## §6 — Updated cycle plan (carries over from kickoff)

| Round | Status | Next |
|---|---|---|
| Round 1 | ✅ Complete (this file) | — |
| Round 2 | Pending | Spawn `implementation-engineer` agent (background, ~10-20 min); prototype the contract.yaml + lint + schema + revision_target.yaml |
| Round 3 | Pending | Resolve 6 OPEN decisions after Round 2 returns |
| Phase 3 | Pending | Present synthesis to user |
| Phase 4 | Pending | Create follow-up tasks; tick ACs; task-complete |
