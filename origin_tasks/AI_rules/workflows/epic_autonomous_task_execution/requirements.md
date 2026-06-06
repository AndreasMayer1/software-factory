---
id: REQ-PROC-041
status: defined
urgency: 4
urgency_reason: U4-DEV-PRODUCTIVITY
impact: 5
impact_reason: I5-ENAB
effort: XL
stakeholder: developer
created: 2026-04-05
after: [REQ-PROC-008, REQ-PROC-031]
blocks: []
market_research_refs: [] # No relevant findings identified
trackable_items:
  sections:
    - id: SEC-01
      name: "Overview"
      heading: "## Overview"
    - id: SEC-02
      name: "Purpose"
      heading: "## Purpose"
    - id: SEC-03
      name: "Scope"
      heading: "## Scope"
    - id: SEC-04
      name: "Features"
      heading: "## Features"
    - id: SEC-05
      name: "Dependencies"
      heading: "## Dependencies"
    - id: SEC-06
      name: "Cross-Feature Invariants"
      heading: "## Cross-Feature Invariants"
---

# Epic: Autonomous Task Execution

## Overview

An orchestration system that automatically starts and manages CCS sessions to process queued tasks without the user being present. The user starts the system, walks away, and returns later to review results and answer any pending questions.

## Purpose

Manual task execution requires the developer to sit at the terminal, start each task, wait for completion, and handle feedback prompts. This epic enables unattended batch processing of the task queue — maximizing throughput during off-hours while preserving the existing feedback-gate safety model by deferring questions instead of skipping them.

## Scope

**Included:**
- Automated sequential CCS session startup and monitoring
- Multi-account rotation to stay within API rate limits
- Graceful session termination on completion and on feedback gates
- Session identity tracking for reliable resumption
- Deferred-feedback storage and injection on resume
- Automated-mode signaling so skills adapt their behavior

**Excluded:**
- Parallel session execution (explicitly out of scope — race conditions unacceptable without user oversight)
- Modifications to task prioritization logic (uses existing "Do Next Task" routing)
- Changes to rate-limit pricing or account provisioning

## Features

- [`feat_session_orchestrator`](feat_session_orchestrator/requirements.md) — Script that starts CCS sessions sequentially, rotates accounts, and monitors process lifecycle
- [`feat_session_lifecycle`](feat_session_lifecycle/requirements.md) — Session termination (on completion and on feedback gate) and session ID tracking in task metadata
- [`feat_automated_mode`](feat_automated_mode/requirements.md) — Automated-mode flag, CLAUDE.md rules for automated behavior, non-blocking skill adaptations
- [`feat_feedback_pause_resume`](feat_feedback_pause_resume/requirements.md) — Structured feedback storage, session resumption with injected user answers

## Dependencies

- **REQ-PROC-008** (Orchestrator Workflow): The "Do Next Task" routing and skill-based task execution that each session relies on
- **REQ-PROC-031** (Smart and Cost-Efficient Model Switching): Account-rotation strategy must respect cost-efficiency principles
- **CCS tool**: The `ccs` CLI wrapper that manages multi-account Claude Code sessions (`ccs <account> --dangerously-skip-permissions`)
- **Claude Code session infrastructure**: Session folders, `--resume` capability, prompt-mode (`-p`) behavior

## Cross-Feature Invariants

1. Every automated session is an independent CCS process — never a subagent within another session
2. At most one automated session runs at any time (strict sequential execution)
3. A single authoritative flag distinguishes automated sessions from manual sessions; all behavioral adaptations key off this flag
4. No skill or workflow step in automated mode may block indefinitely waiting for terminal input
5. Feedback gates remain semantically intact — questions are deferred, never silently skipped
6. Manual (interactive) sessions are completely unaffected; all automated-mode behavior is gated behind the flag
