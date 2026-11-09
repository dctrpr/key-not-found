# Scan-Only Held-To-Light Adjudication

Scope: use only `magazine.pdf` embedded scanned pages to make a fixed, human-readable held-to-light sheet for the physically valid page 75 -> page 76 leaf relation. No key derivation, OCR-to-key extraction, hashing, seed/WIF/address checks, or broad brute force were run.

- Created: `2026-05-24T21:20:07`
- Sheet: `analysis_outputs/source_audit/scan_only_held_to_light_adjudication/scan_only_held_to_light_adjudication_sheet.jpg`
- Source page: `75` back-side source
- Target page: `76` front-side target
- Orientation: embedded pages rotated `180` degrees to readable/upright, then page 75 was horizontally mirrored with `dx=0`, `dy=0`.
- Fixed opacities: `0.35, 0.50, 0.65`

## Active Target Scores

| target | phrase | source-only coverage | control p95 | percentile | above p95 |
|---|---|---:|---:|---:|---|
| `O4` | buying the dip | `0.004238` | `0.510381` | `0.125` | `False` |
| `B4` | $1 billion | `0.000000` | `0.127878` | `0.781` | `False` |
| `G5` | Volcano Bonds | `0.005767` | `0.239292` | `0.391` | `False` |
| `O5` | shitcoiner at heart | `0.003188` | `0.318454` | `0.344` | `False` |

## Findings

- Active boxes at or above 10% source-only ink: `0/4`.
- Active boxes above same-size nearby-control p95: `0/4`.
- Source-backed R3 unit/order bridge from strict/context/line-band gates: `0`.
- Control boxes scored: `256`.
- Fingerprint: `pair=75->76|opacities=0.35,0.50,0.65|controls=256|activeGe10=0/4|activeGtP95=0/4|sourceR3=0|selectors=0`.
- Adversarial review response: decision is scoped to fixed natural no-shift registration; the sheet now includes an unlabeled overlay plus a full-control population panel.

## Decision

- Result: `fail_no_r3_fixed_natural_registration_not_selector`.
- The fixed natural overlay remains source-registration/visual evidence only.
- This pass does not claim every shifted/warped scan registration is newly exhausted; it closes the fixed no-shift natural light-table view requested here.
- Do not promote this current-scan held-to-light view into extraction/key checks.
- Reopen only with a physically new or higher-resolution scan, or raw clue wording that names unit/order/transform.
