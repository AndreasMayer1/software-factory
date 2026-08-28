# External Prior Art — How to Evaluate / Test Skills

**What this is:** Distilled reference material on how the wider ecosystem evaluates and tests
LLM "skills" (instruction packs an agent loads on demand). Gathered for TASK-PROC-068-01
(LLM-verifiable testing of open-ended factory skills). This file is intended to survive
without the original pages, so substance and verbatim rubric/checklist content are preserved.

**Sources (fetched 2026-06-21):**
1. `https://agentskills.io/skill-creation/evaluating-skills` — third-party guide on eval-driven skill iteration.
2. `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator` — Anthropic's official `skill-creator` plugin (SKILL.md + eval agents + schemas + scripts).

---

## Source 1 — agentskills.io evaluating-skills

URL: https://agentskills.io/skill-creation/evaluating-skills (title: "Evaluating skill output quality").

Core thesis: "seemed to work once" is not evidence. Run **structured evaluations (evals)** to
learn whether a skill works *reliably* across varied prompts and edge cases, and crucially
**better than no skill at all**. The whole method is a comparative, iterative feedback loop.

### Test-case design

A test case has three parts:
- **Prompt** — a realistic user message ("the kind of thing someone would actually type").
- **Expected output** — a *human-readable description of what success looks like* (not a fixed string).
- **Input files** (optional) — files the skill works with.

Stored in `evals/evals.json` in the skill directory. Example fields per eval:
`id`, `prompt`, `expected_output`, `files`, and (added later) `assertions`.

Tips for good prompts (verbatim guidance):
- "Start with 2-3 test cases. Don't over-invest before you've seen your first round of results."
- "Vary the prompts." Different phrasing/detail/formality — some casual, some precise.
- "Cover edge cases." At least one boundary condition: malformed input, unusual request, or a case where the skill's instructions might be ambiguous.
- "Use realistic context." Real users mention file paths, column names, personal context; "process this data" is too vague to test anything useful.
- Don't define pass/fail checks yet — "just the prompts and expected outputs. You'll add detailed checks (called assertions) after you see what the first run produces."

### Running evals — the comparative core

**The defining pattern: run each test case twice — once WITH the skill, once WITHOUT it**
(or with a previous version). The without-skill run is the **baseline to compare against**.
This is what isolates the skill's *marginal* value rather than the base model's competence.

- **Clean context per run.** Each run starts fresh "no leftover state… ensures the agent follows only what the `SKILL.md` tells it." In Claude Code, subagents give this isolation naturally (each child task starts fresh); without subagents, use a separate session per run.
- **Workspace layout:** results in a sibling `<skill>-workspace/` with one `iteration-N/` dir per pass; within it, one dir per eval, each containing `with_skill/` and `without_skill/` subdirs holding `outputs/`, `timing.json`, `grading.json`; plus an iteration-level `benchmark.json`. Only `evals/evals.json` is hand-authored; the rest is produced during the run.
- **Improving an existing skill:** snapshot the old version (`cp -r`), point the baseline at the snapshot, save to `old_skill/outputs/` instead of `without_skill/`.
- **Capture timing** (`timing.json`: `total_tokens`, `duration_ms`) so the skill's *cost* (extra time/tokens) is weighed against its *benefit* (higher pass rate).

### Writing assertions (what to assert on)

Assertions = "verifiable statements about what the output should contain or achieve." Added
**after** seeing the first outputs ("you often don't know what 'good' looks like until the skill has run").

GOOD assertions (verbatim):
- `"The output file is valid JSON"` — programmatically verifiable.
- `"The bar chart has labeled axes"` — specific and observable.
- `"The report includes at least 3 recommendations"` — countable.

WEAK assertions (verbatim):
- `"The output is good"` — too vague to grade.
- `"The output uses exactly the phrase 'Total Revenue: $X'"` — too brittle; correct output with different wording would fail.

