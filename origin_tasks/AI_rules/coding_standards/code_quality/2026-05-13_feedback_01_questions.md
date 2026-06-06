# Questions accumulated while processing `2026-05-13_feedback_01.md`

Each section corresponds to one feedback item. Reviewed sequentially; items not listed here had no questions when I worked them through.

---

## A — Accessibility (more strict, screen reader, easy language)

### Changes I made (no input needed from you)

- **REQ-PROC-046 AC-07** rewritten to enforce the *full* active set of REQ-NFUNC-002 commitments per screen, not just the four `AccessibilityGuideline` checks. Now covers: tap-target / contrast / labelled-tap (existing), dynamic text scaling 200 % (NEW), reduce-motion respect (NEW), Simple-Mode parity for animated screens (NEW), linguistic-complexity gate (NEW). The gate auto-extends when Phase-2 ACs in REQ-NFUNC-002 promote to MVP.
- **REQ-NFUNC-002**:
  - Added `AC-14` for cognitive / linguistic accessibility on `.arb` strings, flag-for-review until you confirm threshold and tool.
  - Added new section `3.7 Cognitive Accessibility (Linguistic Complexity)` explaining the rationale and the decisions still open.
  - Added the corresponding entry to the MVP acceptance-criteria checklist in section 7.

### Decisions I need from you to finalize the cognitive-accessibility AC (AC-14)

**A.1 — Target audience for German readability.**

Two German-language standards exist:

| Standard | Target | Strictness |
|---|---|---|
| **Leichte Sprache** | Users with learning disabilities, very limited literacy; legally defined in Germany | Very strict — short sentences (< 8 words), one main clause, no subordinate clauses, defined vocabulary, no metaphors |
| **Einfache Sprache** | General inclusion (low-literacy adults, non-native speakers, users in cognitive load) | Lighter — sentences ≤ ~15 words, no nested subordinate clauses, common vocabulary, simple sentence structures |

Looking at the persona set (Sophie, Max, Jana, Hanna, Nina) — most are German-native adults with mental-health conditions, not learning disabilities. **My recommendation: Einfache Sprache.** Leichte Sprache would force the app's prose into a style that may feel patronising to the actual users.

Do you agree, or do you want Leichte Sprache, or a mixed approach (Leichte Sprache only for certain critical surfaces like onboarding and crisis-resources)?

**A.2 — Tool / metric choice.**

Three viable options:

1. **Local script + Wiener Sachtextformel.** A Python script parses `.arb` files, computes the index for each string, flags those exceeding the threshold. Self-contained, no external dependency, no API key. Threshold for Einfache Sprache typically 4th–6th-grade reading level (Wiener formula ~ 4–6).
2. **Local script + sentence-length + word-count + nesting-depth heuristics.** Simpler than (1); doesn't require a real readability formula; faster to implement. Less correlated with actual reading ease.
3. **LanguageTool API integration.** External service, supports "leichte Sprache" rule sets, returns rule-violation flags rather than a numeric score. More accurate but requires either self-hosting LanguageTool or a subscription.

My recommendation: option **(1)** — self-contained, deterministic, fits the project's "no external services" privacy stance. If accuracy is unacceptable after baselining, escalate to (3) with self-hosted LanguageTool.

Do you agree?

**A.3 — Threshold value.**

The Wiener Sachtextformel produces a score roughly correlating to school-grade reading level (1 = easy, 15 = very difficult). For Einfache Sprache, typical thresholds:

- **≤ 6**: very easy, conservative
- **≤ 8**: easy, common Einfache-Sprache target
- **≤ 10**: moderate

I'd suggest **≤ 8** as the initial threshold (matches the Einfache Sprache norm), but the right answer depends on baselining the current `.arb` content. Want me to ask the implementer of the future cognitive-accessibility task to baseline first and then propose a threshold?

**A.4 — Other accessibility dimensions you mentioned (mental, vision, touch, hearing, writing, seeing).**

Current coverage state after my edits:

| Dimension | Current coverage | Gap? |
|---|---|---|
| Vision (low vision / blindness) | Contrast WCAG AA, semantic labels, screen-reader Phase 2 | Phase 2 items not gate-enforced yet — promote when? |
| Cognitive / mental | Simple Mode, reduce motion, NEW linguistic gate | None remaining |
| Touch / motor | 48 dp tap target | No keyboard / switch / voice-input dimension yet |
| Hearing | None — app has no audio surface today | Add ACs *if and when* audio is introduced (notifications? voice prompts?) |
| Writing / form input | None explicit | Could add: forms with auto-complete suggestions, validation hints, error-recovery affordances |
| Speech input (voice control) | None | Lower priority; only matters once OS-level voice control is supported on Android |

Do you want me to:
- Promote any Phase 2 ACs (high-contrast theme, screen-reader flow, focus order) to MVP gate enforcement now?
- Add explicit ACs for writing/form-input accessibility (auto-complete, validation hints)?
- Defer hearing-accessibility until audio is introduced (with a note that it must be addressed at that time)?

**A.5 — "Check pending tasks, it's likely that not all of them are already written down."**

I searched `requirements_tasks/` for tasks referencing accessibility. The pending impl tasks under `epic_data_transfer/feat_qr_data_transfer/`, `feat_therapist_transfer_ui/`, `feat_transfer_detail_screen/`, and the QR transfer foundation tasks all mention accessibility in scope but I haven't read each goal.md to verify whether they own concrete accessibility ACs or just reference the requirement.

