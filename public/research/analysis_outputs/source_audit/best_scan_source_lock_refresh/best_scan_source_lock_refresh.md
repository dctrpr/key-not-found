# Best Scan Source Lock Refresh

Scope: verify that the user-supplied Desktop best scan, the workspace scan, and the 3D article map all use the same high-res geometry source. No key derivation, hashing of candidate text, seed phrase, WIF, or address checks were run.

## PDF Sources

| id | exists | size | sha256 | pages | rotation | page size |
|---|---:|---:|---|---:|---|---|
| `desktopBestScan` | `True` | `6904582` | `a0714dcbe503ecdff846f0f77334e2d1d259937d7fe5130258212f24c137716e` | `8` | `180` | `610.56 x 783.36 pts` |
| `workspaceScan` | `True` | `6904582` | `a0714dcbe503ecdff846f0f77334e2d1d259937d7fe5130258212f24c137716e` | `8` | `180` | `610.56 x 783.36 pts` |
| `mapHighresSource` | `True` | `6904582` | `a0714dcbe503ecdff846f0f77334e2d1d259937d7fe5130258212f24c137716e` | `8` | `180` | `610.56 x 783.36 pts` |
| `mapOcrSource` | `True` | `6512512` | `0078fe23401fab4882303ae038df0de6b439f498acb852d3b226c366caf5ab5c` | `8` | `0` | `612 x 792 pts (letter)` |
| `workspaceOcrPdf` | `True` | `6512512` | `0078fe23401fab4882303ae038df0de6b439f498acb852d3b226c366caf5ab5c` | `8` | `0` | `612 x 792 pts (letter)` |

## 3D Page Image Derivatives

| page | width | height | mode |
|---:|---:|---:|---|
| 75 | `2544` | `3264` | `RGB` |
| 76 | `2544` | `3264` | `RGB` |
| 77 | `2544` | `3264` | `RGB` |
| 78 | `2544` | `3264` | `RGB` |
| 79 | `2544` | `3264` | `RGB` |
| 80 | `2544` | `3264` | `RGB` |

## Conclusions

- Desktop best scan, workspace scan, and 3D map high-res source are byte-identical.
- The OCR PDF is a different file and remains label/navigation evidence only, not geometry truth.
- All 3D page images for pages 75-80 are 2544x3264 upright derivatives of the high-res scan geometry.

## Decision

- Treat `private_inputs/Desktop/magazine.pdf` and workspace `magazine.pdf` as the same canonical high-res geometry source. Do not reopen local PDF source selection unless a materially different physical scan, original layout export, or higher-resolution image appears.

## Next Move

- Use this refreshed source lock as the baseline for future source comparison. Further progress needs a new source image/original layout clue or an explicit unit/order rule.
