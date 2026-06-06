---
name: requ-merge
description: Merge all requirements into a single requirements.md file
tools: ["Bash"]
model: haiku
---

Merge all markdown files from `requirements_general_overview/` and `requirements_tasks/` into a single `requirements.md` file in the project root.

**Execute**:
```bash
python3 scripts/artifacts/merge_requirements.py
```

**Output**: Report the number of files merged and confirm the commit.
