---
id: REQ-PROC-056
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: active
effort: M
stakeholder: app_provider
created: 2026-05-21
updated: 2026-05-21
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — internal AI governance rule
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "No dependency version is introduced into the repository whose upstream publication timestamp is less than 7 days old at the moment the change is made. The rule applies symmetrically to new dependencies and to version upgrades of existing dependencies."
    - id: AC-02
      text: "No dependency version is introduced into the repository for which a security advisory (CVE, GitHub Security Advisory, pub.dev advisory, PyPI / OSV advisory, npm advisory) is published and unresolved at the moment the change is made. Resolution means either: (a) the advisory marks the specific version as not affected, or (b) a patched version exists that itself satisfies AC-01."
    - id: AC-03
      text: "Every dependency change committed to the repository carries verifiable evidence that AC-01 and AC-02 were checked before the change: the agent that proposed the change produced an artifact (commit-attached note, task protocol entry, or check-script run log) naming the version, its publication date, and the advisory-database state at the time of the check. Absence of the artifact is treated as failure of this requirement."
    - id: AC-04
      text: "The age check (AC-01) and the advisory check (AC-02) compose: a version that is older than 7 days is not automatically safe, and a version with no advisory is not automatically safe. Both must pass independently for a dependency change to be admissible."
    - id: AC-05
      text: "The rule applies to dependencies the project executes or ships: `pubspec.yaml` (Dart / Flutter runtime + dev dependencies, including those resolved via `pubspec.lock`), Python packages declared in `requirements*.txt` / `pyproject.toml` / `uv.lock` files anywhere under `scripts/`, npm packages installed by automation skills, and any equivalent package-manifest files that land in the repository. The rule does not extend to OS-level packages (`apt`, `brew`) installed by the devcontainer or by `claude-install-os-tool`; those are covered by their own ecosystem's review."
    - id: AC-06
      text: "The default outcome when AC-01 or AC-02 cannot be satisfied is to refrain from the change — wait for the version to age past the threshold, wait for the advisory to be resolved, or pin to an older version that does pass. Choosing an older satisfying version is preferred over installing a fresh version."
    - id: AC-07
      text: "The rule may be overridden only by an explicit, recorded developer authorization for the specific dependency and version. The override is recorded next to the change (commit message, task protocol, or a designated override-log file) and names: the package, the version, the AC being overridden, and the reason. Silent override — an agent installing a fresh version because it is needed — is forbidden."
    - id: AC-08
      text: "A dependency change that violates this requirement is never declared complete: violations trigger a revision cycle under the same five-cycle back-pressure protocol defined in REQ-PROC-046, with escalation to the user on irrecoverable failure."
    - id: AC-09
      text: "The active set of forbidden conditions, the advisory data sources consulted, the override path, and the location of the override log are documented in a single authoritative location consistent with this requirement — an agent (LLM or human) can determine, without asking, what is admissible and what is not."
---

# Dependency Supply-Chain Safety (LLM Back-Pressure Gates)

## Overview

This requirement defines what versions of external packages the AI agent — and any developer working with it — is **forbidden from introducing** into the repository. It governs the *intake* of dependencies, not their *use*: an admissible package may still be misused at the code level (that is REQ-PROC-052's domain), and a well-used package may still be inadmissible at the version level (this requirement's domain). The two failure modes are distinct.

Gates are enforced through the same back-pressure protocol as REQ-PROC-046 and REQ-PROC-052: an LLM cannot declare a dependency change complete while any forbidden version condition is present.

## Purpose

Supply-chain attacks on package ecosystems have shifted from a rare event to a recurring class of incident. Compromises of npm packages (`event-stream`, `ua-parser-js`, `coa`, `colors.js`), PyPI packages (`ctx`, `phpass`, the 2024 `polyfill.io` chain reaction), and pub.dev packages have repeatedly succeeded by following the same pattern: an attacker publishes a malicious version to a legitimate-looking package, and ecosystem consumers — especially automated ones — pull the new version within hours. Days later the malicious version is identified, advisories are filed, and patched releases are published. The window between **publication** and **public detection** is the danger zone.

