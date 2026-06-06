# Lint Demo Run — check_skill_contracts.py

Demonstrates the lint script catching a real interface-contract violation.

## Setup

```
prototypes-dir: .../prototypes/
skills-root: .claude/skills/
contracts checked: contract_ui-create-scribble.yaml, contract_code-simple.yaml, contract_task-create.yaml
```

---

## Step 1 — Clean run on three valid contracts

```
$ python3 prototypes/check_skill_contracts.py \
    --prototypes-dir prototypes/ \
    --skills-root .claude/skills

PASS — 3 contract(s) checked, 0 violations.
```

**Exit code: 0**

---

## Step 2 — Inject violation

Edit `contract_code-simple.yaml` to claim it reads from a path no producer declares.

**Change applied to `derived_from.optional` in `contract_code-simple.yaml`:**

```yaml
# Before (valid — matches ui-create-scribble's produces block)
- path: requirements_tasks/<feature>/scribbles/v{n}/
  schema: .claude/schemas/scribble_metadata.yaml
  role: approved wireframe referenced during implementation

# After (violation — no skill produces this path)
- path: requirements_tasks/<feature>/prototypes_test_violation_scribbles/iteration_{n}/
  schema: .claude/schemas/scribble_metadata.yaml
  role: approved wireframe referenced during implementation
```

This simulates Scenario A from the Round 1 synthesis: a scribble folder rename
(`scribbles/v{n}/` → `iteration_{n}/`) that was applied in ui-create-scribble's
SKILL.md prose but NOT reflected in contract.yaml. code-simple still references
the old path convention.

---

## Step 3 — Violation run

```
$ python3 prototypes/check_skill_contracts.py \
    --prototypes-dir prototypes/ \
    --skills-root .claude/skills

FAIL — 1 contract violation(s):
  - contract_code-simple.yaml derived_from[optional] 'requirements_tasks/<feature>/prototypes_test_violation_scribbles/iteration_{n}/' — no producer declares this path and it is not a known external source. Add it to a producing skill's produces: block.
```

**Exit code: 1**

The error is specific and actionable:
- Identifies the exact contract file (`contract_code-simple.yaml`)
- Names the exact section (`derived_from[optional]`)
- Quotes the exact path string that has no declared producer
- Tells the author what to do ("Add it to a producing skill's produces: block")

This is the lint behavior specified in the web research (file 02 §Q5 anti-pattern:
"don't punt; say the exact strings"). A vague "contract mismatch detected" would
require the author to diff both files manually.

---

## Step 4 — Revert and re-verify

```
# Revert contract_code-simple.yaml to original scribbles/v{n}/ path

$ python3 prototypes/check_skill_contracts.py \
    --prototypes-dir prototypes/ \
    --skills-root .claude/skills

PASS — 3 contract(s) checked, 0 violations.
```

**Exit code: 0**

---

## What the lint checks

1. **Cross-reference: derived_from vs produces** — for every path in a skill's
   `derived_from.required` and `derived_from.optional`, the lint verifies that
   *some* skill's `produces.required` or `produces.conditional` block declares
   the same path (exact match or folder-level match for skills that consume a
   whole folder of files).

   Exceptions that bypass the check:
   - `source: external` annotation — developer-authored inputs (requirements.md,
     RELEASE_BACKLOG.md, user-provided image files)
   - `source: skill:<name>` annotation — explicitly named cross-reference
   - Paths starting with `doc/`, `requirements_user_needs/`, `lib/`, `test/`,
     `.claude/schemas/` — known external filesystem trees

2. **may_invoke existence** — for every skill name in `may_invoke:`, the lint
   checks that `.claude/skills/<name>/SKILL.md` exists. Catches misspellings and
   references to skills not yet created.

## What the lint does NOT check

- Whether the skill actually writes the declared output (that's a runtime guard, not a static lint)
- Whether the schema reference in `schema:` points to a valid `.claude/schemas/` file
- Whether `source: external` annotations are honest (a skill could wrongly exempt a cross-ref)
- Cross-skill consistency when only 3 of 60 skills have contracts (full benefit requires broad adoption)
