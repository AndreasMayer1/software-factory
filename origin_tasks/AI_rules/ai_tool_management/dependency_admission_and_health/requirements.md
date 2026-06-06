---
id: REQ-PROC-060
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: active
effort: M
stakeholder: app_provider
created: 2026-05-26
updated: 2026-05-26
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — internal AI governance rule
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "No new top-level dependency (runtime or dev) is introduced into pubspec.yaml, any Python manifest under scripts/, or any npm manifest without recorded developer pre-authorization. The authorization names the package, the justification for adding it (vs. writing the functionality inline), and the developer who approved. An LLM agent that encounters a task requiring a new dependency must escalate — via the back-pressure protocol of REQ-PROC-046 — rather than self-authorize."
    - id: AC-02
      text: "Every new top-level dependency proposed for introduction satisfies all of the following admission criteria at the moment of the proposal: (a) the package has existed on its registry (pub.dev, PyPI, npm) for at least 6 calendar months; (b) the package has a permissive license compatible with closed-source distribution (MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, or Zlib — GPL and LGPL are disqualifying for runtime dependencies); (c) the package shows maintenance activity (a commit to the source repository within the last 90 days, or a stable release series at 1.x+ with fewer than 10 open issues and an explicit 'stable/done' signal from the maintainer); (d) the package's direct dependency count (its own pubspec.yaml/requirements.txt dependencies) is 5 or fewer; (e) the package scores at least 100 pub points on pub.dev (Dart packages only; equivalent quality signals for Python/npm packages). Criteria (a)–(e) are evaluated by the proposing agent and recorded as evidence alongside the developer authorization of AC-01."
    - id: AC-03
      text: "For Dart packages, a verified publisher badge on pub.dev is a strong positive signal in the admission evaluation. Packages from verified publishers (e.g. dart.dev, google.dev, invertase.dev) may have the 6-month package-age criterion (AC-02a) reduced to 30 days by explicit developer authorization. Packages from unverified publishers are held to the full criteria without reduction."
    - id: AC-04
      text: "A package whose primary functionality introduces a capability surface that the project's architecture rejects — network I/O (REQ-PROC-052 SP1), telemetry or analytics (REQ-PROC-052 SP2), or platform channels not already used by the project — is flagged as a capability-surface concern at admission. The flag is advisory, not automatically disqualifying: the proposing agent records which capability is introduced, whether the project's code would invoke it, and whether the zero-network-IO architecture mitigates the runtime risk. The developer decides whether the concern is disqualifying case by case."
    - id: AC-05
      text: "The same admission criteria (AC-02a through AC-02e, AC-03, AC-04) are applied during ongoing health re-evaluation of existing dependencies — triggered by the lifecycle cadence defined in the sibling requirement (REQ-PROC-061). A package that was healthy at admission can become unhealthy (license change, maintainer abandonment, discontinued flag on pub.dev, pub points drop below threshold). When a health re-evaluation surfaces a failing criterion, the agent records the finding and escalates to the developer with a recommendation (continue, replace, or remove)."
    - id: AC-06
      text: "An admission criterion that cannot be satisfied may be overridden only by an explicit, recorded developer authorization for the specific package and criterion. The override is recorded next to the change (commit message, task protocol, or a designated override-log file) and names: the package, the criterion being overridden (AC-02a/b/c/d/e, AC-03, or AC-04), and the reason. This mechanism reuses the same override pattern as REQ-PROC-056 AC-07. Silent override — an agent adding a dependency that fails a criterion without recording the exception — is forbidden."
    - id: AC-07
      text: "The admission criteria, the override path, the autonomy boundary (what the agent may do without human authorization), and the health-evaluation procedure are documented in a single authoritative location consistent with this requirement — an agent (LLM or human) can determine, without asking, what is required to add a new dependency and what properties an existing dependency must maintain."
---

# Dependency Admission & Package Health

## Overview

This requirement defines when a new dependency may be added to the project and what package-level health properties every dependency — new or existing — must satisfy. It governs the package as a unit: should this package exist in our project, and is it healthy enough to stay? The sibling requirements complete the dependency-governance surface: REQ-PROC-056 governs which *version* of an admitted package may enter; REQ-PROC-061 governs *when* existing dependencies are re-evaluated and how updates and replacements are carried out; REQ-PROC-052 governs what the project's *code* may do with any dependency at runtime.

## Purpose

The strongest supply-chain defense is not adding the dependency in the first place. Every top-level dependency is an irreversible expansion of the project's attack surface and long-term maintenance burden. In a project where most code is produced by LLM agents, the default behavior of an LLM is to reach for a package whenever it encounters a problem — because that is what public training examples overwhelmingly model. Without a contractual gate, an agent will accumulate dependencies until the transitive tree becomes unauditable.

