# scripts/quality/ — quality gate scripts

Pattern- and AST-based gates implementing REQ-PROC-052 (privacy & security
hygiene), the grep-detectable acceptance criteria of REQ-PROC-046
(suppression justification, no leftover debug artifacts), and the six
DCM-replacement gates introduced by TASK-PROC-046-14 (complexity, type
naming, architectural imports, direct styling, test smells, folder
taxonomy). Each gate is run individually or via the aggregate entry point
`check_quality_gates.sh`.

All gates honor the same exclusion mechanism: a path-substring list at
`scripts/quality/exclusions.txt`, optionally overridden per-invocation with
`--exclude-paths <file>`. Exclusion entries should be rare and well-justified
— the gate's value comes from being unconditional.

## Entry point

### `check_quality_gates.sh`

Runs all twelve gates in sequence, streams each gate's full output, then prints a
single PASS/FAIL summary block at the end. Exits `0` if every gate passed,
`1` if at least one gate failed, `2` on a runner error (missing script,
unexpected return code). Intended for use by humans running a quick
local check, by `task-complete` / `task-complete-bugfix`, and (via a future
TASK-PROC-046-11) by the pre-commit hook.

```
scripts/quality/check_quality_gates.sh [--exclude-paths <file>]
```

## Individual gates

### `check_no_network_io.sh`  (REQ-PROC-052 SP1)

Greps `lib/` for the public surface of HTTP / socket / WebSocket APIs:
`package:http/`, `package:dio/`, `package:web_socket_channel`, `HttpClient(`,
`HttpServer.bind`, `Socket.connect`, `ServerSocket.bind`, `WebSocket.connect`,
and related entry points from `dart:io`. The bare `import 'dart:io';` is
intentionally NOT flagged because the same import legitimately provides
`File`, `Directory`, `Platform`, `stdout`, etc. Exits `0` if zero matches in
`lib/`, `1` if any match. Inter-device transfer in this project is QR-only
(REQ-FUNC-007); a network-I/O finding is a contractual gate failure.

### `check_no_telemetry_sdks.py`  (REQ-PROC-052 SP2)

Parses `pubspec.yaml`'s `dependencies`, `dev_dependencies`, and
`dependency_overrides` sections and asserts no entry matches the
forbidden-SDK list. The list — Firebase Analytics, Firebase Crashlytics,
Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag — is
encoded verbatim from REQ-PROC-052 AC-02 as the Python constant
`FORBIDDEN_SDKS` so divergence between the requirement and the gate is
impossible. Exits `0` on a clean pubspec, `1` on any match, `2` if
pubspec.yaml is missing or unreadable.

### `check_no_hardcoded_secrets.sh`  (REQ-PROC-052 SP3)

Regex-scans `lib/`, `test/`, `integration_test/`, `pubspec.yaml`, and
`analysis_options.yaml` for common credential shapes: AWS access keys, PEM /
OpenSSH private-key headers, JWT three-part tokens, generic
`api_key=…` / `client_secret=…` patterns, Google API keys, Stripe live
secrets, Slack tokens, GitHub PATs. If `gitleaks` is on `PATH` it is
preferred. Exits `0` on no candidate matches, `1` on any. False positives
are expected (synthetic test fixtures that look like keys); resolve by
adding the path to `exclusions.txt` with a one-line reason.

### `check_weak_crypto.sh`  (REQ-PROC-052 SP4)

Greps `lib/` for `sha1` / `md5` / `Sha1` / `Md5` from `package:crypto`. For
each match, the script verifies an *adjacent* justification comment exists
within two lines above (or trailing the same line) and contains one of the
recognized non-security purposes (`cache key`, `checksum`, `non-security`,
`integrity`, `fingerprint`, `legacy compat`, …). Per AC-04, weak hashes are
permissible only outside security contexts and only with this justification.
Exits `0` on no unjustified uses, `1` otherwise.

### `check_suppression_justification.sh`  (REQ-PROC-046 AC-11)

Greps `lib/`, `test/`, `integration_test/` for `// ignore:` and
`// ignore_for_file:` directives. For each, requires either (a) a same-line
trailing comment of at least 12 characters of explanatory content, or
(b) a comment line within two lines above carrying that content. The 12-char
minimum is a low bar that filters out empty / whitespace-only comments
without being draconian. Exits `0` if every suppression is justified, `1`
otherwise.

