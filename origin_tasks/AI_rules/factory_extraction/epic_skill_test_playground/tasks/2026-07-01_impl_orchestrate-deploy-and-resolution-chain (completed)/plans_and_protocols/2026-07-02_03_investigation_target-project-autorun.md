# Investigation — Running the layer-derivation chain under a deployed harness using the harness's OWN autorun

**Task:** TASK-PROC-068-15 (orchestrate-deploy-and-resolution-chain)
**Date:** 2026-07-02
**Mode:** Read-only investigation
**Question:** When `layer-derivation-start` runs, its unit tasks must be executed by an orchestrator/autorun. In the harness scenario we must drive the **TARGET project's own autorun (the harness's orchestrator), NOT this factory's autorun.** How does dispatch work, is the orchestrator targetable, does a solution exist, and what is the gap?

---

## 1. How the derivation chain starts and dispatches

### 1a. The three skills (all under `.claude/skills/`)

**`layer-derivation-start/SKILL.md`**
- **Plan** (creates ChainState): step 2, lines 30–33 — `python3 scripts/factory/layer_derivation/backfill_orchestration.py plan <spec_path> <chain_state_path>`.
- **Get first directive**: step 3, lines 39–43 — `... backfill_orchestration.py next <chain_state_path>`.
- **Create first unit task**: step 5, lines 50–57. TASK_DIR is a **hardcoded main-factory path**:
  `requirements_tasks/process/AI_rules/factory_extraction/epic_layer_derivation/feat_backfill_orchestration/tasks/$(date)_impl_derivation-unit-${UNIT_ID}` (line 55), with `--req-id REQ-PROC-071-06` (line 52). It writes `goal.md` (a `type: impl` task) + `plans_and_protocols/.gitkeep`.
- **DISPATCH — step 6, lines 61–63** (the load-bearing mechanism):
  > 6. **Start dispatch**:
  > - In automated mode (`CLAUDE_AUTOMATED_MODE=1`): invoke `claude-autorun start` if orchestrator is not already running.
  > - In interactive mode: print "Chain planned. Run `/autorun start` or `/layer-derivation-resume <chain_state_path>` to dispatch the first unit."

**`layer-derivation-resume/SKILL.md`**
- `next` directive: step 2, lines 21–26. Stale-answer resolve: step 3, lines 28–36.
- Create next unit task: step 5, lines 44–52 — **same hardcoded main-factory TASK_DIR** (line 50) + `REQ-PROC-071-06`.
- **DISPATCH — step 6, lines 57–59**: same as start — automated: `claude-autorun start`; interactive: print "Run `/autorun start`".

**`layer-derivation-status/SKILL.md`** — read-only report; no dispatch.

### 1b. What the dispatch actually invokes

The derivation skills **do NOT shell out to `orchestrate.py` directly.** They dispatch by calling the **`claude-autorun` skill** (`start`). `claude-autorun/SKILL.md` Action: start, step 3, line 37:
```bash
nohup python3 -u scripts/automation/orchestrate.py [args] > automation/orchestrate.log 2>&1 &
```
So the chain is: unit-task `goal.md` files land in `requirements_tasks/`, then `orchestrate.py` runs its normal "pick next runnable task → launch a `claude` child session → child runs the task" loop and picks the unit tasks up like any other task. The derivation skills never execute the unit skills themselves — they enqueue task files and hand off to autorun.

**Key coupling:** `claude-autorun` invokes `python3 scripts/automation/orchestrate.py` **relative to the current working directory**, and the unit-task paths are **relative** (`requirements_tasks/...`). Both resolve against whatever cwd the session runs in.

---

## 2. Orchestrator/autorun scoping — is it project-bound or targetable?

**`scripts/automation/orchestrate.py` is NOT parametrically targetable. It self-scopes two independent ways, both bound to the main factory:**

**(a) PROJECT_ROOT derived from `__file__`** — line 87:
```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```
All its bookkeeping is rooted here: `AUTOMATION_DIR`/`STATE_PATH`/`FEEDBACK_DIR` (lines 89–93), the `requirements_tasks` scan (`req_dir = os.path.join(PROJECT_ROOT, "requirements_tasks")`, lines 658, 1006, 1349), and every git/next-task subprocess passes `cwd=PROJECT_ROOT` (lines 975, 987, 1071, 1086, 1099, 1107, 2394, 2794, 2814, 3603, 3621). **Consequence: a *copy* of orchestrate.py at `test_harness_app/scripts/automation/orchestrate.py` self-resolves PROJECT_ROOT to `test_harness_app/` — it self-scopes to wherever the script physically lives.**

