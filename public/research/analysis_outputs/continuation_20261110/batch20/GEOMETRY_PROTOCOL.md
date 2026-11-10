# Ten fixed geometry and image procedures

Registered before target execution. Exact parameters, source bytes and three implementation pins are frozen in [GEOMETRY_PROTOCOL.json](GEOMETRY_PROTOCOL.json). The previous ten text procedures are a separate part of the same batch. Variants, phases, detector views, checksum candidates and independent theories are different counts. No target result is claimed in this registration.

The priority test is **G01: mirror first, then read the first selected word per printed row**. It combines the George Sand first-word clue with mirror reading on the corrected physical leaves. Source repair produced all 1,243 lexical-word boxes across the 142 canonical rows; OCR remains approximate. Seven character confusions were visually adjudicated against the source scan. The raw observations, frozen review plate, uncertainty and [source-only reproduction](../../../sources/WORD-GEOMETRY.md) are public. Word centers near a mask edge prevent a full negative rather than being guessed into a reading.

G02 tests a two-sided printed stencil. G03–G05 evaluate specific printed-state, spacing and displacement serializations. G06/G09 are evidence audits of repeated artwork and alignment, not independent key solutions. G07/G08 check fixed OCR and machine-code views. **G10 is deliberately low priority**: current raster least bits have a weak connection to a physical-print clue and may have been destroyed by printing, scanning or JPEG compression. None of these procedures exhausts its wider family.

## Evaluation and controls

Literal WIF, 22/30-character minikey, boundary-delimited 64hex scalar and unfiltered contiguous BIP39 words are checked. Invalid decoded groups are hard boundaries. No arbitrary prose hash or 32-byte ASCII/pixel scalar is generated. G09 is a fixed alignment screen with wrong pairs and shifted controls. Vision uses revision 3, accurate en-US OCR, language correction off. QR/DataMatrix/Aztec/Code128 each have four registered control transforms; this does not claim planted validation of every target view/scale. Engine metadata and failures are recorded. G04/G05 measure actual ink and reject clipped regions rather than treating OCR boxes as exact font positions.

Every procedure checks pinned sources and implementations plus synthetic controls before reading targets. Procedures requiring Vision run additional local controls. Detector/control/source failures remain inconclusive. Any valid private record is held for separate review and is not automatically called the prize. No transactions, wallet imports, accounts, messages or external API calls are performed.

## Reproduce

Use Python 3.10+, Pillow, NumPy and PyMuPDF. G06–G08 additionally require macOS, Swift and Apple Vision. From the research archive root, use a fresh local output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G01 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out G01-rerun
```

Replace REGISTRATION_COMMIT with the commit first publishing this protocol. G01–G10 are the registered IDs. Raw streams, detector observations and images stay private until reviewed. G10 processes one serialization at a time and preserves the 24 exact source bitplanes plus deterministic descriptors rather than building a gigabyte of decoded JSON; safe per-stream digests/inventory allow replay comparison.

## Procedures

- **G01 — Mirror first, then first selected word** (primary). Incomplete or boundary-ambiguous selected word geometry makes the affected stream inconclusive.
- **G02 — Two-sided printed highlight stencil** (coverage-correction). Uses corrected physical pairs and actual printed masks, not old chosen-p76 phrase boxes.
- **G03 — Orange/black two-alphabet channel** (exploratory). Color encoding was not specified by the creator; no DOCM/manual partial-bold state is used.
- **G04 — Fixed interword-gap binary channel** (conditional). Word boxes are machine-verified source geometry, not a claim of original font metadata.
- **G05 — Printed-line displacement channel** (conditional). The ink-bottom quantile is an optical baseline proxy, not original font metadata or an exact typographic baseline.
- **G06 — Reused capsule interior differences** (source-audit). Differences may be interpolation/compositing/printing artifacts. Shape reuse alone is not a selector.
- **G07 — Spectral color-isolation OCR** (coverage-check). No posthoc contrast/threshold/character substitution. OCR errors can hide genuine text.
- **G08 — Literal machine-readable codes** (sanity-check). No explicit creator QR clue known. Nonstandard, damaged or artistic codes remain possible.
- **G09 — Corrected-leaf alignment specificity** (coverage-correction). Evidence audit, not a key decoder. Nonsignificance is not absence proof.
- **G10 — Current raster least-bit payload** (low-priority-reserve). A weak file sanity check: physical printing/scanning/JPEG may erase an earlier digital payload.
