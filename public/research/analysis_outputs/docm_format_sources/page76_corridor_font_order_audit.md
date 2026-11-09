# Page 76 Corridor Font-Order Audit

Scope: test whether the verified page-76 corridor gives an ordered selector when combining `Article with Fonts.docm` layers, high-res highlight labels, and the established p79-yellow -> p76-black calibration anchor. No key candidates are generated.

## Layer Codes

- `Y` = yellow/orange highlight
- `K` = black/grey highlight
- `M` = Typeka Mix
- `B` = Typeka bold without highlight

## Streams

- `p76SignalLayerCodes` hits=none: `YBMMMKBMYKMYBKKBMMY`
- `p76SignalInitials` hits=none: `GUGbcGsnbIEbP$VIMIs`
- `p76SignalLastInitials` hits=none: `thCrbmsnmgSdBbBlNgh`
- `p76SignalLengthMod10` hits=none: `1831411984020727337`
- `matchedTargetLayerCodes` hits=none: `YKYKYKKY`
- `matchedTargetInitials` hits=none: `GGbIb$Vs`
- `matchedTargetLastInitials` hits=none: `tmmgdbBh`
- `targetWithNearestMixTriplets` hits=none: `GGcGnnbEnIEE"ME$ME“MIs`

## Page 76 Signal Groups

- G01 Y runs 80-81 hits=-: `Get some toxicity. Get some bitcoin. Open your heart toBitcoin.`
- G02 B runs 83-83 hits=-: `UTXO ghetto up in here`
- G03 M runs 87-87 hits=-: `George Clinton`
- G04 M runs 90-91 hits=-: `being ripped`
- G05 M runs 93-93 hits=-: `central bankers`
- G06 K runs 95-96 hits=-: `Gotta be this way. Forty years of dumb post-1971 fiat moneynonsense`
- G07 B runs 102-102 hits=-: `shitcoiners'`
- G08 M runs 104-104 hits=-: `nocoiners'`
- G09 Y runs 109-109 hits=-: `by the rancid catnip of fiat money.`
- G10 K runs 115-115 hits=-: `It's a stun gun to the genitals.`
- G11 M runs 120-120 hits=-: `El Salvador`
- G12 Y runs 124-126 hits=dip: `"buying the dip."`
- G13 B runs 128-128 hits=-: `President Nayib Bukele`
- G14 K runs 131-131 hits=-: `$1 billion`
- G15 K runs 137-137 hits=-: `“Volcano Bonds”`
- G16 B runs 140-141 hits=-: `IMF loan`
- G17 M runs 143-144 hits=-: `Mike Novogratz`
- G18 M runs 148-148 hits=-: `I don't really trust that guy.`
- G19 Y runs 151-151 hits=-: `shitcoiner at heart.`

## Confirmed Target Groups

- `open_heart` -> G01 Y runs 80-81: `Get some toxicity. Get some bitcoin. Open your heart toBitcoin.`
- `calibration_black` -> G06 K runs 95-96: `Gotta be this way. Forty years of dumb post-1971 fiat moneynonsense`
- `rancid_catnip` -> G09 Y runs 109-109: `by the rancid catnip of fiat money.`
- `stun_gun` -> G10 K runs 115-115: `It's a stun gun to the genitals.`
- `buying_dip` -> G12 Y runs 124-126: `"buying the dip."`
- `one_billion` -> G14 K runs 131-131: `$1 billion`
- `volcano_bonds` -> G15 K runs 137-137: `“Volcano Bonds”`
- `shitcoiner_heart` -> G19 Y runs 151-151: `shitcoiner at heart.`

## Nearest Typeka Mix Around Targets

- `open_heart` G01: prevMix=G- `-`; nextMix=G3 `George Clinton`; triplet=`GG`
- `calibration_black` G06: prevMix=G5 `central bankers`; nextMix=G8 `nocoiners'`; triplet=`cGn`
- `rancid_catnip` G09: prevMix=G8 `nocoiners'`; nextMix=G11 `El Salvador`; triplet=`nbE`
- `stun_gun` G10: prevMix=G8 `nocoiners'`; nextMix=G11 `El Salvador`; triplet=`nIE`
- `buying_dip` G12: prevMix=G11 `El Salvador`; nextMix=G17 `Mike Novogratz`; triplet=`E"M`
- `one_billion` G14: prevMix=G11 `El Salvador`; nextMix=G17 `Mike Novogratz`; triplet=`E$M`
- `volcano_bonds` G15: prevMix=G11 `El Salvador`; nextMix=G17 `Mike Novogratz`; triplet=`E“M`
- `shitcoiner_heart` G19: prevMix=G18 `I don't really trust that guy.`; nextMix=G- `-`; triplet=`Is`

## 76/79 Calibration Context

- p79 signal layer codes: `KYYMBBYMBMB`
- Registered p79 source group: G2 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` layer=YELLOW
- Local p79 context:
  - G01 K runs 295-296: `war and violence economy`
  - G02 Y runs 299-301: `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
  - G03 Y runs 307-308: `That's right, Bitcoin will take all the energy.`
  - G04 M runs 310-317: `In so doing, our energy consumption drops to near zero because our natural tendency toward love and peace gets monetized for the first time in our existence.`

## Assessment

- The page-76 signal sequence is structured, but it follows the visible prose: opening toxicity, UTXO/Clinton, fiat nonsense, El Salvador/Bukele, $1 billion/Volcano Bonds, Novogratz, distrust, shitcoiner-at-heart.
- Confirmed page-76 targets are all `Y` or `K`; the Typeka Mix groups are nearby semantic anchors (`George Clinton`, `El Salvador`, `Mike Novogratz`, `I don't really trust that guy`) rather than a separate ordered index.
- The known 76/79 calibration is a color-inversion clue (`p79 YELLOW` landing on `p76 BLACK`), but it does not produce a new ordering rule from the font states.
- Close this as a direct selector. Keep it as evidence that Typeka/font layers are formatting witnesses which still need an external rule.
- Next best move: inspect page-76 corridor for non-font visual ordering marks or obtain a higher-fidelity source/physical scan; do not rerun Typeka initial/length streams without a new selector.
