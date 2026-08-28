# Protocol 09 — CCS auth inside the jail: findings + pending design decision

Task: TASK-PROC-068-11 · 2026-07-04 · developer-directed (interactive).

## Done this session (verified)
- **containment.py `--share-net`**: jail keeps network (child claude reaches api.anthropic.com);
  CON-04/AC-09 (mount-namespace filesystem isolation) unaffected. Regression test added.
- **Ephemeral workspace + deploy exclude fix + reset own-repo guard** (agent, protocol 08):
  workspace = sibling of host project under parent folder; deploy → git-init → run → reset →
  `finally: destroy_workspace`. Catastrophe guards proven (reset refuses non-own-repo;
  destroy refuses non-`playground_ws_` paths). 112 playground tests green.
- **Live smoke test** (`run_skeleton`): whole mechanism works end-to-end and safely — workspace
  created, whole factory deployed (82 skills), git baseline, contained+networked child launched,
  cleanup ran on the error path, outer repo untouched, no leak.

## Child-auth investigation
- Child failed only with `"Not logged in · Please run /login"`. Root cause: creds live at
  `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/web/.credentials.json` (OAuth token:
  claudeAiOauth.{accessToken,refreshToken,expiresAt,...}), which is OUTSIDE the jail.
- **CCS model**: multi-account manager. Accounts = instances under `~/.ccs/instances/`
  (`web`,`gmail`,`gmail2`). Active account selected via `CLAUDE_CONFIG_DIR`. `claude` talks
  DIRECTLY to the API with the OAuth token (instance settings.json sets no base URL/proxy).
  `orchestrate.py` hardcodes absolute `/home/vscode/.ccs/instances` + shared context-groups path.
- `~/.ccs` is container-local (NOT a mount); but `~/.claude` (+ container-backup/windows_mirror)
  ARE 9p bind-mounts from the Windows host. `~/.ccs/shared/{agents,commands,skills,plugins,settings.json}`
  are symlinks → `~/.claude/{...}`.

## Developer constraints (this session)
- Do NOT copy the (huge) JSON anywhere.
- `orchestrate.py` must run `ccs` inside the jail → real CCS machinery must be present + functional.
- Must ALSO work for native `claude` (CCS-independent fallback).
- OK for skills-under-test to read auth (trusted use case = testing new skills).
- Want ALL ccs accounts available inside.

## CRITICAL incident + lesson
- Probed `--bind ~/.ccs` (READ-WRITE) alone + HOME=/home/vscode. `ccs version` inside the jail
  ran its auto-recovery and **DELETED** real `~/.ccs/shared/{commands,skills,agents}` symlinks —
  because their targets (`~/.claude/*`) were ABSENT in the jail (we bound `~/.ccs` but not `~/.claude`),
  so ccs judged them "broken" and removed them from the REAL dir.
- **Repaired**: manually restored agents/commands/skills → `~/.claude/<name>`; then `ccs doctor --fix`
  restored plugins + settings.json. `ccs doctor` now clean: 4 profiles intact, symlinks healthy.
  (Remaining doctor warnings — Delegation not installed, Image Analysis — are pre-existing/unrelated.)
- **Lesson (design constraint)**: to run `ccs` in the jail you MUST bind the whole consistent set
  (`~/.ccs` AND `~/.claude`) so no symlink target is missing; a partial view makes ccs "repair"
  (damage) the real tree. Also: an rw bind lets the jail mutate the real dirs.

## CoW feasibility probes (to avoid mutating real dirs without copying) — ALL NEGATIVE
- `bwrap --tmp-overlay` / any `--overlay`: **unsupported** by this bwrap build.
- Unprivileged overlayfs via `unshare -Urm; mount -t overlay`: **fails** (not permitted here).
- `fuse-overlayfs`: **not installed**.
→ No off-the-shelf copy-on-write. Getting CoW would require installing `fuse-overlayfs`
  (dependency admission, REQ-PROC-060 → developer approval).

## PENDING DECISION (for the developer)
How the jail gets working ccs + native claude auth, given no-copy + no-CoW:
- **(A)** rw-bind `~/.ccs` + `~/.claude` (both, at real paths). Works for ccs + native claude;
  symlink web consistent so no destructive recovery. Tradeoff: jail WRITES into real `~/.ccs`
  (session-history pollution; buggy skill could in principle touch config).
- **(A-CoW)** Install `fuse-overlayfs` (needs approval) → bind real dirs as read-only lower +
  workspace-local writable upper → real dirs NEVER mutated, no big-file copy. Cleanest if approved.
- **(C)** For the current milestone only (author harness anchors) use native `claude` auth via a
  minimal bind of `~/.ccs`+`~/.claude`; defer full in-jail `ccs`/orchestrator to a later milestone.

## Safety rule adopted
No more live `ccs`-in-jail experiments against the REAL `~/.ccs` — test any bind/overlay approach
against a THROWAWAY COPY first (the rw-bind incident above must not recur).

## Not committed
containment.py + workspace.py + deploy.py + reset.py + run_skeleton.py changes and tests remain
uncommitted pending the auth-design decision and a final green live smoke run.
