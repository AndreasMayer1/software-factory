# External-Interface Contract Declarations (≥3 spanning the spectrum)

**Task:** TASK-PROC-044-10 · **Date:** 2026-05-30

These are *exploration drafts* showing the internal contract format extending to the
factory boundary. They are deliberately kept in plans_and_protocols/ — choosing their
**canonical home** (e.g. `.claude/contracts/external/`) and wiring a lint is rollout work,
delegated to the follow-up impl task. Three interfaces are declared, spanning the spectrum
the goal requires: **dev-input (E1)**, **web (E4)**, **OS (E5)**.

## Format delta vs the internal `contract.yaml`

Identical structural skeleton (`derived_from` / `produces` / `quality_criteria` /
`preconditions` / `postconditions`). Three differences, all **additive** — an internal
contract that omits them is still valid:

1. Top key is `interface:` (E-number) not `skill:` — these are channels, not skills.
2. New field `input_modality:` on each `derived_from`/`produces` item — one of
   `file | frontmatter | conversation | invocation_arg | command_output | url_response`.
   The internal format only ever needed `file`; the boundary needs the rest (this is the
   single additive field the parent exploration predicted in `07_external_interfaces.md`).
3. `quality_criteria` items become `{check: <vocabulary-term>, …}` referencing
   `scripts/factory/external_state/`, instead of free-text "conforms to schema X".

---

## E1 — Developer-question response (dev → factory, pull)

```yaml
contract_version: 1
kind: external-interface
interface: E1
title: Developer-question response
direction: dev -> factory (pull)
purpose: >
  A skill that cannot proceed without a human decision writes a question and pauses;
  on resume it reads the developer's answer. Formalizes the pending_feedback channel.

derived_from:
  required:
    - path: automation/pending_feedback/<TASK_ID>/answer.md
      source: external            # the developer is the producer
      input_modality: file
      schema: null                # free-form markdown
      reason: The developer's decision; consumed by the resuming skill.
  optional:
    - path: automation/pending_feedback/TEMPLATE_answer.md
      source: external
      input_modality: file
      reason: Baseline used to detect "still unanswered" (answer == template).

produces:
  required:
    - path: automation/pending_feedback/<TASK_ID>/question.md
      input_modality: file
      schema: .claude/schemas/pending_question.yaml   # to be authored in rollout
      reason: The question + full context; produced by the pausing skill.

quality_criteria:
  - check: developer_responded
    target: automation/pending_feedback/<TASK_ID>/answer.md
    args: [--template, automation/pending_feedback/TEMPLATE_answer.md]
    note: PASS only when answer.md exists, is non-empty, and differs from the template.

preconditions:
  - The task is in_progress with session_id set in goal.md (claude-automated-mode rule).
postconditions:
  - On PASS the orchestrator resumes the session; on FAIL the session stays paused.
```

---

## E4 — LLM web research (factory → web → factory)

```yaml
contract_version: 1
kind: external-interface
interface: E4
title: LLM web research
direction: factory -> web -> factory
purpose: >
  doc-lookup-dependencies / find-docs fetch current API docs. The response body is
  inherently variable, so the postcondition is "the fetch succeeded from an allowed
  host", never "the body matches schema X".

derived_from:
  required:
    - path: "ctx7:docs:<library-id>"
      source: external
      input_modality: command_output    # ctx7 CLI prints docs to stdout
      schema: null
      reason: Preferred structured-doc channel.
  optional:
    - path: "https://<official-docs-host>/*"
      source: external
      input_modality: url_response       # WebFetch / curl fallback
      schema: null
      reason: Fallback when ctx7 returns nothing.

produces: {}     # web research is informational; it emits no factory artifact directly

quality_criteria:
  - check: network_host_allowlisted
    target: "<fetched-url>"
    args: [flutter.dev, dart.dev, pub.dev, docs.python.org]
    note: Precondition guard — refuse fetches outside the doc allowlist.
  - check: url_returned_2xx
    target: "<fetched-url>"
    note: Applies to the WebFetch/curl fallback path.
  - check: command_output_nonempty
    target_command: [ctx7, docs, "<library-id>", "<query>"]
    note: ctx7 exits 0 even when empty; emptiness is the real failure → fall back.

preconditions:
  - REQ-PROC-053 per-task lookup budget not exhausted.
postconditions:
  - Fetched docs are treated as informational, not authoritative; no downstream
    artifact assumes response-schema conformance (parent exploration §E4).
```

---

## E5 — OS-level tooling install (factory → OS → factory)

```yaml
contract_version: 1
kind: external-interface
interface: E5
title: OS-level tooling install
direction: factory -> OS -> factory
purpose: >
  claude-install-os-tool installs a binary from an external registry. "Installed" is
  insufficient — REQ-PROC-051 tier-A tracking needs the version pinned.

derived_from:
  required:
    - path: "apt|pip|npm|pub:<package-name>"
      source: external
      input_modality: invocation_arg
      schema: null
      reason: Package coordinate fetched from an external registry.

produces:
  conditional:
    - path: "<install-prefix>/bin/<tool>"
      input_modality: file
      schema: null                 # binary artifact
      condition: install command exited 0
      reason: The installed executable.

quality_criteria:
  - check: command_exited_zero
    target_command: [<install-cmd>, install, <package-name>]
    note: The install action succeeded.
  - check: package_installed_at_version
    target: <tool>
    args: [<expected-version-substring>]
    note: The installed tool reports the expected version.

preconditions:
  - REQ-PROC-060 dependency-admission applies for new top-level project deps
    (distinct from OS tooling; this contract governs OS tools only).
postconditions:
  - The tool is on PATH at the expected version and recorded per REQ-PROC-051 tier-A.
```

---

## Coverage of the other interfaces (declared by analogy — full set is rollout work)

| # | Interface | Reuses | Primary `quality_criteria` term(s) |
|---|---|---|---|
| E2 | Product intake | `input_modality: conversation` | (governance — no external-state check; routed through persona chain) |
| E3 | Developer notes | E1 pattern (`file`) | `file_exists_at_path` |
| E6 | Dependency admission | E1 pattern (structured `file`) | `developer_responded` (on the review reply) |
| E7 | Code → release → user | E5 pattern (binary `produces`) | `command_exited_zero`, `file_exists_at_path --min-bytes` |
| E9 | Optimize-event channel | structured-`file` produce | `json_event_wellformed` |
| E10 | Git-remote (NEW) | — | `git_remote_pushed` (deferred — no automated channel) |
| E11 | Windows-host bridge (NEW) | — | (deferred — bridge deleted, manual only) |
