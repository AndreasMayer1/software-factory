# Research: Release Workflow Patterns

_Task: TASK-PROC-036-09 — Explore Release Skill Improvements_
_Date: 2026-03-28_

---

## Key Findings

### 1. CI/CD Release Gates

**Pattern: Staged pipelines with dedicated pre-release phase**

The dominant pattern across Fastlane, GitHub Actions, Codemagic, and Bitrise is a staged pipeline where different branches trigger different phases:

- **PR stage**: formatting, static analysis, tests, coverage enforcement
- **Staging stage**: build artifacts, distribute to testers (TestFlight / Firebase App Distribution)
- **Production stage**: final gate checks → publish to stores

The pre-release gate phase runs _before_ any artefact is pushed to the store and includes:
1. All tests passing
2. Coverage threshold met (automated)
3. Static analysis clean
4. Clean working tree on the release branch
5. Version not yet bumped (idempotency guard)

**Fastlane lanes as phase separators**

Fastlane models phases as separate `lane` entries in a `Fastfile`. A `pre_release` lane calls `run_tests`, then `xcov` for coverage enforcement, then `scan` for static analysis. The `release` lane depends on the `pre_release` lane completing cleanly. This is the closest structural analog to our multi-phase `/release` skill.

**GitHub Actions: environment-based gating**

GitHub Actions' native mechanism for release gates is `environment:` on a job. When a job specifies `environment: production`, GitHub pauses the job and requires configured reviewers to approve before execution resumes. This is the production-grade solution and works without third-party actions.

**Codemagic: phase scripts**

Codemagic YAML exposes `pre-test`, `post-test`, `pre-build`, `post-build`, `pre-publish`, and `post-publish` hooks. Pre-publish is the canonical location for a final quality gate (tests pass + coverage met + manual confirmation) immediately before the delivery action.

**Key takeaway**: Industry standard is to treat "pre-release checks" and "delivery" as structurally separate phases, not sequential steps in one lane. The gate between them is where the human approval lives.

---

### 2. Test Coverage Thresholds

**Flutter/Dart toolchain**

`flutter test --coverage` generates `coverage/lcov.info`. This file is the input to all threshold enforcement tools.

**Common threshold values**

| Context | Typical minimum |
|---|---|
| Open-source / hobbyist | 70–75% |
| Professional mobile app | 80% |
| Regulated / safety-critical | 90–95% |
| Google's own Flutter tooling | Not publicly prescribed; team-dependent |

The Codemagic Flutter CI/CD guide uses **70% as "a reasonable starting point for most projects"**. The `dlcov` README and `zgosalvez/github-actions-report-lcov` action both default to examples using **80%**.

**Concrete tools for Dart/Flutter**

| Tool | How to use |
|---|---|
| `dlcov` (pub.dev package) | `dlcov gen-refs && flutter test --coverage && dlcov -c 80` — exits non-zero if coverage < 80 |
| `test_cov_console` (pub.dev) | `--pass 80` flag — prints pass/fail based on threshold |
| `zgosalvez/github-actions-report-lcov` | GitHub Action that posts coverage to a PR comment and fails if below `minimum-coverage` |
| `lcov --summary` + `awk` | Shell script: extract line coverage from `lcov.info`, compare to threshold |
| SonarQube Cloud | Dart-native support via `coverage/lcov.info`; enforces quality gates centrally |

**Shell script pattern (no external tool)**

```bash
flutter test --coverage
COVERAGE=$(lcov --summary coverage/lcov.info 2>&1 | grep "lines......" | awk '{print $2}' | tr -d '%')
if (( $(echo "$COVERAGE < 80" | bc -l) )); then
  echo "Coverage ${COVERAGE}% is below threshold 80%"
  exit 1
fi
```

This requires only `lcov` (available in most CI environments).

**Important nuance: untested files**

Flutter's `flutter test --coverage` only instruments files that are actually imported in tests. Files with no tests do not appear in the report, making coverage look artificially high. `dlcov --include-untested-files=true` corrects for this. This is a significant accuracy concern for threshold enforcement.

---

### 3. Human Approval Gate Patterns

**CI/CD: environment protection rules (GitHub Actions)**

The native GitHub Actions approach attaches `environment: production` to the deploy job. GitHub pauses the job and notifies required reviewers. Reviewers approve or reject via the GitHub UI. The workflow resumes or fails accordingly. This requires no third-party action and works on free plans for public repos (paid plan for private repos with environments).

