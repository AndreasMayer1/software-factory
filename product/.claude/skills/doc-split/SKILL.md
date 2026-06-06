---
name: doc-split
description: Split an oversized doc/ guideline file into topic-cohesive parts per REQ-PROC-048
tools: Read, Edit, Write, Bash
model: sonnet
---

You split a single oversized `doc/` guideline file into topic-cohesive output files, satisfying REQ-PROC-048 ACs.

**Invocation**: `"Use doc-split skill on <path>"`

## 1. Read and analyse

Read the source file fully. Identify natural topic boundaries — groups of sections that can be read and applied independently. List the proposed topics and output filenames.

## 2. Decide topology

- **2 output files** → write both into the source file's folder.
- **≥3 output files** → write into a **new subfolder** one level below. Name the subfolder after the common theme.

**Depth guard** (AC-06): Count the path components between `doc/` and the file (e.g. `doc/testing/file.md` = depth 1; `doc/testing/presentation/file.md` = depth 2).
- If depth is already 2 (`doc/X/Y/file.md`): **only the 2-file topology is permitted** — a ≥3-file split would create a level-3 path, which is forbidden. If content truly requires ≥3 files, stop and present to the user: "⚠ level-1 redesign required: `<path>` is already at maximum depth. A peer subfolder under `doc/<X>/` must be introduced before splitting. Plan this as a separate manual redesign task." **Wait for user approval before doing anything further.**
- If depth is 0 or 1: both topologies are allowed. Output the proposed topology and proceed directly to step 3 — no approval gate.

**Summary:** Only pause for user approval when a folder restructuring is required (depth-2 source needing ≥3 outputs). For all other cases, proceed immediately after stating the plan.

## 3. Execute the split

1. **Write output files** — each covering one cohesive topic. Absorb the source file's introductory/overview content into the destination folder's README (≥3-file case) or distribute across the two files (2-file case). Preserve ALL content — nothing may be silently dropped.

1a. **Verify no information lost** (run before deleting source):

   **Word count ratio** (must be ≥ 99%):
   ```bash
   wc -w <source> <out1> [<out2> ...]   # exclude README
   ```
   Sum of output word counts ÷ source word count must be ≥ 0.99.

   **Section heading coverage** (strip numbering before comparing):
   ```bash
   grep -E "^#{1,6} " <source> \
     | sed 's/^#\+ //' | sed 's/^[0-9][0-9.]*[. ]*//' | sed 's/^\*\*Step [0-9]*: //' \
     | while IFS= read -r title; do
         grep -rqF "$title" <output_dir>/ || echo "MISSING: $title"
       done
   ```
   Any `MISSING:` line = dropped content → do not proceed.

   **Code fence parity**:
   ```bash
   src=$(grep -c '```' <source>)
   out=$(grep -rh '```' <output_dir>/ | grep -v README | wc -l)
   [ "$src" -eq "$out" ] || echo "FENCE MISMATCH: source=$src outputs=$out"
   ```

   **If any check fails:** compare source content (read in step 1) against output content (generated in step 1) in your current context — both are already in the context window, no file reads needed. Identify what is missing, fix the affected output file, re-run the failing check. Re-read a file only if the session was interrupted and context was lost.

2. **Delete source file**:
   ```bash
   rm <source_path>
   ```

3. **Update parent README** (AC-02):
   - 2-file case: replace the source file's row with two rows (one per output file).
   - ≥3-file case: replace the source file's row with a single row for the new subfolder.

4. **Create subfolder README** (AC-03, ≥3-file case only):
   Create `<new_subfolder>/README.md` conformant with REQ-PROC-026 §4.5:
   ```markdown
   # <Topic Name>

   ## Purpose
   <What this subfolder contains>

   ## Allowed Content
   <What belongs here>

   ## Forbidden Content
   <What must not go here>

   ## Naming Conventions
   <File naming rules>

   ## Files

   | File | Topic | Read when… |
   |------|-------|------------|
   | `file1.md` | ... | ... |
   ```

5. **Update cross-references** (AC-05):
   ```bash
   python3 scripts/artifacts/update_doc_references.py --find <source_path>
   ```
   Review each match. Determine which output file (or new subfolder) each reference should point to. Then apply:
   ```bash
   python3 scripts/artifacts/update_doc_references.py --replace <source_path>=<new_path> [--replace ...]
   ```
   Run `--find` again to verify zero remaining references.

## 4. Validate

- Each output file: `wc -l <file>` must be < 600.
- No orphan references: `python3 scripts/artifacts/update_doc_references.py --find <source_path>` exits 0.
- No level-3 paths: `python3 scripts/artifacts/doc_governance.py --check-depth` exits 0.
- Output: "Split complete. <N> output files created. All checks passed."
