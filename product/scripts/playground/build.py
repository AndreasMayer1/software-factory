"""Build/maintain mode for the Skill-Test Playground (REQ-PROC-068 AC-11/13/14/17).

Additive sibling to run_skeleton.py's test-and-reset mode (AC-07): instead of
resetting the harness back to a clean baseline after each run, build mode
derives the harness's own product-definition layers **inside an isolated
deployed copy**, then **harvests** the registry-classified product-definition
artifacts back into the persistent `test_harness_app/` tree, retaining them.

Why the isolated copy is a durable git-backed workspace under .worktree/, NOT
a /tmp dir (AC-13):
  Build mode reuses the SAME ephemeral-workspace convention run_skeleton.py
  already uses (`workspace.py::create_workspace` + `init_workspace_git`): the
  copy is a `playground_ws_<uuid8>` directory under `<repo>/.worktree/`,
  resolved by `worktree_root.py` (+ optional `worktree.config.json`) rather
  than an OS temp directory. This makes the copy its own git repository, so
  the inner orchestrator deployed into it can run git-backed derivation, and
  it lives at the configured durable location instead of `tempfile.mkdtemp()`
  — the divergence the resumability synthesis (SOL-02, §G2-1) identified as
  the bug.
  Source: requirements_tasks/process/AI_rules/factory_extraction/
  epic_skill_test_playground/tasks/2026-07-08_explore_build-mode-resumability
  (completed)/plans_and_protocols/2026-07-09_006_synthesis_v2.md

Why the harvest is COMPLETION-GATED and the copy is preserved by default
(AC-14, HIGH-consequence):
  Harvest + discard run ONLY when an injected completion predicate over the
  copy returns complete AND the child session succeeded AND it terminated by a
  clean exit (`reason == 'exited'`). On ANY other termination — a hang, a
  timeout, a non-zero exit, a usage-limit kill, or a not-yet-complete predicate
  — build mode PRESERVES the copy and skips the harvest entirely
  (preserve-by-default, discard-only-on-verified-complete). This is fail-safe:
  a partially-derived copy is never harvested (which would leak half-work into
  test_harness_app/) and never discarded (which would lose resumable state).

Why the run registry is written status=running BEFORE launch:
  A tree-wide usage limit can kill the wrapper AFTER launch but BEFORE the
  completion gate runs (ADV-synthesize-gate-02). Recording the durable copy
  path + status=running up front means a later cold session (T2,
  TASK-PROC-068-22) can re-attach to the preserved copy. build mode itself only
  WRITES the record here; the cold-session re-attach/resume READ side is T2.

Why the completion predicate is INJECTED, not hard-coded (AC-17):
  Layer-derivation's "ChainState complete" is ONE instance of the gate, not the
  gate itself. run_build_mode takes a `completion_predicate` over the copy path;
  any long build-mode run supplies its own. When none is injected the gate
  reduces to succeeded + clean-exit — a safe generic default.

Why the isolated copy must be seeded from test_harness_app's current state:
  `deploy_candidate` deliberately excludes `requirements_user_needs/` and
  `requirements_tasks/{functional,non-functional}/` (app-owned product
  content, not factory machinery) — see deploy.py's `_TOP_LEVEL_EXCLUDES` /
  `_SUBFOLDER_EXCLUDES`. `create_workspace` seeds the copy from
  test_harness_app's current tree, then deploy overlays the factory machinery
  on top (deploy's excludes leave the seeded product content untouched, so the
  overlay never collides). `sync_product_definition` then confirms the
  registry-classified product-definition content is present and records it in
  the manifest's `seeded_paths`.
  Source: same synthesis, §"The genuinely-new work".

Why the harvest classification is registry-driven, not a hand-maintained list:
  `.factory/registry/artifacts.yaml` already designates every artifact token
  with a `category:`. Product-definition categories are `user-needs`,
  `requirements`, `scribble`, and `source-code` (goal.md's own wording).
  Walking the registry means factory growth (a new token added to the
  registry) is classified automatically; a hand-maintained file list would
  silently drift out of sync with the registry as new categories/tokens land.

Why discard is `destroy_workspace`, never `git reset`:
  Discard goes through `workspace.py::destroy_workspace`, whose own-prefix
  safety guard refuses any path whose basename does not start with
  `playground_ws_` — so it can only ever remove a workspace this module made,
  never the host project, the harness seed, or an enclosing directory. It is a
  plain recursive delete, never `git reset`: the topology hazard T-B
  (TASK-PROC-068-16) makes a git-reset scoped at an in-tree path resolve to the
  OUTER repo root and nuke the whole factory repo. A directory delete has no
  such ambiguity (C1).

Output:
  Prints one JSON manifest object to stdout on success:
    {
      "seeded_paths": [...], "harvested_paths": [...],
      "completed": bool, "workspace_preserved": <path|null>,
      "run_registry_path": "...",
      "advisory": "...", "max_budget_usd": ..., "total_cost_usd": ...,
      "total_duration_ms": ..., "over_budget": ..., "run_count": ...,
      "runs": [...]
    }
  Writes progress/errors to stderr via logging. Exit 0 on success, 1 on error.
"""

# tier: C  # one-shot CLI orchestrator, mirrors run_skeleton.py's tier

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import uuid as _uuid_mod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from scripts.dev_env.worktree_root import worktree_root
from scripts.ideation.index_session import load_index, save_index
from scripts.playground.containment import (
    ContainmentUnavailable,
    wrap_with_containment,
)
from scripts.playground.cost_ledger import (
    BudgetExceeded,
    CostLedger,
    check_budget,
    record_run,
)
from scripts.playground.deploy import deploy_candidate
from scripts.playground.launch_adapter import (
    LaunchDeps,
    LaunchRequest,
    LaunchResult,
    run_with_hung_detection,
)
from scripts.playground.workspace import (
    MAINTENANCE_BRANCH,
    compact_workspace_git,
    create_workspace,
    destroy_workspace,
    export_workspace_git_bundle,
    harness_git_bundle_path,
    init_workspace_git,
    restore_workspace_git,
)
from scripts.user_needs.check_materialization_provenance import DECIDED_BY_RE
from scripts.util.task_folder_resolver import resolve_task_folder_path

_LOG = logging.getLogger(__name__)

DEFAULT_MAX_BUDGET_USD = 2.00
DEFAULT_MODEL = "claude-sonnet-4-5"

# Registry path relative to host_project_dir — the factory's own controlled
# vocabulary of artifact categories (REQ-PROC-044-02).
DEFAULT_REGISTRY_RELPATH = ".factory/registry/artifacts.yaml"

# Product-definition categories per goal.md — the subset of registry
# categories that build mode harvests back into test_harness_app/. Everything
# else (factory-skills, scripts, automation, factory-runtime, doc, …) is
# transient deployed machinery, left behind in the discarded isolated copy.
_PRODUCT_DEFINITION_CATEGORIES = frozenset(
    {"user-needs", "requirements", "scribble", "source-code"}
)

# Run-registry (AC-14 durable state). The registry lives OUT of the project
# tree — a sibling dir under the workspace root — so it survives the workspace
# discard and is reachable by a later cold session (T2). It is deliberately NOT
# `.factory/playground/runs/` inside the tree (the synthesis, §G2-1, rejected
# that in-tree location).
#
# Public aliases (T2, TASK-PROC-068-22): build_resume.py reads these constants
# to interpret a registry record without importing a leading-underscore
# private name across modules. The private names are kept as aliases so any
# existing in-module reference (and G4/G1 lint expectations on this file's own
# history) still resolves.
RUN_REGISTRY_DIRNAME = ".playground_runs"
RUN_STATUS_RUNNING = "running"
RUN_STATUS_COMPLETE = "complete"
RUN_STATUS_PRESERVED = "preserved"
# Terminal statuses for the three clean-exit-but-not-complete outcomes (AC-18).
# They are deliberately DISTINCT from RUN_STATUS_PRESERVED so build_resume's
# _RESUMABLE_STATUSES ({running, preserved}) never auto-resumes them: a
# blocked/abandoned/inconclusive run must NOT be re-launched (resume cannot fix a
# skill that stopped early — it would loop forever).
RUN_STATUS_BLOCKED = "blocked"
RUN_STATUS_ABANDONED = "abandoned"
RUN_STATUS_INCONCLUSIVE = "inconclusive"
_RUN_REGISTRY_DIRNAME = RUN_REGISTRY_DIRNAME
_RUN_STATUS_RUNNING = RUN_STATUS_RUNNING
_RUN_STATUS_COMPLETE = RUN_STATUS_COMPLETE
_RUN_STATUS_PRESERVED = RUN_STATUS_PRESERVED


