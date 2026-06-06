---
name: code-complex
description: End-to-end workflow for complex, multi-file architectural changes
tools: "*"
model: inherit
---

You orchestrate a complex task workflow from start to finish.

**User invokes**: "Use code-complex skill for [task name] in [path]"

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the task goal.md is missing or off-schema. (Skip only when bootstrapping a brand-new task that step 1 will create.)
```bash
GOAL_PATH="${1:?code-complex requires the task goal.md path}"
[ -f "${GOAL_PATH}" ] || { echo "ERR: missing goal.md at ${GOAL_PATH} — run task-create first (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${GOAL_PATH}" .claude/schemas/goal_metadata.yaml || exit 2
```

**You execute**:

1. **Setup**: Use task-create skill to initialize workspace (if not already done)

2. **Plan**: Spawn `architecture-advisor` agent. The agent's default model is opus (it does strategic planning). Implementation-engineer agents (spawned later) stay on sonnet.

   Agent tasks:
   - Reads goal.md + relevant doc/ guidelines
   - If task involves Presentation Layer: review `doc/presentation/design/persona_design_bridge.md` for persona trait-to-design mapping
   - If plan involves Presentation Layer changes affecting multiple personas: read `vcd:` YAML blocks for affected personas and flag any value conflicts in the plan document under section "Value Trade-offs Identified"

   **Sketch Gate (Presentation Layer)**:
   If task modifies Presentation Layer:
   1. If goal.md has `skip_scribble: true`: skip gate.
   2. Discover the scribble path — (a) read `[requirement]/requirements.md` for `feature_path`; if present, check `requirements_tasks/scribbles/<feature_path>/` for `status: approved` version; (b) otherwise search `find requirements_tasks/scribbles/ -name "metadata.yaml" | xargs grep -l "<REQ-ID>"` for the requirement ID; (c) legacy fallback: `[requirement]/scribbles/`. If no approved scribble: plan must include a `ui-scribble-iterate` step before implementation begins.
   3. If approved scribble exists:
      a. Read `flutter_handoff.yaml` in the approved version folder; locate the top-level `contract:` block (fields: `locked_in`, `re_derive`, `source`).
      b. Include in the implementation plan:
         - **LOCKED-IN** (`contract.locked_in` keys L1–L15): implement exactly as depicted — widget choices, screen list/order, copy text, information hierarchy, persona-sizing token references, navigation pattern, dialog pattern, component-library choices, design decisions, and accessibility intent.
         - **RE-DERIVE** (`contract.re_derive` keys D1–D8): derive from `doc/presentation/` and `tokens.json` — do NOT copy literal color values, exact token values, animations, responsive mechanics, focus order, BLoC wiring, or cross-persona constraints from the scribble.
      c. **Navigation graph** (AC-38): if `flutter_handoff.yaml` contains a `flow_navigation_files:` block, load each referenced `flow_navigation.yaml`. Include in the implementation plan: `edges[]` define the GoRouter routes or Navigator calls that must be present (implement navigation from declared edges, not by inferring from screen order); `escape_paths[]` define required back-navigation or cancel handling.
      d. Every implementation batch that touches Presentation files must note which contract side applies for each scribble element it references.
   - Analyzes codebase
   - Creates high-level plan in plans_and_protocols/ using claude-log skill (with agent ID)
   - **YAGNI scope gate**: before finalizing the plan, for each scope item beyond the task's ACs, cite ≥ 1 piece of real evidence (user-described need, named direct dependency, existing code path that breaks without it, or documented incident). Items lacking evidence go to `## Deferred (YAGNI)` in the plan document with a named reopen-when trigger (format: `### {item}` / `**Why deferred:** [missing evidence]` / `**Reopen when:** [named trigger]` / `**Source:** [origin]`). Apply Gate 2 — shape: prefer the strictly simpler version that satisfies the same evidence. User override: any single deferral can be overridden; note the rationale in the plan.
   - **Optional** (AC-07 / REQ-PROC-053): pre-warm `lookup_log.jsonl` by invoking `doc-lookup-dependencies` for any high-churn API surfaces named in the plan — reduces per-batch lookup cost

**2b. Adversarial Plan Review** *(optional — explicitly invoked only; not always-on)*:

Invoke when: user says "challenge the plan", "run adversarial review", "validate plan", or similar; OR the plan from step 2 cites external research, fetched URLs, or web evidence (triggers strategy 4 of the validator).

Spawn `han-adversarial-validator` agent. Pass it the full plan document from step 2 as input (the plan IS the "evidence summary + planned fix"). The agent challenges the plan's evidence base, assumptions, and proposed scope. Findings are written to `plans_and_protocols/[date]_adversarial_review.md`. Review findings before proceeding to step 3.

Do NOT invoke by default — this step adds ~1 extra agent call (sonnet) and is worth it only when the plan's assumptions are load-bearing or the plan cites external sources.

