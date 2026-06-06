# Plan — TASK-PROC-066-04: Web Fixture Toolchain, doc/ Surface & Quality Gates

**Date**: 2026-06-05  
**Agent**: main session (Sonnet)  
**Task**: TASK-PROC-066-04

---

## Gate Analysis

This task hits two mandatory human-authorization gates immediately:

1. **Framework choice** — React vs Angular must be confirmed per Notes + goal body.
   - Source: TASK-PROC-066-03 synthesis recommends **React** (largest codegen corpus,
     lighter scaffold). The developer has not yet confirmed this (it is Decision #4 of the
     pending question in `automation/pending_feedback/TASK-PROC-066-03/question.md`).

2. **REQ-PROC-060 dependency-admission gate** — standing up any web toolchain is a large
   new top-level dependency addition. The task body explicitly mandates this gate.
   - Scope note: REQ-PROC-060 formally covers "npm manifests used by automation skills".
     The web fixture is a standalone mini-project the factory runs *against*, not an
     automation skill itself. The gate's application here is by task-author mandate.

Neither gate can be bypassed autonomously. A pending_feedback question is written for
developer authorization before any scaffolding proceeds.

---

## Proposed React Stack (pending confirmation)

### Why React over Angular
- Largest LLM training corpus → cheapest codegen per loop (the fixture's whole point)
- Lighter scaffold for a small offline app (no heavy DI/module system)
- Vite build → fast HMR, minimal config overhead
- Source: 066-03 synthesis §5

### Proposed packages

#### Runtime deps
| Package | Latest | License | Age | Notes |
|---------|--------|---------|-----|-------|
| `react` | 19.2.7 | MIT | 2011-10-26 (14+ yrs) | AC-02a/b: pass |
| `react-dom` | 19.x | MIT | 2014-05-06 (12+ yrs) | AC-02a/b: pass |

#### Dev deps
| Package | Latest | License | Age | Dep count | Notes |
|---------|--------|---------|-----|-----------|-------|
| `typescript` | 6.0.3 | Apache-2.0 | 2012-10-01 (13+ yrs) | - | AC-02a/b: pass |
| `vite` | 8.0.16 | MIT | 2020-04-21 (5+ yrs) | 5 | AC-02a/b/d: pass (≤5 deps exactly) |
| `@vitejs/plugin-react` | latest | MIT | 2021-09-20 (4+ yrs) | 1 | AC-02a/b/d: pass |
| `vitest` | latest | MIT | 2021-12-03 (4+ yrs) | 20 | **AC-02d: marginal** (20 deps; criterion designed for pub.dev; noted below) |
| `@testing-library/react` | latest | MIT | 2019-05-30 (7+ yrs) | 1 | AC-02a/b/d: pass |
| `@testing-library/jest-dom` | latest | MIT | 2019-07-08 (6+ yrs) | - | AC-02a/b: pass |
| `eslint` | latest | MIT | 2013-07-04 (12+ yrs) | - | AC-02a/b: pass |
| `@typescript-eslint/eslint-plugin` | latest | MIT | - | - | Part of typescript-eslint monorepo |
| `@typescript-eslint/parser` | latest | MIT | - | - | Part of typescript-eslint monorepo |

**vitest dep-count note**: AC-02d (≤5 direct deps) was designed for pub.dev Dart packages.
npm packages routinely carry more transitive deps; 20 is not unusual for a test framework.
Developer confirmation covers this criterion as a scope clarification.

#### Capability-surface flags (AC-04)
- None of the above packages introduce network I/O (vitest is a local test runner).
- No telemetry/analytics packages.
- No platform channels (this is a web project, not Flutter).
→ No capability-surface concerns.

---

## Proposed `doc/` Guideline Surface

Once the framework is confirmed, the doc/ surface will mirror the Flutter structure:

```
doc/
  web/
    architecture/
      architecture.md      (component structure, folder layout, layer boundaries)
    testing/
      testing.md           (unit + component test standards, coverage expectations)
    presentation/
      component_standards.md (naming, prop patterns, styling approach)
```

Content will be adapted from the Flutter doc/ guidelines but scoped to React conventions.

---

## Proposed Quality Gates

Analogous to the Dart gates:
- **G1-web**: `eslint` + `tsc --noEmit` (lint + type check)
- **G2-web**: `vitest run` (unit/component tests)
- **G3-web**: `vite build` (build succeeds)

Wired via a new script `scripts/quality/check_web_gates.sh` (will go through `claude-write-script`).

---

## Execution Plan (post-authorization)

1. **Framework confirmed + deps authorized** → Create fixture scaffold
   - `mkdir fixture_app/ && cd fixture_app && npm create vite@latest . -- --template react-ts`
   - Install deps
   - Remove default boilerplate, verify empty-scaffold builds
2. **Quality gates** → Write `scripts/quality/check_web_gates.sh` via `claude-write-script`
3. **doc/ surface** → Write 3 guideline files under `doc/web/`
4. **Verify gates green** → Run gates on the empty scaffold
5. **Commit via task-complete**

---

## Blocker

Session terminates here. Developer must answer the pending_feedback question before
scaffolding can begin.
