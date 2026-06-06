# Third-Party Notices

This file lists third-party components used in this project that require attribution.

---

## han — Claude Code Plugin

**Source:** https://github.com/testdouble/han  
**Author:** Test Double, Inc.  
**License:** MIT  
**Snapshot commit SHA (han `main` HEAD at fetch date):** 8d5cff9bc7d68cc1cf4d22cb18c21a813c94f466  
**File last-touched commit SHA:** 124fb9036ee72224fa1168ca156ed85cbff346b4  
**Adopted:** 2026-05-27  
**Adoption type:** Selective copy (frozen snapshot — not tracking upstream)  
**Adopted file(s):**
- `product/.claude/agents/han-adversarial-validator.md` — adapted from `plugin/agents/adversarial-validator.md`; renamed with `han-` prefix for collision avoidance (REQ-PROC-055 OR-4)

**MIT License text:**

```
MIT License

Copyright (c) 2026 Test Double, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Modification notes:** Renamed `name:` field from `adversarial-validator` to `han-adversarial-validator` in YAML frontmatter. Updated `description:` to reflect explicitly-invoked specialist usage. Content (domain vocabulary, anti-patterns, validation strategies, output format, rules) is verbatim from the source commit above.
