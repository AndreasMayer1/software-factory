# Discovery Synthesis v2 — Dependency Lifecycle + Admission Decomposition

**Task**: TASK-PROC-056-02
**Date**: 2026-05-26
**Session**: 68bd6062-1605-49af-9e68-6e6895801c07 (automated, Opus)
**Supersedes**: `2026-05-26_01_synthesis_decomposition.md` (v1, pre-web-research)
**Web research**: `2026-05-26_02_web_research_findings.md` — completed successfully

---

## 0. What changed between v1 and v2

The web research validated the two-requirement split and refined several sub-decisions:

- **Bitwarden** literally separates "who approves new deps" (team ownership gate) from "how updates flow" (Renovate with 7-day minimumReleaseAge + biweekly batching). This maps directly to R-A / R-B.
- **The Dart ecosystem's supply-chain tooling is significantly weaker than npm/PyPI** — no Socket.dev coverage, no maintainer-change alerting, no `dart pub audit` command. R-A's health criteria must be framed as a *manual admission checklist* (agent checks before proposing), not as an automated enforcement gate. This is a structural distinction from REQ-PROC-056 (whose gates ARE mechanically checkable).
- **The 7-day cooldown blocks 80% of documented supply-chain attacks** — directly validates REQ-PROC-056's threshold.
- **The zero-network-IO architecture (SP1) provides defense-in-depth** — even a compromised dependency cannot exfiltrate data at runtime. This makes the capability-surface question (D3) less urgent than v1 suggested.
- **Monthly batched updates** is the converging recommendation from OWASP, OpenSSF, and community best practice for solo/small teams — refining D2 to include a monthly cadence (not just per-release + event-based).
- **No AI-agent governance framework treats "add new dep" as a distinct permission class** — this project would be innovating here. Only Codex has a hard sandbox; everything else uses soft rules. Our CLAUDE.md + requirement-based enforcement is state-of-the-art for this tooling generation.

No structural change to the decomposition itself. The two-requirement split stands, reinforced.

---

## 1. Recommended decomposition (unchanged from v1, refined in detail)

