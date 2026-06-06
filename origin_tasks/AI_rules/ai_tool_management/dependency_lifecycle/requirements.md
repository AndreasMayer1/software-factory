---
id: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: app_provider
created: 2026-05-26
updated: 2026-06-03
after: [REQ-PROC-056]
blocks: []
market_research_refs: [] # No relevant findings identified — internal AI governance rule
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "A monthly dependency review is performed: the agent runs flutter pub outdated (for Dart) and the equivalent outdated-check for Python manifests under scripts/, evaluates each available upgrade against the version-intake gates of REQ-PROC-056 (DG1–DG4), and produces a grouped update proposal. The monthly cadence is triggered by a calendar mechanism (recurring task, orchestrator schedule, or equivalent) — it does not depend on the agent remembering to check."
    - id: AC-02
      text: "Event-based triggers surface dependency actions immediately, outside the monthly batch: (a) a security advisory is disclosed for a pinned version (surfaced by osv-scanner, pub.dev advisory warnings during dart pub get, or equivalent); (b) flutter analyze or dart fix --apply surfaces a deprecation warning originating from a dependency API; (c) a build failure or quality-gate failure is caused by a dependency incompatibility; (d) a package is flagged as discontinued on pub.dev. Each event-based trigger produces a recorded finding — the agent does not silently ignore it."
    - id: AC-03
      text: "Before any release candidate is approved, a mandatory dependency sweep runs: flutter pub outdated + osv-scanner (or equivalent advisory scanner) over all in-scope manifests. No release candidate ships with a dependency version for which a known, unresolved security advisory exists at the time of the sweep. This sweep is a gate on the release workflow (integration point with REQ-PROC-036)."
    - id: AC-04
      text: "Deprecation signals are classified by urgency: (a) immediate — security advisory with known-exploited status, build failure; (b) normal — dart fix deprecation warnings, discontinued flag, available minor/patch upgrades surfaced by monthly review; (c) deferred — packages with no release in >12 months (potential abandonment), available major-version upgrades, cosmetic improvements with no security implication. The agent acts on immediate signals within the current task/session, batches normal signals into the next monthly review, and records deferred signals for quarterly evaluation."
    - id: AC-05
      text: "When an existing dependency must be replaced (abandonment, incompatible license change, discontinued without successor, or irrecoverable deprecation), the replacement workflow applies: (a) candidate replacements are evaluated against the admission criteria of REQ-PROC-060 (AC-02a through AC-02e, AC-03, AC-04); (b) the replacement requires human pre-authorization (it is a new admission); (c) the migration is scoped as a dedicated task, not buried inside unrelated work; (d) the new version pin passes REQ-PROC-056's intake gates (DG1–DG4)."
    - id: AC-06
      text: "Patch-level and minor-level version bumps of existing dependencies are autonomous (with recorded evidence) when: the new version passes REQ-PROC-056's intake gates (DG1–DG4), and the project's quality gates (REQ-PROC-046, REQ-PROC-002, REQ-PROC-052) pass after the update. No human pre-authorization is required for patch/minor bumps that satisfy these conditions."
    - id: AC-07
      text: "Major-version bumps (semver-major) of existing dependencies require human pre-authorization. The agent proposes the bump with: the package name, current and target versions, a summary of breaking changes from the CHANGELOG or migration guide (obtained via the REQ-PROC-053 lookup policy), an assessment of which project call sites are affected, and the results of running the project's quality gates against the bumped version."
    - id: AC-08
      text: "The regression-confirmation contract scales with the change class: (a) patch/minor bumps — the existing quality gates (REQ-PROC-046 G1–G8, REQ-PROC-002 TQ1–TQ4, REQ-PROC-052 SP1–SP6) are sufficient; no additional testing required; (b) major bumps — standard gates plus the agent reads the package's CHANGELOG/migration guide and verifies API changes in project call sites; integration tests run if the package touches a critical path; (c) package replacement — same as major bump, plus a dedicated test pass exercising the replaced functionality."
    - id: AC-09
      text: "Running flutter pub upgrade without first checking which versions would change, or without evaluating each changed version against REQ-PROC-056's intake gates, is forbidden. The agent must inspect the available upgrades (via flutter pub outdated or equivalent), evaluate each candidate version, and apply only the versions that pass the gates. Blanket upgrade-then-check-if-it-works is not a valid workflow."
    - id: AC-10
      text: "The trigger model, cadence, deprecation-urgency classification, usage-check classification, replacement workflow, regression-confirmation contract, and autonomy boundaries are documented in a single authoritative location consistent with this requirement — an agent can determine, without asking, when to check for updates, what to do with each class of finding, and what level of authorization is needed."
    - id: AC-11
      text: "The monthly review includes a usage-check pass that classifies each direct dependency in pubspec.yaml as: (a) directly imported — at least one import statement in lib/, test/, or integration_test/ references the package; (b) indirectly required — the package provides platform binaries, code-generation assets, or runtime support consumed by another admitted direct dependency, and this indirect requirement is explicitly documented in the review proposal; or (c) no evidence of use — neither (a) nor (b) applies. Packages classified as (c) are listed in the review proposal as removal candidates, not as upgrade candidates. The usage-check pass runs before version-bump evaluation so that upgrade effort is not spent on unused packages."
    - id: AC-12
      text: "After each monthly batch review produces a proposal under automation/dependency_reviews/, a designated reusable decision task in requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/tasks/ is set to status pending. The decision task is the developer's single entry point for reviewing the monthly proposal and authorizing downstream actions: (a) autonomous bumps and removal candidates — once the developer authorizes, an agent executes them within the same task session; (b) major-version bumps — a dedicated follow-up impl task is created per authorized bump (not executed inline), scoped to the migration work required. The task is not recreated monthly — the same task folder is reused by resetting its status to pending at the start of each new review cycle. The active review month and proposal path are recorded in the task's protocol at each reset."
    - id: AC-13
      text: "The usage-check pass recognizes structural evidence of use that is not a Dart import statement, so packages exercised through configuration or native platform participation are not misclassified as removal candidates: (a) a package referenced as an analyzer plugin, ruleset, or custom_lint entry in analysis_options.yaml is classified config-referenced and is not a removal candidate; (b) a package declared as a native plugin for at least one target platform in the project's flutter-plugins-dependencies manifest is flagged native-declared and surfaced for manual call-site verification rather than listed as a plain removal candidate (native declaration is evidence of being built, not of being used). The proposal presents removal candidates in tiers that separate likely-dead packages from those retained via (a) or flagged via (b), so the reviewer is not forced to re-adjudicate the same structural false positives as if they were genuinely unused."
    - id: AC-14
      text: "A developer decision to retain a package that the usage-check flagged as a removal candidate is persisted in a data-owned registry that records, per package: the package name, the retention class (indirect, config, native, or other), the reason, and the acknowledgement date. The usage-check reads this registry and presents acknowledged-kept packages in a classification distinct from active removal candidates, so an acknowledged false positive does not reappear in the active removal-candidate list of subsequent monthly reviews. A registry entry whose package is no longer present in the manifests is reported as stale rather than silently retained."
    - id: AC-15
      text: "Removal of an authorized removal candidate is confirmed empirically rather than by manual code search. With the package removed on an isolated branch, the project's analyzer, test suite, and the build-plus-smoke lanes for every target platform covered by CI must pass; if any fail, the removal is reverted and the failing signal (compile, link, or test error) is recorded as that package's retention justification in the AC-14 registry. For a package whose target platforms include platforms with no CI lane, removal may be confirmed once all CI-covered platforms pass, provided the uncovered platforms are recorded as accepted residual risk in the proposal and the decision task. A package used only via configuration or code generation (config-referenced, or a code-generation tool) is exempt from empirical trial-removal, because its removal produces no test or build failure; its retention is decided by the configuration or code-generation reference instead."
