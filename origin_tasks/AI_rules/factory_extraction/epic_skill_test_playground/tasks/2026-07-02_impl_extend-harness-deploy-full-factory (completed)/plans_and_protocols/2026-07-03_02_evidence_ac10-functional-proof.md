# AC-10 Functional Proof Evidence (EGP archetype F)

Real (non-mocked) run executed 2026-07-03 in this session (session_id
49f95366-4629-4938-81b9-2b2675477080). Scratch harness at
`/tmp/playground-proof-9icQEB` (deleted after the run); never touched the
real `test_harness_app/` (see plan's "Discovered risk" section for why).

## Setup

1. Scratch dir created via `mktemp -d`, `git init` + one commit (`.seed`
   file) — its own independent git repo, `git rev-parse --show-toplevel`
   resolves to itself, not the outer `flutter_app` repo.
2. Host-tree sentinel `/tmp/host-sentinel-068-16.txt` written with
   `host-only secret content`, outside the harness dir.

## Step 1 — real `deploy_candidate`

```
deploy_candidate('/workspaces/private_mood_tracker/flutter_app', '<scratch>')
→ DEPLOY_OK
```

Verified in the deployed scratch tree:
- **Absent** (excluded, as intended): `lib/`, `test/`, `integration_test/`,
  `requirements_user_needs/`, `requirements_tasks/functional/`,
  `requirements_tasks/non-functional/`, `test_harness_app/`.
- **Present** (factory content, correctly copied): `scripts/playground/deploy.py`,
  `.claude/skills/`, `requirements_tasks/process/`, `doc/python/`.
- The scratch harness's own `.git` survived the deploy (`git rev-parse
  --show-toplevel` still resolves to the scratch dir itself) — confirms the
  merge-copy (`dirs_exist_ok=True`, no upfront `rmtree`) does not clobber the
  harness's identity, and the host's `.git` was correctly excluded from
  overwriting it.

## Step 2 — real containment + script-calling skill

Exemplar: `scripts/artifacts/doc_governance.py --list-violations` (anchors on
`Path(__file__).parent.parent.parent`, exactly the failure mode AC-10
exists to close; genuinely invoked by the `doc-split` skill; stdlib-only —
`generate_id_registry.py`, goal.md's suggested exemplar, was tried first but
needs `ruamel.yaml` from `/home/vscode/.local/...`, a path bwrap does not
bind — an environment/dependency constraint of the containment jail's bound
set (`/usr`, `/etc` only), unrelated to deploy correctness).

```
wrap_with_containment(['python3', 'scripts/artifacts/doc_governance.py',
                        '--list-violations'], scratch_harness_dir)
→ ['bwrap', '--unshare-all', '--die-with-parent', ...]  (real bwrap available
   on this host — not the PLAYGROUND_ALLOW_UNCONTAINED bypass)
subprocess.run(contained_cmd, cwd=scratch_harness_dir, env=scrubbed_env)
→ returncode 0, stdout empty (no violations — matches the host's own
  `--list-violations` run, also returncode 0)
```

Completed successfully using **only** the deployed contents.

## Step 3 — negative control (no host reach-back)

```
# Without jail:
subprocess.run(['cat', '/tmp/host-sentinel-068-16.txt'])
→ rc 0, stdout "host-only secret content"

# With jail (wrap_with_containment):
subprocess.run(contained_cmd, cwd=scratch_harness_dir)
→ rc 1, stderr "cat: /tmp/host-sentinel-068-16.txt: No such file or directory"
```

Confirms: the sentinel is reachable from the host, unreachable from inside
the jail — closing "no reach-back to the host factory tree."

## Step 4 — bonus: full deploy→run→reset cycle (safe, since scratch owns its `.git`)

```
git -C scratch status --porcelain   # 28 untracked/modified entries (the deploy)
reset_harness(scratch)              # → RESET_OK
git -C scratch status --porcelain   # → empty (clean)
git status --porcelain              # outer host repo: unchanged, only this
                                     # task's own pre-existing edits — reset
                                     # correctly scoped to the scratch repo
                                     # only, confirming the git-topology
                                     # hazard (see plan) does NOT reproduce
                                     # here because scratch has its own `.git`
```

## Conclusion

AC-10 referent satisfied: a real, non-mocked workflow run in which a
contained child session ran a script-calling factory skill's underlying
script end-to-end inside the harness jail, using only the deployed
contents, completing successfully, with no reach-back to the host factory
tree (verified negative control) — all via the real `deploy_candidate`
implemented in this task.

Cleanup: scratch dir and sentinel file removed after the run; no residue
left in the repository.
