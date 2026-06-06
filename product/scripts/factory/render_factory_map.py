#!/usr/bin/env python3
"""Render a static HTML factory map from skill contracts and schema files.

Reads .claude/skills/*/contract.yaml, .claude/schemas/*.yaml, and optional heat data,
then emits a Cytoscape.js JSON + self-contained single-file HTML viewer.

Output:
    .factory/overview/factory_map.html (or --output PATH)
    Stdout: "Factory map written to <path> (N nodes, M edges)"

Usage:
    scripts/factory/render_factory_map.py [--output PATH] [--heat-data PATH]
"""

# tier: B  # generator; imported by tests and CI — non-trivial graph-building logic

from __future__ import annotations

import argparse
import html as _html
import json
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parent.parent.parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CYTOSCAPE_CDN = "https://unpkg.com/cytoscape@3.30.2/dist/cytoscape.min.js"
DEFAULT_OUTPUT = ".factory/overview/factory_map.html"
SKILL_FAMILY_PREFIXES: tuple[tuple[str, str], ...] = (
    ("code-", "code"),
    ("ui-", "ui"),
    ("requ-", "requ"),
    ("task-", "task"),
    ("claude-", "claude"),
    ("ux-", "ux"),
    ("release-", "release"),
    ("doc-", "doc"),
    ("verify-", "verify"),
)
SKILLS_DIR = ".claude/skills"
SCHEMAS_DIR = ".claude/schemas"
ARTIFACT_REGISTRY_PATH = ".factory/registry/artifacts.yaml"
LARGE_DOC_BYTES_THRESHOLD = 5000
MIN_DISTANCE = 1
MAX_DISTANCE = 5


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def detect_family(name: str) -> str:
    """Return the family string for a skill name based on its prefix."""
    for prefix, family in SKILL_FAMILY_PREFIXES:
        if name.startswith(prefix):
            return family
    return "other"


def load_artifact_registry(project_root: Path) -> dict[str, str]:
    """Return {token: category} from .factory/registry/artifacts.yaml, empty dict on failure."""
    registry_path = project_root / ARTIFACT_REGISTRY_PATH
    if not registry_path.exists():
        return {}
    try:
        data = yaml.safe_load(registry_path.read_text()) or {}
    except yaml.YAMLError as exc:
        sys.stderr.write(f"WARNING: failed to parse artifact registry: {exc}\n")
        return {}
    result: dict[str, str] = {}
    for key, value in data.items():
        if not key.startswith("_") and isinstance(value, dict) and "category" in value:
            result[str(key)] = str(value["category"])
    return result


def _classify_artifact(path: str, registry: dict[str, str]) -> str:
    """Return the registry category for an artifact path, or a path-derived fallback."""
    stripped = path.rstrip("/")
    tail = stripped.rsplit("/", 1)[-1] if "/" in stripped else stripped
    if tail in registry:
        return registry[tail]
    if stripped.endswith((".py", ".ps1")):
        return "scripts"
    if stripped.endswith(".md"):
        return "doc"
    if stripped.endswith(".dart"):
        return "source-code"
    return "other"


def _contract_items(block: dict[str, Any], *sections: str) -> list[dict[str, Any]]:
    """Flatten named sub-sections (required/conditional/optional) of a contract block."""
    out: list[dict[str, Any]] = []
    for section in sections:
        for item in (block or {}).get(section, []) or []:
            if isinstance(item, dict):
                out.append(item)
    return out


def _artifact_id(path: str) -> str:
    return f"artifact:{path}"


def _skill_id(name: str) -> str:
    return f"skill:{name}"


def _schema_id(stem: str) -> str:
    return f"schema:{stem}"