---

# Dependency Lifecycle & Update Cadence

## Overview

This requirement defines when existing dependencies are re-evaluated, what triggers action, and how updates and replacements are carried out safely. It governs the temporal dimension of dependency management: not *whether* a package should exist (REQ-PROC-060) or *which version* is safe to pin (REQ-PROC-056), but *when* version changes happen and *how the work is run*.

## Purpose

Dependencies that are never revisited accumulate two classes of risk silently: (1) known vulnerabilities disclosed after the version was pinned, and (2) staleness that makes future upgrades progressively harder as API drift accumulates. In a project where an LLM agent runs autonomous sessions on most days but has no built-in trigger to update dependencies, the realistic risk is *silent staleness*, not over-eager updates.

The app provider (PERSONA-015) maintains this project alongside a full-time job, with the value *longevity over velocity*. The system/maintenance constraints (PERSONA-004) demand that the app run reliably on 2017-era hardware and never lose mental-health entries. A dependency update that breaks the app is a direct threat to both values — but so is a dependency that silently rots until a forced upgrade becomes a multi-day migration.

The cadence model balances these tensions: a monthly batch review catches silent staleness before it compounds, event-based triggers surface urgent signals immediately, and a per-release sweep ensures no known-vulnerable version ships. The model deliberately avoids aggressive time-based auto-upgrade (daily/weekly `pub upgrade` runs) — that would fight REQ-PROC-056's "default is to wait" principle and create unnecessary churn in a project that prioritizes stability.

