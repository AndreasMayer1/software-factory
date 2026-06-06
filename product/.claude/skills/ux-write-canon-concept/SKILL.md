---
name: ux-write-canon-concept
description: Add/update/rename canon concepts; required for new user-facing concepts
tools: [Read, Write, Edit, Bash, Glob, Grep, Skill]
model: inherit
---

**REQUIRED** before introducing any new user-facing concept — covers both therapist register and lay (self-user) register audience axes.
Sole gatekeeper for `requirements_user_needs/concept_canon/concept_canon.yaml`.

## Lock

Acquire before any write; release on exit (success or failure):
```bash
# acquire
[ -f requirements_user_needs/concept_canon/.canon-lock ] && echo "LOCKED — another session is editing. Abort." && exit 1
touch requirements_user_needs/concept_canon/.canon-lock

# release (always)
rm -f requirements_user_needs/concept_canon/.canon-lock
```

## Mode Detection

Detect from user input: **add** | **update** | **upgrade-provenance** | **rename-cascade**.

## Add

1. Duplicate check: normalize name (lowercase, collapse spaces/hyphens), compare against all `name_canonical` + `aliases` entries. Abort if match.
2. Generate ID: `CONCEPT-<UPPER-KEBAB>` (e.g. "Hand Over" → `CONCEPT-HAND-OVER`). Verify uniqueness in YAML.
3. Append entry to `concept_canon.yaml` following `.claude/schemas/concept_canon_entry.yaml` (canonical field list, types, enums); use existing entries as worked examples.
4. **Regenerate** (see below), then **release lock**.

## Update

1. Locate entry by ID or `name_canonical`.
2. Apply field changes.
3. **Regenerate**, then **release lock**.

## Upgrade Provenance

Levels (ascending): `inferred` → `proto-evidenced` → `evidenced`.

1. Locate entry by ID or name. Confirm current level.
2. Update `provenance.<lang>.level`; set `validated_at` to today.
3. **Regenerate**, then **release lock**.

## Rename Cascade

1. Record `old_name`. Enumerate all referencing files:
   ```bash
   grep -rl "<old_name>" requirements_user_needs/ requirements_tasks/ lib/ test/ doc/
   ```
2. Count results.
3. **Count > 10**: do NOT edit inline. Invoke `task-create` skill to create an impl task under REQ-PROC-049 describing the rename (`<old_name>` → `<new_name>`, file list). Release lock and exit.
4. **Count ≤ 10**: apply rename in all files + update `name_canonical` in YAML.
5. **Regenerate**, then **release lock**.

## Regenerate

```bash
python3 scripts/user_needs/generate_concept_canon_md.py
```
Overwrites `concept_canon.md` and `concept_canon.index.yaml`.
