# Source Packet Highlight Count Slot Permutation Control

Scope: mapped existing active phrase count metrics to the eight `OVERDOSE` slots with zero-based and one-based modulo, then checked canonical and bounded active-order permutations for layout/instruction/fold-world streams. No OCR-to-key extraction, key candidates, hash search, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T20:13:41`
- Metrics / index modes / canonical streams: `10` / `2` / `20`
- Canonical layout / instruction / fold-world hits: `0` / `0` / `0`
- Interesting permutation rows / fold-world hits / layout hits: `5` / `5` / `0`
- All-active center-fit metrics / max active center fit: `0` / `2/4`
- Source count-cue hits / source-backed R3 / satisfied triggers / selectors: `0` / `0` / `0/9` / `0`
- Fingerprint: `metrics=10|indexModes=2|canonical=20|permRows=5|canonLayout=0|canonInstr=0|canonFold=0|permFold=5|permLayout=0|allCenterFit=0|maxCenterFit=2/4|sourceCountCues=0|sourceR3=0|triggers=0/9|selectors=0`

## Canonical Active Streams

| metric | mode | stream | layout | instruction | fold-world |
|---|---|---|---|---|---:|
| `wordCount` | `zero_based_mod8` | `REER` | `-` | `-` | `0` |
| `wordCount` | `one_based_mod8` | `EVVE` | `-` | `-` | `0` |
| `spanSlotCount` | `zero_based_mod8` | `REER` | `-` | `-` | `0` |
| `spanSlotCount` | `one_based_mod8` | `EVVE` | `-` | `-` | `0` |
| `alnumCount` | `zero_based_mod8` | `DODV` | `-` | `-` | `0` |
| `alnumCount` | `one_based_mod8` | `RERO` | `-` | `-` | `0` |
| `glyphNoSpaceCount` | `zero_based_mod8` | `DVDV` | `-` | `-` | `0` |
| `glyphNoSpaceCount` | `one_based_mod8` | `RORO` | `-` | `-` | `0` |
| `docmHighlightCount` | `zero_based_mod8` | `SEOR` | `-` | `-` | `0` |
| `docmHighlightCount` | `one_based_mod8` | `OVDE` | `-` | `-` | `0` |
| `firstWordLen` | `zero_based_mod8` | `SEEE` | `-` | `-` | `0` |
| `firstWordLen` | `one_based_mod8` | `OVSV` | `-` | `-` | `0` |
| `lastWordLen` | `zero_based_mod8` | `REOO` | `-` | `-` | `0` |
| `lastWordLen` | `one_based_mod8` | `ESDD` | `-` | `-` | `0` |
| `minWordLen` | `zero_based_mod8` | `REOE` | `-` | `-` | `0` |
| `minWordLen` | `one_based_mod8` | `EVDV` | `-` | `-` | `0` |
| `maxWordLen` | `zero_based_mod8` | `SEEE` | `-` | `-` | `0` |
| `maxWordLen` | `one_based_mod8` | `OSSV` | `-` | `-` | `0` |
| `sumWordLengths` | `zero_based_mod8` | `DVDV` | `-` | `-` | `0` |
| `sumWordLengths` | `one_based_mod8` | `RORO` | `-` | `-` | `0` |

## Fold-World Permutation Hits

| metric | mode | order | stream |
|---|---|---|---|
| `docmHighlightCount` | `one_based_mod8` | `O4,B4,O5,G5` | `OVED` |
| `docmHighlightCount` | `one_based_mod8` | `O4,G5,O5,B4` | `ODEV` |
| `docmHighlightCount` | `one_based_mod8` | `O4,O5,B4,G5` | `OEVD` |
| `docmHighlightCount` | `one_based_mod8` | `B4,O5,G5,O4` | `VEDO` |
| `docmHighlightCount` | `one_based_mod8` | `G5,O5,B4,O4` | `DEVO` |

## Center-Fit Summary

| metric | mode | active hits | grey-control hits |
|---|---|---:|---:|
| `wordCount` | `zero_based_mod8` | `1/4` | `2/13` |
| `wordCount` | `one_based_mod8` | `1/4` | `3/13` |
| `spanSlotCount` | `zero_based_mod8` | `1/4` | `1/13` |
| `spanSlotCount` | `one_based_mod8` | `1/4` | `2/13` |
| `alnumCount` | `zero_based_mod8` | `0/4` | `3/13` |
| `alnumCount` | `one_based_mod8` | `0/4` | `1/13` |
| `glyphNoSpaceCount` | `zero_based_mod8` | `1/4` | `4/13` |
| `glyphNoSpaceCount` | `one_based_mod8` | `0/4` | `3/13` |
| `docmHighlightCount` | `zero_based_mod8` | `0/4` | `0/0` |
| `docmHighlightCount` | `one_based_mod8` | `2/4` | `0/0` |
| `firstWordLen` | `zero_based_mod8` | `1/4` | `3/13` |
| `firstWordLen` | `one_based_mod8` | `2/4` | `1/13` |
| `lastWordLen` | `zero_based_mod8` | `0/4` | `2/13` |
| `lastWordLen` | `one_based_mod8` | `1/4` | `5/13` |
| `minWordLen` | `zero_based_mod8` | `0/4` | `2/13` |
| `minWordLen` | `one_based_mod8` | `1/4` | `4/13` |
| `maxWordLen` | `zero_based_mod8` | `1/4` | `4/13` |
| `maxWordLen` | `one_based_mod8` | `1/4` | `3/13` |
| `sumWordLengths` | `zero_based_mod8` | `1/4` | `4/13` |
| `sumWordLengths` | `one_based_mod8` | `0/4` | `1/13` |

## Decision

- `source_packet_highlight_count_slot_permutation_no_selector`
- Canonical active order does not produce `OVER`, `DOSE`, a hard instruction stream, or one of the fold-world streams.
- The only fold-world stream hits come from one-based `docmHighlightCount` under arbitrary active target permutations, not from a source-backed order; canonical `docmHighlightCount` gives `OVDE`.
- Existing source count/length cue hits remain 0, source-backed R3 remains 0, and reopen triggers remain 0/9.

## Next Move

- Do not use phrase counts, character counts, or highlight counts as extraction rules without a source clue naming count/length/highlight-count and target order.
- Highest-value direction remains distinct physical/original-layout/source evidence or raw clue wording that supplies the missing unit/order.