**(b) The child `claude` session inherits the orchestrator's process cwd.** The child is launched at line 1801:
```python
proc = deps.popen_subprocess(cmd, stdout=..., stderr=..., text=True, env=env)   # NO cwd= argument
```
There is **no `cwd=`**; the child inherits the orchestrator process's cwd. The env (`_env`, lines 2743–2748) sets only `CLAUDE_AUTOMATED_MODE`, `CLAUDE_CONFIG_DIR=<CCS_ROOT>/<account>`, `CLAUDE_SESSION_ACCOUNT`, `CLAUDE_SESSION_ID` — **no `CLAUDE_PROJECT_DIR` / project-root override.** So the child's project = the orchestrator's launch cwd.

**No CLI escape hatch.** `parse_args()` (lines 3950–4000) exposes only `--accounts`, `--stop-at`, `--min-wait-seconds`, `--max-tasks`, `--hung-check-interval`, `--hung-timeout`, `--session-timeout`. **There is no `--project` / `--target-root` / `--cwd` flag.**

**Two HARDCODED globals that break a naive harness copy:**
- `CCS_ROOT = "/home/vscode/.ccs/instances"` (line 88) — account config dirs; global.
- `JSONL_BASE` (lines 1771–1774) — **hardcoded to the main factory's CCS project name**:
  ```python
  JSONL_BASE = "/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app"
  ```
  Used for hung-session detection at line 1812 (`os.path.join(JSONL_BASE, f"{session_uuid}.jsonl")`). A deployed copy would watch the **main factory's** JSONL dir, not the harness's. (Contrast: `run_skeleton.py._derive_jsonl_dir`, lines 228–241, correctly derives this per-harness by the slash→dash convention — orchestrate.py does not.)

**Summary:** orchestrate.py is targetable-by-relocation (via `__file__` + inherited cwd) but NOT targetable-by-parameter, and it carries two absolute path constants (`CCS_ROOT`, `JSONL_BASE`) hardcoded to the main factory.

---

## 3. Does a solution already exist? — PARTIAL

### What exists
**A single-shot contained harness runner exists** — the playground walking skeleton, `scripts/playground/run_skeleton.py`:
- Deploys, budget-gates, launches **ONE** contained `claude -p` child (`_build_claude_cmd`, lines 216–225), records cost, git-resets. It runs a **single prompt**, not an orchestrator loop / multi-task chain.
- Containment sets cwd to the harness: `scripts/playground/containment.py._build_bwrap_cmd` uses `--chdir harness_dir` (line 167) and binds only the harness (line 166); `scrub_env` redirects HOME/XDG into the harness (lines 247–260). So a *single* child already runs with cwd = harness.

