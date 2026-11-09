# Opener Pill / Cash Inventory

Scope: visual source-layer inventory only. This pass records the photographed `OVERDOSE` opener pills/cash/field motif and compares it with the known page-79 pill fragments. It does not generate private-key candidates.

- Review sheet: `analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory_sheet.jpg`
- Page 73 capsules detected: `5`
- Page 79 known pill/orange fragments: `5`
- Page 74 orange components: `8`

## Page 73 Capsules

- O73-1: box=(619, 1206, 676, 1306) center=(647.5, 1256.0) size=57x100 maskArea=3392
- O73-2: box=(911, 1336, 1005, 1410) center=(958.0, 1373.0) size=94x74 maskArea=3536
- O73-3: box=(1125, 1578, 1204, 1655) center=(1164.5, 1616.5) size=79x77 maskArea=2430
- O73-4: box=(865, 1759, 946, 1843) center=(905.5, 1801.0) size=81x84 maskArea=2895
- O73-5: box=(497, 1943, 563, 2028) center=(530.0, 1985.5) size=66x85 maskArea=2281

## Page 79 Fragments

- P79-6: box=(146, 2370, 196, 2446) center=(171.0, 2408.0) size=50x76
- P79-7: box=(387, 2429, 456, 2480) center=(421.5, 2454.5) size=69x51
- P79-8: box=(577, 2576, 635, 2641) center=(606.0, 2608.5) size=58x65
- P79-9: box=(408, 2746, 466, 2815) center=(437.0, 2780.5) size=58x69
- P79-10: box=(161, 2935, 206, 3001) center=(183.5, 2968.0) size=45x66

## Assessment

- The opener spread is real source/provenance evidence because Max's announcement photo foregrounds it.
- Page 73 has a visually clean five-capsule sequence; page 79 also has five known orange pill fragments.
- Paired top-to-bottom, the p73 capsules fit p79 orange boxes 6-10 with affine mean residual `1.07` px and max residual `1.95` px.
- That near-perfect fit means the page-79 fragments are very likely a scaled/rotated reuse of the opener capsule artwork, not five unrelated marks.
- This gives a reliable five-item ordering layer, but it still does not define target region or extraction unit. It cannot yet select letters from page 76 by itself.
- Close `opener capsule count alone` as a direct selector. Keep p73/p79 capsule order active only when a specific mirror/fold rule ties it to page 76.

## Next Best Move

- Use the five-capsule order as an ordering layer for a supported p79->p76 mirror operation, not as key material.
