# The archived George Sand examples

The 26 December 2022 capture preserves the linked article at 15:16:50 UTC, 67 minutes and 23 seconds after Keiser posted at 14:09:27 UTC. The archived opening letter has 22 explicit HTML lines. Lines 1, 3 and each subsequent odd line through 21 are bold. The final word sits on unmarked line 22. The current page moves that word onto a new line 23 and marks it bold. Its first 21 rows match the archived version. [Creator post](https://x.com/maxkeiser/status/1607378060172460032) · [Same-day capture](https://web.archive.org/web/20221226151650/https://ciphermysteries.com/2010/05/16/george-sands-cryptography)

The 26 January 2021 capture has the same normalized rows and marks as the same-day capture in all three quotation blocks. The second and third blocks retain their 9 and 2 explicit lines in the current page. The nine-line example marks the first words of its first eight lines. Its final line is unmarked. The article author confirmed the final-word correction in the 28 December 2022 comment thread. [Earlier capture](https://web.archive.org/web/20210126163451/http://ciphermysteries.com/2010/05/16/george-sands-cryptography) · [Current article](https://ciphermysteries.com/2010/05/16/george-sands-cryptography) · [Author confirmation](https://ciphermysteries.com/2010/05/16/george-sands-cryptography#comment-480459)

The capture fixes explicit source breaks at the archive time. Keiser’s exact CMS state at posting, personal view and viewport wrapping remain unknown. The relationship between these examples and the later Issue 24 claim remains unresolved. The earlier creator analysis describes the two reading families already considered. [Historical creator analysis](../../continuation_20261109/george_sand_research.md)

## Source identities

| Source | Recorded time | Raw HTML SHA-256 |
| --- | --- | --- |
| [Earlier archive](https://web.archive.org/web/20210126163451/http://ciphermysteries.com/2010/05/16/george-sands-cryptography) | 2021-01-26 16:34:51 UTC | `c8222a1debad6e62f451090ee978d021f04bd0cbc78d5e3891c3879b58c415ef` |
| [Same-day archive](https://web.archive.org/web/20221226151650/https://ciphermysteries.com/2010/05/16/george-sands-cryptography) | 2022-12-26 15:16:50 UTC | `fc27e630115adf842a53d51fea2ad288b7f7d2df96ffe72fa4260559d3e5cca7` |
| [Current page](https://ciphermysteries.com/2010/05/16/george-sands-cryptography) | Retrieved 2026-11-11 | `d18d779c29ed60250a5b583c0ad1999f89f798cb4dd8e1f151c6367688b113b3` |

| Quotation block | Archived lines | Both archived quote digests | Current lines | Current quote digest |
| --- | ---: | --- | ---: | --- |
| 1 | 22 | `d8049c53e1ecc547c40c0d2f9942d3208b792099e812e73fb911af236d1d869f` | 23 | `fad148d69c032ea26f50a6d315d1c08543ad09f8ab6eedbdf74cec09bffef9fa` |
| 2 | 9 | `393d3d910983d610c3b8f95c2e36a213b7f73de48c911a27c073c80ead4fad69` | 9 | `393d3d910983d610c3b8f95c2e36a213b7f73de48c911a27c073c80ead4fad69` |
| 3 | 2 | `516324b90333ae689ffcc9f651ba4cf5521c0f6c50d1a309fcd5228477354d9a` | 2 | `516324b90333ae689ffcc9f651ba4cf5521c0f6c50d1a309fcd5228477354d9a` |

## Reproduction

The parser takes explicit rows from `br` elements inside the three `blockquote` blocks. It collapses whitespace in each row and its `strong` or `b` text, then hashes the resulting pairs as compact UTF-8 JSON. The two saved comparisons reproduced byte for byte. The public receipts carry row counts, marked line numbers and digests. Fresh retrievals can change the archive wrapper or current article bytes. Use the recorded raw hashes for byte-identical replay. [Parser](../../../scripts/audit_sand_quote_markup.py) · [Same-day comparison](SAME_DAY_COMPARISON.json) · [Earlier comparison](EARLIER_COMPARISON.json)

From the repository root, set `SAME_DAY_HTML`, `EARLIER_HTML` and `CURRENT_HTML` to saved HTML responses from the corresponding URLs above.

```sh
python3 public/research/scripts/audit_sand_quote_markup.py "$SAME_DAY_HTML" "$CURRENT_HTML"
python3 public/research/scripts/audit_sand_quote_markup.py "$EARLIER_HTML" "$CURRENT_HTML"
```

The report was verified and finalized at 2026-11-11T01:39:56.748Z. [Machine result](RESULT.json)
