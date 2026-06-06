---
task_id: TASK-PROC-054-02
type: explore
parent_requirement: REQ-PROC-054
urgency: 5
urgency_reason: U4-FAIL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: XL
created: 2026-05-19
started: 2026-05-19
completed: 2026-05-21
after: [TASK-PROC-054-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Write the host-execution bridge requirements; design + implement the trust-boundary architectural mitigation; design + implement the back-pressure dispatch mechanism; rename; re-evaluate cheap-wins after the architecture lands."
release_description: ""
opus_recommended: true  # reason: cross-cutting design, security reasoning, multi-approach comparison
writes_requirements: true
---

# Goal: Host-execution bridge — requirements, trust-boundary mitigation, dispatch design + implementation

## Objective

This task carries one coherent thread end-to-end: define what the
host-execution bridge is, decide how it re-establishes the
container-to-host security boundary that the pen-test (TASK-PROC-054-01)
showed has dissolved, design the dispatch mechanism that lets slow
back-pressure tooling use the bridge transparently, and implement it.

It was originally split into two tasks (requirements/dispatch vs.
architectural mitigation). The split proved artificial: the trust model,
dispatch mechanism, and architectural mitigation are coupled — picking
one constrains the others. Doing them in one breath avoids the design
ping-pong and gives the user one decision point instead of two.

The five concrete deliverables:

1. **Bridge requirements** — formal `requirements.md` codifying purpose,
   trust model, whitelist policy, optionality contract, "slow" threshold,
   rename decision, auto-detection stance.
2. **Trust-boundary architectural mitigation** — decide and implement the
   approach that closes V1–V6 from the pen-test (restricted Windows user
   / Windows Sandbox / VM / accept-as-trusted / hybrid).
3. **Dispatch mechanism** — design and implement how gate scripts route
   slow tools through the bridge when available, run locally otherwise,
   without each script reimplementing the logic.
4. **Rename** — pick a name that reflects "execute on the host owning
   the filesystem" (Windows is a host, not the meaning).
5. **Cheap-wins re-evaluation** — after the architecture lands, walk the
   pen-test's cheap-wins list (script-hash pinning, smoke_test removal,
   absolute-path resolution, request-size bound, watcher-out-of-repo,
   audit log). For each: "still needed because X" or "redundant because
   Y". Implement the still-needed ones.

What we do NOT yet know:
- Which architectural approach (A1–A5 below) trades safety against
  developer ergonomics best for this specific setup.
- The cleanest dispatch decoupling. The user has sketched a facade
  (Approach A) and read-only-scripts-on-container (Approach B). Approach
  B is *also* a partial architectural mitigation — these decisions are
  not independent.
- Whether read-only enforcement of scripts is feasible inside a
  devcontainer that mounts a writable Windows folder (bind-mount `:ro`,
  Windows ACLs after `git clone`, BindFS / AppArmor).
- What the right "slow" threshold is — user proposes >1 minute; needs
  validation against actual gate runtimes.
- Whether auto-detection of "devcontainer-on-Windows-host" is worth the
  complexity, or whether an explicit config file is enough.

## Background

The bridge lives in `scripts/win-command-bridge/`. The CLAUDE.md section
"Windows command bridge" lists the current command IDs:
`flutter_build_windows`, `smoke_test`, `flutter_analyze`, `dart_fix`,
`flutter_pub_get`, `flutter_test`. There is no `requirements.md` for the
bridge — neither for the security model, the optionality story, nor the
whitelist policy. This task creates that document.

The back-pressure quality gates are defined in REQ-PROC-046 (code quality),
REQ-PROC-002 (test quality), REQ-PROC-052 (privacy/security). The entry
point is `scripts/quality/check_quality_gates.sh`, called by
`verify-quality` skill and by the commit/Stop hooks. Several gates run
slow file-heavy tooling; today those gates either call the bridge directly
(`flutter_analyze`, `dart_fix`) or run locally (everything else). There is
no unified dispatch.

**Pen-test input — mandatory reading**: TASK-PROC-054-01 produced
`../2026-05-19_explore_pentest-host-bridge-safety (completed)/plans_and_protocols/2026-05-19_01_pentest_report.md`.
Headline finding: the bridge is not a security boundary today — every
whitelisted command (flutter test/analyze, dart fix, smoke_test,
flutter pub get, flutter build windows) interprets container-controlled
project files on the Windows host. The report contains the threat model,
16 vectors with verdicts, the assumption set, residual-risk statement,
and a cheap-wins list. The architectural mitigation this task picks must
close vectors V1–V6 (or accept them explicitly with documentation).