In a project where most code, configuration, and dependency-manifest edits are now produced by LLM agents, the default behavior of an LLM is to install the *latest* version it knows about — because that is what most public examples do. The LLM has no inherent sense that "yesterday's release" might be a poisoned release. Without a contractual gate, an LLM will eventually pull a compromised version, in good faith, into a repository that holds some of the most sensitive personal data a user produces.

This requirement turns the "wait it out" heuristic into a machine-checkable rule. The rule rests on two empirical observations:

1. **A version 7+ days old has had time to be examined by the ecosystem.** Compromises this old are typically already flagged by GitHub, OSV, pub.dev's advisory feed, or the package's own issue tracker.
2. **Age alone is not enough.** A version published last week can be confirmed compromised this week. The agent must also check the advisory databases at the time of the install — not just count days.

Combining the two rules eliminates both failure modes: brand-new compromises (caught by the age rule) and older compromises that have just been disclosed (caught by the advisory rule). Composing them is not redundant — each rule individually has known blind spots that only the other can cover.

The cost of the rule is bounded: developers and the AI may need to wait several days before adopting a new release. The cost of *not* having the rule is a foothold for an attacker inside an app that stores user mental-health data — a cost the app provider (PERSONA-015) refuses to accept.

## When This Requirement Applies

- Any change to `pubspec.yaml`, `pubspec.lock`, `pubspec_overrides.yaml`.
- Any change to Python dependency manifests under `scripts/`: `requirements*.txt`, `pyproject.toml`, `uv.lock`, `Pipfile`, `Pipfile.lock`.
- Any change to package manifests for tooling installed by automation skills (e.g. `package.json` / `package-lock.json` for npm packages used by skills, dart globals installed for the project).
- Before a task is marked complete (via `task-complete` or otherwise) when that task touched any of the files above.
- Before a commit is created on `develop` that contains a change to any of the files above.

## When This Requirement Does NOT Apply