Do you want me to do that pass now (read each accessibility-touching task goal.md and surface any missing AC commitments), or defer to the screen-inventory task TASK-PROC-046-07 which is already scheduled to walk every screen?

---

## B — `doc/` ↔ pushback relationship (5 sub-questions)

### Changes I made (no input needed from you)

- **REQ-PROC-046 Developer Guidelines** gained two new bullets:
  1. **The doc/-vs-gate-set border is the scriptability test.** If a rule can be decided yes/no from a syntactic / structural property, it belongs in the gate set. Otherwise it stays in `doc/` and `quality-checker` enforces it by reading both. Gate set is the deterministic floor; `doc/` is the judgment-level ceiling. Both run in the back-pressure protocol.
  2. **Gate-set changes require user approval, not LLM autonomy.** An LLM may *propose* gate changes via `task-create` but must not silently modify analyzer config, scripts, or requirement ACs in the same task that triggered the proposal. Prevents the Goodhart's-Law failure of an LLM weakening its own constraints under pressure. `doc-update-guidelines` skill remains the legitimate path for evolving narrative guidance.
- **TASK-PROC-046-12 created** — analyze task to walk every `doc/` file, classify each rule as scriptable / judgment-only / already-gated, and propose migrations. This is the concrete answer to sub-question 3 ("how to migrate").

### Sub-questions and how my changes address them

| # | Sub-question | Status |
|---|---|---|
| 1 | More than one loop on verification? | Already addressed: REQ-PROC-046 AC-10 five-cycle bound; TASK-PROC-046-11 implements it. No new change. |
| 2 | Border between guidelines and gates? | New Developer-Guidelines bullet defines the scriptability test. |
| 3 | Migration path for `doc/` rules into the gate set? | TASK-PROC-046-12 is the audit; downstream impl tasks become candidates from its output. |
| 4 | Should pushback include a step that runs the guidelines verification? | Yes — `quality-checker` agent already reads `doc/` per layer; my changes in TASK-PROC-046-11 keep that step. No new gate; existing mechanism stays. |
| 5 | Auto-update of gates by LLM? | Explicitly forbidden by the new "user approval required" bullet. LLM proposes via task-create only. |

### Decisions I need from you

**B.1 — Granularity of "user approval" for gate-set changes.**

The new rule says LLM must propose, user must approve. Two interpretations:

- *Per-PR review.* LLM creates a task; user reads goal.md and approves the task; user reviews the resulting PR. Two checkpoints.
- *Per-task creation.* User approves the *task creation* itself (via `AskUserQuestion` from `task-create`). The implementation then proceeds without a second user gate. One checkpoint, but the user commits earlier.

I'd recommend per-PR review (two checkpoints) for gate-set changes specifically — they're consequential enough to deserve the extra gate. Other task types can use the lighter per-task-creation flow as today. Do you agree?

**B.2 — TASK-PROC-046-12 priority vs the other doc audits.**

This audit is `urgency: 2, impact: 4`. The other doc audit (TASK-PROC-046-12 walks `doc/`; TASK-PROC-052-04 audits cryptographic key storage; TASK-PROC-002-07 audits test naming) are similar weight. I haven't given them an explicit ordering. Want them sequenced (run doc-audit first since it surfaces the menu of potential gates that informs the others), or parallel (all three run independently and the user reviews proposals from each)?



---

## C — Flutter performance best practices

### Changes I made (no input needed from you)

Added seven Flutter-specific performance lints to the gate set (via TASK-PROC-046-03's scope and REQ-PROC-046's G1 row):

| Rule | What it catches | Cost of violation |
|---|---|---|
| `avoid-unnecessary-setstate` | `setState` calls that don't change rendered state | Wasteful rebuilds of entire widget subtree |
| `avoid-shrink-wrap-in-lists` | `shrinkWrap: true` on `ListView` / `GridView` in non-bounded contexts | Forces synchronous layout of all children (O(n) build per frame) |
| `avoid-rebuilds` | Widget construction patterns that force rebuild when constants would do | Compounds across frames on slow devices |
| `avoid-returning-widgets` | Method that returns a widget rather than extracting to a stateless class | Defeats `const` optimisation and BLoC selectors |
| `prefer-extracting-callbacks` | Inline closures in `build()` that rebuild every frame | Allocates new closures per frame; defeats child equality |
| `avoid-expensive-async-functions` | `Future` chains in widget `build()` or `initState` without isolation | Blocks first frame; blows G7 cold-start budget on the A40 |
| `avoid-passing-async-when-sync-expected` | Async callback passed where sync expected (common with `onTap`) | Multiple-tap bugs; race conditions during data-entry |

These all align directly with PERSONA-004's old-device constraint (Galaxy A40 / 2 GB-RAM devices). They're per-change gates via G1.

### Things considered but not yet gated

The following Flutter performance patterns are **not** lint-checkable today; they need either a custom DCM rule (cost: substantial), a heuristic grep gate (cost: moderate, accuracy: low), or a code-review discipline (status quo):

- **`RepaintBoundary` placement** around expensive subtrees (e.g. animations, complex visualisations).
- **`ListView.builder` vs. `ListView(children: ...)`** — the builder form is required for long lists but no lint enforces the choice.
- **Image caching / decoding off the main isolate** — `precacheImage`, `Image.network` cache extent.
- **State-management granularity** — using BLoC selectors / `BlocSelector` rather than rebuilding on every state change.
- **Lazy initialization** of expensive dependencies (avoid eager `GetIt.registerLazySingleton` violations).
- **Defer-to-idle work** — using `Future.microtask` / `scheduler.addPostFrameCallback` rather than running heavy code in `build()`.

