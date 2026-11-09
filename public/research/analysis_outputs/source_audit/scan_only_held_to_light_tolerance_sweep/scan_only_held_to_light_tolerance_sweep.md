# Scan-Only Held-To-Light Tolerance Sweep

Scope: use only `magazine.pdf` embedded scanned pages to test whether a small registration tolerance around the physically valid page 75 -> page 76 held-to-light relation creates a target-specific unit/order cue. No key derivation, OCR-to-key extraction, hashing, seed/WIF/address checks, or broad brute force were run.

- Created: `2026-05-25T06:38:30`
- Sheet: `analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep/scan_only_held_to_light_tolerance_sweep_sheet.jpg`
- Source page: `75` back-side source
- Target page: `76` front-side target
- Orientation: embedded pages rotated `180` degrees to readable/upright, then page 75 was horizontally mirrored.
- Registration grid: dx `-80..80` step `20`, dy `-80..80` step `20`, rotation `-1.0, +0.0, +1.0` degrees.
- Modes checked: `243`.
- Controls scored per mode: `256`.

## Best Mode

- Best transform: `rot=-1.0, dx=-80, dy=-20`.
- Active boxes at or above 10% source-only ink: `0/4`.
- Active boxes above same-size nearby-control p95: `0/4`.
- Mean source-only coverage: `0.014194`.

| target | phrase | source-only coverage | control p95 | percentile | above p95 |
|---|---|---:|---:|---:|---|
| `O4` | buying the dip | `0.000089` | `0.410635` | `0.125` | `False` |
| `B4` | $1 billion | `0.000000` | `0.091700` | `0.672` | `False` |
| `G5` | Volcano Bonds | `0.051694` | `0.264589` | `0.562` | `False` |
| `O5` | shitcoiner at heart | `0.004992` | `0.263116` | `0.328` | `False` |

## Natural Mode Comparator

- Natural transform: `rot=+0.0, dx=+0, dy=+0`.
- Natural active >=10%: `0/4`.
- Natural active above control p95: `0/4`.
- Natural mean source-only coverage: `0.003298`.

## Sweep Findings

- All-four signal candidate modes: `0`.
- All-four >=10% source-only modes: `0`.
- All-four above control p95 modes: `0`.
- Source-backed R3 unit/order bridge from strict/context/line-band gates: `0`.
- Selector unlocked: `False`.
- Fingerprint: `pair=75->76|grid=dxdy+-80x20,rot=-1/0/+1|modes=243|controls=256|all4Signal=0|all4Ge10=0|all4GtP95=0|bestGe10=0/4|bestGtP95=0/4|sourceR3=0|selectors=0`.

## Adversarial Review

- Blocking findings: `0`.
- Verdict: `pass review`.
- Review checked cherry-picked grid/opacity/thresholds, control comparability, unprimed readability, R3 unit/order evidence, and bounded-scope wording.
- Script response: the source-only visual panel now uses the same transformed binary feature mask as scoring.

## Decision

- Result: `fail_no_r3_bounded_registration_tolerance_not_selector`.
- The bounded registration sweep does not supply a readable target-specific instruction or a source-backed unit/order cue.
- This closes only the declared scan-registration window: dx/dy +/-80 px in 20 px steps and rotation -1/0/+1 degrees. It does not claim arbitrary warps or a new physical scan are exhausted.
- Do not promote current-scan held-to-light into selector/key checks.
- Reopen only with a materially better physical scan or raw clue wording that names unit/order/transform.
