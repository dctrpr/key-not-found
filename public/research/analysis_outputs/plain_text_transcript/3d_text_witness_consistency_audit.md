# 3D Text Witness Consistency Audit

Scope: compare the 3D map's internal text witness against the corrected DOCM-derived article text. No key derivation was run.

- Created: `2026-05-20T05:11:41`
- Canonical tokens: `1477`
- 3D-map tokens: `1460`
- Sequence match ratio: `0.987813`

## Known Hotspots

- `puts an end`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `Volcano Bonds`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `has gone`: canonical has canonical=`True`, 3D has canonical=`False`, 3D has suspect=`True`
  - 3D suspect context: `untry is now hyperbitcoinized (at the time of writing) jack mallers' strike app nas gone from 20,000 new sign-ups a day to a mind-bending 100,000 and growing. at this r`
- `100,000`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `salesmen`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `gargantuanly`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `money printing`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `$2 trillion fiat cuck-bucks`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`
- `Bitcoin fills in the gap`: canonical has canonical=`True`, 3D has canonical=`False`, 3D has suspect=`True`
  - 3D suspect context: `h perfect bitcoin. remove the war incentive, and you remove the hate incentive. bitcoin fills the gap with love; our most natural tendency if given a chance. the warmongers will sta`
- `The economy of love is infinitely more efficient than hate and war.`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`True`
  - 3D suspect context: `o the game-theorized bitcoin protocol, observable by anyone choosing to see it, right there in the genesis block. to wrap this up, as we move from a war and violence economy to a peace and love economy, the ef`
- `gets monetized for the first time`: canonical has canonical=`True`, 3D has canonical=`True`, 3D has suspect=`False`

## First Diff Windows

- `delete` canonical[670:671] model[670:670]
  - canonical: `hyperbitcoinized ( at the time of writing ) . jack mallers' strike app has gone from 20`
  - 3D model: `hyperbitcoinized ( at the time of writing ) jack mallers' strike app nas gone from 20`
- `replace` canonical[675:676] model[674:675]
  - canonical: `of writing ) . jack mallers' strike app has gone from 20 , 000 new sign -`
  - 3D model: `time of writing ) jack mallers' strike app nas gone from 20 , 000 new sign -`
- `delete` canonical[1161:1162] model[1160:1160]
  - canonical: `you remove the hate incentive . bitcoin fills in the gap with love ; our most natural`
  - 3D model: `you remove the hate incentive . bitcoin fills the gap with love ; our most natural`
- `delete` canonical[1211:1224] model[1209:1209]
  - canonical: `it , right there in the genesis block . the economy of love is infinitely more efficient than hate and war . to wrap this up , as we`
  - 3D model: `it , right there in the genesis block . to wrap this up , as we`
- `delete` canonical[1295:1296] model[1280:1280]
  - canonical: `drops by 95% or more . that's right , bitcoin will take all the energy . in`
  - 3D model: `drops by 95% or more . that's right bitcoin will take all the energy . in`
- `delete` canonical[1444:1445] model[1428:1428]
  - canonical: `have been living in here for 10 years . we've seen some shit . happy to share`
  - 3D model: `have been living in here for 10 years we've seen some shit . happy to share`

## Assessment

- The 3D map remains useful for visual/geometry inspection, but its text layer is a label witness, not exact source truth.
- The most important live discrepancy for page-77 text is `has gone` vs 3D-map `nas gone`; the zero hotspot remains canonical `100,000`, not `1000,000`.
- Future selectors should use this order: high-res scan for geometry, corrected DOCM/plain text for wording, and the 3D map only for navigation/visual labeling.
