# Page-76 Target Format Authority Lock

Scope: lock the authoritative formatting witnesses for the active page-76 targets. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:33:27`
- Sheet: `analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock_sheet.jpg`
- Decision: `page76_target_format_authority_locked_no_selector`

## Active Format Pattern

- Color pattern: `OBBO`
- Visual-state order: `YKKY`
- Page lines: `22 25 27 32`
- Sentence rows: `44 45 45 48`
- Corridor indexes: `4 7 9 14`
- All active targets DOCM Typeka bold: `True`
- High-res visual exact matches: `4/4`
- Crop-pack active coverage: `3/4`

## Active Targets

| order | target | color/state | line/corridor | DOCM font/bold | DOCM highlight | high-res exact | crop evidence |
|---:|---|---|---|---|---|---:|---|
| 1 | `buying the dip` | `orange/Y` | `L22/C4` | `Typeka / 1.0` | `yellow:14` | `True` | visual-consistency only |
| 2 | `$1 billion` | `black/K` | `L25/C7` | `Typeka / 1.0` | `black:10` | `True` | L25_should_sell |
| 3 | `Volcano Bonds` | `black/K` | `L27/C9` | `Typeka / 1.0` | `black:13` | `True` | L27_G5_pair, L26_L29_source_band, L25_L32_frame_context |
| 4 | `shitcoiner at heart` | `orange/Y` | `L32/C14` | `Typeka / 1.0` | `yellow:19` | `True` | L32_O5_primary, L25_L32_frame_context |

## Nearby Format Context

| phrase | role | DOCM font | bold | highlight | use |
|---|---|---|---:|---|---|
| `El Salvador` | Typeka Mix nearby anchor | `Typeka Mix` | `0.0` | `{'none': 11}` | context only |
| `Novogratz` | Typeka Mix nearby anchor | `Typeka Mix` | `0.0` | `{'none': 9}` | context only |
| `I don't really trust that guy` | Typeka Mix local phrase | `Typeka Mix` | `0.0` | `{'none': 29}` | context only |
| `IMF loan` | G5 neighbor | `Typeka` | `0.889` | `{'none': 8}` | context only |

## Authority Lock

- Format authority: `DOCM runs + high-res visual highlight consistency + page-76 crop pack/manual boxes`
- Text authority: `canonical_plain + docm_text + markdown_transcript`
- Markdown use: `text/markup transcript only; not font-state authority`
- Annotated transcript use: `format/highlight witness; not exact-prose authority and not selector permission`
- Nearby Typeka Mix use: `I don't really trust that guy` and nearby names are context, not active highlight targets
- Selector unlocked: `False`
- Blocker: The O-B-B-O/Y-K-K-Y format pattern corroborates target identity but still does not name an extraction unit or order beyond the visual order already known.

## Gate Rows

- `format authority`: `pass` - DOCM rows, high-res visual highlight matches, and crop-pack/manual boxes agree on the active target formatting.
- `active pattern`: `pass` - The four locked active targets form O-B-B-O / Y-K-K-Y at page lines 22, 25, 27, and 32.
- `R3 unit/order`: `fail` - Formatting states give target identity only; they do not provide a source-backed word/letter/line/side/index rule.

## Next Move

- Use DOCM/high-res/crop-pack witnesses as format authority for future source comparison. Do not treat Markdown bold, annotated notes, or Typeka Mix context as selector permission without new R3 unit/order evidence.
