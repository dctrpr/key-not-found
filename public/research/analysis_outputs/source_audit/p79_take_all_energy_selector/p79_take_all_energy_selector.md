# P79 Take-All-Energy Selector Audit

Scope: focused high-res mirror audit of the p79 highlighted action phrase `That's right, Bitcoin will take all the energy.` No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.

- Created: `2026-05-20T21:57:02`
- Review sheet: `analysis_outputs/source_audit/p79_take_all_energy_selector/p79_take_all_energy_selector_sheet.jpg`

## Source Phrase

- Source: p79 orange/highlight box `2`
- Text: `That's right, Bitcoin will take all the energy.`
- Source instruction hits: `['right', 'take']`
- Reflected box on p76: `[640, 830, 1447, 915]`

## Page-76 Landing

- Direct words inside reflected box: `Gotta be S way. Forty years`
- Direct instruction hits: `[]`

| target | target label | overlap source | overlap target | overlap words | right-side words | hits |
|---|---|---:|---:|---|---|---|
| `black1` | `Gotta be this way... post-1971 fiat money` | `0.70588` | `0.43081` | `Gotta be S way. Forty years` | `of dumb post-1971 flat money` | `[]` |
| `black2` | `nonsense` | `0.02223` | `0.06759` | `` | `Peter Schiff miss buying bitcoin` | `[]` |

## Findings

- The source phrase is not ignored: it is one of the few font-state runs with action-like wording (`right`, `take`).
- Under the current high-res mirror, it lands on p76 upper grey prose: `Gotta be this way... post-1971 fiat money`, not on the lower El Salvador / IMF / `Volcano Bonds` / `shitcoiner at heart` target corridor.
- The literal `right` side of that landing yields ordinary article prose and no `word`, `letter`, `line`, `key`, `private`, `seed`, or `address` unit.

## Decision

- Close p79 `That's right, Bitcoin will take all the energy` as a standalone current-scan selector.
- Keep it only as thematic energy/action wording unless a new source transform moves this phrase onto the lower page-76 corridor or a clue supplies the unit/order.
