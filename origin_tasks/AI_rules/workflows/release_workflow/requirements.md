---
id: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-ENAB
status: active
effort: XL
stakeholder: developer
created: 2026-03-10
updated: 2026-04-25
after: [REQ-PROC-034, REQ-PROC-035, REQ-PROC-037]
blocks: []
market_research_refs: [] # No relevant findings identified
trackable_items:
  sections:
    - id: SEC-01
      name: "Release Skill"
      heading: "## Release Skill"
      target_package: "Transfer Data Model"
    - id: SEC-02
      name: "Automation Scripts"
      heading: "## Automation Scripts"
      target_package: "Transfer Data Model"
    - id: SEC-03
      name: "Technical Release Notes"
      heading: "## Technical Release Notes"
      target_package: "Transfer Data Model"
    - id: SEC-04
      name: "Marketing Release Notes"
      heading: "## Marketing Release Notes"
      target_package: "Transfer Data Model"
    - id: SEC-05
      name: "Task Metadata Extension"
      heading: "## Task Metadata Extension"
      target_package: "Transfer Data Model"
    - id: SEC-06
      name: "release-begin-impl Integration"
      heading: "## release-begin-impl Integration"
      target_package: "Transfer Data Model"
    - id: SEC-07
      name: "Manual Setup Guide"
      heading: "## Manual Setup Guide"
      target_package: "Transfer Data Model"
    - id: SEC-08
      name: "Release Notes UI"
      heading: "## Release Notes UI"
      target_package: "Onboarding Flow"
    - id: SEC-09
      name: "Windows Deployment Completeness"
      heading: "## Windows Deployment Completeness"
      target_package: "Transfer Data Model"
    - id: SEC-10
      name: "Smoke Test Gate"
      heading: "## Smoke Test Gate"
      target_package: "Transfer Data Model"
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
target_package: "Transfer Data Model"

---

# REQ-PROC-036: Release Execution Workflow

## Overview

A `/release` Claude Code skill plus supporting automation scripts that cover the full release execution path: from a verified develop branch to a tagged, pushed release with generated release notes. The skill orchestrates scripts; the scripts handle the deterministic parts.

## Purpose

Once a release passes the preparation gate (REQ-PROC-035), the developer needs a reliable, repeatable path from "code is ready on develop" to "tagged release on GitHub with build artifacts and release notes". Without this, each release is a manual, error-prone sequence of git commands, note-writing steps, and pipeline checks. This requirement defines that path as an automatable, AI-assisted workflow.

## When to Use

Invoke the `/release` skill when:
- RELEASES.md has exactly one entry with `status: active` (set by `release-begin-impl`)
- All tasks for that active release are `completed`
- `release-begin-impl-finalize` has completed successfully (all impl tasks verified and after-chains reconciled)
- The develop branch is clean (no uncommitted changes, all tests green locally)
- `pubspec.yaml` version does NOT yet match the release version (the script will bump it)

## When NOT to Use

Do NOT invoke `/release` when:
- No release has `status: active` in RELEASES.md → run `release-begin-impl` first
- There are open/pending tasks for the active release → complete them first
- The develop branch has uncommitted changes → commit or stash first
- You only want to generate release notes without cutting a release → not supported; run steps manually

---

## Release Skill

The `/release` skill orchestrates the following steps, delegating deterministic work to scripts:

1. **Run pre-flight script** → abort with actionable error if any check fails
2. **Smoke test gate** → skill provides scripts for developer to run on Windows; waits for explicit confirmation before proceeding (see SEC-10)
3. **Run release script** → bumps pubspec.yaml, merges, tags, pushes
4. **Generate technical release notes** → from task metadata, stored under `releases/[version]/`
5. **Generate marketing release notes draft** → AI-written, stored under `releases/[version]/`
6. **Present marketing notes for user review** → user edits/approves before the skill completes
7. **Update RELEASES.md** → set active release `status: released`

If any script step fails, the skill halts with a clear error message describing exactly which manual step to run to recover. No retry loops.

---

## Automation Scripts

Two Python scripts handle the automatable parts:

### `scripts/check_release_preconditions.py`

Checks all preconditions for a release. Exits with code 0 if all pass, non-zero otherwise with a clear message per failed check:

- `status: active` release exists in RELEASES.md → extract version
- No `pending` or `in_progress` tasks assigned to the active release
  - Reuse logic from the existing "next task" script: if the next pending task belongs to the active release, the check fails
