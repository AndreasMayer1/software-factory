---
requirement: REQ-PROC-068
requirements_version: edddd25f
created: 2026-07-17
mode: full
derived_by: TASK-PROC-068-29
---

# Task Creation Plan for REQ-PROC-068 — Persistent Harness Git (AC-20, AC-21, reworded AC-11)

Decomposition of the persistent-harness-git mechanism fixed by TASK-PROC-068-28
(protocol: `tasks/2026-07-17_explore_persistent-harness-git (completed)/plans_and_protocols/2026-07-17_01_protocol_persistent-harness-git-design.md`).
Design is closed; this plan only decomposes/sizes/wires. No design re-opened.

## Gate results (Phase 1.5 / 1.5b)

- **EGP disposition gate (1.5b)**: PASS — 0 missing dispositions, 0 invalid consequences
  (`check_egp_audit.py`). AC-11/20/21 show no confirmed≠auto mismatch. The 11 remaining
  mismatches are pre-existing (AC-01–10, AC-17 — self-certifiable/not-bearing) and advisory
  only (not blocking under AC-23).
- **HIGH-consequence approval (1.5b.5)**: AC-20 is `consequence: HIGH` (archetype F). Automated
  mode → auto-accepted; recorded in the verify task's implementation_notes.
- **Cross-ref gate (1.5)**: WAIVED (1.5.5). Auto-derived term "offline" produced only unrelated
  privacy/data-transfer false-positives. Domain terms (playground/harness/harvest) yielded only
  keyword co-mentions across the factory-extraction epic family; the genuinely-coupled
  requirements — REQ-PROC-066 (parent epic), REQ-PROC-071-06 (layer-derivation) — are already
  cited in this requirement's `## Dependencies`/`## References` (curated by TASK-PROC-068-28 at
  commit edddd25f). No candidate is a *missing hard dependency* of the persistent-git ACs
  (AC-11/20/21), whose mechanism is self-contained in `scripts/playground/`. Requirement uses
  `## Dependencies`/`## References` prose rather than a `## Related Requirements` section, so the
  script's prose-based filter could not subtract the already-present links.

## Code anchors (verified in tree)

- `scripts/playground/workspace.py:136` `init_workspace_git()` — the maintenance `git init` baseline.
- `scripts/playground/build.py:570` Step 3 — calls the git-init baseline (maintenance-mode deploy).
- `scripts/playground/build.py:393 harvest_authored` / `:666 _gate_harvest` — the COMPLETE/harvest
  branch (persist-on-harvest + compaction hook). Same branch TASK-PROC-068-30 edits.
- `scripts/playground/deploy.py:127 _SUBFOLDER_EXCLUDES` — the exclude set.
- `scripts/playground/run_skeleton.py` — TEST-mode throwaway git init; UNCHANGED per design.

## Concurrency constraint (goal AC + override note)

