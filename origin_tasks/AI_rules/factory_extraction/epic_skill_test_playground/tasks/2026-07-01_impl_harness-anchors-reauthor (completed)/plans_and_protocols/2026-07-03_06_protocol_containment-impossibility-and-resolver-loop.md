# Protocol 06 — Containment is impossible for LLM authoring + machine-resolver loop

Task: TASK-PROC-068-11 · 2026-07-03 · third resume.

## The machine-resolver loop (needs a HUMAN)

Feedback checkpoints 02, 03, and now 05 all carry the **identical** resolution — same
`resolving_session_id: 585bc823…`, same `resolved_at: 2026-07-03T15:48:13Z`, same "Option A / use
`containment.py`" text with the same resume steps. Checkpoint 05 is a **stale re-serve** by the machine
resolver (TASK-PROC-068-17): it did **not** engage with my protocol-04 follow-up (the A1/A2/A3 blocker)
at all. Re-parking identically will keep looping. This decision needs the **actual developer**, not the
auto-resolver.

## Decisive new fact — the prescribed mechanism is technically impossible (empirically proven this turn)

The resolution says: author via an **isolated contained child session** (`containment.py`). I tested
whether a `containment.wrap_with_containment(...)` (bwrap `--unshare-all`) jail can reach the network:

```
probe_bwrap() → True   (bwrap present, jail is real)
inside jail: socket.create_connection(('api.anthropic.com', 443))
  → rc 1, getaddrinfo failure (DNS unreachable) — NO NETWORK
```

`--unshare-all` unshares the network namespace and `containment.py` never re-shares it. Therefore a
`claude -p` child session — which **must** reach the Anthropic API — **cannot run inside the containment
jail**. The AC-10 proof only ever ran an **offline stdlib script** (`doc_governance.py`); that is the
*only* thing the jail can run. "Author via a contained child session" is impossible **by construction**
for any LLM-driven skill (`ux-write-persona` / `ux-write-scenario` included).

This is not a preference or a safety-margin call — it is a hard technical incompatibility the machine
resolution never accounted for.

## Full blocker set (unchanged from protocol 04, still valid)

1. **Repo-destroying reset** — `test_harness_app/` is not its own git repo; `reset.py`'s
   `git reset --hard HEAD` resolves to the whole outer repo (known unfixed "Discovered risk" from 068-16).
2. **Containment has no network** — proven above; contained `claude -p` cannot author.
3. **Skill READMEs absent** — `deploy.py` excludes `requirements_user_needs/`.

## Consequence for the options

- The **only** ways an LLM authoring skill can actually target `test_harness_app/` are:
  - **A2′ — UNCONTAINED child session** (`cd test_harness_app && claude -p …`, network available, NO
    bwrap, NO reset). Functional, but: (i) uncontained + `--dangerously-skip-permissions` is a
    high-blast-radius nested-LLM run that CLAUDE.md §Agent Spawn Topology forbids without explicit
    bespoke authorization, and (ii) it drops the AC-09 isolation the resolution assumed. Needs explicit
    human sign-off on the *uncontained* aspect specifically.
  - **A3 — parametrize the skills** and author from THIS session (no child session at all). The
    developer previously declined this (chose Option A over "Option B"). Would need them to reverse that.
- **A1 (fix harness git topology) alone does NOT unblock authoring** — it fixes the reset hazard but the
  contained session still has no network, so a contained `claude` still can't author. A1 only helps if
  paired with A2′ (uncontained).

## Ask (for the human developer)

Given contained LLM authoring is impossible, pick one:
- **(1)** Authorize **A2′** — uncontained child `claude -p` session (no bwrap, no reset), trusted host
  authoring into `test_harness_app/`. (Optionally preceded by A1 to also fix the reset hazard for future
  runs.) I proceed on explicit yes.
- **(2)** Authorize **A3** — I add a target-root arg to the two skills via `claude-modify-skill` and
  author from this session (reverses the earlier Option-A-over-B choice).
- **(3)** Something else / defer.

No tree mutation has occurred across any of the three parks — a clean re-park strands nothing.
