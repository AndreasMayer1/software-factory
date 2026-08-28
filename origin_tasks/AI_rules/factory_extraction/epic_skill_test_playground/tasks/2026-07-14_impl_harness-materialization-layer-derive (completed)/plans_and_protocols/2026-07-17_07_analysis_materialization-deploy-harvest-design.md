# Analysis — Materialization Deploy-In / Harvest-Out Design (build-mode playground)

Date: 2026-07-17 · read-only design investigation · agent ID candidates: `aa129601e70ef5551` /
`a17b4b3f6ee4fa055` (two subagents active concurrently at spawn — the parallel de-hardcoding agent is
the other; both jsonl updated 18:54).

Owning task: TASK-PROC-068-26. Sibling design task: TASK-PROC-068-27 (degenerate-span/harvest oracle).
Governing requirements: REQ-PROC-068 (playground build/harvest), REQ-PROC-074 (materialization layer).

Read: `scripts/playground/deploy.py`, `scripts/playground/build.py`,
`scripts/playground/acceptance_oracles.py`, `scripts/user_needs/check_materialization_provenance.py`,
`.factory/ideation/index.yaml`, `.factory/registry/artifacts.yaml`, the 068-26 `_05` blocker, the
068-27 goal + context_summary + `_003_analysis`. Verified two-tree git state directly.

---

## Summary

Making materialization deploy-in / harvest-out "possible" needs two independent mechanism edits, both
owned by REQ-PROC-068 / the playground scripts (NOT by 068-27, which explicitly scopes provenance out):

1. **Deploy fix (small, uncontested):** add `requirements_user_needs/product_materialization` to
   `deploy.py::_SUBFOLDER_EXCLUDES` so flutter's own MAT-002 stops leaking into the seeded copy and the
   child authors **CREATE**. No harness-side seed of materialization is needed (there is none yet — that
   is exactly what the run produces).

2. **Harvest-carry (the real work):** build-mode must, on COMPLETE, carry the child's ideation
   **ledger + index entry** out of the discarded copy into a `.factory/ideation/` under `test_harness_app/`
   and commit them alongside the harvested `product_materialization.md`, so the artifact's
   `decided_by: IDEATION-NNN @ <sha>` resolves on the host. Recommended: **Option (a) harvest+rebase the
   ideation ledger + index entry, rewriting the commit ref to the harvest commit.** Options (b) and (c)
   are inferior (b widens the harvest category too bluntly; c/Option-A is a per-run manual workaround).

Verified facts that shape the design (git):
- `test_harness_app/requirements_user_needs/**` **is tracked by flutter_app's git** (33 files).
- `git -C test_harness_app rev-parse --show-toplevel` → `.../flutter_app` — i.e. **git discovery from
  inside test_harness_app resolves to the flutter_app repo.** So `git cat-file -e <sha>` with a derived
  repo root of `test_harness_app` still resolves any commit in flutter_app's history. **Commit
  reachability is already satisfied** once the ledger/index/artifact are committed to flutter_app git.
- `test_harness_app` has **no `.git` and no `.factory`** of its own (confirmed).
- Harness scenarios live at `test_harness_app/requirements_user_needs/personas/{theo,maya}/scenarios/…/scenario.md`.

---

## 1. Deploy fix

### What leaks and why

`deploy_candidate` overlays the whole factory tree onto the seeded copy. `_SUBFOLDER_EXCLUDES`
(deploy.py:127–137) currently excludes `requirements_user_needs/{personas,user_flows,_meta/project}` but
**not** `requirements_user_needs/product_materialization/` (that path post-dates the list). So flutter's
`product_materialization/product_materialization.md` (MAT-002, `decided_by: IDEATION-022 @ a62abcfd`,
refs FLOW-001..004) lands byte-identical in the copy. `ux-write-materialization` Mode-Detection then sees
a present artifact → runs UPDATE/supersession against a **foreign MAT id** instead of CREATE.

Note `product_materialization/` also contains `medium_vocabulary/` (registry category `user-needs`,
`medium_vocabulary.yaml` + `.md` + `.index.yaml`). The medium-vocabulary registry is a *shared authoring
input* (append-only vocab the authoring skill checks against), not product content — but it is
regenerated, and the harness has none. Excluding the whole `product_materialization/` subtree is correct
for leak-containment; if `ux-write-materialization` needs the medium-vocabulary registry present at
runtime, it will create/extend the harness's own (open-vocab-soft is warning-not-error, IDEATION-019), so
excluding it does not break authoring. (Flag this as the one thing to confirm when implementing —
same class of "harness-runtime input?" question the deploy comments already litigate for `_meta/`.)

