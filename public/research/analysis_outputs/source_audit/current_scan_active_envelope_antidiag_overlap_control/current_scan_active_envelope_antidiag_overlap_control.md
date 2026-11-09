# Current Scan Active-Envelope Anti-Diagonal Overlap Control

Scope: applied the same normalized anti-diagonal fold to every four-box page-76 active/highlight quartet and compared all-four partial-overlap behavior. This is a bounded geometry/format control; no OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T19:58:16`
- Page-76 active/highlight boxes / quartets: `11` / `330`
- All-four overlap quartets / distinct all-four streams: `42` / `17`
- Active quartet rank among all-four / distinct all-four: `1` / `1`
- Active quartet min/mean/max overlap-vs-projected: `0.129086526` / `0.208202625` / `0.324256666`
- Active quartet stream/kind stream: `O4-O5-G5-B4` / `orange-orange-black-black`
- Paired text/format strict rows: `0` / `0`
- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`
- Sheet: `analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control/current_scan_active_envelope_antidiag_overlap_control_sheet.jpg`
- Fingerprint: `boxes=11|quartets=330|allFour=42|distinct=17|activeRank=1/1|activeMinMeanMax=0.129086526/0.208202625/0.324256666|strict=0/0|sourceR3=0|triggers=0/9|selectors=0`

## Distribution

- All-four overlap by active-box count: `{'0': 5, '1': 22, '2': 12, '3': 2, '4': 1}`
- Distinct all-four overlap by active-box count: `{'0': 1, '1': 8, '2': 5, '3': 2, '4': 1}`

## Top All-Four Rows

| rank | combo | active boxes | stream | kind stream | min overlap | mean overlap |
|---:|---|---:|---|---|---:|---:|
| 1 | `O4/B4/G5/O5` | `4` | `O4-O5-G5-B4` | `orange-orange-black-black` | `0.129086526` | `0.208202625` |
| 2 | `O4/B4/O5/G4` | `3` | `O4-O5-B4-G4` | `orange-orange-black-grey` | `0.106371811` | `0.211770624` |
| 3 | `B4/O5/G2/G4` | `2` | `G4-G2-O5-G4` | `grey-grey-orange-grey` | `0.068355641` | `0.10735492` |
| 4 | `O1/O3/G1/G2` | `0` | `G1-G2-G1-O3` | `grey-grey-grey-orange` | `0.063922632` | `0.139657793` |
| 5 | `O1/O3/G2/G3` | `0` | `O1-O3-G3-G2` | `orange-orange-grey-grey` | `0.057514625` | `0.148959673` |
| 6 | `O4/G5/O5/G3` | `3` | `O4-O5-G5-G3` | `orange-orange-black-grey` | `0.055838302` | `0.069315862` |
| 7 | `O1/G1/G2/G3` | `0` | `G1-G1-G3-G2` | `grey-grey-grey-grey` | `0.055493274` | `0.145410962` |
| 8 | `O1/O3/G1/G3` | `0` | `G1-O3-G1-G1` | `grey-orange-grey-grey` | `0.053851461` | `0.074115875` |
| 9 | `O4/B4/O3/G4` | `2` | `O3-G4-O4-G4` | `orange-grey-orange-grey` | `0.051124953` | `0.113979881` |
| 10 | `O4/O3/G1/G3` | `1` | `O3-O4-G1-G3` | `orange-orange-grey-grey` | `0.045569584` | `0.088396257` |
| 11 | `O4/O2/G2/G3` | `1` | `G2-G3-O4-O2` | `grey-grey-orange-orange` | `0.04555234` | `0.144200764` |
| 12 | `O4/B4/O3/G1` | `2` | `O3-B4-O4-G1` | `orange-black-orange-grey` | `0.039395298` | `0.1042165` |

## Decision

- `current_scan_active_envelope_antidiag_overlap_control_no_selector`
- The active quartet is the strongest page-76 highlighted quartet under this specific anti-diagonal self-overlap control, so the near miss is real geometry.
- It still fails extraction: the minimum overlap is only about 13%, paired text/format strict rows are 0, no reopen trigger is satisfied, and no source-backed unit/order exists.

## Next Move

- Keep anti-diagonal active-envelope overlap as locator/provenance evidence only.
- Reopen extraction only if a distinct source or raw clue explicitly names this fold and tells us what unit/order to read.
