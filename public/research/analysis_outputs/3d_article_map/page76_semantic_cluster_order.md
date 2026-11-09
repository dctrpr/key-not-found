# Page 76 Semantic Cluster Order

Scope: inspect only exact high-res page-76 highlight spans that survive reflected-geometry checks.
No hashing or broad key generation is performed here.

## Geometry-Supported Clusters

- R orange idx=0-10 initial=`g` text=`Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` match=1.0
  - radius 40 partial=`eelibe` words=['31:George[ee]', '32:Clinton[li]', '50:being[be]']
- R grey_black idx=61-73 initial=`g` text=`Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` match=0.917
  - radius 10 partial=`ippedelbe` words=['51:ripped[ipped]', '54:central[el]', '55:bankers[be]']
  - radius 20 partial=`beippedelbe` words=['50:being[be]', '51:ripped[ipped]', '54:central[el]', '55:bankers[be]']
  - radius 40 partial=`eelibeippedelbeie` words=['31:George[ee]', '32:Clinton[li]', '50:being[be]', '51:ripped[ipped]', '54:central[el]', '55:bankers[be]', '102:nocoiners[ie]']
- L orange idx=127-133 initial=`b` text=`by the rancid catnip of fiat money.` match=1.0
  - radius 40 partial=`ielvd` words=['102:nocoiners[ie]', '172:Salvador[lvd]']
- B grey_black idx=148-154 initial=`i` text=`It’s a stun gun to the genitals.` match=1.0
  - radius 20 partial=`lvd` words=['172:Salvador[lvd]']
  - radius 40 partial=`lvd` words=['172:Salvador[lvd]']
- B orange idx=187-189 initial=`b` text=`“buying the dip.”` match=1.0
  - radius 20 partial=`lvd` words=['172:Salvador[lvd]']
  - radius 40 partial=`lvd` words=['172:Salvador[lvd]']
- B grey_black idx=208-209 initial=`1` text=`$1 billion` match=1.0
  - radius 40 partial=`lvdieNvz` words=['172:Salvador[lvd]', '239:Mike[ie]', '240:Novogratz[Nvz]']

## Simple Streams

- `reading_phrase_initials`: `ggbib1`
- `reading_source_codes`: `RRLBBB`
- `geometry_phrase_initials`: `ggibb1`
- `geometry_source_codes`: `RRBBLB`
- `dual_source_phrase_initials`: `ib1`
- `dual_source_word_initials`: `iasgttgbtd1b`
- `reading_radius20_partial_bold`: `beippedelbelvdlvd`
- `dual_source_radius20_partial_bold`: `lvdlvd`

## Assessment

- Reading order gives source-code pattern `RRLBBB`, which is structured but not directly instructional.
- Dual-source geometry-supported phrases reduce to phrase initials `ib1`, not a readable instruction.
- Nearby partial-bold letters remain dominated by known fragments such as `be`, `lvd`, and `ieNvz`; they point back to El Salvador / Mike Novogratz rather than forming a new message.
- This supports the page-76 semantic corridor but does not supply the missing final selector.
- Next best move: manually mark true overlay correspondences on the improved 76/79 registration image, or test page-76 semantic clusters as ordering labels for existing ray selections rather than as key material.
