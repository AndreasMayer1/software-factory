# Web Research: Dependency Lifecycle & Admission Gap Analysis

Date: 2026-05-26

---

## 1. Dependency Policies in Privacy-Sensitive Open-Source Projects

### Bitwarden (most documented)
- **Tooling**: Renovate with per-repo `.github/renovate.json5` config
- **Cadence**: Two-week PR cycle; security patches bypass and generate PRs immediately
- **Delay**: 7-day minimum release age before Renovate proposes an update
- **Grouping**: Minor+patch combined into rollup PRs; major updates as individual PRs
- **Approval**: Team-owned repos require assigned team sign-off; shared repos require the team owning each dependency to approve; QA team reviews
- **New deps**: Must be assigned a team owner before merge in shared repos
- **Source**: https://contributing.bitwarden.com/contributing/dependencies/

### Signal
- Minimal public documentation on dependency policy. CONTRIBUTING.md files focus on CLA, code style, and PR process. When dependencies change, acknowledgments files must be regenerated.
- The project appears to rely on internal review processes rather than published automation configs.
- Signal minimizes third-party dependencies heavily (e.g., libsignal is largely self-contained Rust/C).
- **Source**: https://github.com/signalapp/Signal-Desktop/blob/main/CONTRIBUTING.md

### Standard Notes
- No published dependency management policy found. Security policy excludes upstream dependency bugs that are already reported upstream.
- Uses Dependabot alerts (GitHub default).
- **Source**: https://github.com/standardnotes/app/security

### Tutanota/Tuta
- No public dependency management policy found in searches. Their repos do not appear to publish renovate/dependabot configs publicly.

**Key takeaway**: Even among privacy-focused projects, only Bitwarden publishes a detailed dependency governance policy. The industry standard for privacy apps is: (1) 7-day minimum release age, (2) team-based approval for new deps, (3) automated tooling with human gate.

**Confidence**: High for Bitwarden; Low for Signal/Tuta/Standard Notes (policies likely internal).

---

## 2. AI-Agent Governance for Dependency Changes

### OpenAI Codex CLI (most explicit)
- **Default sandbox**: No network access; write limited to workspace
- **Dependency install**: Requires explicit `network_access = true` in config.toml
- **Two-phase model (cloud)**: Setup phase (online, can install deps from manifest) then agent phase (offline by default)
- **Org enforcement**: `requirements.toml` can prevent agents from disabling sandbox
- **Source**: https://developers.openai.com/codex/permissions

### Claude Code (community patterns)
- No built-in hard restriction on `pub add`/`npm install` at the tool level; permissions are filesystem/network-based
- Community CLAUDE.md patterns (awesome-claude-code-toolkit) recommend:
  - Check package maintenance status, download count, issues, last publish date before adding
  - Prefer packages with zero/few transitive deps
  - Require `>1M weekly downloads` and active maintenance
  - Document justification in commit messages
  - Fail builds on critical/high vulnerabilities
- **Source**: https://github.com/rohitg00/awesome-claude-code-toolkit/blob/main/rules/dependency-management.md

### Aider
- No built-in dependency governance. Uses CONVENTIONS.md for standing instructions.
- No sandbox or network restriction layer; operates directly on the filesystem.
- **Source**: https://aider.chat/

### Academic Research (2025)
- "Securing AI Agent Execution" (arxiv 2510.21236): Proposes policy enforcement engine as sandbox enforcing declared permissions; evaluated ~6k MCP servers
- "Architecting Resilient LLM Agents" (arxiv 2509.08646): Advocates "Least Privileged Access" for agents
- No papers found that specifically address dependency-addition as an autonomy boundary

**Key takeaway**: Only Codex CLI has a hard technical boundary (network sandbox). All other tools rely on soft governance via config files (CLAUDE.md, CONVENTIONS.md). No published framework treats "adding a new dependency" as a distinct permission class. This is a gap.

**Confidence**: High for Codex; Medium for Claude Code community patterns; Low for academic coverage of this specific topic.

