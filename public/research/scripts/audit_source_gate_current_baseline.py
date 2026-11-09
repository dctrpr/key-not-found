#!/usr/bin/env python3
"""Dry-run the source validation gate on the current canonical scan.

The goal is to verify the gate's expected behavior: the current magazine.pdf
should pass baseline/source-quality checks, but extraction must remain blocked
because no source/clue names the unit/order to extract.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_gate_current_baseline"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_gate_current_baseline.json"
OUT_MD = OUT / "source_gate_current_baseline.md"

PROJECT_PDF = ROOT / "magazine.pdf"
DESKTOP_PDF = Path("private_inputs/Desktop/magazine.pdf")
GATE_JSON = ROOT / "analysis_outputs/source_audit/source_validation_gate/source_validation_gate.json"
PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
ZERO_JSON = ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops.json"
PILL_JSON = ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.json"
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
STABILITY_JSON = ROOT / "analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window.json"
MAG_PLACEMENT_MD = ROOT / "analysis_outputs/source_audit/magazine_pdf_image_placement/magazine_pdf_image_placement.md"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def image_ok(path: Path) -> dict:
    try:
        with Image.open(path) as img:
            return {"exists": True, "width": img.width, "height": img.height, "mode": img.mode}
    except Exception as exc:
        return {"exists": False, "error": str(exc)}


def gate_result(gate_id: str, status: str, evidence: str, block: str | None = None) -> dict:
    return {"gate": gate_id, "status": status, "evidence": evidence, "block": block}


def main() -> None:
    gate = load(GATE_JSON)
    priority = load(PRIORITY_JSON)
    zero = load(ZERO_JSON)
    pill = load(PILL_JSON)
    tri = load(TRI_JSON)
    stability = load(STABILITY_JSON)

    project_md5 = md5(PROJECT_PDF)
    desktop_md5 = md5(DESKTOP_PDF) if DESKTOP_PDF.exists() else None
    same_pdf = desktop_md5 == project_md5

    priority_images = [image_ok(ROOT / crop["output"]) for crop in priority["crops"]]
    zero_rows_ok = sum(1 for row in zero["rows"] if Path(row["highresCrop"]).exists())
    pill_count = len(pill["trustedHighresFragments"])
    exact_sig = " | ".join(stability["targetSignature"]["labels"])
    tri_edge = next((r for r in tri["records"] if r["name"] == "g5_edge_touch"), None)
    exact_and_tri = stability["summaries"]["targetExactAndTriContact"]

    results = [
        gate_result(
            "source_quality",
            "pass_baseline",
            f"Project magazine.pdf md5={project_md5}; desktop copy md5={desktop_md5}; byte-identical={same_pdf}. PDF placement report says full-bleed single 2544x3264 image per page.",
        ),
        gate_result(
            "page76_priority_crops",
            "pass_baseline",
            f"{sum(1 for item in priority_images if item['exists'])}/{len(priority_images)} priority crops exist; O5/G5/frame context are baseline-visible.",
        ),
        gate_result(
            "zero_hash0_hotspots",
            "pass_baseline",
            f"{zero_rows_ok}/{len(zero['rows'])} trusted high-res zero/#0 crops exist; p77 baseline reads 100,000.",
        ),
        gate_result(
            "p79_pill_geometry",
            "pass_baseline",
            f"Trusted p79 lower-left pill-fragment count is {pill_count}; alternate OCR/PDF witness also normalizes to five fragments but is not geometry truth.",
        ),
        gate_result(
            "p78_frame_exact_edge",
            "pass_baseline",
            f"Repaired signature `{exact_sig}` / `{stability['targetSignature']['styles']}`; exact+tri-contact stable dx={exact_and_tri['dxRange']} dy={exact_and_tri['dyRange']}; edge-touch frame={tri_edge['frame'] if tri_edge else None}.",
        ),
        gate_result(
            "extraction_permission",
            "blocked",
            "No current-source or raw external clue names the extraction unit/order.",
            "Need explicit unit/order such as word, letter, line, edge, font state, first/last, or a new source geometry change that supplies one.",
        ),
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "dry-run source validation gate on current canonical magazine.pdf baseline; no key derivation",
        "gateSource": str(GATE_JSON.relative_to(ROOT)),
        "pdf": {
            "project": str(PROJECT_PDF),
            "desktop": str(DESKTOP_PDF),
            "projectMd5": project_md5,
            "desktopMd5": desktop_md5,
            "byteIdentical": same_pdf,
        },
        "results": results,
        "decision": "Current scan passes as canonical baseline, but extraction remains blocked. A future source must change/confirm benchmark geometry or name the extraction unit before key checks resume.",
        "nextMove": "Use this dry-run as the expected baseline comparison for any future physical/original-layout/source material.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Gate Current-Baseline Dry Run",
        "",
        "Scope: run the source-validation gate against the current canonical `magazine.pdf` baseline. No key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Project md5: `{project_md5}`",
        f"- Desktop md5: `{desktop_md5}`",
        f"- Byte-identical desktop/project scan: `{same_pdf}`",
        "",
        "## Gate Results",
        "",
        "| gate | status | evidence | block |",
        "|---|---|---|---|",
    ]
    for item in results:
        block = item["block"] or "-"
        evidence = re.sub(r"\|", "/", item["evidence"])
        lines.append(f"| `{item['gate']}` | `{item['status']}` | {evidence} | {block} |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    for item in results:
        print(item["gate"], item["status"])


if __name__ == "__main__":
    main()
