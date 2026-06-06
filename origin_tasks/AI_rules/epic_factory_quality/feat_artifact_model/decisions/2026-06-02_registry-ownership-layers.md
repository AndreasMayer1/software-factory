# Decision: ownership-layer split for the artifact registry

Date: 2026-06-02
Context: TASK-PROC-044-02-03 (developer ratification of `devcontainer` / `pubspec` tokens)
Status: **suggestion accepted in principle; full reclassification deferred to factory extraction**

## Problem

When the software factory is extracted into its own project (separate from this and
any concrete app), the artifact vocabulary must split cleanly. The developer raised two
constraints while ratifying new tokens:

1. The **dev container** is separate from *both* the factory and the app — every
   developer working on the concrete app may use their own environment. It must not be
   bound to either.
2. **Source code is a factory artifact** — producing source is the factory's whole
   purpose — but it is *technology-agnostic*. A **`pubspec`** (Flutter/Dart package
   manifest) is *not* a factory artifact: it is project/technology-specific. In the
   target architecture there is a technology-agnostic **factory core** plus a
   **plugin per technology** (e.g. a Flutter plugin), and tech-specific artifacts like
   `pubspec` live in the plugin.

## Decision — three ownership layers (orthogonal to content category)

The registry's existing `_categories` axis groups by *content domain*
(task-workspace, requirements, doc, automation, …). Layering adds an **orthogonal
ownership axis** that answers "who ships this artifact once the factory is its own
product?":

| Layer | Owner | Examples (today's tokens) |
|---|---|---|
| **L1 — factory core** (technology-agnostic) | the extracted factory | task-workspace, requirements, user-needs, doc, factory-skills, automation, factory-runtime, market-research, scripts, **and the generic `source` notion** |
| **L2 — technology plugin** (Flutter today; swappable) | a per-technology plugin | `pubspec` (`tech-stack`), and the Dart-specific shape of `token-source`/`token-dart`, `test`, `integration-test` |
| **L3 — developer environment** (per-developer, outside both) | neither factory nor app | `devcontainer` (`environment`) |

## What was implemented now (minimal, forward-compatible)

To resolve the 10 live violations without a premature mass-reclassification, two new
content categories were added to `.factory/registry/artifacts.yaml`, each named to
foreshadow its ownership layer:

- `environment` (L3): token `devcontainer`.
- `tech-stack` (L2): token `pubspec`.

Existing tokens were left in their current categories.

## Deferred to factory extraction (NOT done here)

- Tagging every category/token with an explicit `layer: core|plugin|environment` field
  (or splitting `source-code` into a core `source` vs a Flutter-plugin set).
- Moving `token-source`/`token-dart` and the Dart-specific test tokens into the L2
  plugin set.
- Reworking the skills/agents that currently hard-code Flutter assumptions — the
  developer explicitly flagged that extraction "will require reworking some skills and
  some artifacts" because the two are currently intertwined.

The `environment` and `tech-stack` categories give the extraction a seam to pull on:
anything outside L1 already sits in a dedicated category rather than being mixed into
the factory-core vocabulary.