These could become a new gate G9 ("performance pattern heuristics") with grep-based detection, but the accuracy of grep heuristics is low and the false-positive rate could erode trust in the gate set.

### Decisions I need from you

**C.1 — Custom DCM rule vs. grep heuristic for the un-linted patterns.**

For `RepaintBoundary` placement, `ListView.builder` usage, and lazy-init patterns: DCM supports custom rules but writing them is non-trivial. Grep-based heuristics are cheap but inaccurate. Three approaches:

1. **Defer the un-linted patterns to `doc/presentation/coding/best_practices.md` and rely on `quality-checker` reading the doc + judging.** Cheapest path. Loses determinism.
2. **Add grep heuristics now, accept false-positives, refine over time.** Fast, but the false-positive rate may force the exclusion-list to grow until the gate is meaningless.
3. **Defer to a future task that writes custom DCM rules** when DCM's rule-authoring API stabilises. Most rigorous, slowest.

My recommendation: **(1)** for now — strengthen `doc/presentation/coding/best_practices.md` with explicit performance patterns, let `quality-checker` read it, and revisit gating after TASK-PROC-046-12's doc audit has surfaced what else is in there. The seven new lints already provide substantial static enforcement; the marginal gain from adding heuristic gates today is small.

**C.2 — Profile-mode CI for the dynamic performance gate.**

G7 dynamic is currently per-release-candidate. With the Windows bridge speeding up flutter commands, would you want G7 to run more frequently (e.g. per-release-PR rather than per-release-candidate)? More frequent measurement catches regressions earlier; the cost is the A40 must be plugged in and the test run takes ~30 seconds per measurement run.



---

## D — Best-practice capture when pushback fails

### Changes I made (no input needed from you)

- **REQ-PROC-046 Back-Pressure Protocol** gained a new step 6: when a gate failure is resolved via a *non-obvious* fix, the LLM invokes `doc-update-guidelines` skill before task completion. The threshold matches the WHY-comment rule in CLAUDE.md §5: capture only patterns a future agent would not reach by reading current `doc/` + the code. Explicitly noted: this is *documentation* evolution, *not* gate-set evolution (gate changes still require user approval per item B).

### Acknowledging your own observation

You wrote: *"the LLM probably does not even repeat the same mistake um since it already reads the coding guidelines before writing code."* This is correct for the *general* case. The reason I still added step 6 is the narrow case of patterns the LLM would *not* reach by reading current `doc/`:

