# Original Clue Provenance

Scope: recover raw source-level clue text from public oEmbed payloads and expand the short links. No key derivation was run.

- Created: `2026-05-20T04:01:30`

## Tweets

### announcement

- tweet id: `1632068898169450497`
- source URL: `https://twitter.com/maxkeiser/status/1632068898169450497`
- recovered text: `“I hid a private #Bitcoin key encoded in this piece I wrote for @BitcoinMagazine Mr. President. Nobody’s figured it out yet, but it’s for 20 BTC” pic.twitter.com/eiSeo82gxP`
- oEmbed final URL: `https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Fmaxkeiser%2Fstatus%2F1632068898169450497&omit_script=true&dnt=true`
- used unverified SSL fallback: `True`
- links:
  - `https://twitter.com/hashtag/Bitcoin?src=hash&ref_src=twsrc%5Etfw`
  - `https://twitter.com/BitcoinMagazine?ref_src=twsrc%5Etfw`
  - `https://t.co/eiSeo82gxP`
  - `https://twitter.com/maxkeiser/status/1632068898169450497?ref_src=twsrc%5Etfw`

### schott_mirror_clue

- tweet id: `1632391507008278528`
- source URL: `https://twitter.com/maxkeiser/status/1632391507008278528`
- recovered text: `“Mirror writing: neurological reflections on an unusual phenomenon”https://t.co/WkSDXKwSiv https://t.co/3NrEhxV2Iz`
- oEmbed final URL: `https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Fmaxkeiser%2Fstatus%2F1632391507008278528&omit_script=true&dnt=true`
- used unverified SSL fallback: `True`
- links:
  - `https://t.co/WkSDXKwSiv`
  - `https://t.co/3NrEhxV2Iz`
  - `https://twitter.com/maxkeiser/status/1632391507008278528?ref_src=twsrc%5Etfw`

## Short-Link Expansions

- `https://t.co/3NrEhxV2Iz` -> `https://x.com/maxkeiser/status/1632068898169450497` (status=200, unverifiedSsl=True)
- `https://t.co/WkSDXKwSiv` -> `https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/` (status=200, unverifiedSsl=True)
- `https://t.co/eiSeo82gxP` -> `https://x.com/maxkeiser/status/1632068898169450497/photo/1` (status=200, unverifiedSsl=True)

## Assessment

- The announcement tweet is recoverable as raw oEmbed and repeats the private-key/source/20 BTC statement.
- The Schott clue tweet is recoverable as raw oEmbed and quotes the exact paper title.
- The Schott clue tweet short links expand to the PMC paper and back to the original announcement tweet, confirming it is an instruction pointer tied to the same puzzle source.
- No additional selector words are present in the recovered tweet text itself.
- This strengthens the Schott/mirror clue as intentional source provenance, but it does not by itself choose source layer, target ordering, or extraction unit.
- Next best move: use this recovered clue text as the canonical clue record and avoid paraphrase drift; source acquisition still means higher-resolution Canva/original layout/physical magazine evidence.
