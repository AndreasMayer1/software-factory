---
task_id: TASK-PROC-056-01
type: explore
parent_requirement: REQ-PROC-056
urgency: 4
urgency_reason: U4-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: pending
effort: L
created: 2026-05-21
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-07, AC-08, AC-09]
  sections: []
scope_description: "Research enforcement mechanism for REQ-PROC-056 dependency supply-chain gates (DG1-DG4): advisory sources, publication-date APIs, where the gate lives, evidence format, override path, agent UX, cost/latency budget."
release_description: ""
opus_recommended: true   # reason: cross-cutting research, security/privacy domain, explicit trade-off analysis required
writes_requirements: false
requirements_version:
  commit: pending  # requirements.md uncommitted at task creation; will be set after commit lands
  file: ../requirements.md
---

# Goal: Research Enforcement Mechanism for Dependency Supply-Chain Safety Gates

## Objective

REQ-PROC-056 defines four version-intake gates (DG1 minimum-age, DG2 advisory clearance, DG3 pre-install evidence, DG4 composability) that any dependency change must pass before it is admissible. The requirement specifies **what** must be true; this exploration determines **how** that is verified, where the verification lives, what evidence it produces, and how it presents itself to the AI agent and to the developer.

The exploration must enter the problem space honestly — multiple ecosystems (Dart/Flutter, Python, npm) have different advisory infrastructures, different publication-metadata APIs, and different attack histories. A single mechanism that works uniformly across all of them is desirable but not assumed. The exploration may conclude that a per-ecosystem approach with a shared evidence format is the right answer, or that a single uniform mechanism is achievable, or something in between.

## Background

REQ-PROC-056 was authored 2026-05-21 in direct response to the user's stated concern about LLM agents pulling brand-new package versions into the repository before the community has had time to surface supply-chain compromises. The empirical pattern that motivates the rule is well established: attackers publish a malicious version to a legitimate package, automated consumers ingest it within hours, and days later the malicious version is identified and patched. The 7-day age threshold combined with active advisory checks compresses this window from "happens by default" to "requires explicit override."

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-21_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For the requirement at task creation time:
```
git show <hash>:requirements_tasks/process/AI_rules/ai_tool_management/dependency_supply_chain_safety/requirements.md
```
(commit hash not yet assigned — requirements.md was authored in the same session as this task and is uncommitted at the moment of task creation.)

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

The exploration has a security-design flavor. Be skeptical of mechanisms that look watertight on paper. Ask: where does the LLM agent meet the mechanism, and what is the easiest way for a future agent to *not notice* the mechanism is there? A gate that the LLM can route around is no gate at all.

## Seeds

The seeds below are entry points, not a workplan. Expect some to lead nowhere and others to open new threads.

### S1 — Advisory data sources per ecosystem

What advisory feeds exist for pub.dev, PyPI, and npm? OSV.dev is the cross-ecosystem aggregator — does it cover pub.dev meaningfully? What is the latency between an advisory being filed in the original feed (GHSA, pub.dev's own feed) and showing up in OSV? Are there ecosystem-specific gaps the LLM should know about? What about rate limits, authentication needs, and whether the feed is queryable offline (cached snapshot vs live API).

### S2 — Publication-date discovery per ecosystem

The DG1 age check needs a reliable answer to "when was version X published?" — `pub.dev` exposes `/api/packages/<name>` with `versions[].published`; PyPI exposes `/pypi/<name>/<version>/json` with `upload_time`; npm exposes `time.<version>` on `/<name>`. Are these timestamps trustworthy under attack? An attacker who compromises a maintainer can backdate a release (or front-date it) — what assumptions does the rule rest on?

### S3 — Where the gate lives

Several architectural options exist, none dominant:
- **Pre-tool hook** intercepting Bash calls to `flutter pub`, `pip install`, `uv add`, `npm install`. Catches intent but easy to bypass (LLM writes the manifest directly).
- **Manifest-diff check** invoked by `verify-quality` / pre-commit. Catches the actual change at commit time. Hard to bypass but late — the LLM may already have run the install locally.
- **Wrapped install skill** (mirroring `claude-install-os-tool`). Forces all installs through a known entry point. Strong if discipline holds; weak if any other path remains.
- **Combination**: pre-tool hook for "intent" telemetry + commit-time check for the hard gate.

The exploration must compare these on three axes: (a) bypassability by the LLM agent, (b) cost/latency to the developer, (c) audit clarity (can a reviewer see what was checked?).

### S4 — DG3 evidence-artifact shape

DG3 requires that every dependency change carry verifiable evidence that DG1 and DG2 were checked. What does that artifact look like? Candidates: commit-message footer (parseable by the commit-time gate), separate override-log file (`automation/dependency_change_log/...`), task protocol entry under `plans_and_protocols/`. The artifact must be machine-parseable so the audit script can verify it; it must also survive normal git workflows.

### S5 — Override path (AC-07)

The override mechanism must be explicit, recorded, and auditable. Options range from environment-variable bypass (used elsewhere: `SKIP_QUALITY_GATES=1`) to commit-message tokens (`Override-DG1: package@version reason ...`) to a dedicated override registry (`.dependency-overrides.yaml`). The choice has implications for how easily an LLM can self-authorize — which the requirement forbids.

### S6 — Agent UX on gate failure

When the gate fires, the LLM sees an error. What error message gives the agent enough signal to make a correct decision (wait, pin to an older satisfying version, escalate)? Where does the agent's behavior plug into the existing five-cycle back-pressure protocol? Should the agent be capable of *proposing* a satisfying older version itself, or must that proposal go to the user?

### S7 — Cost and latency budget

A dependency change is rare but interactive. A 30-second advisory-DB query may be tolerable; a 5-minute one is not. What is the realistic latency budget? Can a local cache of the advisory DB make the common path fast (offline) and the rare path thorough (online refresh)? OSV.dev publishes full snapshots — is that the right caching primitive?

### S8 — Threat model for the mechanism itself

The mechanism is software. It can be compromised. What does the mechanism's threat model look like — what attacker capabilities does it assume, what does it explicitly not defend against, and what dependencies does the mechanism itself have (which must also pass the rule, recursively)?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: This task requires web research — advisory-feed APIs, registry APIs, prior art in supply-chain gate tooling (`pip-audit`, `dependabot`, `socket.dev`, `renovate`), and the threat-model literature. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. The subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags. Examples:
- *"How does pub.dev expose package version publication timestamps via API in 2025/2026?"*
- *"What is OSV.dev's coverage of pub.dev advisories and what is the typical latency from disclosure to OSV index?"*
- *"What prior art exists for git pre-commit gates that block fresh package versions, and what bypass patterns have been documented?"*

When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

A synthesis plan in `plans_and_protocols/` that:
- Names a concrete recommended enforcement mechanism (architecture, where it lives, how it composes with existing back-pressure infrastructure).
- Documents the rejected alternatives with the reasoning that ruled them out — future readers must understand the design space, not just the choice.
- Specifies the per-ecosystem details (which advisory source, which publication-date endpoint, what cache strategy) at enough resolution that an impl task can be derived without re-doing the research.
- Defines the DG3 evidence-artifact shape and the AC-07 override path concretely (file format / commit-message tokens / etc.).
- Identifies decisions that still require user input (and frames them clearly enough that the user can decide in one round).
- Is honest about what remains uncertain — e.g. attacker capabilities not defended against, ecosystem coverage gaps, latency characteristics not yet measured.

This task does NOT implement the mechanism. Implementation is a separate impl task (or task chain) derived from the approved plan.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-056 | pending | Parent requirement (defines the gates this task plans the enforcement for) |