def heat_path_to_node_id(file_path: str) -> str | None:
    """Map a heat-data file path to a Cytoscape node ID, or None if not mappable.

    Accepts both relative paths (from test fixtures) and absolute paths (as written
    by the PreToolUse/PostToolUse Read hooks, which receive absolute file paths from
    the Claude Code tool invocation).
    """
    p = file_path
    if Path(p).is_absolute():
        try:
            p = str(Path(p).relative_to(_PROJECT_ROOT))
        except ValueError:
            return None  # path is outside the project
    if p.startswith(".claude/skills/"):
        rest = p[len(".claude/skills/"):]
        parts = rest.split("/")
        if parts:
            return _skill_id(parts[0])
    if p.startswith(".claude/schemas/"):
        stem = Path(p).stem
        return _schema_id(stem)
    return None


def normalize_heat(raw: dict[str, float]) -> dict[str, float]:
    """Normalize heat values to [0.0, 1.0] range."""
    if not raw:
        return {}
    max_val = max(raw.values())
    if max_val == 0:
        return dict.fromkeys(raw, 0.0)
    return {k: v / max_val for k, v in raw.items()}


# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------


def load_heat_data(path: Path) -> dict[str, float]:
    """Load heat data from a JSON file and return {node_id: read_count}."""
    raw_heat: dict[str, float] = {}
    if not path.exists():
        return raw_heat
    try:
        data = json.loads(path.read_text())
        by_file = data.get("by_file", {})
        for file_path, stats in by_file.items():
            node_id = heat_path_to_node_id(file_path)
            if node_id:
                raw_heat[node_id] = float(stats.get("reads", 0))
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        sys.stderr.write(f"WARNING: failed to parse heat data from {path}: {exc}\n")
    return raw_heat


def collect_skill_dirs(project_root: Path) -> list[Path]:
    """Return sorted list of skill directories under .claude/skills/."""
    skills_root = project_root / SKILLS_DIR
    if not skills_root.exists():
        return []
    return sorted(d for d in skills_root.iterdir() if d.is_dir())


def collect_schema_files(project_root: Path) -> list[Path]:
    """Return sorted list of .yaml files under .claude/schemas/."""
    schemas_root = project_root / SCHEMAS_DIR
    if not schemas_root.exists():
        return []
    return sorted(schemas_root.glob("*.yaml"))


def build_skill_node(
    skill_dir: Path,
    contract: dict[str, Any] | None,
    heat: dict[str, float],
) -> dict[str, Any]:
    """Build a Cytoscape node dict for a skill."""
    name = skill_dir.name
    node_id = _skill_id(name)
    return {
        "data": {
            "id": node_id,
            "label": name,
            "type": "skill",
            "family": detect_family(name),
            "has_contract": contract is not None,
            "heat": heat.get(node_id, 0.0),
        }
    }


def build_schema_nodes(schema_files: list[Path]) -> list[dict[str, Any]]:
    """Build Cytoscape node dicts for schema files."""
    nodes = []
    for schema_file in schema_files:
        stem = schema_file.stem
        nodes.append({
            "data": {
                "id": _schema_id(stem),
                "label": stem,
                "type": "schema",
                "family": "other",
                "has_contract": False,
                "heat": 0.0,
            }
        })
    return nodes


def _add_artifact_node(
    artifact_id: str,
    artifact_nodes: dict[str, dict[str, Any]],
    registry: dict[str, str],
) -> None:
    """Ensure an artifact node exists in the artifact_nodes dict."""
    if artifact_id not in artifact_nodes:
        path = artifact_id[len("artifact:"):]
        path_stripped = path.rstrip("/")
        label = path_stripped.rsplit("/", 1)[-1] if "/" in path_stripped else path_stripped
        artifact_nodes[artifact_id] = {
            "data": {
                "id": artifact_id,
                "label": label or path_stripped,
                "type": "artifact",
                "art_type": _classify_artifact(path, registry),
                "family": "other",
                "has_contract": False,
                "heat": 0.0,
            }
        }


