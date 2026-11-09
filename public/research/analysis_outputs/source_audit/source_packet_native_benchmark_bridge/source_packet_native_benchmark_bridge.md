# Source Packet Native Benchmark Bridge

Scope: package the active page-76 source-comparison benchmarks in both readable/upright and native source coordinates. No OCR, extraction, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-21T05:34:54`
- Transform: `rotate180`
- Image size: `2544x3264`
- Native rotated 180 vs upright mean abs diff: `0.2859`; max diff `31`; nonzero `12.1415%`
- Direct native vs upright mean abs diff: `27.6479`; max diff `255`
- Benchmark boxes: `15`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- Active visual-state order: `YKKY`
- C9 frame x-mirror invariant: `True`
- OVERDOSE glyph sequence: `OVERDOSE`
- Header glyph max edge delta vs equal slots: `0.087628` px
- All native boxes in bounds: `True`
- Sheet: `analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge_sheet.jpg`

## Coordinate Rows

| id | kind | upright box | native source box | size |
|---|---|---|---|---|
| `buying_dip` | `active_target` | `[1334, 2177, 1801, 2225]` | `[743, 1039, 1210, 1087]` | `[467, 48]` |
| `one_billion` | `active_target` | `[428, 2398, 691, 2445]` | `[1853, 819, 2116, 866]` | `[263, 47]` |
| `volcano_bonds` | `active_target` | `[795, 2544, 1196, 2592]` | `[1348, 672, 1749, 720]` | `[401, 48]` |
| `shitcoiner_heart` | `active_target` | `[1040, 2932, 1661, 2982]` | `[883, 282, 1504, 332]` | `[621, 50]` |
| `c9_yk_frame` | `source_frame` | `[294, 2177, 2250, 3024]` | `[294, 240, 2250, 1087]` | `[1956, 847]` |
| `p78_reflected_frame_on_p76` | `source_frame` | `[1234, 2398, 2250, 2950]` | `[294, 314, 1310, 866]` | `[1016, 552]` |
| `p76_overdose_header` | `overdose_header` | `[2150.98, 153.05, 2291.26, 184.24]` | `[253, 3080, 393, 3111]` | `[140, 31]` |
| `overdose_glyph_1_O` | `overdose_glyph` | `[2150.98, 153.05, 2168.52, 184.24]` | `[375, 3080, 393, 3111]` | `[18, 31]` |
| `overdose_glyph_2_V` | `overdose_glyph` | `[2168.52, 153.05, 2186.05, 184.24]` | `[358, 3080, 375, 3111]` | `[18, 31]` |
| `overdose_glyph_3_E` | `overdose_glyph` | `[2186.05, 153.05, 2203.59, 184.24]` | `[340, 3080, 358, 3111]` | `[18, 31]` |
| `overdose_glyph_4_R` | `overdose_glyph` | `[2203.59, 153.05, 2221.12, 184.24]` | `[323, 3080, 340, 3111]` | `[18, 31]` |
| `overdose_glyph_5_D` | `overdose_glyph` | `[2221.12, 153.05, 2238.66, 184.24]` | `[305, 3080, 323, 3111]` | `[18, 31]` |
| `overdose_glyph_6_O` | `overdose_glyph` | `[2238.66, 153.05, 2256.19, 184.24]` | `[288, 3080, 305, 3111]` | `[18, 31]` |
| `overdose_glyph_7_S` | `overdose_glyph` | `[2256.19, 153.05, 2273.73, 184.24]` | `[270, 3080, 288, 3111]` | `[18, 31]` |
| `overdose_glyph_8_E` | `overdose_glyph` | `[2273.73, 153.05, 2291.26, 184.24]` | `[253, 3080, 270, 3111]` | `[18, 31]` |

## Decision

- Keep this as source-registration scaffolding only.
- The bridge makes future physical/original-layout comparisons less ambiguous, but it does not supply a selector, unit, or order.
- Any future source match still needs R3 wording or equivalent source evidence before extraction resumes.
