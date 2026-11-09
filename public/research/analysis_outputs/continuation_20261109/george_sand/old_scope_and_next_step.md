# George Sand clue: what old code did and what remains

## The newly supplied source changes the investigation

The user supplied a26 December2022 Max Keiser tweet referencing a physical copy, his column, hidden private keys, and [Nick Pelling's George Sand article](https://ciphermysteries.com/2010/05/16/george-sands-cryptography). I independently read the linked page on9 November2026. It describes two distinct mechanisms: selecting alternating complete lines in Sand's letter and taking the first word of every line in Musset's reply. The page's comments document fixes to bolding and a final line break; the latter was corrected on28 December2022. Consequently, exact printed lines matter. This source supports fresh line-based work without the old mandatory-new-scan/R3 gate.

## Old scope, precisely

| Source | Actual scope | Material limit |
|---|---|---|
| `cracker.js:140–151,167–180,262–269` | Raw WIF/64-hex regex on alternating whole-line and first-word streams, plus an acrostic stream. | Heuristic only; no checksum or chain queries here. Word-joined streams retain spaces, so regex does not find an assembled WIF across several words. Its hardcoded article starts on p76, excluding p75. |
| `solver.js:31–69` | Prints odd/even whole lines, first/last words, initials, and a reversed-line variant. | Reads `full_article.txt`, deletes empty lines, has no page-local reset, and does not validate direct private keys in these outputs. |
| `src/main.js:45–101` | BIP39 checks on Sand and first-word strategies. | Mnemonic-focused; requires BIP39 matches rather than literal hidden plaintext/key interpretation. |
| `bip39_hunter.js:160–177` | Counts BIP39 words after alternating-line and first-word selection. | BIP39 word membership rather than a general cipher solution. |
| `scripts/search_structured_candidates.py:118–189` | Strict BIP39 windows from alternating lines and first/last words, including filtered word streams and13-word deletion variants. | Explicitly deletes non-BIP39 words before many checks; uses old transcript. Does not close line-faithful Sand/Musset plaintext or direct-key extraction. |
| `index.html:354–383`; `server.js:109–181` | UI builds12/24-word windows from Sand variants, then checks valid mnemonics and supplied literal WIFs. | Bulk brainwallet checks are explicitly skipped/unimplemented. `server.js:91–93` maps API failures to an empty result, so old UI "no activity" alone is not proof of a successful lookup. |
| `scripts/check_brainwallets.py:41–72` | Hashes title, whole article, highlights, mirror clue and simple variants. | Its source list does not contain Sand/first-word streams. |

Therefore **the old Sand branch was not BIP39-only**, but its direct-private-key coverage was much narrower than the log's broad “ruled out” language suggests.

## Concrete line-fidelity errors

- The scan puts `Really?` and `Yes.` on **one baseline** on p75. `full_article_corrected.txt:3–4` splits them into two. This flips every subsequent global odd/even assignment until another mismatch compensates it.
- `full_article_corrected.txt` omits the p75 title. Its first line begins with the body. Titles must be explicitly included or excluded in a declared rule.
- `cracker.js:4` starts at p76. This is a different source scope from the full article tested by other scripts.
- The Markdown source is not a physical-line transcript: `user_markdown_transcript.md:12` joins several p75 printed lines; line74 joins numerous p77 lines. It cannot serve as the line-cipher authority.
- `canonical_plain_article_body.txt` improves wording and joins `Really? Yes.`, but prepends `OVERDOSE`, `with Max Keiser`, and the title, then removes explicit page boundaries. Its line count requires a new source-layout audit.
- Physical highlighted lines differ from combined highlighted phrases. In p78, `money printing` and `wars to keep it going` share one baseline. On p77, the long Sorry/XRP highlight occupies two lines. On p79, the `infinitely...or gold` span occupies three lines. Earlier combined-span tests do not equal Sand/Musset on physical lines.

## New bounded test completed

`scripts/continuation_george_sand_highlight_lines.py` manually restores46 highlighted fragments into45 physical highlighted baselines. It tests the two linked methods, all/orange/grey text, global/page-local order, and forward/reverse reads. It records both the first word of the highlighted fragment and the first word of the complete printed line containing it. It never deletes words merely because they are absent from BIP39 and never hashes arbitrary prose.

Across540 recorded streams:

- Zero checksum-valid WIFs.
- Zero literal64-hex keys.
- Zero contiguous, unfiltered checksum-valid BIP39 windows.
- One unique22-character minikey checksum hit, occurring twice because two selections overlap. Its one-byte checksum is weak evidence.

`scripts/continuation_george_sand_minikey_check.cjs` then derives that minikey using its standard encoding and checks five conventional address forms. All five have zero confirmed transactions and zero mempool transactions according to the recorded mempool.space responses. See `minikey_activity.json` for UTC check time, exact addresses, source URLs, and raw statistics. This rejects this candidate as a currently funded or previously used puzzle key under those address forms. No transactions were submitted.

## Concrete next step

Create a **scan-faithful per-page body-line transcript** for p75–79, retaining source paragraph boundaries and titles as separately flagged records. Apply Sand's odd/even full-line selection and Musset's first word of **every** line independently, with an explicitly declared body-only page-local reset first. Then test global parity and paragraph-local resets as small, separate variants. Preserve every word and punctuation before any encoding validation. Read intermediate plaintext for an instruction as well as testing direct key formats. This is meaningfully different from the old filtered-BIP39 tests and from the new highlighted-line test.

The supplied clue justifies this test on the existing scans. A new scan or an explicit prose extraction command is not a prerequisite imposed by the puzzle creator.
