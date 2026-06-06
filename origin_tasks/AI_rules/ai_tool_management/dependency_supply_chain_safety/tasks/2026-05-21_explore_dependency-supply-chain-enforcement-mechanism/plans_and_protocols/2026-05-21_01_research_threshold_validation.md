---
type: research_report
task_id: TASK-PROC-056-01
question: "Is 7 days the right minimum-age threshold for dependency intake?"
created: 2026-05-21
---

# Validation of the 7-day Dependency-Adoption Cooldown Threshold

## Bottom-line recommendation

**7 days is well-supported as a defensible default**, sitting at the lower edge of the practitioner consensus range of **3–14 days**. Multiple independent industry analyses converge on the same finding: for ~80–90% of recent npm/PyPI compromises the malicious version was yanked within hours to a few days, so a 7-day window catches the bulk of commodity attacks while keeping bug-fix lag tolerable. The defensible range backed by the cited sources is **3 days (aggressive, ~80% coverage) → 14 days (cautious, ~90%+ coverage)**. 7 days lands roughly at the knee of that curve; 30 days would buy only marginal additional protection and re-introduces patch-lag risk. **Combining the age threshold with an advisory-database check (as REQ-PROC-056 plans) is essential**, because the advisory arm handles the long-dormant cases (xz-utils, Django-log-tracker) that no realistic age window catches.

## Evidence base — detection latency for real incidents

Two independent enumerations of recent compromises agree:

| Incident | Window from publish to yank |
|---|---|
| chalk (2025) | <12 h |
| Nx (Aug 2025) | 4–5 h |
| rspack | 1 h |
| Ultralytics phase 1/2 | 12 h / 1 h |
| num2words | <12 h |
| web3.js | 5 h |
| Axios | 2–3 h |
| LiteLLM, Telnyx SDK, Durabletask | "hours" |
| ua-parser-js (2021) | ~4 h |
| tj-actions (2025) | 3 days |
| Kong Ingress Controller | ~10 days |
| event-stream (2018) | ~2.5 months (historical outlier, pre-Socket/Phylum era) |
| xz-utils (2024) | ~5 weeks (nation-state, build-system implant) |
| Django-log-tracker (PyPI) | ~22 months dormant before weaponisation |

The Yossarian analysis quantifies: **"8/10 attacks had windows of opportunity of less than a week. Setting a cooldown of 7 days would have prevented the vast majority of these attacks from reaching end users."** A 14-day cooldown raises this to "all but 1." The cooldowns.dev analysis reports the same result on a 10-incident sample: **3 days blocks ~80%, 7 days ~90%**.

## Practitioner recommendations

- **Renovate** (`minimumReleaseAge`): docs use 14 days illustratively; the project's `config:best-practices` preset enables a **3-day** default for npm via `security:minimumReleaseAgeNpm`. Liran Tal's Renovate best-practice guidance: **"If you automerge third-party dependencies, we recommend setting minimumReleaseAge to 14 days."**
- **StepSecurity** reference architecture: configurable, example **10 days**.
- **Christian Schneider (industry post)**: explicitly defends **7 days** — "a zero-cost 7-day delay breaks the attacker's time advantage and neutralizes short-lived blast radii easily."
- **cooldowns.dev** (vendor-neutral campaign site): uses **3 days** as the example, "pick whatever number you're comfortable with; even one day makes a real difference."
- **Yossarian (William Woodruff, PyPI maintainer)**: **7 days** baseline, 14 days for higher assurance.
- **OpenSSF / NIST**: no specific numeric minimum-age recommendation found; the OSPS Baseline and NIST CSF 2.0 cover SBOM, signing, and patch hygiene but do not mandate a cooldown value.
- **Academic literature**: empirical studies (arXiv 2309.11021, ACM TOSEM 3705304) characterise malicious-package behaviour and detection models but do not publish a median time-to-disclosure that would pin a single optimal threshold.

## Strongest evidence FOR 7 days

1. **Convergence across independent sources** — Yossarian, Christian Schneider, and StepSecurity all land at 7–10 days from separately compiled incident lists.
2. **Empirical hit rate** — 7 days would have stopped 8 of 10 recent high-profile attacks per Yossarian; cooldowns.dev's 10-attack sample puts 7 days at the ~90% mark.
3. **Detection-window data is short** — the modal "yank within hours" pattern means going beyond ~7 days yields diminishing returns: incidents that survive 7 days (Kong: 10d; tj-actions: 3d edge case; xz-utils: weeks) are dominated by either nation-state implants or build-system attacks that no practical age window stops.

## Strongest evidence AGAINST 7 days (i.e. that it is too short)

1. **Kong Ingress Controller (~10 days)** — would slip past a 7-day window. Argues for 14 days if the project ships infra-touching code.
2. **xz-utils (5 weeks) and long-dormant PyPI accounts (months)** — no age threshold defeats these. *This is the case for the advisory-check arm*, not for a longer threshold.
3. **Renovate's own auto-merge guidance is 14 days**, not 7 — meaning the most opinionated tool vendor doubles the threshold for high-trust contexts.

## Interaction with the advisory-database check

The threshold and the advisory check are **complementary, not redundant**, and the advisory arm is what justifies *not* extending the threshold further:

- The age threshold catches **"new and not yet detected"** attacks — the commodity npm/PyPI wave.
- The advisory check catches **"old but newly disclosed"** cases — long-dormant compromises, retroactive disclosures, xz-utils-style implants.

Because the advisory arm covers the long tail, the age window can be tuned for the short-tail attacks where 7 days already captures ~90%. Pushing to 30+ days would not measurably improve coverage against the advisory-arm's failure modes.

## Caveats

- The "8 of 10" / "~90%" figures come from curated lists of *publicly visible* incidents; they undercount silent or unreported compromises.
- Sample sizes are small (n ≈ 10 in both quantitative sources). Treat the recommendation as "evidence-informed default", not "statistically proven optimum".
- Commodity, financially motivated attackers are typically caught in <72 h; **nation-state actors routinely evade 30+ day windows** (xz-utils). Cooldown alone is insufficient for high-assurance targets.
- 7 days requires an **emergency-bypass mechanism for security patches** — Christian Schneider and Renovate docs both emphasise that cooldowns must not apply to CVE-driven updates.

## Cited sources

1. **Woodruff, W. — "We should all be using dependency cooldowns" (blog.yossarian.net, Nov 2025)** — quantitative table of 10 incidents; explicit defence of 7 days, 14 days for higher assurance.
2. **Schneider, C. — "Dependency cooldowns: a simple supply chain fix" (christian-schneider.net)** — explicit 7-day recommendation, multiple incident timelines (Nx, Axios, LiteLLM, Durabletask).
3. **cooldowns.dev (vendor-neutral campaign)** — 3-day example, 80–90% blocked, 10-attack analysis.
4. **Renovate docs — Minimum Release Age (docs.renovatebot.com)** — 14-day illustrative value; `security:minimumReleaseAgeNpm` 3-day default in `config:best-practices`.
5. **StepSecurity — Mini Shai-Hulud analysis (stepsecurity.io)** — 10-day reference cooldown configuration.
6. **Unit 42 / Palo Alto — Shai-Hulud npm worm coverage (unit42.paloaltonetworks.com)** — Sep 2025 / Nov 2025 wave timelines; hours-to-days exposure windows.
7. **Snyk — event-stream post-mortem (snyk.io/blog)** — 2.5-month detection lag, historical outlier predating modern monitoring.
8. **arXiv 2309.11021 — Empirical Study of Malicious Code in PyPI** — 4,669-sample behavioural study; characterises malicious patterns (no specific median time-to-detection published).