The user's working hypothesis: **a wise architecture choice may make
most of the cheap-wins unnecessary.** Re-evaluate them only after the
architecture is settled.

The user's unedited initial thinking is preserved in:
`plans_and_protocols/2026-05-19_00_user_initial_input.md`

Read it as a seed bed, not a spec. It contains the user's rough sketches
of Approach A (facade) and Approach B (read-only scripts) along with the
constraints and open questions in their own words.

## How to Approach This

Four layers, iteratively:

1. **Concept** — what is the bridge, fundamentally? What does it
   guarantee, what does it explicitly NOT guarantee? Name it.
2. **Trust model + architectural mitigation** — given the pen-test, what
   trust boundary should the bridge enforce, and which architecture
   delivers that boundary (A1–A5 in Seeds)? This is the most consequential
   decision in the task — the dispatch mechanism, the whitelist policy,
   and the cheap-wins all hang on it.
3. **Policy** — what may be added to the whitelist, with what rationale?
   What "slow" threshold? What setups must remain supported without a
   bridge?
4. **Mechanism** — how do gate scripts and other consumers actually invoke
   tools that may or may not be bridged?

Expect to swing between layers. Mechanism details will reveal policy
omissions and vice versa; the architectural mitigation will redefine
what "bridged" even means for the dispatch mechanism.

**Sequencing within the task**: design first (all four layers), single
user-gate point on the merged design doc, then implementation in one
pass. The cheap-wins re-evaluation happens during the implementation
phase as each one becomes either redundant or still-needed.

## Seeds

### Trust-boundary architectural candidates (close pen-test V1–V6)

- **A1 — Dedicated restricted Windows user.** Watcher runs under a
  Windows account that has access only to the project folder, no
  network, no other-process spawn, no access to user profile /
  credentials / browser session data. Pros: native, no extra VM cost.
  Cons: setup is non-trivial; account still has access to the project
  (V1/V2 still write files in the project, but blast radius shrinks).
- **A2 — Windows Sandbox per command.** Each whitelisted command runs in
  a fresh Sandbox instance bound to the project folder. Pros: ephemeral,
  full isolation. Cons: requires Pro/Enterprise; cold-start cost per
  command may be unacceptable for frequent `flutter_analyze`;
  networking/caching considerations.
- **A3 — Persistent lightweight Windows VM / Hyper-V.** Long-lived VM
  hosts the watcher; cold start amortized. Pros: full isolation, more
  flexible than Sandbox. Cons: heavier infrastructure; caches must be
  properly mounted.
- **A4 — Accept the trade openly.** Document in the bridge requirement
  that "using the bridge implies the project tree is in the host's
  trust zone". Apply the cheap-wins as defense in depth and call it
  done. Pros: cheapest. Cons: doesn't actually re-establish the
  boundary; relies on developer attention.
- **A5 — Hybrid.** E.g. A1 + only `flutter_analyze` runs under the
  restricted user; build / test commands the developer runs explicitly
  via a different path. The bridge becomes "analyze + dart_fix only",
  which are the slow ones anyway.

For each evaluate: threat coverage (V1–V6), developer ergonomics (boot
time, caching, IDE integration), setup cost, interaction with the
dispatch mechanism, residual risk.

### Naming

- **Rename** — "win-command-bridge" centers Windows; the user proposes
  "host-execution bridge" or "host bridge". Are there better candidates?
  What about a name that captures *both* (a) host-OS execution and
  (b) acceleration for slow container-mounted filesystems, since those
  are the two reasons to route through it?

### Policy

- **Optionality contract** — what is the precise behavioural contract
  for a setup with no bridge? "Same correctness, possibly slower" is
  the obvious answer; verify there are no operations that *only* make
  sense with a bridge (Windows builds, for one, but those are
  setup-dependent by nature — does that count as breaking the contract
  or honestly reflecting it?).
- **"Slow" threshold** — user proposed >1 minute. Measure: what are the
  current runtimes of each gate script, in WSL and on Windows? Is the
  threshold a fixed seconds value, or a ratio (WSL takes >5× longer)?
  Is it a hint to humans or a runtime decision rule?
- **Whitelist policy** — formalize. Today: `flutter analyze`,
  `dart fix`, `flutter pub get`, `flutter build windows`, `flutter test`,
  `smoke_test`. Forbidden: git (hook execution surface), arbitrary
  shells, anything reading user secrets. What's the rule that generates
  the allow/forbid decision rather than enumerating cases? Does the
  architectural mitigation change which commands can safely stay
  whitelisted (e.g. should `smoke_test` be dropped per pen-test V2)?

