# P80 Symptom Relief Rule Audit

Scope: test page-80 `5 SYMPTOM RELIEF` as a literal remove/relieve operation on page-76 highlight units. No key candidates were generated.

- Created: `2026-05-20T13:11:03`
- Symptoms: `NAUSEA, HEARTBURN, INDIGESTION, UPSET STOMACH, SHITCOINS`
- Package action terms: `relief, reliever, fixes, proof, work, anti, fake`
- Explicit extraction terms on package: `none`

## Direct Symptom Matches

| symptom | unit | hits | relieved literal | relieved all | instruction hits |
|---|---|---|---|---|---|
| HEARTBURN | `O1_2` `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` | `heart` | `Get some toxicity. Get some bitcoin. Open your to Bitcoin.` | `Get some toxicity. Get some bitcoin. Open your to Bitcoin.` | `none` |
| HEARTBURN | `O5` `shitcoiner at heart.` | `heart` | `shitcoiner at.` | `shitcoiner at.` | `none` |
| UPSET STOMACH | `B3` `It's a stun gun to the genitals` | `semantic:genitals` | `It's a stun gun to the genitals` | `It's a stun gun to the` | `none` |
| SHITCOINS | `O5` `shitcoiner at heart.` | `shitcoiner, shitcoin` | `at heart.` | `at heart.` | `none` |

## Forced Five-Order Relief

| symptom | target unit | changed | relieved text | initials |
|---|---|---:|---|---|
| NAUSEA | `O1_2` `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` | `False` | `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` | `GstGsbOyhtB` |
| HEARTBURN | `O3` `by the rancid catnip of fiat money.` | `False` | `by the rancid catnip of fiat money.` | `btrcofm` |
| INDIGESTION | `O4` `“buying the dip.”` | `False` | `“buying the dip.”` | `btd` |
| UPSET STOMACH | `B3` `It's a stun gun to the genitals` | `False` | `It's a stun gun to the genitals` | `Iasgttg` |
| SHITCOINS | `B4` `$1 billion` | `False` | `$1 billion` | `$b` |

## Streams

- `directLiteralRelief` hits `none`: `Get some toxicity. Get some bitcoin. Open your to Bitcoin. | shitcoiner at. | It's a stun gun to the genitals | at heart.`
- `directAllRelief` hits `none`: `Get some toxicity. Get some bitcoin. Open your to Bitcoin. | shitcoiner at. | It's a stun gun to the | at heart.`
- `orderedForcedRelief` hits `none`: `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin. | by the rancid catnip of fiat money. | “buying the dip.” | It's a stun gun to the genitals | $1 billion`
- `directLiteralInitials` hits `none`: `GstGsbOytBsaIasgttgah`
- `directAllInitials` hits `none`: `GstGsbOytBsaIasgttah`
- `orderedForcedInitials` hits `none`: `GstGsbOyhtBbtrcofmbtdIasgttg$b`

## Assessment

- `5 SYMPTOM RELIEF` is real count/theme evidence, and `relief` is the cleanest action word on the package.
- Literal symptom removal has no complete five-of-five mapping into the ordered page-76 targets; in the forced printed order, none of the five target texts changes.
- Direct literal matches cluster on `heart` and `shitcoiner at heart`, but relieving HEARTBURN and SHITCOINS from O5 collapses to short leftovers like `shitcoiner at` / `at heart` / `at`, not an instruction.
- Instruction hits in relief streams: none.
- This keeps p80 as a five-count locator and theme validator, not the missing extraction-unit rule.

Decision: `do_not_promote_relief_to_selector`.

Next move: Keep p80 package copy in the C6 locator evidence. Reopen only if source geometry places the bottle/package copy onto page 76 or an external clue explicitly says to relieve/remove symptoms.
