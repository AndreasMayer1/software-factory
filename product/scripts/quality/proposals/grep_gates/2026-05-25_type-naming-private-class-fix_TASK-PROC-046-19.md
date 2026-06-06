---
proposal_id: type-naming-private-class-fix
proposal_type: grep_gates
proposed_at: 2026-05-25
proposed_by_model: claude-opus-4-7
source_task: TASK-PROC-046-19
status: applied
---

## Change applied

`check_type_naming.sh` modified to:
1. Skip private classes (name starts with `_`) — standard Dart/Flutter convention
2. Skip `*.config.dart` files alongside `*.g.dart` and `*.freezed.dart`

This implements the proposal filed as `2026-05-24_type-naming-allow-private-classes_TASK-NFUNC-002-02.md`.

## Effect

16 type-naming violations eliminated. All were private classes (`_FooState`,
`_ScannerBody`, `_DataBeamTimerTicked`, etc.) or generated code
(`_AppLocalizationsDelegate`, `_` in `injection_container.config.dart`).
