#!/usr/bin/env python3
"""Audit whether the p78->p76 dx repair is ordinary source/page drift.

The current p78 frame needs about dx=-38/-40 to touch trusted G5 while
preserving M3/O5 contact. Before treating that as puzzle evidence, this pass
compares independent source/registration witnesses:

- PDF image placement inside magazine.pdf.
- Alternate OCR/Google PDF p79 pill geometry.
- bitcoin4.pdf low-res Issue 24 geometry witness.
- p78 tri-contact and exact-edge stability window.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/registration_drift_explanation"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "registration_drift_explanation.json"
OUT_MD = OUT / "registration_drift_explanation.md"

INPUTS = {
    "pdfPlacement": ROOT / "analysis_outputs/source_audit/magazine_pdf_image_placement/magazine_pdf_image_placement.json",
    "alternatePdfPills": ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.json",
    "bitcoin4Witness": ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json",
    "triContact": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "stabilityWindow": ROOT / "analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def highres_equivalent(px: float, scale: float) -> float:
    if scale == 0:
        return 0.0
    return round(px / scale, 3)


def main() -> None:
    pdf = load(INPUTS["pdfPlacement"])
    alt = load(INPUTS["alternatePdfPills"])
    btc4 = load(INPUTS["bitcoin4Witness"])
    tri = load(INPUTS["triContact"])
    stability = load(INPUTS["stabilityWindow"])

    pdf_summary = pdf["summary"]
    alt_fit = alt["affineFitGoogleToHighres"]
    btc4_p76 = btc4["transforms"]["p76"]
    btc4_p78 = btc4["transforms"]["p78"]
    btc4_nat = btc4["bitcoin4NaturalGeometry"]["records"]
    btc4_scaled = btc4["simpleScaledHighresBaseline"]["records"]
    tri_records = {row["name"]: row for row in tri["records"]}
    current = tri_records["current"]
    repair = tri_records["g5_edge_touch"]
    nearest = tri_records["nearest_grid_dx_-40"]
    common_window = stability["summaries"]["targetExactAndTriContact"]

    # Convert the bitcoin4 p78 natural gap to the high-res coordinate system
    # using the fitted p78 x scale. This is only a rough witness comparison.
    btc4_natural_g5_gap_low = btc4_nat["G5"]["horizontalGapPx"]
    btc4_natural_g5_gap_high_equiv = highres_equivalent(btc4_natural_g5_gap_low, btc4_p78["ax"])
    btc4_scaled_g5_gap_low = btc4_scaled["G5"]["horizontalGapPx"]
    btc4_scaled_g5_gap_high_equiv = highres_equivalent(btc4_scaled_g5_gap_low, btc4_p78["ax"])

    rows = [
        {
            "witness": "magazine.pdf embedded page placement",
            "measurement": "per-page image offset/scale drift",
            "value": "0 pt gaps; one full-bleed image per page",
            "implication": "does not explain dx=-38/-40",
            "supportsOrdinaryDrift": False,
        },
        {
            "witness": "alternate OCR/Google p79 pill geometry",
            "measurement": "affine residual after mapping to high-res p79",
            "value": f"mean {alt_fit['meanResidualPx']} px, max {alt_fit['maxResidualPx']} px",
            "implication": "alternate p79 has same pill geometry after affine normalization",
            "supportsOrdinaryDrift": False,
        },
        {
            "witness": "bitcoin4.pdf p76/p78 low-res transforms",
            "measurement": "page transform residuals",
            "value": f"p76 mean {btc4_p76['meanAbsResidualPx']} px; p78 mean {btc4_p78['meanAbsResidualPx']} px",
            "implication": "low-res source has page-specific distortion, but not a useful repair",
            "supportsOrdinaryDrift": False,
        },
        {
            "witness": "bitcoin4.pdf natural p78->p76 geometry",
            "measurement": "reflected frame gap to trusted G5",
            "value": f"{btc4_natural_g5_gap_low} low-res px (~{btc4_natural_g5_gap_high_equiv} high-res px)",
            "implication": "worse than current high-res G5 gap, so it does not validate the dx repair",
            "supportsOrdinaryDrift": False,
        },
        {
            "witness": "current high-res p78 frame",
            "measurement": "gap to trusted G5 before repair",
            "value": f"{current['leftEdgeToG5RightPx']} px",
            "implication": "the only coherent repair is local dx about -38/-40",
            "supportsOrdinaryDrift": None,
        },
        {
            "witness": "p78 frame tri-contact repair",
            "measurement": "dx needed to touch G5 while preserving M3/O5 contact",
            "value": f"edge-touch dx {repair['dx']} px; nearest grid dx {nearest['dx']} px",
            "implication": "use as a benchmark for future sources, not as extraction",
            "supportsOrdinaryDrift": None,
        },
        {
            "witness": "repaired exact-edge stability window",
            "measurement": "dx/dy cells satisfying exact trio plus tri-contact",
            "value": f"dx {common_window['dxRange']}, dy {common_window['dyRange']}, count {common_window['count']}",
            "implication": "stable local signature, but still no extraction unit",
            "supportsOrdinaryDrift": None,
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source/page drift explanation for p78->p76 dx repair; no key derivation",
        "sourceReports": {key: rel(path) for key, path in INPUTS.items()},
        "keyMeasurements": {
            "pdfPlacement": {
                "fullBleedSingleImageEveryPage": pdf_summary["fullBleedSingleImageEveryPage"],
                "scalePxPerPtPairs": pdf_summary["scalePxPerPtPairs"],
                "rotations": pdf_summary["rotations"],
            },
            "alternatePdfPills": {
                "meanResidualPx": alt_fit["meanResidualPx"],
                "maxResidualPx": alt_fit["maxResidualPx"],
            },
            "bitcoin4": {
                "p76MeanAbsResidualPx": btc4_p76["meanAbsResidualPx"],
                "p78MeanAbsResidualPx": btc4_p78["meanAbsResidualPx"],
                "naturalG5GapLowResPx": btc4_natural_g5_gap_low,
                "naturalG5GapHighresEquivalentPx": btc4_natural_g5_gap_high_equiv,
                "simpleScaledG5GapLowResPx": btc4_scaled_g5_gap_low,
                "simpleScaledG5GapHighresEquivalentPx": btc4_scaled_g5_gap_high_equiv,
            },
            "currentHighres": {
                "currentG5GapPx": current["leftEdgeToG5RightPx"],
                "edgeTouchDxPx": repair["dx"],
                "nearestGridDxPx": nearest["dx"],
                "stableDxRange": common_window["dxRange"],
                "stableDyRange": common_window["dyRange"],
                "stableCellCount": common_window["count"],
            },
        },
        "rows": rows,
        "assessment": [
            "The dx=-38/-40 repair is not explained by hidden placement inside magazine.pdf; page placement is uniform.",
            "The alternate OCR/Google PDF preserves the p79 pill geometry after affine normalization and does not supply a new global offset.",
            "The low-res bitcoin4.pdf witness has page-specific distortion, but its natural p78->p76 geometry makes the G5 gap worse, not better.",
            "So ordinary source/page drift is a weak explanation for dx=-38/-40 under currently available files.",
            "The repair remains useful only as a source-registration benchmark; it still does not name an extraction unit.",
        ],
        "nextMove": "Do not treat dx=-38/-40 as a solved physical correction. Keep it as a benchmark for future physical/Canva/original-layout imagery, and only resume extraction if a new source also names the unit to read.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Registration Drift Explanation Audit",
        "",
        "Scope: check whether the p78->p76 `dx=-38/-40` repair is likely ordinary source/page drift. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Current high-res G5 gap before repair: `{current['leftEdgeToG5RightPx']} px`",
        f"- Tri-contact repair: edge-touch dx `{repair['dx']} px`, nearest grid dx `{nearest['dx']} px`",
        f"- Stability window: dx `{common_window['dxRange']}`, dy `{common_window['dyRange']}`, count `{common_window['count']}`",
        "",
        "## Witness Comparison",
        "",
        "| witness | measurement | value | implication |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['witness']} | {row['measurement']} | `{row['value']}` | {row['implication']} |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("ordinary drift explanation:", "weak")
    print("bitcoin4 natural G5 gap high-res equivalent:", btc4_natural_g5_gap_high_equiv)


if __name__ == "__main__":
    main()