**Explicit limit — what assertions deliberately do NOT cover** (directly relevant to open-ended testing):
> "Not everything needs an assertion. Some qualities — writing style, visual design, whether
> the output 'feels right' — are hard to decompose into pass/fail checks. These are better
> caught during human review. Reserve assertions for things that can be checked objectively."

### Grading outputs

Grading = evaluate each assertion against actual outputs, record **PASS/FAIL with specific
evidence** that *quotes or references the output, not just states an opinion*.

- **Deterministic where possible:** "For assertions that can be checked by code (valid JSON, correct row count, file exists with expected dimensions), use a verification script — scripts are more reliable than LLM judgment for mechanical checks and reusable across iterations." LLM grading is the fallback for the rest.
- `grading.json` records per-assertion `text` / `passed` / `evidence`, plus a `summary` with `passed`/`failed`/`total`/`pass_rate`.

Grading principles (verbatim):
- "Require concrete evidence for a PASS. Don't give the benefit of the doubt. If an assertion says 'includes a summary' and the output has a section titled 'Summary' with one vague sentence, that's a FAIL — the label is there but the substance isn't."
- "Review the assertions themselves, not just the results." While grading, notice assertions that are too easy (always pass), too hard (always fail), or unverifiable (can't be checked from the output alone). Fix them next iteration.

**Open-ended handling — blind comparison (verbatim tip):**
> "For comparing two skill versions, try blind comparison: present both outputs to an LLM judge
> without revealing which came from which version. The judge scores holistic qualities —
> organization, formatting, usability, polish — on its own rubric, free from bias about which
> version 'should' be better. This complements assertion grading: two outputs might both pass
> all assertions but differ significantly in overall quality."

### Aggregating + analyzing

- `benchmark.json` aggregates per-configuration `pass_rate`/`time_seconds`/`tokens` with mean & stddev, plus a `delta` (what the skill costs vs. buys). Heuristic: "+13s but +50pp pass rate is probably worth it; double tokens for +2pp is probably not."
- stddev only meaningful with multiple runs per eval; early on (2-3 cases, single run) focus on raw counts and the delta.

Pattern analysis (verbatim heuristics):
- "Remove or replace assertions that always pass in both configurations" — they don't reflect skill value and inflate the with-skill rate.
- "Investigate assertions that always fail in both configurations" — broken assertion, too-hard case, or checking the wrong thing.
- "Study assertions that pass with the skill but fail without" — that's where the skill clearly adds value; understand *why*.
- "Tighten instructions when results are inconsistent across runs" — high stddev means either a flaky eval (model randomness) or ambiguous skill instructions; add examples / specifics to reduce ambiguity.
- "Check time and token outliers" — read the execution transcript to find bottlenecks.

### Human review (the open-ended catch-all)

> "Assertion grading and pattern analysis catch a lot, but they only check what you thought to
> write assertions for. A human reviewer brings a fresh perspective — catching issues you didn't
> anticipate, noticing when the output is technically correct but misses the point, or spotting
> problems that are hard to express as pass/fail checks."

Feedback must be actionable ("missing axis labels", not "looks bad"); empty feedback = the case
passed review. Stored e.g. in `feedback.json` keyed by eval name.

### Iterating on the skill

Three signal sources feed improvement: **failed assertions** (specific gaps), **human feedback**
(broader quality issues — wrong approach, poor structure, technically-correct-but-unhelpful), and
**execution transcripts** (the *why* — ignored instruction ⇒ ambiguous; wasted steps ⇒ simplify/remove).

Give all three + current SKILL.md to an LLM and ask for proposed changes, with guidelines (verbatim):
- "Generalize from feedback" — fix underlying issues broadly, not narrow patches for the test cases.
- "Keep the skill lean. Fewer, better instructions often outperform exhaustive rules." If pass rates plateau despite more rules, the skill may be over-constrained — try removing instructions.
- "Explain the why. Reasoning-based instructions ('Do X because Y tends to cause Z') work better than rigid directives ('ALWAYS do X, NEVER do Y')."
- "Bundle repeated work" — if every run rewrote a similar helper, bundle it into `scripts/`.

The loop: (1) give signals + SKILL.md to LLM → propose; (2) review & apply; (3) rerun all cases in a
new `iteration-<N+1>/`; (4) grade & aggregate; (5) human review; repeat. **Stop when satisfied,
feedback is consistently empty, or improvements plateau.**

(The page notes Anthropic's `skill-creator` Skill automates much of this loop — see Source 2.)

---

## Source 2 — Anthropic skill-creator plugin

Repo path: `plugins/skill-creator/skills/skill-creator/`. Files actually fetched:

| Path | Purpose |
|---|---|
| `.../SKILL.md` | The skill-creator's own instructions (6-stage workflow). |
| `.../agents/grader.md` | Sub-agent that grades assertions PASS/FAIL with evidence. |
| `.../agents/comparator.md` | Blind A/B comparator between two skill versions (rubric scoring). |
| `.../agents/analyzer.md` | Post-hoc benchmark pattern analyzer. |
| `.../references/schemas.md` | JSON schemas for evals / grading / timing / benchmark / comparison. |
| (directory listings only) `.../scripts/` (`run_eval.py`, `run_loop.py`, `aggregate_benchmark.py`, `generate_report.py`, `quick_validate.py`, `improve_description.py`, `package_skill.py`), `.../eval-viewer/`, `.../assets/` | Automation for running the loop; not fetched in full. |

Raw URL base: `https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/skill-creator/skills/skill-creator/`

### Overall approach (SKILL.md)

A **6-stage iterative workflow**: (1) Capture intent — what it does, trigger, outputs, whether
test cases are needed; (2) Interview & research — edge cases, I/O formats, success criteria;
(3) Write SKILL.md; (4) Test cases — 2-3 realistic prompts → `evals/evals.json`; (5) Run &
evaluate — execute with and without the skill, grade, review; (6) Improve & iterate until satisfied.

Verbatim, the core loop is framed as: "Figure out what the skill is about → Draft or edit the
skill → Run claude-with-access-to-the-skill on test prompts → With the user, evaluate the outputs
→ Repeat until satisfied."

Key gating statement on *when* test cases apply (verbatim, directly relevant to open-ended skills):
> "Skills with objectively verifiable outputs (file transforms, data extraction, code generation,
> fixed workflow steps) benefit from test cases."

Same-turn baseline discipline (verbatim):
> "For each test case, spawn two subagents in the same turn — one with the skill, one without.
> This is important: don't spawn the with-skill runs first and then come back for baselines later."

Assertion-naming guidance (verbatim):
> "Good assertions are objectively verifiable and have descriptive names — they should read
> clearly in the benchmark viewer so someone glancing at the results immediately understands what
> each one checks."

### grader.md — assertion grading rules (verbatim substance)

- **Pass** = "Clear evidence the expectation is true AND the evidence reflects genuine task completion." Evidence must show the output "contains correct content, not just the right filename." Specific, citable evidence required (transcript quotes or output contents).
- **Fail** = no evidence; evidence contradicts; OR "the evidence is superficial — the assertion is technically satisfied but the underlying task outcome is wrong"; or met "by coincidence rather than by actually doing the work."
- **Burden of proof:** "The burden of proof to pass is on the expectation." When uncertain, the expectation gets no credit.
- **Substantive verification:** a file existing with empty content FAILS despite correct naming.
- **False-confidence guard:** "A passing grade on a weak assertion is worse than useless — it creates false confidence." Trivially satisfied assertions are flagged.
- **Dual role:** the grader grades both the outputs AND the evaluations themselves — flags gaps where important outcomes lack a corresponding assertion. Effective assertions are "discriminating: they pass when the skill genuinely succeeds and fail when it doesn't."

### comparator.md — blind A/B for holistic / open-ended quality (verbatim substance)

This is the official mechanism for the *no-single-correct-output* case.

- **Blindness:** outputs are labeled only "A" and "B" with no info about which skill/version produced each, to prevent favoring an approach.
- **Two rubrics, each dimension scored 1-5:**
  - **Content rubric:** correctness, completeness, accuracy.
  - **Structure rubric:** organization, formatting, usability.
  - Dimensions are "adapted to task-specific criteria" (e.g. "Field alignment" for PDFs, "Schema correctness" for data).
- **Holistic scoring beyond the rubric:** strengths, weaknesses, and an overall **1-10** quality rating; it judges subjective qualities ("Professional, polished" formatting, "Easy to use" usability) "through criterion-based assessment rather than impression."
- **Bias avoidance:** blind to source identity; "Output quality first: Assertion scores are secondary to overall task completion"; avoids style preferences, focuses on correctness/completeness.
- **Winner selection priority:** (1) overall rubric scores (content + structure averaged to 1-10); (2) expectation pass rates (secondary); (3) tiebreaker (rare). "Be decisive" with evidence-based reasoning.
- Output schema `comparison.json`: `winner` ("A"/"B"), `reasoning`, `rubric` (per-output content/structure sub-scores + `content_score`/`structure_score`/`overall_score`), `output_quality` (per-output 1-10 `score` + `strengths`/`weaknesses`), and `expectation_results` (per-output pass counts).

### analyzer.md — benchmark pattern heuristics (verbatim substance)

Per-assertion patterns across with/without configs:
- always pass both ⇒ "may not differentiate skill value";
- always fail both ⇒ "may be broken or beyond capability";
- pass-with / fail-without ⇒ "skill clearly adds value here";
- fail-with / pass-without ⇒ "skill may be hurting";
- highly variable ⇒ "flaky expectation or non-deterministic behavior".

Diagnoses flaky evals by variance ("50% ± 40%" flags run anomalies); reports cost-benefit
tradeoffs and bottlenecks. **Constraint:** the analyzer does NOT propose skill improvements during
benchmark analysis — that belongs to the separate comparison/improvement phase.

### schemas.md — data structures

- **`evals.json`**: `skill_name`, then `evals[]` each with `id`, `prompt`, `expected_output`, `files[]`, `expectations[]` (note: in the official schema the assertion array is called `expectations`, e.g. "The output includes X", "The skill used script Y").
- **`grading.json`**: `expectations[]` (`text`/`passed`/`evidence`); `summary` (`passed`/`failed`/`total`/`pass_rate`); `execution_metrics` (tool_calls breakdown, total_steps, errors, output/transcript chars); `timing`; `claims[]` (extracted facts with `type`/`verified`/`evidence`); `user_notes_summary` (`uncertainties`/`needs_review`/`workarounds`); `eval_feedback.suggestions[]` (assertion + reason to fix it).
- **`timing.json`**: `total_tokens`, `duration_ms`, plus ISO start/end timestamps and durations for the executor and grader phases separately.
- **`benchmark.json`**: `metadata` (skill, models, `runs_per_configuration`, evals run), `runs[]` (per eval/config/run with `result` metrics + per-expectation detail + `notes`), `run_summary` per config (mean/stddev/min/max for pass_rate/time/tokens) and `delta`. Configuration strings must be exactly `"with_skill"` / `"without_skill"`.
- **`comparison.json`**: as described under comparator above.

---

## Relevance to TASK-PROC-068-01 (open-ended skill testing)

- **Assert-on-process vs content-correctness is explicitly first-class here.** The official `expectations` schema includes assertions like *"The skill used script Y"* — i.e. asserting on *what the agent did* (process/tool-use), not only on output content. The `grading.json.execution_metrics` (tool_calls, steps, errors) further makes process inspectable. This directly supports our "assert on process" idea: for open-ended skills where output content has no single right answer, you can still assert on observable process behaviors (which references were read, which gates ran, which structure was produced).
- **Both sources draw a hard line between "objectively verifiable" and "feels right" qualities — and only the former get assertions.** agentskills.io: "Reserve assertions for things that can be checked objectively"; skill-creator: test cases benefit "Skills with objectively verifiable outputs." This is exactly the boundary our task lives on: most factory skills (requ-explore, ideation, ux-create-flow) produce open-ended artifacts, so a pure-assertion approach is, by the sources' own framing, insufficient.
- **Deterministic-vs-LLM-judged is an explicit recommended split.** "For assertions that can be checked by code… use a verification script — scripts are more reliable than LLM judgment for mechanical checks." LLM grading is the fallback. Maps cleanly to a tiered playground: deterministic checks (schema valid, file present, section exists, frontmatter well-formed) first; LLM-judge only for the irreducibly semantic checks.
- **The official open-ended answer is the BLIND COMPARATOR with an ANCHORED RUBRIC, not free scoring.** comparator.md scores six named dimensions 1-5 (correctness/completeness/accuracy + organization/formatting/usability), each "adapted to task-specific criteria," plus a 1-10 holistic score with required strengths/weaknesses. This is the strongest external precedent for *anchored-rubric LLM judging* of open-ended outputs — and it is deliberately **relative** (A vs B), not absolute.
- **Golden / reference runs appear in a specific, comparative form — "baseline" and "previous version snapshot," not a fixed golden output.** The reference is "the same prompt without the skill" or "the snapshotted prior skill version." Nobody asserts equality against a canonical golden artifact; they assert *relative improvement* (delta pass-rate, A-beats-B). For open-ended factory skills this is the usable notion of a golden run: keep a reference version and require non-regression, rather than diffing against one blessed output.
- **Reliability is measured by repetition + variance, not a single pass.** High `stddev` across runs is treated as a first-class signal (flaky eval OR ambiguous skill). For open-ended skills whose LLM judging is itself noisy, this argues for multiple runs per case and explicitly tracking judge variance — a property our playground should bake in.
- **"Discriminating assertion" is the central quality bar and a reusable design rule.** grader/analyzer both demand assertions that pass-with / fail-without; assertions that pass in both configs are pruned. For open-ended tests this is the antidote to vacuous checks: every check must be one a no-skill (or worse-skill) baseline would actually fail. Our playground should auto-flag non-discriminating checks the same way.
- **False-confidence is named as the primary failure mode.** "A passing grade on a weak assertion is worse than useless." This is the risk we most need to guard against when testing open-ended skills with soft/LLM checks — a green test that proves nothing. The mitigation in both sources: require *concrete cited evidence* for every PASS, and grade the assertions themselves, not just the outputs.
- **WHERE THE EXTERNAL SOURCES DON'T COVER US (useful gaps):**
  - Neither source gives an *absolute, single-output* rubric for an open-ended artifact judged on its own — the open-ended path is always *comparative* (A/B or with/without). Our task may need absolute anchored rubrics (a flow/requirement judged good in isolation), which is beyond their precedent.
  - Both are oriented to skills with **file/data outputs** (CSV, PDF, charts, code). They give no guidance on testing **conversational / decision-routing / interview-style** skills (e.g. product-intake, ideation phases) whose "output" is a sequence of questions, classifications, or routing decisions rather than an artifact.
  - No treatment of **process-conformance against a documented method** (e.g. "did requ-explore actually run Phase 0 eligibility and the four tripwires?") — they assert on tool-use only opportunistically, not against a normative process spec. Our factory skills are method-defined, so process-conformance grading is a genuine extension we'd have to design.
  - No notion of **rubric anchors with concrete examples per score level** (their 1-5 is unanchored beyond the dimension name). For reproducible LLM judging of factory artifacts we likely need anchored level descriptors, which the sources leave to the judge's discretion.