class RunOutcome(str, Enum):
    """The exactly-one classified outcome of a build/maintain run (AC-18/AC-19).

    Named outcomes over bool (doc/python/architecture.md §Structural rule 2): the
    gate has five meaningful cases, only one of which (COMPLETE) is harvested.

    COMPLETE     — clean child exit AND the injected acceptance oracle confirms
                   the derivation finished. The ONLY harvested outcome.
    INTERRUPTED  — non-clean termination (usage-limit / timeout / hung / crash).
                   Preserve the copy for resume (AC-14/15/16).
    BLOCKED      — clean exit AND an explicit blocker/escalation artifact was
                   recorded in the copy. A developer-facing pause: NOT harvested,
                   NOT a failure of the skill under test.
    ABANDONED    — clean exit, the oracle reports not-finished, NO blocker
                   artifact, AND at least one unit with REAL authoring pairs is
                   left non-terminal (AC-18's D1 narrowing). A run failure
                   attributable to the skill-under-test's completion guidance:
                   NOT harvested, NOT auto-resumed.
    INCONCLUSIVE — AC-19 fail-safe: EITHER no oracle was injected ("cannot
                   certify complete"), OR the oracle reports not-finished but NO
                   real-authoring unit is left non-terminal (only structurally
                   degenerate no-op spans remain — never blamed on the skill
                   under test, AC-18, yet not positively certifiable, AC-19).
                   Never harvested, never reported successful. The second case
                   is reachable in practice only from legacy un-migrated state
                   (a degenerate span parked short of VACUOUS_COMPLETE) — see
                   plan D1.
    """

    COMPLETE = "complete"
    INTERRUPTED = "interrupted"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"
    INCONCLUSIVE = "inconclusive"


# Map each non-complete outcome to the terminal run-registry status it records.
# COMPLETE is intentionally absent — its record is flipped to RUN_STATUS_COMPLETE
# by the harvest branch itself, alongside the harvested_count detail.
_OUTCOME_TO_PRESERVE_STATUS: dict[RunOutcome, str] = {
    RunOutcome.INTERRUPTED: RUN_STATUS_PRESERVED,
    RunOutcome.BLOCKED: RUN_STATUS_BLOCKED,
    RunOutcome.ABANDONED: RUN_STATUS_ABANDONED,
    RunOutcome.INCONCLUSIVE: RUN_STATUS_INCONCLUSIVE,
}

# Injected-oracle kind selectable from the CLI (--acceptance-oracle). "chainstate"
# resolves to acceptance_oracles.chainstate_complete_predicate over the copy.
ACCEPTANCE_ORACLE_CHAINSTATE = "chainstate"

# Relative path, under the isolated copy, of the pending_feedback questions an
# escalating skill-under-test records — the generic BLOCKED signal (any factory
# skill escalates through automation/pending_feedback via claude-automated-mode).
_PENDING_FEEDBACK_GLOB = "automation/pending_feedback/*/question.md"

# Sidecar filename suffix for the persisted pre-child baseline snapshot
# (Deliverable 1): kept separate from the main record so the record itself
# stays small and human-readable; the record only stores the sidecar's path
# (`baseline_snapshot_ref`). build_resume.list_runs excludes files matching
# this suffix when it globs the registry dir for run records.
BASELINE_SIDECAR_SUFFIX = ".baseline.json"

# The clean-exit reason a successful child session reports (launch_adapter).
_REASON_EXITED = "exited"

# AC-22 doomed-spec plan-time exit code. Distinct from every existing exit code
# this CLI (and build_resume.py's CLI) can return: 0 (success), 1 (generic
# operational failure — BudgetExceeded/ContainmentUnavailable/OSError/ValueError/
# RuntimeError), and build_resume.py's own FENCE_EXIT_FENCED (3, an unrelated
# fence-check verdict on a DIFFERENT CLI subcommand). A doomed-spec rejection is
# neither a generic failure nor a fence — it is a plan-time verdict the caller
# must be able to distinguish from "something broke" (AC-22).
EXIT_DOOMED_SPEC = 2


class DoomedSpecError(RuntimeError):
    """Raised when the AC-22 harvestability pre-flight predicts a spec can never be harvested.

    Carries the pre-flight's teaching-quality error messages (SpecLintResult.errors,
    reused verbatim from backfill_orchestration.lint_spec) so main() can surface WHY
    the spec was rejected, not just that it was. Raised BEFORE any workspace is
    prepared/deployed (run_build_mode) or before a resume reaches the launch->gate
    tail (build_resume.resume_run) — a doomed spec consumes no deployed run.
    """

    def __init__(self, errors: tuple[str, ...]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors) or "doomed spec: pre-flight rejected")


# ---------------------------------------------------------------------------
# Registry-driven glob loading
# ---------------------------------------------------------------------------


def load_product_definition_globs(registry_path: str) -> list[str]:
    """Return the path: globs for every registry entry classified as product-definition.

    Parses `.factory/registry/artifacts.yaml` via ruamel.yaml (the canonical
    yaml-parse-serialize library, REQ-PROC-070 — never a hand-rolled parser,
    G4). Skips the `_categories` documentation block and any non-dict entry.

    Args:
        registry_path: Path to the artifacts registry YAML file.

    Returns:
        List of glob-pattern strings (registry `path:` values) whose
        `category:` is one of user-needs, requirements, scribble, source-code.

    Raises:
        FileNotFoundError: If registry_path does not exist.
    """
    path = Path(registry_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Artifact registry not found: {path}. "
            "Cannot classify product-definition artifacts for harvest."
        )

    yaml = YAML(typ="safe")
    data = yaml.load(path.read_text(encoding="utf-8")) or {}

    globs: list[str] = []
    for token, entry in data.items():
        if token == "_categories" or not isinstance(entry, dict):
            continue
        if entry.get("category") in _PRODUCT_DEFINITION_CATEGORIES:
            entry_path = entry.get("path")
            if entry_path:
                globs.append(entry_path)
    return globs


# ---------------------------------------------------------------------------
# Registry-driven sync (used both for seed and for harvest)
# ---------------------------------------------------------------------------