Industry reference: the converging recommendation from OWASP, OpenSSF Scorecard, Bitwarden's published policy, and community best practice (William Woodruff's cooldown analysis) for solo/small teams is: monthly batched updates with a 7-day minimum release age and immediate security patches. This requirement follows that recommendation.

## Behavior

### The Trigger Model

Three trigger layers are active, ordered by urgency:

| Layer | Trigger | When it fires | Agent response |
|---|---|---|---|
| **Event-based (immediate)** | Security advisory for a pinned version; build failure from dep incompatibility | As soon as surfaced during any task | Act within the current task/session: evaluate upgrade, apply if gates pass, escalate if not |
| **Monthly batch** | Calendar cadence (recurring task or orchestrator schedule) | Once per calendar month | Run usage-check pass (AC-11), then `flutter pub outdated` + `osv-scanner`; evaluate all available upgrades; propose a grouped update |
| **Per-release sweep** | Release-candidate preparation | Before each release candidate is approved | Mandatory `pub outdated` + `osv-scanner` run; no release with known-vulnerable dependencies |

**Not included**: aggressive time-based auto-upgrade (daily/weekly `flutter pub upgrade`). This would fight REQ-PROC-056's "default is to wait" and is inappropriate for a stability-oriented project.

### Monthly Review Usage-Check Pass

Before evaluating available version upgrades, the monthly review classifies every direct dependency in `pubspec.yaml` into one of three buckets:

| Classification | Condition | Review action |
|---|---|---|
| **Directly imported** | ≥1 `import` statement in `lib/`, `test/`, or `integration_test/` references the package | Proceed to version-bump evaluation normally |
| **Indirectly required** | Package provides platform binaries, code-generation assets, or a runtime support library consumed by another admitted direct dependency; the indirect requirement is documented in the proposal | Proceed to version-bump evaluation; document the dependency chain |
| **Config-referenced** (AC-13a) | Package is referenced as an analyzer plugin, ruleset, or `custom_lint` entry in `analysis_options.yaml` | Retain — not a removal candidate; its use is the config reference |
| **Native-declared** (AC-13b) | Package is declared as a native plugin for ≥1 target platform in the flutter-plugins-dependencies manifest | Surface for manual call-site verification; native declaration proves it is *built*, not that it is *used* |
| **Acknowledged-kept** (AC-14) | Package appears in the retention registry from a prior cycle's keep decision | Present separately; not an active removal candidate |
| **No evidence of use** | None of the above | List as a **removal candidate** in the proposal — do not propose a version bump |

The classification runs before version-bump evaluation. Spending effort evaluating a version upgrade for an unused package is waste; classifying first ensures the upgrade proposal only covers packages the project actually depends on. The proposal presents removal candidates in tiers: *likely-dead* (no evidence of any kind) separated from *needs-manual-review* (native-declared) and *retained* (indirect, config-referenced, acknowledged-kept), so structural false positives are not re-adjudicated each cycle as if genuinely unused.

