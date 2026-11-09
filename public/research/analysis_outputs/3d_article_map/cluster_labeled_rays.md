# Cluster-Labeled Anchor Rays

Scope: use the geometry-supported page-76 semantic clusters as labels for existing anchor-ray selections.
This tests ordering/labeling only; it does not hash or derive keys.

## Best Ray Per Cluster

- OPEN_HEART src=R initial=g range=[0, 10] bestRank=6 distance=0 overlap=1 selector=`p79_pill_4_mirror->p76_black_bar_2:ray_ab:48:reading`
  - text=`bitcoin UTXO It's tied dumb Schiff some and psychotic heads euthanized bitcoin money chest`
  - bold any=`bitcoinUTXO` partial=``
- FIAT_NONSENSE src=R initial=g range=[61, 73] bestRank=6 distance=0 overlap=1 selector=`p79_pill_4_mirror->p76_black_bar_2:ray_ab:48:reading`
  - text=`bitcoin UTXO It's tied dumb Schiff some and psychotic heads euthanized bitcoin money chest`
  - bold any=`bitcoinUTXO` partial=``
- FIAT_CATNIP src=L initial=b range=[127, 133] bestRank=9 distance=0 overlap=1 selector=`p79_pill_3_mirror->p76_black_bar_2:ray_ab:32:projection`
  - text=`money bitcoin heads and the`
  - bold any=`the` partial=``
- STUN_GUN src=B initial=i range=[148, 154] bestRank=30 distance=0 overlap=1 selector=`p79_pill_4_mirror->p76_black_bar_2:ray_ab:20:projection`
  - text=`money bitcoin heads and It’s`
- BUY_DIP src=B initial=b range=[187, 189] bestRank=28 distance=0 overlap=1 selector=`p79_pill_1_mirror->p79_pill_2_mirror:ray_ab:32:projection`
  - text=`IMF the off tagged I`
  - bold any=`theI` partial=``
- ONE_BILLION src=B initial=1 range=[208, 209] bestRank=27 distance=1 overlap=0 selector=`p79_pill_4_mirror->p79_pill_5_mirror:ray_ba:48:projection`
  - text=`of El Monetary He's when he to mine`
  - bold any=`El` partial=``

## Streams From Best Rays In Cluster Reading Order

- `cluster_labels`: `OPEN_HEART|FIAT_NONSENSE|FIAT_CATNIP|STUN_GUN|BUY_DIP|ONE_BILLION`
- `source_codes`: `RRLBBB`
- `phrase_initials`: `ggbib1`
- `ray_first_letters`: `bUItdSsaphebmcbUItdSsaphebmcmbhatmbhaIItotIoEMHwhtm`
- `ray_last_letters`: `nOsdbfedcsdnytnOsdbfedcsdnytynsdeynsdsFefdIflysneoe`
- `ray_any_bold`: `bitcoinUTXObitcoinUTXOthetheIEl`
- `ray_partial_bold`: ``
- `ray_lengths`: `74344643950755.74344643950755.57533.57533.33361.22834224`

## Assessment

- Every cluster has at least one nearby ray, but the same broad ray supports multiple early clusters, so this does not create an independent ordering rule.
- The later rays touch the IMF/El/Monetary corridor, while earlier rays mostly repeat generic UTXO/fiat/bitcoin material.
- Combined best-ray bold material is `bitcoinUTXObitcoinUTXOthetheIEl`, with no partial-bold stream. This is semantic reinforcement, not final key material.
- The cluster labels do not impose a readable message over the ray selections.
- Next best move: manually mark real corresponding points on the improved overlay; automated global alignment and cluster-labeled rays have both failed to produce a final selector.