def sync_product_definition(
    src_root: str, dst_root: str, globs: list[str]
) -> list[str]:
    """Copy every path matching a glob from src_root into dst_root (merge).

    Used in BOTH directions by run_build_mode: seed (test_harness_app ->
    isolated copy) and harvest (isolated copy -> test_harness_app) — same
    classification logic, opposite src/dst, so the registry-driven rule is
    defined once (see module docstring).

    Args:
        src_root: Root directory to search for glob matches.
        dst_root: Root directory to copy matches into (merged, not wiped).
        globs: Glob patterns (as found in artifacts.yaml `path:` values).
            A trailing "/" (directory-only tokens, e.g. scribble version
            sets) is stripped before globbing — pathlib.Path.glob does not
            accept a trailing separator.

    Returns:
        Relative path strings (POSIX-style) copied, in first-seen order,
        deduplicated (dict.fromkeys — a later match of an already-copied
        path is not re-listed).
    """
    src = Path(src_root)
    dst = Path(dst_root)

    copied: dict[str, None] = {}
    for pattern in globs:
        normalized = pattern.rstrip("/")
        for match in sorted(src.glob(normalized)):
            rel = match.relative_to(src)
            rel_posix = rel.as_posix()
            target = dst / rel
            if match.is_dir():
                shutil.copytree(match, target, dirs_exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(match, target)
            copied[rel_posix] = None

    return list(copied)


# ---------------------------------------------------------------------------
# Net-new harvest — copy back ONLY what the child authored (REQ-PROC-068-19)
# ---------------------------------------------------------------------------


def _iter_product_definition_files(
    root: str, globs: list[str]
) -> Iterator[tuple[Path, str]]:
    """Yield (file_path, rel_posix) for every FILE matching a product-def glob.

    Directory matches (trailing-"/" tokens, e.g. scribble version sets) are
    expanded to the files they contain via rglob, so the net-new harvest can
    diff and copy at file granularity — shutil.copytree cannot filter by
    per-file content hash. First-seen order; each rel path is yielded once.
    """
    src = Path(root)
    seen: set[str] = set()
    for pattern in globs:
        normalized = pattern.rstrip("/")
        for match in sorted(src.glob(normalized)):
            candidates = (
                sorted(match.rglob("*")) if match.is_dir() else [match]
            )
            for f in candidates:
                if not f.is_file():
                    continue
                rel_posix = f.relative_to(src).as_posix()
                if rel_posix in seen:
                    continue
                seen.add(rel_posix)
                yield f, rel_posix


def _hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's bytes (content identity).

    Bytes, not text: content identity must be newline-exact (see
    doc/python/anti_patterns.md "Text-mode file copy") — a hash over decoded
    text would call a CRLF and an LF copy identical.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_product_definition(root: str, globs: list[str]) -> dict[str, str]:
    """Map every product-def file under root to its content hash (harvest baseline).

    Taken AFTER deploy+seed but BEFORE the child runs, so the baseline captures
    BOTH deploy-brought factory machinery and seeded harness content. harvest
    then copies only files absent-or-changed vs. this baseline — i.e. exactly
    what the child authored (Option B, REQ-PROC-068-19).

    Why this and not "widen deploy excludes": several residual files
    (`_meta/id_registry.md`, `_scribble_components/*/metadata.yaml`, …) are
    harness-RUNTIME inputs read by skills that run in the harness, so dropping
    them from the deployed copy would risk AC-10. Scoping the HARVEST instead
    keeps the deployed copy whole (AC-10-safe) yet stops ALL deploy/seed residue
    — not just the process/ corpus — from leaking into test_harness_app/.
    """
    return {
        rel: _hash_file(f)
        for f, rel in _iter_product_definition_files(root, globs)
    }


def harvest_authored(
    src_root: str, dst_root: str, globs: list[str], baseline: dict[str, str]
) -> list[str]:
    """Copy back only the product-def files the child authored (net-new or modified).

    A file is harvested iff its POSIX relpath is absent from ``baseline``
    (net-new) or its content hash differs from the baseline (modified). Files
    byte-identical to the pre-child snapshot — deploy-brought machinery and
    untouched seed — are skipped. This is the Option-B fix for the residual
    harvest over-inclusion that excluding process/ alone did not close
    (REQ-PROC-068-19).

    Returns the relpaths copied, in first-seen order.
    """
    dst = Path(dst_root)
    copied: list[str] = []
    for f, rel_posix in _iter_product_definition_files(src_root, globs):
        if baseline.get(rel_posix) == _hash_file(f):
            continue
        target = dst / rel_posix
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        copied.append(rel_posix)
    return copied


# ---------------------------------------------------------------------------
# AC-11 retention clause — scoped ideation-provenance retention
# ---------------------------------------------------------------------------

# The harness's own materialization singleton relpath (product-definition
# category user-needs). check_materialization_provenance.py's
# _derive_project_root docstring establishes this artifact is always a
# per-project singleton at this exact location, so a literal relpath match
# (no glob) is enough to recognize it among harvest_authored's output.
_MATERIALIZATION_RELPATH = (
    "requirements_user_needs/product_materialization/product_materialization.md"
)
_IDEATION_INDEX_RELPATH = ".factory/ideation/index.yaml"


def _load_materialization_frontmatter(artifact_path: Path) -> dict[str, object]:
    """Parse the `---`-delimited YAML frontmatter of a materialization artifact.

    Duplicated from check_materialization_provenance.py's own private
    ``_load_frontmatter`` (identical shape) rather than importing a
    leading-underscore private helper across modules — the same convention
    ``_derive_jsonl_dir`` documents below for its own duplication, and
    check_materialization_provenance.py is out of scope for this task (goal.md
    Out of Scope: "Editing check_materialization_provenance.py").
    """
    text = artifact_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3 or text.lstrip() != text or not text.startswith("---"):
        raise ValueError("no YAML frontmatter block")
    data = YAML(typ="safe").load(parts[1]) or {}
    return dict(data)


def _upsert_ideation_index_entry(index_path: Path, entry: dict[str, object]) -> None:
    """Insert-or-replace the SINGLE entry with this id in index_path's index.yaml.

    Never touches any other entry — this is the scalpel AC-21 requires: a
    wholesale copy of the workspace's own `.factory/ideation/index.yaml` would
    leak flutter_app's other ideation entries into test_harness_app, defeating
    its standalone-project status. Reuses index_session.py's own
    load_index/save_index round-trip (ruamel.yaml, G4) rather than
    hand-rolling a second index reader/writer — that module already owns
    index.yaml's read/write convention (creates `{entries: []}` when the file
    is absent).
    """
    index = load_index(index_path)
    entries = index["entries"]
    entry_id = entry.get("id")
    for i, existing in enumerate(entries):
        if existing.get("id") == entry_id:
            entries[i] = entry
            break
    else:
        entries.append(entry)
    save_index(index_path, index)


def _copy_ideation_provenance_paths(
    workspace: Path, target_project_dir: Path, entry: dict[str, object]
) -> None:
    """Copy the entry's ledger_path file and task_path folder into target.

    Resolves BOTH stored paths via resolve_task_folder_path (doc/python/
    anti_patterns.md "Literal task-folder path checks that miss a
    status-suffix rename") rather than joining the stored relpath literally —
    a task folder inside the isolated copy can in principle already carry a
    status suffix. The copy destination mirrors the RESOLVED path's relpath
    (via .relative_to(workspace)), not the possibly-stale stored one, so the
    two trees agree on where the content actually lives. Copying the whole
    task_path folder (not just ledger_path) is what makes
    resolve_task_folder_path succeed for `task_path` too on the far side —
    the ledger_path copy is then redundant-but-harmless belt-and-braces.
    """
    task_rel = str(entry.get("task_path") or "").strip()
    if task_rel:
        task_src = resolve_task_folder_path(workspace, task_rel)
        if task_src is not None:
            task_dst = target_project_dir / task_src.relative_to(workspace)
            task_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(task_src, task_dst, dirs_exist_ok=True)

    ledger_rel = str(entry.get("ledger_path") or "").strip()
    if ledger_rel:
        ledger_src = resolve_task_folder_path(workspace, ledger_rel)
        if ledger_src is not None:
            ledger_dst = target_project_dir / ledger_src.relative_to(workspace)
            ledger_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ledger_src, ledger_dst)


