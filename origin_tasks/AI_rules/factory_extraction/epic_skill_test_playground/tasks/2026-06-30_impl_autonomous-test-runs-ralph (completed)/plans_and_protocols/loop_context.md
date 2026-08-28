# Loop Context: PROC-068-playground-captest-loop

## Ridge (immutable — set once at loop start, never edited)
- end_goal: Autonomously discover, author, and run capability tests over the Skill-Test Playground harness, driving the harness's capability-testing coverage toward completeness using the verified ralph perpetuating mechanism (REQ-PROC-065-06) — with every oracle verdict consumed under the five mandatory ADVISORY caveats.
- termination_condition: No remaining in-scope, externally-justified capability-test work over the playground harness remains — i.e. `next_tasks.py` surfaces no unblocked candidate whose value is justified by an external signal (requirement priority, active release scope, or persona need) for capability-testing the playground — OR `iteration ≥ loop_ceiling`.
- scope: Autonomous capability-test runs over the `test_harness_app/` playground harness using the perpetuating-task-creation mechanism — discovering, authoring, and running capability tests that exercise factory skills/workflows against the harness and consume oracle verdicts. EXCLUDES: building the harness app's product content (the layer-derivation / factory-skill job — TASK-PROC-068-07), modifying the ralph or layer-derivation mechanisms themselves, and any work outside the playground harness.
- origin_task: TASK-PROC-068-08
- loop_ceiling: 12   # AC-17 — finite max chain length; default 12 (per-link authoring-accuracy decay curve)

## Basin (mutable — one row appended per iteration)
| iteration | task_id | outcome (follow-up id / no-op) | date | note |
|-----------|---------|--------------------------------|------|------|
| 1 | TASK-PROC-068-08 | TASK-PROC-068-10 | 2026-06-30 | loop start (T-orch3). Discovery: terminate-first (iter 1<12) → value-gate AUTHOR (verify gate 068-09 AC-2 requires ≥1 landed run) → authored iteration-2 follow-up TASK-PROC-068-10 |
| 2 | TASK-PROC-068-10 | NO-OP (loop ends) | 2026-06-30 | RAN one capability-test over harness FLOW-HARNESS-01: matched OLD(clean)/NEW(injected kind-#2 semantic-contradiction) pair, blind A/B Opus oracle, 2 swapped passes → detection 2/2, position-robust, mechanism-precise ($0.131, ~25s). Verdict consumed under 5 advisory caveats. Discovery: iter 2<12; value gate → NO-OP (apoptosis default) — the sole external signal (verify gate 068-09 AC-2 ≥1 run) is now satisfied by this run; next_tasks.py surfaces no other externally-justified candidate; more runs would be a forbidden self-referential coverage-delta. Loop ends gracefully. |
