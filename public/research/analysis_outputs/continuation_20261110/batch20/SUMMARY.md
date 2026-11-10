# Twenty registered procedures · 10 November 2026

**The puzzle remains unsolved.** Twenty additional procedures were executed after the first embedded-minikey audit: **15 scoped literal/code negatives, one failed alignment screen, and four inconclusive procedures**. No valid private record, authenticated prize address, network query or transaction resulted. These are twenty procedures, not twenty independent theories or twenty entire cipher families ruled out.

Protocols and implementations were public on GitHub before target execution: [text registration](https://github.com/dctrpr/key-not-found/commit/8f4fa38bf24db7e432410c4daaa29e9de486156c), [geometry registration](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). Parameters, source hashes, controls, exact outputs or replay descriptors, timestamps and limits are preserved for each test.

The ten text procedures found no valid declared records; independent form/count/checksum audits agreed. These included faithful-line boustrophedon, interior columns, mesostics, paragraph/sentence boundaries, capitalization, and additional serialized key/public-record formats.

The geometry/image procedures produced useful limits:

- G01: only 12/120 readings were complete; 36/40 selection scopes remained ambiguous. **Mirror-first word selection remains open.**
- G02: every two-sided stencil scope had uncertain boundaries; no complete decoding was justified.
- G03: 1,296 fixed color-state decodes contained no declared literal key.
- G04/G05: 104 spacing rows and 98 displacement proxies were usable. No full page had complete coverage, so these remain inconclusive.
- G06/G07: 20 capsule residual views and 112 spectral/baseline OCR views yielded no declared literal key within their fixed detector scope.
- G08: 384 views yielded no QR/DataMatrix/Aztec/Code128 payload. All 16 planted control views passed.
- G09: true-leaf mean IoU 0.03085 failed to exceed the strongest wrong pair 0.03970. It passed the shifted-control rank screen but failed the required joint screen. This is not proof against mirror methods.
- G10: 768 current-raster least-bit serializations contained no declared literal key. This has weak relevance to a printed puzzle because printing/scanning/JPEG can erase earlier least-bit data.

**Best next step:** inspect the G01 boundary cases against the source pixels and freeze unambiguous selected words before testing additional decodings. Expanding guesses while the selector is uncertain would not give a clean exclusion. The exact failing scopes and source geometry are public.

## Results and reproduction

| ID | Procedure | Completed UTC | Outcome |
| --- | --- | --- | --- |
| [T01](T01/RESULT.md) | Alternating direction on the actual printed lines | 2026-11-10T05:14:17.446Z | No declared record/payload |
| [T02](T02/RESULT.md) | Fixed interior columns of printed words and characters | 2026-11-10T05:14:17.463Z | No declared record/payload |
| [T03](T03/RESULT.md) | Mirror-axis centers of printed lines | 2026-11-10T05:14:17.472Z | No declared record/payload |
| [T04](T04/RESULT.md) | Paragraph-boundary readings | 2026-11-10T05:14:17.484Z | No declared record/payload |
| [T05](T05/RESULT.md) | Sentence-boundary readings from the faithful body | 2026-11-10T05:14:17.492Z | No declared record/payload |
| [T06](T06/RESULT.md) | Visible capitalization as a data carrier | 2026-11-10T05:14:17.502Z | No declared record/payload |
| [T07](T07/RESULT.md) | Serialized extended private-key records | 2026-11-10T05:14:17.552Z | No declared record/payload |
| [T08](T08/RESULT.md) | BIP38 encrypted private-key records | 2026-11-10T05:14:17.603Z | No declared record/payload |
| [T09](T09/RESULT.md) | Literal candidate funding addresses | 2026-11-10T05:14:17.665Z | No declared record/payload |
| [T10](T10/RESULT.md) | Literal SEC public keys and curve membership | 2026-11-10T05:14:17.718Z | No declared record/payload |
| [G01](G01/RESULT.md) | Mirror first, then first selected word | 2026-11-10T05:25:27.770Z | Inconclusive |
| [G02](G02/RESULT.md) | Two-sided printed highlight stencil | 2026-11-10T05:25:28.009Z | Inconclusive |
| [G03](G03/RESULT.md) | Orange/black two-alphabet channel | 2026-11-10T05:25:28.052Z | No declared record/payload |
| [G04](G04/RESULT.md) | Fixed interword-gap binary channel | 2026-11-10T05:25:28.989Z | Inconclusive |
| [G05](G05/RESULT.md) | Printed-line displacement channel | 2026-11-10T05:25:29.898Z | Inconclusive |
| [G06](G06/RESULT.md) | Reused capsule interior differences | 2026-11-10T05:26:03.907Z | No declared record/payload |
| [G07](G07/RESULT.md) | Spectral color-isolation OCR | 2026-11-10T05:26:30.920Z | No declared record/payload |
| [G08](G08/RESULT.md) | Literal machine-readable codes | 2026-11-10T05:29:08.958Z | No declared record/payload |
| [G09](G09/RESULT.md) | Corrected-leaf alignment specificity | 2026-11-10T05:25:30.357Z | Alignment screen failed |
| [G10](G10/RESULT.md) | Current raster least-bit payload | 2026-11-10T05:27:05.026Z | No declared record/payload |

[Machine summary](SUMMARY.json) · [Text protocol](TEXT_PROTOCOL.md) · [Geometry protocol](GEOMETRY_PROTOCOL.md)
