# Source Reopen Requirements

Scope: define what would be strong enough to reopen extraction after the current-scan local selector search was paused. No extraction, hashing, seed, WIF, address, or candidate checks were run.

- Created: `2026-05-24T20:54:42`
- Sheet: `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg`
- Current scan byte-identical: `True`
- Desktop/workspace SHA-256: `a0714dcbe503ecdff846f0f77334e2d1d259937d7fe5130258212f24c137716e`

## Current State

- Page 76 lower corridor remains the validation surface, not solved key material.
- Local text/format/layout permutations are closed for the current scan unless a new clue/source changes the rule space.
- Source constraint: no native/original PDF is expected; all available PDFs are scanned-page sources.
- The p78 frame benchmark remains useful only as a source-registration test.

## Required Validation Targets

- `O5 primary`: shitcoiner at heart - highest-scoring target surface; lower page-76 orange highlight
  box: `[1040.0, 2932.0, 1661.0, 2982.0]`
- `G5 pair`: Volcano Bonds - paired black/grey target in the same lower corridor
  box: `[795.0, 2544.0, 1196.0, 2592.0]`
- `OBBO anchor set`: buying the dip / $1 billion / Volcano Bonds / shitcoiner at heart - compact O-B-B-O boundary signature; source changes must preserve or explain it
- `Priority crop pack`: line-level p76 comparison crops - manual visual baseline for future physical or higher-resolution scan sources

## Reopen Gates

| gate | name | pass condition |
|---|---|---|
| `R1` | source identity | new material must be physically or scanned-source distinct from the byte-locked current scan |
| `R2` | target preservation | must preserve or clearly explain O5, G5, L26-L29, and the p78 frame contact pattern |
| `R3` | unit/order evidence | must name or visibly supply the extraction unit/order before any key checks resume |
| `R4` | orientation discipline | must state whether coordinates are readable/upright or native/source and apply the 180-degree guardrail |
| `R5` | controlled improvement | must improve a compact benchmark, preferably dx -38/-40 G5 edge repair, O5 bottom contact, M3 right-edge cut, or the p77 one-line near miss |

## Acceptable New Evidence

### physical magazine
- flat photos/scans of pages 75-80
- photos of physical leaves 75/76, 77/78, and 79/80 from both sides
- held-to-light shots only if the same leaf and orientation are visible
- enough resolution to read O5, G5, $1 billion, buying the dip, and p80 package text

### higher-resolution scanned source/export
- higher-resolution scanned page image or scanned PDF, not a resaved screenshot
- visible page edges, scan provenance, or export metadata for the scanned page images
- must preserve or explain the p78 frame to p76 tri-contact benchmark

### external clue/provenance
- wording that names an extraction unit/order such as word, letter, line, edge, font, first/last, left/right, or read direction
- must point back to the page-76 lower corridor or explain why it should be abandoned

## Not Enough To Reopen

- the same Desktop/workspace magazine.pdf again
- requests for native/original PDF layout layers from the current source set
- resaved or downsampled screenshots of the same PDF
- OCR-PDF coordinate boxes used as geometry truth
- current 3D viewer focus/camera state without a new source image
- additional broad hashing, BIP39, WIF, minikey, Base58, or prose-hash passes
- more local G5/O5 text-unit permutations without a clue naming the unit/order

## Orientation Guardrail

- Compare like with like: rotate fresh PDF/source_images 180 degrees before applying readable/upright crop coordinates.
- Current readable/upright coordinates are the ones used in the 3D map and crop pack.
- Current `source_images` and fresh PDF extraction are native orientation and should be rotated 180 degrees before applying those crop coordinates.

## Decision

- Do not resume extraction from: `current scan or duplicate/resaved derivatives alone`.
- Resume only after: `a source/clue passes R1-R5 and names or materially supplies the extraction unit/order`.
- Next best move: obtain or inspect physical scan, higher-resolution scanned-source provenance, or raw clue wording, then score it against this checklist before any selector/key test.