def retain_ideation_provenance(
    workspace: str, target_project_dir: str, harvested_relpaths: list[str]
) -> str | None:
    """AC-11 retention clause: scalpel-retain the harness's own ideation provenance.

    A build/maintain run derives the harness's materialization INSIDE the
    isolated copy, so its `decided_by: IDEATION-NNN @ <sha>` provenance points
    at an ideation index entry + ledger that live only in the copy's own
    `.factory/ideation/` (never in test_harness_app, which has no `.factory`
    subsystem runtime — AC-21). check_materialization_provenance.py's
    index-lookup and ledger-read steps need those two things as FILES ON DISK
    after a future redeploy; restore_workspace_git only makes the referenced
    COMMIT reachable (TASK-PROC-068-32/34), it does not check anything out.
    This function is the missing half: it copies exactly the ONE index entry
    (never the workspace's other ideation entries — AC-21) plus its ledger and
    task folder into test_harness_app, at harvest time, so they persist as the
    harness's own project data.
    Source: requirements_tasks/process/AI_rules/factory_extraction/
      epic_skill_test_playground/tasks/2026-07-19_impl_harvest-retain-ideation-provenance/goal.md

    Deliberately narrow (goal.md "Out of Scope"): does NOT add `factory-runtime`
    or `task-workspace` to `_PRODUCT_DEFINITION_CATEGORIES` — that would harvest
    ALL of the copy's ideation history wholesale, not just the one entry a
    harvested materialization actually references.

    Gated on `harvested_relpaths` containing the materialization singleton
    (T-1): a materialization that harvest_authored did NOT copy this run is
    byte-identical to what test_harness_app already has, so its provenance
    (if any) was already retained by a prior run — re-scanning it here would
    be redundant, not incorrect, but the gate keeps this a no-op on the common
    "child touched nothing new" run.

    Never raises (T-1 "harmless no-op"): an absent/unparsable decided_by, or
    an IDEATION id missing from the copy's own index, means the run authored
    no (or unprovenanced) materialization — not a build-mode failure.

    Returns the retained IDEATION-NNN id, or None on any no-op branch.
    """
    if _MATERIALIZATION_RELPATH not in harvested_relpaths:
        return None
    materialization = Path(workspace) / _MATERIALIZATION_RELPATH
    if not materialization.exists():
        return None

    try:
        frontmatter = _load_materialization_frontmatter(materialization)
    except (ValueError, YAMLError) as exc:
        _LOG.info(
            "Ideation-provenance retention skipped (unparsable frontmatter in %s): %s",
            materialization, exc,
        )
        return None

    decided_by = str(frontmatter.get("decided_by") or "").strip()
    match = DECIDED_BY_RE.match(decided_by)
    if not match:
        _LOG.info(
            "Ideation-provenance retention skipped (no resolvable decided_by: %r)",
            decided_by,
        )
        return None
    ideation_id = match.group(1)

    src_index = load_index(Path(workspace) / _IDEATION_INDEX_RELPATH)
    entry = next(
        (e for e in src_index["entries"] if e.get("id") == ideation_id), None
    )
    if entry is None:
        _LOG.info(
            "Ideation-provenance retention skipped: %s not found in workspace's own index",
            ideation_id,
        )
        return None

    target = Path(target_project_dir)
    _upsert_ideation_index_entry(target / _IDEATION_INDEX_RELPATH, entry)
    _copy_ideation_provenance_paths(Path(workspace), target, entry)
    _LOG.info("Retained ideation provenance for %s into %s", ideation_id, target)
    return ideation_id


# ---------------------------------------------------------------------------
# AC-20 harvest-time compaction — referenced-commit collection
# ---------------------------------------------------------------------------

# The two commit-reference shapes this factory records into artifacts — the
# referenced-commit set AC-20's compaction must keep reachable at stable hashes:
#   1. "<ID> @ <sha>" — a materialization artifact's provenance pointer
#      (decided_by: IDEATION-NNN @ <sha>; the shape DECIDED_BY_RE validates in
#      scripts/user_needs/check_materialization_provenance.py, hex{4,40}).
#   2. "commit: <sha>" — a task goal.md's pinned requirements version
#      (requirements_version.commit).
# Over-matching is fail-safe: a false candidate merely preserves more, and any
# candidate that does not resolve in the WORKSPACE repo is dropped inside
# compact_workspace_git. Under-matching would let compaction squash a commit an
# artifact still references. The trailing \b / line anchor keep 64-hex sha256
# content hashes (snapshot values) from matching — a 64-hex run has no word
# boundary within its first 40 chars, so the whole match fails.
_PROVENANCE_REF_PATTERNS = (
    re.compile(r"@\s*([0-9a-f]{4,40})\b"),
    re.compile(r"^\s*commit:\s*['\"]?([0-9a-f]{4,40})['\"]?\s*$", re.MULTILINE),
)
# Task goal.md files carry the pinned-requirements-version refs but are NOT
# product-definition globs — scanned in addition to the harvested files.
_TASK_GOAL_GLOB = "requirements_tasks/**/goal.md"


def _collect_referenced_commits(
    workspace: str, harvested_relpaths: list[str]
) -> set[str]:
    """Raw candidate commit ids the harvested artifacts + task pins reference.

    Scans the harvested files (workspace side — the same bytes the harvest just
    copied) plus every task goal.md under the copy for the reference shapes in
    _PROVENANCE_REF_PATTERNS. Candidates are returned raw; resolution — and the
    foreign-ref filtering it provides (the deployed factory's own goal.md pins
    name factory-repo commits that resolve to nothing here) — happens in
    compact_workspace_git against the workspace repo.
    """
    ws = Path(workspace)
    files = [ws / rel for rel in harvested_relpaths]
    files.extend(sorted(ws.glob(_TASK_GOAL_GLOB)))
    candidates: set[str] = set()
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in _PROVENANCE_REF_PATTERNS:
            candidates.update(match.group(1) for match in pattern.finditer(text))
    return candidates


# ---------------------------------------------------------------------------
# Build-mode configuration (groups params to stay within PLR0913 <= 5)
# ---------------------------------------------------------------------------


@dataclass
class BuildModeConfig:
    """Configuration for a single build/maintain-mode run.

    Why a dataclass: mirrors FixtureConfig in run_skeleton.py — grouping the
    launch/path parameters keeps run_build_mode's own signature within
    PLR0913's <= 5 params limit.
    """

    target_project_dir: str  # test_harness_app: harvest target AND seed source
    host_project_dir: str  # the factory: deploy source
    workspace_root: str  # parent under <repo>/.worktree/ where playground_ws_<uuid8> lives
    session_uuid: str
    prompt: str
    jsonl_dir: str = ""  # defaults to the CCS path derived from the workspace
    max_budget_usd: float = DEFAULT_MAX_BUDGET_USD
    model: str = DEFAULT_MODEL
    registry_path: str = ""  # artifacts.yaml; filled by main() when not given
    run_registry_dir: str = ""  # durable run-registry dir; derived when empty
    # Acceptance-oracle spec (AC-19). Persisted into the run-registry record so a
    # cold resume reconstructs the SAME oracle from the record alone. Empty kind
    # means NO oracle → the gate "cannot certify complete" (INCONCLUSIVE fail-safe).
    acceptance_oracle_kind: str = ""
    chain_state_path: str = ""  # ChainState relpath under the copy (chainstate oracle)
    # AC-22 pre-flight spec input: raw fixed_layers name strings (parsed to the
    # layer_derivation package's Layer enum only inside the boundary-module
    # indirection, acceptance_oracles.harvestability_preflight_verdict — build.py
    # itself never imports Layer, preserving AC-17's layer-derivation-free core).
    # Empty means this run's spec doesn't use the span-screening surface — the
    # pre-flight is Not Applicable (see run_harvestability_preflight).
    fixed_layers: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Run registry (AC-14 durable state) — WRITE side only; T2 owns re-attach reads
# ---------------------------------------------------------------------------


def _run_registry_dir(cfg: BuildModeConfig) -> str:
    """Resolve the durable run-registry directory for this run.

    Defaults to ``<workspace_root>/.playground_runs`` — a sibling of the
    ephemeral workspace under ``.worktree/``, so it survives the workspace
    discard.
    """
    return cfg.run_registry_dir or os.path.join(
        cfg.workspace_root, _RUN_REGISTRY_DIRNAME
    )


