# Protocol 19 — Resume: reconcile signals, park for re-derivation venue/cost decision

Agent: main session (automated), account gmail2, session 13c0851e-2d87-4b85-b986-7f1cee0ec4f8.

## State reconstructed on resume (from git + protocols 16–18)

- **Deps now satisfied** (were the parking reason): `after: [TASK-PROC-068-16, TASK-PROC-066-13]` — both
  `completed`. Task is genuinely unblocked for the first time.
- **HEAD harness anchors** (produced/reset by 066-13, commit `b31d4be2`): 2 personas (PERSONA-001 Theo /
  archivist, PERSONA-002 Maya / quick_logger) + 2 scenarios (SCEN-001-01, SCEN-002-01) + SCENARIO_INDEX.
  066-13 did the *factory/project-separation ("Layer F") correction* and **reset the fabricated
  `review_status: approved` → `draft`** (developer's checkpoint-18 point #3 — already handled).
- **These HEAD anchors are still structurally SHALLOW**: sections are the OLD set
  (Who / Jobs-to-Be-Done / Status Quo / Trigger / Barriers / Anti-Traits) — **no Driver–Context spine**
  (R0 Driver&Lens / R1 beyond-the-moment / R2 social field / T trajectory), no composite-archetype
  governor, no swap-test evidence tags. 066-13 corrected separation, NOT depth.
- **Working-tree state**: those 5 HEAD files are **deleted (uncommitted)** in the working tree — a stray
  pre-existing deletion from a prior session, NOT made by this session. All recoverable from HEAD
  (`git checkout HEAD -- test_harness_app/requirements_user_needs/...`). Nothing is lost. Left untouched
  this session (do not sweep pre-existing changes).

## The two authoritative signals

1. **Checkpoint-18 developer answer (2026-07-05)** — AC-4 = **No**. Re-derive both personas + both
   scenarios against the newly-deepened TASK-PROC-010-17 guidance (commit `5cb7e7f2`: Driver–Context
   spine, composite governor, instrument+swap-test, persona/scenario boundary), **via the real
   `ux-write-persona`/`ux-write-scenario` skills — "so the re-authoring is itself a live test that the
   new rules produce deeper anchors."** Re-present for AC-4 after re-derivation.
2. **goal.md `after`-note (2026-07-05, 066-07 closeout)** — "068-11's AC-4 gate must approve the
   corrected artifacts, not the uncorrected ones."

**Reconciliation**: no hard contradiction. Read (2) as a *sequencing/baseline* note (approve the
066-13-corrected baseline, not the pre-correction versions), and (1) as the *substance* still owed
(depth re-derivation on top of that corrected baseline). The corrected baseline is still shallow, so
presenting it for AC-4 as-is would just repeat the rejection.

## The only mechanism to author into the harness = playground containment

The `ux-*` skills read/write `requirements_user_needs/` (the FLUTTER tree, hardcoded). The harness tree
carries **no** README_3/4/CLAUDE.md of its own. The sanctioned path (built by this task, commit
`be270123`, exercised in protocols 13–16) is `scripts/playground/`: deploy the outer-repo guidance +
skills into an ephemeral **bwrap-jailed** sibling workspace, run a **nested `claude -p` child** that
executes the `ux-*` skills there, scoped-harvest personas/scenarios/SCENARIO_INDEX back into
`test_harness_app/`, destroy the workspace. Because deploy pulls from the outer HEAD (now containing
`5cb7e7f2`), a re-run would deploy the **deepened** guidance — exactly the developer's "live test".

**Cost/fragility (from protocol 16)**: prior child runs took ~5 min / ~$1.73 / 40 turns and **hit the
account session limit mid-run twice** (429). The child self-asserts its own approval (why 066-13 had to
reset it). It runs **unobserved** in automated mode.

## Why this session parks instead of firing the re-derivation autonomously

- The developer's **"live test"** framing implies they want to *observe* the re-authoring — an
  interactive venue. Automated mode runs the contained child unobserved and self-approving, defeating
  that intent.
- Autonomously firing an **expensive, repeatedly-rate-limited nested-`claude`** run is a cost /
  hard-to-reverse call that warrants explicit confirmation, not a self-authorized default.
- The reconciliation above is *my* reading; the developer should confirm before ~$2 + a scarce session
  window are spent on it.

Genuine human decision required → park via `pending_feedback` (exit 2). Not self-approving, not
completing, not firing the nested run. Task left `in_progress`.

## Decision requested (see question.md)

A) Run the contained re-derivation now, **automated/unobserved** (I harvest → reset self-approval to
   draft → park for AC-4); OR
B) Hand off to an **interactive** session so the developer watches the "live test"
   (`/autorun-resume-interactive TASK-PROC-068-11`); OR
C) Skip re-derivation — proceed to AC-4 review on the current 066-13-corrected (shallow) anchors as-is
   (I restore the 5 files from HEAD first).