### `check_no_debug_artifacts.sh`  (REQ-PROC-046 AC-12)

Greps `lib/` for three kinds of leftover debug code: bare `print(` (never
appropriate in production code), `debugPrint(` calls without a
`[DIAG-<tag>]` bracketed prefix on the first string argument, and
`// TEMPORARY:` markers. CLAUDE.md's "Bugfix conventions" require both
prefixes — they signal "this is a temporary diagnostic, remove before
`task-complete-bugfix`". Comment lines that merely *mention* `debugPrint`
or `print` in explanatory prose are not flagged. Exits `0` on zero findings,
`1` on any.

The script does NOT consult `automation/state.json` to determine which
bugfix tasks are mid-flight. The accepted limitation: during an active
bugfix, the developer may add the file path to `exclusions.txt` to silence
the gate, then remove it as part of the bugfix's clean-up step.

### `check_complexity.py`  (REQ-PROC-046 AC-02)

DCM-replacement gate for per-function complexity metrics. Shells out to the
Dart helper at `_complexity_analyzer/` (which uses `package:analyzer` to
build the AST), reads its JSON output, and applies these thresholds:

| Metric                          | Threshold |
|---------------------------------|-----------|
| Cyclomatic complexity            | ≤ 20      |
| Parameter count                  | ≤ 4       |
| Source lines of code (body)      | ≤ 50      |
| Max control-flow nesting         | ≤ 5       |

Nesting is control-flow-only (`if` / `for` / `while` / `do` / `switch`);
widget composition and map literals do not contribute, per
REQ-PROC-046 AC-02. Exits `0` on a clean run, `1` on violations, `2` on a
parser / invocation error.

**First-time setup**: inside `scripts/quality/_complexity_analyzer/` run
`dart pub get` once to fetch the `analyzer` dependency. The Python wrapper
emits a `NOTICE` and skips the run if the helper has not been resolved.

### `check_type_naming.sh`  (REQ-PROC-046)

DCM-replacement for `prefer-correct-type-name`. Every `class Foo` under
`lib/` (excluding `*.g.dart` and `*.freezed.dart`) must match
`^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|
(Service)|(UseCase)|(Entity)|(ValueObject))?$`.

### `check_architectural_imports.sh`  (REQ-PROC-046 AC-05)

DCM-replacement for `avoid-banned-imports`. Reads
`architectural_imports_policy.yaml` (path-glob → deny-regex list) and
fails on any import that violates the policy. New rules are added by
editing the YAML, not the script.

### `check_no_direct_styling.sh`  (2026-05-13 K.1)

DCM-replacement for the `ban-name` rule over `ButtonStyle`, `TextStyle`,
`Color`, `Colors.*`, and `ThemeData`. Forbids these constructions inside
`lib/features/`; `lib/core/design_system/` is the canonical home for
direct Material styling.

### `check_test_smells.sh`  (REQ-PROC-046)

DCM-replacement for `missing-test-assertion`, `avoid-empty-test-groups`,
and `prefer-test-matchers`. Three sub-checks against `test/unit/`,
`test/widget/`, and `integration_test/`:

- Missing assertion — a `test(...)` body containing no `expect(`,
  `verify(`, `expectLater(`, `expectAsync*(`, or
  `tester.ensureSemantics(`.
- Empty group — `group(...)` body with zero `test(` / `testWidgets(` /
  `group(` calls.
- Literal expect — `expect(x.length, N)` flagged in favour of
  `expect(x, hasLength(N))`.

### `check_folder_taxonomy.sh`  (REQ-PROC-046 K.2)

Walks `lib/core/domain/` and `lib/features/*/domain/`. Every `.dart`
must live in a sub-folder listed in `folder_taxonomy_allowlist.txt`.
Files directly at `domain/` (no sub-folder) or in an unrecognised
sub-folder name are flagged. Adding a new category is a one-line edit
to the allowlist with a short justification.

## Exit-code convention (all gates)

