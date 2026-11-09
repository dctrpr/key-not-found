# 3D Ray Backlog Audit

Scope: inspect ray selections stored in the 3D map JSON but not rendered by the runtime viewer. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T20:47:40`
- Rays stored: `40`
- Viewer-rendered limit: `28`
- Backlog rays: `12`
- Overlay: `analysis_outputs/3d_article_map/ray_backlog_audit/ray_backlog_overlay.jpg`

## Backlog Rays

| pos | rank | score | endpoints | mode | order | instruction hits | target hits | active target box hits | text |
|---:|---:|---:|---|---|---|---|---|---|---|
| 29 | 29 | 35.7 | `p79_pill_1_mirror -> p79_pill_2_mirror` | `ray_ab/32` | `reading` | - | imf, novogratz | - | off the IMF those leeches. I tagged Novogratz in the tweet, bunch |
| 30 | 30 | 35.64 | `p79_pill_4_mirror -> p76_black_bar_2` | `ray_ab/20` | `projection` | - | - | - | money bitcoin heads. psychotic and some Schiff It's |
| 31 | 31 | 35.64 | `p79_pill_4_mirror -> p76_black_bar_2` | `ray_ab/20` | `reading` | - | - | - | It's Schiff some and psychotic heads. bitcoin money |
| 32 | 32 | 35.0 | `p76_black_bar_2 -> p76_x_mark` | `ray_ba/20` | `projection` | - | - | - | Get freaking of buy euthanized bitcoin money |
| 33 | 33 | 34.9 | `p79_pill_2_mirror -> p76_black_bar_2` | `ray_ab/48` | `projection` | - | - | - | money bitcoin euthanized heads. psychotic buy Schiff dumb bankers Brown parallel UTXO some |
| 34 | 34 | 34.9 | `p79_pill_2_mirror -> p76_black_bar_2` | `ray_ab/48` | `reading` | - | - | - | some UTXO parallel Brown bankers dumb Schiff buy psychotic heads. euthanized bitcoin money |
| 35 | 35 | 34.83 | `p79_pill_3_mirror -> p76_x_mark` | `ray_ba/32` | `projection` | - | sell | - | trolling taunting President Nayib nation's should sell |
| 36 | 36 | 34.0 | `p79_pill_2_mirror -> p76_black_bar_2` | `ray_ab/20` | `projection` | - | - | - | money bitcoin euthanized bankers Brown some |
| 37 | 37 | 34.0 | `p79_pill_2_mirror -> p76_black_bar_2` | `ray_ab/20` | `reading` | - | - | - | some Brown bankers euthanized bitcoin money |
| 38 | 38 | 34.0 | `p79_pill_5_mirror -> p76_black_bar_2` | `ray_ab/32` | `projection` | - | - | - | money bitcoin euthanized buy bankers Brown |
| 39 | 39 | 34.0 | `p79_pill_5_mirror -> p76_black_bar_2` | `ray_ab/32` | `reading` | - | - | - | Brown bankers buy euthanized bitcoin money |
| 40 | 40 | 33.74 | `p79_pill_4_mirror -> p76_wire_left_knot` | `segment/48` | `projection` | - | heart | - | minds. in bitcoin skin nothing heart |

## Duplicate/Alternate Check

- Hidden rays sharing endpoint/mode/threshold with a displayed ray: `1`
  - hidden pos `29` shares `('p79_pill_1_mirror', 'p79_pill_2_mirror', 'ray_ab', 32)` with displayed pos `[28]`

## Findings

- The viewer-rendered cap accounts for ranks 1-28; ranks 29-40 are stored only in JSON/backlog.
- The backlog rays are mostly lower-score alternates or reading-order duplicates of the already-rendered pill/black-bar/wire rays.
- Backlog target-term hits are contextual only: they include IMF/Novogratz, `should sell`, and a generic `heart`, but not trusted G5/O5 box contacts.
- No backlog ray text contains an extraction instruction term such as read/take/word/letter/edge/font/mirror/key.
- No backlog selected word center or word box intersects the active O4/B4/G5/O5 target boxes, so the hidden ray list does not recover a missed selector into the locked page-76 targets.

## Decision

- Do not treat the 12 non-rendered ray selections as hidden 3D-view evidence. Keep them as low-score diagnostic alternates unless a future rule explicitly chooses ray ranks 29-40 or the unrendered JSON layer.
- Next move: Return to source/clue acquisition or validation; the local 3D map ray backlog does not name the missing unit/order.