### Concrete change

In `scripts/playground/deploy.py::_SUBFOLDER_EXCLUDES` add:

```python
os.path.join("requirements_user_needs", "product_materialization"),
```

plus a rationale comment in the same style as the existing block (leak-containment C3, same class as
`personas/` and `user_flows/`; the harness authors its OWN materialization, so flutter's must not seed
the copy). This is a **1-line functional change** (must route through `claude-write-script`).

### Does the harness need its own materialization seeded?

**No.** The purpose of the 068-26 run is to *produce* the harness's first `MAT-NNN` forward from the
approved scenarios. Seeding a placeholder would re-create the exact UPDATE-vs-CREATE hazard. The correct
pre-child state is: **no `product_materialization/` in the copy** → authoring runs CREATE. The deploy
exclude alone achieves this (once the leak is gone, nothing seeds it — `create_workspace` seeds only what
exists under `test_harness_app/`, which has no `product_materialization/`). This means the in-driver
"delete the leaked file in SETUP" workaround from the 068-26 blocker becomes **unnecessary** once the
deploy exclude lands — the exclude is the durable fix; the driver-delete was the stopgap.

---

## 2. Harvest-carry design

### The provenance chain and where it breaks

`check_materialization_provenance.py::check()` resolves, for the artifact's `decided_by: IDEATION-NNN @ <sha>`:
1. `IDEATION-NNN` present in `<index_path>` (default `<root>/.factory/ideation/index.yaml`);
2. `entry.task_path` folder resolvable under `repo_root`;
3. `entry.ledger_path` file resolvable under `repo_root`;
4. `<sha>` reachable via `git cat-file -e` with `cwd=repo_root`;
5. ≥1 `requirements_user_needs/personas/…/scenarios/…/scenario.md` reference in the ledger text that
   exists under `repo_root` (regex `SCENARIO_PATH_RE`, **unanchored** — captures the substring even from a
   `test_harness_app/…`-prefixed path, dropping the prefix).

