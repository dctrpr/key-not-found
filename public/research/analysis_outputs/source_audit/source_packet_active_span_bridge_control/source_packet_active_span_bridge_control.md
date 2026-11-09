# Source Packet Active Span Bridge Control

- Created: `2026-05-24T20:20:58`
- Scope: Adjacent active span bridge control using current scan/PDF source-packet active rows and grey/black control rows; no key material or brute force.
- Fingerprint: `activeRows=4|nonactiveRows=13|linePairs=3|xPairs=3|lineExactOVER=1|xExactOVER=1|uniqueActiveExactOVER=1|activeLayoutPairs=2|controlPairs=8|controlLayoutPairs=6|controlExactOVER=0|nonactiveSingleLayout=5|nonactiveExactOVER=1|nonactiveExactOVERDOSE=1|bridgeCues=0|sourceR3=0|triggers=0/9|selectors=0`

## Findings

- Active readable-line adjacent span streams: `O4+B4=DOSOV, B4+G5=OVER, G5+O5=ERRDO`.
- The only active exact `OVER` bridge is `B4+G5`; this is the known black-pair span bridge, not a new ordering rule.
- Non-active single-span controls with layout hits: `5`; exact `OVER`: `1`; exact `OVERDOSE`: `1`.
- Non-active page-adjacent control pairs with layout hits: `6` of `8`.
- Example non-active page-adjacent layout bridges:
  - `p75_grey_1+p75_grey_2` -> `RDOSOVERDO` hits `OVER`
  - `p75_grey_2+p75_grey_3` -> `OVERDOOVER` hits `OVER`
  - `p76_grey_1+p76_grey_2` -> `OVERDOSEOV` hits `OVERDOSE,OVER,DOSE`
  - `p76_grey_2+p76_grey_3` -> `OVERDOS` hits `OVER`
  - `p77_grey_1+p77_grey_2` -> `OVERDOSRDOS` hits `OVER`
  - `p78_grey_1+p78_grey_2` -> `DOSEVER` hits `DOSE`
- Source bridge-cue hits: `0`; source-backed R3 hits: `0`; reopen triggers: `0/9`.

## Decision

Adjacent active span bridging is controlled as a layout echo. It can recreate `OVER` only through the same B4/G5 black-pair bridge already seen in source packet controls, while non-active spans already provide `OVER`, `DOSE`, and `OVERDOSE` without unlocking any source-backed unit/order.

## Next Move

Do not continue local adjacent-span variants. Keep O4/B4/G5/O5 as validation targets and move back to source/physical/original-layout or raw clue evidence that explicitly names transform, unit, and order.
