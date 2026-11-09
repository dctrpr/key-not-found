# Current PDF Native Registration Candidate Source Trace

Scope: traced only the exact-native registration rows that crossed candidate thresholds in the previous gate. This is provenance review only: no key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T07:14:59`
- Decision: `current_pdf_native_registration_candidate_trace_no_instruction_source`
- Candidate trace rows / active / projected OVERDOSE slots: `4` / `2` / `2`
- Components / component pixels / source-only pixels: `34` / `196264` / `198756`
- Source-word rows / source-word hits: `2` / `16`
- Strict instruction rows / hits: `0` / `0`
- Context rows / hits: `2` / `2`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace/current_pdf_native_registration_candidate_source_trace_sheet.jpg`
- Fingerprint: `rows=4|active=2|slots=2|components=34|pixels=196264|sourceOnly=198756|wordRows=2|words=16|strictRows=0|strict=0|contextRows=2|context=2|sourceR3=0|triggers=0/9|selectors=0`

## Trace Rows

| PDF | kind | target | coverage | components | source words | strict | context | source preview |
|---|---|---|---:|---:|---:|---:|---:|---|
| `keyser bitcoin .pdf` | `active` | `O4` | 0.5757 | 2 | 8 | 0 | 1 | in by riding Bitcoins Buterin came up with |
| `keyser bitcoin .pdf` | `overdose_slot` | `slot0_O_O` | 0.6339 | 15 | 0 | 0 | 0 |  |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `active` | `O4` | 0.5757 | 2 | 8 | 0 | 1 | in by riding Bitcoins Buterin came up with |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `overdose_slot` | `slot0_O_O` | 0.6339 | 15 | 0 | 0 | 0 |  |

## Decision

- `current_pdf_native_registration_candidate_trace_no_instruction_source`
- Do not promote the low-resolution duplicate PDF O4/slot0 native-registration spike as a selector.
- The threshold-crossing pixels trace to ordinary page-75 prose/context rather than source-side unit/order wording, and the spike remains duplicate-only and non-quartet.
- Next move: require distinct physical/original-layout source material or raw clue wording that explicitly names transform, unit, and order before reopening selector/key checks.
