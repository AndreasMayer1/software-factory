# Opus Analysis: Release Workflow Implementation (REQ-PROC-036 + REQ-PROC-037)

Date: 2026-03-11
Analyst: Opus (claude-switch-opus)
Scope: Full implementation audit — all 6 subtasks of TASK-PROC-036 plus REQ-PROC-037

---

## Executive Summary

The release workflow implementation is **substantially complete and of high quality**. All 6 subtasks
of REQ-PROC-036 are done (5 committed, 1 staged but not yet committed). REQ-PROC-037 is done and
committed. The `/release` skill, both automation scripts, the technical notes generator, the
marketing notes spec, SETUP_GUIDE.md, and releases/README.md all meet their acceptance criteria.

One immediate action is required: **commit TASK-PROC-036-01** (the files are staged, the task is
marked completed, but the commit has not been made).

Several **improvement opportunities** exist — none are blockers for the release, but two are
worth addressing before the first real `/release` run.

---

## 1. Task Status: TASK-PROC-036-01

### Current state (from git status and git log)

| File | State |
|------|-------|
| `.claude/skills/release/skill.md` | Staged (A), not committed |
| `releases/README.md` | Staged (A), not committed |
| `releases/SETUP_GUIDE.md` | Staged (A), not committed |
| `.claude/skills/INDEX.md` | Modified (M), staged |
| `CLAUDE.md` | Modified (M), staged |
| Task folder `(completed)/goal.md` | Staged (A), not committed |
| Task folder `(completed)/plans_and_protocols/2026-03-11_audit_report.md` | Staged (A), not committed |
| Task folder `(completed)/plans_and_protocols/2026-03-11_protocol.md` | Staged (A), not committed |

**Observation**: The task was marked `status: completed` and the folder renamed to add the
`(completed)` suffix. The quality audit passed. The only missing step is the git commit.

**The task goal.md in the original (non-completed) folder still exists at the path the user
was working from** — but the staged files show the folder has already been renamed to the
`(completed)` variant. The working copy at `2026-03-10_impl_release-skill-and-setup-guide/`
contains only an unstaged `plans_and_protocols/` subfolder (this analysis file), while the
`(completed)` version already has goal.md and the audit/protocol files staged.

**Resolution**: Commit the staged files, then this task is fully done.

---

## 2. Overall Quality Assessment

### 2.1 The `/release` Skill

**Quality: HIGH**

The skill is well-structured and operationally sound. Each step is clearly bounded, failure
paths are explicit, and the marketing notes approval loop is correctly implemented.

Specific strengths:
- Pre-flight abort is clean: shows output verbatim, stops immediately.
- Technical notes step is a single script call — no AI hallucination risk.
- Marketing notes approval loop (4.6) explicitly waits for "approve" before writing anything.
- Git add in Step 6 uses separate calls (no && chaining).
- INDEX.md updated correctly with both Quick Reference entry and category section.

One issue found (minor, see Section 3.1):
- `execute_release.ps1` ends with "Run the /release skill to mark the release as 'released'"
  in its own output — but the /release skill *is* what runs the script. This creates a circular
  message that will confuse the user on first run.

### 2.2 `scripts/check_release_preconditions.ps1`

**Quality: HIGH**

- All 5 checks present and correct.
- Fail-all (non-fail-fast) behavior: accumulates failures, reports all at once. This is better
  UX than fail-fast — users see everything they need to fix in one run.
- Frontmatter parsing is bounded correctly (tracks two `---` delimiters).
- Push-Location/Pop-Location pattern for flutter test is correct.
- Error messages are actionable.

### 2.3 `scripts/execute_release.ps1`

**Quality: HIGH**

- DryRun parameter enables testing without side effects.
- Invoke-Step helper correctly propagates remaining recovery steps on failure.
- Build number increment logic handles the absent-version-line case.
- All git commands are separate calls — no && chaining.

One issue found (minor, see Section 3.2):
- The "Next steps" message at the end tells the developer to "Run the /release skill" — but the
  script is *called by* the /release skill. From the user's perspective this message appears mid-
  skill run, which is jarring and contradictory.

### 2.4 `scripts/generate_technical_release_notes.py`

**Quality: HIGH**

