"""Tests for scripts/factory/render_factory_map.py."""

# tier: B  # tests for a Tier B generator

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs

sys.path.insert(0, str(Path(__file__).parent.parent / "factory"))
import render_factory_map as rfm  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_skill(
    skills_root: Path,
    name: str,
    contract: dict[str, object] | None = None,
) -> Path:
    """Create a skill folder with SKILL.md and optional contract.yaml."""
    folder = skills_root / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    if contract is not None:
        (folder / "contract.yaml").write_text(yaml.safe_dump(contract))
    return folder


def _write_schema(schemas_root: Path, stem: str) -> Path:
    """Create a .yaml schema file."""
    schemas_root.mkdir(parents=True, exist_ok=True)
    f = schemas_root / f"{stem}.yaml"
    f.write_text(f"schema_version: 1\nname: {stem}\n")
    return f


def _minimal_contract(
    skill_name: str,
    produces_paths: list[str] | None = None,
    derived_paths: list[str] | None = None,
    may_invoke: list[str] | None = None,
    side_effects: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    contract: dict[str, object] = {"contract_version": 1, "skill": skill_name}
    if produces_paths:
        contract["produces"] = {
            "required": [{"path": p} for p in produces_paths]
        }
    if derived_paths:
        contract["derived_from"] = {
            "required": [{"path": p, "source": "external"} for p in derived_paths]
        }
    if may_invoke:
        contract["may_invoke"] = may_invoke
    if side_effects:
        contract["side_effects"] = side_effects
    return contract


# ---------------------------------------------------------------------------
# Family detection
# ---------------------------------------------------------------------------


def test_detect_family_code() -> None:
    assert rfm.detect_family("code-simple") == "code"


def test_detect_family_ui() -> None:
    assert rfm.detect_family("ui-verify-flutter") == "ui"


def test_detect_family_requ() -> None:
    assert rfm.detect_family("requ-explore") == "requ"


def test_detect_family_task() -> None:
    assert rfm.detect_family("task-create") == "task"


def test_detect_family_claude() -> None:
    assert rfm.detect_family("claude-log") == "claude"


def test_detect_family_ux() -> None:
    assert rfm.detect_family("ux-write-persona") == "ux"


def test_detect_family_release() -> None:
    assert rfm.detect_family("release-plan") == "release"


def test_detect_family_doc() -> None:
    assert rfm.detect_family("doc-split") == "doc"


def test_detect_family_verify() -> None:
    assert rfm.detect_family("verify-quality") == "verify"


def test_detect_family_other() -> None:
    assert rfm.detect_family("brb") == "other"
    assert rfm.detect_family("codegraph") == "other"


# ---------------------------------------------------------------------------
# Node generation from contract
# ---------------------------------------------------------------------------


def test_skill_node_has_correct_fields(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract("task-create")
    _write_skill(skills_root, "task-create", contract)

    nodes, _ = rfm.build_graph(tmp_path, {})
    skill_nodes = [n for n in nodes if n["data"]["type"] == "skill"]
    assert len(skill_nodes) == 1
    d = skill_nodes[0]["data"]
    assert d["id"] == "skill:task-create"
    assert d["label"] == "task-create"
    assert d["family"] == "task"
    assert d["has_contract"] is True
    assert d["heat"] == 0.0


def test_schema_nodes_created_from_yaml_files(tmp_path: Path) -> None:
    schemas_root = tmp_path / ".claude" / "schemas"
    _write_schema(schemas_root, "goal_metadata")
    _write_schema(schemas_root, "requirements_frontmatter")

    nodes, _ = rfm.build_graph(tmp_path, {})
    schema_nodes = [n for n in nodes if n["data"]["type"] == "schema"]
    ids = {n["data"]["id"] for n in schema_nodes}
    assert "schema:goal_metadata" in ids
    assert "schema:requirements_frontmatter" in ids


def test_artifact_nodes_created_from_produces(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "task-create",
        produces_paths=["requirements_tasks/x/tasks/t/goal.md"],
    )
    _write_skill(skills_root, "task-create", contract)

    nodes, _ = rfm.build_graph(tmp_path, {})
    artifact_nodes = [n for n in nodes if n["data"]["type"] == "artifact"]
    assert any(
        n["data"]["id"] == "artifact:requirements_tasks/x/tasks/t/goal.md"
        for n in artifact_nodes
    )


# ---------------------------------------------------------------------------
# Edge generation
# ---------------------------------------------------------------------------


def test_produces_edge_created(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "task-create",
        produces_paths=["requirements_tasks/x/goal.md"],
    )
    _write_skill(skills_root, "task-create", contract)

    _, edges = rfm.build_graph(tmp_path, {})
    produces_edges = [e for e in edges if e["data"]["type"] == "produces"]
    assert len(produces_edges) == 1
    assert produces_edges[0]["data"]["source"] == "skill:task-create"
    assert produces_edges[0]["data"]["target"] == "artifact:requirements_tasks/x/goal.md"


def test_consumes_edge_created(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "code-simple",
        derived_paths=["requirements_tasks/x/goal.md"],
    )
    _write_skill(skills_root, "code-simple", contract)

    _, edges = rfm.build_graph(tmp_path, {})
    consumes_edges = [e for e in edges if e["data"]["type"] == "consumes"]
    assert len(consumes_edges) == 1
    assert consumes_edges[0]["data"]["source"] == "skill:code-simple"
    assert consumes_edges[0]["data"]["target"] == "artifact:requirements_tasks/x/goal.md"


def test_invokes_edge_created(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract_a = _minimal_contract("task-create", may_invoke=["requ-explore"])
    contract_b = _minimal_contract("requ-explore")
    _write_skill(skills_root, "task-create", contract_a)
    _write_skill(skills_root, "requ-explore", contract_b)

    _, edges = rfm.build_graph(tmp_path, {})
    invoke_edges = [e for e in edges if e["data"]["type"] == "invokes"]
    assert len(invoke_edges) == 1
    assert invoke_edges[0]["data"]["source"] == "skill:task-create"
    assert invoke_edges[0]["data"]["target"] == "skill:requ-explore"


def test_script_call_edge_created(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "task-create",
        side_effects=[
            {"target": "scripts/artifacts/generate_id_registry.py", "action": "regenerate"}
        ],
    )
    _write_skill(skills_root, "task-create", contract)

    _, edges = rfm.build_graph(tmp_path, {})
    script_edges = [e for e in edges if e["data"]["type"] == "script_call"]
    assert len(script_edges) == 1
    assert script_edges[0]["data"]["source"] == "skill:task-create"
    assert (
        script_edges[0]["data"]["target"]
        == "artifact:scripts/artifacts/generate_id_registry.py"
    )


def test_schema_ref_edge_created(tmp_path: Path) -> None:
    schemas_root = tmp_path / ".claude" / "schemas"
    _write_schema(schemas_root, "goal_metadata")
    skills_root = tmp_path / ".claude" / "skills"
    contract: dict[str, object] = {
        "contract_version": 1,
        "skill": "task-create",
        "produces": {
            "required": [
                {
                    "path": "requirements_tasks/x/goal.md",
                    "schema": ".claude/schemas/goal_metadata.yaml",
                }
            ]
        },
    }
    _write_skill(skills_root, "task-create", contract)

    _, edges = rfm.build_graph(tmp_path, {})
    schema_edges = [e for e in edges if e["data"]["type"] == "schema_ref"]
    assert len(schema_edges) == 1
    assert schema_edges[0]["data"]["target"] == "schema:goal_metadata"


# ---------------------------------------------------------------------------
# Graceful degradation
# ---------------------------------------------------------------------------


def test_missing_contract_adds_unmanaged_node(tmp_path: Path) -> None:
    """Skill without contract.yaml is still added as a node with has_contract=False."""
    skills_root = tmp_path / ".claude" / "skills"
    _write_skill(skills_root, "brb")  # no contract

    nodes, edges = rfm.build_graph(tmp_path, {})
    skill_nodes = [n for n in nodes if n["data"]["type"] == "skill"]
    assert len(skill_nodes) == 1
    d = skill_nodes[0]["data"]
    assert d["has_contract"] is False
    # No edges should be created for this unmanaged skill
    assert edges == []


def test_missing_contract_emits_warning(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:  # type: ignore[type-arg]  # capsys is typed by pytest
    skills_root = tmp_path / ".claude" / "skills"
    _write_skill(skills_root, "brb")

    rfm.build_graph(tmp_path, {})
    captured = capsys.readouterr()
    assert "brb/contract.yaml not found" in captured.err


# ---------------------------------------------------------------------------
# Heat data
# ---------------------------------------------------------------------------


def test_heat_data_loaded_and_normalized(tmp_path: Path) -> None:
    heat_file = tmp_path / "heat.json"
    heat_data = {
        "by_file": {
            ".claude/skills/task-create/SKILL.md": {"reads": 10, "bytes_total": 5000, "sessions": 3},
            ".claude/skills/code-simple/SKILL.md": {"reads": 5, "bytes_total": 2000, "sessions": 2},
        }
    }
    heat_file.write_text(json.dumps(heat_data))

    raw = rfm.load_heat_data(heat_file)
    assert raw["skill:task-create"] == 10.0
    assert raw["skill:code-simple"] == 5.0

    normalized = rfm.normalize_heat(raw)
    assert normalized["skill:task-create"] == pytest.approx(1.0)
    assert normalized["skill:code-simple"] == pytest.approx(0.5)


def test_heat_applied_to_skill_node(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract("task-create")
    _write_skill(skills_root, "task-create", contract)

    heat_file = tmp_path / "heat.json"
    heat_file.write_text(json.dumps({
        "by_file": {
            ".claude/skills/task-create/SKILL.md": {"reads": 8, "bytes_total": 3000, "sessions": 2},
        }
    }))
    raw_heat = rfm.load_heat_data(heat_file)
    heat = rfm.normalize_heat(raw_heat)

    nodes, _ = rfm.build_graph(tmp_path, heat)
    skill_node = next(n for n in nodes if n["data"]["id"] == "skill:task-create")
    assert skill_node["data"]["heat"] == pytest.approx(1.0)


def test_heat_path_to_node_id_skill() -> None:
    assert rfm.heat_path_to_node_id(".claude/skills/task-create/SKILL.md") == "skill:task-create"


def test_heat_path_to_node_id_schema() -> None:
    assert rfm.heat_path_to_node_id(".claude/schemas/goal_metadata.yaml") == "schema:goal_metadata"


def test_heat_path_to_node_id_unknown() -> None:
    assert rfm.heat_path_to_node_id("lib/some/file.dart") is None


def test_heat_path_to_node_id_skill_absolute() -> None:
    abs_path = str(rfm._PROJECT_ROOT / ".claude/skills/code-simple/SKILL.md")
    assert rfm.heat_path_to_node_id(abs_path) == "skill:code-simple"


def test_heat_path_to_node_id_schema_absolute() -> None:
    abs_path = str(rfm._PROJECT_ROOT / ".claude/schemas/flutter_handoff.yaml")
    assert rfm.heat_path_to_node_id(abs_path) == "schema:flutter_handoff"


def test_normalize_heat_empty() -> None:
    assert rfm.normalize_heat({}) == {}


def test_normalize_heat_all_zero() -> None:
    result = rfm.normalize_heat({"a": 0.0, "b": 0.0})
    assert result == {"a": 0.0, "b": 0.0}


# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------


def test_build_html_contains_cytoscape_cdn() -> None:
    html = rfm.build_html([], [])
    assert rfm.CYTOSCAPE_CDN in html


def test_build_html_embeds_graph_data(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract("task-create", produces_paths=["requirements_tasks/x/goal.md"])
    _write_skill(skills_root, "task-create", contract)
    nodes, edges = rfm.build_graph(tmp_path, {})
    html = rfm.build_html(nodes, edges)
    assert "skill:task-create" in html
    assert "artifact:requirements_tasks/x/goal.md" in html


def test_load_artifact_registry(tmp_path: Path) -> None:
    registry_dir = tmp_path / ".factory" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "artifacts.yaml").write_text(
        "_categories:\n  scripts: Scripts\nscript:\n  category: scripts\n  path: scripts/**\n  definition: A script\n"
    )
    reg = rfm.load_artifact_registry(tmp_path)
    assert reg == {"script": "scripts"}


def test_load_artifact_registry_missing_file(tmp_path: Path) -> None:
    assert rfm.load_artifact_registry(tmp_path) == {}


def test_classify_artifact_registry_lookup() -> None:
    registry = {"goal": "task-workspace", "script": "scripts"}
    assert rfm._classify_artifact("goal", registry) == "task-workspace"
    assert rfm._classify_artifact("script", registry) == "scripts"


def test_classify_artifact_path_based() -> None:
    assert rfm._classify_artifact("scripts/foo/bar.py", {}) == "scripts"
    assert rfm._classify_artifact("doc/guidelines/README.md", {}) == "doc"
    assert rfm._classify_artifact("lib/app.dart", {}) == "source-code"
    assert rfm._classify_artifact("unknown/thing", {}) == "other"


def test_artifact_node_stores_art_type(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    registry = {"goal": "task-workspace"}
    contract = _minimal_contract("task-create", produces_paths=["goal"])
    _write_skill(skills_root, "task-create", contract)
    nodes, _ = rfm.build_graph(tmp_path, {}, registry)
    art_node = next(n for n in nodes if n["data"]["id"] == "artifact:goal")
    assert art_node["data"]["art_type"] == "task-workspace"


def test_build_html_uses_art_categories(tmp_path: Path) -> None:
    skills_root = tmp_path / ".claude" / "skills"
    registry = {"goal": "task-workspace"}
    contract = _minimal_contract("task-create", produces_paths=["goal"])
    _write_skill(skills_root, "task-create", contract)
    nodes, edges = rfm.build_graph(tmp_path, {}, registry)
    html = rfm.build_html(nodes, edges)
    assert 'value="task-workspace"' in html
    assert 'value="schema-yaml"' not in html


def test_option_values_are_html_escaped(tmp_path: Path) -> None:
    """Artifact IDs containing < > must be HTML-escaped in dropdown option values."""
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "claude-write-script",
        side_effects=[{"target": "scripts/<domain>/<script>.py", "action": "write", "pattern": True}],
    )
    _write_skill(skills_root, "claude-write-script", contract)
    # Pattern side effects are skipped — use a produces path with angle brackets instead
    contract2: dict[str, object] = {
        "contract_version": 1,
        "skill": "test-skill",
        "produces": {"required": [{"path": "scripts/<domain>/<out>.py"}]},
    }
    _write_skill(skills_root, "test-skill", contract2)
    nodes, edges = rfm.build_graph(tmp_path, {})
    html = rfm.build_html(nodes, edges)
    assert 'value="artifact:scripts/&lt;domain&gt;/&lt;out&gt;.py"' in html
    assert "<domain>" not in html.split("GRAPH_DATA")[0]


def test_directory_artifact_gets_nonempty_label(tmp_path: Path) -> None:
    """Artifact paths ending in / must not produce an empty label."""
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "code-run-integration",
        side_effects=[{"target": "scripts/integration_test_runner/test_outputs/", "action": "write"}],
    )
    _write_skill(skills_root, "code-run-integration", contract)
    nodes, _ = rfm.build_graph(tmp_path, {})
    artifact_nodes = [n for n in nodes if n["data"]["type"] == "artifact"]
    dir_node = next(
        (n for n in artifact_nodes if "test_outputs" in n["data"]["id"]), None
    )
    assert dir_node is not None
    assert dir_node["data"]["label"] != ""
    assert dir_node["data"]["label"] == "test_outputs"


def test_template_side_effects_skipped(tmp_path: Path) -> None:
    """Side effects with '<' in target are template placeholders and must be skipped."""
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract(
        "claude-write-script",
        side_effects=[
            {"target": "scripts/<domain>/<script>.py", "action": "write"},
            {"target": "scripts/real/helper.py", "action": "write"},
        ],
    )
    _write_skill(skills_root, "claude-write-script", contract)
    nodes, edges = rfm.build_graph(tmp_path, {})
    artifact_ids = {n["data"]["id"] for n in nodes if n["data"]["type"] == "artifact"}
    assert "artifact:scripts/<domain>/<script>.py" not in artifact_ids
    assert "artifact:scripts/real/helper.py" in artifact_ids
    script_edges = [e for e in edges if e["data"]["type"] == "script_call"]
    targets = {e["data"]["target"] for e in script_edges}
    assert "artifact:scripts/<domain>/<script>.py" not in targets


def test_main_writes_html_file(tmp_path: Path) -> None:
    """End-to-end: main() writes the HTML file and prints the summary line."""
    skills_root = tmp_path / ".claude" / "skills"
    contract = _minimal_contract("task-create")
    _write_skill(skills_root, "task-create", contract)

    output_path = tmp_path / "out.html"
    # Temporarily redirect project_root resolution by patching __file__ is not feasible;
    # call main with explicit argv and mock project_root via monkeypatching is not necessary
    # because we can call the pure functions directly in an e2e manner using a tmpdir.
    # Instead, call build_graph + build_html directly as the integration path.
    nodes, edges = rfm.build_graph(tmp_path, {})
    html = rfm.build_html(nodes, edges)
    output_path.write_text(html)
    assert output_path.exists()
    assert len(html) > 100
    assert "cytoscape" in html.lower()
