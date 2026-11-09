# Current Scan Valid Leaf Source-Ink Landing Gate

Scope: measured whether mirrored page-75 source ink physically lands inside the O4/B4/G5/O5 page-76 active boxes under the natural same-leaf 75->76 held-to-light registration. This checks actual source ink, not arbitrary blend appearance. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T08:54:42`
- Scenario: `valid_75_to_76_natural` / `same_leaf_75_to_76` / `natural_hflip`
- Source / target pages: `75` -> `76`
- Shift dx,dy: `0,0`
- Active boxes / line-shift controls: `4` / `24`
- Estimated line pitch: `74.55px`
- Source-ink support threshold: `0.05`
- Active source-supported targets: `O4,G5,O5` (`3/4`)
- Weak source-supported targets: `O4,G5,O5` (`3/4`)
- Zero-source-ink targets: `B4`
- All-four source-supported / weak-source-supported: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Overlay: `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/valid_75_to_76_source_ink_overlay.jpg`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/current_scan_valid_leaf_source_ink_landing_gate_sheet.jpg`
- Fingerprint: `scenario=valid_75_to_76_natural|targets=4|controls=24|activeGe05=3|activeGe01=3|all4Ge05=0|all4Ge01=0|zeroTargets=B4|ratios=O4:0.1402,B4:0.0000,G5:0.0596,O5:0.1940|sourceR3=0|triggers=0/9|selectors=0`

## Target Rows

| target | phrase | source ink ratio | ink pixels | control p95 | controls >= active | supported | local ink bbox |
|---|---|---:|---:|---:|---:|---:|---|
| `O4` | `buying the dip` | 0.140212 | 3143 | 0.473969 | 4 | 1 | `[0, 15, 467, 48]` |
| `B4` | `$1 billion` | 0.000000 | 0 | 0.000000 | 6 | 0 | `None` |
| `G5` | `Volcano Bonds` | 0.059643 | 1148 | 0.210645 | 3 | 1 | `[229, 17, 401, 48]` |
| `O5` | `shitcoiner at heart` | 0.194042 | 6025 | 0.258535 | 3 | 1 | `[0, 0, 621, 38]` |

## Decision

- `current_scan_valid_leaf_source_ink_landing_no_selector`
- The valid same-leaf page-75-to-76 geometry does not physically support all four active targets.
- B4 has zero landing source ink, so the average-blend all-four visual pop is not a physical back-page ink carrier.
- This closes the strongest remaining held-to-light caveat from the blend-mode pass.

## Next Move

- Keep current-scan held-to-light panels as source-review witnesses only.
- Continue with original-layout/physical source acquisition or raw clue wording that supplies transform, unit, and order.
