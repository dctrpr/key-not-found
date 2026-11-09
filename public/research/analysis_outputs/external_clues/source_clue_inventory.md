# Source Clue Inventory

Run time: Wed May 20 02:18:12 CEST 2026

## Scope

Checked the local external-clue material before opening another candidate-generation branch:

- recovered ThreadReader announcement report
- recovered media sequence mapping
- Schott mirror-writing literal experiment report
- OVERDOSE series title/key-check report
- raw ThreadReader HTML around the extra media URLs

## Findings

### Announcement Text

The only recovered written announcement clue remains:

> I hid a private #Bitcoin key encoded in this piece I wrote for @BitcoinMagazine Mr. President. Nobody’s figured it out yet, but it’s for 20 BTC

This gives target type and source, but no explicit selector beyond the later Schott/mirror clue.

### True Announcement Media

The actual 2023 announcement thread media set is seven images:

1. Max holding the OVERDOSE spread with Bukele.
2. Max and Bukele in front of the El Salvador presidential seal.
3. Stacy Herbert portrait.
4. Max and Bukele holding the Bitcoin Magazine El Salvador issue.
5. Max/Stacy/driver car photo.
6. Stacy in bathtub/lava/El Salvador flag composite.
7. Bitcoin symbols erupting from a volcano.

These repeatedly reinforce the page-76 corridor:

- President of El Salvador
- IMF / Twitter
- "buying the dip"
- President Nayib Bukele
- volcanoes
- $1 billion
- Volcano Bonds
- IMF loan

### ThreadReader Noise

Two local media files are not part of the 2023 puzzle announcement:

- `08_EmQGt1qVoAAU-iB.jpg`
- `09_EmQWsdEWEAAB38H.jpg`

They appear in `analysis_outputs/source_audit/thread_1632068898169450497.html` inside a lower related-thread card for Max's November 7, 2020 thread `1325191578818908160`, not inside the March 2023 six-tweet puzzle thread. They should be excluded from future clue ordering and media-derived candidate checks.

### Schott Literal Branch

The Schott report already tested the five strongest literal interpretations:

- hold-to-light leaf pairs
- character/word reversal
- bimanual interleaving
- visual letter-diff streams
- strict BIP39 ray interception

Result: 66 streams, 708 private-key candidates, 3540 private-key addresses, no activity; no strict BIP39 mnemonic candidates. This branch should stay closed unless a new physical/source alignment changes the selected text.

### OVERDOSE Series Branch

The OVERDOSE title check included `Bitcoin Is A Mirror That Reflects All`, joined/reversed series titles, announcement-plus-title strings, inscription block/tx/hash, and related phrases.

Result: 384 candidate private keys, 1920 addresses, no activity. Treat the recurring OVERDOSE/mirror title as thematic support, not a direct key source.

## Conclusion

The local source inventory does not contain a missing written instruction. It strengthens, but does not solve, the current model:

- source is the Bitcoin Magazine piece;
- public clue is mirror writing / Schott;
- recovered media targets the page-76 Bukele/IMF/volcano corridor;
- extra ThreadReader media 08/09 are unrelated noise;
- literal string/key transformations and OVERDOSE-title derivations are ruled out.

## Next Best Move

Stop using local external-clue files as candidate material. The next high-value step is source acquisition/verification:

1. inspect the original Canva/browser clue manually for any visual instruction not represented in local files;
2. obtain or create a physical magazine scan/photo of pages 75-80, especially the front/back leaf pairs and true spreads;
3. only then rerun alignment/selector extraction on page 76.

Until that source gap is closed, the best local follow-up is a small hygiene task: update media scripts and reports so files 08/09 are explicitly ignored.

## 2026-05-20 Addendum: Raw Clue oEmbed Archived

See `analysis_outputs/external_clues/original_clue_provenance.md`.

- Announcement tweet `1632068898169450497` was recovered through public oEmbed.
- Schott clue tweet `1632391507008278528` was recovered through public oEmbed.
- `https://t.co/WkSDXKwSiv` expands to `https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/`.
- `https://t.co/3NrEhxV2Iz` expands back to `https://x.com/maxkeiser/status/1632068898169450497`.
- This promotes the Schott clue from log paraphrase to archived source evidence, but it still supplies no extra selector words beyond the paper title and source-link relationship.

## 2026-05-20 Addendum: Schott Concept Distillation

See `analysis_outputs/external_clues/schott_instruction_distillation.md`.

- The linked Schott paper emphasizes mirror/reversal, left-hand/handedness, Leonardo, bimanual movement, corpus callosum, and right-hemisphere concepts.
- This supports physical/visual mirroring and left/right or cross-page interaction.
- It does not choose a source layer, order, or extraction unit.
- Do not treat Schott keyword counts as key material; use the paper only to constrain future human-readable selector rules.

## 2026-05-20 Addendum: Announcement Opener Spread

See `analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.md`.

- The first announcement image shows Max holding the physical `OVERDOSE` opener spread.
- That spread corresponds to `magazine.pdf` PDF pages 1-2, before the body pages mapped as article pages 75-80.
- Track these as opener pages 73-74: page 73 contains `OVERDOSE`, pills, and cash; page 74 contains the field/cash illustration.
- This does not replace page 76 as the strongest text target, but it adds an overlooked source/provenance layer to the model.
