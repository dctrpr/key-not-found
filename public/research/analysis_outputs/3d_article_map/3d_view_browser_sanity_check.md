# 3D View Browser Sanity Check

Scope: inspect the local 3D article map in the in-app browser and verify whether the Fold/Page 76 view is usable for manual visual inspection. No key derivation, hashing, OCR extraction, or address checks were run.

- Created: `2026-05-20T09:26:00+02:00`
- URL checked: `http://127.0.0.1:8765/analysis_outputs/3d_article_map/index.html`
- Focused URL checked: `http://127.0.0.1:8765/analysis_outputs/3d_article_map/index.html?layout=fold&focus=76`

## Observations

- The selected tab is the expected local viewer: `Max Keiser Puzzle 3D Article Map`.
- With the hidden/default in-app browser measurement state, the page initially reported a tiny effective viewport and a near-zero canvas height. This appears to be a browser inspection state, not a puzzle-layer signal.
- After applying a normal inspection viewport, the viewer loaded without console errors.
- The Fold/Page 76 state is reachable through URL parameters.
- In Fold/Page 76 state:
  - Active layout: `Fold`.
  - Active focus: `76`.
  - Canvas visual rect: about `1155 x 1066` px.
  - Canvas backing buffer: `1155 x 2112` px.
  - Layers enabled: page scans, letters, important words, highlights, mirror boxes, anchors, rays.
  - Counts visible in the UI: `5,966` letters, `1,243` words, `16` anchors, `29` mirror boxes.

## Viewer Findings Panel

The viewer itself still reports the same investigation state:

- Page 76 has the densest clue concentration.
- The strongest ray pull lands on President/Nayib/volcano language.
- Reflected highlights select readable phrases, but direct key/index derivations are clean.
- The Fold view treats the 76/79 system as orientation evidence and still needs a stricter selector.

## Assessment

- The 3D viewer is useful as a manual inspection surface, especially for Page 76 + Fold mode.
- It did not expose a new selector, hidden UI state, or contradiction with the current ledger.
- Do not treat the temporary tiny canvas measurement as geometry evidence; it came from browser viewport state.
- Continue using generated geometry reports as source-of-truth for measurements, and use the viewer for manual orientation and correction review.

## Next Move

- Since local 3D UI state does not add a selector, continue with source/physical registration or a new source-level instruction. If the viewer is used again, start with `?layout=fold&focus=76` and verify the canvas has a normal visible size before drawing conclusions.