3. **Plan Size Check** (CRITICAL):
   Before proceeding, evaluate the plan:

   | Indicator | Threshold | Action |
   |-----------|-----------|--------|
   | Files to change | > 10 files | Consider splitting |
   | Layers affected | All 3 layers with significant changes | Consider splitting |
   | Estimated effort | > 1 focused session | Consider splitting |
   | Risk level | High complexity or unknowns | Consider splitting |

   **If plan is too large**:
   - Identify logical split points (by layer, by feature slice, by dependency order)
   - Propose splitting to user
   - If user agrees:
     a) Reduce current task scope in goal.md
     b) Create additional task(s) using `task-create-code` skill
     c) **Use same date prefix** as current task to preserve ordering
     d) Update plan to reflect reduced scope
   - Re-verify plan size after splitting

4. **User Approval**: Wait for user to approve the (possibly reduced) plan

5. **Implement** (multi-agent, all sequential):

   **5a. Dependencies** *(only if plan lists new packages)*:
   Admission gate (REQ-PROC-060): new packages require developer pre-authorization — check `doc/process/dependency_admission_gate.md` first; never self-authorize.
   Spawn one `implementation-engineer` agent: edit `pubspec.yaml` → `flutter pub get` → verify resolution. Wait before proceeding.

   **5b. Implementation batches** *(max 3 source files per agent)*:
   - Group plan's file list into batches of ≤3 files, Data layer first → Presentation last
   - For each batch spawn one `implementation-engineer` agent (runs `doc-lookup-dependencies` per new API surface — see agent docs; dedup via `lookup_log.jsonl`):
     - Implements the batch files
     - Writes initial test file(s) for those files (does NOT run them)
     - Adds WHY comments for non-obvious code
     - **If a missing design token is discovered**: pause and invoke `doc-update-tokens` skill before continuing
     - **Canon alignment**: prefer canonical names from `concept_canon.yaml` for classes, methods, BLoC events/states, user-facing strings; when a new user-facing concept is introduced, invoke `ux-write-canon-concept` first
     - Uses claude-log skill (with agent ID)
   - Run batches **sequentially** — each waits for the previous to finish

   **5c. Test execution** *(one agent per test file, sequential)*:
   - For each test file written across all batches, spawn one `test-engineer` agent:
     - Runs `flutter test [that_test_file] `
     - Fixes any failures (may modify both test and source files)
     - Uses claude-log skill (with agent ID)
   - Run **sequentially** — test agents may change implementation files

6. **Quality**: Spawn quality-checker agent to verify code against doc/ guidelines
   - VCD: Verify that any value trade-off decisions in implemented code have a WHY comment referencing the trade-off record in the originating artifact

   **Gate-failure → lookup edge** (REQ-PROC-053 §7.2): if quality-checker reports `STATUS: RED`, classify the failure before spawning the fix agent:

   | Failure category | Detection | `--trigger` |
   |---|---|---|
   | Deprecation | "deprecated" / "deprecated_member_use" in analyzer output | `deprecation` |
   | Unknown symbol | "Undefined name" / "isn't defined for the type" / `non_existent_method` | `unknown_symbol` |
   | Signature mismatch | "argument type" / "isn't a subtype" / `extra_positional_arguments` | `gate_failure_api_mismatch` |
   | Test framework subtle | test-runner stack-trace + matcher mismatch on async/golden/semantics | `test_framework_subtle` |
   | SP gate (REQ-PROC-052) | SP1–SP6 violation on security-relevant package | `gate_failure_api_mismatch` |

   If the failure matches any row: invoke `doc-lookup-dependencies` with `--trigger <value>` **before** spawning the fix agent. The fix agent receives both the failure text and the fresh doc result.

7. **Log**: Use claude-log skill for overall workflow

8. **Doc guidelines**: Use doc-update-guidelines skill (mandatory — it will exit early if no update is needed)

9. **Complete Task**: Use task-complete skill (marks task completed and commits)

---

## Task Splitting Guidelines

When splitting a task:

### Preserve Order
If current task is `2026-01-04_impl_feature/`, new tasks should be:
- `2026-01-04_impl_feature_part2/`
- `2026-01-04_impl_feature_part3/`

Or by logical name:
- `2026-01-04_impl_feature_domain/`
- `2026-01-04_impl_feature_presentation/`

### Good Split Points
1. **By Layer**: Domain → Data → Presentation
2. **By Feature Slice**: Core functionality → Extensions → Polish
3. **By Dependency**: Independent parts first → Dependent parts later
4. **By Risk**: Low-risk changes first → High-risk changes later

### What Goes in Each Split Task
Each task should:
- Be independently completable (tests pass after each)
- Reference the parent requirement
- Note its relationship to sibling tasks
- Have clear acceptance criteria

---

**Output**: "Task completed. Changes committed with plan in plans_and_protocols/."
