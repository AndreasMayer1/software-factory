# How to apply this license (read before shipping)

You chose **Elastic License 2.0 (ELv2)**, kept **pristine**. The whole point is
that ELv2 is a recognized, unmodified license legal teams already accept — so
the `LICENSE` file is *not* edited. All scope-tightening lives in `NOTICE` and in
per-file headers, which only clarify *what files* the license applies to. They
do not modify the license.

## What ELv2 gives you (matches your intent)

- ✅ Anyone may use, copy, modify, and use it as an internal tool to build
  software/services — **including for their clients**.
- ❌ They may **not** offer it to third parties as a hosted/managed service that
  exposes a substantial set of its features (the anti-SaaS clause).
- ❌ They may **not** strip your copyright/license notices.
- ✅ Automatic termination on violation, with a 30-day cure window — the
  termination clause your custom draft was missing.

ELv2 does **not** auto-convert to open source (unlike BSL). That's why it fits.

## Steps to go live

1. Fill the bracketed fields in `NOTICE` (`[PROJECT NAME]`, `[YEAR]`,
   `[YOUR NAME / ENTITY]`), and list any genuine documentation files that should
   sit *outside* the license. Keep that exclusion list short and explicit — the
   shorter it is, the harder it is to argue a prompt file fell into some
   undefined "docs" gap.
2. Move `LICENSE` and `NOTICE` to the repository root.
3. Add the header below to the top of every crown-jewel `.md` file (prompts,
   personas, agent/skill/orchestration definitions). This stops any single file
   from being recast as stray documentation.
4. Add exceptions to NOTICE

## Per-file header for prompt / persona / skill `.md` files

```
<!-- SPDX-License-Identifier: LicenseRef-Elastic-2.0 -->
<!-- Part of the software licensed under the Elastic License 2.0. Not documentation. -->
```

`LicenseRef-Elastic-2.0` is the correct SPDX form: ELv2 is not on the SPDX
standard license list, and `LicenseRef-` is the convention for non-listed
licenses.

## What this still does NOT protect

Copyright (and therefore ELv2) stops people copying your *files*. It does not
stop someone reading your prompts, learning the method, and writing their own
prompts that do the same thing (the idea/expression line). No license closes
that gap — only staying closed-source or patents would. Keep your defensible
value in the creative whole (the large, structured corpus), not in any single
reusable instruction.
