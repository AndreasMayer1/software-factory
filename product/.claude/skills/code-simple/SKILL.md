---
name: code-simple
description: End-to-end workflow for simple, single-file tasks
tools: "*"
model: inherit
---

You orchestrate a simple task workflow from start to finish.

**User invokes**: "Use code-simple skill for [task name] in [path]"

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the task goal.md is missing or off-schema. (Skip only when bootstrapping a brand-new task that step 1 will create.)
```bash
GOAL_PATH="${1:?code-simple requires the task goal.md path}"
[ -f "${GOAL_PATH}" ] || { echo "ERR: missing goal.md at ${GOAL_PATH} — run task-create first (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${GOAL_PATH}" .claude/schemas/goal_metadata.yaml || exit 2
```

**You execute**:

1. **Setup**: Use task-create skill to initialize workspace (if not already done)

2. **Read & Assess**:
   - Read goal.md and identify relevant doc/ guidelines
   - If task involves Presentation Layer: read `doc/presentation/design/persona_design_bridge.md` to understand persona-to-design mapping (referenced by goal's context)
   - Quick assessment: Is this really "simple"?

   | Simple Task | Not Simple → Use code-complex |
   |-------------|----------------------------------------|
   | 1-3 files | > 3 files |
   | Single layer | Multiple layers |
   | Clear pattern exists | New pattern needed |
   | Low risk | Architectural impact |

   **If not simple**: Inform user and suggest using `code-complex` skill instead.

   **Sketch Gate (Presentation Layer only)**:
   If task modifies Presentation Layer:
   1. Check goal.md for `skip_scribble: true` field
   2. If absent: discover the scribble path — (a) read `[requirement]/requirements.md` for `feature_path`; if present, check `requirements_tasks/scribbles/<feature_path>/` for `status: approved` version; (b) otherwise search `find requirements_tasks/scribbles/ -name "metadata.yaml" | xargs grep -l "<REQ-ID>"` for the requirement ID; (c) legacy fallback: check `[requirement]/scribbles/`.
   3. If no approved scribble exists: invoke `ui-scribble-iterate` skill, pause for user approval
   4. If approved scribble exists:
      a. Read `flutter_handoff.yaml` in the approved version folder; locate the top-level `contract:` block (fields: `locked_in`, `re_derive`, `source`).
      b. Pass the following contract split to the implementer:
         - **LOCKED-IN** (`contract.locked_in` keys L1–L15): implement exactly as depicted in the scribble — widget choices, screen list/order, copy text, information hierarchy, persona-sizing token references, navigation pattern, dialog pattern, component-library choices, design decisions, and accessibility intent.
         - **RE-DERIVE** (`contract.re_derive` keys D1–D8): derive from `doc/presentation/` and `tokens.json` regardless of what the scribble shows — do NOT copy literal color values, exact token values, animations, responsive mechanics, focus order, BLoC wiring, or cross-persona constraints from the scribble.
      c. **Navigation graph** (AC-38): if `flutter_handoff.yaml` contains a `flow_navigation_files:` block, load each referenced `flow_navigation.yaml`. Pass the navigation graph to the implementer: `edges[]` define the GoRouter routes or Navigator calls that must be present (implement navigation from declared edges, not by inferring from screen order); `escape_paths[]` define required back-navigation or cancel handling.
      d. Every implementation note that references a scribble element must state which side of the contract applies (`locked-in` or `re-derive`).

**VCD Guard** (skip if change is purely technical with no UX impact):
If this change affects a feature used by personas with conflicting values:
1. Read `vcd:` YAML blocks for the 2-3 most relevant personas
2. Does this change degrade any persona's primary value?
3. If YES → PAUSE and present the conflict to the user before implementing
4. If NO → proceed

3. **Implement**:
   - Initialize doc-lookup log (AC-07 / REQ-PROC-053): `touch <task-plans_and_protocols>/lookup_log.jsonl`
   - Spawn one `implementation-engineer` agent (runs `doc-lookup-dependencies` per new API surface — see agent docs):
   - Implements the 1–3 files
   - Writes initial test file(s) for those files (does NOT run them)
   - Adds WHY comments for non-obvious code (see CLAUDE.md Section 5 for when to skip)
   - **If a missing design token is discovered**: pause and invoke `doc-update-tokens` skill before continuing
   - **Canon alignment**: prefer canonical names from `concept_canon.yaml` for classes, methods, BLoC events/states, user-facing strings; when a new user-facing concept is introduced, invoke `ux-write-canon-concept` first
   - Runs `dart fix --apply`

4. **Test execution** *(one agent per test file, sequential)*:
   For each test file written, spawn one `test-engineer` agent:
   - Runs `flutter test [that_test_file] `
   - Fixes any failures (may modify both test and source files)
   Run **sequentially** — test agents may change implementation files

5. **Quality**: Spawn `quality-checker` agent to verify code against doc/ guidelines

   **Gate-failure → lookup edge** (REQ-PROC-053 §7.2): if quality-checker reports `STATUS: RED`, classify the failure before spawning the fix agent:

   | Failure category | Detection | `--trigger` |
   |---|---|---|
   | Deprecation | "deprecated" / "deprecated_member_use" in analyzer output | `deprecation` |
   | Unknown symbol | "Undefined name" / "isn't defined for the type" / `non_existent_method` | `unknown_symbol` |
   | Signature mismatch | "argument type" / "isn't a subtype" / `extra_positional_arguments` | `gate_failure_api_mismatch` |
   | Test framework subtle | test-runner stack-trace + matcher mismatch on async/golden/semantics | `test_framework_subtle` |
   | SP gate (REQ-PROC-052) | SP1–SP6 violation on security-relevant package | `gate_failure_api_mismatch` |

   If the failure matches any row: invoke `doc-lookup-dependencies` with `--trigger <value>` **before** spawning the fix agent. The fix agent receives both the failure text and the fresh doc result.

6. **Log**: Use claude-log skill to document work

7. **Doc guidelines**: Use doc-update-guidelines skill (mandatory — it will exit early if no update is needed)

8. **Complete Task**: Use task-complete skill (marks task completed and commits)

**Output**: "Task completed. Changes committed."