| Code | Meaning |
|------|---------|
| 0    | gate passed (zero violations) |
| 1    | gate failed (one or more violations); details printed to stdout |
| 2    | invocation error (missing input, can't parse pubspec, etc.) |

The aggregate runner combines individual exit codes: any `1` produces a
final `1`; any `2` produces a final `2`.

## Exclusions

`scripts/quality/exclusions.txt` is the canonical exclusion list. Format:
one path-substring per line, with `#` comments for justification. A path is
excluded if it *contains* any non-comment line as a substring. Each gate
reads this file by default; an explicit `--exclude-paths <file>` argument
swaps it for a different one (useful for one-off scans, never commit a
parallel list).

Treat exclusions as technical debt: the more entries it gains, the less
the gate can guarantee. If a gate's pattern is producing many false
positives, fix the pattern; do not paper over it with exclusions.

---

## Python gates (REQ-PROC-051)

Python quality is enforced by a parallel gate set. Run via:

```
scripts/quality/check_python_gates.sh
```

### `check_python_gates.sh`

Aggregate runner for five Python gates (G1–G5). Mirrors `check_quality_gates.sh`
in shape — one pattern for both language stacks. Exits `0` on all-pass, `1` on
any failure, `2` on runner error.

**Intermediate state**: `develop` currently FAILS G4 and may fail others — the
compliance cleanup that brings `scripts/` to passing is TASK-PROC-051-04. Gate
failures on the develop baseline are expected and documented.

### G1 — `ruff_check.sh` (lint)

Runs `ruff check scripts/` using `pyproject.toml` as the single authority.
Rule selection: pycodestyle (E/W), pyflakes (F), bugbear (B), isort (I),
pyupgrade (UP), simplify (SIM), comprehensions (C4), return (RET), ruff-native
(RUF). Line-length enforcement (E501) is deferred to the formatter.

### G2 — `mypy_check.sh` (type check)

Runs `mypy --config-file pyproject.toml scripts/`. Tier-based strictness:
TIER A modules use `strict = true`; TIER B/C use the lenient baseline
(`check_untyped_defs = false`). Tier-to-module mapping is explicit in
`pyproject.toml` `[[tool.mypy.overrides]]` stanzas.

### G3 — `pytest_check.sh` (tests)

Runs `pytest -q` with collection roots defined in `pyproject.toml`:
`scripts/automation/tests` and `scripts/tests`.

### G4 — `check_no_handrolled_yaml.py` (no hand-rolled YAML)

AST visitor that flags functions or modules containing the two-signature
hand-rolled YAML-frontmatter parser pattern:

1. A string-literal comparison against `"---"` (Compare node)
2. Either a boolean local named `in_frontmatter` / `in_fm` / `frontmatter_started`,
   or a `.split(":", ...)` call on a stripped line

Both must co-occur in the same function scope to flag. The central helper
`scripts/util/yaml_frontmatter.py` is allow-listed and exempt.

**Expected failures on develop** (until TASK-PROC-051-04): `orchestrate.py`,
`generate_status_overview.py`, `generate_id_registry.py`,
`reconcile_dependencies.py`.

### G5 — `check_print_discipline.py` (print discipline)

AST visitor that enforces `print()` discipline:

- Non-CLI modules: any `print()` or `pprint.pprint()` call is a violation.
- CLI modules (`if __name__ == "__main__":` present at top level): `print()`
  is allowed only if the module docstring contains the literal substring
  `Output:` or `Output contract:`.

`sys.stderr.write()` and `sys.stdout.write()` are not flagged.

### Central YAML helper

`scripts/util/yaml_frontmatter.py` — the only permitted place for hand-rolled
YAML boundary detection. Provides `read_frontmatter()`, `update_frontmatter()`,
and `frontmatter_session()` context manager. Uses `ruamel.yaml` for
comment-preserving round-trip.

### Tier annotation system

Every `scripts/**/*.py` module carries a `# tier: A | B | C` header comment
immediately after its module docstring. Gate-runner reads the first 20 lines
to discover the tier; files without the annotation emit a WARNING (not FAIL)
until TASK-PROC-051-04 completes the full-pass annotation.

| Tier | Strictness | Examples |
|------|-----------|---------|
| A    | Full mypy strict; highest review bar | `scripts/automation/orchestrate.py` |
| B    | Lenient mypy baseline; typed where natural | `scripts/util/yaml_frontmatter.py` |
| C    | Minimal enforcement; one-shot CLIs | `scripts/tasks/goal_preview.py` |

### Tooling

Python dev dependencies are pinned in `pyproject.toml` and `uv.lock`.
Install with `uv sync` (or `pip install -r requirements-dev.txt --require-hashes`
as a no-uv fallback). Use `claude-install-os-tool` skill to install `uv` itself.
