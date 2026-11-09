# Capsule Motif Recurrence

Scope: check whether the Issue 24 orange capsule artwork recurs in the user-provided comparison PDFs. This is a layout/provenance check only; no key candidates are generated.

- Review sheet: `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg`

## Summary

- issue24_toxic_af: candidates `35`, strong individual warm-shape matches `23`, strong five-point sequence matches `2`
- issue26: candidates `18`, strong individual warm-shape matches `17`, strong five-point sequence matches `0`
- issue27: candidates `12`, strong individual warm-shape matches `8`, strong five-point sequence matches `0`
- bitcoin3: candidates `75`, strong individual warm-shape matches `41`, strong five-point sequence matches `0`
- bitcoin4: candidates `34`, strong individual warm-shape matches `24`, strong five-point sequence matches `2`

## Five-Point Sequence Matches

- issue24_toxic_af p01: ref=issue24_p73_capsules meanResidual=0.48 px maxResidual=0.95 px meanBlobScore=0.9294
- bitcoin4 p07: ref=issue24_p79_fragments meanResidual=1.01 px maxResidual=1.46 px meanBlobScore=0.8489
- issue24_toxic_af p07: ref=issue24_p79_fragments meanResidual=1.1 px maxResidual=2.25 px meanBlobScore=0.8794
- bitcoin4 p01: ref=issue24_p79_fragments meanResidual=1.64 px maxResidual=2.08 px meanBlobScore=0.895
- bitcoin3 p07: ref=issue24_p79_fragments meanResidual=36.29 px maxResidual=48.49 px meanBlobScore=0.4583
- bitcoin4 p08: ref=issue24_p73_capsules meanResidual=41.2 px maxResidual=61.76 px meanBlobScore=0.5522
- issue26 p05: ref=issue24_p73_capsules meanResidual=48.92 px maxResidual=97.06 px meanBlobScore=0.5307
- issue24_toxic_af p08: ref=issue24_p73_capsules meanResidual=51.92 px maxResidual=77.7 px meanBlobScore=0.4792
- bitcoin3 p08: ref=issue24_p79_fragments meanResidual=93.54 px maxResidual=146.94 px meanBlobScore=0.6001

## Top Comparison Matches

- issue26 p05: score=0.7561 ref=O73-2 box=(856, 2200, 934, 2282) size=78x82
- bitcoin3 p08: score=0.75 ref=O73-2 box=(1896, 408, 1958, 444) size=62x36
- issue26 p05: score=0.7475 ref=O73-2 box=(864, 2084, 948, 2116) size=84x32
- bitcoin3 p08: score=0.7328 ref=P79-7 box=(892, 576, 934, 616) size=42x40
- bitcoin3 p08: score=0.7113 ref=O73-2 box=(1292, 938, 1346, 1010) size=54x72
- bitcoin3 p07: score=0.6979 ref=O73-3 box=(1008, 1048, 1046, 1086) size=38x38
- bitcoin3 p07: score=0.6894 ref=P79-7 box=(1012, 1090, 1052, 1132) size=40x42
- bitcoin3 p08: score=0.6792 ref=O73-3 box=(86, 1282, 118, 1354) size=32x72
- bitcoin3 p08: score=0.6764 ref=O73-2 box=(70, 928, 104, 1110) size=34x182
- issue27 p03: score=0.6719 ref=O73-5 box=(1652, 1672, 1740, 1768) size=88x96
- bitcoin3 p07: score=0.6655 ref=O73-2 box=(1914, 1924, 1966, 2070) size=52x146
- issue27 p08: score=0.6566 ref=P79-7 box=(758, 644, 800, 702) size=42x58

## Assessment

- Individual red/orange blobs in the comparison PDFs can score as capsule-like, so single-component matching is not decisive.
- The five-point zigzag sequence check is the important discriminator: it recovers Issue 24's p73/p79 capsule motif and finds no strong five-point sequence recurrence in `Issue_26.pdf`, `Issue_27.pdf`, or `bitcoin3.pdf`.
- `bitcoin4.pdf` is treated as a lower-resolution Issue 24 witness; matches there confirm source-family duplication, not a generic OVERDOSE motif.
- That makes the p73/p79 capsule chain more Issue-24-specific than generic OVERDOSE house style, but it remains source/order evidence, not a direct key selector.

## Next Best Move

- Keep the capsule motif in the active provenance layer. The missing piece is still the human rule that maps source/order evidence onto page-76 text.
