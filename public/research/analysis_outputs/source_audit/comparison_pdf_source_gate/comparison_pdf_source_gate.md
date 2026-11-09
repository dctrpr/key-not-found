# Comparison PDFs Against Source Gate

Scope: apply the source-validation gate to local comparison PDFs. No OCR, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:39:15`
- Promoted for Issue 24 extraction geometry: `0`
- Style-only comparison PDFs: `3`

## Gate Results

| PDF | class | gate status | allowed use | style/highlighter note | reason |
|---|---|---|---|---|---|
| `bitcoin3.pdf` | comparison Max/OVERDOSE issue | `reject_for_issue24_geometry` | style-only Max/OVERDOSE comparison | orange=4, dark=4, sustained=[8], max=7 | Different issue/article material cannot alter Issue 24 page-76 geometry or provide extraction coordinates for the 20 BTC puzzle. |
| `Issue_26.pdf` | comparison Max/OVERDOSE issue | `reject_for_issue24_geometry` | style-only Max/OVERDOSE comparison | orange=11, dark=4, sustained=[3, 4], max=14 | Different issue/article material cannot alter Issue 24 page-76 geometry or provide extraction coordinates for the 20 BTC puzzle. |
| `Issue_27.pdf` | comparison Max/OVERDOSE issue | `reject_for_issue24_geometry` | style-only Max/OVERDOSE comparison | orange=2, dark=3, sustained=[], max=3 | Different issue/article material cannot alter Issue 24 page-76 geometry or provide extraction coordinates for the 20 BTC puzzle. |
| `bitcoin4.pdf` | low-res Issue 24 article witness | `reject_as_geometry_truth` | low-res Issue 24 source-fidelity witness only | orange=28, dark=14, sustained=[3, 4, 6, 7], max=19 | It is the same Issue 24 article, but the existing witness audits show lower resolution/distortion and no repair of the trusted G5/O5 p78-frame registration. |

## bitcoin4 Witness Constraint

- `bitcoin4.pdf` preserves the same Issue 24 regions only as a lower-resolution witness.
- Page-76 affine residual in the witness audit: mean `3.618` px, max `10.079` px.
- It does not repair the p78 frame / G5 / O5 benchmark, so it cannot replace `magazine.pdf` for extraction geometry.

## Decision

- No comparison PDF passes the source gate for Issue 24 extraction geometry. bitcoin4 remains a low-res Issue 24 fidelity witness; bitcoin3, Issue_26, and Issue_27 remain style-only comparison articles.

## Next Move

- Use comparison PDFs only to test whether Typeka/highlighter/pill grammar is unique. Do not use them to select key material unless a future raw clue explicitly references a comparison issue/article.
