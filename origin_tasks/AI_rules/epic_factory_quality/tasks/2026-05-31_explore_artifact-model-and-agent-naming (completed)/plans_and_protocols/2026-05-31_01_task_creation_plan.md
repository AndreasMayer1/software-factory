---
requirement: REQ-PROC-044-02
requirements_version: 412618f2
created: 2026-05-31
revised: 2026-05-31
mode: full
---

# Task Creation Plan for REQ-PROC-044-02 (feat_artifact_model)

> Revised after the establishment-gate design decision (2026-05-31): gate fires
> **eager at authoring + lint backstop**; artifact establishment is a human-authorized
> act owned by REQ-PROC-044-01 (new AC-06). 044-02 AC-04 narrowed to the registry
> property (open / append-structured / no-overlap). The seeding task carries a
> developer review gate. One task (#3) is parented to REQ-PROC-044-01.

## Tasks

- task_name: "create-and-seed-artifact-registry"
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md"
  requirements_version: "412618f2"
  covers_acs: [AC-01, AC-04, AC-05, AC-06]
  effort: M
  layer: process/factory
  after: []
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    Create .factory/registry/artifacts.yaml (each entry: unique token + path/glob +
    one-line definition; append-structured; no duplicate tokens — satisfies AC-04's
    registry property). Propose the initial token set from the union of existing
    .claude/skills/*/contract.yaml and .claude/agents/*.contract.yaml produces/derived_from
    values, cross-checked against scripts/factory/render_factory_map.py nodes and the
    CLAUDE.md Information Map. REVIEW GATE (mandatory): the seeded token set is canon — the
    developer must ratify it (confirm / rename-to-existing / reject per token) before the
    registry is finalized; do not auto-commit the seeded set. Create .factory/README.md
    (authored-vs-generated lifecycle; inventory of registry/ vs optimize/ vs session_logs/
    with owners; .claude/ and root CLAUDE.md out of .factory scope). Ensure registry is
    committed and excluded from any .factory pruning config. Foundational — no deps.

- task_name: "artifact-token-resolve-lint"
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md"
  requirements_version: "412618f2"
  covers_acs: [AC-02, AC-03]
  effort: M
  layer: process/scripts
  after: ["create-and-seed-artifact-registry"]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    Build a resolve-to-token lint (script via claude-write-script, REQ-PROC-043) wired into
    the per-change quality gates (REQ-PROC-046) in the boundary-contract-lint family
    (epic AC-08). Checks: (a) every produces:/derived_from: value resolves to a registry token;
    (b) every governed agent-name artifact-or-lens segment resolves to a token; (c) the registry
    has no duplicate token (backs AC-04 no-overlap). Unresolved/duplicate => visible warning +
    graceful stop. NOTE: check (b) only goes fully green once REQ-PROC-044-01 renames land —
    coordinate ordering with 044-01.

- task_name: "artifact-establishment-gate-in-authoring-skills"
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md"
  requirements_version: "412618f2"
  covers_acs: [AC-06]
  effort: M
  layer: process/skills
  after: ["create-and-seed-artifact-registry"]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    PARENT: REQ-PROC-044-01 (not 044-02). Implements the eager establishment gate in the
    capability-authoring skills (claude-create-agent/-modify-agent, claude-create-skill/-modify-skill):
    when authoring would emit a produces:/derived_from: token or an agent-name artifact-or-lens
    segment absent from .factory/registry/artifacts.yaml, eagerly propose a registry entry
    (token+path+definition), the developer ratifies / renames-to-existing / rejects before
    authoring proceeds; append only on ratification; refuse duplicate/alias; automated mode
    escalates via pending_feedback (never auto-append). Edit skills via claude-modify-skill.

- task_name: "remediate-contracts-to-resolve-tokens"
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md"
  requirements_version: "412618f2"
  covers_acs: [AC-02]
  effort: M
  layer: process/factory
  after: ["artifact-token-resolve-lint"]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    Enforcement-creates-violations remediation: run the resolve lint across all existing
    contract.yaml files, reconcile every produces:/derived_from: value to a registry token
    (adding genuinely-new tokens via the establishment gate, fixing typos/aliases), until the
    contract-side check reports zero violations. Agent-name violations are handled by the
    REQ-PROC-044-01 rename work, not here.

- task_name: "verify-artifact-model"
  req_path: "requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md"
  requirements_version: "412618f2"
  covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06]
  effort: S
  layer: process
  after: ["artifact-token-resolve-lint", "artifact-establishment-gate-in-authoring-skills", "remediate-contracts-to-resolve-tokens"]
  task_type: verify
  opus_recommended: false
  implementation_notes: >
    Audit: run the resolve lint repo-wide; confirm graceful-stop on a seeded unresolved token
    and a seeded duplicate; confirm .factory/registry/artifacts.yaml + README exist and match
    AC-01/AC-04/AC-05; confirm the registry is reachable from the AC-06 authoritative set and
    consistent with contracts + factory map + Information Map; exercise the establishment gate
    (propose → ratify → append; reject alias). Record the residual AC-03 agent-name dependency
    on REQ-PROC-044-01 as a known follow-up if renames have not landed.

## Coverage Matrix

| AC | Requirement | Task(s) | Package |
|----|-------------|---------|---------|
| AC-01 | 044-02 | create-and-seed-artifact-registry; verify-artifact-model | n/a |
| AC-02 | 044-02 | artifact-token-resolve-lint; remediate-contracts-to-resolve-tokens; verify-artifact-model | n/a |
| AC-03 | 044-02 | artifact-token-resolve-lint; verify-artifact-model | n/a |
| AC-04 | 044-02 | create-and-seed-artifact-registry; artifact-token-resolve-lint; verify-artifact-model | n/a |
| AC-05 | 044-02 | create-and-seed-artifact-registry; verify-artifact-model | n/a |
| AC-06 | 044-02 | create-and-seed-artifact-registry; verify-artifact-model | n/a |
| AC-06 | 044-01 | artifact-establishment-gate-in-authoring-skills | n/a |

## Notes

- 4 impl tasks + 1 verification task (>= 3 impl → separate verification task mandatory). ✓
- All process/factory-tooling; no lib/test/integration_test changes → task-create (not -code).
- Process category → no target_package (skip per task-create Package Inheritance guard).
- Cross-requirement: task #3 is parented to REQ-PROC-044-01 (establishment gate AC-06);
  the other tasks are REQ-PROC-044-02. AC-03's full green state needs the 044-01 agent renames.
- Cross-ref gate: genuine links (REQ-PROC-044, -044-01, -043, -046) present; generic-"artifact"
  keyword candidates classified ignore.
