#!/usr/bin/env python3
"""Stamp the Elastic License 2.0 per-file header onto Markdown files.

Folder-level _LICENSE_NOTICE.txt markers plus the repository-root NOTICE already
scope every file as "the software". This script is the OPTIONAL extra layer from
SCOPE_AND_HEADERS.md step 3: a per-file SPDX header on crown-jewel .md files so no
single file can be recast as stray documentation.

It is intentionally NOT run as part of the initial export, because the header
would be loaded into LLM context on every skill/agent invocation. Run it later if
per-file headers are ever wanted:

    python3 apply_license_headers.py            # dry run, lists what would change
    python3 apply_license_headers.py --write    # actually prepend headers

Idempotent: files already containing the SPDX line are skipped. README.md and the
notice/license files are never touched.
"""
import sys
from pathlib import Path

HEADER = (
    "<!-- SPDX-License-Identifier: LicenseRef-Elastic-2.0 -->\n"
    "<!-- Part of the software licensed under the Elastic License 2.0. Not documentation. -->\n"
)
SPDX_MARKER = "SPDX-License-Identifier: LicenseRef-Elastic-2.0"
SKIP_NAMES = {"README.md", "LICENSE", "NOTICE", "SCOPE_AND_HEADERS.md", "_LICENSE_NOTICE.txt"}

ROOT = Path(__file__).resolve().parent


def main() -> int:
    write = "--write" in sys.argv
    changed = 0
    skipped = 0
    for md in sorted(ROOT.rglob("*.md")):
        if md.name in SKIP_NAMES or ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        if SPDX_MARKER in text:
            skipped += 1
            continue
        changed += 1
        if write:
            md.write_text(HEADER + "\n" + text, encoding="utf-8")
        print(f"{'STAMP' if write else 'WOULD STAMP'}: {md.relative_to(ROOT)}")
    print(f"\n{changed} file(s) {'stamped' if write else 'to stamp'}, "
          f"{skipped} already had the header.")
    if not write and changed:
        print("Dry run only. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
