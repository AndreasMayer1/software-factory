---
task_id: TASK-PROC-061-16
type: impl
parent_requirement: REQ-PROC-061
urgency: 3
urgency_reason: U3-MAINTENANCE
impact: 3
impact_reason: I3-MAINT
status: pending
effort: M
created: 2026-06-03
after: [TASK-PROC-061-07]
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Bump camera 0.11.4→0.12.0+1; update camera_windows_patched fork with stub implementations for new camera_platform_interface abstract methods"
release_description: ""
opus_recommended: false
---
# Goal: Bump camera 0.11.4 → 0.12.0+1 + Update Fork Stubs

## Objective

Apply the approved bump: `camera` from `0.11.4` to `0.12.0+1`. This requires also updating the local fork `packages/camera_windows_patched` to implement any new abstract methods added to `camera_platform_interface` between the fork's pinned interface version and the version pulled in by `camera 0.12.x`.

## Background

Decision rationale: `plans_and_protocols/2026-06-03_01_decisions.md` in TASK-PROC-061-07.

## Breaking Changes Confirmed (from TASK-PROC-061-07 investigation)

**camera package itself:** No breaking changes to `CameraController`, `CameraDescription`, `ResolutionPreset`, or `ImageFormat`. v0.12.0 adds video stabilization (additive); v0.12.0+1 makes `Optional.of` constructor `const`.

**camera_platform_interface** — new abstract methods added across versions (the fork must implement or stub these):

| Version | Addition |
|---|---|
| v2.7.0 | `setImageFileFormat()` |
| v2.9.0 | Streaming support query method |
| v2.10.0 | `CameraLensType` enum |
| v2.11.0 | `VideoCaptureOptions.enablePersistentRecording` flag |
| v2.12.0 | Video stabilization support methods |
| v2.13.0 | `setJpegImageQuality()` |

**Note:** Not all of these may be abstract in the base class — some may have default implementations. The impl task must inspect `camera_platform_interface`'s actual class definition after the bump to determine which methods the fork is required to implement.

## Project Context

- `packages/camera_windows_patched/`: local fork of `camera_windows`, patched to add `CaptureAndDecodeFrame()` for QR scanning.
- The fork declares `camera_platform_interface: ^2.6.0` in its own `pubspec.yaml`.
- Call sites in `lib/` use `CameraController`, `CameraDescription`, `ResolutionPreset` — no API changes to these.

## Steps

1. Update main `pubspec.yaml`: `camera: any` → `camera: ^0.12.0+1` (or keep `any` with a floor constraint via pub.lock)
2. Run `flutter pub get` to resolve — note the resolved version of `camera_platform_interface`
3. Inspect `camera_platform_interface`'s `CameraPlatform` base class for newly abstract methods
4. In `packages/camera_windows_patched/`, implement or add `throw UnimplementedError()` stubs for each required method not yet present
5. Update `packages/camera_windows_patched/pubspec.yaml` camera_platform_interface constraint to match the resolved version
6. Run `dart analyze` — must be clean (no missing override errors)
7. Run `flutter test` — existing camera-related tests must pass
8. Run quality gates (via `verify-quality` skill)

## Acceptance Criteria

- [ ] `camera` bumped to `^0.12.0+1` (or resolved to 0.12.0+1) in `pubspec.lock`
- [ ] `packages/camera_windows_patched/` compiles without missing override errors after adding required stubs
- [ ] All stub methods are marked `// TODO: implement` (not silent no-ops for methods with observable behavior)
- [ ] `dart analyze` reports no new issues
- [ ] All existing tests pass
- [ ] Quality gates green
