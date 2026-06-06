# Discovery Synthesis — Dependency Lifecycle + Admission Decomposition

**Task**: TASK-PROC-056-02
**Date**: 2026-05-26
**Session**: e6e07dc5-df69-4fa1-8db1-d96a5e27098b (automated, Opus)
**Phase**: 1 (Discovery synthesis) — Part 1 deliverable. Authoring (Part 2) is gated on user approval of the decomposition below.

---

## 1. What this synthesis concludes (the headline)

The assistant's first-pass **four-requirement** decomposition is **rejected in favour of a two-requirement split**, plus a small **modification to REQ-PROC-056**. The reasoning, the rejected alternatives, and the open user-decisions are below.

**Recommended decomposition:**

| # | Working title | One-line scope | Boundary vs. siblings |
|---|---|---|---|
| **R-A** | **Dependency Admission & Package Health** | "*Should this package exist in our project, and is it healthy enough to stay?*" — the justification gate for adding a new top-level dependency, and the package-level health properties (maintainer status, license, capability surface, abandonment) that are evaluated both at admission and during ongoing re-evaluation. | Governs **package properties** (the package as a unit). REQ-PROC-052 governs **code behaviour** (what `lib/` does). REQ-PROC-056 governs **which version** of an already-admitted package may enter. |
| **R-B** | **Dependency Lifecycle & Update Cadence** | "*When do we revisit existing dependencies, what triggers action, and how do we carry out an update or replacement safely?*" — the trigger/cadence model, deprecation-signal aggregation and urgency classification, the replacement workflow, and the regression-confirmation contract for updates. | Governs **when version changes happen and how the work is run**. REQ-PROC-056 governs the **intake gates any such change must pass**. R-A supplies the **candidate-evaluation criteria** that a replacement must satisfy. |
| **mod** | **REQ-PROC-056** (existing) | One-paragraph modification only: the Scope-Boundary sentence "*Re-evaluating already-committed versions is the job of a separate audit cadence (out of scope for this requirement)*" gains a forward cross-reference to R-B; the "Future: enforcement task" Related-Requirements bullet gains R-A/R-B. No gate changes. | — |

The **LLM-autonomy taxonomy** is **embedded per-requirement** (a small table in each of R-A and R-B), **not** spun out as a third shared requirement. Rationale in §4.

---

## 2. The decision axes (how the problem space actually factors)

Stripping the user's questions and the seeds down to their decision axes yields five candidate concerns:

- **AX1 — Admission**: "Should this package exist at all?" (justification: write-it-yourself vs. pull a dep)
- **AX2 — Version intake**: "Is *this version* safe to introduce?" → **already fully owned by REQ-PROC-056 (DG1–DG4)**. Applies identically to new deps and upgrades.
- **AX3 — Cadence/trigger**: "When do we revisit existing deps?" (time / event / opportunistic / manual)
- **AX4 — Package health**: "What properties beyond version must a package satisfy?" (maintainer, license, capability surface, abandonment)
- **AX5 — Replacement**: "When a package must be swapped, how do we choose and migrate?"

The key structural observations that drive the split:

1. **AX2 is already done.** REQ-PROC-056 cleanly owns version intake and explicitly applies symmetrically to new and upgraded deps. Nothing new is needed here except a cross-reference (the `mod`).

2. **AX1 and AX4 are the same question at two points in time.** The signals you check to decide "should we *add* this package" (license, maintainer health, capability surface, abandonment) are *identical* to the signals you check to decide "is this package still acceptable to *keep*." Splitting them into the first-pass's separate requirements #3 (admission) and #4 (package-level safety) forces an agent to read two files to evaluate one package and duplicates the criteria. **They belong together → R-A.**

3. **AX3 and AX5 are both "lifecycle events on an existing dep."** A deprecation/abandonment signal (AX5 trigger) is one kind of cadence trigger (AX3); the replacement that follows reuses R-A's candidate criteria. The first-pass split #1 (update cadence) and #2 (deprecation/replacement) share the same trigger machinery and the same "how do we run the work safely" question. **They belong together → R-B.** R-B's hardest case (replacement) *borrows* R-A's criteria rather than redefining them.

