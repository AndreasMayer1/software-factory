---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - claude-commit
  - task-complete
---

# Protocol 27 — Machine resolution consumed: re-derive under TASK-PROC-010-18's reworked guidance

Agent: main session (automated), session ec060365-1ed5-4d49-98ce-cce64740eaf8, account web.

## What the machine resolution said (checkpoint 26)

The AC-4 request from protocol 25 was **withdrawn, not answered** — a machine resolution
(REQ-PROC-041-04 AC-15) authored under `resolves_parked_task: TASK-PROC-068-11` by TASK-PROC-010-18,
which reworked README_3/4 + the `ux-write-persona`/`ux-write-scenario` skills (developer-approved
2026-07-08) after the artifacts sitting at 068-11's AC-4 gate were authored. The four artifacts
exhibited exactly the defects the rework corrects: **leaked method** (R0/R1/R2/T headings, swap-test
write-ups as visible content), no brevity discipline, and — for Maya specifically — a **circular,
tool-referential R0 driver** ("habit preservation through friction minimization"). Resume instructions:
clean-slate the four files, re-deploy so the child runs against the reworked guidance, re-derive via
the real skills with the new output self-check, re-park at AC-4.

## Work done this session

1. **Clean-slated** the four artifacts (`git rm`) per the resume instructions.
2. **Read the reworked README_3/README_4** in full — key changes: method (R0/R1/R2/T, swap-test,
   why-stack, method-anchor jargon) must never appear as artifact content, only as the author's
   private reasoning; output schema is fixed to README_3's six elements / README_4's template; hard
   brevity ceilings (persona body ≤120 lines, scenario body ≤150 lines, excl. YAML); a
   **why-stack/product-independence test** now runs alongside the swap-test specifically to catch a
   driver that bottoms out in the tool/practice/habit itself (exactly Maya's defect).
3. **Discovered the two bugs from protocols 23–25 were independently fixed upstream** by a completed
   bugfix task (`TASK-PROC-068-19`, staged-uncommitted on top of `TASK-PROC-010-18`'s commit — left
   untouched, not mine to commit): `build.py`'s `child_env` now uses real `HOME` (matching my protocol-24
   workaround), and harvest is now a **content-hash diff against a pre-child snapshot**
   (`harvest_authored`/`snapshot_product_definition`, "Option B") — copies back only files the child
   actually created/changed, which fixes the over-broad-harvest bug at its root (safe even with the
   full registry-driven glob set, unlike my protocol-24 narrow-glob workaround). Ran
   `scripts/tests/test_playground_{build,deploy}.py` — 43/43 pass. **Switched to `scripts.playground.build`'s
   own CLI** (`python3 -m scripts.playground.build ...`) instead of continuing with the throwaway
   `/tmp` driver, now that the production tool is correct.
4. **New prompt** (`/tmp/harness_redrive_prompt_v2.txt`): CREATE-mode authoring brief (the 4 files were
   just deleted) restating the fixed facts (names, archetypes, IDs, the completeness-vs-speed value
   conflict), the non-interactive/no-confirmation instruction (still needed — unrelated to the guidance
   rework), and the reworked rules verbatim (no leaked method, both driver tests including why-stack,
   brevity ceilings, no repetition, one memorable anchor woven into prose) with an explicit warning not
   to repeat Maya's specific circular-driver mistake.
5. **Run timed out** at 9m50s (foreground Bash ceiling) — CREATE-mode authoring of 4 files + self-checks
   is more work than the earlier deepen-in-place run and didn't finish in time. The child (and its
   subtree) was killed by the tool timeout before `run_build_mode`'s own harvest step executed, and
   before the driver's `finally: shutil.rmtree` could run — but the isolated workspace + its 77-turn
   JSONL transcript survived on disk, and inspection showed **all 4 files were substantively written**
   (deploy → seed → author-Theo → author-Maya → update-index, per the JSONL's last recorded action) —
   nothing was lost, just not yet harvested/cleaned up by the (killed) driver process.
6. **Manually harvested** the 4 files + the (minor, accuracy-improving) `SCENARIO_INDEX.md` notes edit
   from the leftover isolated dir into `test_harness_app/`, then cleaned up the leftover directory.

## Review + fixes applied on top of the harvested content

Precise body-line counts (excl. YAML) computed programmatically, not via `wc -l` on the whole file
(which over-counts by the YAML header length):

| File | Cap | As-harvested | Notes |
|---|---|---|---|
| `personas/theo/persona.md` | 120 | 84 | clean, no leaked jargon |
| `personas/maya/persona.md` | 120 | 86 (before my edit) | driver still read circular — fixed, see below |
| `theo/.../scenario.md` | 150 | 149 | within bar as-is |
| `maya/.../scenario.md` | 150 | 154 | **4 over** — trimmed |

No leaked-method-jargon hits anywhere in the 4 files' actual body content (a grep for
R0/R1/R2/swap-test/why-stack/objectification/incorporation/SCOT/domestication/etc. across both
persona folders returns only my own `review_history` audit note below, which documents the fix — not
narrative content).

**Fix 1 — Maya's driver, the specific defect this whole cycle exists to correct.** The harvested
"Who is Maya?"/Mental Model still bottomed out as tool/habit-referential ("proof the habit happened",
"the list itself is the value") — an improvement on the old "habit preservation through friction
minimization" in wording, but not in kind. Rewrote to ground the driver in **trusting an immediate,
in-the-moment reaction over any reconstructed/retrospective memory of it** — a genuine why-stack
terminus (still true of Maya even if she tracked nothing at all) that also passes the swap-test (the
same epistemic stance about trusting first impressions over reconstruction is a real, independent
trait, not a restatement of "wants speed"). Bumped `version: 1.0→1.1`, `updated`, added a
`review_history` seq-2 entry naming the defect and the fix (method language belongs in a changelog
audit note, unlike in the narrative body — not a violation of the leaked-method rule).

**Fix 2 — Maya's scenario over the 150-line bar.** Trimmed Act 2's four separately-headed micro-beats
(Opening Notes / Scrolling / Typing / Closing, each with its own header+paragraph) into two merged
beats, shortened the boilerplate "User Flows" and one "Downstream" placeholder line, and re-aligned the
"Why this goal matters" sentence with Maya's corrected driver (it had restated the old
habit/streak framing). Result: 144 lines. Added a matching `review_history` seq-2 entry.

**Files NOT hand-edited beyond the mechanical harvest** (Theo's persona, Theo's scenario, the
`SCENARIO_INDEX.md` notes tweak): reviewed, already compliant, no changes needed — their
`review_history`/`version` are untouched (these are still their first authored version under the
current spec, unlike Maya's persona/scenario which needed a documented post-harvest correction).

## Verification

- `python3 scripts/quality/validate_against_schema.py test_harness_app/requirements_user_needs/SCENARIO_INDEX.md .claude/schemas/scenario_index.yaml` → PASS (no dedicated machine schema exists for `persona.md`/`scenario.md` — conformance there is README-guideline-governed).
- `test_harness_app/requirements_user_needs/_meta/id_registry.md` — unchanged (IDs/folders/status all
  identical to before; no regeneration needed).
- Isolated workspace cleaned up; no stray `/tmp/playground-build-*` directories remain.

## Next step

Re-park for the mandatory AC-4 developer-approval gate — same substance as protocol 25's request, now
against artifacts that actually conform to the current (reworked) spec. Do not self-approve, do not
`task-complete`.