---

## 3. Package Health Signals Beyond CVE Checks

### Socket.dev (70+ signals)
- **Maintainer signals**: "Unstable ownership" (new maintainer given publish permission), out-of-chronological-order publishing
- **Typosquatting**: Detects names 1-2 chars from popular packages with 1000x download differential
- **Capability analysis**: Detects install scripts, network access, filesystem access, shell execution in package code
- **Dart/pub.dev support**: NOT supported as of 2026. Covers npm, PyPI, Go, Maven, Ruby, Cargo, NuGet
- **Source**: https://docs.socket.dev/docs/faq, https://socket.dev/blog/2025-report-destructive-malware-in-open-source-packages

### Snyk Advisor (0-100 score)
- Four categories: Popularity (downloads, stars), Maintenance (release cadence, recent version in past 3 months), Security (known vulns), Community (contributors, CoC)
- **Dart support**: Snyk Advisor does NOT appear to cover pub.dev packages specifically
- **Source**: https://snyk.io/blog/dependency-health-assessing-package-risk-with-snyk/

### deps.dev (Google)
- Provides dependency graphs, license info, OpenSSF Scorecard scores, advisory info
- **Dart/pub.dev**: Indexed (packages appear on deps.dev with dependency trees and advisories)
- Signals: version freshness, dependency count, known advisories, scorecard (where available)
- Limitation: No behavioral/capability analysis; primarily metadata-based

### pub.dev native signals
- **Pub points** (pana tool): Conventions, documentation, platform support, static analysis, dependency freshness
- **Verified Publishers**: Blue badge, domain-verified identity (e.g., `dart.dev`, `google.dev`)
- **Discontinued flag**: Packages marked by maintainer as unmaintained
- **Security advisories**: Surfaces GitHub Advisory Database warnings during `dart pub get`
- **Limitation**: No maintainer-change alerting, no capability analysis, no typosquatting detection

**Key takeaway for Dart**: The ecosystem is significantly behind npm/PyPI for supply-chain tooling. No Socket.dev or Snyk Advisor coverage. Primary defenses are: pub.dev advisories (reactive, CVE-only), verified publishers (identity only), and deps.dev metadata. There is no Dart-specific tool that detects maintainer takeover or behavioral changes.

**Confidence**: High for Socket/Snyk capabilities; High for pub.dev limitations.

---

## 4. Supply-Chain Incident History & Detection Timelines

| Incident | Year | Attack Vector | Time to Detection | Early Warning Signals |
|----------|------|--------------|-------------------|----------------------|
| event-stream | 2018 | Social engineering of maintainer to hand over repo; malicious dep added | ~2-8 weeks (flatmap-stream published Oct 5; detected late Oct) | New maintainer, new dependency added, minified code hiding payload |
| ua-parser-js | 2021 | Maintainer account compromised | ~4 hours | Versions published outside normal cadence, cryptominer payload |
| colors.js | 2022 | Maintainer self-sabotage (protest) | <24 hours | Infinite loop in code; immediate user reports |
| polyfill.io | 2024 | Domain+GitHub account purchased by malicious actor (Funnull/China) | ~4 months (purchased Feb, detected Jun 25) | Original author warned publicly in Feb; domain ownership change |
| axios | 2026 | Social engineering of maintainer (fake company, fake Teams call, credential theft; DPRK/UNC1069) | ~3 hours | Published at 00:21 UTC Sunday night; new runtime dep `plain-crypto-js` added; out-of-pattern timing |

**Pattern analysis**:
- **Account takeover attacks** (ua-parser-js, axios): detected in hours due to obvious payload
- **Long-con social engineering** (event-stream): weeks to months because payload was targeted and subtle
- **Domain/ownership transfers** (polyfill.io): months because no package-manager-level detection; relied on manual researcher vigilance
- **Common early signals**: (1) new/changed maintainer, (2) new dependencies added, (3) publish outside normal hours/cadence, (4) minified/obfuscated code in source