- Dual YAML parsing (PyYAML with fallback to custom parser) handles both environments.
- UTF-8 BOM handling (Windows editors) is present.
- Warnings for missing release_description go to stderr — they are visible but don't block.
- Creates output directory if needed.
- Smoke-tested against 0.0.1 (protocol confirms this).

One observation (see Section 3.3):
- The "Fixes" category (from Keep-a-Changelog) is absent. The script only generates "Features"
  and "Improvements". Bug fixes committed to functional/ would appear under "Features" rather
  than "Fixes". This is a minor categorization gap.

### 2.5 `releases/SETUP_GUIDE.md`

**Quality: GOOD**

All five required sections are present. Content is accurate and actionable.

Issues found:
- Section 2 says the workflow "triggers on push to master or on a tag push — configure as
  needed" but the workflow file (`.github/workflows/release.yml`) does not exist yet. The guide
  describes what the file *will do* but does not mention that it must be created first. A user
  reading this guide cold would not know they need to create the workflow file. (See Section 3.4.)
- Section 4 uses a placeholder description that is correct but doesn't help the user know what
  trigger to configure (tag push vs. branch push). The requirement says tags should trigger builds,
  not branch pushes — but the guide says "configure as needed" which is vague.

### 2.6 REQ-PROC-037 (Marketing Writing Rules)

**Quality: VERY HIGH**

This is a comprehensive, well-structured document. The persona analysis (TASK-PROC-037-01) and
the external communication preference additions to all 14 personas (TASK-PROC-037-02) provide
solid grounding for the rules.

Specific strengths:
- Universal Tone Hierarchy (SEC-01) is clear, ordered by priority, persona-anchored.
- Writing Style (SEC-02) has concrete "So nicht" (anti-pattern) examples for every rule.
- Forbidden Patterns table (SEC-07) covers all the edge cases.
- The Sachlich-warm voice character is precisely specified with examples.
- Stability framing section directly addresses the mental model the AI should adopt before writing.

Minor observations (see Section 3.5):
- SEC-05 (In-App Release Notes) references images as allowed but the /release skill currently
  generates text-only release notes. This is not a problem for v0.0.1 — but should be noted.
- The SEC-05 "recommended structure" and the skill Step 4 "structure" are slightly divergent on
  the version line format. The requirement shows `[Version] — [Date]` and the skill shows
  `[Version] — [Monat Jahr]`. Both work but slight inconsistency.

### 2.7 Marketing Notes Embedded in Skill

**Quality: GOOD** (with one concern)

The marketing notes section (Steps 4.1–4.7) is thorough and correctly implements the REQ-PROC-037
spec from TASK-PROC-036-04.

One concern: **the skill is 245 lines long**, and roughly 150 of those are the Step 4 marketing
spec. Skills are "token-sensitive context loaded into every agent call" per CLAUDE.md. Every time
a user runs any Claude Code command, this skill is loaded into context if it matches. At 245 lines,
the skill is on the upper end of what is practical for a skill file.

However: the `/release` skill is not a utility skill that gets loaded frequently — it is a
one-off workflow skill invoked rarely (once per release). The token cost is therefore bounded in
practice. This is acceptable.

---

## 3. Specific Issues Found

### 3.1 Circular Message in `execute_release.ps1` (LOW SEVERITY)

**Location**: `scripts/execute_release.ps1`, lines 221–223

```
Write-Host "  1. Run the /release skill to mark the release as 'released' in RELEASES.md"
```

The /release skill is what calls this script. After the script succeeds, the skill continues to
Step 3 (technical notes) and beyond. This "next steps" message will appear mid-skill and tell the
user to run the very skill that is currently running — confusing.

**Recommendation**: Remove the "Next steps" block from the script output (lines 219–223).
The script's job is git — it should end with "Release vX.Y.Z complete." The skill provides the
narrative continuity to the user.

### 3.2 Missing `.github/workflows/release.yml` Template (MEDIUM SEVERITY)

**Location**: `releases/SETUP_GUIDE.md`, Section 4

The SETUP_GUIDE describes what the workflow does, but the file itself does not exist and there is
no template. A developer setting up for the first time would need to know:
- The exact trigger condition (on: push: tags: ['v*.*.*'])
- How to decode the keystore secret and write key.properties
- The exact flutter build command and artifact upload step

