# 3D Runtime View Modes Audit

Scope: render the local 3D article map in several modes and check whether the canvas is actually usable. No text extraction stream, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T20:36:48`
- Base URL: `http://127.0.0.1:8765/analysis_outputs/3d_article_map/index.html`
- Render path: Chrome headless with `--use-angle=swiftshader`

## Static Viewer Surface

- Layout modes: `spread, fold, stack`
- URL params: `focus, layout`
- Toggles: `togglePages, toggleChars, toggleImportant, toggleHighlights, toggleReflections, toggleAnchors, toggleRays`
- Data counts: `{'pages': 6, 'chars': 7299, 'words': 1243, 'anchors': 16, 'reflections': 29, 'raySelections': 40}`
- Reflection target pairs: `76->78, 78->76, 79->75, 79->76`

## Render Captures

| capture | layout | focus | screenshot | canvas non-bg | color pixels | status |
|---|---|---|---|---:|---|---|
| `spread_all` | `spread` | `all` | `analysis_outputs/3d_article_map/runtime_view_modes/spread_all.png` | 0.83542 | `{'orange': 26138, 'cyan': 3084, 'magenta': 3702, 'green': 4528}` | nonblank |
| `fold_all` | `fold` | `all` | `analysis_outputs/3d_article_map/runtime_view_modes/fold_all.png` | 0.47949 | `{'orange': 11409, 'cyan': 962, 'magenta': 2455, 'green': 2739}` | nonblank |
| `fold_page76` | `fold` | `76` | `analysis_outputs/3d_article_map/runtime_view_modes/fold_page76.png` | 0.2304 | `{'orange': 6925, 'cyan': 678, 'magenta': 5251, 'green': 814}` | nonblank |
| `stack_all` | `stack` | `all` | `analysis_outputs/3d_article_map/runtime_view_modes/stack_all.png` | 0.62679 | `{'orange': 14354, 'cyan': 178, 'magenta': 108423, 'green': 142}` | nonblank |

## Findings

- The rendered 3D viewer is reproducibly nonblank when Chrome is forced to use SwiftShader/ANGLE; this avoids the blank-canvas failure seen in the default headless path.
- The viewer still exposes only the three known layout modes: spread, fold, and stack.
- The URL focus parameter is a display filter only. It hides non-selected page groups but does not recompute mirror/fold geometry or create a new selector.
- Runtime metrics are populated and source-consistent: the viewer reports 5,966 display letters, 1,243 words, 16 anchors, and 29 mirror boxes; the JSON has 7,299 raw character records because it includes blanks/spacing, plus 40 stored ray selections with 28 displayed.
- The screenshots show overlay layers, anchors, rays, highlights, and text sprites as review aids. They do not reveal a hidden UI mode, hidden fold selector, or new ordering rule.

## Decision

- Use the 3D viewer for visual review/orientation only. Future runtime screenshots should force SwiftShader/ANGLE; do not infer puzzle signal from blank default headless captures or from focus/layout UI state.
- Next move: Return to source evidence: only reopen extraction when a new source/clue names the unit/order, or when a physical/original-layout image changes the page-76/G5/O5 geometry.