Every emitted impl task that edits `build.py`'s COMPLETE/harvest branch carries
`after: [TASK-PROC-068-30]` (068-27's build.py-mechanism impl task) so the shared branch is never
edited concurrently. Task-2 additionally follows Task-1 (both touch the harvest region + share the
bundle mechanism).

## Tasks

- task_name: "persistent-harness-git-restore-persist-bundle"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "edddd25f"
  covers_acs: [AC-20, AC-21]
  effort: M
  layer: process/scripts (scripts/playground)
  after: [TASK-PROC-068-30]
  task_type: impl
  target_package: ""
  egp:
    - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
    - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
  consequence: HIGH
  opus_recommended: false
  implementation_notes: >
    Maintenance-mode (build/maintain) persistent git via a git bundle. Replace the fresh
    `git init` baseline for maintenance-mode runs: (1) RESTORE-ON-DEPLOY — the deployed copy
    initializes its git repository by restoring from the harness's persisted bundle (kept with
    the harness in the container project) instead of an empty repo (`workspace.py init_workspace_git`
    + `build.py:570` Step 3, maintenance path only); (2) PERSIST-ON-HARVEST — on harvest
    (build.py COMPLETE branch, `_gate_harvest`/`harvest_authored`) export the copy's advanced
    history back to the persisted bundle and store it with the harness. TEST mode (run_skeleton.py)
    KEEPS the throwaway `git init` — do NOT touch it (its clean-reset contract AC-07 is correct).
    AC-21 (encapsulation): ALL of this handling lives entirely inside scripts/playground/ — no
    other factory mechanism may grow harness-specific handling. Edits build.py's COMPLETE/harvest
    branch → after: [TASK-PROC-068-30]. Route scripts/** edits via claude-write-script; run Python
    gates (scripts/quality/check_python_gates.sh). RECURSIVE OVERRIDE RULE: append this task to
    .claude/task_ordering_priority_override.txt on creation.

- task_name: "persistent-harness-git-harvest-compaction"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "edddd25f"
  covers_acs: [AC-20, AC-21]
  effort: M
  layer: process/scripts (scripts/playground)
  after: [TASK-PROC-068-30]
  task_type: impl
  target_package: ""
  egp:
    - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
    - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
  consequence: HIGH
  opus_recommended: false
  implementation_notes: >
    Harvest-time compaction policy on the persist side (builds on the restore/persist bundle from
    task "persistent-harness-git-restore-persist-bundle"). PRESERVE every referenced commit — any
    commit a harvested artifact's provenance field points to (a materialization artifact's
    provenance commit, a task's pinned requirements version) stays reachable with a STABLE HASH
    forever. SQUASH only unreferenced intermediate commits to bound bundle growth. Prior runs'
    persisted commits are IMMUTABLE — a later run's compaction may only append + selectively squash
    unreferenced gaps, never rewrite already-persisted commits (the backward-reference constraint:
    a global squash-and-rewrite would silently break every existing backward reference). Test mode
    carries no persisted history (nothing to compact). AC-21 (encapsulation): handling stays inside
    scripts/playground/. Edits build.py's COMPLETE/harvest branch → after: [TASK-PROC-068-30]; also
    ADD after: [<restore-persist-bundle task id>] at creation (shared harvest region + depends on the
    persist mechanism; avoids concurrent edit). Route scripts/** edits via claude-write-script; run
    Python gates. RECURSIVE OVERRIDE RULE: append to task_ordering_priority_override.txt on creation.

- task_name: "playground-deploy-exclude-product-materialization"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "edddd25f"
  covers_acs: [AC-11]
  effort: XS
  layer: process/scripts (scripts/playground)
  after: []
  task_type: impl
  target_package: ""
  egp:
    - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data" }
  consequence: MEDIUM
  opus_recommended: false
  implementation_notes: >
    Trivial fix surfaced during the closed exploration (TASK-PROC-068-28 protocol §Follow-on 3):
    add `requirements_user_needs/product_materialization` to `_SUBFOLDER_EXCLUDES` in
    `scripts/playground/deploy.py:127` so the transient factory deploy does NOT clobber the harness's
    own materialization provenance — realizing the AC-11 reword's tail (the harness retains its own
    factory-runtime provenance grounding its product definition as project data of the standalone
    harness). Independent of build.py's COMPLETE branch → after: [] (goal AC explicitly permits).
    Route the deploy.py edit via claude-write-script; run Python gates. RECURSIVE OVERRIDE RULE:
    append to task_ordering_priority_override.txt on creation.

- task_name: "verify-persistent-harness-git"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "edddd25f"
  covers_acs: [AC-11, AC-20, AC-21]
  effort: M
  layer: process/scripts (verification)
  after: [<restore-persist-bundle>, <harvest-compaction>, <deploy-exclude>]
  task_type: verify
  target_package: ""
  egp:
    - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance runs observed to keep earlier runs' referenced commits reachable in the harness git after restore" }
    - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
    - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to retain its own factory-runtime provenance as project data in test_harness_app/" }
  consequence: HIGH
  opus_recommended: false
  implementation_notes: >
    Verification of the persistent-harness-git mechanism. HIGH-consequence AC (auto-accepted at
    the 1.5b.5 gate, automated mode): AC-20 (archetype F, referent = a real sequence of maintenance
    runs keeping earlier runs' referenced commits reachable after restore-from-persisted-history).
    ORACLE-INDEPENDENCE DECLARATION (AC-02): expected values come from REAL deploy-run-harvest
    behaviour, NOT from the persist code's own output.
    (1) AC-20 [F, HIGH] — run a real sequence of ≥2 maintenance runs; a provenance commit a first
        run records must still be reachable (stable hash) in a later run's git after
        restore-from-persisted-bundle. Metamorphic relation allowed (F): compaction preserves
        referenced-commit reachability across runs; unreferenced intermediates may be squashed;
        prior runs' persisted commits are unchanged (immutable). Exercise the load-bearing
        restore/persist/compaction path, not a stub.
    (2) AC-11 [F, MEDIUM] — a real build/maintain run observed to retain the harness's own
        factory-runtime provenance (ideation index + ledger backing a derived decision) as project
        data in test_harness_app/ after harvest, with transient factory machinery absent.
    (3) AC-21 [X, MEDIUM] — coherence/absence check: grep/diff across all NON-playground factory
        mechanisms (skills, scripts outside scripts/playground/, quality gates, orchestration) to
        confirm NONE carries harness-specific handling — every other mechanism operates on the
        harness exactly as on any real project. Real-artifact absence check, not self-derived.
    consequence: HIGH = gate-computed governing floor (max of covered ACs), never self-rated.
    RECURSIVE OVERRIDE RULE: append to task_ordering_priority_override.txt on creation.

## Coverage Matrix

| AC | Task(s) | Package |
|----|---------|---------|
| AC-11 | playground-deploy-exclude-product-materialization, verify-persistent-harness-git | (none — process) |
| AC-20 | persistent-harness-git-restore-persist-bundle, persistent-harness-git-harvest-compaction, verify-persistent-harness-git | (none — process) |
| AC-21 | persistent-harness-git-restore-persist-bundle, persistent-harness-git-harvest-compaction, verify-persistent-harness-git | (none — process) |

100% of the three in-scope ACs covered. Separate verification task present (≥ 3 impl tasks → mandatory).

## Validation checks

- 100% AC coverage of the in-scope ACs (AC-11/20/21): PASS.
- ≥ 3 impl tasks (3) → separate verification task present: PASS.
- No circular dependencies: chain is 068-30 → {task1} → {task2}; task3 independent; verify after all three. Acyclic.
- Every task has sizing signals (effort + egp + consequence): PASS.
- Every EGP-bearing AC has a covering verification task with the AC-02 oracle-independence declaration: PASS (verify task).
- Ideation-decision respect (AC-22 of the skill): the plan respects the TASK-PROC-068-28 design's
  phasing (restore/persist → compaction), sequencing (COMPLETE-branch tasks after 068-30), and scope
  (test mode excluded; no provenance-contract change). PASS.