def write_run_registry_running(
    cfg: BuildModeConfig,
    workspace: str,
    *,
    jsonl_dir: str,
    baseline: dict[str, str],
) -> str:
    """Record status=running + everything a cold resume needs BEFORE the child launches.

    A tree-wide usage limit can kill the wrapper after launch but before the
    completion gate (ADV-synthesize-gate-02); this record is what lets a later
    cold session (T2, build_resume.py) re-attach WITHOUT re-running
    deploy/seed/snapshot (AC-15). Beyond the original identity fields, the
    record now also carries prompt, jsonl_dir, registry_path,
    workspace_root, and max_budget_usd — resume reconstructs a BuildModeConfig
    from these alone, with no second input.

    The pre-child baseline snapshot is written to a SIDECAR file
    (`<uuid>.baseline.json`) rather than inlined into the record: the baseline
    can be large (one hash entry per product-def file), so keeping it out of
    the main record keeps the record itself small and human-readable while
    `baseline_snapshot_ref` (the sidecar's path) is enough for resume to load
    it back (see `load_baseline` in build_resume.py).

    Returns the record's path.
    """
    registry_dir = _run_registry_dir(cfg)
    os.makedirs(registry_dir, exist_ok=True)

    baseline_path = os.path.join(
        registry_dir, f"{cfg.session_uuid}{BASELINE_SIDECAR_SUFFIX}"
    )
    Path(baseline_path).write_text(json.dumps(baseline, indent=2), encoding="utf-8")

    path = os.path.join(registry_dir, f"{cfg.session_uuid}.json")
    record = {
        "session_uuid": cfg.session_uuid,
        "workspace_path": workspace,
        "target_project_dir": cfg.target_project_dir,
        "host_project_dir": cfg.host_project_dir,
        "model": cfg.model,
        "prompt": cfg.prompt,
        "jsonl_dir": jsonl_dir,
        "registry_path": cfg.registry_path,
        "workspace_root": cfg.workspace_root,
        "max_budget_usd": cfg.max_budget_usd,
        # Persisted so a cold resume rebuilds the SAME acceptance oracle from the
        # record alone (no re-specification) — matching resume's cold-reattach rule.
        "acceptance_oracle_kind": cfg.acceptance_oracle_kind,
        "chain_state_path": cfg.chain_state_path,
        # AC-22 pre-flight spec input + verdict, persisted next to
        # acceptance_oracle_kind for the SAME cold-resume-reconstruction reason.
        # "harvestable" is always True here — run_build_mode raises DoomedSpecError
        # (before this function is ever called) on a negative pre-flight, so no
        # doomed spec's run ever reaches a registry write. build_resume.resume_run
        # does NOT trust this stored bool as-is — it RECOMPUTES the pre-flight from
        # "fixed_layers" on every resume (D4/ADV-sg-06); the field is carried here
        # so that recomputation has its spec input without a second source.
        "fixed_layers": list(cfg.fixed_layers),
        "harvestable": True,
        "baseline_snapshot_ref": baseline_path,
        "status": RUN_STATUS_RUNNING,
        "started_at": datetime.now().astimezone().isoformat(),
    }
    Path(path).write_text(json.dumps(record, indent=2), encoding="utf-8")
    return path


