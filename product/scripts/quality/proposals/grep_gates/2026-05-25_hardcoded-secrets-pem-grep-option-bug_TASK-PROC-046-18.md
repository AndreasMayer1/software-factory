---
proposal_id: hardcoded-secrets-pem-grep-option-bug
proposal_type: grep_gates
proposed_at: 2026-05-25
proposed_by_model: claude-sonnet-4-6
source_task: TASK-PROC-046-18
status: pending_review
---

## Reason

`check_no_hardcoded_secrets.sh` stores patterns as `"LABEL|regex"` strings and
passes the regex portion directly to `grep -rEnI`. Two patterns start with
`-----` (five dashes):

```bash
"PRIVATE_KEY_PEM|-----BEGIN ((RSA|DSA|EC|OPENSSH|PGP) )?PRIVATE KEY-----"
"SSH_PRIVATE_KEY|-----BEGIN OPENSSH PRIVATE KEY-----"
```

When bash expands `"$regex"` after the `--include=...` options, grep receives
a word starting with `--`. POSIX and GNU grep treat `--` as the end-of-options
sentinel: everything after `--` is treated as a positional argument (file
path), not as the pattern. The pattern is therefore never applied, and PEM
private-key headers in source files pass the gate silently.

Confirmed in tests: `test_check_no_hardcoded_secrets.py` →
`test_pem_private_key_header_flagged` is marked xfail (strict=True) and
succeeds in confirming the failure.

## Impact

High (security): RSA/EC/OpenSSH private-key PEM headers embedded in source
code are not detected. SP3 gate gives false confidence for the most critical
credential class.

## Proposed change

Prefix the `grep` pattern argument with a `--` end-of-options guard to
isolate patterns that begin with `-`:

```bash
grep -rEnI --include="*.dart" ... -- "$regex" "${TARGETS[@]}"
```

The `--` before `$regex` tells grep to treat all subsequent arguments as
positional (pattern + files), regardless of leading dashes. This is the
standard POSIX fix for this class of bug and requires no logic change to the
pattern array.

Alternatively, use `grep -e "$regex"` (the `-e` flag explicitly marks its
argument as a pattern):

```bash
grep -rEnI --include="*.dart" ... -e "$regex" "${TARGETS[@]}"
```

Both approaches fix the PEM and SSH patterns without affecting any other
patterns in the array.
