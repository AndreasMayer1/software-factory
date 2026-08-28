# Protocol — Developer Decision: Option B (real OS-level containment)

Task: TASK-PROC-068-04 · captured 2026-06-27
Decision record (developer answer archived in `2026-06-27_03_feedback-checkpoint.md`).

## Decision

**Option B — implement the REAL `unshare`/`bwrap` mount-namespace jail** for SG-04 / AC-09 /
CON-04. NOT "containment by refusal". The sandbox is wanted: the walking skeleton must run REAL
child sessions so AC-07 (real deploy-run-reset) and AC-08 (real token/wall-clock cost) get genuine,
externally-grounded evidence.

User namespaces are now ENABLED in the devcontainer (TASK-PROC-054-12): a minimal custom seccomp
profile derived from Docker's default, relaxing only namespace-creation + mount-jail syscalls — no
`--privileged`, no `seccomp=unconfined`, outer wall otherwise intact. Container recreated.

**Verified now-working (2026-06-27, this session):**
- `unshare --user --map-root-user --mount sh -c '...'` → runs inside ns, `whoami` = root. OK.
- `bwrap --unshare-all --ro-bind ... echo` → OK.

(This reverses the earlier `2026-06-27_02_protocol_implementation.md` § environment finding, which was
correct at the time it was written — the container has since been recreated with userns enabled.)

## Implementation direction for the build

1. **`containment.py`**: replace the "refuse-to-launch" core with a REAL jail that wraps the child
   command so it executes inside a user+mount namespace confined to the harness dir, with the host
   factory tree (and the rest of the host fs outside the harness) UNREACHABLE via absolute path or
   cwd escape. Prefer `bwrap` (clean bind-mount jail: bind only the harness dir as the child's view,
   `--unshare-all`, no host paths bound) — it expresses the confinement declaratively. `unshare` is
   the fallback primitive. **Keep `ContainmentUnavailable` fail-safe** as the guard for any
   environment where userns is still unavailable (probe at launch; refuse uncontained unless
   `PLAYGROUND_ALLOW_UNCONTAINED=1`).
2. **AC-09 test (archetype-S/HIGH)**: must exercise the REAL jail — from inside the confinement,
   attempt to read/write a sentinel under the HOST factory tree via an absolute path and assert it
   FAILS (path not present / permission denied), while the same path is reachable WITHOUT the jail.
   This is the behavioural closure of CON-04, not a structural assertion.
3. **launch_adapter.py**: wrap the child `claude` invocation in the real containment; keep the
   JSONL hung-detection path parameterized on the CHILD's cwd (SG-01).
4. Finish deploy/reset/cost_ledger/run_skeleton; SG-02 cost path reused; SG-03 advisory annotation
   on every result artifact. All FIVE Python gates GREEN (use `claude-write-script` for every
   scripts/ file).

## Residual-risk note to bake into output (still required)

Even with the real jail, skeleton-stage REGRESSION verdicts remain ADVISORY (SG-03 — ~100
paired-fixture floor unreached). The containment itself is now real; the advisory scope is about
statistical validity of verdicts, not about the sandbox.