- `develop` branch is clean (`git status --porcelain` returns empty)
- Local tests pass (`flutter test`)
- Test line coverage meets the project minimum threshold (75%); the measurement must account for all tracked source files, not only those imported by tests
- pubspec.yaml version does not yet match the release version
- (Warning, non-blocking) All `impl`-type tasks assigned to the active release have a `release_description` field set; tasks without this field are listed by name so the developer can confirm the omission is intentional — they will not appear in the technical release notes

### `scripts/execute_release.py`

Executes the git portion of the release. Must be run only after `check_release_preconditions.py` exits 0:

1. Bump `version:` in `pubspec.yaml` to match the release version (format: `X.Y.Z+[build]`, build number = incremented by 1)
2. `git add pubspec.yaml`
3. `git commit -m "chore: bump version to vX.Y.Z"`
4. `git checkout master`
5. `git merge develop --no-ff -m "release: vX.Y.Z"`
6. `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
7. `git push origin master`
8. `git push origin vX.Y.Z`
9. `git checkout develop`

GitHub Actions fires automatically on the tag push. Android and Windows builds run; Apple is deferred (see Developer Guidelines).

---

## Technical Release Notes

File: `releases/[version]/release_notes_technical.md`

**Generated automatically** from the `release_description` field of all completed `impl`-type tasks assigned to the active release. Only tasks from `functional/` and `non-functional/` are included — `process/` tasks are excluded (internal tooling is not user-relevant).

**Format**: grouped list by category (Features, Fixes, Improvements), each entry = one task's `release_description`. Language: English.

**Depends on**: SEC-05 (Task Metadata Extension) — tasks must have `release_description` populated.

---

## Marketing Release Notes

File: `releases/[version]/release_notes_marketing_[lang].md` (one per supported language)

**Supported languages**: German (primary), English.

**Generation**: The AI reads the active release's `description`, `goals`, and `scope_boundaries.includes` from RELEASES.md and drafts a user-facing text in marketing tone — enthusiastic, benefit-focused, no jargon. See REQ-PROC-037 (Marketing Writing Rules) for style and structure.

**Review step (MANDATORY)**: After generating the draft, the skill presents it to the user and waits for approval. The user may edit inline or ask the AI to revise. The skill does NOT mark the release complete until the user explicitly approves both language versions.

**Storage**: Notes live in `releases/[version]/`. A `releases/README.md` explains the folder structure and file naming conventions.

**Depends on**: REQ-PROC-037 (Marketing Writing Rules).

---

## Task Metadata Extension

All goal.md files for `impl`-type tasks must include a `release_description` field in the YAML frontmatter:

```yaml
release_description: "Add QR code scanning with progress feedback"  # max 15 words, English
```

**Rules**:
- Required for `impl` tasks only; optional for `explore`, `define`, `review`, `analyze`
- Max 15 words, written in English
- Written from the user's perspective: what they gain, not what the developer did
- Set at task creation time; may be refined before release

**Skill updates required**:
- `task-create`: add `release_description` field to goal.md template and prompt the user to fill it for `impl` tasks
- `task-create-impl`: same

---

## release-begin-impl Integration

The `release-begin-impl` skill must set the release's `status` in RELEASES.md to `active` when it completes preparation for a release. This is the single source of truth for "which release is currently being worked on".

**Lifecycle**:
- `planned` → set to `active` by `release-begin-impl` when preparation is approved
- `active` → set to `released` by the `/release` skill after successful release
- Only one release may have `status: active` at a time; `release-begin-impl` must enforce this

The pre-flight script reads this field to determine the target release version — no other mechanism is needed.

### release-begin-impl-finalize

After the autorun completes all implementation packages for the active release (the validation orchestration task reports success), the developer runs `/release-begin-impl-finalize` before invoking `/release`. This interactive skill:

1. **Phase 1 — Coverage audit**: Verifies all in-scope packages have ≥1 non-terminal impl task (`generate_status_overview.py`), then runs `check_task_against_plan.py` for each impl task to surface deviations from the approved `task_creation_plan.md`.
2. **Phase 2 — After-chain reconciliation**: Runs `reconcile_after_chains.py --release [v] --plan [plan_path]` to detect missing `after:` entries; applies fixes with `--apply` if gaps are found.
3. **Phase 3 — Semantic validation**: Spawns one agent per feature, each verifying that the feature's impl task goal.md addresses the ACs' intent. High-confidence mismatches are flagged.
4. **Phase 4 — User review gate**: The orchestrator presents consolidated findings for developer approval.
5. **Phase 5 — Finalize**: On approval, updates RELEASES.md metadata, regenerates STATUS.md, commits.

`/release` may only be invoked after `/release-begin-impl-finalize` completes successfully.

---

## Manual Setup Guide

File: `releases/SETUP_GUIDE.md`

One-time guide for the developer, written as part of the first release. Covers:

- **GitHub repository connection**: How to add the remote, authentication (SSH key or personal access token)
- **GitHub Actions secrets**: Which secrets must be set (Android signing keystore, keystore password, key alias, key password)
- **Android signing**: How to generate a release keystore and register it in Actions secrets
- **Build pipeline overview**: What `.github/workflows/release.yml` does, where artifacts are stored (Actions artifacts page)
- **How to verify a successful release**: Checking the Actions run, confirming the tag exists on GitHub, downloading the artifact

The skill references this guide on first run (when GitHub remote is not yet configured). It does not reprint the guide on subsequent runs.

---

## Release Notes UI

> **OUT OF SCOPE for 0.0.1** — deferred to `0.1.0` or later.

An in-app screen showing `release_notes_marketing_de.md` (or `_en.md` based on device locale) on first launch after an update. Also accessible from settings. Full requirements to be elaborated when scheduled.

---

## Windows Deployment Completeness

The Windows build artifact produced by GitHub Actions must be a **self-contained, deployable package** that installs and runs correctly on a clean Windows machine — one that has no development tools, Visual Studio, or pre-installed Visual C++ Redistributables.

### Requirement

Every Windows release artifact must satisfy one of the following two conditions:

**Option A — MSIX package (preferred)**
The artifact is an `.msix` installer that declares the `Microsoft.VCLibs` framework package as a dependency. Windows installs the VC++ runtime automatically when the user installs the MSIX. Use the Flutter `msix` package to generate this artifact.

**Option B — Standalone folder with bundled DLLs**
If MSIX is not yet implemented, the deployment folder must include the following DLLs alongside `mood_tracker.exe`:
- `vcruntime140.dll`
- `vcruntime140_1.dll`
- `msvcp140.dll`
- `concrt140.dll`

These must be copied from the Visual Studio redistributable output or from the GitHub Actions runner environment as part of the CI build step.

### What is NOT acceptable

A deployment that crashes silently on a clean machine due to a missing or version-mismatched runtime DLL is a release blocker. This has been confirmed by a concrete incident: `MSVCP140.dll` version mismatch (14.28 on target vs. newer on dev) caused `0xc0000005` access violation, confirmed via Windows Event Log.

### Pre-flight check

`check_release_preconditions.py` must verify that the Windows build artifact includes either an `.msix` file or the required VC++ DLLs. If neither is present, the pre-flight check must fail with a clear error message.

### Developer Guidelines

- **MSIX is the long-term target**: It handles dependency management cleanly and is the modern Windows packaging standard.
- **Bundling DLLs is acceptable for Alpha/early releases**: Copying the four DLLs listed above is a valid interim approach. The DLLs must come from the GitHub Actions runner (which has Visual Studio installed), not from a development machine, to ensure version consistency.
- **Never ship a release without verifying on a clean machine**: At least once per release cycle, install the artifact on a machine without Visual Studio and confirm the camera screen does not crash.
- **Do not bundle debug DLLs** (`MSVCP140d.dll`, `VCRUNTIME140d.dll`): These are not redistributable and will not be present on end-user machines.

---

## Smoke Test Gate

A verification gate between the pre-flight check and the delivery script. Its purpose is to protect against shipping a build that passes all automated pre-flight checks but is broken in practice — app crashes on launch, critical screens inaccessible, or visible corruption.

The gate has two components:

**Automated flow verification (mandatory)**: Critical end-to-end flows are verified on the target platform before delivery. Due to the WSL2/Windows platform boundary, this verification is triggered and observed by the developer rather than run automatically by the skill. A failed verification blocks the release.

Flows appropriate for this gate are those that:
- Span multiple screens or involve platform-specific behavior
- Would not be reliably caught by unit or widget tests alone
- Represent core functionality a user encounters on first launch

Simple logic and scenarios already covered by unit or widget tests are not in scope here.

**LLM visual review (optional)**: An automated visual check confirms the app's appearance after launch. The result is presented to the developer as advisory information — it augments, does not replace, the automated flow verification. A FAIL from this check is surfaced for the developer's judgment; it does not automatically block the release.

**Explicit human confirmation**: The skill displays a summary of all verification results and waits for the developer's explicit confirmation before proceeding to delivery. There is no auto-approval path. This gate exists because the delivery step is irreversible once the version tag is pushed (same HITL principle as the marketing notes approval gate).

---

## Iterative Impl-Task Creation (Automated Mode)

- **AC-01**: `task-create-impl`, when invoked in zero-parameter automated mode (via an orchestration task created by the bootstrap), picks one package from `RELEASE_BACKLOG.md`, creates its impl task, logs decisions to `protocol.md`, and calls `task-complete` on the orchestration task. One package per session execution.
- **AC-02**: In automated mode, confirmation checkpoints (Phase 0.6 candidate confirm, Phase 3.2.5 dependency proposal, Phase 4.1 review) auto-accept the heuristic default. Decisions are logged to `protocol.md`. Genuinely ambiguous cases (zero candidates, Large-size split required, script error) write `question.md` instead of crashing.
- **AC-03**: A dedicated validation orchestration task (not `task-create-impl`) runs when no packages remain uncovered for the active release. It verifies: AC coverage completeness, `after:` chain integrity (no cycles, no cross-release deps), `target_package` consistency, no orphan packages, `opus_recommended` flag sanity, and `skip_scribble` flag on technical spikes. Failures write `question.md`; passing writes a `validation_report.md` and closes the task.

---

## Developer Guidelines

### Key Decisions

- **`status: active` is the source of truth** for the current release. Scripts and the skill read it from RELEASES.md — no other mechanism (e.g. reading pubspec.yaml version) is used for release identification.
- **Scripts for deterministic steps, skill for AI steps**: The skill does not run git commands directly — it delegates to `check_release_preconditions.py` and `execute_release.py`. This makes individual steps testable and re-runnable independently.
- **No GitHub Release object**: The repo is private; a dedicated GitHub Release page is not needed for 0.0.1. Tags and Actions artifacts are sufficient.
- **No top-level CHANGELOG.md**: Per-release files under `releases/[version]/` are more readable and maintainable than a single growing changelog.
- **Apple builds deferred**: GitHub Actions must only trigger on tag push (not branch push) to avoid unnecessary build minutes. When Apple support is added, the runner cost must be evaluated — consider only running Apple builds on tags, not PRs.
- **Error recovery**: If `execute_release.py` fails mid-way, the skill prints the exact git commands needed to complete or roll back the remaining steps manually. No automatic retry.

### Common Pitfalls

- **Never chain `git add && git commit`** — run as separate commands (per CLAUDE.md git rules). The script must do the same.
- **`release_description` missing on impl tasks**: The technical release notes generation will skip tasks without this field. Warn the user during release if any assigned impl task is missing it.
- **Wrong language in marketing notes**: German version must use `du` form per REQ-NFUNC-013. Do not copy-translate — write each language naturally.
- **`status: active` not set**: If `release-begin-impl` was not run, the pre-flight script will abort. Do not work around this by manually editing RELEASES.md mid-release.
- **Coverage artificially high**: `flutter test --coverage` only instruments files imported by tests. Files with no tests are invisible and not counted, making coverage appear higher than it is. The coverage check implementation must account for all tracked source files, not only those with existing tests.
- **Smoke test gate skipped**: The developer's explicit confirmation is mandatory before delivery. The gate must not be auto-approved even when all automated checks pass — it exists because `execute_release.py` is irreversible once the version tag is pushed.

## Related Requirements

- **REQ-PROC-034** (Release Version Management): Defines version numbering and how requirements are assigned to releases.
- **REQ-PROC-035** (Release Preparation): The gate that must pass before `/release` is invoked.
- **REQ-PROC-037** (Marketing Writing Rules): Style and structure rules for marketing release notes. Must exist before SEC-04 is implemented.
- **REQ-NFUNC-013** (UX Writing): Tone and language baseline that REQ-PROC-037 extends.

## References

- `requirements_tasks/RELEASES.md` — release version registry and active release tracking
- `requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md` (REQ-PROC-034)
- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md` (REQ-PROC-035)