| # | Working title | One-line scope | Enforcement model |
|---|---|---|---|
| **R-A** | **Dependency Admission & Package Health** | "*Should this package exist in our project, and is it healthy enough to stay?*" | **Manual checklist** — the agent evaluates criteria before proposing; no automated gate script (Dart tooling doesn't support it). Human pre-authorization for new deps. |
| **R-B** | **Dependency Lifecycle & Update Cadence** | "*When do we revisit existing dependencies, what triggers action, and how do we carry out an update or replacement safely?*" | **Cadence-triggered workflow** — monthly batch review + event triggers. Automated signals (`pub outdated`, `osv-scanner`, analyzer deprecations) feed the agent's decision; REQ-PROC-056 gates enforce version safety. |
| **mod** | **REQ-PROC-056** (existing) | One-paragraph cross-reference to R-B in Scope Boundary; R-A/R-B in Related Requirements. No gate changes. | — |

---

## 2. R-A detail — Dependency Admission & Package Health

### What it covers

1. **Justification gate for new top-level dependencies**: When is it acceptable to add a new dep vs. write the functionality inline? Threshold: domain complexity (always pull crypto), LoC saved (only if significant), whether it introduces a new capability surface the project doesn't already use.

2. **Package-health admission checklist** (evaluated manually by the agent at proposal time):
   - **Verified publisher** on pub.dev (strong signal of identity; not proof of safety)
   - **Pub points ≥ 100** (basic quality bar from pana)
   - **Active maintenance**: commit activity in last 90 days OR stable package with clear "done" signal (version 1.x+ with minimal issues)
   - **Minimum package age**: must exist on pub.dev for ≥ 6 months (complements REQ-PROC-056's 7-day *version* age with a *package-level* age signal for brand-new packages)
   - **Transitive dependency footprint**: prefer packages with ≤ 5 direct dependencies themselves; flag packages that pull large transitive trees
   - **License compatibility**: must be permissible for closed-source distribution (MIT, BSD, Apache 2.0 — no GPL/LGPL for runtime deps)
   - **No disqualifying capability surface**: the package must not introduce capabilities the project rejects at the architecture level (network I/O, telemetry — already covered by REQ-PROC-052 SP1/SP2, but the admission check catches it *before* the code lands in `lib/`)

3. **Ongoing health re-evaluation** (same criteria, applied during R-B's lifecycle sweep): a package that *was* healthy at admission can become unhealthy (maintainer abandonment, license change, discontinued flag on pub.dev). The criteria are the same; the trigger is different (R-B's cadence).

4. **LLM-autonomy boundary** for admission: see §4 autonomy table.

### What it does NOT cover (boundary)

- *Which version* of an admitted package may enter → REQ-PROC-056 (DG1–DG4)
- *What the code does* with the package → REQ-PROC-052 (SP1–SP6)
- *When* to re-evaluate existing deps → R-B (cadence triggers)
- OS-level packages → `claude-install-os-tool` (unchanged)

### Why "manual checklist" not "automated gate"

The Dart/pub.dev ecosystem lacks tooling for automated package-health enforcement:
- No Socket.dev coverage (no maintainer-change alerts, no capability analysis)
- No Snyk Advisor for pub packages
- No `dart pub audit` command
- deps.dev has metadata but no behavioral analysis

The practical enforcement model is: the agent checks the criteria as part of the admission workflow (the same way it currently checks REQ-PROC-056 by inspecting pub.dev dates manually) and records the evidence in DG3-style artifacts. Automated tooling (`osv-scanner`, pub.dev advisory warnings) catches a subset (known CVEs) but not the full health surface. **This is an honest acknowledgement of ecosystem limitations, not a policy weakness** — the gate is real, the enforcement is agent-driven-with-evidence rather than script-driven.

---

## 3. R-B detail — Dependency Lifecycle & Update Cadence

### What it covers

1. **Trigger model** (layered, multiple signals):
   - **Monthly batch review**: Run `flutter pub outdated` once per month (calendar cadence). Evaluate each available upgrade against REQ-PROC-056 gates. Propose a grouped update PR/task.
   - **Event-based immediate triggers**: (a) security advisory disclosed for a pinned version (osv-scanner / pub.dev warning); (b) `dart fix --apply` or `flutter analyze` surfaces a deprecation warning; (c) build failure caused by dependency incompatibility; (d) a release-candidate preparation explicitly sweeps deps.
   - **Per-release-candidate sweep**: Before any release, a mandatory `pub outdated` + `osv-scanner` run ensures no known-vulnerable version ships. This is a *gate* on the release workflow (REQ-PROC-036 integration point).
   - **NOT included**: aggressive time-based auto-upgrade (daily/weekly `pub upgrade` runs). This would fight REQ-PROC-056's "default is to wait" and create unnecessary churn.

2. **Deprecation-signal aggregation and urgency classification**:
   - **Immediate action** (within current task/session): security advisory with known-exploited status; build failure.
   - **Next monthly batch** (normal priority): `dart fix` deprecation warnings; package flagged as "discontinued" on pub.dev; `pub outdated` showing available minor/patch upgrades.
   - **Quarterly evaluation** (deferred): packages with no release in >12 months (potential abandonment); major-version upgrades available; packages where the agent notices the maintained fork has diverged.
   - **Acceptable to defer indefinitely**: deprecated APIs that still function at the pinned version with no security implication; packages that work but have a "better alternative" available (cosmetic improvement, not a risk).

3. **Replacement workflow** (when a package must be swapped):
   - Apply R-A's admission checklist to each candidate replacement.
   - The replacement is a new admission — the same human-pre-authorization gate applies (it's adding a new dep).
   - The migration is scoped as a dedicated task (not buried inside another task's work).
   - REQ-PROC-056 gates apply to the new version pin.

4. **Regression-confirmation contract for updates**:
   - Patch/minor bumps: existing quality gates (REQ-PROC-046 G1–G8, REQ-PROC-002 TQ1–TQ4, REQ-PROC-052 SP1–SP6) are **sufficient**. No additional testing needed beyond the standard back-pressure protocol.
   - Major bumps: standard gates **plus** the agent must read the package's CHANGELOG/migration guide (REQ-PROC-053 lookup) and verify any API changes in our call sites. Integration tests run if the package touches a critical path.
   - Package replacement: same as major bump, plus a dedicated test pass exercising the replaced functionality.

5. **LLM-autonomy boundary** for lifecycle: see §4 autonomy table.

### What it does NOT cover (boundary)

- *Whether* a package should exist at all → R-A (admission/health)
- *Which version* is safe to pin → REQ-PROC-056 (DG1–DG4)
- *How* the agent runs a quality-gate pass after the update → REQ-PROC-046 (back-pressure protocol)
- Release-workflow gating mechanics → REQ-PROC-036

---

## 4. LLM-autonomy taxonomy (embedded in R-A and R-B)

### R-A autonomy boundary (admission & health)

| Operation | Autonomy level | Rationale |
|---|---|---|
| **Add a new top-level runtime dependency** | Human pre-authorization required | Every new dep is an irreversible expansion of the attack surface and maintenance burden. No AI agent framework in the industry auto-approves this. Bitwarden requires team sign-off; this project requires developer sign-off. |
| **Add a new dev_dependency** (test tooling, build runner, analysis) | Human pre-authorization required | Same principle — dev deps also run code on the developer's machine. Lower risk than runtime deps but still requires explicit admission. |
| **Evaluate health of an existing dep** (read-only: check pub.dev, deps.dev) | Fully autonomous | No side effects; the agent is gathering information. |
| **Block/refuse** a dep that fails a health criterion | Autonomous (refusal is the safe default) | The agent surfaces the failure; the developer can override. |
| **Override a failed health criterion** to admit anyway | Forbidden without recorded developer authorization | Reuses REQ-PROC-056 AC-07 pattern. |

### R-B autonomy boundary (lifecycle)

| Operation | Autonomy level | Rationale |
|---|---|---|
| **Patch-level bump** of existing dep, REQ-PROC-056 + quality gates pass | Autonomous with recorded evidence | Low risk; the gates catch breakage; the 7-day age rule catches fresh compromises. Bitwarden auto-merges patch Renovate PRs after CI passes. |
| **Minor-level bump**, gates green, no API breakage detected | Autonomous with recorded evidence | Same risk profile as patch if the semver contract holds and no deprecated API is used. |
| **Major-version bump** | Human pre-authorization required | Semver-major signals breaking changes. Agent proposes; developer approves. |
| **Package replacement** (swap `foo`→`bar`) | Human pre-authorization required | It's a new admission (R-A gate) plus removal of an existing dep. Two decisions, both gated. |
| **Defer a deprecation past a release** | Autonomous with recorded rationale | The agent documents why it's deferred and files it for the next monthly batch. No escalation needed unless it causes a gate failure. |
| **Self-authorize a REQ-PROC-056 override** | Forbidden | Already forbidden by REQ-PROC-056 AC-07. |
| **Run `flutter pub upgrade` without checking** | Forbidden | This is the "latest is best" reflex that REQ-PROC-056 exists to prevent. |

---

## 5. Overlap audit (updated from v1)

| Existing requirement | Overlap / gap | Verdict |
|---|---|---|
| **REQ-PROC-056** | Version-intake safety (DG1–DG4). The 7-day threshold validated by research (blocks 80% of attacks). | **Owns version safety. No change needed** to gates. Only the cross-reference `mod`. |
| **REQ-PROC-052 SP1/SP2** | Capability-surface check on **code in `lib/`** (network/telemetry). Does NOT check package capabilities pre-admission. | **R-A's capability-surface admission criterion is additive, not duplicative.** It catches the risk *before* code lands. However, the zero-network-IO architecture means even a compromised dep cannot exfiltrate at runtime — defense-in-depth makes this advisory, not critical. |
| **REQ-PROC-046 G1** | Catches breakage on update + surfaces deprecation warnings. | **R-B consumes these signals** as triggers. No overlap. |
| **REQ-PROC-053** (doc lookup) | Requires a lookup when introducing/modifying a dep. | **Complementary**: REQ-PROC-053 says "look up the docs"; R-A says "should this dep exist at all." Different questions. |
| **Dart ecosystem tooling** | `osv-scanner` is the strongest automated tool available; no maintainer-change detection; no `dart pub audit`. | **Acknowledged limitation.** R-A uses manual checklist; R-B uses `pub outdated` + `osv-scanner` as signal sources. Automated enforcement tools are not available for the full health surface. |

---

## 6. What the research CHANGED vs. v1

| Topic | v1 position | v2 position (after research) |
|---|---|---|
| **D2 cadence** | Event-based + per-release sweep | **Event-based + monthly batch + per-release sweep** (monthly cadence is the converging standard recommendation; not having it means deps accumulate silently) |
| **D3 capability surface** | Hard gate on direct deps | **Advisory signal only** (the zero-network-IO architecture provides defense-in-depth; the Dart ecosystem can't enforce it mechanically anyway; the real risk is mitigated by SP1/SP2 at the code level) |
| **Health enforcement model** | Implied automated gates | **Explicit manual checklist** (Dart lacks the tooling for automated package-health gates; honest about this) |
| **Package age for NEW packages** | Not discussed | **≥ 6 months on pub.dev** (complements REQ-PROC-056's 7-day version age — a brand-new package published yesterday by an unknown author is higher risk than a version update to an established package) |
| **Verified publisher** | Not discussed | **Strong admission signal** (pub.dev's blue badge is the only Dart-native identity verification available) |
| **Overall confidence** | Internal analysis only | **Multiple converging external sources** validate the decomposition, cadence, and autonomy boundaries |

---

## 7. Decisions requiring user input (revised)

**If you agree with all recommended defaults, answer "approve all defaults."**

- **D1 — New-dependency autonomy.** Must every new top-level dependency (runtime AND dev) require recorded human pre-authorization?
  → **Recommend: YES for both runtime and dev dependencies.** (Universal among privacy-focused projects; no AI framework auto-approves this; the project innovates here by making the boundary explicit as a requirement.)

- **D2 — Update cadence model.** Which trigger layering?
  → **Recommend: event-based (advisory/deprecation/failure) + monthly batch review (`pub outdated` + `osv-scanner`) + per-release-candidate sweep.** (Converging recommendation from OWASP/OpenSSF/community best practice; monthly catches silent staleness; per-release prevents known-vulnerable versions from shipping.)

- **D3 — Capability-surface depth.** Hard gate or advisory signal?
  → **Recommend: advisory signal only at admission (not a blocking gate).** (Zero-network-IO architecture provides defense-in-depth; Dart tooling can't mechanically enforce it; SP1/SP2 catch it at the code level. The admission checklist flags it; the developer decides whether it's disqualifying case-by-case.)

- **D4 — Endorse the two-requirement split?**
  → **Recommend: YES.** (Bitwarden's published policy literally makes the same structural separation; research found no counter-evidence.)

- **D5 — Placement.** Two new sibling folders under `process/AI_rules/ai_tool_management/` (e.g. `dependency_admission_and_health/` and `dependency_lifecycle/`)?
  → **Recommend: YES.** (Keeps the intake/admission/lifecycle boundary visible at folder level.)

- **D6 — Proceed to authoring?** Web research is now complete. Do you want me to proceed to Phase 2 (author R-A, R-B, and REQ-PROC-056 mod via `requ-explore`)?
  → **Recommend: YES, proceed.**

---

## 8. Honest uncertainties / residual risks

- **Dart ecosystem gap is structural, not fixable by policy alone.** No tool will alert this project when a pub.dev package undergoes a maintainer transfer. The policy acknowledges this and relies on defense-in-depth (7-day version cooldown + zero-network-IO + manual health review at admission) rather than pretending automated detection exists.
- **Package-age threshold (6 months) is a heuristic.** Some legitimate new packages from verified publishers (dart.dev, google.dev) would fail this criterion. R-A should include an override path for verified-publisher packages younger than 6 months.
- **Monthly batch cadence requires a trigger mechanism.** How does the agent know it's "that time of month"? Options: (a) the automation orchestrator creates a recurring task; (b) the release-preparation checklist includes it; (c) it's part of a scheduled routine. This is an implementation detail for the task that follows R-B, not for R-B itself, but worth noting.
- **The "no one else does this" risk.** No published AI-agent governance framework treats dependency admission as a distinct permission boundary. This project would be innovating. The innovation is justified by the privacy sensitivity of the data, but it means there's no external prior art to validate the exact boundary placement. Bitwarden's human-approval gate is the closest analogue, and it's not AI-specific.
- **Attacker model residual.** Long-con social engineering (event-stream pattern) defeats both the 7-day cooldown and the admission checklist — the attacker waits months and the package looks healthy at every check. The zero-network-IO architecture is the load-bearing defense against this class (even if the dep is compromised, no data leaves the device). This is documented as a known residual, not a solvable gap.

---

## 9. Part-2 authoring plan (executes only after user approval)

If approved:
1. `requ-explore` → **R-A** (`dependency_admission_and_health/requirements.md`), `status: active`.
2. `requ-explore` → **R-B** (`dependency_lifecycle/requirements.md`), `status: active`.
3. `requ-explore` → **REQ-PROC-056 mod** (cross-reference additions only).

Each requirement embeds its autonomy table, references REQ-PROC-056 for version intake, REQ-PROC-052 for code-behaviour gates, and records the user's decisions on D1–D5 as end-state constraints.
