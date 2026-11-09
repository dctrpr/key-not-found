# Current PDF Thumbnail Active Signal Gate

Scope: checked the tiny embedded page-76 thumbnail against the same-size trusted page-image downsample around O4/B4/G5/O5, page-76 highlight controls, and C9/OVERDOSE slots. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T19:06:55`
- Thumbnail: xref `38`, size `82x106`
- Best orientation vs trusted downsample: `rot180` with MAD `15.2525`
- Active state matches expected: `3/4`
- Active / control / slot state changes vs same-size downsample: `1` / `1` / `2`
- Active min pixel count: `60`
- Max active / slot crop MAD: `52.2833` / `36.8774`
- Hidden thumbnail signal candidate / selectors: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate/current_pdf_thumbnail_active_signal_gate_sheet.jpg`
- Fingerprint: `thumb=82x106|transform=rot180|mad=15.2525|activeMatch=3/4|activeChanged=1|controlChanged=1|slotChanged=2|activeMinPx=60|maxActiveMad=52.2833|maxSlotMad=36.8774|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Active Rows

| id | expected | thumbnail state | downsample state | pixels | MAD | thumb orange/dark/grey |
|---|---|---|---|---:|---:|---|
| O4 | orange | black_or_grey | orange | 95 | 37.5018 | 0.084211/0.147368/0.084211 |
| B4 | black_or_grey | black_or_grey | black_or_grey | 60 | 52.0556 | 0.0/0.133333/0.133333 |
| G5 | black_or_grey | black_or_grey | black_or_grey | 80 | 52.2833 | 0.0/0.1125/0.1375 |
| O5 | orange | orange | orange | 92 | 22.5616 | 0.369565/0.076087/0.0 |

## Decision

- `current_pdf_thumbnail_active_signal_no_selector`
- The page-76 thumbnail is only `82x106`; active text boxes collapse to tiny regions and are a preview/downsample witness, not a separate source layer.
- The thumbnail does not invent a cleaner all-four active or OVERDOSE-slot signal beyond the same-size trusted downsample, and no source-backed R3 trigger is satisfied.
- Keep embedded thumbnails closed as provenance-only previews.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