**CI/CD: trstringer/manual-approval action (free alternative)**

For private repos on free plans, the `trstringer/manual-approval` action creates a GitHub Issue assigned to named reviewers. The workflow polls until an approver comments "approved" or "lgtm". This works across all plans but requires a GitHub token and the workflow staying active during the wait.

**Bitrise: "Approve and Run Build" button**

Bitrise supports manual approval for pull request builds. The build pauses with a "Pending - Waiting for approval" status visible on the Builds page. A button triggers the actual execution. This is analogous to a confirmation gate placed before the expensive/irreversible steps.

**AI agent workflows: HITL (Human-in-the-Loop) pattern**

In AI-assisted workflows (LangGraph, LLM agents, Claude Code), the canonical pattern is **propose → confirm → execute**:

1. Agent reaches a high-stakes or irreversible step
2. Agent presents a clear, human-readable summary of what it is about to do
3. Agent explicitly pauses and waits for a keyword (e.g., "yes", "proceed", "approve")
4. On approval: continues execution
5. On anything else: stops and reports what was not done

Key design rules (from Permit.io, StackAI, and LangGraph literature):
- **Never self-approve**: the agent cannot proceed without explicit human input
- **Summarize context, not raw data**: show the human what matters (version, scope, what will be pushed), not the full script output
- **Binary choice**: approve or stop — no ambiguous middle ground
- **Irreversibility threshold**: apply HITL gates specifically before _irreversible_ actions (git tag + push, store submission)

**In a Claude Code skill context**, this translates to: display a confirmation block, then use `Read user input` / wait for a reply, and proceed only if the reply matches an approval keyword. The existing `/release` skill already does this for marketing notes (Step 4.6: loop until "approve"). The same pattern is appropriate for the pre-delivery gate.

---

### 4. Claude Code Ecosystem

**Official documentation**

Claude Code supports skill files (`.claude/skills/`) with SKILL.md frontmatter. Skills are invoked by name and can call tools, read files, and execute shell commands. There is no official "release" or "deployment" skill in the Anthropic-provided examples, but the skill format is flexible enough to implement multi-phase gating.

**Community skill collections (2025)**

Several community repositories have been created with release-related skills:

- `alirezarezvani/claude-skills` (GitHub): includes a `release-manager` skill described as "orchestrates the full release cycle with changelog generation, version bumping, and readiness checks" and supports "structured handoff between development phases." Also includes a `ci-cd-pipeline-builder` skill.
- `levnikolaevich/claude-code-skills` (GitHub): "full delivery lifecycle: Agile pipeline with multi-model AI review, project bootstrap, documentation generation." Explicitly models multi-phase delivery.
- `ahmedasmar/devops-claude-skills` (GitHub): DevOps-focused marketplace including deployment and CI/CD skills.
- `jeremylongshore/claude-code-plugins-plus-skills` (GitHub): 340+ plugins including "production orchestration patterns."
- Claude Code Plugins Hub (claudecodeplugins.io): aggregates community skills.

**Relevant patterns from community skills**

The `release-manager` skill in `alirezarezvani/claude-skills` explicitly models phase separation: readiness check → changelog → version bump → handoff. This mirrors the improvement goal: separate "is this ready to release?" from "execute the release."

The multi-agent handoff pattern (present in multiple community collections) is relevant: Phase 1 (readiness check) can be a separate agent/phase that must complete before Phase 2 (build/test) is invoked.

**Key gap**: No community skill found that implements a _coverage threshold check_ as a release gate. This is a differentiator for the improved `/release` skill.

---

### 5. Flutter Release Best Practices

**Official Flutter release process (flutter/flutter Wiki)**

