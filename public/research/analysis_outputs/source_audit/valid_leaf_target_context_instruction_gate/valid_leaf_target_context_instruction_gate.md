# Valid Leaf Target Context Instruction Gate

Scope: classified target-side context words in the valid page 75 -> page 76 held-to-light line-band trace, especially article words that can look procedural (`sell`, `mine`, `heart`). No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.

- Created: `2026-05-24T08:11:16`
- Decision: `valid_leaf_target_context_instruction_no_selector`
- Trace rows: `8`
- Target context carrier rows: `6`
- Target context terms: `bitcoin, bukele, imf, mine, sell, volcano`
- Phrase context terms: `billion, bond, dip, heart, shitcoiner, volcano`
- Target-only context carrier rows: `6`
- Source-backed context carrier rows: `1`
- Action / unit / order carrier rows: `0` / `0` / `0`
- Instruction candidate rows: `0`
- Source-backed instruction candidate rows: `0`
- All-four active targets covered by target context carriers: `False`
- All-four active targets covered by instruction candidates: `False`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/valid_leaf_target_context_instruction_gate_sheet.jpg`
- Fingerprint: `rows=8|ctxRows=6|lineTerms=bitcoin,bukele,imf,mine,sell,volcano|phraseTerms=billion,bond,dip,heart,shitcoiner,volcano|targetOnly=6|sourceCtx=1|sourceCtxTerms=bitcoin|action=0|unit=0|order=0|instr=0|sourceInstr=0|all4ctx=0|all4instr=0|sourceR3=0|triggers=0/9|selectors=0`

## Target Context Rows

| mode | target | target lines | target context | source-backed context | action | unit | order | target text |
|---|---|---:|---|---|---|---|---|---|
| `valid_75_to_76_natural` | `O4` | 23,24,25 | `bukele,imf` | `-` | `-` | `-` | `-` | trolling the International Monetary Fund (IMF) on Twitter? / He's taunting them, telling them he's ByiiREeraipy" / I tweeted President Nayib Bukele when he announced |
| `valid_75_to_76_natural` | `B4` | 26,27,28 | `bitcoin,mine,sell,volcano` | `-` | `-` | `-` | `-` | he was going to tap his nation's volcanoes to mine / eis in bitcoin that he should sell / billions worth of future bitcoin earnings |
| `valid_75_to_76_natural` | `G5` | 28,29,30 | `bitcoin,imf` | `-` | `-` | `-` | `-` | billions worth of future bitcoin earnings / collateralized to pay off the IMF / loan and get rid of those leeches. I tagged Mike |
| `valid_75_to_76_small_jitter_best` | `O4` | 23,24,25 | `bukele,imf` | `-` | `-` | `-` | `-` | trolling the International Monetary Fund (IMF) on Twitter? / He's taunting them, telling them he's ByiiREeraipy" / I tweeted President Nayib Bukele when he announced |
| `valid_75_to_76_small_jitter_best` | `B4` | 26,27,28 | `bitcoin,mine,sell,volcano` | `-` | `-` | `-` | `-` | he was going to tap his nation's volcanoes to mine / eis in bitcoin that he should sell / billions worth of future bitcoin earnings |
| `valid_75_to_76_small_jitter_best` | `G5` | 28,29,30 | `bitcoin,imf` | `bitcoin` | `-` | `-` | `-` | billions worth of future bitcoin earnings / collateralized to pay off the IMF / loan and get rid of those leeches. I tagged Mike |

## Decision

- The target-side context terms are ordinary page-76 article context, not extraction grammar.
- `sell` and `mine` occur in the B4 article lines (`he was going to tap his nation's volcanoes to mine` / `eis in bitcoin that he should sell`), but they are content verbs and do not pair with a unit/order such as word, letter, line, first, last, left, or right.
- `heart` appears in the known O5 phrase label (`shitcoiner at heart`) but not as a readable target-side line-band context term in the current trace row.
- Only one row has exact source-backed context (`bitcoin` in the small-jitter G5 row), and it is still context only with no instruction grammar.
- Keep valid 75->76 target-side line-band context closed as prose/context, not a selector.

## Next Move

- Do not reopen held-to-light line-band extraction from target context words. Best direction remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.