The parallel agent is de-hardcoding `check()` to take `index_path`/`repo_root` derived from the artifact
path. For a harvested artifact at `test_harness_app/requirements_user_needs/product_materialization/…md`
the derived `repo_root` is `test_harness_app`. Given the git facts above, that resolves:
- **(4) commit reachability → OK** automatically (git discovery walks up to flutter_app's repo).
- **(5) scenario refs → OK** *iff* the ledger references the harness scenarios (the child ran ideation
  over the seeded harness scenarios, so its ledger does; after harvest the substring resolves under
  `test_harness_app`).
- **(1) index, (2) task_path, (3) ledger_path → MISSING** — because they live in the discarded copy's
  `.factory/ideation/` + copy task folder, and `test_harness_app` has no `.factory` and the ledger is
  under `requirements_tasks/**/plans_and_protocols/` which is **never harvested** (category
  `task-workspace`, not in `_PRODUCT_DEFINITION_CATEGORIES`).

So the de-hardcoding fix closes (4) and (5) but **(1)(2)(3) require the harvest to carry the ideation
artifacts and land them where the derived root can see them.** That is the harvest-carry problem.

> Caveat to hand to the parallel agent: how it derives `repo_root` decides everything. If it walks up to
> the nearest `.factory` it will land on **flutter_app** (test_harness_app has none) → then the index/git
> it checks are flutter's, and only Option (c)/Option-A satisfies it. If it derives root = "dir
> containing `requirements_user_needs`" = **test_harness_app**, then Option (a) below satisfies it and a
> `test_harness_app/.factory/ideation/index.yaml` must exist. **These two designs are mutually
> exclusive** — the harvest-carry target must match the check's derived-root rule. This is the one
> hard coupling between the two parallel tasks; it must be reconciled before either lands.

### Option (a) — harvest + rebase the ideation ledger + index entry (RECOMMENDED)

**Mechanism.** Extend `_gate_harvest` / `harvest_authored` (or add a sibling step in the COMPLETE branch
of `launch_and_gate`) that, in addition to the product-definition diff, performs a **materialization
provenance carry** when a `product_materialization.md` is among the harvested files:
1. Read the harvested artifact's `decided_by` → `IDEATION-NNN`.
2. In the copy, look up that entry in `<copy>/.factory/ideation/index.yaml`; read its `ledger_path`
   (copy-relative, under `requirements_tasks/**/plans_and_protocols/…_ideation_ledger.yaml`).
3. Copy the **ledger file** to a durable harness-owned location, e.g.
   `test_harness_app/.factory/ideation/ledgers/<IDEATION-NNN>_ideation_ledger.yaml` (flatten out of the
   copy's task folder, which is never harvested), and **upsert the index entry** into
   `test_harness_app/.factory/ideation/index.yaml`, rewriting `ledger_path` (and `task_path`, or dropping
   it — `check()` only fails task_path if present-and-unresolvable) to the new harness-relative path.
4. Stage + commit the artifact + ledger + index together on the host (the "harvest commit"), then rewrite
   the artifact's `decided_by` sha to that harvest commit's sha (or leave the child's sha — see
   truthfulness below).

**Blast radius.** Net-new: a `.factory/ideation/` tree under `test_harness_app` (first `.factory` there;
harmless, additive). A new harvest sub-step keyed on the materialization artifact — additive to the
existing net-new harvest, does not touch span-1/product-definition diff behavior. Requires build-mode to
know the ideation-index/ledger shape (a light coupling; can be a small helper module, mirroring how
`acceptance_oracles` isolates layer-derivation coupling from build.py core).

**Truthfulness.** High. The ledger and index entry are the *real* child-authored reasoning; they are
carried verbatim, only relocated. The scenario refs resolve to the real harness scenarios. The only
subtlety is the **commit sha**: the child's own sha (in the discarded copy's fresh git) is genuinely
unreachable on the host, so rewriting `decided_by`'s sha to the **harvest commit** (which actually
contains the ledger on the host) is *more* truthful than leaving a dangling copy-sha — it points at the
commit where this reasoning genuinely lives in host history. Document this rewrite in a WHY/rationale.

**What breaks / risks.**
- IDEATION id collision: the copy assigns `IDEATION-NNN` from the *copy's* index (which was deployed
  from flutter's index, excluded? — no: `.factory` is NOT excluded from deploy, so the copy's index is a
  clone of flutter's, and the child's `index_session.py append` picks `next_entry_id` after flutter's
  highest, e.g. IDEATION-024). On harvest into `test_harness_app/.factory/ideation/index.yaml` (a
  *separate, harness-owned* index), that id lives in the harness namespace — fine, but the two-tree ID
  rule (CLAUDE.md §"ID scope") says never aggregate IDs across trees. So the harness ideation index is
  its own namespace; a harvested `IDEATION-024` there is unrelated to flutter's `IDEATION-024`. Acceptable
  and consistent with the two-tree split, but must be stated explicitly.
- The de-hardcoded `check()` must derive `repo_root = test_harness_app` (not walk-up-to-flutter-.factory)
  for this to resolve. **Hard dependency on the parallel agent's derivation rule** (see caveat above).
- `.factory/ideation/index.yaml` is a factory-runtime file; introducing a hand-shaped one under
  test_harness_app should reuse `scripts/ideation/index_session.py` semantics (append/upsert), not a
  bespoke writer (G4 no hand-rolled YAML).

### Option (b) — make `.factory/ideation` a harvestable category for the materialization artifact

**Mechanism.** Add ideation ledger + index to the harvest allowlist (either a new pseudo-category or a
special-case glob) so the net-new diff sweeps them like product-definition files.

**Blast radius.** Larger and blunter. `.factory/ideation/index.yaml` is a **single shared file** cloned
from flutter's into the copy; a content-hash diff would flag the *entire* index as "authored" (the child
appended one entry to a 754-line file) and copy the whole thing back — overwriting/merging flutter's
index into test_harness_app or vice-versa depending on direction. Ledgers live under
`requirements_tasks/**` (task-workspace) which is *deliberately* excluded from harvest (068-19); making
them harvestable re-opens the over-inclusion the net-new baseline diff was built to close. You would
harvest the child's *task folder* too, or special-case just the ledger file — at which point you have
re-implemented Option (a) with worse blast radius.

