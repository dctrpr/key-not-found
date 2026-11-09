# 3D Target Wording Bridge

Scope: pair trusted page-76 crop images with corrected wording and 3D-label status. No key derivation, hashing, seed, WIF, or address checks were run.

- Created: `2026-05-20T13:54:18`
- Sheet: `analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge_sheet.jpg`

## Rows

| crop | exact wording | 3D-label status | use |
|---|---|---|---|
| `L32_O5_primary` | `Maybe because he's a shitcoiner at heart.` | `p76_shitcoiner_heart=False` | primary O5 target; exact text absent from 3D labels |
| `L27_G5_pair` | `collateralized "Volcano Bonds" to pay off the IMF loan` | `p76_volcano_bonds=False; p76_imf_loan=True` | G5 pair; Volcano Bonds absent from 3D labels, IMF loan present |
| `L25_should_sell` | `$1 billion in bitcoin - that he should sell` | `p76_one_billion=False; p76_should_sell=True` | $1 billion absent from 3D labels; should sell present |
| `L26_L29_source_band` | `billions worth of future bitcoin earnings / Volcano Bonds / IMF loan / Mike Novogratz` | `p76_future_earnings=True; p76_volcano_bonds=False; p76_imf_loan=True; p76_mike_novogratz=True` | mixed reliability; use crop and corrected transcript for exact wording |
| `L25_L32_frame_context` | `should sell -> Volcano Bonds -> shitcoiner at heart` | `p76_should_sell=True; p76_volcano_bonds=False; p76_shitcoiner_heart=False` | compact p78-frame benchmark; registration evidence only |

## Assessment

- The active page-76 visual targets need exact transcript text, not 3D OCR labels.
- The sheet preserves the current crop/geometry baselines while making the text authority explicit.
- This supports future source comparison and manual inspection; it does not reopen extraction.

## Decision

- Use this bridge when inspecting the 3D view or future source images for the lower page-76 corridor.

## Next Move

- Continue source-gated investigation; a new source/clue must still name the extraction unit/order before key work resumes.
