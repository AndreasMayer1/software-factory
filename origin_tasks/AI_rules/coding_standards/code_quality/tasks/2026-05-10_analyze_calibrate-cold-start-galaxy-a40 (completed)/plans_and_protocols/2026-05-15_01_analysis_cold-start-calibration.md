# Cold-Start Calibration — Analysis & Protocol

Task: TASK-PROC-046-02
Date: 2026-05-15
Agent: automated session 805864fb-88f9-479b-a36d-5e56086d103e

## Raw Measurements

Device: Samsung Galaxy A40 (SM-A405FN), Exynos 7904, 4 GB RAM
Mode: `flutter run --trace-startup --profile`
Cold-start protocol: force-stop + process kill between each run; screen on; charger connected.
Metric: `timeToFirstFrameRasterizedMicros` from `build/start_up_info.json` (converted to ms)

| Run | ms |
|-----|----------|
| 01  | 5 302.9  |
| 02  | 4 304.9  |
| 03  | 4 485.5  |
| 04  | 4 115.9  |
| 05  | 3 762.9  |
| 06  | 4 261.6  |
| 07  | 5 623.2  |
| 08  | 3 429.8  |
| 09  | 3 776.5  |
| 10  | 4 703.9  |

Raw JSON files archived: `plans_and_protocols/raw/run_01.json` … `run_10.json`

## Statistics

| Statistic | Value    |
|-----------|----------|
| Mean      | 4 377 ms |
| Median    | 4 283 ms |
| p95       | 5 623 ms |
| Max       | 5 623 ms |
| Std dev   | 687 ms   |

(p95 computed via nearest-rank method: rank = ceil(0.95 × 10) = 10 → value = 5 623.2 ms)

## Threshold Decision

Rule applied: **p95 + 30 % headroom, rounded up to the next 250 ms boundary**.

```
p95 = 5 623 ms
p95 × 1.30 = 7 310 ms
Rounded up to next 250 ms → 7 500 ms
```

**Calibrated threshold: 7 500 ms**

Rationale for the statistical rule:
- p95 captures near-worst-case variance without flapping on rare hot-cache hits (which can be 1–2 s faster).
- 30 % headroom accounts for thermal variation, OS background activity, and JIT warmup drift that a 10-run sample does not fully cover.
- 250 ms granularity avoids false precision (the measurement noise is ±~350 ms between runs).

## Why the A40 Measures Much Slower Than the 3 000 ms Estimate

The original 3 000 ms placeholder was derived from Google Play's "slow" classification (≥ 5 s) minus headroom for old hardware. The actual measurements show median 4 283 ms and p95 5 623 ms — more than 40 % above the estimate.

Probable causes:
- **Flutter's startup cost is higher than a native-Android estimate**. The 5 s "slow" baseline is for any Android app; Flutter adds Dart VM init, shader compilation, and first-frame rasterization on top of process start.
- **The A40's Exynos 7904 is a budget 14 nm SoC** (2019). JIT compilation and shader warmup are significantly slower than a flagship SoC. The original estimate underweighted this.
- **The app's startup path is non-trivial** (GetIt service locator, Hive DB init, Argon2 key check). This adds real work before the first rasterized frame.

The persona's broader commitment to worst-case 2017/2 GB devices remains an architectural goal — the gate threshold is set to what the A40 actually does. A future task can optimise the startup path if the threshold is deemed too loose.

## Deliverable Changes

1. REQ-PROC-046 AC-08: updated "≤ 3 000 ms" → "≤ 7 500 ms"
2. G7 table: updated pass condition to ≤ 7 500 ms
3. Reference Test Device section: updated commentary and µs Example
4. Created `doc/testing/cold_start_measurement_methodology.md`