**Truthfulness.** Same as (a) if done carefully, but the mechanism invites accidental index-merge bugs.

**Verdict.** Rejected as the primary path — it fights the 068-19 net-new-harvest design. Option (a)'s
targeted, artifact-triggered carry is the same intent with a contained blast radius.

### Option (c) — outer-session ideation (blocker's Option A) as fallback

**Mechanism.** Run the medium-selection ideation **in the host flutter_app session** before the child
run, committing the ledger + `.factory/ideation` index entry (referencing the harness scenarios) →
`IDEATION-NNN @ <sha>` reachable in flutter_app git. Feed that id/sha to the child, which authors the
materialization with that `decided_by` and deletes the leaked flutter file.

**Blast radius.** Zero mechanism change; all cost is in the driver + a manual host-side ideation per run.
The provenance then resolves against **flutter's** index/git (so it *requires* the de-hardcoded check to
derive root = flutter, the opposite of Option (a)).

**Truthfulness.** The ledger references `test_harness_app/…` scenario paths from a flutter-namespace
ideation entry — cross-tree, mildly unusual but the blocker judged it acceptable. It also means the
harness materialization's provenance lives in **flutter's** ideation index, not the harness's — arguably
a two-tree-split smell (harness product provenance in the host's factory-runtime).

**Verdict.** Good as a **one-shot unblock** for 068-26 today (no mechanism change), but not the durable
answer: it is per-run manual, and 068-27's synthesis (IDEATION-023) already lists "retires the
068-26/068-12 Option-A workaround" as an intent — so leaning on Option A long-term collides with that
direction. Use (c) only if the developer wants AC-1 satisfied *now* without waiting for the (a) mechanism
task.

---

## 3. Recommendation + change list + ownership

**Recommended path: deploy-exclude (now) + Option (a) harvest-carry (new impl task).**

| # | Change | File / artifact | Owner task/req | Route |
|---|--------|-----------------|----------------|-------|
| C1 | Add `requirements_user_needs/product_materialization` to `_SUBFOLDER_EXCLUDES` + rationale comment | `scripts/playground/deploy.py` | REQ-PROC-068 (playground deploy) — small new impl task, or fold into the (a) task | `claude-write-script` |
| C2 | Materialization provenance-carry step in the COMPLETE harvest branch: copy the child's ideation ledger to `test_harness_app/.factory/ideation/ledgers/…`, upsert the index entry into `test_harness_app/.factory/ideation/index.yaml`, rewrite `ledger_path`/`task_path`, commit + rewrite `decided_by` sha to the harvest commit | `scripts/playground/build.py` (+ small ideation-index helper reusing `index_session.py`) | **New impl task under REQ-PROC-068** (build/harvest mechanism) | `claude-write-script` |
| C3 | Ensure `check_materialization_provenance.py` derives `repo_root`/`index_path` = **the harvested artifact's own project root (`test_harness_app`)**, matching C2's carry target | `scripts/user_needs/check_materialization_provenance.py` | **The parallel de-hardcoding agent already owns this** — must be reconciled so its derivation rule = "dir containing `requirements_user_needs`", not "walk up to nearest `.factory`" | (already in flight) |
| C4 | (Only if Option (c) chosen instead) driver-side host ideation + feed id/sha to child | driver prompt (task-local) | TASK-PROC-068-26 driver | in-task |

**Requirement grounding.** C1 + C2 add new build-mode behavior ("carry materialization provenance across
harvest") not covered by any current REQ-PROC-068 AC. Per the factory rule, this should be grounded in a
new/clarified AC under REQ-PROC-068 (a "harvest carries the materialization provenance so the host-side
provenance check resolves" AC) authored via `requ-explore` before/with the impl task. This is distinct
from 068-27's ACs (which are about degenerate-span disposition + harvestability pre-flight + spec
authoring) — **no overlap**, so it needs its own AC, not a rider on 068-27's edits.

### Interaction with TASK-PROC-068-27 (no collision)

068-27's own context_summary explicitly lists the provenance gap as an **"Adjacent (out-of-scope)
finding … Separate concern from the degenerate-span/harvest defect — noted, not owned by this task."**
068-27 owns: a distinct `VACUOUS` unit disposition, AC-18/19 clarification, a plan-time harvestability
pre-flight, and the spec-authoring surface. **None of those touch deploy excludes or provenance carry.**
The two are complementary and both required for a green 068-26 run:
- 068-27 makes the *degenerate span-0* (persona↔scenario zero-pair) harvestable at all (today it forces
  ESCALATED → oracle False → no harvest → provenance never even gets a chance).
- This design (C1/C2) makes the *harvested materialization's provenance* resolve on the host.

**Sequencing:** 068-27's degenerate-span fix is *upstream* — without it the run never reaches COMPLETE,
so the harvest-carry never fires. The harvest-carry (C2) is only exercised on a COMPLETE harvest. So the
(a) impl task should be ordered **after** 068-27's degenerate-span fix lands (or at least the two must
both land before a real 068-26 build-mode run can go green). Shared touch-point to watch: both modify the
COMPLETE branch region of `build.py`/`acceptance_oracles.py` — schedule the two impl tasks **sequentially**
on `build.py` (disjoint-write rule) to avoid a collision, not parallel.

---

## 4. Impact on TASK-PROC-068-26 AC-1

AC-1: `product_materialization.md` (`MAT-NNN`) authored via `ux-write-materialization`; provenance
resolves (`check_materialization_provenance.py` prints `OK`) — **post-harvest, on the host.**

**Is it satisfiable by pure build-mode harvest today? No.** Two independent blockers stand:
- The degenerate span-0 makes the run un-harvestable (ESCALATED → oracle False) — **068-27's** fix.
- Even if it harvested, the provenance dangles (ledger/index in the discarded copy) — **this design's**
  C2 fix.

**Does the recommended design make AC-1 satisfiable by pure build-mode harvest? Yes — conditionally**, once
**all four** land and are reconciled:
1. 068-27 degenerate-span fix (VACUOUS disposition) → run reaches COMPLETE and harvests.
2. C1 deploy exclude → child authors CREATE (real harness MAT), no foreign-MAT UPDATE.
3. C2 harvest-carry → ledger + index entry land under `test_harness_app/.factory/ideation/` + committed.
4. C3 de-hardcoded check derives root = `test_harness_app` (git reachability + scenario refs already
   resolve there, verified). Then `check()` prints `OK`.

With those, AC-1 is satisfied by a pure build-mode harvest with **no per-run manual Option-A**.

**Minimal viable path if the developer wants AC-1 closed sooner** (before the C2 mechanism task is built):
Option (c)/Option-A — host-session ideation committed to flutter's index + driver-fed id/sha + driver
deletes the leaked file (C1 still recommended to make the delete unnecessary and durable). That closes
AC-1 for 068-26 *now* against flutter's index/git, at the cost of a per-run manual step and a cross-tree
provenance smell, and requires the de-hardcoded check to derive root = flutter for this one artifact. It
should be explicitly framed as a stopgap that C2 retires — consistent with 068-27's stated intent to
retire the Option-A workaround.

**Recommendation to the orchestrator:** do **not** try to close AC-1 via a bespoke per-run hack now.
Land C1 (trivial), open the C2 harvest-carry impl task under REQ-PROC-068 (grounded by a new AC via
`requ-explore`), reconcile C3's derivation rule with the parallel agent, and order it after 068-27's
degenerate-span fix. If 068-26 must show green before C2 is ready, use Option (c) as an explicitly-labeled
stopgap.

---

## Open questions / to confirm at implementation time

- **C3 derivation rule is the load-bearing coupling.** Confirm with the parallel de-hardcoding agent
  whether `check()` derives `repo_root` by "dir containing `requirements_user_needs`" (→ Option a) or
  "nearest `.factory` ancestor" (→ Option c/flutter). Everything downstream depends on this single choice.
- Does `ux-write-materialization` require the medium-vocabulary registry present at runtime? If yes,
  confirm excluding `product_materialization/` at deploy doesn't starve it (it should self-create the
  harness's own, open-vocab-soft = warning-not-error per IDEATION-019).
- The harvested harness ideation index is a **separate namespace** from flutter's (two-tree ID rule).
  Confirm `index_session.py` can target an arbitrary `--index` path under test_harness_app.
- Whether to rewrite `decided_by`'s sha to the harvest commit (recommended, truthful) vs. keep the
  child's copy sha (dangling). Recommend rewrite; document it.
</content>
</invoke>