**T-B is created but pending.** `TASK-PROC-068-16 extend-harness-deploy-full-factory` (per this task's protocol `2026-07-02_02`, lines 14–15) will extend `deploy.py` to copy the **whole factory** (scripts + docs), covering **REQ-PROC-068 AC-10** ("A deploy places the *whole* factory into the harness so a contained child session can invoke any factory skill end-to-end … no reach-back to the host"). **Not yet done.**

### What does NOT exist
- **`deploy_candidate` currently copies ONLY `.claude/skills/`** — `scripts/playground/deploy.py`, `_SKILLS_SUBPATH = .claude/skills` (line 24), `shutil.copytree(src, dst)` (line 61). `scripts/` (hence orchestrate.py) is **not deployed into the harness yet** — the harness has no orchestrator copy to self-scope. (T-B closes this.)
- **No harness-scoped multi-task orchestrator loop exists.** Nothing runs `orchestrate.py` (or `claude-autorun`) with the harness as its project. The skeleton runs one child, not the autorun loop.
- **T-C — the task that would close exactly this gap — is NOT YET CREATED.** It is `layer-derivation-reuse-of-deploy` ("`layer-derivation-start` can run its unit skills under the deployed harness so TASK-PROC-068-12 consumes the same mechanism"). Per this task's blocker protocol (`2026-07-02_01`, G2, lines 39–47) and resume protocol (`2026-07-02_02`, lines 22–26, 30–47), T-C is **blocked on decision D3** — whether to ground its new AC ("layer derivation runs under a deployed harness") in **REQ-PROC-071** (derivation engine gains target-root capability — leaning) vs **REQ-PROC-068** (or reuse AC-10, no new AC). That AC does not exist in either requirement yet.
- **TASK-PROC-068-12 (`harness-middle-rederive`)** is the consumer: its "How to Approach" step 2 says run the middle-layer derivation via `layer-derivation-start` (the real skill) with all product content under `test_harness_app/requirements_*` (AC-4). It depends on `[TASK-PROC-071-05-05, TASK-PROC-068-11]` and is to be rewired to also depend on T-C. It cannot run correctly until the harness-targeting mechanism exists.

**Verdict: PARTIAL.** Single-shot contained execution with cwd=harness is built; whole-factory deploy is specced+task-created but unimplemented (T-B pending); the harness-scoped autorun loop and the layer-derivation target-root capability are **entirely missing** (T-C not created).

---

## 4. The concrete gap — what must be built

For `layer-derivation-start` (running for the harness) to dispatch its unit tasks to the **HARNESS's** autorun rather than this factory's, all of the following must hold. Two viable strategies:

### Strategy A — "relocate + inherited cwd" (matches the existing task chain; least invasive to orchestrate.py)
Run the derivation session itself inside the contained harness (cwd = harness), and rely on the deployed factory copy self-scoping.
1. **Deploy `scripts/` (esp. `scripts/automation/orchestrate.py`) + `automation/` scaffolding into the harness.** Currently `deploy.py` copies only `.claude/skills/` (line 24/61). → **T-B (068-16), pending.** Once done, `test_harness_app/scripts/automation/orchestrate.py` self-resolves PROJECT_ROOT = harness (line 87), and a child launched with cwd=harness inherits the harness project (line 1801, no cwd override).
2. **Make the derivation skills' unit-task paths target-relative.** `layer-derivation-start` step 5 line 55 and `layer-derivation-resume` step 5 line 50 hardcode `requirements_tasks/process/AI_rules/factory_extraction/epic_layer_derivation/feat_backfill_orchestration/tasks/...` and `--req-id REQ-PROC-071-06`. In a harness whose product is different, that path/req-id do not apply — the unit-task dir must be rooted in the **harness's own** `requirements_tasks/` tree for the harness product. → **This is T-C's job (not yet created).**
3. **Fix the two hardcoded absolute globals in orchestrate.py** so a harness copy watches the right JSONL and (optionally) the right accounts:
   - `JSONL_BASE` (lines 1771–1774) is pinned to `-workspaces-private-mood-tracker-flutter-app`; a harness copy would watch the wrong dir. Must derive from PROJECT_ROOT via the slash→dash CCS convention (as `run_skeleton._derive_jsonl_dir` already does, lines 228–241).
   - `CCS_ROOT` (line 88) / account rotation are global; decide whether the harness orchestrator reuses the same CCS accounts (likely acceptable) or needs isolation.
   *Note: editing `orchestrate.py` is gated — it is a `scripts/**` change requiring the `claude-write-script` skill and the Python gates.*

### Strategy B — "thread a target-root parameter" (more invasive, avoids relocation)
Add `--target-root`/`--project` to `orchestrate.py.parse_args()` (absent today, lines 3950–4000), replace the `__file__`-derived `PROJECT_ROOT` (line 87) and every `cwd=PROJECT_ROOT` with the parameter, pass `cwd=<target>` to the child popen (line 1801) or set `CLAUDE_PROJECT_DIR` in `_env` (lines 2743–2748), and thread the same target through `claude-autorun start` (which currently hardcodes `python3 scripts/automation/orchestrate.py`, line 37) and through the derivation skills' dispatch (start/resume step 6). Heavier, and still needs JSONL_BASE derivation.

### Blocking assumptions in current code (summary)
- `orchestrate.py` PROJECT_ROOT is `__file__`-bound (line 87) — no param.
- Child launch has no `cwd=` and no project-dir env var (lines 1801, 2743–2748) — child project = launch cwd only.
- `JSONL_BASE` hardcoded to the main factory (lines 1771–1774); `CCS_ROOT` global (line 88).
- No `--project`/`--target-root` CLI flag (lines 3950–4000).
- Derivation skills hardcode a main-factory unit-task path + `REQ-PROC-071-06` (start L52/L55, resume L46/L50).
- `deploy.py` copies only `.claude/skills/` (line 24) — orchestrate.py isn't in the harness yet (T-B pending).

**Bottom line:** The intended design (per the task chain) is Strategy A — T-B copies the whole factory so the contained child sees autorun/orchestrate as its *own* self-scoping copy, and T-C teaches `layer-derivation-start` to author its unit tasks target-rooted and dispatch under that deployed harness. T-B is created-but-pending; **T-C is the missing piece and is not yet created** (blocked on the D3 grounding decision: REQ-PROC-071 vs REQ-PROC-068). Additionally, `JSONL_BASE` (and to a lesser degree `CCS_ROOT`) in orchestrate.py must be de-hardcoded for a relocated copy to self-scope cleanly.
