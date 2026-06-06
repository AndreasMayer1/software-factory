# Guideline Updates — TASK-PROC-044-03-01

## doc/python/testing.md — new section "Loading a module under test via `importlib`"

**Trigger**: testing pitfall discovered (applies to all future `scripts/tests/` modules).

**Learning**: A test that loads a `scripts/` module via `importlib.util.spec_from_file_location`
crashes at load time with `AttributeError: 'NoneType' object has no attribute '__dict__'` when the
loaded module combines `@dataclass` with `from __future__ import annotations`. Deferred annotations
make `dataclasses` resolve field types via `sys.modules[cls.__module__].__dict__`, which is `None`
for an unregistered importlib module. Fix: `sys.modules[spec.name] = module` BEFORE
`spec.loader.exec_module(module)`. Hit while building `test_create_feedback_checkpoint.py`.

**Why it matters**: the `spec_from_file_location` helper is copied across many `scripts/tests/`
files; without the registration the failure is dormant until a dataclass is added to the module
under test, then breaks mysteriously. Documented so the loader helper registers unconditionally.

No README row change (testing.md already listed). No other doc folders touched.