**Key takeaway**: A 7-day cooldown would have blocked axios, ua-parser-js, colors.js, and the short-lived event-stream window. It would NOT have blocked polyfill.io (CDN, not package manager) or the full event-stream campaign (attacker waited months). The single strongest signal is "new dependency added by recently-changed maintainer."

**Confidence**: High (well-documented incidents with public post-mortems).

---

## 5. Recommended Update Cadence (Standards Bodies)

### NIST SP 800-218 (SSDF v1.1)
- Practice PW.4: "Verify that acquired third-party software components comply with requirements throughout their life cycles"
- Does NOT prescribe a specific cadence (time-based vs event-based)
- Emphasizes: continuous monitoring, provenance verification, SBOM maintenance
- **Source**: https://csrc.nist.gov/pubs/sp/800/218/final

### OpenSSF Scorecard
- "Dependency-Update-Tool" check: Verifies a tool (Dependabot/Renovate) is configured
- Does not enforce specific frequency but implies at minimum weekly or monthly scans
- **Source**: https://github.com/ossf/scorecard/blob/main/docs/checks.md

### Community Consensus (2025-2026)
- **7-day cooldown/minimum release age**: Emerging as baseline recommendation
  - William Woodruff analysis: 8/10 major attacks had windows <7 days; 7-day cooldown blocks 80%
  - Bitwarden uses 7 days; Renovate docs recommend `minimumReleaseAge` of 3-14 days
  - Dependabot cooldown (2025+): configurable per semver level
- **Recommended hybrid strategy for solo/small teams**:
  - Security patches: immediate (bypass cooldown)
  - Minor/patch updates: monthly batch with 7-day minimum release age
  - Major updates: quarterly evaluation with dedicated testing
- **Source**: https://blog.yossarian.net/2025/11/21/We-should-all-be-using-dependency-cooldowns

### OWASP Guidance
- Run dependency scans in CI/CD pipeline after dependency install, before testing
- Minimum cadence: weekly for production; build-time scanning on every change
- Keep vulnerability databases current (NVD feeds refresh daily)
- **Source**: https://owasp.org/www-project-dependency-check/

**Key takeaway for solo Flutter developer**: Monthly update cadence + 7-day minimum release age + immediate security patches is the sweet spot. This matches NIST's "continuous monitoring" principle while being manageable for one person.

**Confidence**: High (multiple converging sources).

---

## 6. Dart/Flutter-Specific Dependency Health Tooling

### Native tooling
| Tool | What it does | Limitation |
|------|-------------|-----------|
| `flutter pub outdated` | Shows outdated deps with resolvable versions | No security info |
| `dart pub get` advisory warnings | Surfaces GitHub Advisory DB during resolution | Reactive only; no health scoring |
| `dart pub deps` | Shows dependency tree | Structural only |

### Third-party Dart tools
| Tool | What it does | Maturity |
|------|-------------|---------|
| `dep_audit` (pub.dev) | Scans pubspec.yaml for outdated/vulnerable/unused deps | Low adoption |
| `cura` (pub.dev) | CLI to audit package health, scores, maintenance status | Newer, limited |
| `osv-scanner` (Google) | Scans lockfiles against OSV database (includes pub advisories) | Production-ready; recommended |
| Dependabot for Dart | Security update PRs for pub packages (since Nov 2022) | Mature; GitHub-native |
| Renovate for Dart | Full dependency update automation | Mature; configurable |

### pub.dev Advisory System (since 2023)
- Uses GitHub Advisory Database as source
- Advisories display during `dart pub get` with affected version and available fix
- Can be suppressed per-advisory via `ignored_advisories` in pubspec.yaml
- Coverage depends on community/maintainer reporting to GitHub Security Advisories
- **No equivalent of `npm audit --fix`** (no auto-resolution command)