def _build_produces_edges(
    skill_name: str,
    contract: dict[str, Any],
    artifact_nodes: dict[str, dict[str, Any]],
    edge_counter: list[int],
    registry: dict[str, str],
) -> list[dict[str, Any]]:
    """Build produces-type edges from a contract's produces block."""
    edges: list[dict[str, Any]] = []
    produces_block = contract.get("produces", {}) or {}
    for item in _contract_items(produces_block, "required", "conditional"):
        path = item.get("path", "")
        if not path:
            continue
        art_id = _artifact_id(path)
        _add_artifact_node(art_id, artifact_nodes, registry)
        edge_counter[0] += 1
        edges.append({"data": {
            "id": f"e{edge_counter[0]}",
            "source": _skill_id(skill_name),
            "target": art_id,
            "type": "produces",
        }})
        schema_path = item.get("schema", "")
        if schema_path:
            edges.extend(_build_schema_ref_edge(
                _skill_id(skill_name), schema_path, edge_counter
            ))
    return edges


def _build_consumes_edges(
    skill_name: str,
    contract: dict[str, Any],
    artifact_nodes: dict[str, dict[str, Any]],
    edge_counter: list[int],
    registry: dict[str, str],
) -> list[dict[str, Any]]:
    """Build consumes-type edges from a contract's derived_from block."""
    edges: list[dict[str, Any]] = []
    derived_block = contract.get("derived_from", {}) or {}
    for item in _contract_items(derived_block, "required", "optional"):
        path = item.get("path", "")
        if not path:
            continue
        art_id = _artifact_id(path)
        _add_artifact_node(art_id, artifact_nodes, registry)
        edge_counter[0] += 1
        edges.append({"data": {
            "id": f"e{edge_counter[0]}",
            "source": _skill_id(skill_name),
            "target": art_id,
            "type": "consumes",
        }})
        schema_path = item.get("schema", "")
        if schema_path:
            edges.extend(_build_schema_ref_edge(
                _skill_id(skill_name), schema_path, edge_counter
            ))
    return edges


def _build_schema_ref_edge(
    source_id: str,
    schema_path: str,
    edge_counter: list[int],
) -> list[dict[str, Any]]:
    """Build a schema_ref edge from source to the schema node."""
    stem = Path(schema_path).stem
    edge_counter[0] += 1
    return [{"data": {
        "id": f"e{edge_counter[0]}",
        "source": source_id,
        "target": _schema_id(stem),
        "type": "schema_ref",
    }}]


def _build_invoke_edges(
    skill_name: str,
    contract: dict[str, Any],
    edge_counter: list[int],
) -> list[dict[str, Any]]:
    """Build invokes-type edges from may_invoke list."""
    edges: list[dict[str, Any]] = []
    for target in contract.get("may_invoke", []) or []:
        if isinstance(target, str):
            target_clean = target.split("#")[0].strip()
            if target_clean:
                edge_counter[0] += 1
                edges.append({"data": {
                    "id": f"e{edge_counter[0]}",
                    "source": _skill_id(skill_name),
                    "target": _skill_id(target_clean),
                    "type": "invokes",
                }})
    return edges


def _build_script_call_edges(
    skill_name: str,
    contract: dict[str, Any],
    artifact_nodes: dict[str, dict[str, Any]],
    edge_counter: list[int],
    registry: dict[str, str],
) -> list[dict[str, Any]]:
    """Build script_call edges from side_effects where target starts with scripts/."""
    edges: list[dict[str, Any]] = []
    for effect in contract.get("side_effects", []) or []:
        if not isinstance(effect, dict):
            continue
        target = effect.get("target", "")
        if "<" in target:
            continue
        if target.startswith("scripts/"):
            art_id = _artifact_id(target)
            _add_artifact_node(art_id, artifact_nodes, registry)
            edge_counter[0] += 1
            edges.append({"data": {
                "id": f"e{edge_counter[0]}",
                "source": _skill_id(skill_name),
                "target": art_id,
                "type": "script_call",
            }})
    return edges