4. **AX3+AX5 are genuinely independent of AX1+AX4.** You can change the *cadence* (per-release → monthly) without touching the *health criteria*, and vice-versa. An agent adding a brand-new dep needs R-A but not R-B; an agent running a periodic refresh needs R-B + REQ-PROC-056 but not R-A's justification gate (existing deps already passed it). **This independence is what justifies two requirements rather than one.**

---

## 3. Rejected alternatives (and why)

### Rejected: the first-pass FOUR-way split
*(1 update-cadence, 2 deprecation/replacement, 3 new-dep-admission, 4 package-level-safety)*

- **Fails the point-of-decision reading test.** Adding one new package would force the agent to consult REQ-PROC-056 **+ #3 + #4** = three files, every time. Evaluating a replacement would force #2 + #4 + REQ-PROC-056 = three files. The split optimises for conceptual tidiness on paper and pessimises for the agent that actually meets the seams (goal.md's explicit warning: "*a four-requirement split that forces an agent to consult three files before adding a single dependency may fail*").
- **Duplicates the health criteria.** #4's criteria (maintainer, license, capability, abandonment) are needed by #3 (admission) and by #2 (replacement selection). Three requirements would each have to reference or restate them.
- **Cuts on a temporal seam that doesn't hold.** #1 (cadence) and #2 (deprecation) are both "lifecycle triggers"; separating them implies a deprecation isn't a cadence trigger, which is false.

### Rejected: ONE combined "Dependency Lifecycle Policy"
- Body would exceed ~200 lines with a large AC set; heavy for an LLM to load when a task only touches one aspect.
- Conflates two independently-evolving axes (when-to-check vs. what-makes-a-package-acceptable). A cadence change would dirty the health section and vice-versa.
- Most tasks touch only one half; forcing the whole file is context tax (cf. REQ-PROC-053's anti-reflex principle and the project's context-window rule).

### Rejected: FIVE-way (split health into license vs. capability)
- Premature for a one-developer, single-app-target project. License compatibility and capability surface are evaluated *together* as part of one "is this package acceptable" judgement. No evidence yet that they evolve independently. Can be split later if a licensing-compliance surface grows (deferred, not foreclosed).

### Rejected: autonomy taxonomy as its own (third/sixth) requirement
- See §4 — embedding wins.

### Rejected: by-stakeholder cut (what LLM owns / what needs human / what's forbidden)
- This is a *cross-cutting attribute* of every dependency operation, not a standalone requirement. It is exactly what the embedded autonomy table in each of R-A/R-B expresses. A separate "who may do what" requirement would have no home for the *criteria* the decisions operate on.

---

## 4. The LLM-autonomy taxonomy (embedded, not separate)

Recommendation: **embed a small autonomy table in each of R-A and R-B.** Reasons: (a) the boundaries differ by requirement (adding a dep vs. updating one), so a single shared table would still need two sections; (b) a shared third file adds a reading hop to every dependency decision; (c) the tables are small enough that there is no real duplication. REQ-PROC-056 AC-07's override mechanism (recorded developer authorization) is **reused** by both — neither redefines it.

**Proposed R-A autonomy boundary (admission & health):**

| Operation | Autonomy level |
|---|---|
| Add a brand-new **top-level** dependency | **Human pre-authorization required** (recommended — see Decision D1) |
| Evaluate health of an existing dep during a sweep, produce a report | Fully autonomous (read-only) |
| **Block/refuse** a dep that fails a mechanical health gate (e.g. disqualifying license) | Autonomous (the refusal is the safe default) |
| Override a failed health gate to admit anyway | Forbidden without recorded developer authorization (reuses REQ-PROC-056 AC-07 pattern) |

**Proposed R-B autonomy boundary (lifecycle):**

| Operation | Autonomy level |
|---|---|
| Patch-level bump of an existing dep that passes REQ-PROC-056 gates + all quality gates | Autonomous with recorded evidence |
| Minor-level bump, gates green, no API breakage | Autonomous with recorded evidence |
| Major-version bump (semver-major) | **Human pre-authorization required** |
| Package replacement (swap `foo`→`bar`) | **Human pre-authorization required** (it is an AX1 admission of `bar`) |
| Ignore/defer a surfaced deprecation past a release | Autonomous with recorded rationale; escalate if it blocks a gate |
| Self-authorize a REQ-PROC-056 override | Forbidden (already forbidden by REQ-PROC-056 AC-07) |

