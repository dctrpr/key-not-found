# Online article comparison

This URL is **a different article**, not an online version of Issue #24’s *Bitcoin Is Toxic AF*.

[Official article](https://bitcoinmagazine.com/culture/max-keiser-el-salvador-bitcoin-maximalism): **El Salvador Should Embrace Bitcoin Maximalism**, by **Max Keiser**, published **April 29, 2022**. The [native WordPress response](https://bitcoinmagazine.com/wp-json/wp/v2/posts?slug=max-keiser-el-salvador-bitcoin-maximalism) identifies post `9664` and publication time `17:00:00 GMT`.

Comparison with `full_article_corrected.txt`:

| Check | Online article | Local puzzle article |
|---|---:|---:|
| Lexical tokens | 352 | 1,259 |
| Longest shared consecutive word run | 3 | 3 |
| `10years`, `Schiff`, `42%`, `Volcano Bonds` | Absent | Present |
| `toxic`, `bitter truth`, `20,000`, `100,000` | Absent | Present |

Native article content has 19 paragraph tags, zero explicit line-break tags, and zero strikethrough tags. HTML source wrapping therefore supplies no printed-line authority or evidence about the puzzle’s Schiff edit.

Preserved files:

- `wordpress_api_response.json`: exact public API response.
- `wordpress_article_body.html`: native content markup.
- `wordpress_article_text.txt`: paragraph-preserving text.
- `variant_0.html`, `variant_3.html`: retrieved rendered HTML.
- `comparison.json`: reproducible comparison metrics.
- `fetch_attempts.json`: retrieval outcomes.

No author manuscript or new puzzle encoding was established.
