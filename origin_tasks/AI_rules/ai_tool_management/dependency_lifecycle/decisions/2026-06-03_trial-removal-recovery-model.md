# ADR: Trial-removal recovery model for dependency retirement

**Date**: 2026-06-03 · **Status**: accepted · **Requirement**: REQ-PROC-061 (AC-13, AC-14, AC-15)
**Source task**: TASK-PROC-061-18 (`tasks/2026-06-03_explore_harden-dependency-usage-check/`)

## Context

The monthly usage-check (`scripts/release/check_dependency_usage.py`) classifies a
`pubspec.yaml` dependency as a *removal candidate* when no Dart `import` references it. This
produces structural false positives (analyzer/lint plugins referenced only in
`analysis_options.yaml`; native plugins with no Dart import) and, until now, offered no
durable recovery: a developer "keep" decision was not persisted, so the same false
positives resurfaced every cycle. Separately, confirming that a removal is *safe* fell on
the developer to verify by code archaeology.

Two structural facts drive the decision:

1. **Removal candidates are un-imported by definition.** Removing one therefore usually
   breaks nothing the analyzer or `flutter test` can observe — a green run is *necessary
   but not sufficient*. The oracle is weakest precisely for the population it judges.
2. **Native/C++ deps are only validated per-platform by CI.** Today only Windows is fully
   covered (`build_windows.yml`); Linux-desktop, macOS, iOS, and Android-device are not.
   Plugin target platforms are enumerated in `.flutter-plugins-dependencies`.

## Decision

**1. Broaden evidence classes (AC-13).** Beyond Dart imports, the usage-check recognizes
*config-referenced* (analyzer/lint/ruleset entries in `analysis_options.yaml` — retained)
and *native-declared* (plugin declared in `.flutter-plugins-dependencies` — surfaced for
manual call-site verification, never auto-retained, because registrant presence is
circular evidence). Output is tiered: *likely-dead* vs *needs-manual-review* vs *retained*.

**2. Durable retention registry (AC-14).** A keep decision is persisted in a data-owned
registry (package, class, reason, date) that the script reads, so acknowledged false
positives leave the active candidate list permanently. The registry accepts *all*
retention classes — unlike the `INDIRECT_REQUIREMENTS` allowlist, which only admits
packages whose consuming dependency can be named. Stale entries (package gone) are
reported.

**3. Empirical trial-removal with allow-with-residual-risk gating (AC-15).** An authorized
removal is confirmed by experiment on an isolated branch: analyzer + tests + every
CI-covered platform's build-plus-smoke lane. Red → revert and write the failing signal
into the registry as keep-justification. **Gating policy chosen: allow-with-residual-risk**
— removal may be confirmed once all *CI-covered* platforms pass, with uncovered platforms
recorded as accepted residual risk in the proposal and decision task (developer
acknowledges). Config-referenced and code-generation packages are exempt (their removal
produces no observable failure).

### Alternatives considered for the gating policy

- **Strict CI-coverage gate** (defer any package whose target platforms aren't all
  CI-covered) — safest, but today defers most desktop-native deps indefinitely and stalls
  cleanup until Apple/Linux lanes exist. *Rejected* as too slow for a solo maintainer.
- **ADR-only, no AC** — capture as guidance without binding it. *Rejected*: the recovery
  guarantee is worth making verifiable now.
- **Chosen: allow-with-residual-risk** — keeps cleanup moving, makes the risk explicit and
  developer-acknowledged rather than hidden.

## Consequences

- A failed trial-removal *auto-generates* the keep-justification the allowlist rule
  demands — the two recovery paths compose.
- **Accepted residual risk**: removal confirmed only on covered platforms can ship a break
  to an uncovered platform (macOS/iOS/Linux-desktop/Android-device today). This is recorded
  per removal, not eliminated. It shrinks automatically as CI lanes are added — AC-15 keys
  off `.flutter-plugins-dependencies` coverage, so new lanes tighten the gate without a
  requirement change.
- Trial-removal must run on an isolated branch/worktree (never `develop`); batch
  confirmable candidates to amortize CI, split/bisect on red.
- `doc/process/dependency_lifecycle.md` must be updated to reflect AC-13/14/15 (AC-10's
  single-authoritative-location contract) — tracked as an implementation task.

## Implementation decomposition

Carried in `tasks/2026-06-03_explore_harden-dependency-usage-check/plans_and_protocols/2026-06-03_01_design.md` §6.
Tasks are derived from this requirement via `task-derive-from-requ`.
