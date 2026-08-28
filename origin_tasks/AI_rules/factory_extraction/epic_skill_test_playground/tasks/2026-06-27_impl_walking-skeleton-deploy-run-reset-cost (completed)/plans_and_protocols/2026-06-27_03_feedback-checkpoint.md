---
skill: task-resolve
mode: automated
decision: ""
task_id: TASK-PROC-068-04
captured_at: 2026-06-27
---

# Question

---
task_id: TASK-PROC-068-04
session_id: cd26108b-11c1-450b-81df-17e28036268d
account: gmail
status: awaiting_answer
asked_at: 2026-06-27T08:40:28Z
skill: task-resolve
---

# Pending Question — SG-04 / AC-09 OS-level containment is infeasible in this devcontainer

Full environment findings (verified): `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-27_impl_walking-skeleton-deploy-run-reset-cost/plans_and_protocols/2026-06-27_02_protocol_implementation.md` (§ Containment environment findings). Build plan: same dir, `..._01_plan_walking-skeleton.md`.

## The blocker

The goal mandates (SG-04, **not open debate**) re-instating ONE OS-level containment layer — `unshare` namespace **or** separate OS user — to close CON-04 (absolute-path cwd-escape) for AC-09 (archetype-S / **HIGH**). I independently verified that **both** are infeasible in this Docker devcontainer:

- `unshare --user --mount` / `--map-root-user` → `Operation not permitted` (even with `sudo -n`). No unprivileged user namespaces.
- `bwrap` → `No permissions to create new namespace`. `chroot` → no `CAP_SYS_CHROOT`.
- Workspace is mounted **world-writable** (`drwxrwxrwx`) → separate-OS-user isolation is ineffective.

The agent's interim implementation (on disk, `scripts/playground/`) falls back to **fail-safe containment**: refuse to launch a child uncontained when no OS layer is available (`ContainmentUnavailable`), plus `HOME`/`XDG_*` env-scrubbing as secondary defense, with a `PLAYGROUND_ALLOW_UNCONTAINED=1` bypass.

## Why this needs your decision

"Containment by refusal" technically closes CON-04, but it means the skeleton **cannot run a real child session in this environment** — which guts the externally-grounded evidence for the other two ACs whose EGP referents demand *real* runs:
- AC-07 (F): "a **real** deploy-run-reset cycle returning the harness to a clean state"
- AC-08 (C): "the **real** token consumption + wall-clock duration of the child sessions a test run launches"

So the walking skeleton can't actually "walk" here. I won't unilaterally (a) mark a HIGH-consequence safety AC satisfied "by refusal," (b) re-scope AC-09, or (c) substitute a different primitive (Docker-in-Docker would trip the REQ-PROC-060 dependency-admission gate and is REQ-PROC-054 dev-infra scope). Pick the direction:

**Option A — Accept fail-safe + env-scrubbing as the skeleton-stage containment (ship as-is).** AC-09 satisfied "by refusal"; AC-07/AC-08 evidence is **mocked-subprocess only** in this env. Add a visible residual-risk note (like SG-03's advisory annotation) that real OS containment + real-child runs are deferred. Cheapest; lands the task now. Downside: HIGH/archetype-S AC met only structurally, not behaviourally.

**Option B — Enable user namespaces in the devcontainer first (dev-infra change), then real `unshare`/`bwrap` containment.** Requires `--privileged` or seccomp `unconfined` / userns-allow in the devcontainer config — a REQ-PROC-054 dev-infrastructure change outside this script task's scope. Likely a separate task + your authorization. This task would park until that lands.

**Option C — Adopt a non-userns containment primitive** (e.g. nested Docker container bind-mounting only the harness dir, no host tree). Heavier design than the goal anticipated; needs docker-socket access and a dependency-admission decision (REQ-PROC-060). Confirm you want this and I'll route the dependency gate.

**Option D — Re-scope AC-09 for the skeleton stage** (formally defer OS-level containment to T-corpus/T-maturity, document residual risk), keeping fail-safe as interim. A requirements change to a HIGH-consequence AC — would route through `requ-explore`.

My recommendation: **A** for the skeleton (with an explicit, visible residual-risk annotation and a follow-up task for B), because the skeleton's purpose is the deploy→run→reset→cost wiring and the real-containment floor is genuinely an environment-capability question, not a code question — but A still under-delivers AC-09's HIGH/archetype-S intent, so I want your call before claiming it.

# Developer Answer

<!-- HUMAN_ANSWER -->

Decision: Option B — enable real OS-level containment, then use the sandbox.

The sandbox is wanted. Implement SG-04 / AC-09 / CON-04 with the real unshare/bwrap
mount-namespace jail (not "containment by refusal"), so the walking skeleton runs REAL
child sessions and AC-07 (real deploy-run-reset) and AC-08 (real token/wall-clock cost)
get genuine evidence.

User namespaces are now enabled in the devcontainer (TASK-PROC-054-12): a minimal custom
seccomp profile derived from Docker's default, relaxing only the namespace-creation +
mount-jail syscalls — no --privileged, no seccomp=unconfined, outer wall otherwise intact.
The container has been recreated, so unshare/bwrap can create the jail.

Proceed with the real containment path. Keep the fail-safe (ContainmentUnavailable) as the
guard for any environment where user namespaces remain unavailable.

# Rationale Captured

(Automated archival — no rationale extracted.)
