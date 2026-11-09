# Current PDF Duplicate Background Feature Artifact Gate

Scope: tested whether lower-resolution duplicate PDF carriers uniquely create the B4 feature-looking contact, or whether matched off-white broad-only background controls convert the same way. This checks PDF/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:48:15+02:00`
- Source point / page: `[1864, 2511]` / `75`
- Carriers total / magazine / duplicate: `6` / `2` / `4`
- B4 baseline RGB/luma/saturation: `[242, 242, 242]` / `242.0` / `0.0`
- B4 duplicate feature rows: `4/4`
- B4 magazine feature rows: `0/2`
- Local controls any/all duplicate feature: `44` / `40` of `54`
- Page-grid controls any/all duplicate feature: `48` / `39` of `57`
- Controls with at least B4's duplicate feature-row count, local/page-grid: `40` / `39`
- Hidden duplicate-PDF feature candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/current_pdf_duplicate_background_feature_artifact_gate_sheet.jpg`
- Fingerprint: `local=54|localAny=44|localAll=40|page=57|pageAny=48|pageAll=39|b4DupFeature=4/4|b4MagFeature=0/2|localAtLeastB4=40|pageAtLeastB4=39|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Histogram

| duplicate feature rows | local controls | page-grid controls |
|---:|---:|---:|
| `0` | `10` | `9` |
| `1` | `0` | `0` |
| `2` | `4` | `9` |
| `3` | `0` | `0` |
| `4` | `40` | `39` |

## Decision

- `duplicate_pdf_b4_feature_contact_controlled_artifact`
- The B4 point is feature-classified in all duplicate/lower-resolution carriers, but not in the byte-locked `magazine.pdf` carriers.
- Many matched off-white broad-only controls also convert to feature in duplicate carriers, including controls that match or exceed B4's duplicate feature-row count.
- This keeps duplicate-PDF feature contacts closed as resampling/provenance artifacts, not source ink or extraction selectors.

## Next Move

- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