The Flutter team's own release process uses branch-based promotion: `master` → `beta` → `stable`. Each promotion requires:
- All CI tests passing on the candidate commit
- No open P0 or P1 issues against the candidate
- Manual sign-off from a Flutter team member (human approval gate exists even in Google's process)

**Community consensus pre-release checklist (2024–2026)**

From multiple sources (codewithandrea.com, medium, thedebuggersitsolutions.com, scribd):

**Mandatory before every release:**
1. `flutter analyze` — zero errors and zero warnings
2. `dart format` — no formatting violations
3. All unit and widget tests passing
4. Test coverage at or above project threshold
5. No `print()` or debug logging left in production code
6. Version in `pubspec.yaml` correct (not pre-bumped)
7. Build artifact builds without errors (`flutter build appbundle` / `flutter build ipa`)
8. Signing configuration correct (production key, not debug keystore)

**Mandatory once before first release (infrastructure):**
- Error monitoring (Sentry or Crashlytics)
- Production vs development environment separation (flavors)
- Privacy policy ready

**Flutter-specific release concerns (2024–2026):**
- Google now enforces `targetSdk 35` and AAB-only (no APK) for Play Store
- App Bundles require deferred components for large apps
- `flutter build appbundle --obfuscate` is recommended for production

**Manual testing (human gate) in Flutter projects:**

Flutter's own release process includes a manual "device lab" sign-off: the build is installed on real physical devices and smoke-tested by a human before the tag is pushed. This is the direct analog of the "manual user testing confirmation gate" being requested.

The community equivalent is: run the release candidate build on a device/simulator, smoke-test core flows, then give explicit sign-off before triggering the store submission script.

---

## Recommendations

### Phase 1: Task Completion Check

**Recommendation**: Keep this as a dedicated first phase, separate from the build/test phase. The check should:
1. Verify all tasks assigned to the active release version have `status: completed` (already done by `check_release_preconditions.py` via `next_tasks.py`)
2. Show a summary of completed tasks (not just a count) so the releaser can confirm the right work is included
3. Fail hard if any open tasks remain — no "warnings only" mode

**Concrete reference**: The Codemagic PR quality gate pattern enforces `set -e` to halt on any failure. The same approach (fail hard, show output, require fix) is appropriate here.

**Implementation note**: The existing `check_release_preconditions.py` already checks open task count. The improvement is surfacing this as an _explicit named phase_ in the skill (currently it is buried inside "Step 1 — Pre-flight check" alongside branch, clean tree, and version checks). A dedicated Phase 1 output block with a task summary makes the gate visible and auditable.

---

### Phase 2: Build + Test + Coverage + Manual Confirmation

**Recommendation**: Split this into three sequential sub-steps, all within Phase 2 before the delivery script runs:

**2a — Tests + Coverage**

Run `flutter test --coverage`, then enforce a coverage threshold using one of:
- `dlcov -c 75` (Dart-native, installable via `dart pub global activate dlcov`)
- Shell + `lcov --summary` (no dependency, recommended for CI portability)

Recommended threshold: **75% line coverage** as the project floor, with guidance to raise it over time. Rationale: 70% is the cited "reasonable starting point" from the Codemagic Flutter guide; 80% is the modal "professional" threshold. 75% is a balanced starting point for a project still accumulating tests.

The coverage check must use `--include-untested-files` (or the lcov-based approach which naturally catches all tracked files) to avoid the false-high-coverage trap.

**2b — Manual smoke test gate**

Before running the delivery script, the skill should:
1. Instruct the user to install the release candidate build on a device (provide the build command)
2. Provide a brief smoke test checklist (e.g., app launches, core flow works, no crash on first open)
3. Display a confirmation block:

```
Manual smoke test required before delivery.

Build: flutter build apk --release (or appbundle for Play Store)
Test: Install and verify core flows on a real device or emulator.

Type "proceed" to continue with the delivery script, or anything else to abort.
```

4. Wait for the user to type "proceed" (case-insensitive)
5. Only if "proceed" is received: continue to Phase 3

**Design justification**: The HITL pattern from AI agent literature (permit.io, LangGraph) specifies that irreversible actions (git tag + push to store) must be preceded by an explicit human confirmation. The delivery script (`execute_release.py`) is irreversible once the tag is pushed and the version is bumped. This gate is therefore a direct application of the "propose → confirm → execute" pattern.

**2c — Final pre-delivery summary**

Before executing delivery, show a summary block:
- Active release version
- Completed tasks count
- Test pass status
- Coverage percentage
- Smoke test: confirmed by user

This summary serves as the audit record for "who confirmed what before delivery ran."

---

### Phase 3: Delivery

**Recommendation**: No changes to the delivery script itself. The improvement is in what precedes it.

The phase boundary should be explicit in the skill:
- Phase 2 ends with "All checks passed. Awaiting your confirmation to proceed with delivery."
- Phase 3 begins with "Delivery started." and runs `execute_release.py`

**Post-delivery steps** (technical notes, marketing notes, mark released, commit) remain as currently structured. The only addition is that Phase 3 should display the executed release tag after `execute_release.py` completes, confirming the exact version that was pushed.

**Concrete reference**: The Flutter team's own release process separates "tagging" from "announcing" — the tag is pushed, then the release notes are written and published as a separate subsequent action. The current `/release` skill already models this correctly.

---

## Sources

- [Mobile CI/CD in a Day: GitHub Actions + Fastlane + App Center](https://developersvoice.com/blog/mobile/mobile-cicd-blueprint/)
- [Flutter CI/CD with Fastlane and GitHub Actions - Part 1: The Basics](https://nttdata-dach.github.io/posts/dd-fluttercicd-01-basics/)
- [CI/CD for Flutter Android Apps with Fastlane & GitHub Actions](https://www.aubergine.co/insights/setting-up-ci-cd-for-flutter-android-apps)
- [How to Build a Complete Flutter CI/CD Pipeline with Codemagic (freeCodeCamp)](https://www.freecodecamp.org/news/build-a-complete-flutter-ci-cd-pipeline-with-codemagic/)
- [Flutter CI/CD with Codemagic Part 1 - Polymorph](https://polymorph.co.za/software-engineering-and-technology/automating-test-releases-for-mobile-app-development-with-codemagic/)
- [GitHub: dlcov — Dart/Flutter code coverage threshold CLI](https://github.com/emanuel-braz/dlcov)
- [dlcov on pub.dev](https://pub.dev/documentation/dlcov/latest/)
- [Efficient Code Coverage Workflow for Flutter (Medium)](https://bagiyoni.medium.com/efficient-code-coverage-workflow-for-flutter-50f29120c1bd)
- [Code Coverage in Dart/Flutter (nequalsonelifestyle.com)](https://www.nequalsonelifestyle.com/2026/03/24/code-coverage-in-dart-flutter/)
- [Flutter Test Coverage with lcov (Medium)](https://medium.com/@tagizada.nicat/flutter-test-coverage-cf7a17314340)
- [Dart test coverage — SonarQube Cloud docs](https://docs.sonarsource.com/sonarqube-cloud/enriching/test-coverage/dart-test-coverage)
- [Manual Approval in a GitHub Actions Workflow — Thomas Stringer](https://trstringer.com/github-actions-manual-approval/)
- [Adding a Manual Approval Step in GitHub Actions (Medium)](https://medium.com/@bounouh.fedi/adding-a-manual-approval-step-in-github-actions-for-controlled-deployments-on-free-github-accounts-cf7f05e759cf)
- [GitHub Deployment Environments and Approval Gates — Silvana's DevOps Blog](https://devops.silvanasblog.com/blog/github-action-deployment-gates/)
- [Manual Workflow Approval — GitHub Marketplace](https://github.com/marketplace/actions/manual-workflow-approval)
- [How to Set Up Deployment Gates in GitHub Actions (OneUptime)](https://oneuptime.com/blog/post/2025-12-20-deployment-gates-github-actions/view)
- [Human-in-the-Loop for AI Agents — Permit.io](https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo)
- [Building Human-In-The-Loop Agentic Workflows (Towards Data Science)](https://towardsdatascience.com/building-human-in-the-loop-agentic-workflows/)
- [Human-in-the-Loop AI Agents: Approval Workflows — StackAI](https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation)
- [Human-in-the-Loop Patterns for AI Agents 2026 (MyEngineeringPath)](https://myengineeringpath.dev/genai-engineer/human-in-the-loop/)
- [6 Key Steps to Take Before Releasing your Next Flutter App — codewithandrea.com](https://codewithandrea.com/articles/key-steps-before-releasing-flutter-app/)
- [Flutter App Pre-release Checklist (Medium, 2025)](https://medium.com/@atatijr/flutter-app-pre-release-checklist-4d8973d81c70)
- [Flutter App Publishing Checklist — The Debuggers](https://thedebuggersitsolutions.com/blog/flutter-app-publishing-checklist)
- [Release process — flutter/flutter Wiki on GitHub](https://github.com/flutter/flutter/wiki/Release-process)
- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
- [alirezarezvani/claude-skills — GitHub](https://github.com/alirezarezvani/claude-skills)
- [levnikolaevich/claude-code-skills — GitHub](https://github.com/levnikolaevich/claude-code-skills)
- [ahmedasmar/devops-claude-skills — GitHub](https://github.com/ahmedasmar/devops-claude-skills)
- [Claude Code Plugins Hub](https://claudecodeplugins.io/)
- [Fastlane run_tests docs](https://docs.fastlane.tools/actions/run_tests/)
- [Approving pull request builds — Bitrise Docs](https://docs.bitrise.io/en/bitrise-ci/run-and-analyze-builds/starting-builds/approving-pull-request-builds.html)
