---
task_id: TASK-PROC-068-16
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-07-02
started: 2026-07-03
completed: 2026-07-03
session_completed_at: 2026-07-03T15:44:08Z
expected_tool_calls: 45
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: []
egp:
  - { ac: AC-10, archetype: F, referent: "a real workflow run in which a contained child session runs a script-calling factory skill end-to-end inside the harness jail, completing without reaching the host factory tree" }
consequence: MEDIUM
scope_description: "Extend the harness deploy to copy the WHOLE factory (not just .claude/skills/) via a coarse TEMPORARY exclude rule; prove a contained child runs a script-calling skill end-to-end."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 7fe71c75
  file: ../requirements.md
session_id: 49f95366-4629-4938-81b9-2b2675477080
session_account: gmail2
---
# Goal: Extend the harness deploy to place the WHOLE factory into the harness

## Objective

Make the harness deploy copy the **whole factory** into `test_harness_app/`, not just `.claude/skills/`,
so a **contained** child session can invoke **any** factory skill end-to-end using only the deployed
contents — including skills that shell out to `scripts/` (which anchor on `script_dir.parent.parent` and
break today because the scripts tree is not deployed). This realizes **REQ-PROC-068 AC-10** (whole-factory
deploy) and unblocks the anchor/middle re-authoring chain (068-11 / 068-12) that must run factory skills
inside the jail.

## Requirements Summary

**REQ-PROC-068 AC-10** (the AC this task covers): *"A deploy places the whole factory into the harness so a
contained child session can invoke any factory skill end-to-end using only the deployed contents, with no
reach-back to the host factory tree."* "Whole factory" means everything the factory provides — **defined by
the factory itself, never by a file/artifact enumeration in the requirement**. AC-09 guarantees the child
*cannot* reach out; AC-10 guarantees it *need not*, because the deploy is complete.

For complete requirements at task creation time:
```
git show 7fe71c75:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

**Authoritative seed/spec** (read before implementing — full grounding, the developer-approved exclude set,
and the two entangled-tree risks):
`../2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`
§§ "Revision (2026-07-01, developer)" and "Pre-extraction exclude set — T-B impl guidance".

## Scope

### In Scope

1. Extend `scripts/playground/deploy.py` (and `reset`/`launch` as needed) so the deploy copies the whole
   factory into the harness using a **coarse, exclude-based** rule marked `// TEMPORARY:` (Python: a
   `# TEMPORARY:` first-line comment on the block). Exclude-based so factory growth is copied by default;
   **over-inclusion is safe** (harness is isolated + git-reset; cannot breach AC-09, which is about reaching
   *out*).
2. **Pre-extraction exclude set** (developer-approved 2026-07-01, **NON-exhaustive** — finalize in code):
   - Tooling/dotdirs: `.codegraph`, `.dart_tool`, `.idea`, `.roo_archive`, `.vscode`, `.VSCodeCounter`,
     `.git`, `.github`, `.githooks`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`
   - Platform/build/app assets: `android`, `assets`, `build`, `coverage`, `doc-temp`, `web`, `windows`,
     `Temp`, `figma`, `ios`, `linux`, `macos`, `packages` (pending endpoint confirm — treat excluded)
   - App code/tests: `lib`, `integration_test`, `test`, `test_driver`, `test_hive`
   - Other non-factory: `dev-analytics`, `releases`, `requirements_market_research`,
     `requirements_general_overview`
3. **Two risks that MUST be handled** (from the seed plan):
   - **`test_harness_app/` is the deploy TARGET, not factory content** — a naive `test*` glob would sweep it
     in; exclude it explicitly.
   - **Top-level exclusion is insufficient for the entangled trees** — `requirements_tasks/` (factory
     `process/AI_rules/**` vs app `functional/`+`non-functional/`), `requirements_user_needs/` (app), and
     `scripts/`/`doc/` (mixed) need **sub-folder** boundaries. Err toward copying (over-inclusion safe);
     extraction-synthesis §1a/§1b is a **non-authoritative** reference.
4. **Contained-child functional proof:** prove a `containment.py`-contained child session runs a
   **script-calling** skill end-to-end inside the jail — e.g. `generate_id_registry.py` (anchors on
   `script_dir.parent.parent`) — completing with **no** reach-back to the host factory tree. This is the
   AC-10 (EGP archetype F) referent.

### Out of Scope

- The post-extraction switchover (replace the temp exclude-rule with "copy whatever the extracted factory
  project provides") — a future REQ-PROC-066-scoped task, noted not created.
- A governed "what is the factory" manifest — deliberately NOT authored (would drift; the factory defines
  itself). The exclude list lives ONLY in this task's temporary code.
- Executing the downstream anchor/middle re-authoring (068-11 / 068-12).

## Acceptance Criteria

- [x] AC-10 — EGP: F (a real workflow run in which a contained child session runs a script-calling factory skill end-to-end inside the harness jail, completing without reaching the host factory tree); consequence: MEDIUM.
  Evidence: `plans_and_protocols/2026-07-03_02_evidence_ac10-functional-proof.md`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Root of the DEPLOY track (`after: []`) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-14](../2026-07-01_explore_whole-factory-deploy-ac%20(completed)/goal.md) | Predecessor — authored the AC-10 this task covers |
| [TASK-PROC-068-11](../2026-07-01_impl_harness-anchors-reauthor/goal.md) | Rewired to `after: [this task]`; unblocked once the deploy mechanism exists |

## Notes

**Standalone override (developer-authorized, interactive, 2026-07-02):** REQ-PROC-068 has uncovered ACs, so
`task-create` §3c would normally redirect to `task-derive-from-requ`. The developer explicitly authorized
standalone creation for this narrow DEPLOY-track task; redirect skipped by authorization, not by evasion.

**RECURSIVE OVERRIDE-REGISTRATION STANDING RULE (developer, 2026-07-01):** every task that creates other
tasks MUST (a) add the tasks it creates to `.claude/task_ordering_priority_override.txt`, and (b) carry this
same instruction forward into each created task's `goal.md`, so the rule propagates recursively down the
chain. If executing this task spawns any further tasks, apply both (a) and (b).
