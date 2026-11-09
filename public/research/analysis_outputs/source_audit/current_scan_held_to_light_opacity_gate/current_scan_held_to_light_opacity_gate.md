# Current Scan Held-To-Light Opacity Gate

Scope: tested opacity and color-transfer blends using the current PDF/source images in readable/upright orientation. Page 76 was blended with mirrored back pages under average, darken, and multiply modes at three opacity levels. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T06:04:30`
- Scenarios / blend rows / active-box rows: `4` / `36` / `144`
- Best natural 75->76 all-box darkening: `0.00` via `average@0.25`
- Best forced/control all-box darkening: `6.33` via `nonphysical_79_to_76_forced_active` / `multiply@0.75`
- Natural all-four delta>=16 rows / forced-or-control all-four delta>=16 rows: `0` / `0`
- Expected Y/K state-stream matches: `20` / `36`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/current_scan_held_to_light_opacity_gate_sheet.jpg`
- Fingerprint: `scenarios=4|blendRows=36|boxRows=144|naturalBest=0.00:average@0.25|controlBest=6.33:nonphysical_79_to_76_forced_active:multiply@0.75|all16=0/0|stateMatches=20/36|sourceR3=0|triggers=0/9|selectors=0`

## Blend Rows

| scenario | mode | alpha | min darkening | mean darkening | min RGB delta | states | binary active coverage |
|---|---|---:|---:|---:|---:|---|---:|
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.75 | 6.33 | 19.30 | 6.34 | `YKKK` | 0.3840 |
| `nonphysical_79_to_76_forced_active` | `darken` | 0.75 | 5.52 | 13.61 | 5.53 | `YKKK` | 0.3840 |
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.50 | 4.26 | 12.94 | 4.26 | `YKKK` | 0.3840 |
| `nonphysical_79_to_76_forced_active` | `darken` | 0.50 | 3.68 | 9.08 | 3.68 | `YKKK` | 0.3840 |
| `valid_75_to_76_forced_active` | `multiply` | 0.75 | 2.89 | 13.68 | 2.89 | `YKKY` | 0.3242 |
| `valid_75_to_76_forced_active` | `darken` | 0.75 | 2.65 | 6.92 | 2.64 | `YKKY` | 0.3242 |
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.25 | 2.21 | 6.60 | 2.21 | `YKKY` | 0.3840 |
| `valid_75_to_76_forced_active` | `multiply` | 0.50 | 1.93 | 9.18 | 1.93 | `YKKY` | 0.3242 |
| `nonphysical_79_to_76_forced_active` | `darken` | 0.25 | 1.87 | 4.60 | 1.87 | `YKKY` | 0.3840 |
| `valid_75_to_76_forced_active` | `darken` | 0.50 | 1.76 | 4.61 | 1.76 | `YKKY` | 0.3242 |
| `valid_75_to_76_forced_active` | `multiply` | 0.25 | 0.98 | 4.70 | 0.98 | `YKKY` | 0.3242 |
| `valid_75_to_76_forced_active` | `darken` | 0.25 | 0.89 | 2.35 | 0.89 | `YKKY` | 0.3242 |
| `valid_75_to_76_natural` | `average` | 0.25 | 0.00 | 0.00 | 31.20 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `average` | 0.50 | 0.00 | 0.00 | 62.74 | `YNNY` | 0.1003 |
| `valid_75_to_76_natural` | `average` | 0.75 | 0.00 | 0.00 | 94.11 | `KNNK` | 0.1003 |
| `valid_75_to_76_natural` | `darken` | 0.25 | 0.00 | 1.47 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `darken` | 0.50 | 0.00 | 2.90 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `darken` | 0.75 | 0.00 | 4.35 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `multiply` | 0.25 | 0.00 | 1.88 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `multiply` | 0.50 | 0.00 | 3.63 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_natural` | `multiply` | 0.75 | 0.00 | 5.39 | 0.00 | `YKKY` | 0.1003 |
| `valid_75_to_76_forced_active` | `average` | 0.25 | 0.00 | 0.00 | 9.52 | `YKKY` | 0.3242 |
| `valid_75_to_76_forced_active` | `average` | 0.50 | 0.00 | 0.00 | 19.08 | `YNNY` | 0.3242 |
| `valid_75_to_76_forced_active` | `average` | 0.75 | 0.00 | 0.00 | 28.61 | `YKNK` | 0.3242 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.25 | 0.00 | 0.46 | 29.64 | `YKKY` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.50 | 0.00 | 0.80 | 59.24 | `YNNK` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.75 | 0.00 | 1.20 | 88.85 | `KNNK` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `darken` | 0.25 | 0.00 | 5.23 | 0.00 | `YKKY` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `darken` | 0.50 | 0.00 | 10.38 | 0.00 | `YKKK` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `darken` | 0.75 | 0.00 | 15.56 | 0.00 | `YKKK` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `multiply` | 0.25 | 0.00 | 5.86 | 0.00 | `YKKY` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `multiply` | 0.50 | 0.00 | 11.57 | 0.00 | `YKKK` | 0.2921 |
| `nonphysical_78_to_76_forced_active` | `multiply` | 0.75 | 0.00 | 17.29 | 0.00 | `YKKK` | 0.2921 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.25 | 0.00 | 0.00 | 15.47 | `YKKY` | 0.3840 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.50 | 0.00 | 0.00 | 31.00 | `YNKY` | 0.3840 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.75 | 0.00 | 0.00 | 46.50 | `YKKK` | 0.3840 |

## Decision

- `opacity_color_transfer_no_selector`
- The physically valid natural 75->76 view does not become a unique active-quartet selector under opacity/color transfer.
- Stronger all-box darkening requires arbitrary blend/opacity choices and is matched or exceeded by forced/non-physical page-76 controls.
- The active visual state remains useful as source-validation evidence, but it does not supply the missing R3 unit/order/transform.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