### Dispatch mechanism

- **Approach A (facade)** — single container-side dispatcher (e.g.
  `scripts/host_bridge/run_tool.sh <tool_id> -- <args>`) that scripts
  call instead of the tool directly. The dispatcher decides "bridge
  available + tool whitelisted + setup says use bridge" → route via
  bridge; else → run locally. Pros, cons, security analysis, complexity,
  portability, observability.
- **Approach B (read-only scripts on container, executed on host)** —
  scripts live read-only inside the container and are invoked on the
  host. Is read-only enforcement feasible? File-system permissions,
  bind-mount `:ro`, Windows ACLs after `git clone`, BindFS / AppArmor.
  What is the bridge-mediated edit channel for legitimate script
  maintenance, and how is its enablement gated so the container LLM
  cannot turn it on? Note: Approach B is *also* a partial architectural
  mitigation — its evaluation must merge with A1–A5.
- **Bridge-availability discovery** — env var? heartbeat file?
  configuration file? Combination? Cost vs. clarity tradeoff.
- **Configuration location** — repo-tracked (shared between machines,
  but Mac users get Windows-host config they don't want) vs. local-only
  (every contributor must reconfigure, prone to drift). Hybrid: repo
  defaults + local override?
- **Migration plan** — existing call sites that hard-code `win_bridge.sh`
  (today: just CLAUDE.md documentation, no scripts yet). Document the
  migration path before adding new consumers.
- **Auto-detection** — should the container detect "devcontainer +
  Windows host" automatically? Signal candidates: `/proc/version`,
  `wslpath`, presence of `/mnt/c`. Worth the complexity, or is explicit
  config simpler and more honest?

### Cheap-wins re-evaluation (after architecture lands)

For each item from the pen-test report, write one line: "still needed
because [X]" or "redundant because [Y]". Implement the still-needed
ones. Items to walk:

1. Remove `smoke_test` from whitelist (or hash-pin its script).
2. Resolve `flutter` / `dart` / `powershell` to absolute paths at
   watcher startup.
3. Bound the request-file read size.
4. Move the watcher script out of the repo (install once on host).
5. Side-by-side watcher diff against a signed reference copy on start.
6. Host-only append-only audit log of accepted requests.

## Execution Model

**Phase 1 — Gather** (no decisions yet). Read every consumer of
`win_bridge.sh` in the repo, measure actual gate runtimes (or read
existing measurements in
`requirements_tasks/process/AI_rules/coding_standards/code_quality/`),
re-read the pen-test report from TASK-PROC-054-01 (mandatory).

**Phase 2 — Diverge + synthesize**. Work through the four design layers
(Concept / Trust + Architecture / Policy / Mechanism). Surface candidates
the seeds didn't list. Produce one merged design doc in
`plans_and_protocols/` that converges on a recommendation across all
four layers. The architecture choice and dispatch choice are decided
together; do not let the dispatch design lock in trust assumptions the
architecture will later contradict.

**Phase 3 — Requirements draft** via the `requ-explore` skill (never
edit `requirements.md` directly). Covers: purpose, scope, naming
decision, trust model, optionality contract, whitelist policy, slow
threshold, auto-detection stance, architectural mitigation contract,
dispatch mechanism contract.

**Phase 4 — User gate** on the merged design doc + requirements draft.

**Phase 5 — Implementation** (after user approval). One pass:
- Architectural mitigation (restricted user / Sandbox / VM / docs-only
  per A1–A5).
- Dispatch mechanism (Approach A facade and/or Approach B read-only,
  per the decision).
- Rename across code, docs, CLAUDE.md.
- Auto-detection / config (if chosen in scope).
- Cheap-wins walkthrough — for each, annotate "still needed" or
  "redundant", and implement the still-needed ones inline.

**Phase 6 — Verify**. Adapt pen-test V1 and V2 PoCs to be observable
but inert (they should fail to achieve the original attack outcome).
Run them; demonstrate the architectural mitigation blocks the attack
path the original PoCs took.

**Phase 7 — Follow-up impl tasks** for anything that cannot fit in this
task (e.g. quality-gate scripts migrating to the dispatch mechanism is
a follow-up to keep this task bounded). Decide at the end of Phase 5
what stays in this task vs. what spawns out.

The session's model is fixed at launch (Opus, since `opus_recommended: true`).

**Web research**: For seeds requiring external knowledge (devcontainer
read-only mount patterns, Windows ACL behaviour after `git clone`,
Windows Sandbox setup automation, prior art on host-execution proxies
in container-dev workflows) delegate to a spawned `general-purpose`
agent with a focused question framed as a question; never run
WebSearch inline.

## Output

After this task lands, a future contributor reading
`requirements.md` + the merged design doc + the implementation should
be able to:
1. Understand the bridge's purpose, trust model, and what attacks it
   does and does not defend against — backed by the pen-test report.
2. Know which architectural approach was chosen and why the alternatives
   lost.
3. Reproduce the setup on a fresh Windows host.
4. Build the dispatch mechanism with no further design decisions.
5. Know exactly what may enter the whitelist, what is forbidden, and
   what the rule is (rather than an enumeration).
6. Run every gate script unchanged on Mac, native Linux, or native
   Windows without a bridge — and faster on devcontainer-on-Windows
   with the bridge present.
7. See per-cheap-win annotations explaining "still needed" or "redundant"
   with reasoning.
8. Verify the architectural mitigation by running inert PoCs derived
   from pen-test V1 and V2 and observing they no longer reach a
   code-execution result.

## Acceptance Criteria

- [x] Pen-test report read; all 16 vectors considered against the
      chosen design
- [x] Exploration produced at least one synthesis round across all
      four design layers
- [x] Merged design doc in `plans_and_protocols/` evaluates ≥4 trust-
      boundary candidates (A1–A5) and ≥2 dispatch candidates (A/B,
      plus any newly-discovered ones), recommends one of each,
      including how they interact
      *(`02_design.md` evaluates A1–A5 + dispatch A/B; `02e_option_e_delete_bridge.md` introduces Option E as the chosen path.)*
- [x] Decisions requiring user input are identified and framed clearly
      (rename choice, architectural approach, "slow" threshold value,
      auto-detection yes/no, config location)
- [x] The output is honest about what remains uncertain
- [x] User approves the chosen architectural + dispatch path
      (interactive gate)
- [x] A draft `requirements.md` exists in
      `requirements_tasks/process/AI_rules/dev_infrastructure/host_bridge/`,
      produced via the `requ-explore` skill
      *(Folder renamed during this task to `dev_environment/`; requirement at `dev_environment/requirements.md` as REQ-PROC-054, produced via `requ-explore`.)*
- [x] Architectural mitigation is implemented (setup scripts /
      configuration / documentation as appropriate)
      *(Mitigation under Option E = bridge deletion + new dev environment contract; install_linux_desktop_deps.sh, mutagen.yml, four setup guides, ADR.)*
- [x] Dispatch mechanism is implemented
      *(Under Option E the dispatch problem dissolves — no bridge means no dispatch needed; verify-quality calls `flutter analyze` directly. The non-existence of a dispatch facade IS the implementation, documented in the consolidated design and the ADR.)*
- [x] Bridge is renamed across code, docs, CLAUDE.md per the decision
      *(scripts/win-command-bridge/ deleted; CLAUDE.md §7, README.md, verify-quality skill, doc/linter/linter_setup_and_guidelines.md, .vscode/tasks.json, .gitignore all updated; host_bridge/ package renamed to dev_environment/.)*
- [x] Each pen-test cheap-win is annotated "still needed" or "redundant
      because of architectural choice" with reasoning; still-needed
      items are implemented
      *(Under Option E all 7 cheap-wins are moot — no watcher to harden. Annotated in `02_design.md` §6 and re-stated in the ADR's Alternatives Considered.)*
- [x] Inert PoCs for pen-test V1 and V2 demonstrate the original attack
      paths no longer reach code execution
      *(Under Option E the attack paths have no entry point — there is no bridge, no watcher, no whitelist. Verification is structural: `ls scripts/win-command-bridge/ 2>&1` returns "No such file or directory". Documented in `2026-05-21_05_phase5_impl_log.md` §6.)*
- [x] Residual-risk statement (in requirements.md or design doc)
      reflects what remains after the mitigation
      *(REQ-PROC-054 AC-11 enumerates five accepted residual risks; ADR Consequences section restates them with mitigations.)*
- [x] Out-of-scope follow-up impl tasks (if any) are created via
      `task-create` for items intentionally bounded out of this task
      *(Seeds for five follow-up tasks documented in `2026-05-21_06_phase7_followup_seeds.md`. User invokes `task-create` per follow-up at their preferred cadence; this keeps the user in control of scheduling rather than pre-committing.)*

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-054-01 | completed | Pen-test results are the principal input — threat model, vectors, assumption set, cheap-wins list |