**Indirect-requirement documentation rule**: A package classified as indirectly required must name the consuming direct dependency (e.g. "`sqlite3_flutter_libs` — platform binaries required by `drift` NativeDatabase on desktop"). If the chain cannot be named, the package is classified as no-evidence-of-use.

**Native-declaration caveat**: A package's presence in the generated plugin registrant or the flutter-plugins-dependencies manifest is *circular evidence* — Flutter generates those entries from every declared plugin regardless of whether the Dart side ever calls it. Native declaration therefore downgrades a package from *removal candidate* to *needs-manual-review*; it never auto-retains it. Confirmation of actual use still requires either a Dart call site or the empirical trial-removal of AC-15.

### False-Positive Recovery

A removal candidate that the developer decides to keep is recovered through two complementary mechanisms, so the decision is made once and the same false positive does not resurface every cycle.

**Durable retention registry (AC-14)**: The keep decision is persisted in a data-owned registry — package name, retention class (`indirect` / `config` / `native` / `other`), reason, acknowledgement date. The usage-check reads it and lists those packages as *acknowledged-kept*, outside the active removal-candidate list. Unlike the indirect-requirement allowlist (which only admits a package whose *consuming dependency* can be named), the registry accepts every retention class — including config-referenced and standalone-native packages that have no consuming dependency to name. A registry entry whose package no longer exists in the manifests is reported as stale.

**Empirical trial-removal (AC-15)**: When removal *is* authorized, it is confirmed by experiment, not by code archaeology — because a removal candidate is by definition un-imported, so a green run is necessary but not sufficient. On an isolated branch the package is removed and the analyzer, tests, and every CI-covered platform's build-plus-smoke lane are run. A red result reverts the removal and writes the failing signal into the retention registry as concrete keep-justification (the build/link error names the consumer the allowlist rule demands). Platforms with no CI lane are recorded as accepted residual risk rather than blocking the removal. Config-referenced and code-generation packages are exempt — removing them produces no test or build failure, so their retention is decided by the configuration or code-generation reference, never by trial-removal.

### Review Output Handoff

When the monthly batch review writes its proposal to `automation/dependency_reviews/YYYY-MM/`, the agent resets the designated decision task to `pending`. The decision task is the developer's single action-authorization entry point: it presents the proposal and prompts the developer to approve, defer, or skip each class of finding.

**Execution model by finding class:**

| Finding class | Developer action | Agent response |
|---|---|---|
| Autonomous bumps (patch/minor, DG1–DG4 green) | Approve or defer | Execute the bumps within the same session; run quality gates; record evidence |
| Removal candidates (no-evidence-of-use packages) | Approve removal or keep | Remove from `pubspec.yaml` and run `flutter pub get`; run quality gates |
| Major-version bumps | Pre-authorize or defer | Create a dedicated scoped impl task per authorized bump; do NOT execute inline |

The decision task is reused across monthly cycles — the same task folder receives a `pending` reset at the start of each new cycle; no new folder is created per month. The cycle month and proposal path are recorded in the task's protocol so the developer immediately knows which review is being actioned.

### Deprecation-Signal Aggregation

Dependencies surface deprecation through multiple channels. The policy aggregates these into a three-tier urgency classification:

| Urgency | Signals | Agent action |
|---|---|---|
| **Immediate** | Security advisory with known-exploited status; build failure caused by dependency | Act within current session — upgrade, patch, or escalate |
| **Normal** | `dart fix --apply` deprecation warnings; package flagged "discontinued" on pub.dev; available minor/patch upgrades in monthly review | Batch into next monthly review; record the finding |
| **Deferred** | No release in >12 months (potential abandonment); available major-version upgrades; cosmetic "better alternative" available | Record for quarterly evaluation; no action unless it causes a gate failure |

A deprecated API that still functions at the pinned version with no security implication is acceptable to defer indefinitely. The agent records the deferral rationale — future sessions see the documented decision, not a silent gap.

### The Replacement Workflow

When an existing dependency must be replaced (abandonment, incompatible license change, discontinued without successor, irrecoverable deprecation), the following sequence applies:

