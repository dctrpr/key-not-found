# Overlapped Color Neighbor Analysis

Scope: for page-76 color spans touched by reflected boxes, collect only nearby partial-bold letters from the corrected transcript.

## Span Windows
- orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin` via 79_76_1 source=canonical-color-indexes
  - radius 5: partial=`` reverse=`` words=[]
  - radius 10: partial=`` reverse=`` words=[]
  - radius 20: partial=`` reverse=`` words=[]
  - radius 40: partial=`eelibe` reverse=`beliee` words=['31:George[ee]', '32:Clinton[li]', '50:being[be]']
- grey `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` via 79_76_2 source=canonical-color-indexes
  - radius 5: partial=`` reverse=`` words=[]
  - radius 10: partial=`ippedelbe` reverse=`beelipped` words=['51:ripped[ipped]', '54:central[el]', '55:bankers[be]']
  - radius 20: partial=`beippedelbe` reverse=`beelippedbe` words=['50:being[be]', '51:ripped[ipped]', '54:central[el]', '55:bankers[be]']
  - radius 40: partial=`eelibeippedelbeie` reverse=`iebeelippedbeliee` words=['31:George[ee]', '32:Clinton[li]', '50:being[be]', '51:ripped[ipped]', '54:central[el]', '55:bankers[be]', '102:nocoiners[ie]']
- orange `by the rancid catnip of fiat money` via 78_76_3 source=canonical-color-indexes
  - radius 5: partial=`` reverse=`` words=[]
  - radius 10: partial=`` reverse=`` words=[]
  - radius 20: partial=`` reverse=`` words=[]
  - radius 40: partial=`ielvd` reverse=`lvdie` words=['102:nocoiners[ie]', '172:Salvador[lvd]']
- grey `It's a stun gun to the genitals` via 79_76_1 source=geometry-only-no-canonical-index
- orange `buying the dip` via 78_76_1 source=canonical-color-indexes
  - radius 5: partial=`` reverse=`` words=[]
  - radius 10: partial=`` reverse=`` words=[]
  - radius 20: partial=`lvd` reverse=`lvd` words=['172:Salvador[lvd]']
  - radius 40: partial=`lvd` reverse=`lvd` words=['172:Salvador[lvd]']
- grey `$1 billion` via 78_76_3 source=canonical-color-indexes
  - radius 5: partial=`` reverse=`` words=[]
  - radius 10: partial=`` reverse=`` words=[]
  - radius 20: partial=`` reverse=`` words=[]
  - radius 40: partial=`lvdieNvz` reverse=`Nvzielvd` words=['172:Salvador[lvd]', '239:Mike[ie]', '240:Novogratz[Nvz]']

## Combined Streams By Radius
- radius 5 normal len=0: ``
- radius 5 reverse-each len=0: ``
- radius 10 normal len=9: `ipped elbe`
- radius 10 reverse-each len=9: `beeli pped`
- radius 20 normal len=14: `beipp edelb elvd`
- radius 20 reverse-each len=14: `beeli ppedb elvd`
- radius 40 normal len=39: `eelib eeeli beipp edelb eieie lvdlv dlvdi eNvz`
- radius 40 reverse-each len=39: `belie eiebe elipp edbel ieelv dielv dNvzi elvd`

## Assessment
- Restricting to reflected-overlapped color spans greatly reduces the page-76 partial-bold stream, but the resulting windows still do not read as an instruction.
- The most stable nearby partial fragments remain `eelibeippedelbe`, `lvd`, and small fragments around Mike/Novogratz/trust-guy when the radius is widened.
- This keeps the branch alive as an ordering/registration clue, but not as a solved selector. The next best discriminator is source/layout: verify whether the exact same reflected overlaps survive on the high-res physical spread after affine registration.