---

## 5. Overlap audit — "we already have it" (seed S10)

| Existing requirement | Overlap with the gap | Verdict |
|---|---|---|
| **REQ-PROC-056** (DG1–DG4) | Version-intake safety (AX2). | **Owns AX2.** Needs only the `mod` cross-reference; the new reqs do not re-specify version gates. |
| **REQ-PROC-052** SP1/SP2 | Capability surface (network/telemetry) — but checks **`lib/` code behaviour**, not **package capability**. A dep that *transitively pulls* `dart:io` without our code calling it is **not** caught by SP1 (which greps `lib/`). | **Partial; a real gap remains.** R-A's capability-surface health signal closes the package-property gap. R-A explicitly defers code-behaviour enforcement to REQ-PROC-052. |
| **REQ-PROC-046** G1 (`dart fix --apply`, analyzer) | Surfaces deprecation warnings; catches breakage on any change. | Catches *breakage* and *surfaces* deprecations, but says nothing about *when* to act or *how to remediate/replace*. R-B consumes these signals; no overlap to remove. |
| **REQ-PROC-053** (external doc lookup) | AC-02 active-signal list already says a lookup is required "when about to introduce a new dependency or modify the pinned version." | **Adjacent, not overlapping.** REQ-PROC-053 governs *consult the docs*; it does **not** govern *should the dep exist* or *which package*. R-A/R-B reference it as the lookup channel. |
| **REQ-PROC-036 / 034** (release workflow / packages) | Per-release activities; package = unit of *deliverable work*, not *dependency*. | No overlap. R-B may *attach* a cadence trigger to the release workflow but does not duplicate it. |
| **REQ-PROC-054** (dev env) | OS-level tooling installs. | No overlap — OS packages are explicitly out of scope for REQ-PROC-056 and remain so. `claude-install-os-tool` stays the OS path. |
| **REQ-PROC-011** (Roo Code deprecation) | Deprecation of an *AI tool*, not a package. | No overlap; different subject. |

**Conclusion:** one genuine net-new gap (package capability surface beyond `lib/` behaviour), one acknowledged-and-deferred gap in REQ-PROC-056 (cadence), and the admission/justification + replacement questions are entirely uncovered. The two-requirement split fills exactly these, with no duplication of existing gates.

---

## 6. Codebase reality check (grounds the policy)

- `pubspec.yaml`: **62 direct deps**, **44 pinned to `any`**, only **10 with caret constraints**. `any` means `flutter pub upgrade` can move them freely — i.e. the project is *already* exposed to the "latest is best" reflex REQ-PROC-056 warns about, and has **no cadence trigger** telling the agent when to (or not to) run an upgrade.
- `pubspec.lock`: ~200 resolved packages (mostly transitive).
- Existing pins carry good WHY comments (`bloc_lint`, `flutter_zxing`, mutation-test tooling) — evidence the project already practises *ad-hoc* lifecycle reasoning; R-B would make it a policy rather than a per-incident note.
- **No existing tooling** (`scripts/quality/check_dependency_*`) for freshness, health, or cadence. (Enforcement mechanism is TASK-PROC-056-01's subject, not this task's.)
- Implication for cadence: because the AI agent runs autonomously most days but never has a *trigger* to update deps, the realistic risk is **silent staleness**, not over-eager updates. R-B's cadence should be **event-based + a per-release sweep**, explicitly *not* aggressive time-based auto-upgrade (which would fight REQ-PROC-056's "default is to wait").

---

## 7. Decisions requiring user input (frame for one-round approval)

These are framed so each can be answered yes/no or A/B in one pass. **My recommendation is bolded.**

- **D1 — New-dependency autonomy.** May the LLM add a *new top-level dependency* on its own authority if it passes REQ-PROC-056 + all R-A health gates, or does every new top-level dep require recorded human pre-authorization?
  → **Recommend: human pre-authorization for every new top-level dep.** (Privacy-sensitive app; "the strongest supply-chain defence is not adding the dep" — seed S7. Transitive/dev deps pulled in *by* an approved dep are not separately gated.)