def _update_run_registry(
    path: str, status: str, detail: dict[str, object] | None = None
) -> None:
    """Flip an existing run-registry record to a terminal status (complete/preserved)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["status"] = status
    data["updated_at"] = datetime.now().astimezone().isoformat()
    if detail:
        data.update(detail)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Core orchestration
# ---------------------------------------------------------------------------


def _prepare_workspace(
    cfg: BuildModeConfig, globs: list[str]
) -> tuple[str, list[str], dict[str, str]]:
    """Create the durable git-backed copy under .worktree/, deploy+seed it, snapshot baseline.

    Returns (workspace_path, seeded_relpaths, pre_child_snapshot). Mirrors
    run_skeleton.py's create_workspace -> deploy_candidate -> init_workspace_git
    ordering, then seeds product-definition content and snapshots it so the
    harvest can copy back only what the child authored (Option B).
    """
    # Step 1: create the ephemeral workspace (AC-13), seeded from
    # test_harness_app's current tree — a playground_ws_<uuid8> directory
    # under the worktree root (<repo>/.worktree/), git-init'd below. NEVER a
    # /tmp dir.
    _LOG.info("Step 1: creating workspace under %s", cfg.workspace_root)
    workspace = create_workspace(
        cfg.host_project_dir,
        cfg.target_project_dir,
        cfg.session_uuid,
        workspace_root=cfg.workspace_root,
    )

    # Step 2: overlay the whole factory machinery on top of the seeded copy
    # (deploy's excludes leave the seeded product content untouched).
    _LOG.info("Step 2: deploying candidate factory into %s", workspace)
    deploy_candidate(cfg.host_project_dir, workspace)

    # Step 3: make the copy its own git repository (AC-13) so the inner
    # orchestrator deployed into it can run git-backed derivation. Maintenance
    # mode restores the harness's PERSISTED history when a bundle exists
    # (AC-20 restore-on-deploy: earlier runs' referenced commits stay reachable
    # with stable hashes); only a first-ever run falls back to a fresh init —
    # already on the single-branch convention the harvest-time export persists.
    bundle_path = harness_git_bundle_path(cfg.target_project_dir)
    if os.path.exists(bundle_path):
        _LOG.info(
            "Step 3: restoring workspace git from persisted bundle: %s", bundle_path
        )
        restore_workspace_git(workspace, bundle_path)
    else:
        _LOG.info(
            "Step 3: git-init workspace baseline (no persisted bundle yet): %s",
            workspace,
        )
        init_workspace_git(workspace, initial_branch=MAINTENANCE_BRANCH)

    # Step 4: confirm the registry-classified product-definition content is
    # present and record it for the manifest's seeded_paths.
    _LOG.info("Step 4: syncing product-definition seed from %s", cfg.target_project_dir)
    seeded = sync_product_definition(cfg.target_project_dir, workspace, globs)

    # Step 5: snapshot the pre-child product-def state (deploy-brought + seeded)
    # so the harvest copies back ONLY what the child authored (Option B).
    pre_child_state = snapshot_product_definition(workspace, globs)
    return workspace, seeded, pre_child_state


@dataclass
class _HarvestGateInputs:
    """Post-launch inputs to the completion gate (grouped to keep params <= 5).

    Why a dataclass: the gate needs the copy path, the launch outcome, the
    product-def globs, the pre-child snapshot, and the run-registry record path
    — five related post-launch facts. Grouping them keeps _gate_harvest within
    PLR0913's <= 5 params limit (doc/python/architecture.md §Structural rule 3).
    """

    workspace: str
    result: LaunchResult
    globs: list[str]
    baseline: dict[str, str]
    registry_path: str


def has_recorded_blocker(workspace: str) -> bool:
    """True iff the copy holds an explicit blocker/escalation artifact (AC-18 BLOCKED signal).

    The generic, skill-agnostic escalation convention across the factory is a
    pending_feedback question (any skill under test that hits a developer decision
    writes `automation/pending_feedback/<id>/question.md` via claude-automated-mode).
    Its presence in the isolated copy means the run paused for a developer, so a
    clean child exit must be classified BLOCKED — a developer-facing pause — rather
    than harvested or reported as a skill failure.
    """
    return any(Path(workspace).glob(_PENDING_FEEDBACK_GLOB))


def classify_run_outcome(
    result: LaunchResult,
    workspace: str,
    completion_predicate: Callable[[str], bool] | None,
    blocker_detector: Callable[[str], bool],
    degeneracy_inspector: Callable[[str], bool] | None = None,
) -> RunOutcome:
    """Classify a run into exactly one RunOutcome (AC-18/AC-19). Pure decision logic.

    Precedence (each guard is a distinct AC-18/AC-19 clause):
      1. Non-clean termination dominates → INTERRUPTED (resumable; the AC-14/15/16
         path). "Clean" = the child both exited zero AND reported reason==exited.
      2. Clean exit + a recorded blocker artifact → BLOCKED. Checked BEFORE the
         oracle so a recorded escalation is never harvested over: a false BLOCKED
         merely preserves the copy (safe), a false COMPLETE harvests unfinished
         work (unsafe) — the fail-safe direction.
      3. Clean exit + NO injected oracle → INCONCLUSIVE (AC-19: absent oracle means
         "cannot certify complete"; never harvest, never report success).
      4. Clean exit + oracle confirms finished → COMPLETE.
      5. Clean exit + oracle reports not-finished (oracle-negative) — AC-18's D1
         narrowing decides between ABANDONED and INCONCLUSIVE: a real-authoring
         unit left non-terminal (degeneracy_inspector True, or the inspector is
         ABSENT — the pre-D1 fail-safe default, so the gate never weakens for an
         unwired run) → ABANDONED (blamed on the skill under test); NO
         real-authoring unit non-terminal (every remaining unit is a
         structurally degenerate no-op span) → INCONCLUSIVE (AC-18 forbids
         blaming the skill; AC-19 independently forbids certifying complete
         without a positive oracle result — INCONCLUSIVE is the only outcome
         satisfying both simultaneously, plan D1).
    """
    if not (result.succeeded and result.reason == _REASON_EXITED):
        return RunOutcome.INTERRUPTED
    if blocker_detector(workspace):
        return RunOutcome.BLOCKED
    if completion_predicate is None:
        return RunOutcome.INCONCLUSIVE
    if completion_predicate(workspace):
        return RunOutcome.COMPLETE
    if degeneracy_inspector is None or degeneracy_inspector(workspace):
        return RunOutcome.ABANDONED
    return RunOutcome.INCONCLUSIVE


def build_acceptance_predicate(
    cfg: BuildModeConfig,
) -> Callable[[str], bool] | None:
    """Construct the injected acceptance oracle named by cfg, or None if unset.

    Lazy-imports the concrete oracle from acceptance_oracles ONLY when a kind is
    selected, so build.py never couples to layer-derivation at module import time
    (AC-17: `"ChainState" not in dir(build)`). An empty/unknown kind returns None
    → the gate's INCONCLUSIVE fail-safe (AC-19).
    """
    if cfg.acceptance_oracle_kind == ACCEPTANCE_ORACLE_CHAINSTATE:
        from scripts.playground.acceptance_oracles import (
            chainstate_complete_predicate,
        )

        return chainstate_complete_predicate(cfg.chain_state_path)
    return None


def build_degeneracy_inspector(
    cfg: BuildModeConfig,
) -> Callable[[str], bool] | None:
    """Construct the injected AC-18 structural-degeneracy inspector named by cfg, or None if unset.

    Mirrors build_acceptance_predicate's lazy-import-on-selected-kind pattern (AC-17:
    build.py never couples to layer-derivation at module import time). An
    unset/unknown kind returns None, which classify_run_outcome treats as the
    pre-D1 fail-safe default (ABANDONED on oracle-negative) — the gate never
    weakens for a run that never wired the inspector.
    """
    if cfg.acceptance_oracle_kind == ACCEPTANCE_ORACLE_CHAINSTATE:
        from scripts.playground.acceptance_oracles import (
            real_authoring_unfinished_predicate,
        )

        return real_authoring_unfinished_predicate(cfg.chain_state_path)
    return None


def run_harvestability_preflight(
    fixed_layers: tuple[str, ...],
) -> tuple[bool, tuple[str, ...]]:
    """The AC-22 plan-time harvestability pre-flight — PUBLIC so build_resume.py's
    resume-path revalidation (D4/ADV-sg-06) calls the SAME implementation rather
    than duplicating it (unlike `_derive_jsonl_dir`'s deliberate duplication,
    this predicate is a correctness-bearing gate, not a convention — one
    implementation is load-bearing here, matching lint_spec's own
    "author-time == plan-time, one implementation" principle it delegates to).

    fixed_layers empty means this run's spec doesn't use the layer-derivation
    span-screening surface — the pre-flight is Not Applicable and this function
    returns `(True, ())` (vacuously harvestable), so every pre-existing
    (fixed_layers-less) build-mode run and test is unaffected by AC-22 landing.
    When fixed_layers IS supplied, this delegates to
    acceptance_oracles.harvestability_preflight_verdict — the boundary-module
    indirection that keeps build.py itself layer-derivation-free (AC-17:
    `"ChainState" not in dir(build)`).

    Returns:
        `(harvestable, errors)` — errors is the teaching-quality message list
        (SpecLintResult.errors) to surface to the developer/log on a doomed verdict.
    """
    if not fixed_layers:
        return True, ()
    from scripts.playground.acceptance_oracles import harvestability_preflight_verdict

    return harvestability_preflight_verdict(fixed_layers)


def _gate_harvest(
    cfg: BuildModeConfig,
    gate: _HarvestGateInputs,
    completion_predicate: Callable[[str], bool] | None,
    blocker_detector: Callable[[str], bool],
    degeneracy_inspector: Callable[[str], bool] | None = None,
) -> tuple[RunOutcome, list[str], str | None]:
    """Completion gate: classify the run, then apply its disposition (AC-18/AC-19).

    Returns (outcome, harvested_relpaths, preserved_workspace_or_None). Harvest +
    discard run ONLY for RunOutcome.COMPLETE; every other outcome preserves the
    copy, skips the harvest, and records its own terminal registry status so a
    resume path treats interrupted (resumable) apart from blocked/abandoned/
    inconclusive (never auto-resumed).
    """
    result = gate.result
    outcome = classify_run_outcome(
        result, gate.workspace, completion_predicate, blocker_detector, degeneracy_inspector
    )

    if outcome is not RunOutcome.COMPLETE:
        _LOG.info(
            "Run classified %s (rc=%d reason=%s) — preserving copy at %s, skipping harvest",
            outcome.value, result.returncode, result.reason, gate.workspace,
        )
        _update_run_registry(
            gate.registry_path,
            _OUTCOME_TO_PRESERVE_STATUS[outcome],
            {"outcome": outcome.value, "reason": result.reason},
        )
        return outcome, [], gate.workspace

    _LOG.info(
        "Run classified complete — harvesting child-authored artifacts into %s",
        cfg.target_project_dir,
    )
    harvested = harvest_authored(
        gate.workspace, cfg.target_project_dir, gate.globs, gate.baseline
    )
    # AC-11 retention clause: scalpel-retain the ideation index entry + ledger +
    # task folder backing the just-harvested materialization's decided_by, as
    # test_harness_app project data (see retain_ideation_provenance's own
    # docstring for the full WHY). Placed right after harvest so it inspects
    # exactly the artifacts that made it out this run; a harmless no-op (T-1)
    # when nothing harvested carries a resolvable decided_by.
    retain_ideation_provenance(gate.workspace, cfg.target_project_dir, harvested)
    # AC-20 persist-on-harvest: export the copy's advanced history back to the
    # persisted bundle BEFORE the registry flips to complete and the copy is
    # destroyed — once destroyed, the bundle is the only copy of this run's
    # commits, which the next maintenance run's restore-on-deploy builds on.
    # This runs on BOTH the fresh-run and the cold-resume path (build_resume
    # reuses launch_and_gate -> here). COMPLETE-only by placement: every other
    # outcome preserves the copy above, so no partial history is ever persisted.
    persisted_bundle = harness_git_bundle_path(cfg.target_project_dir)
    # AC-20 compaction runs BETWEEN harvest and export: after harvest so the
    # reference scan sees exactly the artifacts that made it out, and BEFORE
    # the export overwrites the bundle — the PRE-RUN bundle's head is how the
    # prior persisted tip (the immutability boundary no rewrite may cross) is
    # recovered.
    referenced = _collect_referenced_commits(gate.workspace, harvested)
    squashed = compact_workspace_git(gate.workspace, persisted_bundle, referenced)
    if squashed:
        _LOG.info(
            "Compacted harness git history: squashed %d unreferenced intermediate commits",
            squashed,
        )
    _LOG.info("Persisting workspace git history to bundle: %s", persisted_bundle)
    export_workspace_git_bundle(gate.workspace, persisted_bundle)
    _update_run_registry(
        gate.registry_path,
        _RUN_STATUS_COMPLETE,
        {"outcome": outcome.value, "harvested_count": len(harvested)},
    )
    _LOG.info("Discarding isolated copy %s", gate.workspace)
    destroy_workspace(gate.workspace)
    return outcome, harvested, None


@dataclass
class LaunchAndGateInputs:
    """Grouped inputs to launch_and_gate (keeps its signature <= 5 params, PLR0913).

    Bundles everything the launch->gate tail needs, regardless of which caller
    assembled it: a FRESH run (built by _prepare_workspace +
    write_run_registry_running, inside run_build_mode) or a COLD RESUME
    (read back from an existing run-registry record + its baseline sidecar,
    build_resume.resume_run, AC-15) — the same five facts either way.

    workspace: the isolated copy's path (fresh: newly created; resume: the
        PRESERVED workspace_path from the registry record — never re-created).
    globs: product-definition globs (registry-driven harvest classification).
    baseline: the pre-child snapshot_product_definition() map (fresh: taken
        right after seeding; resume: loaded from the baseline sidecar via
        build_resume.load_baseline — never re-snapshotted).
    registry_path: path to this run's registry record (already status=running).
    jsonl_dir: CCS JSONL dir the hung-detection launcher watches.
    ledger: the CostLedger this launch's cost is recorded onto and whose
        to_dict() feeds the returned manifest.
    degeneracy_inspector: the AC-18 D1 structural-degeneracy inspector passed
        through to classify_run_outcome (via _gate_harvest). Bundled here rather
        than as its own launch_and_gate keyword param — that would push
        launch_and_gate's own signature past PLR0913's <= 5 params limit
        alongside completion_predicate.
    """

    workspace: str
    globs: list[str]
    baseline: dict[str, str]
    registry_path: str
    jsonl_dir: str
    ledger: CostLedger
    degeneracy_inspector: Callable[[str], bool] | None = None


def launch_and_gate(
    cfg: BuildModeConfig,
    inputs: LaunchAndGateInputs,
    *,
    launch_deps: LaunchDeps | None = None,
    probe_fn: object = None,
    completion_predicate: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Launch the child session, then run the completion gate (the single reusable seam).

    Extracted from run_build_mode (TASK-PROC-068-22, T2) so build_resume.py's
    resume_run can drive the EXACT SAME launch->gate tail on a preserved
    workspace/baseline pair — WITHOUT repeating deploy/seed/snapshot. Callers
    that ran `_prepare_workspace` (a fresh run) and callers that instead read a
    preserved workspace + baseline back from the registry (a cold resume)
    converge here; there is only one launch->gate code path (AC-15).

    Args:
        cfg: Build-mode configuration (paths, prompt, budget, model).
        inputs: Grouped launch/gate inputs (workspace, globs, baseline,
            registry_path, jsonl_dir, ledger).
        launch_deps: Injectable I/O boundaries for the child session launcher.
        probe_fn: Injectable containment probe for tests.
        completion_predicate: Injected acceptance oracle over the copy path
            (AC-17/AC-19); None means "cannot certify complete" (INCONCLUSIVE
            fail-safe — never harvested, never reported successful).

    Returns:
        A manifest dict with harvested_paths/outcome/completed/workspace_preserved/
        run_registry_path plus the ledger's cost fields. Does NOT include
        seeded_paths — that is a fresh-run-only concept the caller adds.

    The BLOCKED-artifact detector is the fixed factory-wide has_recorded_blocker
    (pending_feedback presence); its injectable form lives on the pure
    classify_run_outcome, which is where tests exercise blocker classification.
    """
    # Build the contained child command, scoped to the isolated copy.
    base_cmd = _build_claude_cmd(cfg.session_uuid, cfg.prompt, cfg.model)
    kwargs: dict[str, object] = {}
    if probe_fn is not None:
        kwargs["probe_fn"] = probe_fn
    contained_cmd = wrap_with_containment(base_cmd, inputs.workspace, **kwargs)  # type: ignore[arg-type]  # probe_fn type-erasure intentional for test injection

    # Child env keeps the REAL HOME and inherited CLAUDE_CONFIG_DIR (AC-12) —
    # NOT scrub_env's isolated-copy HOME redirect. wrap_with_containment binds
    # ~/.claude (+ ~/.ccs) at their real absolute paths, so the contained
    # `claude` child can only authenticate if HOME still points at the real home
    # and CLAUDE_CONFIG_DIR still names the active CCS account instance — both
    # of which `dict(os.environ)` inherits unchanged. Mirrors run_skeleton.py.
    child_env = dict(os.environ)
    # AC-19 part 2 (clean-exit attribution): force the CLI's print-mode
    # background-wait ceiling to 0 so a still-working background agent inside the
    # child can NOT keep `-p` alive to a delayed 0 return and be observed as a
    # clean, complete exit. A clean process-exit must reflect the child session's
    # OWN completion decision. Same defense orchestrate.py's build_env applies.
    child_env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"

    # Launch the derivation session inside the isolated copy.
    _LOG.info("Launching derivation session %s", cfg.session_uuid[:8])
    result = run_with_hung_detection(
        LaunchRequest(
            cmd=contained_cmd,
            env=child_env,
            session_uuid=cfg.session_uuid,
            jsonl_dir=inputs.jsonl_dir,
        ),
        deps=launch_deps,
    )
    _LOG.info(
        "Derivation session finished: rc=%d reason=%s",
        result.returncode, result.reason,
    )

    # Record cost from stdout JSON envelope.
    record_run(inputs.ledger, cfg.session_uuid, result.stdout)

    # Completion gate: classify the run, harvest+discard on COMPLETE else preserve.
    outcome, harvested, preserved = _gate_harvest(
        cfg,
        _HarvestGateInputs(
            workspace=inputs.workspace,
            result=result,
            globs=inputs.globs,
            baseline=inputs.baseline,
            registry_path=inputs.registry_path,
        ),
        completion_predicate,
        has_recorded_blocker,
        inputs.degeneracy_inspector,
    )

    manifest: dict[str, Any] = {
        "harvested_paths": harvested,
        "outcome": outcome.value,
        # Retained for backward-compat with existing consumers: True iff COMPLETE.
        "completed": outcome is RunOutcome.COMPLETE,
        "workspace_preserved": preserved,
        "run_registry_path": inputs.registry_path,
    }
    manifest.update(inputs.ledger.to_dict())
    return manifest


