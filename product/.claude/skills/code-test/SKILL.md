---
name: code-test
description: End-to-end TDD workflow for implementing tests
tools: "*"
model: inherit
---

You orchestrate a TDD workflow from start to finish.

**User invokes**: "Use code-test skill for [task name] in [path]"

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the task goal.md is missing or off-schema. (Skip only when bootstrapping a brand-new task that step 1 will create.)
```bash
GOAL_PATH="${1:?code-test requires the task goal.md path}"
[ -f "${GOAL_PATH}" ] || { echo "ERR: missing goal.md at ${GOAL_PATH} — run task-create first (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${GOAL_PATH}" .claude/schemas/goal_metadata.yaml || exit 2
```

**You execute**:

1. **Setup**: Use task-create skill to initialize workspace

2. **Plan**: Spawn `test-engineer` agent for the planning phase. The agent runs in the session's model; if a more strategic planning pass is needed, the orchestrator/route will already have launched the session in Opus.

   Agent tasks:
   - **CRITICAL**: Read doc/testing/ guidelines first
   - Reads goal.md
   - Creates test plan in plans_and_protocols/ of the current task
   - Uses claude-log skill (with agent ID)
   - **Optional**: Wait for user plan approval

3. **Implement**: test-engineer continues (or resume if new agent) — Phase 2 invokes `doc-lookup-dependencies` per AC-07 for test-framework API surfaces before writing tests (see agent docs):
   - Write tests (TDD approach)
   - Run `flutter test [file] ` after each test
   - Fix failures immediately
   - NEVER proceed if tests fail
   - Uses claude-log skill after each run

4. **Report**: test-engineer creates final test report

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

6. **Log**: Use claude-log skill for overall workflow

7. **Doc guidelines**: Use doc-update-guidelines skill (mandatory — it will exit early if no update is needed)

8. **Complete Task**: Use task-complete skill (runs merge docs, marks task completed, and commits)

**Output**: "Tests implemented and passing. Test report in plans_and_protocols/."
