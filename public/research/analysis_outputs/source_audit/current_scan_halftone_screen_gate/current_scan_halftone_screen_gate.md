# Current Scan Halftone Screen Gate

Scope: inspected current page-76 scan high-frequency/halftone texture and dominant screen angle in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This is a visual/source artifact gate, not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T06:25:02`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Active dominant-share outliers above shifted-control p95: `0` (``)
- Active highpass-RMS outliers above shifted-control p95: `1` (`G5`)
- All-four active dominant-share/highpass outliers: `0` / `0`
- Active dominant angle bins: `90.0-112.5,90.0-112.5,90.0-112.5,90.0-112.5`
- Shared active angle bin / matching controls / matching OVERDOSE slots: `90.0-112.5` / `12` / `7`
- Max active/control/OVERDOSE dominant share: `0.241` / `0.373` / `0.240`
- Max active/control/OVERDOSE highpass RMS: `50.752` / `50.636` / `38.139`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_halftone_screen_gate/current_scan_halftone_screen_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|shareOutliers=0|highpassOutliers=1|allFourShare=0|allFourHighpass=0|activeBins=90.0-112.5,90.0-112.5,90.0-112.5,90.0-112.5|commonBin=90.0-112.5|controlCommon=12|slotCommon=7|shareMax=0.241/0.373/0.240|highpassMax=50.752/50.636/38.139|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | highpass RMS | high-freq power | dominant share | angle | bin | anisotropy |
|---|---|---:|---:|---:|---:|---|---:|
| `shifted_control` | `O5_dy+146` | 0.640 | 0.620 | 0.373 | 11.2 | `0.0-22.5` | 0.355 |
| `shifted_control` | `O5_dy+292` | 0.709 | 0.539 | 0.304 | 101.2 | `90.0-112.5` | 0.239 |
| `shifted_control` | `O4_dy-292` | 0.611 | 0.501 | 0.295 | 101.2 | `90.0-112.5` | 0.257 |
| `active` | `G5` | 50.752 | 0.132 | 0.241 | 101.2 | `90.0-112.5` | 0.171 |
| `overdose_slot` | `slot7_E` | 4.296 | 0.014 | 0.240 | 101.2 | `90.0-112.5` | 0.163 |
| `shifted_control` | `O5_dy-292` | 29.113 | 0.115 | 0.216 | 101.2 | `90.0-112.5` | 0.140 |
| `active` | `O5` | 24.466 | 0.065 | 0.214 | 101.2 | `90.0-112.5` | 0.130 |
| `active` | `B4` | 49.775 | 0.136 | 0.199 | 101.2 | `90.0-112.5` | 0.133 |
| `shifted_control` | `O4_dy+292` | 23.601 | 0.156 | 0.197 | 101.2 | `90.0-112.5` | 0.119 |
| `shifted_control` | `B4_dy+146` | 49.981 | 0.127 | 0.194 | 101.2 | `90.0-112.5` | 0.115 |
| `active` | `O4` | 25.547 | 0.104 | 0.190 | 101.2 | `90.0-112.5` | 0.105 |
| `overdose_slot` | `slot3_R` | 36.940 | 0.075 | 0.188 | 101.2 | `90.0-112.5` | 0.102 |
| `shifted_control` | `B4_dy-146` | 47.578 | 0.122 | 0.186 | 101.2 | `90.0-112.5` | 0.102 |
| `overdose_slot` | `slot2_E` | 37.158 | 0.074 | 0.185 | 101.2 | `90.0-112.5` | 0.099 |
| `shifted_control` | `G5_dy+292` | 42.863 | 0.097 | 0.181 | 11.2 | `0.0-22.5` | 0.105 |
| `shifted_control` | `B4_dy-292` | 48.981 | 0.156 | 0.181 | 101.2 | `90.0-112.5` | 0.111 |
| `shifted_control` | `G5_dy-146` | 44.851 | 0.141 | 0.180 | 101.2 | `90.0-112.5` | 0.099 |
| `overdose_slot` | `slot0_O` | 25.279 | 0.078 | 0.180 | 101.2 | `90.0-112.5` | 0.095 |
| `overdose_slot` | `slot4_D` | 34.683 | 0.080 | 0.180 | 101.2 | `90.0-112.5` | 0.093 |
| `overdose_slot` | `slot5_O` | 21.411 | 0.050 | 0.178 | 101.2 | `90.0-112.5` | 0.088 |
| `shifted_control` | `G5_dy+146` | 50.568 | 0.145 | 0.177 | 101.2 | `90.0-112.5` | 0.089 |
| `shifted_control` | `B4_dy+292` | 50.636 | 0.111 | 0.176 | 101.2 | `90.0-112.5` | 0.099 |
| `shifted_control` | `G5_dy-292` | 45.217 | 0.068 | 0.175 | 11.2 | `0.0-22.5` | 0.090 |
| `overdose_slot` | `slot1_V` | 38.139 | 0.096 | 0.175 | 101.2 | `90.0-112.5` | 0.088 |
| `shifted_control` | `O5_dy-146` | 29.838 | 0.111 | 0.173 | 101.2 | `90.0-112.5` | 0.080 |
| `overdose_slot` | `slot6_S` | 4.877 | 0.060 | 0.169 | 11.2 | `0.0-22.5` | 0.080 |
| `shifted_control` | `O4_dy-146` | 24.492 | 0.087 | 0.166 | 101.2 | `90.0-112.5` | 0.073 |
| `shifted_control` | `O4_dy+146` | 36.197 | 0.110 | 0.165 | 11.2 | `0.0-22.5` | 0.073 |

## Decision

- `current_scan_halftone_screen_no_selector`
- Active boxes and projected OVERDOSE slots do not produce a unique halftone/screen-angle or high-frequency texture signature against shifted controls.
- The active quartet shares a dominant angle bin, but that bin is ordinary page/scan texture evidence and is not an all-four control-threshold outlier or source-backed extraction rule.
- The scan texture remains source-quality/printing evidence only, not an extraction rule.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