def run_build_mode(
    cfg: BuildModeConfig,
    *,
    launch_deps: LaunchDeps | None = None,
    probe_fn: object = None,
    completion_predicate: Callable[[str], bool] | None = None,
    degeneracy_inspector: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Pre-flight -> deploy -> seed -> launch -> completion-gate (AC-22, then AC-18/AC-19).

    Injectable launch_deps and probe_fn allow tests to mock subprocess calls,
    same pattern as run_skeleton.py's run_single_fixture. ``completion_predicate``
    is the injected acceptance-oracle seam (AC-17/AC-19); when a caller does not
    inject one directly it is derived from cfg's acceptance-oracle spec
    (build_acceptance_predicate), and an ABSENT oracle means the gate "cannot
    certify complete" (INCONCLUSIVE fail-safe — never harvested, never a success).
    ``degeneracy_inspector`` is the AC-18 D1 narrowing seam; when not injected it
    is derived from cfg the same way (build_degeneracy_inspector).

    Before any of that: the AC-22 harvestability pre-flight screens cfg.fixed_layers
    (this is the "-start" re-validation D4 requires — the CLI's ONLY entry point
    to a fresh run runs through here). A doomed verdict raises DoomedSpecError
    BEFORE `_prepare_workspace` — no workspace is created, no run is registered,
    no deployed run is consumed (AC-22's "consumes no deployed run").

    The launch->gate tail (everything after the registry write) is delegated to
    the public `launch_and_gate` — the same seam build_resume.resume_run calls
    on a cold re-attach (AC-15), so fresh-run and resume never duplicate it.

    Args:
        cfg: Build-mode configuration (paths, prompt, budget, model, fixed_layers).
        launch_deps: Injectable I/O boundaries for the child session launcher.
        probe_fn: Injectable containment probe for tests.
        completion_predicate: Injected acceptance oracle over the copy path;
            when None it is derived from cfg's acceptance_oracle_kind.
        degeneracy_inspector: Injected AC-18 structural-degeneracy inspector;
            when None it is derived from cfg's acceptance_oracle_kind.

    Raises:
        DoomedSpecError: cfg.fixed_layers is non-empty and the AC-22 pre-flight
            predicts the spec can never be certified complete (AC-22).
    """
    # AC-22: screen BEFORE any workspace/run exists. fixed_layers empty means this
    # run's spec doesn't use the layer-derivation span-screening surface — the
    # pre-flight is Not Applicable for such a run (mirrors AC-19's own
    # oracle-optionality: absence is a distinct, non-blocking case) and every
    # pre-existing (fixed_layers-less) build-mode caller is unaffected.
    harvestable, preflight_errors = run_harvestability_preflight(cfg.fixed_layers)
    if not harvestable:
        raise DoomedSpecError(preflight_errors)

    # An explicitly-injected predicate (tests / direct callers) wins; otherwise
    # construct it from cfg's persisted oracle spec so the production CLI path and
    # the injectable test seam converge on the same gate.
    if completion_predicate is None:
        completion_predicate = build_acceptance_predicate(cfg)
    if degeneracy_inspector is None:
        degeneracy_inspector = build_degeneracy_inspector(cfg)
    globs = load_product_definition_globs(cfg.registry_path)
    ledger = CostLedger(max_budget_usd=cfg.max_budget_usd)

    workspace, seeded, pre_child_state = _prepare_workspace(cfg, globs)

    # Gate on budget before launching.
    _LOG.info("Checking budget (cap: $%.4f)", cfg.max_budget_usd)
    check_budget(ledger)

    # jsonl_dir is derived BEFORE the registry write (not after, as before this
    # refactor) so the record itself carries the resolved directory rather than
    # forcing a resumed run to re-derive it from the workspace path.
    jsonl_dir = cfg.jsonl_dir or _derive_jsonl_dir(workspace)

    # Record status=running + everything a cold resume needs (prompt,
    # jsonl_dir, registry_path, workspace_root, max_budget_usd, baseline ref)
    # BEFORE launch — a tree-wide limit can kill the wrapper before the
    # completion gate (ADV-synthesize-gate-02); T2 (build_resume.py) reads
    # this record back to re-attach without re-deploying (AC-15).
    registry_path = write_run_registry_running(
        cfg, workspace, jsonl_dir=jsonl_dir, baseline=pre_child_state
    )

    manifest = launch_and_gate(
        cfg,
        LaunchAndGateInputs(
            workspace=workspace,
            globs=globs,
            baseline=pre_child_state,
            registry_path=registry_path,
            jsonl_dir=jsonl_dir,
            ledger=ledger,
            degeneracy_inspector=degeneracy_inspector,
        ),
        launch_deps=launch_deps,
        probe_fn=probe_fn,
        completion_predicate=completion_predicate,
    )
    manifest["seeded_paths"] = seeded
    return manifest


def _build_claude_cmd(session_uuid: str, prompt: str, model: str) -> list[str]:
    """Build the claude -p command list for the contained derivation session."""
    return [
        "claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "--model", model,
        "--session-id", session_uuid,
        "-p", prompt,
    ]


def _derive_jsonl_dir(dir_path: str) -> str:
    """Derive the CCS JSONL directory for a project dir path.

    Why: CCS names the project directory by replacing '/' with '-' in the
    absolute path. Build mode watches the derivation session's JSONL in the
    directory derived from the isolated copy (the child's cwd), not the host
    factory or test_harness_app. Duplicated from run_skeleton.py's
    _derive_jsonl_dir (same CCS convention) rather than importing a
    leading-underscore private helper across modules.
    """
    normalized = dir_path.rstrip("/")
    ccs_project_name = normalized.replace("/", "-")
    return os.path.join(
        "/home/vscode/.ccs/shared/context-groups/default/projects",
        ccs_project_name,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Build/maintain mode: derive the harness's own layers in an "
            "isolated deployed copy, harvest product-definition artifacts "
            "back into test_harness_app/, retaining them (AC-11)."
        )
    )
    p.add_argument(
        "--target-project-dir",
        required=True,
        help="Absolute path to test_harness_app (harvest target AND seed source).",
    )
    p.add_argument(
        "--host-project-dir",
        required=True,
        help="Absolute path to the host factory project (deploy source).",
    )
    p.add_argument(
        "--workspace-root",
        default=None,
        help=(
            "Parent directory where the isolated playground_ws_<uuid8> copy "
            "is created. Defaults to the worktree root (worktree_root.py + "
            "worktree.config.json), i.e. <repo>/.worktree/."
        ),
    )
    p.add_argument(
        "--session-uuid",
        default=None,
        help="Pre-assigned session UUID. Defaults to a fresh uuid4.",
    )
    p.add_argument(
        "--prompt",
        required=True,
        help="Prompt passed to claude -p for the derivation session.",
    )
    p.add_argument(
        "--jsonl-dir",
        default=None,
        help=(
            "Directory where the child session writes its JSONL file. "
            "Defaults to the CCS shared context-groups path for the workspace."
        ),
    )
    p.add_argument(
        "--max-budget-usd",
        type=float,
        default=DEFAULT_MAX_BUDGET_USD,
        help=f"Hard budget cap in USD. Default: {DEFAULT_MAX_BUDGET_USD}.",
    )
    p.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model to use. Default: {DEFAULT_MODEL}.",
    )
    p.add_argument(
        "--registry-path",
        default=None,
        help=(
            "Path to the artifacts registry. "
            f"Defaults to <host-project-dir>/{DEFAULT_REGISTRY_RELPATH}."
        ),
    )
    p.add_argument(
        "--run-registry-dir",
        default=None,
        help=(
            "Durable directory for the run registry. Defaults to "
            f"<workspace-root>/{_RUN_REGISTRY_DIRNAME}."
        ),
    )
    p.add_argument(
        "--acceptance-oracle",
        choices=[ACCEPTANCE_ORACLE_CHAINSTATE],
        default=None,
        help=(
            "Acceptance oracle that certifies the run complete (AC-19). "
            f"'{ACCEPTANCE_ORACLE_CHAINSTATE}' checks the copy's layer-derivation "
            "ChainState is fully DONE. WITHOUT this flag the gate cannot certify "
            "complete and never harvests (fail-safe)."
        ),
    )
    p.add_argument(
        "--chain-state-path",
        default=None,
        help=(
            "ChainState JSON path RELATIVE to the isolated copy, used by the "
            f"'{ACCEPTANCE_ORACLE_CHAINSTATE}' acceptance oracle."
        ),
    )
    p.add_argument(
        "--fixed-layers",
        default=None,
        help=(
            "Comma-separated fixed_layers names (the spec input the AC-22 "
            "harvestability pre-flight screens BEFORE any workspace is "
            "deployed). Omit for a build-mode run with no spec to screen — the "
            "pre-flight is then vacuously passed (Not Applicable)."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [playground-build] %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    parser = _build_parser()
    args = parser.parse_args(argv)

    session_uuid = args.session_uuid or str(_uuid_mod.uuid4())
    workspace_root = args.workspace_root or str(worktree_root())
    registry_path = args.registry_path or os.path.join(
        args.host_project_dir, DEFAULT_REGISTRY_RELPATH
    )

    cfg = BuildModeConfig(
        target_project_dir=args.target_project_dir,
        host_project_dir=args.host_project_dir,
        workspace_root=workspace_root,
        session_uuid=session_uuid,
        prompt=args.prompt,
        jsonl_dir=args.jsonl_dir or "",
        max_budget_usd=args.max_budget_usd,
        model=args.model,
        registry_path=registry_path,
        run_registry_dir=args.run_registry_dir or "",
        acceptance_oracle_kind=args.acceptance_oracle or "",
        chain_state_path=args.chain_state_path or "",
        fixed_layers=tuple(
            name.strip()
            for name in (args.fixed_layers or "").split(",")
            if name.strip()
        ),
    )

    try:
        manifest = run_build_mode(cfg)
        print(json.dumps(manifest, indent=2))  # documented CLI output contract (see module docstring)
        return 0

    except DoomedSpecError as exc:
        # AC-22: distinct exit code, caught BEFORE the generic RuntimeError clause
        # below (DoomedSpecError subclasses RuntimeError) — a doomed spec is a
        # plan-time verdict, not an operational failure (EXIT_DOOMED_SPEC's own
        # docstring/comment explains the distinctness from every other code).
        _LOG.error("Doomed spec — pre-flight rejected before deploy: %s", exc)
        return EXIT_DOOMED_SPEC
    except BudgetExceeded as exc:
        _LOG.error("Budget cap exceeded: %s", exc)
        return 1
    except ContainmentUnavailable as exc:
        _LOG.error("Containment unavailable: %s", exc)
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        _LOG.error("Build-mode run failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