def build_graph(
    project_root: Path,
    heat: dict[str, float],
    registry: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build the full Cytoscape node/edge lists from the project's skill contracts.

    Returns (nodes, edges).
    """
    if registry is None:
        registry = load_artifact_registry(project_root)
    skill_dirs = collect_skill_dirs(project_root)
    schema_files = collect_schema_files(project_root)

    nodes: list[dict[str, Any]] = []
    artifact_nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    edge_counter = [0]

    # Schema nodes first
    nodes.extend(build_schema_nodes(schema_files))

    for skill_dir in skill_dirs:
        contract_path = skill_dir / "contract.yaml"
        contract: dict[str, Any] | None = None
        if contract_path.exists():
            try:
                loaded = yaml.safe_load(contract_path.read_text())
                contract = loaded if isinstance(loaded, dict) else None
            except yaml.YAMLError as exc:
                sys.stderr.write(
                    f"WARNING: failed to parse {contract_path}: {exc}\n"
                )
        else:
            sys.stderr.write(
                f"WARNING: {skill_dir.name}/contract.yaml not found — "
                "skill added as unmanaged node\n"
            )

        nodes.append(build_skill_node(skill_dir, contract, heat))

        if contract is None:
            continue

        skill_name = skill_dir.name
        edges.extend(_build_produces_edges(skill_name, contract, artifact_nodes, edge_counter, registry))
        edges.extend(_build_consumes_edges(skill_name, contract, artifact_nodes, edge_counter, registry))
        edges.extend(_build_invoke_edges(skill_name, contract, edge_counter))
        edges.extend(_build_script_call_edges(skill_name, contract, artifact_nodes, edge_counter, registry))

    nodes.extend(artifact_nodes.values())
    return nodes, edges


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

_FAMILIES = ["code", "ui", "requ", "task", "claude", "ux", "release", "doc", "verify", "other"]


def _build_family_checkboxes() -> str:
    parts = []
    for fam in _FAMILIES:
        parts.append(
            f'<label><input type="checkbox" class="fam-cb" value="{fam}" checked> {fam}</label>'
        )
    return "\n".join(parts)


def _build_artifact_type_checkboxes(categories: list[str]) -> str:
    parts = []
    for cat in categories:
        label = cat.replace("-", " ")
        parts.append(
            f'<label><input type="checkbox" class="art-cb" value="{_html.escape(cat)}" checked>'
            f' {_html.escape(label)}</label>'
        )
    return "\n".join(parts)


def _build_node_selector_options(nodes: list[dict[str, Any]]) -> str:
    parts = ['<option value="">-- select --</option>']
    for node in nodes:
        d = node["data"]
        nid = d["id"]
        label = d.get("label", nid)
        parts.append(
            f'<option value="{_html.escape(nid)}">'
            f'{_html.escape(label)} ({d.get("type","?")})</option>'
        )
    return "\n".join(parts)


def build_html(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    art_categories: list[str] | None = None,
) -> str:
    """Render the Cytoscape.js HTML viewer as a self-contained string."""
    if art_categories is None:
        art_categories = sorted({
            n["data"].get("art_type", "other")
            for n in nodes if n["data"].get("type") == "artifact"
        }) or ["other"]
    graph_json = json.dumps({"nodes": nodes, "edges": edges}, indent=2)
    family_checkboxes = _build_family_checkboxes()
    artifact_checkboxes = _build_artifact_type_checkboxes(art_categories)
    node_selector_options = _build_node_selector_options(nodes)
    n_nodes = len(nodes)
    n_edges = len(edges)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Factory Map</title>
<script src="{CYTOSCAPE_CDN}"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ display: flex; height: 100vh; font-family: sans-serif; font-size: 13px; }}
#sidebar {{ width: 260px; min-width: 220px; overflow-y: auto; padding: 10px;
           border-right: 1px solid #ccc; background: #f8f8f8; }}
#cy-wrap {{ flex: 1; display: flex; flex-direction: column; }}
#cy {{ flex: 1; }}
#statusbar {{ padding: 4px 10px; background: #222; color: #eee; font-size: 12px; }}
h2 {{ font-size: 14px; margin-bottom: 6px; }}
.panel {{ margin-bottom: 14px; padding: 8px; background: #fff;
          border: 1px solid #ddd; border-radius: 4px; }}
.panel h3 {{ font-size: 13px; margin-bottom: 6px; color: #333; }}
label {{ display: block; margin: 2px 0; cursor: pointer; }}
input[type=number] {{ width: 50px; }}
select {{ width: 100%; margin: 4px 0; }}
button {{ margin-top: 4px; padding: 3px 8px; cursor: pointer; }}
.filter-actions {{ margin-bottom: 4px; }}
.filter-actions button {{ margin: 0 2px 0 0; padding: 1px 6px; font-size: 11px; }}
#tooltip {{ position: absolute; background: rgba(0,0,0,0.75); color: #fff;
            padding: 6px 10px; border-radius: 4px; font-size: 12px;
            pointer-events: none; display: none; z-index: 9999; }}
</style>
</head>
<body>
<div id="sidebar">
  <h2>Factory Map</h2>
  <div class="panel">
    <h3>Legend</h3>
    <label><span style="display:inline-block;width:12px;height:12px;background:#4a90d9;border-radius:50%;"></span> Skill (managed)</label>
    <label><span style="display:inline-block;width:12px;height:12px;background:#aaa;border-radius:50%;"></span> Skill (unmanaged)</label>
    <label><span style="display:inline-block;width:12px;height:12px;background:#5cb85c;border-radius:2px;"></span> Artifact</label>
    <label><span style="display:inline-block;width:12px;height:12px;background:#f0a30a;border-radius:2px;"></span> Schema</label>
  </div>
  <div class="panel">
    <h3>Filter: Family</h3>
    <div class="filter-actions">
      <button id="fam-all">All</button><button id="fam-none">None</button>
    </div>
    {family_checkboxes}
  </div>
  <div class="panel">
    <h3>Filter: Artifact Type</h3>
    <div class="filter-actions">
      <button id="art-all">All</button><button id="art-none">None</button>
    </div>
    {artifact_checkboxes}
  </div>
  <div class="panel">
    <h3>Filter: Distance</h3>
    <label>From node:
      <select id="dist-node">{node_selector_options}</select>
    </label>
    <label>Max hops: <input type="number" id="dist-hops" min="{MIN_DISTANCE}" max="{MAX_DISTANCE}" value="2"></label>
    <button id="dist-apply">Apply</button>
    <button id="dist-reset">Reset</button>
  </div>
</div>
<div id="cy-wrap">
  <div id="cy"></div>
  <div id="statusbar">Loading...</div>
</div>
<div id="tooltip"></div>

<script>
const GRAPH_DATA = {graph_json};
const TOTAL_NODES = {n_nodes};
const TOTAL_EDGES = {n_edges};

function heatColor(heat) {{
  if (heat <= 0) return null;
  const r = Math.round(70 + heat * 185);
  const g = Math.round(144 - heat * 144);
  const b = Math.round(217 - heat * 217);
  return `rgb(${{r}},${{g}},${{b}})`;
}}

function nodeColor(d) {{
  if (d.type === 'artifact') return '#5cb85c';
  if (d.type === 'schema') return '#f0a30a';
  if (!d.has_contract) return '#aaa';
  const hc = heatColor(d.heat || 0);
  return hc || '#4a90d9';
}}

function artifactTypeClass(d) {{
  return d.art_type || 'other';
}}

const cy = cytoscape({{
  container: document.getElementById('cy'),
  elements: GRAPH_DATA,
  style: [
    {{ selector: 'node', style: {{
        'background-color': ele => nodeColor(ele.data()),
        'label': 'data(label)',
        'font-size': '10px',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-background-color': '#fff',
        'text-background-opacity': 0.85,
        'text-background-padding': '2px',
        'text-background-shape': 'round-rectangle',
        'width': ele => ele.data('type') === 'skill' ? 20 : 14,
        'height': ele => ele.data('type') === 'skill' ? 20 : 14,
        'shape': ele => ele.data('type') === 'artifact' ? 'rectangle' :
                        ele.data('type') === 'schema' ? 'diamond' : 'ellipse',
    }}}},
    {{ selector: 'edge', style: {{
        'width': 1,
        'line-color': 'rgba(153,153,153,0.6)',
        'target-arrow-color': 'rgba(153,153,153,0.6)',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(type)',
        'font-size': '9px',
        'text-rotation': 'autorotate',
        'color': '#111',
        'text-background-color': '#fff',
        'text-background-opacity': 1,
        'text-background-padding': '4px',
        'text-background-shape': 'round-rectangle',
        'text-border-width': 0.5,
        'text-border-color': '#bbb',
        'text-border-opacity': 1,
        'min-zoomed-font-size': 8,
    }}}},
    {{ selector: 'edge[type="produces"]', style: {{ 'line-color': 'rgba(92,184,92,0.6)', 'target-arrow-color': 'rgba(92,184,92,0.6)' }} }},
    {{ selector: 'edge[type="consumes"]', style: {{ 'line-color': 'rgba(74,144,217,0.6)', 'target-arrow-color': 'rgba(74,144,217,0.6)' }} }},
    {{ selector: 'edge[type="invokes"]', style: {{ 'line-color': 'rgba(155,89,182,0.6)', 'target-arrow-color': 'rgba(155,89,182,0.6)', 'line-style': 'dashed' }} }},
    {{ selector: 'edge[type="script_call"]', style: {{ 'line-color': 'rgba(230,126,34,0.6)', 'target-arrow-color': 'rgba(230,126,34,0.6)' }} }},
    {{ selector: 'edge[type="schema_ref"]', style: {{ 'line-color': 'rgba(240,163,10,0.6)', 'target-arrow-color': 'rgba(240,163,10,0.6)', 'line-style': 'dotted' }} }},
    {{ selector: '.highlighted', style: {{ 'line-color': '#e74c3c', 'target-arrow-color': '#e74c3c', 'width': 2 }} }},
    {{ selector: '.faded', style: {{ 'opacity': 0.1 }} }},
  ],
  layout: {{ name: 'cose', idealEdgeLength: 160, nodeOverlap: 20, refresh: 20,
             fit: true, padding: 60, randomize: false, componentSpacing: 300,
             nodeRepulsion: 800000, edgeElasticity: 100, nestingFactor: 5,
             gravity: 20, numIter: 2000, initialTemp: 1000, coolingFactor: 0.95 }},
}});

function updateStatusBar() {{
  const vis = cy.elements(':visible');
  const vn = vis.nodes().length;
  const ve = vis.edges().length;
  document.getElementById('statusbar').textContent =
    `${{TOTAL_NODES}} nodes, ${{TOTAL_EDGES}} edges  |  visible: ${{vn}} nodes, ${{ve}} edges`;
}}

// Tooltip
const tooltip = document.getElementById('tooltip');
cy.on('mouseover', 'node', evt => {{
  const d = evt.target.data();
  const heat = (d.heat || 0).toFixed(3);
  tooltip.innerHTML = `<b>${{d.id}}</b><br>type: ${{d.type}}<br>heat: ${{heat}}`;
  tooltip.style.display = 'block';
}});
cy.on('mouseout', 'node', () => {{ tooltip.style.display = 'none'; }});
cy.on('mousemove', evt => {{
  tooltip.style.left = (evt.renderedPosition.x + 15) + 'px';
  tooltip.style.top = (evt.renderedPosition.y + 15) + 'px';
}});

// Click to highlight edges
cy.on('tap', 'node', evt => {{
  cy.elements().removeClass('highlighted faded');
  const node = evt.target;
  const connected = node.connectedEdges();
  connected.addClass('highlighted');
  cy.elements().not(connected).not(node).not(connected.connectedNodes()).addClass('faded');
  document.getElementById('dist-node').value = node.data('id');
}});
cy.on('tap', evt => {{
  if (evt.target === cy) cy.elements().removeClass('highlighted faded');
}});

// Family filter
function applyFilters() {{
  const activeFamilies = new Set(
    [...document.querySelectorAll('.fam-cb:checked')].map(c => c.value)
  );
  const activeArtTypes = new Set(
    [...document.querySelectorAll('.art-cb:checked')].map(c => c.value)
  );
  cy.nodes().forEach(n => {{
    const d = n.data();
    if (d.type === 'skill') {{
      n.style('display', activeFamilies.has(d.family) ? 'element' : 'none');
    }} else if (d.type === 'artifact') {{
      const cls = artifactTypeClass(d);
      n.style('display', activeArtTypes.has(cls) ? 'element' : 'none');
    }}
  }});
  cy.edges().forEach(e => {{
    const src = e.source().style('display');
    const tgt = e.target().style('display');
    e.style('display', src !== 'none' && tgt !== 'none' ? 'element' : 'none');
  }});
  updateStatusBar();
}}

document.querySelectorAll('.fam-cb, .art-cb').forEach(cb => {{
  cb.addEventListener('change', applyFilters);
}});

function setAll(cls, checked) {{
  document.querySelectorAll(cls).forEach(cb => {{ cb.checked = checked; }});
  applyFilters();
}}
document.getElementById('fam-all').addEventListener('click', () => setAll('.fam-cb', true));
document.getElementById('fam-none').addEventListener('click', () => setAll('.fam-cb', false));
document.getElementById('art-all').addEventListener('click', () => setAll('.art-cb', true));
document.getElementById('art-none').addEventListener('click', () => setAll('.art-cb', false));

// Distance filter
document.getElementById('dist-apply').addEventListener('click', () => {{
  const nodeId = document.getElementById('dist-node').value;
  const hops = parseInt(document.getElementById('dist-hops').value, 10);
  if (!nodeId) return;
  const root = cy.getElementById(nodeId);
  if (!root.length) return;
  const nearby = root.closedNeighborhood().add(
    root.successors().filter(e => e.data('type') !== undefined)
  );
  let frontier = root;
  let reachable = root;
  for (let i = 0; i < hops; i++) {{
    frontier = frontier.neighborhood().not(reachable);
    reachable = reachable.union(frontier);
  }}
  cy.nodes().forEach(n => {{
    n.style('display', reachable.has(n) ? 'element' : 'none');
  }});
  cy.edges().forEach(e => {{
    const src = e.source().style('display');
    const tgt = e.target().style('display');
    e.style('display', src !== 'none' && tgt !== 'none' ? 'element' : 'none');
  }});
  updateStatusBar();
}});

document.getElementById('dist-reset').addEventListener('click', () => {{
  cy.elements().style('display', 'element');
  applyFilters();
}});

cy.ready(updateStatusBar);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a static HTML factory map from skill contracts."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output HTML path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--heat-data",
        dest="heat_data",
        default=None,
        help="Path to JSON file with heat data (format: {by_file: {path: {reads: N}}})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    args = _parse_args(argv)
    project_root = Path(__file__).parent.parent.parent

    raw_heat: dict[str, float] = {}
    if args.heat_data:
        raw_heat = load_heat_data(Path(args.heat_data))

    heat = normalize_heat(raw_heat)
    nodes, edges = build_graph(project_root, heat)

    html = build_html(nodes, edges)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = project_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    print(f"Factory map written to {output_path} ({len(nodes)} nodes, {len(edges)} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
