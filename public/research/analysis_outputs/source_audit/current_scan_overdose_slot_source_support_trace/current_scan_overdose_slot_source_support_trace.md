# Current Scan OVERDOSE Slot Source-Support Trace

Scope: valid page `75 -> 76` horizontal-mirror light-table geometry only. Each projected OVERDOSE slot was mapped back to its page-75 source band, then checked for source words, instruction terms, and context terms. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T16:53:25`
- Slots traced: `8`
- High source-supported slots: `3` (`O5,S6,E7`)
- High source-supported runs: `OSE@5-7`
- Source word hits / rows: `111` / `58`
- Instruction-like hits / high-slot action-order hits: `1` / `0`
- Unit-only terms: `words`
- Context hits: `2` (`bitcoin, bitcoins`)
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `slots=8|highSrc=3|highRun=OSE@5-7|highSlots=O5,S6,E7|words=111|wordRows=58|instructionLike=1|actionOrder=0|highActionOrder=0|unitOnly=words|context=2|sourceR3=0|triggers=0/9|selectors=0`

## Slot Rows

| slot | source-supported share | target-only share | source x band | words | rows | instruction-like | action/order | context | source text preview |
|---|---:|---:|---|---:|---:|---|---|---|---|
| `O0` | `5.7e-05` | `0.9814` | `2005-2250` | 0 | 0 | `-` | `-` | `-` |  |
| `V1` | `0.020364` | `0.957363` | `1761-2005` | 0 | 0 | `-` | `-` | `-` |  |
| `E2` | `0.32972` | `0.650683` | `1516-1761` | 12 | 7 | `-` | `-` | `-` | (MRERREIGStY epithet. mEthereum lab. bare if this hard to listen shitcoiners unloved. |
| `R3` | `0.417748` | `0.566246` | `1272-1516` | 17 | 8 | `-` | `-` | `-` | (MRERREIGStY at the mEthereum experience. with your rabbit hole hearing is hard men and shitcoiners and unloved. |
| `D4` | `0.475111` | `0.507683` | `1027-1272` | 20 | 10 | `-` | `-` | `bitcoins` | up with the of stake at shitcoinery. Maximalist, Satoshi digging blindly Bitcoin's rabbit worth hearing from con men the gullible |
| `O5` | `0.666921` | `0.318052` | `783-1027` | 24 | 11 | `words` | `-` | `-` | Buterin came up slinging proof or shitcoinery. dignity. Toxic Maximalist, of the whole be digging muck of true. Anything pleasant words listening for the |
| `S6` | `0.948586` | `0.035701` | `538-783` | 27 | 11 | `-` | `-` | `bitcoin` | Vitalik Buterin Now he's slinging Don't fa Keep your dignity. Go Bitcoin the BSR You wouldn't hands in the weren't true. to. Nice, pleasant are easy listening |
| `E7` | `0.791745` | `0.188936` | `294-538` | 11 | 11 | `-` | `-` | `-` | Vitalik Now Don't Keep Go the You hands weren't to. are |

## Decision

- `overdose_slot_source_support_is_page75_text_band_no_selector`.
- Reason: The high source-supported OVERDOSE slots form a contiguous OSE run, but their mirrored source bands contain ordinary page-75 prose/context, not a source-backed unit/order instruction.
- Next move: Treat these OVERDOSE slots as a useful source-support control, not as an extraction selector; stop varying light-table blend/slot opacity unless a new source or clue names unit, transform, and read order.

Sheet: `analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/current_scan_overdose_slot_source_support_trace_sheet.jpg`
