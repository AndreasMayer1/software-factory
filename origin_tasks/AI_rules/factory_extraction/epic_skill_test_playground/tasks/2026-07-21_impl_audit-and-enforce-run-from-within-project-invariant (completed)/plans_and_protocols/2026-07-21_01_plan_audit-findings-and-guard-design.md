# Plan: Audit findings + mechanical guard design

agent: main session (7c4cf7e8-105f-4f62-8f93-4483956d4972), routed via task-resolve (not code-* — scope is scripts/, not lib/test)

## Audit method

Grepped scripts/**/*.py (340 files, excluding tests/) for:
1. Absolute-path string literals with 3+ path segments.
2. `..` traversal (`os.pardir`, `"../../.."`, `os.path.join(dirname(__file__), "..", ...)`).
3. Hardcoded references to the host project name ("private_mood_tracker", "flutter_app").
4. `Path(__file__).parents[N]` / `.parent` chains, checked systematically for hop-count correctness
   against each file's actual depth under the repo root (a Python one-off computed, for every
   `PROJECT_ROOT`/`REPO_ROOT`/`ROOT`/`SCRIPTS_DIR`-named `__file__`-anchored assignment, the required
   vs actual traversal-hop count).

Confirmed via `deploy.py` (`scripts/playground/deploy.py`): the harness deploy step is a real
`shutil.copytree`, NOT a symlink (explicit WHY comment: "Symlinks would let the child session modify
the host factory tree through the link"). This means `Path(__file__)`-anchored resolution is SAFE by
construction in a deployed copy — it always resolves within whichever tree the file physically lives
in. So the `Path(__file__).parents[N]` pattern itself is not the AC-09 risk; hardcoded absolute paths
and `..`-escapes are.

## Findings

### Finding 1 (AC-09-proper — genuine provider-hardwiring)

`scripts/dev_environment/check_mutagen.py:13`:
```python
ALPHA = Path("/workspaces/private_mood_tracker/flutter_app")
```
Hardcodes the specific host project's absolute path. `scripts/dev_environment/` is not deploy-excluded
(only the folders in `deploy.py`'s `_TOP_LEVEL_EXCLUDES`/`_SUBFOLDER_EXCLUDES` are), so this file would
be copied into `test_harness_app/` on a candidate deploy; if a child session ran it there, it would
write/delete a probe file in the **real host project**, not its own deployed copy — exactly the AC-09
threat. `BETA` (`/home/vscode/windows_mirror`) is left as-is: it is a fixed dev-machine mirror target
(REQ-PROC-054 mutagen ADR), not a project-tree path — nothing to make project-relative.

Fix: derive `ALPHA` from `Path(__file__).resolve().parents[2]` (file-location-relative, safe under
copytree deploy per the confirmed-clean pattern in `allocate_req_id.py`).

### Findings 2-6 (adjacent, NOT provider-hardwiring, but live severe defects — same audit criterion, "`..` traversal")

All five hardcode a traversal-hop count **one hop short** of the file's real depth from repo root,
landing inside `scripts/` (or a nonexistent subpath of it) instead of at the real project root. This is
the *opposite* direction from AC-09's escape concern (it doesn't reach the host tree; it fails to reach
its own project's root), so it is out of AC-09's literal scope — but it is the same
`__file__`-anchored-resolution defect class the goal's audit criteria name, so it surfaced directly from
the mandated grep, and all five are confirmed live via direct execution (not maybes):

| File | Bug | Confirmed impact |
|---|---|---|
| `scripts/tasks/is_awaiting_answer.py` | `FEEDBACK_DIR = os.path.join(os.path.dirname(__file__), "..", "automation", "pending_feedback")` — needs 2 `".."` (depth 3), has 1 | Ran against `TASK-PROC-066-15`, which genuinely has an unanswered `question.md` (template-only `answer.md`) — script returns exit 0 ("not awaiting") when it must return 1. This is the exact safety gate `task-start` P2b and the whole pending_feedback protocol depend on. |
| `scripts/requirements/check_requirements_ready.py` | `base = os.path.join(os.path.dirname(__file__), "..", "requirements_tasks")` — same off-by-one | Resolves to `scripts/requirements_tasks` (does not exist) → `find_goal_files` always empty → always reports "NOT READY", regardless of real state. |
| `scripts/release/execute_release.py` | `PROJECT_ROOT = Path(__file__).parent.parent` — needs 3 parents (depth 3), has 2 | Confirmed by running `--dry-run`: reports "No active release found" even though `requirements_tasks/RELEASES.md` currently has an active release (0.0.1 QR beam PoC). |
| `scripts/release/check_release_preconditions.py` | Same `PROJECT_ROOT` off-by-one | Confirmed by running it directly: cascades into false failures for "active release", `test/` directory ("not found"), `check_canon.py`/`check_dependency_sweep.py`/`check_scribble_currency.py` ("not found") — essentially every check is a false negative because every relative lookup is off by one directory. |
| `scripts/artifacts/generate_technical_release_notes.py` | Same `PROJECT_ROOT` off-by-one | `RELEASES_MD`/`RELEASE_BACKLOG_MD` module constants resolve to nonexistent `scripts/requirements_tasks/RELEASES.md` / `scripts/RELEASE_BACKLOG.md`. |

Decision: fix all five. Rationale — CLAUDE.md's "bug fixes that restore already-documented behavior" carve-out
applies (each script's own docstring/usage states the intended behavior; current code fails to deliver
it); the fix is mechanical/unambiguous (add one more `.parent` / one more `".."`), low-risk, and each
gets a regression test that exercises the REAL path computation (the existing test suites for these
files monkeypatch around `find_goal_files`/`base` entirely — confirmed by reading
`scripts/tests/test_check_requirements_ready.py` — which is exactly why this shipped unnoticed).

### False positives ruled out during the systematic hop-count scan

`script_dir = Path(__file__).parent` (singular, e.g. in `generate_status_overview.py`,
`aggregate_value_tradeoffs.py`, `generate_id_registry.py`, `coverage_report.py`,
`sync_task_packages.py`, `sync_requirement_packages.py`, `validate_meta.py`,
`check_canonical_library.py`) is an intermediate variable (1 hop, always trivially "correct" — it's
just "this file's own directory"); the real root is computed one line later via
`project_root = script_dir.parent.parent` (2 more hops, total 3, correct for all these files' actual
depth). No bug here — flagged only by a naive single-line grep, not by the full per-variable
dataflow trace.

## Mechanical guard design (AC-09 enforcement) — CORRECTED after mid-implementation course change

**Course correction**: initially planned as a new `scripts/quality/check_project_root_escape.py` gate
wired into `scripts/quality/check_python_gates.sh`. Caught before writing any file: CLAUDE.md §7 is
explicit — *"Don't edit gates yourself: AI agents MUST NOT modify `analysis_options.yaml`,
`scripts/quality/check_*.sh/.py`, or gate-defining ACs. File proposals under
`scripts/quality/proposals/` instead."* Confirmed by reading `scripts/quality/proposals/README.md`:
the `check_*.sh`/`check_*.py` restriction is unqualified (applies to Python gates, not just the Dart
G1-G8/SP1-SP6 set) — new gates go through the `new_gates/` proposal category, not a direct AI edit.

The goal text itself only asks for *"a test/script that fails if a script resolves outside its own
project root"* — it does not require a new standalone `scripts/quality/check_*` gate. A pytest test
satisfies this literally and already runs automatically via the **existing, already-wired G3 pytest
gate** (`scripts/quality/pytest_check.sh`, itself unmodified) — no edit to the restricted files needed.

**Revised design**:
- `scripts/util/path_anchor_audit.py` (TIER B reusable library, analogous to
  `scripts/util/yaml_frontmatter.py` / `scripts/util/task_folder_resolver.py`) — holds the AST-based
  analysis, importable and independently testable:
  1. **Escape check**: for every `__file__`-anchored chain (`.parent` chains, `.parents[N]`,
     `os.path.dirname(__file__)` nesting, `os.path.join(dirname_chain, "..", ...)`), compute the
     traversal-hop count via a small recursive evaluator with intra-file variable tracking (so chained
     `script_dir = ...; project_root = script_dir.parent.parent` resolves through `script_dir`,
     avoiding the false-positive class found during the audit above). Compare against
     `len(file.relative_to(repo_root).parts)` — the exact hop count that lands at repo root. Any chain
     exceeding that count would resolve *above* repo root, i.e. outside the project — flagged.
  2. **Hardcoded absolute path check**: any string literal matching an absolute path with 3+ segments,
     except an explicit, commented allowlist for machine-level (not project-tree) paths already
     reviewed as legitimate: `/home/*/.ccs`, `/home/*/.claude` (Claude Code's own infra, doc'd
     rationale in `run_skeleton.py`), `/home/*/windows_mirror` (dev-machine mutagen mirror target,
     REQ-PROC-054).
  Excludes `tests/`, `__pycache__`, and `test_*.py`/`*_test.py` files (fixtures legitimately hardcode
  paths for test isolation).
- `scripts/tests/test_project_root_resolution.py` — pytest test that calls the library against the
  real `scripts/` tree and asserts zero findings. This is the literal "test that fails if a script
  resolves outside its own project root" the goal asks for; it runs on every `check_python_gates.sh`
  invocation via the existing G3 gate, with no edit to any `check_*` file.

## Outcome — what the guard actually found once built

Running the built guard against the real tree (after fixing an initial scope-blindness bug in the
tracker — see below) surfaced exactly two live findings, not zero:

1. `scripts/dev_environment/check_mutagen.py:13` — the ALPHA hardcode (Finding 1 above). Fixed:
   `ALPHA = Path(__file__).resolve().parents[2]`.
2. **`scripts/dev_env/worktree_root.py:65` — a genuine, previously-undiscovered AC-09 escape**, not a
   false positive. `worktree_root()`'s auto-derive (`Path(__file__).resolve().parents[2].parent`)
   returns "the parent of the repo root" — by design, for placing sibling git worktrees next to a
   normal host checkout. But `code-bugfix` SKILL.md calls this resolver as a plain subprocess
   (`WT_ROOT="$(python3 scripts/dev_env/worktree_root.py)"`), and `scripts/dev_env/` is not
   deploy-excluded (`scripts/playground/deploy.py`'s `_TOP_LEVEL_EXCLUDES`/`_SUBFOLDER_EXCLUDES` don't
   cover it). Deployed harness copies are independently `git init`-ed INSIDE the host tree
   (`scripts/playground/workspace.py`: "test_harness_app tree, then git init-ed there so it genuinely
   is its own [repo]") — so if a candidate session's `code-bugfix` worktree mode ran inside a deployed
   harness, "one level above repo root" would resolve to the actual HOST project tree, and
   `git worktree add` would materialize real files there. This is the literal AC-09 threat, concretely
   exploitable, not hypothetical.
   **Fix applied**: `worktree_root()` now calls `_is_nested_inside_another_repo(repo_root)` before
   auto-deriving — if `repo_root` (the presumed project root) has a `.git` anywhere in ITS OWN ancestor
   chain, it means repo_root is itself nested inside another git repository, so auto-derive refuses
   (raises `FileNotFoundError`) instead of silently returning a path inside that outer tree. Normal host
   usage (repo_root's parent has no further `.git` above it) is unaffected. The legitimate one-hop
   escape line itself carries a `# path-anchor-audit: allow-escape — <reason>` inline suppression (a new
   mechanism added to the guard, mirroring this repo's bare-suppression discipline — a marker with no
   reason text is still flagged) so the guard doesn't (and shouldn't) treat this by-design behavior as
   an unreviewed regression going forward.
   Regression test added: `scripts/dev_env/tests/test_worktree_root.py::test_refuses_when_repo_root_nested_inside_another_repo`.

**Guard correctness bug found and fixed before trusting the above**: the first `_check_escape`
implementation used a flat `ast.walk` with one file-wide `var_hops` dict, so an unrelated
function-local variable sharing a name with a `__file__`-anchored variable elsewhere in the SAME file
(e.g. `generate_status_overview.py`'s `git_commit()` has its own runtime `project_root` that walks
toward a `.git` directory in a `while` loop, while `main()` elsewhere in the same file has a real
`__file__`-anchored `project_root`) collided and produced a false escape finding. Fixed by rewriting
the tracker as a scope-aware `ast.NodeVisitor` (`_ScopeVisitor`) that gives each function/class body its
own inherited-but-independent `var_hops` copy. Regression test:
`test_same_named_variable_in_unrelated_function_has_no_finding`.

**Out-of-scope observation (not fixed — different bug class)**: fixing `check_release_preconditions.py`'s
PROJECT_ROOT let it run far enough to reveal a SEPARATE, unrelated bug: it invokes
`PROJECT_ROOT / "scripts" / "next_tasks.py"` (line 188), which no longer exists after a prior scripts
reorganization moved it to `scripts/tasks/next_tasks.py`. This is a stale post-refactor reference, not a
`__file__`-anchoring or provider-hardwiring defect (it doesn't touch AC-09's escape concern at all) —
noted here for traceability but deliberately NOT fixed, to keep this task's scope bounded to the
run-from-within-project invariant.

## Steps taken (chronological) — all complete

1. Wrote `scripts/util/path_anchor_audit.py` + `scripts/tests/test_project_root_resolution.py` (via
   `claude-write-script`). Found and fixed a scope-blindness bug in the tracker itself (see above)
   before trusting its output.
2. Fixed all 7 files (the 6 planned + `scripts/dev_env/worktree_root.py`, discovered by the guard
   itself), each with a regression test exercising the real resolution (not monkeypatched around it):
   `check_mutagen.py`, `is_awaiting_answer.py`, `check_requirements_ready.py`,
   `generate_technical_release_notes.py`, `check_release_preconditions.py`, `execute_release.py`,
   `worktree_root.py`.
3. Ran `scripts/quality/check_python_gates.sh` — G1/G2/G4/G5/G6/G7 all PASS; G3 (pytest) has exactly
   one failure, `test_validate_against_schema.py::test_all_goal_md_against_real_schema`, confirmed via
   `git stash` to be a pre-existing develop-baseline failure unrelated to this task (an unrelated
   goal.md under `epic_layer_derivation` fails schema validation). No edit to any `check_*.sh/.py` gate
   file was made anywhere in this task, per CLAUDE.md's AI-agent restriction.
4. Next: `claude-log`, `doc-update-guidelines` (the worktree_root.py nested-repo defense is a
   non-obvious workaround worth a doc/ note if a suitable guideline file exists), `task-complete`.
