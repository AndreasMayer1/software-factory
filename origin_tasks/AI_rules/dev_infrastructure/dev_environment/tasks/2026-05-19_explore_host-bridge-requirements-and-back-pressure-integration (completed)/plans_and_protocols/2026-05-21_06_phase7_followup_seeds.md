# Phase 7 — Follow-up Task Seeds

**Task**: TASK-PROC-054-02
**Date**: 2026-05-21
**Author**: Claude (Opus 4.7), main session

Five follow-up tasks are derived from this task's design and remain explicitly out of its scope. The user invokes `task-create` (or `claude-route`) on each when ready. Goal-statement seeds below.

---

## F1 — Implement the Android-emulator narrow-watcher

**Parent requirement**: REQ-PROC-054 (the optional architecture mentioned in AC-07)
**Type**: impl
**Effort**: M
**Suggested folder**: `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/tasks/2026-MM-DD_impl_android-emulator-narrow-watcher/`

**Goal**: a Windows-side script installed outside the project repository observes a sentinel file inside the project tree and, on detecting it, starts a configured Android Virtual Device on the Windows host. The watcher reads no project files beyond the sentinel's presence, takes no parameters from the container, and produces a result file the container can read for the emulator's IP/port. The watcher's installation, sentinel-file location, supported AVD configuration command, and security properties (does NOT interpret container-controlled inputs in any whitelisted command) are documented in the existing `setup_guides/android_device_setup.md` or a new `setup_guides/android_emulator_setup.md`.

**Acceptance**: with the watcher running, a container-side `touch <sentinel-path>` triggers AVD start; `flutter devices` after AVD boot lists the emulator; the watcher script lives at `~/host-tools/...` (outside the project mount) and is hash-pinned at install time. The pen-test V1–V6 vector classes do not regain reach because the watcher does not execute container-controlled files — only a pre-configured AVD-start command.

---

## F2 — Write the verification_strategy requirement (REQ-PROC-053)

**Parent requirement**: new requirement at the same level as REQ-PROC-054 / REQ-PROC-002 / REQ-PROC-046
**Type**: explore
**Effort**: L
**Suggested folder**: `requirements_tasks/process/AI_rules/verification_strategy/tasks/2026-MM-DD_explore_verification-strategy/`

**Goal**: codify the project's verification approach now that REQ-PROC-054 has defined the *mechanism* on which tests run. Topics: cadence per test type (per-change vs release-cadence), golden-file regeneration discipline (Linux as canonical platform; non-Linux regeneration discouraged), pre-release manual smoke checklist (Windows desktop integration tests, camera-code smoke check, visual regression walkthrough), definition of "release-ready" by target platform, conditions under which a release may ship without Windows-target tests run locally, and the test-coverage matrix per user flow (composing with REQ-NFUNC-023 *Epic: Integration Tests*).

**Acceptance**: a requirements.md exists under `verification_strategy/` with ACs covering cadence, golden discipline, manual smoke checklist, release-readiness criteria, and a release-notes provenance rule for non-supported configurations. REQ-PROC-054's AC-12 forward reference resolves.

---

## F3 — Rewrite / repair the existing integration tests targeting Linux desktop

**Parent requirement**: REQ-NFUNC-023 (Epic: Integration Tests) AND REQ-PROC-054 AC-06
**Type**: impl
**Effort**: XL (likely a parent task with one sub-task per flow)
**Suggested folder**: `requirements_tasks/non-functional/integration_tests/tasks/2026-MM-DD_impl_rewrite-integration-tests-linux/`

**Goal**: the existing integration tests in `flutter_app/integration_test/` are documented as broken (user note from exploration phase). Bring them up to a working baseline targeting the Linux desktop variant under headless Xvfb. Per-flow sub-tasks may emerge from the rewrite. Camera-related integration tests stay manual (the test cannot be automated because it requires a human holding a QR code in front of the camera).

**Acceptance**: `xvfb-run -a flutter test integration_test -d linux` from the project root passes against an agreed set of flows; the surviving integration tests are committed; broken or obsolete tests are either repaired or removed with documented justification.

---

## F4 — Add WSLg / X11 forwarding to the devcontainer (visible Linux app runs)

**Parent requirement**: REQ-PROC-054 (the deferred nice-to-have in §3.5 and the "Common Pitfalls" mention)
**Type**: impl
**Effort**: S
**Suggested folder**: `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/tasks/2026-MM-DD_impl_wslg-integration/`

**Goal**: enable Windows 11 + WSLg developers to launch the Linux desktop variant of the Flutter app from inside the devcontainer with a visible window. Concrete: mount `/mnt/wslg` into the container and set `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR`, `PULSE_SERVER` per Microsoft's published WSLg-in-container recipe. Document fallbacks for Windows 10 (no WSLg; VcXsrv-style external X server).

**Acceptance**: `flutter run -d linux` from inside the container opens a real Linux app window on the developer's Windows desktop on a Windows 11 + recent-WSL setup. Documented in the WSL setup guide; container config changes (devcontainer.json mounts + containerEnv) recorded in the repository for any reader.

**Priority note**: low. The LLM-autonomous loop does not need visible windows — golden tests + screenshot capture in headless Xvfb cover the LLM use case. WSLg is for the human developer's interactive UI work; defer until the developer wants it.

---

## F5 — Refine the requ-explore skill to scaffold companion artefacts

**Parent requirement**: existing skill at `.claude/skills/requ-explore/` (process improvement, no formal parent requirement; could be a new REQ under `process/AI_rules/requirements_management/`)
**Type**: impl
**Effort**: M
**Suggested folder**: `requirements_tasks/process/AI_rules/requirements_management/tasks/2026-MM-DD_impl_requ-explore-companion-artefacts/`

**Goal**: address the gap surfaced during this task — the requ-explore skill currently produces only `requirements.md`, which forces requirement authors to either inline implementation-flavoured content (setup-guide bodies, runbooks) into the requirement or reference docs that do not yet exist. Two design options surfaced:

1. **Companion stubs**: requ-explore optionally scaffolds empty `setup_guides/` or `decisions/` files with frontmatter and a "to be written" body, so the implementation task has structure to fill in.
2. **Plan-suggestion file** (user's framing — likely the better split): requ-explore writes a `plan_suggestion.md` into the exploration task's `plans_and_protocols/` folder that summarizes ideas for the implementation task without putting them in the requirement. Keeps the requirement pure specification; gives the follow-on task a head start.

**Acceptance**: the chosen option (likely #2 per the user's framing) is implemented in the requ-explore skill; the skill emits the new artefact alongside requirements.md; the existing skill documentation is updated; a demonstration task uses the new flow end-to-end.

---

## Suggested ordering

- **F2** before F1, F3, F4 — verification strategy informs what F1 / F3 are tested against.
- **F3** can start once F2 is in flight; the test rewrite is shape-able from the existing tests' subjects.
- **F1** can run in parallel with F3 once the user has the WSL+Mutagen configuration working.
- **F4** is independent; spawn when the developer wants visible Linux windows.
- **F5** is independent of all the above; spawn whenever the requ-explore-skill refinement is the next worthwhile process improvement.

No strict dependency graph; the user prioritises based on what blocks their next concrete work.
