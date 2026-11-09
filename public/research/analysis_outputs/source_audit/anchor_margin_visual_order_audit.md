# Anchor Margin Visual-Order Audit

Scope: inspect the full horizontal band around the p79-yellow -> p76-black color-inversion anchor, including margins outside the previous core crop. Article text boxes and known highlight boxes are masked before component detection. No key derivation is run.

- Band: `(0, 560, 2544, 1280)`
- Previous core crop: `(350, 650, 2200, 1050)`
- Preview: `analysis_outputs/source_audit/anchor_margin_visual_order_audit.jpg`

## Stats

- p76 residual pixels in band: `19162` across `53` components
- registered p79 residual pixels in band: `26913` across `29` components
- overlap pixels after masking: `205`
- overlap pixels outside previous core crop: `108`

## Region Summary

- p76:
  - `above_core`: components=8 pixels=2510 outsideCore=8
  - `below_core`: components=18 pixels=4684 outsideCore=18
  - `core`: components=27 pixels=8013 outsideCore=0
- registered p79:
  - `above_core`: components=5 pixels=1000 outsideCore=1
  - `below_core`: components=11 pixels=5203 outsideCore=11
  - `core`: components=12 pixels=11076 outsideCore=0
  - `right_margin`: components=1 pixels=7254 outsideCore=1

## Largest Components Outside Previous Core

- p76:
  - region=above_core area=873 box=[2145, 600, 2215, 626] size=70x26 aspect=2.692
  - region=below_core area=803 box=[2153, 1056, 2214, 1089] size=61x33 aspect=1.848
  - region=below_core area=492 box=[1816, 1138, 1857, 1163] size=41x25 aspect=1.64
  - region=below_core area=418 box=[1649, 1064, 1667, 1091] size=18x27 aspect=0.667
  - region=below_core area=384 box=[1819, 1211, 1841, 1235] size=22x24 aspect=0.917
  - region=above_core area=340 box=[719, 598, 742, 631] size=23x33 aspect=0.697
  - region=above_core area=308 box=[1400, 604, 1417, 629] size=17x25 aspect=0.68
  - region=below_core area=285 box=[673, 1214, 695, 1239] size=22x25 aspect=0.88
  - region=below_core area=270 box=[1510, 1212, 1525, 1245] size=15x33 aspect=0.455
  - region=above_core area=255 box=[814, 596, 827, 631] size=13x35 aspect=0.371
- registered p79:
  - region=right_margin area=7254 box=[2296, 560, 2544, 723] size=248x163 aspect=1.521
  - region=below_core area=2064 box=[694, 1215, 836, 1250] size=142x35 aspect=4.057
  - region=below_core area=926 box=[724, 1165, 844, 1185] size=120x20 aspect=6.0
  - region=below_core area=481 box=[1000, 1210, 1019, 1245] size=19x35 aspect=0.543
  - region=below_core area=332 box=[1527, 1212, 1546, 1236] size=19x24 aspect=0.792
  - region=below_core area=327 box=[1734, 1208, 1749, 1233] size=15x25 aspect=0.6
  - region=below_core area=217 box=[1435, 1211, 1445, 1238] size=10x27 aspect=0.37
  - region=below_core area=211 box=[1946, 1059, 1961, 1085] size=15x26 aspect=0.577
  - region=below_core area=203 box=[2036, 1203, 2052, 1228] size=16x25 aspect=0.64
  - region=above_core area=198 box=[1863, 624, 1877, 650] size=14x26 aspect=0.538

## Assessment

- The broader band does add margin components that the earlier crop could not see, but they behave like publication/page furniture, scan-edge residue, or transformed source-page residue.
- There is no clear repeated non-font ordering system: no usable dot count, pill count, X sequence, wire-knot sequence, arrow, or one-to-one component alignment appears around the color-inversion anchor.
- Close this as a local visual-order selector under the current high-res transform.
- Next best move: either inspect lower page-76 visual marks as a separate system, or pause geometry until a better physical/source scan gives new evidence.