### What Dart LACKS compared to npm/cargo/pip
1. No `dart pub audit` command (feature requested: dart-lang/pub#2106, still open)
2. No capability/behavioral analysis (no Socket.dev equivalent)
3. No maintainer-change alerting
4. No typosquatting detection
5. No license compliance scanning built into tooling
6. No lockfile integrity verification beyond pub's own resolution
7. Smaller advisory database (fewer researchers focused on Dart packages)

**Key takeaway**: For a privacy-sensitive Flutter app, the primary defense layers are: (1) osv-scanner in CI, (2) Dependabot/Renovate with minimumReleaseAge, (3) verified publisher preference, (4) manual review of new dependencies using pub.dev scores + deps.dev metadata. There is no automated tool that will catch a maintainer takeover of a Dart package in real-time.

**Confidence**: High (verified against official Dart docs and pub.dev).

---

## Synthesis: Implications for This Project

### Critical gaps in the Dart ecosystem relevant to an offline mental-health app:
1. **No real-time supply-chain threat detection** for pub packages (Socket.dev does not cover Dart)
2. **No automated maintainer-change alerting** (unlike npm where Socket detects "unstable ownership")
3. **Advisory coverage is thin** (Dart advisory database is smaller than npm/PyPI)
4. **AI agent has no hard technical boundary** preventing `flutter pub add` (unlike Codex's network sandbox)

### Recommended mitigations (actionable):
1. **7-day minimum release age** in Renovate/Dependabot config (blocks 80% of attacks)
2. **CLAUDE.md rule**: AI agent must NOT add new dependencies without human approval; updates to existing deps require justification
3. **Monthly update batch**: Review `flutter pub outdated` monthly; apply with 7-day age filter
4. **osv-scanner in pre-commit or CI**: Catches known advisories at resolution time
5. **Verified publisher preference**: Only adopt packages from verified publishers for new deps
6. **Manual new-dep admission checklist**: Pub points >100, verified publisher, >6 months old, <5 transitive deps, active maintenance (commit in last 90 days)
7. **Zero-network-IO advantage**: Since the app has no network, even a compromised dependency cannot exfiltrate data at runtime (defense in depth)

---

## Sources

- Bitwarden Contributing Docs: https://contributing.bitwarden.com/contributing/dependencies/
- Signal Desktop CONTRIBUTING: https://github.com/signalapp/Signal-Desktop/blob/main/CONTRIBUTING.md
- OpenAI Codex Permissions: https://developers.openai.com/codex/permissions
- Claude Code community rules: https://github.com/rohitg00/awesome-claude-code-toolkit/blob/main/rules/dependency-management.md
- Socket.dev FAQ: https://docs.socket.dev/docs/faq
- Socket 2025 Malware Report: https://socket.dev/blog/2025-report-destructive-malware-in-open-source-packages
- Snyk Advisor: https://snyk.io/blog/dependency-health-assessing-package-risk-with-snyk/
- Dart Security Advisories: https://dart.dev/tools/pub/security-advisories
- pub.dev Scoring: https://pub.dev/help/scoring
- Dart/GitHub partnership: https://dart.dev/blog/partnering-with-github-on-supply-chain-security-for-dart-packages
- event-stream post-mortem: https://snyk.io/blog/a-post-mortem-of-the-malicious-event-stream-backdoor/
- axios compromise (2026): https://github.com/axios/axios/issues/10636
- polyfill.io analysis: https://blog.qualys.com/vulnerabilities-threat-research/2024/06/28/polyfill-io-supply-chain-attack
- Dependency cooldowns: https://blog.yossarian.net/2025/11/21/We-should-all-be-using-dependency-cooldowns
- Renovate minimumReleaseAge: https://docs.renovatebot.com/key-concepts/minimum-release-age/
- NIST SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- OpenSSF Scorecard: https://github.com/ossf/scorecard/blob/main/docs/checks.md
- OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/
- Securing AI Agent Execution (paper): https://arxiv.org/pdf/2510.21236
- dep_audit: https://pub.dev/packages/dep_audit
- osv-scanner for Dart: https://medium.com/@yshean/scan-your-dart-and-flutter-dependencies-for-vulnerabilities-with-osv-scanner-7f58b08c46f1