Without a template or example, the developer must construct this from scratch.

**Recommendation**: Create `.github/workflows/release.yml` with a working template for Android
APK builds triggered on tag push. The SETUP_GUIDE can then reference it: "Edit
`.github/workflows/release.yml` to configure the runner and artifact retention."

This is a genuine gap — the SETUP_GUIDE says "GitHub Actions fires automatically on the tag push"
but there is nothing in the repo to make that happen.

### 3.3 Technical Notes Missing "Fixes" Category (LOW SEVERITY)

**Location**: `scripts/generate_technical_release_notes.py`

The Keep-a-Changelog format supports "Added", "Changed", "Fixed", "Removed", "Deprecated",
"Security". The script generates only "Features" and "Improvements". Bug fix tasks (type: impl,
in non-functional/) would appear under "Improvements" — which is semantically wrong for a fix.

More importantly: bug fix tasks in functional/ would appear under "Features" — which is wrong.
(There is no mechanism to distinguish between a bug fix impl task and a feature impl task other
than which folder it lives in.)

**Recommendation**: Consider adding a `release_category` field to goal.md frontmatter (values:
`feature`, `improvement`, `fix`). The script would then use this field to sort entries into the
correct Keep-a-Changelog sections. This is a forward-looking suggestion — for v0.0.1 it may not
matter since all tasks are genuinely new features.

### 3.4 Skill Step 6: Commits Files That Don't Exist Yet at Skill Launch (NOT A BUG)

**Question raised during gathering**: Step 6 commits `releases/[version]/` files — but these
don't exist when the skill is invoked. Is there a gap?

**Resolution**: This is correct behavior. The files are created during Steps 3 and 4 within the
same skill run. By the time Step 6 executes, all three release notes files exist. No gap.

### 3.5 RELEASES.md Has `status: planned` for 0.0.1 (EXPECTED STATE)

**Question raised during gathering**: The /release skill Step 4.1 checks for `status: active`
but RELEASES.md shows `planned`. Is this circular?

**Resolution**: No. The lifecycle is:
1. `requ-prep-release` is run → sets 0.0.1 to `status: active`
2. All tasks are completed
3. `/release` is invoked → runs pre-flight (which also requires `status: active`), executes
   release, generates notes, then sets `status: released`

RELEASES.md currently showing `planned` is correct — no release prep has been run yet.
The precondition check will correctly abort until `requ-prep-release` is run.

### 3.6 `check_release_preconditions.ps1` Does Not Verify Current Branch is `develop` (LOW SEVERITY)

The pre-flight check verifies the branch is *clean* but does not verify the developer is *on*
the develop branch. If a developer accidentally runs the release from master or a feature branch,
the check passes (assuming a clean worktree) and `execute_release.ps1` would merge that branch
into master instead of develop.

**Recommendation**: Add `git rev-parse --abbrev-ref HEAD` check to verify current branch is
`develop` before proceeding.

### 3.7 `execute_release.ps1` Build Number When Version Already Matches (MINOR EDGE CASE)

**Location**: `scripts/execute_release.ps1`, lines 109–119

If the existing pubspec.yaml version is `0.0.0+5` and the release version is `0.0.1`, the script
correctly bumps to `0.0.1+6`. But if pubspec.yaml already has `version: 0.0.1` (somehow), the
pre-flight check would catch this and abort. So this edge case is handled upstream. No action
needed.

---

## 4. Gap Analysis: What is Missing

### Critical (must fix before first real release)

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| Missing `.github/workflows/release.yml` template | The "GitHub Actions fires automatically" claim in SETUP_GUIDE and REQ-PROC-036 is false without this file | Create the file as a template |
| `execute_release.ps1` "next steps" message is wrong | Confuses user mid-skill-run | Remove lines 219–223 from the script |
| `check_release_preconditions.ps1` does not check current branch | Risk of merging wrong branch to master | Add branch check |

### Minor (improvement opportunities, not blockers)

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No "Fixes" category in technical notes | Bug fixes miscategorized in release notes | Add `release_category` field to goal.md templates |
| SETUP_GUIDE Section 4 vague on trigger config | Developer must figure out trigger independently | Add exact trigger snippet in comment in the workflow template |
| In-app release notes images not yet supported in skill | Future releases with screenshots will need manual handling | Document this as a known limitation; address when needed |

