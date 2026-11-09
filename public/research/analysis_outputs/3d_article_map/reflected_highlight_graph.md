# Reflected Highlight Graph

Scope: exact high-res highlighted spans intersected by reflected OCR/mask hits. This checks whether geometry creates a clean ordering rule; it does not generate key candidates.

## Summary

- Total reflected-hit edges: 25
- Strong edges: 9
- Medium-or-strong edges: 17
- Page-76 medium-or-strong edges: 17
- Page-76 target initials by graph order: `GGGbbbbbIIII$$$$$`
- Page-76 source-page pattern by graph order: `7979797878787979787879797878787979`
- Page-76 reflected-text initials by graph order: `bGCaJBcIsMLntVwuIstsosbrolcbttabs|GbSwFyoalowP|mbb|obettpcMBm|HystpoES|hybh|GbSwFyoalowP|mbb|hybh|obettpcMBm|GbSwFyoalowP|bGCaJBcIsMLntVwuIstsosbrolcbttabs|HystpoES|obettpcMBm|Oi|HystpoES|ttIMFIoTtttthsB`

## Page Pair Counts

- 78 -> 76: 8
- 79 -> 76: 9

## Page 76 Medium+ Edges

- strong 79->76 `but George Clinton and James Brown clones. It's Martin Luther nailing…` -> orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` (span=0.297, reflected=0.957, dist=58.0)
- strong 79->76 `Gotta be S way. Forty years of (and loyears of watching Peter` -> orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` (span=0.056, reflected=0.937, dist=393.6)
- medium 79->76 `miss buying bitcoin` -> orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` (span=0.012, reflected=0.518, dist=499.7)
- medium 78->76 `¥ortunately, bitcoin end to the paper chase Manhattan Bank money` -> orange `by the rancid catnip of fiat money.` (span=0.135, reflected=0.458, dist=311.8)
- medium 78->76 `Have you seen the president of El Salvador` -> orange `by the rancid catnip of fiat money.` (span=0.055, reflected=0.525, dist=503.4)
- strong 78->76 `honéy-badgering him` -> orange `“buying the dip.”` (span=0.069, reflected=1.000, dist=79.0)
- medium 79->76 `Gotta be S way. Forty years of (and loyears of watching Peter` -> orange `“buying the dip.”` (span=0.055, reflected=0.453, dist=175.3)
- strong 79->76 `miss buying bitcoin` -> orange `“buying the dip.”` (span=0.035, reflected=0.713, dist=620.1)
- strong 78->76 `honéy-badgering him` -> grey_black `It’s a stun gun to the genitals.` (span=0.025, reflected=0.790, dist=221.6)
- medium 78->76 `¥ortunately, bitcoin end to the paper chase Manhattan Bank money` -> grey_black `It’s a stun gun to the genitals.` (span=0.116, reflected=0.555, dist=411.6)
- medium 79->76 `Gotta be S way. Forty years of (and loyears of watching Peter` -> grey_black `It’s a stun gun to the genitals.` (span=0.036, reflected=0.651, dist=276.4)
- medium 79->76 `but George Clinton and James Brown clones. It's Martin Luther nailing…` -> grey_black `It’s a stun gun to the genitals.` (span=0.165, reflected=0.571, dist=316.4)
- strong 78->76 `Have you seen the president of El Salvador` -> grey_black `$1 billion` (span=0.028, reflected=0.948, dist=327.1)
- strong 78->76 `¥ortunately, bitcoin end to the paper chase Manhattan Bank money` -> grey_black `$1 billion` (span=0.063, reflected=0.751, dist=487.2)
- medium 78->76 `Our imaginations` -> grey_black `$1 billion` (span=0.011, reflected=0.928, dist=656.5)
- strong 79->76 `Have you seen the president of El Salvador` -> grey_black `$1 billion` (span=0.048, reflected=0.949, dist=319.4)
- strong 79->76 `trolling the International Monetary Fund (IMF) on Twitter? taunting t…` -> grey_black `$1 billion` (span=0.052, reflected=0.949, dist=396.0)

## Target Groups

- grey_black_4 p76 grey_black `It’s a stun gun to the genitals.`: sources=78,78,79,79 strengths=S,M,M,M
- grey_black_5 p76 grey_black `$1 billion`: sources=78,78,78,79,79 strengths=S,S,M,S,S
- orange_7 p76 orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.`: sources=79,79,79 strengths=S,S,M
- orange_8 p76 orange `by the rancid catnip of fiat money.`: sources=78,78 strengths=M,M
- orange_9 p76 orange `“buying the dip.”`: sources=78,79,79 strengths=S,M,S

## Assessment

- The reflected graph is concentrated on page 76, but the medium/strong edges repeat broad prose areas rather than producing a one-edge-per-highlight selector.
- The page-76 graph-order stream is not readable as an instruction. Source-page ordering is dominated by repeated 79 and 78 hits, not a clean mirror/fold sequence.
- The most meaningful evidence remains semantic: reflected text keeps landing near the El Salvador/Bukele/IMF/bitcoin-buying corridor. It is not yet precise enough for letter-level extraction.
- Next best move: compare source scans/physical copy, or manually test one mirror-clue rule on the page-76 corridor only.