The app provider (PERSONA-015) is a solo developer maintaining a mental-health application on the values of *longevity over velocity* and *simplicity as a survival strategy for one-person maintenance over years*. The system/maintenance constraints (PERSONA-004) demand zero tolerance for data loss and support for 2017-era hardware. Every dependency added is a future maintenance obligation — version bumps, deprecation migrations, API breakage, potential abandonment — that falls on one person.

The Dart/pub.dev ecosystem has significantly weaker supply-chain tooling than npm or PyPI. There is no Socket.dev coverage for Dart packages (no maintainer-change alerting, no capability analysis, no typosquatting detection), no Snyk Advisor for pub.dev, and no `dart pub audit` command. The project's primary defenses are therefore: (1) the 7-day version cooldown of REQ-PROC-056, (2) the zero-network-IO architecture of REQ-PROC-052 SP1 (even a compromised dependency cannot exfiltrate data at runtime), and (3) this requirement's manual admission checklist — evaluated by the proposing agent and recorded as evidence, not enforced by an automated scanner.

The admission checklist is deliberately *manual* — not because automation would be unwelcome, but because the Dart ecosystem does not yet offer the tooling to automate package-health evaluation at the level npm projects enjoy via Socket.dev or Snyk. When such tooling becomes available for Dart, the enforcement model of this requirement should evolve from manual-with-evidence to automated-with-override.

Industry reference: Bitwarden — the only privacy-focused open-source project with a published dependency governance policy (2025/2026) — requires team ownership sign-off for every new dependency in shared repos, uses Renovate with a 7-day minimumReleaseAge, and separates admission from lifecycle management structurally. No published AI-agent governance framework (Codex, Claude Code community patterns, aider, OpenHands) treats "add new dependency" as a distinct permission class — this project innovates here, justified by the privacy sensitivity of the data it protects.

## Behavior

### The Admission Gate

When an LLM agent determines that a task requires a new top-level dependency (one not already present in the relevant manifest), the following sequence applies:

1. The agent evaluates the admission criteria (AC-02) against the candidate package and records the results as evidence (same DG3-style artifact pattern as REQ-PROC-056).
2. The agent checks for capability-surface concerns (AC-04) and records findings.
3. The agent escalates to the developer with the evaluation results and a recommendation (add / do not add / consider alternative).
4. The developer authorizes or rejects the addition (AC-01). The authorization is recorded next to the change.
5. If authorized and a version is selected, REQ-PROC-056's version-intake gates (DG1–DG4) apply to the chosen version.

The admission gate applies to `pubspec.yaml` dependencies (both `dependencies:` and `dev_dependencies:`), Python manifests under `scripts/`, and npm manifests used by automation skills. It does not apply to OS-level packages (governed by `claude-install-os-tool`) or to transitive dependencies pulled in by an approved direct dependency (those are covered at the version level by REQ-PROC-056 when the lockfile is resolved).

### The Health Checklist

The admission criteria form a checklist, not a scoring system. Each criterion is binary (pass/fail), and all must pass for a package to be admissible without an override. The criteria are:

| Criterion | What the agent checks | Pass condition |
|---|---|---|
| **Package age** | Registry publication date of the package (not the version) | ≥ 6 months on pub.dev / PyPI / npm (reduced to 30 days for verified publishers with explicit developer authorization) |
| **License** | License field on registry; SPDX identifier | MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, or Zlib. GPL/LGPL disqualifying for runtime deps. |
| **Maintenance** | Source repository commit history; issue tracker | Commit in last 90 days, OR stable 1.x+ with <10 open issues and explicit maintainer "stable" signal |
| **Transitive footprint** | Package's own dependency list | ≤ 5 direct dependencies |
| **Quality score** | pub.dev pub points (Dart) | ≥ 100 pub points |
| **Capability surface** | Package documentation, API surface, imports | Advisory flag if package introduces network I/O, telemetry, or unused platform channels |

### Ongoing Health Re-evaluation

The same criteria apply when an existing dependency is re-evaluated during the lifecycle cadence of REQ-PROC-061. A package that was healthy at admission can become unhealthy:

- Maintainer abandons the package (no commits in >12 months, issues unanswered)
- pub.dev marks the package as "discontinued"
- License changes to an incompatible license
- Pub points drop below the threshold
- A capability-surface concern emerges (package adds network I/O in a new version)

When a health re-evaluation surfaces a failing criterion, the agent records the finding, assesses severity (blocking vs. advisory), and escalates to the developer with a recommendation: continue with documented risk acceptance, replace with an alternative (triggering a new R-A admission + REQ-PROC-061 replacement workflow), or remove the dependency if no longer needed.

### LLM Autonomy Boundary

| Operation | Autonomy level |
|---|---|
| Add a new top-level runtime dependency | Human pre-authorization required |
| Add a new dev_dependency | Human pre-authorization required |
| Evaluate health of an existing dep (read-only) | Fully autonomous |
| Block/refuse a dep that fails a health criterion | Autonomous (refusal is the safe default) |
| Override a failed health criterion | Forbidden without recorded developer authorization (reuses REQ-PROC-056 AC-07 pattern) |