---

## 5. Systemic Observations

### 5.1 Strong Design: Scripts-for-Deterministic, Skill-for-AI

The separation between deterministic steps (scripts) and AI steps (skill) is well-executed. The
pre-flight script runs all checks before any git state is mutated. The release script handles all
git operations. The skill handles all AI generation. This makes each component independently
testable and the failure surface narrow.

### 5.2 The Approval Gate is Correctly Placed

Step 4.5/4.6 place the user review between generation and file-writing. This is the correct
position — the AI generates the draft in memory, presents it, and only writes after explicit
approval. The files are not written to disk during revision cycles. This is exactly right.

### 5.3 REQ-PROC-037 Quality Enables Future Channels

The marketing writing rules are comprehensive enough that they could govern app store listings
and website copy in addition to release notes. The document correctly defers SEC-06 (Website)
to 0.1.0, but the foundation is solid. This is good long-term thinking.

### 5.4 The `release_description` Field Adoption

The task metadata extension (TASK-PROC-036-05) adds `release_description` to new task templates.
However, all existing tasks (pre-036-05) lack this field. The technical notes generator correctly
warns and skips such tasks. For v0.0.1, 7 tasks were already missing this field at smoke test
time (per the TASK-PROC-036-03 protocol). This means the first release's technical notes will
be sparse unless these tasks are manually backfilled.

**Recommendation**: Before running `/release` for v0.0.1, manually audit all completed impl tasks
assigned to 0.0.1 and add `release_description` to those missing it.

---

## 6. What Remains for TASK-PROC-036-01

**Status**: The task is done. The only remaining action is:

1. Write this analysis file (you are reading it)
2. Commit the staged files

The commit should include:
- `.claude/skills/release/skill.md`
- `releases/README.md`
- `releases/SETUP_GUIDE.md`
- `.claude/skills/INDEX.md` (updated)
- `CLAUDE.md` (updated if any changes there relate to this task)
- The completed task folder with goal.md, audit report, protocol, this file

Commit message format: `feat(TASK-PROC-036-01): add /release skill, SETUP_GUIDE.md, releases/README.md`

---

## 7. Recommended Follow-Up Tasks (Not Blockers for Commit)

In priority order:

1. **Create `.github/workflows/release.yml` template** (HIGH — needed before first release)
   - Android APK build triggered on `v*.*.*` tag push
   - Keystore decode from KEYSTORE_BASE64 secret
   - flutter build apk --release
   - Upload artifact

2. **Fix `execute_release.ps1` "next steps" message** (LOW — minor UX issue)
   - Remove lines 219–223 (the "Next steps" block)
   - The script should end at "Release vX.Y.Z complete."

3. **Add branch check to `check_release_preconditions.ps1`** (MEDIUM — safety)
   - Verify `git rev-parse --abbrev-ref HEAD` returns `develop`

4. **Backfill `release_description` on existing 0.0.1 tasks** (HIGH — needed before v0.0.1 release notes are meaningful)
   - All completed impl tasks in functional/ and non-functional/ assigned to 0.0.1

5. **Consider `release_category` field** (LOW — forward-looking)
   - Only matters when the project has both features and fixes in the same release

---

## 8. Verdict

| Component | Quality | Blocker? |
|-----------|---------|----------|
| `/release` skill | HIGH | No |
| `check_release_preconditions.ps1` | HIGH (with branch check gap) | No |
| `execute_release.ps1` | HIGH (with confusing message) | No |
| `generate_technical_release_notes.py` | HIGH | No |
| `releases/SETUP_GUIDE.md` | GOOD (missing workflow template ref) | No for commit; YES before first release |
| `releases/README.md` | HIGH | No |
| REQ-PROC-037 | VERY HIGH | No |

**TASK-PROC-036-01**: COMPLETE — commit the staged files.
**REQ-PROC-036 overall**: FUNCTIONALLY COMPLETE for 0.0.1 — one follow-up task needed (workflow template) before the first real release run.
**REQ-PROC-037**: COMPLETE.
