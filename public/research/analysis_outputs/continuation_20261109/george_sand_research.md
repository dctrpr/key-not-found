# George Sand clue — primary verification, 2026-11-09

## Result

The user-supplied December 26, 2022 post is authentic in X's current public oEmbed and syndication responses. It materially strengthens the case for text/printed-line steganography and supplies a creator-backed extraction family. The investigation should no longer describe the source corpus as lacking any line/word/unit/order clue.

## Preserved primary responses

- `max_1607378060172460032_oembed.json`
- `max_1607378060172460032_syndication.json`

Original post: https://x.com/maxkeiser/status/1607378060172460032

Public transport endpoints used:

- https://publish.twitter.com/oembed?url=https://twitter.com/maxkeiser/status/1607378060172460032
- https://cdn.syndication.twimg.com/tweet-result?id=1607378060172460032&token=0&lang=en

Syndication reports `created_at=2022-12-26T14:09:27.000Z`, creator handle `maxkeiser`, post ID `1607378060172460032`, and `isEdited=false`. Its expanded URL resolves the linked short URL `WFuYviL30N` to the exact CipherMysteries article supplied by the user.

The post asks about physical Bitcoin Magazine copies and Max's column, compares its mechanism to George Sand, and claims hidden private keys in the text. It refers to keys in the plural. It does **not** name an issue, article title, specific printed page, target address, derivation path, or a 20-BTC prize.

The attached poll has four answers:

1. Wait… Wat?!
2. Yes, I found 10 BTC
3. Not yet
4. Buccaneers in playoffs

Poll duration was 24 hours, ending December 27 at 14:09:27 UTC. Its answers are not authenticated claims of successful solutions. The 10-BTC figure occurs in an answer choice, so do not infer that the later March 2023 20-BTC claim is necessarily the same wallet, a doubled prize, or two 10-BTC keys.

## The exact linked mechanisms

Source: [Nick Pelling, George Sand’s cryptography!, May 16, 2010](https://ciphermysteries.com/2010/05/16/george-sands-cryptography).

The page reproduces three messages. The first has a cover message whose **complete odd-numbered lines** form a second message; currently it is 23 lines, so the selected lines are 1,3,…23. The second hides a question in the **first word of every line** across eight lines. The final two-line reply uses the same first-word operation to say when.

Two comments explicitly clarify formatting: a 2010 reader corrects the first example from first words to whole odd lines, and Pelling says he fixed it. A December 28, 2022 reader points out that the final word of the first example needs its own line; Pelling again records a correction. This is two days after Max linked the page, so current lineation is not proof of exactly what Max saw. None of the examples uses SHA256 or a blockchain-specific cipher. The page is a primary source for the mechanism Max linked; it does not establish historical authenticity of the attributed correspondence.

## Relationship to the magazine and March clue

The December post is broad: physical copies, column, and plural keys. The later [March 4, 2023 announcement](https://x.com/maxkeiser/status/1632068898169450497) points visually at the El Salvador Issue spread and uses a singular private key and 20 BTC. The [March 5 mirror-writing clue](https://x.com/maxkeiser/status/1632391507008278528) links back to that March announcement. The December mechanism is therefore relevant creator evidence but its applicability specifically to Issue #24 remains an inference.

There was at least one different Max column by December 2022: [Bitcoin Magazine's official Fall 2022 Orange Party issue contents](https://bitcoinmagazine.com/2022-orange-party-issue) names an OVERDOSE article about banana republics and centralizing power. This rules out treating the December post as uniquely identifying Issue #24. The official store also lists [Issue #24](https://store.bitcoinmagazine.com/products/el-salvador-issue), [Issue #25](https://store.bitcoinmagazine.com/products/bitcoin-magazine-issue-25), and [Issue #26](https://store.bitcoinmagazine.com/products/copy-of-bitcoin-magazine-issue-26) as early 2022 issues; that chronology alone does not show that each contains a key or identify each column's title.

Local `src/main.js`, `src/utils/ciphers.js`, and `cracker.js` already implement operations named George Sand, odd/even lines, and first words. A bounded text search found no preserved December post ID or exact George Sand creator wording in the copied logs/reports available during this pass. Thus the algorithm family was known, but its creator authority was not visible in those later source-gate summaries. Checking a generic transcript with these functions does not exhaust the printed-line mechanism.

## Concrete implications for the next experiment

1. Derive canonical **printed lines and columns** from the scan, preserving hyphenation and wrapping, rather than substituting the application's reflowed or Markdown paragraph breaks.
2. Test first-word extraction and odd/even full-line selection with declared page/column reset conventions. Combine only a small set of mirror-directed reversals: right-edge last words, reversed line order, and reverse character reading. Save the exact streams so another person can reproduce them.
3. Distinguish an intermediate readable instruction from a final private key. An arbitrary valid scalar or short numeric hash is not confirmation; a reproducible checksum-bearing encoding, a funded matching address, or an independently named target is substantially stronger.
4. Preserve other pre-December-2022 OVERDOSE columns as a separate question. The plural wording creates a legitimate scope question; it does not authorize conflating unrelated columns into a key.

[Private context omitted from this public copy.]