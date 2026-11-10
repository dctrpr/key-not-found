# Original detector coordinates for G07

The coordinate export records 321 observation rectangles from the saved 16 baseline views. It contains page, view, public stream ID, exact recorded decimal bounds and their outward-rounded pixel enclosures. It contains 114 reflected-view and 207 ordinary-view rectangles. [Coordinate export](BASELINE_BOXES.json) · [Published detector totals](../batch20/G07/DETAILS.json)

The archive's original job list and saved detector observations were replayed against the public streams in their original sort order. All 926 observation records and 112 whole-view records matched exactly. All eight saved upright baseline images matched the public G07 pixel hashes. Each of the eight stored reflected baselines was the exact horizontal column reversal of its upright partner. An independent rational arithmetic check reproduced all 321 view and upright crop bounds. [Earlier result](../batch20/G07/RESULT.json) · [Public stream archive](../batch20/G07/STREAMS.json)

The detector observations and job manifest are retained as owning archival inputs. Their SHA-256 values are in the export. The observations' locations are measurements made by that detector. The text identity and raster replay establish the provenance of the stored coordinates. They supply no independent optical calibration or glyph judgment.

The public crop command uses the pinned PDF and the published coordinate export directly. Each reflected-view box is mapped back to the same upright pixels before cropping. This lets anyone reproduce the visual review packet without rerunning the detector.