1. The agent identifies candidate replacements and evaluates each against the admission criteria of REQ-PROC-060.
2. The replacement is a new admission — the same human-pre-authorization gate applies.
3. The migration is scoped as a dedicated task (not buried inside another task's work). The task references the deprecation finding that triggered the replacement.
4. REQ-PROC-056's version-intake gates (DG1–DG4) apply to the replacement's version pin.
5. The regression-confirmation contract for replacements (AC-08c) applies: standard quality gates plus a dedicated test pass exercising the replaced functionality.

### Regression Confirmation

The confirmation depth scales with the change class:

| Change class | Required confirmation |
|---|---|
| **Patch bump** | REQ-PROC-046 + REQ-PROC-002 + REQ-PROC-052 quality gates (standard back-pressure) |
| **Minor bump** | Same as patch (semver contract implies no breakage; gates catch violations) |
| **Major bump** | Standard gates + CHANGELOG/migration guide review (REQ-PROC-053 lookup) + verification of affected call sites + integration tests if package touches a critical path |
| **Package replacement** | Same as major bump + dedicated test pass for replaced functionality |

### LLM Autonomy Boundary

| Operation | Autonomy level |
|---|---|
| Patch-level bump, REQ-PROC-056 + quality gates pass | Autonomous with recorded evidence |
| Minor-level bump, gates green, no API breakage | Autonomous with recorded evidence |
| Major-version bump | Human pre-authorization required |
| Package replacement | Human pre-authorization required (new admission via REQ-PROC-060) |
| Defer a deprecation past a release | Autonomous with recorded rationale |
| Flag package with no evidence of use as removal candidate | Autonomous with recorded classification |
| Classify a package config-referenced / native-declared / acknowledged-kept | Autonomous with recorded classification |
| Append a keep decision to the retention registry | After developer authorizes the keep at the decision task |
| Confirm an authorized removal via empirical trial-removal (covered platforms) | Autonomous once removal is authorized; revert on red |
| Accept residual risk for an uncovered platform on removal | Developer acknowledges in the decision task |
| Reset decision task to `pending` after monthly review proposal is written | Autonomous |
| Run `flutter pub upgrade` without checking | Forbidden |
| Self-authorize a REQ-PROC-056 override | Forbidden (REQ-PROC-056 AC-07) |

## Developer Guidelines

### Key Decisions

- **Monthly is the cadence, not faster.** The monthly batch review is the minimum frequency that prevents silent staleness while respecting the project's stability orientation. More frequent sweeps are noise for a solo developer; less frequent risks compound staleness.
- **Events override cadence.** A security advisory doesn't wait for the monthly review. Event-based triggers are immediate and take precedence.
- **Patch/minor bumps are autonomous; major bumps are gated.** This reflects the semver contract: patch/minor versions should not break callers. When they do (semver violation), the quality gates catch it. Major versions signal intentional breakage and require human judgment.
- **Replacement is admission.** Swapping `package:foo` for `package:bar` is not an "update" — it is removing one dependency and admitting another. Both gates apply.
- **The gates catch the breakage; the cadence catches the staleness.** REQ-PROC-046/002/052 prevent a bad update from shipping; this requirement prevents the absence of updates from accumulating risk.

### Common Pitfalls

- **"I'll update deps when something breaks"**: reactive-only cadence misses silent rot. A package with a disclosed CVE that doesn't break the build still ships vulnerable code. The monthly review catches this.
- **"`flutter pub upgrade` is safe because our tests pass"**: `pub upgrade` moves *every* dependency to its latest resolvable version simultaneously. If any single upgraded version is compromised (and less than 7 days old), REQ-PROC-056 DG1 fails — but the agent won't know unless it inspects each changed version individually. The correct workflow is `pub outdated` → evaluate → selective upgrade.
- **"This deprecation warning is harmless, I'll ignore it"**: harmless today, but deprecations compound. The deferred-urgency classification is acceptable; ignoring without recording is not. Future sessions must see the documented deferral.
- **"Major bumps are just like minor bumps with more changes"**: major bumps signal that the maintainer intentionally broke the API. The extra confirmation (CHANGELOG review, call-site verification) is not overhead — it's the contract.
- **Skipping the per-release sweep**: "we already reviewed deps this month" does not satisfy the per-release gate. Advisories are disclosed daily; the sweep must run at release time, not at review time.
- **Proposing upgrades for unused packages**: a package that appears in `pubspec.yaml` but has no imports in `lib/` is a removal candidate, not an upgrade candidate. Spending DG1–DG4 evaluation effort on it — and writing upgrade tasks — is waste. Run the usage-check pass first. A package may still be *indirectly required* (e.g. platform binaries for another direct dep); that indirect requirement must be named explicitly, not assumed.
- **Treating an un-imported package as automatically dead**: analyzer/lint plugins (referenced in `analysis_options.yaml`), code-generation tools, and native plugins are exercised without a Dart `import`. Removing them on the strength of "no import found" silently weakens analysis or breaks a platform build that the local test suite never exercises. The config-referenced and native-declared classes exist precisely to stop this.
- **Trusting a green test run as proof of safe removal**: removal candidates are un-imported by definition, so removing one usually breaks nothing the analyzer or `flutter test` can see. Green is necessary, not sufficient. Confirmation must include every CI-covered platform's build, and uncovered platforms are accepted residual risk — not silently assumed safe.
- **Re-adjudicating the same false positive every month**: if a keep decision is not written to the retention registry, the package returns to next month's removal-candidate list and trains the reviewer toward a rubber-stamp "approve". Persist the keep with its reason; decide once.

## Related Requirements

- **REQ-PROC-060 (Dependency Admission & Package Health)** — sibling. Supplies the admission criteria that replacement candidates must satisfy (AC-05). Supplies the health re-evaluation criteria triggered by this requirement's cadence (REQ-PROC-060 AC-05).
- **REQ-PROC-056 (Dependency Supply-Chain Safety)** — sibling. Every version change surfaced by this requirement's cadence must pass the intake gates (DG1–DG4). This requirement defines *when* version changes happen; REQ-PROC-056 defines the *safety gates* any such change must pass.
- **REQ-PROC-046 (Code Quality Standard)** — source of the back-pressure protocol. Quality gates are the regression-confirmation mechanism for patch/minor/major bumps.
- **REQ-PROC-002 (Test Quality Standard)** — test gates compose with quality gates as the regression-confirmation contract.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — SP1–SP6 gates compose with quality gates.
- **REQ-PROC-053 (External Documentation Lookup)** — AC-07's major-bump workflow requires reading the package's CHANGELOG/migration guide, which is a lookup trigger under REQ-PROC-053.
- **REQ-PROC-036 (Release Workflow)** — AC-03's per-release sweep is a gate on the release workflow.
- **REQ-PROC-055 (External Plugin Adoption)** — sibling governance boundary. REQ-PROC-055 covers adoption of external *plugins* (VS Code extensions, Claude Code MCP servers, etc.) and explicitly excludes software-package supply-chain safety, pointing to REQ-PROC-056 and its siblings (REQ-PROC-060, this requirement) for that scope. The two requirements together define non-overlapping surfaces: plugins vs. pub/PyPI/npm packages.

## References

- `requirements_user_needs/personas/app_provider/persona.md` — source of the stability-over-velocity values.
- `requirements_user_needs/personas/system_maintenance/persona.md` — source of data-sensitivity constraints.
- `requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/tasks/2026-05-21_explore_dependency-lifecycle-and-admission-gap-analysis/plans_and_protocols/2026-05-26_03_synthesis_v2_with_research.md` — discovery synthesis.
- `requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/tasks/2026-05-21_explore_dependency-lifecycle-and-admission-gap-analysis/plans_and_protocols/2026-05-26_02_web_research_findings.md` — web research: cadence recommendations, incident analysis.
- Industry references (non-normative): OWASP Dependency-Check guidance, OpenSSF Scorecard `Dependency-Update-Tool` check, Bitwarden Renovate configuration, William Woodruff dependency-cooldown analysis, NIST SP 800-218 (SSDF) practice PW.4.