### Override Path

A criterion that cannot be satisfied may be overridden by recorded developer authorization. The override names the package, the specific criterion (AC-02a/b/c/d/e, AC-03, or AC-04), and the reason. The agent must not self-authorize — it escalates via the back-pressure protocol of REQ-PROC-046.

## Developer Guidelines

### Key Decisions

- **The default is to not add.** The burden of proof is on the proposer — the agent must demonstrate that adding the dependency is justified (vs. writing the functionality inline or using an existing dependency).
- **Admission is a one-time gate; health is ongoing.** The admission criteria are checked once at entry and then re-checked during lifecycle sweeps. A package does not need to be re-admitted after a version bump.
- **Evidence is part of the proposal.** A dependency proposal without the health-checklist evaluation is incomplete, in the same way a dependency bump without REQ-PROC-056 DG3 evidence is incomplete.
- **The checklist is manual, not automated.** The Dart ecosystem lacks tooling for automated package-health enforcement. The agent evaluates criteria by inspecting pub.dev, the source repository, and the package's API surface. When automated Dart supply-chain tooling becomes available, this requirement should evolve to leverage it.
- **Capability surface is advisory.** The zero-network-IO architecture (REQ-PROC-052 SP1) means even a compromised dependency cannot exfiltrate data at runtime. Capability-surface flags inform the developer's decision but do not automatically block admission.

### Common Pitfalls

- **"It's popular, so it's safe"**: download count correlates with ecosystem trust but not with package health. The event-stream incident (2018) involved one of npm's most-downloaded packages. Popularity is not an admission criterion.
- **"It's a dev dependency, so it's low risk"**: dev dependencies run code on the developer's machine during build, test, and analysis. A compromised dev dependency can modify source files, inject code into build output, or exfiltrate repository contents. The admission gate applies equally.
- **"The existing dep handles this, I just need a complementary package"**: adding a second package for what the first package already provides (or could provide with a minor usage change) doubles the maintenance surface. Verify the existing dep doesn't cover the need before proposing a new one.
- **"The package is from Google/Dart team, no need to check"**: verified publishers get a reduced package-age threshold (30 days vs. 6 months), not a bypass. All other criteria still apply.
- **Confusing package age with version age**: AC-02a checks when the *package* was first published on the registry (not the version). REQ-PROC-056 DG1 checks when the *version* was published. Both are needed — a new version of a new package faces both gates.

## Related Requirements

- **REQ-PROC-056 (Dependency Supply-Chain Safety)** — sibling. Governs which *version* of an already-admitted package may enter. AC-01's admission gate precedes REQ-PROC-056's version-intake gates (DG1–DG4) in the dependency-addition workflow.
- **REQ-PROC-061 (Dependency Lifecycle & Update Cadence)** — sibling. Governs *when* existing dependencies are re-evaluated (triggering the health re-evaluation of AC-05) and how replacements are carried out.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — SP1 (no network I/O) and SP2 (no telemetry SDKs) enforce code-level behavior; this requirement catches package-level capability concerns *before* the code lands in `lib/`. The zero-network-IO architecture provides defense-in-depth.
- **REQ-PROC-046 (Code Quality Standard)** — source of the back-pressure protocol that AC-01's escalation and AC-06's override mechanism inherit.
- **REQ-PROC-053 (External Documentation Lookup)** — AC-02's active-signal list already requires a lookup when introducing a new dependency. This requirement adds the *admission decision* that precedes the lookup.
- **REQ-PROC-055 (External Plugin Adoption)** — sibling governance boundary. REQ-PROC-055 covers adoption of external *plugins* (VS Code extensions, Claude Code MCP servers, etc.) and explicitly excludes software-package supply-chain safety, pointing to REQ-PROC-056 and its siblings (this requirement, REQ-PROC-061) for that scope. The two requirements together define non-overlapping surfaces: plugins vs. pub/PyPI/npm packages.

## References

- `requirements_user_needs/personas/app_provider/persona.md` — source of the "longevity over velocity" and "simplicity" values that motivate dependency minimalism.
- `requirements_user_needs/personas/system_maintenance/persona.md` — source of the data-sensitivity constraints.
- `requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/tasks/2026-05-21_explore_dependency-lifecycle-and-admission-gap-analysis/plans_and_protocols/2026-05-26_03_synthesis_v2_with_research.md` — the discovery synthesis (with web research) that produced this requirement.
- `requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/tasks/2026-05-21_explore_dependency-lifecycle-and-admission-gap-analysis/plans_and_protocols/2026-05-26_02_web_research_findings.md` — industry prior art: Bitwarden dependency governance, AI-agent frameworks, Dart ecosystem tooling gaps, supply-chain incident analysis.
- Industry references (non-normative): Bitwarden contributing docs (`contributing.bitwarden.com/contributing/dependencies/`), William Woodruff 7-day cooldown analysis, Socket.dev 2025 malware report.