- Framework quirks (e.g. a specific Flutter widget's known rebuild behaviour)
- Library workarounds (a `drift` migration pattern that's not in `doc/architecture/drift_database_patterns.md` yet)
- Novel interactions between rules (e.g. how `prefer_const_constructors` interacts with localised strings)

For these, the LLM *would* repeat the mistake if it's not in `doc/`. The cost of an extra `doc-update-guidelines` invocation when nothing novel is found is low (the skill's job is to decide whether anything is worth writing); the cost of missing a captureable pattern is repeated friction.

### Coupling to item E (doc/ size discipline)

The "capture non-obvious patterns" rule risks doc/ bloat. That tension is the subject of item E — I'll address sizing/structural discipline there.



---

## E — doc/ size discipline and findability

### Changes I made (no input needed from you)

- **REQ-PROC-046 Related Requirements** gained a cross-reference to **REQ-PROC-048 (Guideline File Organization)** explaining how items D and E compose: D adds content via `doc-update-guidelines`; -048's 600-line bound + auto-split via `scripts/doc_governance.py` prevents unbounded growth.

### Why no further changes were needed

The system you're worried about is already in place:

1. **Findability** — `doc/README.md` is the navigation index. Each layer (`architecture/`, `domain/`, `presentation/`, `testing/`) has its own README. CLAUDE.md instructs every agent to read `doc/README.md` first and then only the relevant subfolder. LLM does NOT have to read everything — the index tells it what's relevant.
2. **Size cap** — REQ-PROC-048 AC-01 caps each file at 600 lines. The current top files are 575 / 566 / 554 lines — close to the limit but compliant. The system enforces this on every doc-update-guidelines run.
3. **Auto-split** — REQ-PROC-048 AC-04: `scripts/doc_governance.py` runs after `doc-update-guidelines` and creates a split task if any file hits 600 lines. Manual intervention not required.
4. **Reference hygiene after split** — AC-05 forbids broken references; AC-03 requires README updates in new subfolders.

### Decisions I need from you

**E.1 — Should the 600-line bound be tightened for pushback-pattern additions specifically?**

Item D's "capture non-obvious fix patterns" rule will steadily push file sizes upward. A file at 580 lines today will hit 600 after a few pattern captures, triggering a split task. That's the intended mechanism — but it means the split tasks become routine maintenance work.

Two options:
1. **Accept the cadence.** Split tasks are cheap (`doc-split` skill exists); the auto-creation mechanism handles them. Steady state: occasional doc-maintenance tasks in the queue.
2. **Tighten the bound to 500 lines for files near layers with high pushback-pattern volume** (e.g. `doc/presentation/` is likely to accumulate framework-quirk patterns). Leaves more headroom before split tasks fire.

My recommendation: **(1)** — accept the cadence. Tightening the bound just shifts the trigger point; doesn't solve the underlying growth dynamic. The auto-split mechanism is designed for exactly this case.

Do you agree, or want me to tighten the bound in REQ-PROC-048?

**E.2 — Should `doc-update-guidelines` be stricter about *what counts as worth capturing*?**

The pushback-pattern capture rule (item D step 6) says "only non-obvious patterns a future agent wouldn't reach by reading current doc/ + code". This is the same threshold as WHY-comments per CLAUDE.md §5. But the threshold is subjective — different LLMs will calibrate differently.

If you want stricter capture (less growth), I could add explicit criteria to the back-pressure step 6 — e.g. "only capture if the same gate failure happens twice on different tasks", or "only capture if the fix involved a workaround for a documented framework bug". Stricter = less growth = fewer captures, possibly missing useful patterns.

Want stricter criteria, or leave the current subjective threshold and rely on `doc-update-guidelines` skill's judgment?



---

## F — Integration tests

### My take

**Yes, integration tests make sense — selectively.** Three reasons specific to the pushback context:

1. **G7 dynamic performance is *already* integration tests.** TASK-PROC-046-02 (cold-start calibration) and TASK-PROC-046-10 (frame-budget) are integration tests by construction. They aren't optional — they're how G7 works.
2. **End-to-end accessibility is uncatchable by widget tests.** Widget tests verify a single screen's `AccessibilityGuideline` compliance (AC-07). They cannot verify *navigation between screens* preserves focus, that screen-reader announces context changes, that no modal traps focus. Onboarding is the strongest case — a user with accessibility needs lost during onboarding never sees the rest of the app.
3. **Critical-path workflows live across layers.** Data transfer, plan migration, entry submission are pipelines spanning domain → data → presentation. Unit tests verify each piece; integration tests verify the seam. Mutation testing (TQ2) can't reach the seam.

**On fragility (your historic concern):** the cure is in the test-writing patterns. Stable selectors (`find.byKey`, `find.bySemanticsLabel`) instead of `find.text("display string")`; centralised DI setup so refactoring doesn't break every test; synthetic-user fixtures shared across tests. These choices made up-front are the difference between "tests survive refactoring" and "tests break on every PR."

### Changes I made (no input needed from you)

- **REQ-PROC-002 AC-09** added — names the five surfaces requiring integration tests: (a) primary data-entry workflow, (b) data-transfer pipeline (sender + receiver), (c) cold-start (already owned by TASK-PROC-046-02), (d) frame-budget (already owned by TASK-PROC-046-10), (e) any new end-user workflow touching an AC-04 critical path. Cadence: per-release-candidate, not per-change.
- **TASK-PROC-002-08 created** — restore integration-test infrastructure + write the three non-performance flows (data entry, data transfer, accessibility onboarding). Cold-start and frame-budget owned by separate tasks but depend on this scaffolding. Phase 1 of the task is explicitly about the brittle parts: scaffolding patterns that survive refactoring.

### Decisions I need from you

**F.1 — QR transfer two-process testing.**

The data-transfer pipeline (AC-09 b) is conceptually sender + receiver. Two ways to test:

1. **Single-process simulation** — encode payload in test, decode in same test, verify round-trip. Doesn't exercise the actual screen-to-camera optical channel.
2. **Two-process** — `flutter drive` with two device instances. Closer to reality; significantly more complex to set up.

My recommendation: start with (1) for the pipeline correctness, defer (2) until/unless a real transfer bug surfaces that (1) cannot catch. Acceptable?

**F.2 — Effort tier.**

Restoring integration-test infrastructure (TASK-PROC-002-08) is L per my estimate — Phase 1 scaffolding alone is half a session, then three flows on top. The user's concern that "still it's a lot of work" is realistic. Do you want this scheduled now, or deferred until after the simpler per-change gates are wired (TASK-PROC-046-03, -046-11)?

**F.3 — Workflow tests beyond the named three.**

AC-09 (e) names "any end-user workflow whose underlying code is on the AC-04 critical-paths list." Today that list (in `doc/testing/critical_paths.md`, owned by TASK-PROC-046-04) includes encryption / Argon2id-KD which don't yet exist. As those features land, AC-09 (e) creates implicit requirements for integration coverage. Acceptable, or do you want each new integration test to be a deliberately scheduled task?



---

## G — Non-Dart code (C++, Kotlin, Swift)

### Changes I made (no input needed from you)

- **REQ-PROC-052 §When This Requirement Applies** now lists native source paths explicitly: `android/app/src/`, `ios/Runner/`, `windows/runner/`, custom-plugin C++ folders, plus native build files (`*.gradle`, `Podfile`, `Info.plist`, `CMakeLists.txt`).
- **REQ-PROC-052 §Behavior** gained a new "Native Code Scope" section spelling out how each SP gate maps to native files:
  - SP1 (no network I/O) → scans our native source for `OkHttp`, `URLSession`, `WinHTTP`, `libcurl`, `<winsock>`, `boost::asio` (network). Plugin source in pub-cache is governed by SP2 at the dependency level instead.
  - SP2 (no telemetry SDKs) → scans `pubspec.yaml` AND `android/app/build.gradle`, `android/build.gradle`, `ios/Podfile` (catches dependencies declared directly in native build files, bypassing pubspec).
  - SP3 (no hardcoded secrets) → all source / config files regardless of language.
  - SP4 (no weak crypto) → extends to `MessageDigest.getInstance("SHA1"|"MD5")` (Kotlin/Java), `CC_MD5` / `CC_SHA1` (Obj-C), `MD5_*` / `SHA1_*` from OpenSSL in C++.
  - SP5 (toString redaction) → Dart-only by nature; native types don't carry Dart-side mental-health content across method-channel boundaries.
  - SP6 (synthetic test data) → applies to native tests if/when added (none today).
- **TASK-PROC-052-01** scope updated: each grep script now also scans the appropriate native paths and patterns.

### What I did NOT add (deliberately)

- **No new native-language linting gate** (clang-tidy / ktlint / SwiftLint). My reasoning: the volume of custom native code is low (the user mentions "sometimes" C++ for QR-scanner mods). Adding a per-language linting toolchain for ~tens of lines of custom code is not minimum-effective-dose. If custom native volume grows, this becomes worthwhile.
- **No native test-infrastructure gate.** Same reason — we don't have native tests, and the integration-test surface goes through Flutter's binding rather than native frameworks.

### Decisions I need from you

**G.1 — Custom C++ volume threshold for adding native linting.**

At what point does it become worth wiring clang-tidy / clang-format into the gate set? Three rough thresholds:

1. **Now (eager).** Add clang-tidy to G1 for any C++ under `windows/runner/` and custom-plugin C++ folders. Cost: medium setup, low ongoing.
2. **At 500 lines of custom C++** (current is far below).
3. **Never explicitly** — defer to whenever a real native bug emerges.

My recommendation: **(2)** with a tripwire — TASK-PROC-046-12 (doc-audit) or a separate audit can count current custom-native LOC and flag if the threshold is approaching.

**G.2 — QR-scanner C++ specifically.**

You mentioned modifying the QR-scanner library's C++ code. Is that modification source-controlled in this repo, or a patch applied at build time? The gate set covers source in the repo but not patches applied externally (those would need a different mechanism — e.g., a pre-build script that re-applies and re-verifies the patch).



---

## H — Standardized 5-cycle escalation

### Changes I made (no input needed from you)

- **REQ-PROC-046 §Back-Pressure Protocol step 4** rewritten with an exact escalation-file specification:
  - **Path**: `automation/pending_feedback/[task-id]/escalation_[YYYY-MM-DDTHHMMSS].md` (uses the existing `automation/pending_feedback/` convention that the autorun system already knows about — the `TASK-PROC-006-02` folder I saw in earlier `git status` confirms this convention is live).
  - **Mirror copy**: hard symlink or copy at `[task-folder]/plans_and_protocols/[date]_escalation.md` for in-context discoverability when reading the task.
  - **Required sections**: Gates Still Failing, Cycle Log, Suspected Root Cause, Questions for User, User Response (initially blank).
  - **YAML frontmatter**: `escalation_type: gate_back_pressure_cap`, `task_id`, `agent_id`, `created_at`, `cycles_used: 5`, `status: awaiting_user_review`.
  - **Resumption protocol**: when the user fills in the User Response section and flips frontmatter `status:` to `resolved`, the next agent run reads the response, resets the cycle counter, and proceeds.
  - **Hard rule**: silent acceptance of a failing gate is forbidden; marking the task complete without resolving the escalation is forbidden.
- **TASK-PROC-046-11 (gate enforcement) scope** updated to implement this specific escalation pattern in the `verify-quality` skill, including reading the User Response on resumption and resetting the cycle counter.

### Decisions I need from you

**H.1 — Hard symlink vs copy.**

The escalation file lives in `automation/pending_feedback/`; a mirror in the task's `plans_and_protocols/` makes it discoverable when a future agent reads the task folder. Two ways to do the mirror:

1. **Hard symlink** — single source of truth, edits in either location reflect in both.
2. **Copy** — two files, must be kept in sync (or treated as snapshot-at-escalation-time + the canonical version is in `pending_feedback/`).

My recommendation: **(1)** hard symlink — avoids divergence. The implementation must handle the OS-level edge cases (Windows-host file systems sometimes don't symlink the same way; might need to test on the project's actual dev environment).

**H.2 — Granularity of "the cycle counter resets".**

When the user resolves an escalation, the cycle counter resets to 0 — the agent gets a fresh 5 cycles to apply the response. But what if the user's response is *itself* an invalid direction (e.g., "just suppress the rule") that introduces new violations? Three policies:

1. **Always reset to 0 on resolution.** User direction is trusted. If it's wrong, a new escalation fires after 5 more cycles.
2. **Reset to 0 only for resolutions that change the gate scope or thresholds.** Other resolutions get fewer cycles.
3. **Track total cycles across escalations.** After cumulative 15 cycles on the same task, hard-stop and require an explicit user override.

My recommendation: **(1)** — simplest, trusts the user. The escalation is itself the rare event; loops of escalations on the same task are rarer still and should be visible to the user via the proliferating escalation files.

**H.3 — Whose `task_id` when escalation spans multiple tasks?**

If an LLM is in the middle of an orchestration that spans multiple tasks (e.g., a backfill creator task that creates child tasks), and the gate failure surfaces during execution of a child task: does the escalation file's `task_id` name the child task (where the gates ran) or the parent orchestration (which is the longer-lived context)?

My answer: the child task (where the violations live). The user's response is about *that code*, not about the orchestrator. Acceptable?



---

## I — How to solve the pitfalls

Going through each Common Pitfall in REQ-PROC-046, -002, -052 and identifying which already has a mechanical countermeasure and which doesn't.

### REQ-PROC-046 pitfalls

| # | Pitfall | Countermeasure | Status |
|---|---------|---------------|--------|
| 1 | Gates passing locally but not in CI (stale `.dart_tool/`, uncommitted fixes mask failures) | `verify-quality` checks `git status --porcelain` is clean before running; refuses dirty tree without `--allow-dirty` | **NEW — added to TASK-PROC-046-11 scope just now** |
| 2 | Splitting a function only to satisfy SLOC (mechanical helper extraction) | Judgment-only; protocol step 2 says "revise the cause, not the symptom" | **No mechanical fix possible.** Mitigation is the quality-checker reading the diff before/after and flagging suspicious mass-extraction patterns. Surfaced as a "quality-checker enhancement" candidate below. |
| 3 | Suppressions without context | AC-11 + back-pressure step 5 + G5 grep script | Already covered |
| 4 | Treating G3 as "the tests I know about pass" | `flutter test` runs all tests, not selected | Already covered |
| 5 | Optimising one gate at the cost of another | Protocol step 2: "revise and re-run all gates as a set" | Already covered |
| 6 | Swallowed `Future`s in the data path | AC-06 + `unawaited_futures` analyzer rule | Already covered (lands in TASK-PROC-046-03) |
| 7 | Heavy work in `initState` without isolate | G1 perf lints added in item C: `avoid-expensive-async-functions`, `avoid-passing-async-when-sync-expected` | Already covered (lands in TASK-PROC-046-03 per item C) |
| 8 | `debugPrint` as production logging | AC-12 + `avoid_print` lint + `[DIAG-*]` convention | Already covered |
| 9 | Coverage as a goal in itself | REQ-PROC-002 AC-02 mutation testing | Already covered |
| 10 | Bundle size 'just because of assets' | `--analyze-size` JSON breaks down asset vs. code contributions | Already covered |

### REQ-PROC-052 pitfalls

| # | Pitfall | Countermeasure | Status |
|---|---------|---------------|--------|
| 1 | "Optional" telemetry SDK | SP2 is unconditional — SDK in `pubspec.yaml` is the failure, not runtime use | Already covered |
| 2 | `debugPrint(entry.toString())` before redaction lands | TASK-PROC-052-03 sequencing — AC-05 (redaction) must land before AC-06 logging restrictions can be meaningfully enforced | Already covered (task documented) |
| 3 | Cache key vs MAC ambiguity for SHA-1 | AC-04 requires inline justification naming non-security purpose | Already covered |
| 4 | Synthetic-looking data that is actually real | Bug-report PII lives in `plans_and_protocols/`, destroyed on task completion (task-complete-bugfix skill enforces) | Already covered |
| 5 | `dart:io HttpClient` added for testing | Test infrastructure lives outside `lib/`; SP1 scope excludes `test/` infrastructure paths | Already covered |

### REQ-PROC-002 pitfalls

| # | Pitfall | Countermeasure | Status |
|---|---------|---------------|--------|
| 1 | `expect(x, isNotNull)` as only assertion | TQ2 mutation testing catches it — nearly every mutation survives an isNotNull-only test | Already covered |
| 2 | Property tests with overly narrow generators | AC-03 requires generator to span the documented invariant range | Already covered |
| 3 | Mutation testing run only at release time | TQ2 has diff-only mode for per-change cadence | Already covered |
| 4 | Determinism failures dismissed as "flaky" | TQ4 10-run gate makes them undismissable | Already covered |
| 5 | Fixing a surviving mutant by deleting the mutated code | Protocol step 5 (revise the cause not the symptom) + quality-checker reading the diff before/after | Mitigation present; not bulletproof |

### Changes I made (no input needed from you)

- **TASK-PROC-046-11 (gate enforcement) scope** updated: `verify-quality` skill now mandated to refuse running on a dirty tree (`git status --porcelain` empty check) unless `--allow-dirty` is passed. This closes pitfall #1 mechanically.

### Decisions I need from you

**I.1 — REQ-PROC-046 pitfall #2 (mechanical helper extraction).**

This is the only pitfall with no mechanical countermeasure. The shape of the failure: an LLM hits the SLOC ≤ 50 bound, extracts five small helpers to dodge it, the original complexity is now distributed across six helper methods that together are more confusing than the original 80-line function would have been.

Three options to mitigate:

1. **Accept the limitation.** Trust quality-checker (reading the diff + `doc/`) to flag suspicious patterns when they're egregious.
2. **Add a heuristic gate**: detect when a single PR adds 4+ new helper methods to the same file each with SLOC < 10. Probably noisy.
3. **Stricter SLOC bound on helpers**: e.g. "no method with SLOC < 5 is permitted unless it's a property accessor". Forces helpers to be substantive.

My recommendation: **(1)** — accept the limitation. The mass-extraction pattern is rare; the false-positive rate of (2) would be high. Quality-checker reading the diff is the right defence.

Acceptable?

**I.2 — REQ-PROC-002 pitfall #5 (delete-the-tested-line).**

Less common but corrosive when it happens. Mitigation today: quality-checker reads the diff before/after and looks for "test was failing → now passes because code under test was deleted". Hard to detect mechanically — the test that *was* failing is no longer present in the diff (it was the unit under test that was deleted, and the test that referenced it was also deleted as "unused"). Detection would require comparing the test suite at two revisions — feasible but adds complexity.

Two options:

1. **Accept the limitation**, rely on code review.
2. **Add an audit gate**: after mutation testing surfaces surviving mutants, if a later mutation run shows fewer total mutants on the same file (because lines were deleted), flag it as a possible test-evasion. Specific, low false-positive rate, but requires the mutation tool to compare runs.

My recommendation: **(1)** for now; revisit if a real incident occurs.

Acceptable?



---

## J — `maximum-nesting-level: 5` for Flutter widgets sound?

### Short answer

**Yes, sound.** Your concern about Flutter widget tree depth is reasonable but rests on a misreading of what the DCM rule measures.

### What the rule actually measures

DCM `maximum-nesting-level` counts **control-flow nesting** within a function body:

- `if` / `else` blocks
- `for` / `while` loops
- `try` / `catch` / `finally`
- `switch` / `case`

It does **NOT** count constructor-call chains. A `build()` method like:

```dart
Widget build(BuildContext context) {
  return Scaffold(
    body: SafeArea(
      child: Padding(
        padding: ...,
        child: Column(
          children: [
            Row(
              children: [
                Container(child: Text("hi")),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}
```

…is six levels of widget composition but zero levels of control-flow nesting. The DCM rule sees this as nesting level 0 and is satisfied.

If the rule did count widget depth, no Flutter project would ever pass with the DCM default of 5 — including all the Flutter sample apps. The fact that the default is 5 across the Flutter community is empirical evidence that this interpretation is the universal one.

### Changes I made (no input needed from you)

- **REQ-PROC-046 AC-02** rewritten to spell out the distinction: "maximum control-flow nesting level ≤ 5", with the explicit clarification that widget composition depth is not counted, and a concrete example (Scaffold → SafeArea → Padding → Column → Row → Container → Text = six widget levels, zero control-flow levels).

This addresses both your concern and any future LLM that might misread the AC.

### Where 5 control-flow levels *might* still be tight

If a single `build()` method does this:

```dart
if (state.isLoading) {
  if (state.hasCache) {
    for (final entry in entries) {
      if (entry.isValid) {
        switch (entry.type) {
          case 'foo': // ← this is level 5
        }
      }
    }
  }
}
```

…it hits 5. The right response is "this is too much logic in `build()`; extract it to the BLoC / repository." Which is the point of the rule. So 5 is the right number even for the cases where it does fire.

### No decisions needed from you



---

## K — Naming, folder structure, pattern usage + web search

### Naming rules — finding

You already have a *proposed* naming-convention rule in `doc/linter/linter_configuration_proposal.md`:

```yaml
- prefer-correct-type-name:
    validation-reg-exp: "^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|(Service)|(UseCase)|(Entity)|(ValueObject))?$"
```

This enforces type-name suffixes. But I checked the *live* `analysis_options.yaml` — only the `dart_code_linter:metrics` section is configured. The naming rule (and most rules from the proposal doc) is NOT live. So naming is currently unenforced.

### Folder-structure rules — finding

The architectural rules in `doc/linter/linter_configuration_proposal.md` (`avoid-banned-imports`, `avoid-dynamic`, `avoid-global-state`, `no-object-declaration`, `ban-name` for `ButtonStyle` / `TextStyle` / `Color`) are also not currently live in `analysis_options.yaml`. The proposal exists; the enforcement doesn't.

### Pattern-usage rules

Most patterns (facade, memento, etc.) are not directly machine-checkable. The naming convention indirectly enforces some (e.g., the `*Repository` suffix implies a repository pattern; `*UseCase` implies CQRS-style separation). For interfaces vs. concrete classes: Dart has no built-in "every implementation must extend an interface" rule. DCM doesn't have one either. Pattern compliance largely remains in `doc/architecture/` + judgment.

### Changes I made (no input needed from you)

- **TASK-PROC-046-03 scope** updated to ALSO promote the proposed-but-not-live rules from `doc/linter/linter_configuration_proposal.md`:
  - Naming: `prefer-correct-type-name` (with the project's regex), `file_names`, `camel_case_types`, `non_constant_identifier_names`, `library_private_types_in_public_api`.
  - Architectural: `avoid-dynamic`, `no-object-declaration`, `avoid-global-state`, `ban-name` for direct styling classes.
- This means TASK-PROC-046-03 is now a substantially bigger task — it's effectively the "adopt the proposed analysis_options.yaml" task. The effort tier may move from M to L.

### Web search — findings

Agent completed. Full report at `2026-05-13_websearch_more_checks.md`. The high-leverage findings, ranked by fit:

| Tool / Package | What it adds | Fit for this project | Effort to adopt |
|---|---|---|---|
| **`bloc_lint`** (OSS, pub.dev) | 9 BLoC-specific rules: `avoid_flutter_imports`, `avoid_public_bloc_methods`, `avoid_public_fields`, `prefer_file_naming_conventions` (enforces `*_bloc.dart` / `*_event.dart` / `*_state.dart`), `prefer_void_public_cubit_methods`, `avoid_build_context_extensions`, etc. | **Strong** — this project uses BLoC heavily | S — add to `pubspec.yaml` dev deps + `analysis_options.yaml` |
| **`clean_architecture_kit`** (OSS) | Repository-must-implement-abstract enforcement; data-Models-leak-into-domain detection via naming heuristics; quick-fix scaffolding for UseCase + `toEntity()` mappers | **Strong** — project is Clean Architecture; naming heuristics could trigger FPs on existing types not following the conventions exactly | M |
| **`very_good_analysis`** (OSS, MIT) | 188 rules vs flutter_lints' 101 — adds ~70 rules including `always_declare_return_types`, `avoid_dynamic_calls`, `cancel_subscriptions`, `close_sinks`, `sort_constructors_first`, `unnecessary_lambdas`, plus most of what's in TASK-PROC-046-03 already | **Strong** — could *replace* `flutter_lints` as the baseline, subsuming most of TASK-PROC-046-03's adopted rules | L — high violation count expected; many small mechanical fixes |
| **`dart_code_metrics_presets`** (OSS) | 20 presets including Bloc, Riverpod, Flutter, Recommended, All; user-defined presets supported via YAML | Useful as alternative to hand-curating the DCM rule list | S–M |
| `clean_architecture_linter` (OSS, pub.dev v1.0.8) | 33 rules across `domain_rules`/`data_rules`/`presentation_rules` | **Mismatch** — Riverpod-flavoured; conflicts with this project's BLoC architecture | Skip |

Other findings worth noting:
- **No public rule asserts "BLoC State extends Equatable"** — would require custom DCM rule authoring.
- **No "WidgetName must end in Widget/Screen/Page" rule exists publicly** — same: custom DCM.
- **No Dart port of `boundaries`** (the ESLint plugin for folder taxonomy) — folder-taxonomy enforcement remains a custom-script gap.

### ⚠ Critical finding — DCM licensing

**DCM (dart_code_linter) is paid for commercial use as of October 2023.** Free tier is for OSS contributors only. Teams license required for closed-source / commercial projects, sold via Lemon Squeezy.

The project's current `analysis_options.yaml` already uses `dart_code_linter` for the complexity metrics (cyclomatic ≤ 20, parameters ≤ 4, SLOC ≤ 50). All the DCM rules I added to TASK-PROC-046-03 (`avoid-unnecessary-setstate`, `prefer-test-matchers`, `prefer-correct-type-name`, etc.) require DCM. And the new findings (`prefer-match-file-name`, DCM Bloc rules) require DCM too.

Since this is a closed-source side-project funded by donations, the **licensing status needs verification**. Two outcomes:

1. **Sole-developer / non-commercial side-project counts as personal use** — DCM may be free under their personal-use terms. Need to confirm against their actual ToS.
2. **Closed-source = commercial regardless of revenue** — would require a Teams subscription, which is a recurring cost the persona is unlikely to want.

If outcome (2), then the gate set has to be restructured to use only:
- Core Dart linter rules (free, OSS)
- `flutter_lints` (free, OSS)
- `very_good_analysis` (free, OSS, MIT) — covers a lot of DCM's ground
- `bloc_lint` (free, OSS)
- Custom Dart scripts (already part of the plan)

This is potentially blocking — please check DCM licensing against your situation before TASK-PROC-046-03 ships.

### Additional decisions I need from you (K.3–K.5)

**K.3 — DCM licensing (blocking).**

What's your DCM licensing status? Options:
1. You already have a Teams subscription — proceed as planned.
2. You believe personal/non-commercial use is covered free — let's confirm against DCM's actual ToS before proceeding.
3. You want to avoid DCM entirely — I'd need to rewrite TASK-PROC-046-03 to use only `flutter_lints` + `very_good_analysis` + `bloc_lint` + custom scripts. Most rules have free equivalents but a few (`avoid-unnecessary-setstate`, `prefer-correct-type-name` regex, `prefer-match-file-name`) would be lost or need custom implementation.

**K.4 — Adopt `very_good_analysis` as baseline?**

If yes: replace `include: package:flutter_lints/flutter.yaml` with `include: package:very_good_analysis/analysis_options.yaml` and remove the rules from TASK-PROC-046-03 that VGA already covers. Net: simpler config, higher initial violation count. Strong recommendation if you go with K.3 option (3).

**K.5 — Adopt `bloc_lint` and `clean_architecture_kit`?**

These are OSS so no licensing concern. Both are strong fits:
- `bloc_lint` is low-risk — purely additive rules.
- `clean_architecture_kit` is medium-risk — its naming-heuristic detection of "data Models leaking into domain" produces medium-FP rate; the project's existing types may or may not match the conventions it expects.

Adopt both? Just `bloc_lint`? Try `clean_architecture_kit` on a pilot subset first?



### Decisions I need from you

**K.1 — Adopting the rest of `linter_configuration_proposal.md`.**

That proposal document is from 2025-09-29 and was never fully adopted. My TASK-PROC-046-03 expansion now promotes most of it. Two open questions:

1. **`ban-name` for direct styling classes** (`ButtonStyle`, `TextStyle`, `Color`): this is restrictive — it forbids direct use anywhere in `lib/features/` and forces use of the design-system components. Probably what you want (it's already in your proposal), but the violation count could be high if existing code uses these directly. Want to keep this in?

2. **`avoid-dynamic` and `no-object-declaration`**: enforce strong typing. Existing code that uses `dynamic` for JSON deserialisation will need to be updated (e.g., switch to `Map<String, dynamic>` with explicit casts, or use code generation via `freezed`/`json_serializable`). High violation count expected. Want to keep this in?

If yes to both: TASK-PROC-046-03 is now firmly L-tier or even XL. Pilot-running it via the agent (as I did for hooks and the grep scripts) would tell us the violation count before committing.

**K.2 — Folder taxonomy enforcement.**

`avoid-banned-imports` enforces *layer boundaries* (domain can't import Flutter). It does not enforce *folder taxonomy* within a layer (e.g., "every file in `domain/` must be in `entities/`, `repositories/`, `value_objects/`, `services/`, `failures/`, or `events/`"). I haven't found a tool that does this for Dart. The closest is a custom shell script that asserts no files at the top level of `domain/`.

Want a small script for this (5 minutes of work)? It would catch new files dropped in wrong locations.


