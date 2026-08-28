---
requirement: REQ-PROC-068
requirements_version: 3a51041e
created: 2026-07-09
mode: full
---

# Task Creation Plan — Build-Mode Resumability (REQ-PROC-068 AC-13..17 + REQ-PROC-071-06 AC-08)

Design source (developer-approved SOL-02): `2026-07-09_006_synthesis_v2.md`.

## Phase 1.5 cross-ref classifications (all IGNORE — keyword false positives, waiver per §1.5.5)
- REQ-FUNC-007-11 (on-device transcription resumable *download*) — ignore: unrelated "resumable" sense.
- REQ-NFUNC-011 (therapist `plan_templates_orchestrator.dart` widget) — ignore: UI widget, not the automation orchestrator.
- REQ-NFUNC-022 / -01 (carbon-efficiency gate deferring the orchestrator) — ignore: sustainability gate, different concern.
No cross-refs applied.

## Phase 1.5b EGP gate: 0 missing dispositions (pass). AC-14 is consequence HIGH → auto-accepted (automated mode).

## Deviation from automated-mode orchestration pattern (documented)
Phase 5 automated default is the deferred orchestration-task pattern. Deviated: concrete tasks are created
now because the parent explore task TASK-PROC-068-20 (AC-07) requires the concrete impl-task IDs to populate
TASK-PROC-068-12's `after:` — a deferred creator cannot supply those IDs at 068-20 completion.

## Tasks

- task_name: "build.py resumable wrapper — parent-dir git-init workspace, completion-gated harvest, completion-predicate seam"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "3a51041e"
  covers_acs: [AC-13, AC-14, AC-17]
  effort: L
  layer: "scripts/playground (Python, non-code)"
  after: []
  task_type: impl
  opus_recommended: true
  implementation_notes: |
    Change scripts/playground/build.py::run_build_mode so the isolated deployed copy is created via the
    EXISTING parent-dir git-init workspace convention (scripts/playground/workspace.py::create_workspace +
    init_workspace_git, out-of-project root resolved by scripts/dev_env/worktree_root.py + worktree.config.json)
    instead of tempfile.mkdtemp() [AC-13]. Gate the harvest+discard: harvest_authored + workspace teardown run
    ONLY when an explicit completion predicate over the copy returns complete AND result.succeeded AND
    result.reason=='exited'; on ANY non-complete termination preserve the copy and skip harvest entirely —
    preserve-by-default, discard-only-on-verified-complete, skip-harvest-on-incomplete [AC-14]. Write the
    registry status=running + durable copy path BEFORE launch (a tree-wide limit can kill the wrapper before
    the gate — ADV-synthesize-gate-02). Parameterize the wrapper by an INJECTED completion predicate so
    layer-derivation (ChainState complete) is one instance, not the hard-coded case [AC-17]. Preserve harvest
    snapshot-diff scoping (REQ-PROC-068-19) and never git-reset (C1). FIRST PHASE: read
    plans_and_protocols/2026-07-09_006_synthesis_v2.md §SP-1/SP-3 for design fidelity; AC text is authoritative.
    AC-14 is HIGH-consequence (archetype F) — its verification (folded into the next task) must use a
    subject-independent oracle: a real interrupted run observed to preserve+skip, and a real completed run
    observed to harvest+discard (real-artifact worktree diff, not f(x)==x).