- **D2 — Cadence model.** Which trigger layering for this project?
  → **Recommend: event-based (advisory disclosed, deprecation surfaced by toolchain, build/gate failure) + a mandatory per-release-candidate `pub outdated` sweep. No time-based periodic auto-upgrade.** (Matches the AI-daily / human-intermittent / privacy-sensitive profile; avoids fighting REQ-PROC-056's wait-by-default.)

- **D3 — Capability-surface depth.** Should R-A's capability-surface health check extend to *transitive* dependencies (does any transitive dep introduce `dart:io`/network capability), or stop at direct deps?
  → **Recommend: direct deps mechanically gated; transitive capability surface assessed as an advisory signal at admission of the direct dep, not a hard per-transitive gate** (a hard transitive gate is high-noise and hard to automate reliably; flagged honestly as a residual risk).

- **D4 — Decomposition itself.** Do you endorse the **two-requirement** split (R-A + R-B + REQ-PROC-056 `mod`), or prefer one of the rejected shapes (four / one / five)?
  → **Recommend: two-requirement split as specified.**

- **D5 — Requirement homes/IDs.** R-A and R-B as **new siblings under `process/AI_rules/ai_tool_management/`** (alongside `dependency_supply_chain_safety/`), e.g. new folders `dependency_admission_and_health/` and `dependency_lifecycle/`. Confirm placement, or prefer they live as sub-features under the existing `dependency_supply_chain_safety/` folder?
  → **Recommend: two new sibling folders under `ai_tool_management/`** (keeps each requirement's intake-vs-admission-vs-lifecycle boundary visible at the folder level; REQ-PROC-056 stays the intake requirement).

---

## 8. Honest uncertainties / what remains open

- **Web research did not complete.** The spawned `general-purpose` agent for industry prior art (seeds S6–S9: Signal/Tuta/Bitwarden dep policies, AI-agent governance frameworks, socket.dev/snyk/deps.dev signal reliability, maintainer-takeover incident latency) **hit a sub-account session limit and returned no findings.** This synthesis is therefore grounded in the *internal* requirement landscape and codebase, not in external prior art. **Before or during authoring, the web research should be re-run** (different sub-account / after limit reset) to validate D2's cadence choice and D3's capability-surface stance against published practice. This is the single biggest evidence gap.
- **Health-signal reliability is assumed, not measured.** "No release in N months = abandonment" is a heuristic with false positives (stable packages). Maintainer-takeover detection is not reliably automatable by an LLM at point-of-decision. R-A must distinguish *mechanically-checkable hard gates* (license, advisory status, publish-date) from *advisory signals informing human judgement* (maintainer reputation, abandonment, capability surface). The exact gate/advisory partition is a Part-2 authoring detail and may shift once web research lands.
- **Attacker model not fully defended.** Neither R-A nor R-B defends against a *compromised transitive dependency introduced by an approved direct dep between lockfile refreshes*; that is partially REQ-PROC-056's intake job and partially out of any current requirement's reach. Flagged, not solved.
- **No modification to REQ-PROC-056's gates is needed** — only the cross-reference `mod`. If web research surfaces a reason to change the 7-day threshold or add a gate, that is TASK-PROC-056-01's territory, not this task's.

---

## 9. Part-2 authoring plan (executes only after user approval of §1 + §7)

If the decomposition is approved as-is, authoring proceeds via `requ-explore` (never direct edits):
1. `requ-explore` → **R-A** (Dependency Admission & Package Health), new sibling folder, `status: active` (living governance rule).
2. `requ-explore` → **R-B** (Dependency Lifecycle & Update Cadence), new sibling folder, `status: active`.
3. `requ-explore` → **REQ-PROC-056 `mod`** (cross-reference sentence + Related-Requirements bullets only).

Each authored requirement embeds its autonomy table (§4), references REQ-PROC-056 for version intake and REQ-PROC-052 for code-behaviour, and records the D1–D3 decisions as end-state constraints. If the user redirects the decomposition, this plan is rewritten before any authoring.