- OS-level packages installed via `apt`, `brew`, `winget`, or equivalent (governed by their distro's review process and by `claude-install-os-tool`).
- Devcontainer features declared in `.devcontainer/devcontainer.json` (versions are controlled by the feature registry; addressed when the feature itself is updated).
- Generated lockfile entries that are byproducts of a manifest change already in scope — the manifest change is the entry point, and validating the manifest implicitly validates the resolved transitive set.
- Documentation references to package versions (e.g. mentioning a version in `doc/` or a task protocol). The rule governs introduction into the executable / shipped set, not prose.

## Behavior

### The Version-Intake Gates

Four gates are active. Each is binary (pass / fail) and detectable from a clean checkout via dependency inspection plus a check against external advisory data:

| Gate | Detection | Pass condition |
|---|---|---|
| **DG1 Minimum-age threshold** | for each newly-pinned or upgraded version in any in-scope manifest, query the registry's publication timestamp for that exact version | `now - published_at ≥ 7 days` for every such version |
| **DG2 Advisory clearance** | for each newly-pinned or upgraded version, query the relevant advisory database (GitHub Security Advisories, OSV.dev, pub.dev advisories, PyPA advisory DB, npm advisories) | zero unresolved advisories naming that exact version |
| **DG3 Pre-install evidence** | inspect the commit / task protocol / change record for an artifact naming version, publication date, and advisory-DB state at the time of the check | artifact present for every in-scope version change |
| **DG4 Composability** | a version that satisfies DG1 OR DG2 but not both | failure — both must independently pass |

The gate set is closed: a supply-chain version-intake property is either represented by one of these gates or by another active requirement. Adding or removing a gate is itself a change that must update this document.

### Override Path

The rule recognizes that emergencies happen — a critical bug fix or a security patch may itself be less than 7 days old. An override is admissible if and only if it is recorded next to the change with the following content:

- The package name and exact version.
- Which AC is being overridden (AC-01, AC-02, or both).
- The reason (the specific bug fix or security patch being applied, with a link to the advisory or issue).
- The agent / human who authorized the override.

The override is *not* a silent decision by an agent. An LLM agent that encounters a failing gate must escalate (under the back-pressure protocol of REQ-PROC-046) rather than self-authorize.

### The Back-Pressure Protocol

The same protocol as REQ-PROC-046 applies: per-change self-check, all gates re-run after each revision, five-cycle iteration bound, escalation on unresolved failure. This requirement does not redefine the protocol; it inherits it. A failure of DG1, DG2, DG3, or DG4 counts toward the same five-cycle budget as a code-quality or privacy gate failure on the same change.

### Scope Boundary: Where the Rule Lives

The rule lives at the **intake** edge — the moment a version pin appears in a manifest committed to the repository. It does not run continuously against the universe of installed dependencies; that would create perpetual instability as advisories are filed for older versions long after install. Once a version is committed and passed the gates at intake time, it remains admissible until the next deliberate change to that version. Re-evaluating already-committed versions is the job of REQ-PROC-061 (Dependency Lifecycle & Update Cadence), which defines the monthly batch review, event-based triggers, and per-release sweep that surface stale or vulnerable pinned versions.

## Examples

**Example 1: DG1 — the fresh release that waits a week**

The Dart team publishes `package:foo 2.5.0` on Monday. On Tuesday, an LLM agent working on an unrelated feature notices `pubspec.yaml` pins `foo: ^2.4.0` and would, by default, run `flutter pub upgrade` and pin `^2.5.0`. DG1 fails (publication is one day old). The correct action is not to upgrade — `foo 2.4.0` is still admissible and the task does not need `2.5.0`. If the task did need a feature only available in `2.5.0`, the change must wait until the following Monday or be escalated.

**Example 2: DG2 — the older version with a fresh advisory**

`package:bar 1.3.0` was published three weeks ago — DG1 passes comfortably. Yesterday, a security researcher disclosed a remote-code-execution vulnerability in `bar 1.3.0`'s YAML parser; the GitHub Security Advisory database now lists `bar < 1.3.1` as affected. DG2 fails. The correct action is to pin `bar 1.3.1` (assuming it itself satisfies DG1 — which it does, having been published two weeks ago when the advisory was first private). If `1.3.1` were brand-new, the agent would have to wait or escalate.

**Example 3: DG3 — the missing evidence**

An LLM agent updates `pubspec.yaml` to bump `package:baz` from `4.1.0` to `4.2.0`. The agent does not produce an artifact recording the publication date of `4.2.0` or the advisory-DB state. DG3 fails *even if DG1 and DG2 would have passed*. The rule requires evidence-of-check, not just absence-of-failure. The agent must redo the check and record the result.

**Example 4: DG4 — composability prevents partial reasoning**

An agent claims "this version is fine because it's old enough." Age alone is not the contract. The agent must also claim "and the advisory databases show no entries naming this version." Both claims, both at the moment of the check, are required.

**Example 5: Override — the legitimate exception**

A critical zero-day is announced in `package:qux`. The maintainer publishes `qux 5.0.1` six hours later. The project needs the patch. DG1 fails. The developer (not the agent) authorizes an override in the commit message:

> Override DG1 for `qux 5.0.1`: CVE-2026-XXXX (RCE in 5.0.0 and below) was disclosed and patched six hours ago. Waiting 7 days is not acceptable given confirmed in-the-wild exploitation. Advisory: https://github.com/advisories/GHSA-... Authorized by: Andreas Mayer.

The override is auditable. The next time an agent reads the history, it sees the authorized exception and does not propagate the same shortcut to unrelated upgrades.

## Developer Guidelines

> Constraints and invariants the final state must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **The default is to wait.** An admissible dependency change is one that satisfies all gates without an override. Overrides exist for genuine emergencies, not for convenience.
- **Old version > fresh version, when both work.** If the existing pinned version still satisfies the task's functional needs, do not upgrade. The cost of upgrading is the supply-chain risk; the benefit is rarely worth the risk.
- **Evidence is part of the change, not optional metadata.** A dependency bump without DG3 evidence is incomplete in the same way a code change without tests is incomplete.
- **The two checks compose, they do not substitute.** An agent that satisfies only DG1 has missed the class of compromise where the advisory landed yesterday. An agent that satisfies only DG2 has missed the class of compromise that has not been disclosed yet.
- **Gates inherit REQ-PROC-046's back-pressure mechanism.** This requirement does not duplicate the five-cycle protocol; failures here trigger the same revision loop.
- **The rule is about intake, not about already-installed code.** Once a version passed the gates at the moment of its commit, it remains admissible. A separate audit cadence handles long-tail advisory drift.

### Common Pitfalls

- **"Latest is best" reflex**: an LLM trained on public examples sees `flutter pub upgrade` paired with "always run this." The rule overrides that reflex — `upgrade` without a check is a gate failure.
- **"It's an existing dependency, not a new one"**: bumping the version is a new install of a new version. The gates apply to the version, not to the package's first appearance.
- **Treating absence of advisory as proof of safety**: GitHub Security Advisories lag publication. A version published three days ago with no advisory is still a DG1 failure. Advisory check and age check are not interchangeable.
- **Skipping the evidence artifact for "obviously safe" upgrades**: DG3 has no carve-out for obviousness. If the artifact is missing, the change is incomplete, regardless of how clean the version looks.
- **Confusing OS package managers with in-scope ecosystems**: `apt install python3-foo` is out of scope (governed by distro review); `uv add foo` inside a `scripts/` `pyproject.toml` is in scope. The boundary is whether the version pin lands in the repository.
- **Self-authorizing an override**: only a recorded developer authorization satisfies AC-07. An LLM agent encountering a gate failure must escalate via the back-pressure protocol, not write its own override.

## Related Requirements

- **REQ-PROC-046 (Code Quality Standard)** — source of the five-cycle back-pressure protocol that AC-08 inherits.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — sibling. Together with this requirement they form the full supply-chain contract for the project: REQ-PROC-052 governs what the *code* may do (no network I/O, no telemetry SDKs); this requirement governs what *versions of code* may enter the project in the first place. The two protect against different attack classes (intentional misuse vs. compromised intake).
- **REQ-PROC-038 (CodeGraph integration)** and **REQ-PROC-011 (Roo Code deprecation)** — sibling per-tool entries under `ai_tool_management/`. This requirement is the cross-cutting policy that applies whenever any of those tools triggers a dependency install.
- **REQ-PROC-060 (Dependency Admission & Package Health)** — sibling. Governs whether a package should exist in the project at all (justification gate, health checklist) and what package-level properties every dependency must satisfy. This requirement governs which *version* of an already-admitted package may enter; REQ-PROC-060 governs the *admission decision* that precedes the version choice.
- **REQ-PROC-061 (Dependency Lifecycle & Update Cadence)** — sibling. Governs *when* existing dependencies are re-evaluated and how updates/replacements are carried out. This requirement's scope boundary explicitly defers cadence to REQ-PROC-061.
- **Future: enforcement task and any check-script created by it.** A `scripts/quality/check_dependency_freshness.*` (or equivalent) and a pre-commit / pre-tool integration are out of scope for this requirement; they are the subject of the exploration task created alongside this requirement.

## References

- `requirements_user_needs/personas/app_provider/persona.md` — source of the trust-by-absence commitments that this requirement defends at the dependency-intake edge.
- `requirements_user_needs/personas/system_maintenance/persona.md` — source of the data-sensitivity constraints; a supply-chain compromise inside a mental-health journal app is a maximum-severity outcome.
- `pubspec.yaml`, `pubspec.lock` — the primary in-scope manifests for Dart / Flutter dependencies.
- `scripts/**/pyproject.toml`, `scripts/**/requirements*.txt`, `scripts/**/uv.lock` — the in-scope Python manifests.
- `CLAUDE.md` — operational checklist; back-pressure protocol referenced for AC-08.
- Industry context (illustrative, non-normative): GitHub Security Advisories (`https://github.com/advisories`), OSV.dev (`https://osv.dev`), pub.dev advisories, PyPA Advisory Database, npm advisory feed — the advisory sources that DG2 consults.
