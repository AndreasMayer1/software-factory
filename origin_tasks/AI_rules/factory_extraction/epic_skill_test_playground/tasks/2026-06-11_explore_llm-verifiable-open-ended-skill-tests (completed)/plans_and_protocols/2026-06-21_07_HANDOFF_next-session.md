# 🛑 SESSION HANDOFF — TASK-PROC-068-01 — READ THIS FIRST, IN FULL

> **You are the resuming session for TASK-PROC-068-01.** This file is the latest protocol; the
> file-based-memory rule (CLAUDE.md §1) requires you to read `goal.md` + the latest protocol before
> doing anything. **Do not write a requirement, edit any synthesis file, answer the developer, or
> call any skill until you have completed the MANDATORY READ GATE below.** If you skip it you will
> re-derive decisions already made, reintroduce staleness already fixed, or contradict the
> developer's explicit choices. Stop and read.

---

## ✅ MANDATORY READ GATE (do these in order — do not skip, do not skim)

1. **`CLAUDE.md`** (repo root) — the constitution. Note: automated-mode rules, the
   requirements-vs-tasks separation, depth-1 agent topology, and the "search-shaped leaves set
   `model:` explicitly" rule (a `PreToolUse` hook now nudges this).
2. **The `requ-explore` skill** — this task is `type: explore` + `writes_requirements: true`; that
   skill is the governing workflow for converging to the requirement.
3. **`goal.md`** (this task folder) — the **immutable objective + acceptance criteria**. Note ACs 5
   & 6 require *developer approval* of the synthesis and a stated next action.
4. **`plans_and_protocols/2026-06-21_04_synthesis-r3_capability-testing-consolidated.md`** — **THE
   CONCEPT. Read it in full.** This single file is the source of truth; it **supersedes the scope**
   of r1 (`…_01_…`) and r2 (`…_03_…`). It contains: problem shape (§1), boundaries (§2), the unit
   = *any governed instruction artifact* (§3), constraints (§4), embedding points (§5), reuse map
   (§6), the full mechanism (§7: L1–L4, descriptor §7.2, run model §7.4, judge calibration §7.5,
   regression gate §7.6, modify case §7.7, behavioural-contract/chain tier §7.8, isolation §7.9,
   testability+lifecycle §7.10), worked ideation instance (§8), honest limits (§9), generality
   (§10), **requirement architecture + the open forks Q-A..Q-E (§11)**, the iterative-resolution
   trail (§12, 12 iterations), extraction alignment (§13), and **§14 Prerequisites (current vs.
   target state)**.

**Read if you need the "why" behind a decision (not required to act):**
5. `…_05_blindspots_capability-testing-critique.md` — my own adversarial critique (B1–B3, G1–G3,
   D1–D4, R1–R2).
6. `…_06_adversarial-validation_synthesis-r3-capability-testing.md` — the developer-run external
   validation (han-adversarial-validator). All its findings were **verified true and folded in**
   (see §12 Iteration 12). Do not re-litigate; it is closed.
7. `…_02_external_skill-evaluation-prior-art.md` (lens reading) + `sources/` (verbatim originals:
   agentskills.io page + 21 skill-creator plugin files, MIT). The raw originals exist so future
   iterations can be checked against the unfiltered source.

---

## WHERE THINGS STAND (one paragraph)

The concept is **fully designed, iterated 12×, and adversarially validated** — it is ready to
converge. The deliverable that remains is **authoring the requirement(s)** per §11, *but* the §11
forks (Q-A..Q-E) are **developer decisions** and must be confirmed before you write anything. The
concept is the WHAT; it deliberately defers the substrate HOW to the §14 prerequisites.

## DECIDED THIS SESSION — DO NOT REOPEN OR CONTRADICT
- **Unit boundary = ANY governed instruction artifact** (skills, agents, CLAUDE.md, ordering-rules,
  orchestrator contract) — not just skills/agents. (developer decision)
- **Regression = old-version vs new-version blind A/B** — NOT skill-creator's no-skill baseline.
- **The Capability-Test Descriptor is authored INLINE at create** (author knows intent best); only
  the baseline run + improve loop defers to a task.
- **Cost = net human time saved, not apparatus size** — maximal automated catching is the goal;
  breadth is justified by time saved (the old "too big" worry R1 is *refuted*, not open).
- Test definitions live in the **product tree** at `test_harness_app/factory_tests/<capability>/`
  (NOT under `.claude/`).
- A soft `PreToolUse` hook (`pre_agent_model_reminder.sh`) was added + committed this session.

## OPEN — NEEDS THE DEVELOPER (do not auto-decide; if automated, use `pending_feedback`)
- **§11 Q-A** requirement home/scope · **Q-B** feature name · **Q-C** EGP coupling binding vs
  recommended · **Q-D** adoption depth · **Q-E** next action (author now / also create impl+adoption
  tasks / stop at synthesis).

## HARD RULES YOU MUST ENFORCE WHEN YOU CONVERGE
1. **§14 prerequisites are DEPENDENCIES, not assumptions.** The requirement must *name* P1 (harness
   not yet a factory project, AC-01 unchecked), P2 (deploy/run/reset mechanism undesigned —
   TASK-PROC-066-03 deferred it), P3 (tested capabilities lack EGP dispositions — 90 floor
   violations; `ideation-start` has no `contract.yaml`), P4 (HJR query interface 044-05 AC-04
   unbuilt), P5 (history-schema adapt) as `after:` edges on the **impl** tasks. Do **not** write a
   requirement that assumes them done. Do **not** stall the requirement waiting for them built
   (that inverts requirements-before-impl — see §12 Iteration 12 "Disagreement recorded").
2. **Do NOT reintroduce corrected overclaims:** the model-hook is *advisory* (not "enforces"); the
   `history.json` `model` field is *our adaptation* (not upstream); the execution substrate is
   *constraints-only* (not "already-designed"); testability is *contract-derivable only where
   declared, else author-declared* (not "mechanically derivable").
3. **Do NOT reintroduce staleness already audited out:** unit is not "skill|agent" in §2; test
   definitions are not in the capability tree; no "frozen reference run" (L3 compares versions
   fresh); the Q-A..Q-E forks live in §11 (not stranded after §13).
4. Requirement writing is governed by `requ-explore`. Requirements state end-state WHAT only — the
   substrate HOW belongs in the §14 prerequisite tasks.

## GIT / ENVIRONMENT STATE
- All task artifacts (this handoff, r2, r3, blindspots, adversarial validation, prior-art, `sources/`)
  are **committed** (an `explore` commit made at handoff time — the tree is clean for this task).
- **Stale `pending_feedback`:** `automation/pending_feedback/TASK-PROC-068-01/{question.md,answer.md}`
  are from an **early automated escalation (2026-06-11)** that is **superseded** by this interactive
  session. `is_awaiting_answer` returns 0 (it will NOT block you). **Ignore that question; do not act
  on its `answer.md`.** Reconcile/remove it when you next commit task work.
- Session model: this work was done on Opus (`opus_recommended: true`). Keep Opus for the
  requirement authoring.
- `goal.md` is already `status: in_progress` with `session_id` set — `task-start` is satisfied; you
  may proceed straight into `requ-explore` convergence (Phase 2 onward) once the developer answers §11.

## RECOMMENDED FIRST MESSAGE TO THE DEVELOPER
"I've read the r3 concept + §14 prerequisites. The design is converged and validated. Before I author
the requirement, confirm §11 Q-A..Q-E (home/scope, name, EGP-binding, adoption-depth, next-action)."
