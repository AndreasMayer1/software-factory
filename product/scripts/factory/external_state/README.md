# External-State Postcondition Vocabulary

**Requirement:** REQ-PROC-044 (FU-8 / TASK-PROC-044-10)

The internal skill-interface contracts (`.claude/skills/*/contract.yaml`) validate
`quality_criteria` against **file conformance** — does the produced artifact match a
schema under `.claude/schemas/`? Factory-**boundary** interfaces (developer answers, web
research, OS installs, code release, optimize events) cannot be checked that way: their
postcondition is a fact about *external state* — a process exit code, an HTTP status, a
file on disk, a developer's reply — not a YAML shape.

This directory is the controlled vocabulary of those external-state checks. A
factory-boundary contract references an entry by name in its `quality_criteria`; the
matching script here is the executable validator. Each script is a self-contained tier-B
CLI: exit 0 = PASS, exit 1 = FAIL.

## Vocabulary

| Term | Script | What it asserts | Rationale (which boundary needs it) |
|---|---|---|---|
| `command_exited_zero` | `check_command_exited_zero.py` | a command's process exit code is 0 | OS installs (E5), builds (E7) — the universal "the action succeeded" signal when there is no readable artifact to schema-check |
| `url_returned_2xx` | `check_url_returned_2xx.py` | a fetched URL responded with HTTP 2xx | web research (E4) — the response body is by-definition variable, so the only stable postcondition is "the fetch succeeded" |
| `file_exists_at_path` | `check_file_exists_at_path.py` | a file exists, optionally ≥ N bytes | build artifacts (E7), installed binaries (E5) — binary outputs have no schema; `--min-bytes` subsumes the `build_artifact_exists` case (a 0-byte `.apk` is a failed build) |
| `developer_responded` | `check_developer_responded.py` | `answer.md` exists, is non-empty, and differs from `TEMPLATE_answer.md` | developer questions (E1) — formalizes the orchestrator's own "still-template = unanswered" convention so a downstream skill never resumes on a stale answer |
| `package_installed_at_version` | `check_package_installed_at_version.py` | `<tool> --version` output contains an expected substring | OS installs (E5) — "installed" is not enough; REQ-PROC-051 tier-A tracking needs the *version* pinned |
| `command_output_nonempty` | `check_command_output_nonempty.py` | a command produced non-whitespace stdout | structured web research via the `ctx7` CLI (E4) — `ctx7 docs` exits 0 even when it returns nothing; emptiness is the real failure |
| `network_host_allowlisted` | `check_network_host_allowlisted.py` | a URL's host is on an allowlist (exact or dotted-subdomain) | governance for E4/E5 — answers the parent exploration's open question "is `WebFetch` allowlisted?"; a precondition guard, not just a postcondition |
| `json_event_wellformed` | `check_json_event_wellformed.py` | a JSON file parses to an object with required keys | optimize-event channel (E9) — events are produced by external observers (git hooks, CI); a malformed event must stop `claude-optimize`, not silently corrupt it |

## Deferred vocabulary (documented, not yet scripted — YAGNI)

- `git_remote_pushed` — assert a ref/tag exists on a remote (`git ls-remote`). Deferred: the factory has **no automated push channel today** (E10 is developer-operated; commits land on local `develop`). Reopen when a skill issues `git push` unattended.
- `pdf_render_completed` / `screen_capture_saved` — Windows-host build/test artifacts (E11). Deferred: the `win-command-bridge` was deleted (TASK-PROC-054-02); Windows ops are manual. Reopen if an automated Windows channel returns.

## What these validators do NOT do

- They check **liveness/shape of external state at a moment**, never semantic correctness (a 2xx response may still be the wrong document; a versioned package may still be broken).
- `url_returned_2xx` and `package_installed_at_version` touch the network / OS and are therefore not exercised by the unit tests (`scripts/tests/test_external_state_checks.py` covers the deterministic predicate functions only).
