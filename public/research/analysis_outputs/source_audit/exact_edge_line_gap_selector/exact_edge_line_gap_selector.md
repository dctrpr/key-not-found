# Exact-Edge Line/Gap Selector

Scope: test whether the exact-edge line numbers `25,27,32`, corridor numbers `7,9,14`, and gaps `2,5` act as a simple local selector inside the page-76 corridor. No key derivation was run.

- Created: `2026-05-20T09:05:19`
- Exact trio: `should sell | Volcano Bonds | shitcoiner at heart`
- Page line numbers: `[25, 27, 32]`
- Corridor numbers: `[7, 9, 14]`
- Gap numbers: `[2, 5]`

## Operations

| operation | reason | output | instruction hits | letters |
|---|---|---|---|---:|
| `numbers_as_letters` | map page lines, corridor lines, and gaps through A1Z26 | `page=YAF corridor=GIN gaps=BE` | `[]` | 24 |
| `numbers_as_letters_reversed` | same A1Z26 streams in mirror order | `page=FAY corridor=NIG gaps=EB` | `[]` | 24 |
| `gap_words_on_exact_lines` | take words 2 and 5 from each exact-edge line | `billion that | Volcano pay | because shitcoiner` | `[]` | 38 |
| `gap_words_on_highlighted_corridor_lines` | take words 2 and 5 from every highlighted corridor line | `taunting them | billion that | Volcano pay | and of | in figuring | moved I | because shitcoiner` | `[]` | 71 |
| `gap_words_in_exact_stream` | take words 2 and 5 from the exact trio stream | `sell shitcoiner` | `[]` | 14 |
| `corridor_numbers_as_lines` | use 7, 9, 14 as corridor line selectors | `L25/C7: $1 billion in bitcoin — that he should sell | L27/C9: collateralized “Volcano Bonds” to pay off the IMF | L32/C14: Maybe because he's a shitc...` | `[]` | 122 |
| `page_numbers_wrapped_to_corridor_lines` | wrap page line numbers 25, 27, 32 through the 14-line corridor | `L29/C11: Novogratz in the tweet, figuring he could sell a | L31/C13: hasn't moved on it. I don't really trust that guy. | L22/C4: He's taunting them,...` | `[]` | 134 |
| `corridor_numbers_as_interval_words` | use 7, 9, 14 as word selectors in the G5-to-O5 interval | `the loan those` | `[]` | 12 |
| `page_numbers_as_interval_words` | use 25, 27, 32 as word selectors in the G5-to-O5 interval | `could a Street` | `[]` | 12 |
| `gap_jump_forward` | start at should-sell, jump +2 to Volcano, then +5 to heart | `L25/C7: $1 billion in bitcoin — that he should sell -> L27/C9: collateralized “Volcano Bonds” to pay off the IMF -> L32/C14: Maybe because he's a shi...` | `[]` | 122 |
| `gap_jump_backward` | mirror the same gap walk backward from heart | `L32/C14: Maybe because he's a shitcoiner at heart. -> L27/C9: collateralized “Volcano Bonds” to pay off the IMF -> L25/C7: $1 billion in bitcoin — th...` | `[]` | 122 |
| `same_phrase_wrapped_chars_by_page_line` | use page line number as wrapped character index inside each exact phrase | `lla` | `[]` | 3 |
| `same_phrase_wrapped_chars_by_corridor_line` | use corridor number as wrapped character index inside each exact phrase | `soe` | `[]` | 3 |

## Assessment

- A1Z26 number streams are short fragments (`YAF`, `GIN`, `BE`) and do not read as an instruction.
- Words 2 and 5 from the exact lines produce ordinary corridor fragments (`billion that`, `Volcano pay`, `because shitcoiner`).
- The gap walk only restates the known locator path from `should sell` to `Volcano Bonds` to `shitcoiner at heart`.
- Wrapped line numbers and interval word indexes produce ordinary text, not a rule naming word, letter, key, mirror, or direction.

## Next Move

- Close exact-edge line/corridor numbers and gaps as a direct numeric selector. Keep the 2/5 gaps only as structural locator evidence for the p76 lower corridor.
