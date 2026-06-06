---
task_id: TASK-PROC-044-02-03
session_id: 8763f2da-6d20-4603-aeac-a2531f8775cd
agent_id: main-session
date: 2026-06-02
skills_used:
  - claude-route
  - task-resolve
  - claude-automated-mode
  - claude-modify-skill
  - task-complete
  - claude-commit
---

# Protocol: developer ratification applied — contract side green, task complete

## Developer answers (from question.md inline edits + answer.md)

- **(A)** 4 `automation-*` tokens approved, with refined definitions (developer edited
  inline: `automation-log` "purged on startup"; `automation-criteria` "health criteria
  the LLM reads during active monitoring"; `automation-cron` "LLM monitoring loop").
- **(B)** Approved a dedicated **`environment`** category for `devcontainer` (outside
  both factory and app) AND a separate layer for project/technology-specific manifests:
  `pubspec` is NOT factory-core (it is Flutter/Dart-specific, future "Flutter plugin"
  territory), whereas generic `source` IS a factory artifact. Asked for a forward-
  compatible split design.
- **(C)** **Option C1** — drop the two `.claude/schemas/*.yaml` `derived_from` lines
  (schemas/templates are never `derived_from`). Also: update the agent-authoring skill
  to make that rule explicit.

## Changes applied

### Registry (`.factory/registry/artifacts.yaml`)
- New categories: `environment`, `tech-stack`.
- New tokens: `automation-sentinel`, `automation-log`, `automation-criteria`,
  `automation-cron` (automation); `devcontainer` (environment); `pubspec` (tech-stack).
  All with the developer's ratified definitions.

### Contracts (10 entries → tokens / removed)
- claude-automated-mode: `automation/.automated_mode` → `automation-sentinel`.
- claude-autorun: `orchestrate.log`→`automation-log`, `.automated_mode`→`automation-sentinel`,
  `MONITORING_CRITERIA.md`→`automation-criteria`, `.monitoring_cron_id`→`automation-cron`.
- claude-install-os-tool: `.devcontainer/devcontainer.json` → `devcontainer` (×2).
- code-complex: `pubspec.yaml` → `pubspec`.
- ui-scribble-handoff-emitter: **removed** the two `.claude/schemas/*.yaml` derived_from
  lines (C1).

### Baseline (`scripts/quality/artifact_token_baseline.txt`)
- Trimmed from 444 entries to the 14 agent-name violations only (+ header). The 409
  obsolete contract-side entries (old literal paths now replaced by tokens) were removed
  so contract-side passes with **zero suppression** (AC-02). Header forbids re-adding
  contract-side entries.

### Skills (C follow-up, via claude-modify-skill)
- `claude-create-agent` (§6 + Establishment Gate) and `claude-modify-agent`
  (step 4 + Establishment Gate): added explicit rule that **schemas and templates are
  NOT artifacts** and must never appear in `produces:`/`derived_from:`/`consumes:`.
  No INDEX.md / factory_flows.md change (descriptions and diagram unaffected).

### Decision record
- `decisions/2026-06-02_registry-ownership-layers.md`: documents the L1 factory-core /
  L2 technology-plugin / L3 developer-environment split (the (B) suggestion). Minimal
  version implemented now; full reclassification deferred to factory extraction.

## Verification

```
$ python3 scripts/quality/check_artifact_token_resolve.py        # no baseline
FAIL — 14 unbaselined violation(s)   # all agent-name (AC-03, out of scope)
  → contract-side (produces/derived_from/consumes) violations: 0   ✅ AC-02

$ python3 scripts/quality/check_artifact_token_resolve.py \
    --baseline scripts/quality/artifact_token_baseline.txt        # as wired in gate
PASS — checked 66 skill contract(s), 9 agent contract(s), 14 agent(s);
       0 unbaselined violation(s). [14 baselined]                 ✅ gate GREEN on develop
```

## Acceptance criteria
- [x] Resolve lint reports zero contract-side violations across the repo.
- [x] Any new tokens added went through the establishment gate (developer-ratified in
      question.md; no silent appends).

## Out of scope (unchanged)
- 14 agent-name violations remain (AC-03) — resolved by REQ-PROC-044-01 rename work.
