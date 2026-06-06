# tier: B
"""Tests for scripts/quality/validate_against_schema.py (REQ-PROC-044 Wave 2).

Strategy: build synthetic schema + artifact YAML files under tmp_path and call the pure
check function (and the CLI main) directly. Covers the three checks the validator owns:
required-present, unknown-key rejection, enum membership.

Real-corpus smoke tests (test_all_goal_md_against_real_schema,
test_all_requirements_md_against_real_schema) iterate over every goal.md and requirements.md
in requirements_tasks/ to guard against schema↔corpus drift. Exception lists below document
pre-schema artifacts and legacy-type files that are exempt because they are immutable
completed/cancelled tasks — any NEW failure outside those lists fails the test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

# scripts/ on path for util.*; scripts/quality on path for the module under test.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quality"))
import validate_against_schema as vas  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

SCHEMA = {
    "schema_version": 1,
    "artifact": "thing.yaml",
    "description": "test schema",
    "required": {
        "id": {"type": "string", "pattern": "X-[0-9]+"},
        "status": {"type": "string", "enum": ["pending", "done"]},
    },
    "optional": {
        "note": {"type": "string"},
    },
}

# ---------------------------------------------------------------------------
# Legacy exception lists for the real-corpus smoke tests
# (relative paths from repo root)
# ---------------------------------------------------------------------------

# goal.md files exempt from validation failures:
#   - PRE_SCHEMA: completed tasks created before the required-frontmatter system existed;
#     missing task_id / type / parent_requirement / status / created.
#   - LEGACY_TYPE: completed tasks that used now-deprecated type values
#     (analyze / review / define / explore+impl); all folded into 'explore'.
#   - PARSE_ERROR: files with malformed YAML (duplicate keys) — cannot be validated.
_GOAL_LEGACY_PRE_SCHEMA: frozenset[str] = frozenset(
    [
        "requirements_tasks/non-functional/architecture/logging/tasks/2026-03-08_impl_logging-guideline (completed)/goal.md",
        "requirements_tasks/non-functional/architecture/logging/tasks/2026-03-08_impl_logging-service (completed)/goal.md",
        "requirements_tasks/non-functional/ui_ux_design_system/navigation_patterns/tasks/2026-01-02_impl_update-navigation-guidelines (completed)/goal.md",
        "requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/tasks/2026-01-04_explore_gemini-requirements-update (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/requirements_writer_mode_flexibility/tasks/2025-10-04_explore_roo_rules_update (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/tasks/2025-10-09_explore_folder_structure (completed)/goal.md",
        "requirements_tasks/process/AI_rules/workflows/interactive_brainstorming_workflow/tasks/2025-10-09_impl_update_rules_with_brainstorming_workflow (completed)/goal.md",
        "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2025-10-04_explore_roo_rules_update (cancelled)/goal.md",
        "requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-27_explore_derive-tasks-claude-optimize (completed)/goal.md",
    ]
)

_GOAL_LEGACY_TYPE: frozenset[str] = frozenset(
    [
        "requirements_tasks/functional/shared/epic_data_transfer/feat_plan_receiving/tasks/2026-03-11_analyze_qr-scan-pipeline-test-gaps (completed)/goal.md",
        "requirements_tasks/process/AI_rules/ai_tool_management/dependency_admission_and_health/tasks/2026-05-26_review_admission-gate-completeness (completed)/goal.md",
        "requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/tasks/2026-05-26_review_lifecycle-completeness (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/language_coherence/tasks/2026-05-15_analyze_coordinate-arb-parser-with-proc-046 (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/market_research/tasks/2026-02-14_analyze_evaluate-research-quality (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/user_flow_to_requirements/tasks/2026-02-22_analyze_pipeline_evaluation (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-02-14_review_user_flow_creation_workflow (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/user_needs_content/tasks/2026-02-08_explore_persona_coverage_gaps (completed)/goal.md",
        "requirements_tasks/process/AI_rules/requirements_management/user_needs_content/tasks/2026-02-14_define_scenario_categories (completed)/goal.md",
        "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-05-26_analyze_scribble-quality-task-func-007-01-05 (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-10_analyze_audit-test-suite-naming-and-isolation (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-10_analyze_inventory-value-objects-needing-property-tests (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-13_analyze_audit-doc-guidelines-for-gate-migration (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_analyze_calibrate-cold-start-galaxy-a40 (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_analyze_inventory-screens-without-widget-tests (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/tasks/2026-05-10_analyze_audit-current-code-against-forbidden-patterns (completed)/goal.md",
        "requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/tasks/2026-05-10_analyze_audit-cryptographic-key-material-storage (completed)/goal.md",
    ]
)

# goal.md files with malformed YAML (duplicate keys) — cannot be loaded at all.
_GOAL_PARSE_ERRORS: frozenset[str] = frozenset(
    [
        "requirements_tasks/functional/shared/epic_data_transfer/tasks/2026-03-29_explore_update_qr_data_transfer (completed)/goal.md",
        "requirements_tasks/functional/shared/epic_data_transfer/tasks/2026-03-29_explore_update_file_transfer_protocol (completed)/goal.md",
        "requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings/tasks/2026-04-01_explore_transfer_speed_preference (completed)/goal.md",
    ]
)

_GOAL_KNOWN_EXCEPTIONS: frozenset[str] = (
    _GOAL_LEGACY_PRE_SCHEMA | _GOAL_LEGACY_TYPE | _GOAL_PARSE_ERRORS
)

# requirements.md files with malformed YAML (duplicate keys) — cannot be loaded.
_REQU_PARSE_ERRORS: frozenset[str] = frozenset(
    [
        "requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md",
        "requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md",
        "requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/requirements.md",
    ]
)

_REQU_KNOWN_EXCEPTIONS: frozenset[str] = _REQU_PARSE_ERRORS


def _rel(repo: Path, path: Path) -> str:
    """Return POSIX-style relative path from repo root for exception-list lookup."""
    return path.relative_to(repo).as_posix()


def _collect_failures(
    files: list[Path],
    schema: object,
    repo: Path,
) -> tuple[list[str], list[str]]:
    """Validate *files* against *schema*; return (parse_errors, validation_errors).

    Each list entry is a relative path string (POSIX, from repo root).
    """
    parse_errors: list[str] = []
    validation_errors: list[str] = []
    for f in files:
        rel = _rel(repo, f)
        try:
            artifact = vas.load_artifact(f)
        except Exception:  # catch-all at corpus level; we record the path, not swallow silently
            parse_errors.append(rel)
            continue
        errors = vas.check_artifact(artifact, schema, str(f))
        if errors:
            validation_errors.append(rel)
    return parse_errors, validation_errors


def _unexpected(found: list[str], known: frozenset[str]) -> list[str]:
    return [p for p in found if p not in known]


# ---------------------------------------------------------------------------
# Synthetic unit tests (unchanged from original)
# ---------------------------------------------------------------------------


def _write(path: Path, data: object) -> Path:
    path.write_text(yaml.safe_dump(data))
    return path


def test_valid_artifact_passes(tmp_path: Path) -> None:
    art = _write(tmp_path / "a.yaml", {"id": "X-1", "status": "done", "note": "ok"})
    errors = vas.check_artifact(vas.load_artifact(art), SCHEMA, str(art))
    assert errors == []


def test_missing_required_key_flagged(tmp_path: Path) -> None:
    art = _write(tmp_path / "a.yaml", {"id": "X-1"})
    errors = vas.check_artifact(vas.load_artifact(art), SCHEMA, str(art))
    assert any("missing required key 'status'" in e for e in errors)


def test_unknown_key_flagged(tmp_path: Path) -> None:
    art = _write(tmp_path / "a.yaml", {"id": "X-1", "status": "done", "bogus": 1})
    errors = vas.check_artifact(vas.load_artifact(art), SCHEMA, str(art))
    assert any("unknown key 'bogus'" in e for e in errors)


def test_enum_violation_flagged(tmp_path: Path) -> None:
    art = _write(tmp_path / "a.yaml", {"id": "X-1", "status": "WAT"})
    errors = vas.check_artifact(vas.load_artifact(art), SCHEMA, str(art))
    assert any("value 'WAT' is not one of" in e for e in errors)


def test_optional_key_allowed(tmp_path: Path) -> None:
    art = _write(tmp_path / "a.yaml", {"id": "X-1", "status": "pending", "note": "hi"})
    assert vas.check_artifact(vas.load_artifact(art), SCHEMA, str(art)) == []


def test_main_exit_codes(tmp_path: Path) -> None:
    schema_file = _write(tmp_path / "schema.yaml", SCHEMA)
    good = _write(tmp_path / "good.yaml", {"id": "X-9", "status": "done"})
    bad = _write(tmp_path / "bad.yaml", {"status": "nope"})
    assert vas.main([str(good), str(schema_file)]) == 0
    assert vas.main([str(bad), str(schema_file)]) == 1


def test_missing_files_fail_gracefully(tmp_path: Path) -> None:
    schema_file = _write(tmp_path / "schema.yaml", SCHEMA)
    assert vas.main([str(tmp_path / "nope.yaml"), str(schema_file)]) == 1
    art = _write(tmp_path / "a.yaml", {"id": "X-1", "status": "done"})
    assert vas.main([str(art), str(tmp_path / "noschema.yaml")]) == 1


# ---------------------------------------------------------------------------
# Real-corpus smoke tests (replaces the brittle single-path test)
# ---------------------------------------------------------------------------


def test_all_goal_md_against_real_schema() -> None:
    """Every goal.md in requirements_tasks/ passes goal_metadata.yaml validation.

    Failures are only allowed for files in _GOAL_KNOWN_EXCEPTIONS (pre-schema artifacts,
    legacy-type completed tasks, and malformed-YAML files). Any NEW failure → test fails.
    """
    repo = Path(__file__).resolve().parents[2]
    schema_path = repo / ".claude/schemas/goal_metadata.yaml"
    assert schema_path.exists(), f"Schema not found: {schema_path}"

    schema = vas.load_schema(schema_path)
    files = sorted((repo / "requirements_tasks").rglob("goal.md"))
    assert files, "No goal.md files found — check repo root derivation"

    parse_errors, validation_errors = _collect_failures(files, schema, repo)

    unexpected_parse = _unexpected(parse_errors, _GOAL_KNOWN_EXCEPTIONS)
    unexpected_validation = _unexpected(validation_errors, _GOAL_KNOWN_EXCEPTIONS)

    messages: list[str] = []
    if unexpected_parse:
        messages.append(
            f"Unexpected parse failures ({len(unexpected_parse)}):\n"
            + "\n".join(f"  {p}" for p in unexpected_parse)
        )
    if unexpected_validation:
        messages.append(
            f"Unexpected validation failures ({len(unexpected_validation)}):\n"
            + "\n".join(f"  {p}" for p in unexpected_validation)
        )

    assert not messages, "\n\n".join(messages)


def test_all_requirements_md_against_real_schema() -> None:
    """Every requirements.md in requirements_tasks/ passes requirements_frontmatter.yaml.

    Failures are only allowed for files in _REQU_KNOWN_EXCEPTIONS (malformed-YAML files).
    Any NEW failure → test fails.
    """
    repo = Path(__file__).resolve().parents[2]
    schema_path = repo / ".claude/schemas/requirements_frontmatter.yaml"
    assert schema_path.exists(), f"Schema not found: {schema_path}"

    schema = vas.load_schema(schema_path)
    files = sorted((repo / "requirements_tasks").rglob("requirements.md"))
    assert files, "No requirements.md files found — check repo root derivation"

    parse_errors, validation_errors = _collect_failures(files, schema, repo)

    unexpected_parse = _unexpected(parse_errors, _REQU_KNOWN_EXCEPTIONS)
    unexpected_validation = _unexpected(validation_errors, _REQU_KNOWN_EXCEPTIONS)

    messages: list[str] = []
    if unexpected_parse:
        messages.append(
            f"Unexpected parse failures ({len(unexpected_parse)}):\n"
            + "\n".join(f"  {p}" for p in unexpected_parse)
        )
    if unexpected_validation:
        messages.append(
            f"Unexpected validation failures ({len(unexpected_validation)}):\n"
            + "\n".join(f"  {p}" for p in unexpected_validation)
        )

    assert not messages, "\n\n".join(messages)
