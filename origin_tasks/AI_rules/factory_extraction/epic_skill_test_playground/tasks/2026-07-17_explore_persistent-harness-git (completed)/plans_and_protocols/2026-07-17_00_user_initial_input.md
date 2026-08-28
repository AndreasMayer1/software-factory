# User Initial Input (verbatim seed)

Captured from the orchestrator prompt that spawned this task. This is the closed, developer-approved
design being applied by this task — preserved here verbatim as the seed record per the file-based
memory rule, even though the task itself performs no open exploration.

---

This is the task-backed tail of a `requ-explore` on REQ-PROC-068 (epic_skill_test_playground). It
establishes **persistent harness git** so the test harness behaves like a real standalone project,
with **encapsulation owned by the playground**.

Edit A — reword AC-11 body. Find the tail of AC-11 (currently ends): "A build/maintain run retains the
derived layers (distinct from a test run's clean reset, AC-07); the transient deployed factory
machinery is absent from `test_harness_app/`." — replace that final sentence with: "A build/maintain
run retains the derived layers (distinct from a test run's clean reset, AC-07); the transient deployed
factory machinery — the skills, scripts, and registries copied in to run the derivation — is absent
from `test_harness_app/`, while the harness retains its own factory-runtime provenance grounding its
product definition (the ideation index and ledger backing a derived decision) as project data of the
standalone harness." Keep the existing EGP inline tail on AC-11 as-is.

Edit B — add two new AC bodies immediately after AC-19:
AC-20: A maintenance (build/maintain) run's deployed copy initializes its git repository by restoring
the harness's persisted history rather than a fresh empty repository, and on harvest the copy's
advanced history is persisted back with the harness in the container project, so a commit reference a
run records (a materialization artifact's provenance commit, a task's pinned requirements version)
stays reachable in every later run. The persisted history retains every commit a harvested artifact
references and omits unreferenced intermediate commits; commits persisted by prior runs are immutable.
A test-mode run, which resets to a clean baseline after each run, carries no persisted history. — EGP:
F; consequence: HIGH

AC-21: The harness's presentation as an ordinary standalone project is established entirely within the
playground deploy/harvest mechanism: durable git history and the harness's own factory-runtime
provenance are provided by the playground, so no other factory mechanism contains handling specific to
the harness being a test fixture — every other mechanism operates on the harness exactly as on any real
project. — EGP: X; consequence: MEDIUM

Edit C — add frontmatter EGP dispositions for AC-20/AC-21, and extend AC-11's existing frontmatter
`egp.referent` to also cover retaining its own factory-runtime provenance as project data.

Design decision context (for the protocol file):
- Mechanism: git bundle-based persistence — maintenance mode restores from a persisted bundle instead
  of `git init`; test mode is unaffected and keeps the throwaway `git init`.
- Compaction policy: preserve every referenced commit; squash unreferenced intermediate commits; prior
  runs' persisted commits are immutable.
- Backward-reference constraint: an artifact can't reference its own commit, so referenced commits must
  survive with stable hashes across compaction — no global squash-and-rewrite.
- Encapsulation invariant: realism (durable git, factory-runtime provenance) is owned entirely by the
  playground; no other factory mechanism special-cases the harness (AC-21).
- This design supersedes earlier options considered during the closed exploration (SHA-rewrite,
  content-hash addressing) and requires no REQ-PROC-074/075 provenance-contract change.
- De-hardcoding precedent already landed at commit 969e3c70.
- Follow-on IMPL tasks to be derived later (not part of this task's scope):
  1. `workspace.py` restore/persist-bundle logic replacing fresh `git init` in maintenance mode.
  2. Harvest-time compaction.
  3. Trivial `deploy.py` `_SUBFOLDER_EXCLUDES` addition of `requirements_user_needs/product_materialization`.
  4. Coordinate sequencing after TASK-PROC-068-27 (shared build.py COMPLETE branch).