- task_name: "build-mode run registry + playground-build-resume skill + dynamic-poll completion wait + usage-limit freeze"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "3a51041e"
  covers_acs: [AC-15, AC-16]
  effort: L
  layer: "scripts/playground + .claude/skills (non-code)"
  after: ["<T1>"]
  task_type: impl
  opus_recommended: true
  implementation_notes: |
    Add a host-side run registry (records durable copy path, derivation/child session identity, jsonl dir,
    baseline snapshot ref, status running|paused|complete) so a cold session discovers an in-progress run and
    re-attaches — re-launching the contained child (inner autorun resumes from ChainState) while SKIPPING
    deploy/seed/snapshot and reusing the preserved baseline; hung-detection watches the recorded child session
    UUID's JSONL (ADV-1/ADV-2) [AC-15]. Add a `playground-build-resume` control skill mirroring
    layer-derivation-resume (reads the registry, re-attaches; no human path-threading). Usage-limit handling
    requires NO automation-orchestrator modification: the shared account window freezes nested outer+inner
    orchestrators together and each resumes after reset (verified: orchestrate.py rate_limit_sleep). The outer
    run learns of completion by self-polling the completion signal at an interval that scales with estimated
    remaining work (remaining ChainState units), with a sane floor/ceiling — not a fixed 15 min [AC-16]. No
    explicit external pause in v1; the autorun stop signal (stop_requested in automation/state.json) is the
    documented extension point. Under automated orchestration the deployed run is a resumable in_progress task.
    VERIFICATION (folded — 068 has <3 impl tasks): after this task, confirm all of AC-13..AC-17 end-to-end via
    a real build-mode run: copy created out-of-project as a git repo (AC-13), interrupted run preserves+skips
    harvest while a completed run harvests+discards (AC-14, subject-independent real-artifact oracle), a cold
    session re-attaches from the registry without re-deploy (AC-15), a usage-limit run resumes with no
    orchestrator change (AC-16), and the completion predicate is injected not hard-coded (AC-17). Covers the
    verification of AC-13..AC-17.
    FIRST PHASE: read 2026-07-09_006_synthesis_v2.md §SP-2/SP-4 for design fidelity; AC text is authoritative.

- task_name: "Validate deployed cross-session derivation resumability under a real shared usage-limit inside the jail"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_layer_derivation/feat_backfill_orchestration/requirements.md"
  requirements_version: "3a51041e"
  covers_acs: [AC-08]
  effort: L
  layer: "scripts/playground + integration (non-code)"
  after: ["<T1>", "<T2>"]
  task_type: impl
  opus_recommended: true
  implementation_notes: |
    Prove REQ-PROC-071-06 AC-08: a real derivation chain running inside a deployed isolated copy, interrupted
    mid-chain by a session termination AND by a real shared usage-limit, resumes the SAME chain in a later
    session from its committed units (never restarting, never losing completed units). This closes the
    now-central uncertainty U2 — TASK-PROC-068-18 used a deterministic child that could not hit a limit, so the
    interrupted-mid-chain deployed case has never been exercised. AC-08 is EGP-bearing (archetype F,
    consequence MEDIUM = computed floor). Oracle-independence declaration (Layer 0): (1) independent of the
    subject — the expected resumed-from unit is the last committed unit in the pre-interruption ChainState/git
    log, not re-derived from the run's own output; (2) referent = the externally-stated goal "resume the same
    chain from committed progress" — checked against the real copy's git commit history (real-artifact worktree
    diff) or a metamorphic relation (units_done after resume ⊇ units_done before interruption); (3) exercises
    the real inner autorun end-to-end, not a stub. Depends on the build.py wrapper (T1) + registry/resume (T2).

## Coverage Matrix

| AC | Task(s) | Requirement | Package |
|----|---------|-------------|---------|
| REQ-PROC-068 AC-13 | T1 | REQ-PROC-068 | — (process) |
| REQ-PROC-068 AC-14 | T1 (+ T2 verification) | REQ-PROC-068 | — |
| REQ-PROC-068 AC-15 | T2 | REQ-PROC-068 | — |
| REQ-PROC-068 AC-16 | T2 | REQ-PROC-068 | — |
| REQ-PROC-068 AC-17 | T1 (+ T2 verification) | REQ-PROC-068 | — |
| REQ-PROC-071-06 AC-08 | T3 | REQ-PROC-071-06 | — |

Verification: REQ-PROC-068 has 2 impl tasks (<3) → verification section folded into T2 (covers AC-13..17
end-to-end). REQ-PROC-071-06 AC-08 verification IS T3 (the real-limit deployed-resumability proof).
