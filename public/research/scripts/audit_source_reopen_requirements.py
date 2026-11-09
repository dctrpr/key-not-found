#!/usr/bin/env python3
"""Build the source-reopen requirements checklist.

The local search is currently paused: page 76 is a strong target surface, but
the current scan-only source set and local text/layout permutations have not
supplied the missing extraction unit. This pass records the exact evidence
needed before extraction should resume. User clarification on 2026-05-24:
there is no native/original PDF; the available PDFs are scanned-page sources.

No OCR extraction, hashing, seed/WIF checks, address checks, or candidate
generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_reopen_requirements"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_reopen_requirements.json"
OUT_MD = OUT / "source_reopen_requirements.md"
SHEET = OUT / "source_reopen_requirements_sheet.jpg"

REPORTS = {
    "future_packet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "priority_crops": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "tri_contact": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "native_bridge": ROOT / "analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge.json",
    "topology": ROOT / "analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology.json",
    "frontier": ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json",
    "scan_lock": ROOT / "analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock.json",
    "obbo": ROOT / "analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json",
}

PANEL_IMAGES = [
    (
        ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
        "page 76 validation crops",
        "O5, G5, should-sell, and L26-L29 source band.",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg",
        "p78 frame tri-contact",
        "Current/repaired frame benchmark around O5, G5, and M3.",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge_sheet.jpg",
        "upright/native bridge",
        "Required orientation bridge for source_images and fresh PDF extraction.",
    ),
    (
        ROOT / "analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology_sheet.jpg",
        "physical topology",
        "Leaves/spreads that a physical scan must respect.",
    ),
    (
        ROOT / "analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock_sheet.jpg",
        "current scan lock",
        "Desktop magazine.pdf is byte-identical to the workspace scan.",
    ),
]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def font(size: int = 20) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def scale_to_width(img: Image.Image, width: int) -> Image.Image:
    scale = min(1.0, width / img.width)
    return img.resize((int(img.width * scale), int(img.height * scale)))


def build_sheet() -> list[dict]:
    panels = []
    panel_w = 640
    margin = 26
    gap = 22
    label_h = 84
    title_font = font(24)
    body_font = font(16)

    for path, title, subtitle in PANEL_IMAGES:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((panel_w, 360))
        canvas = Image.new("RGB", (panel_w, label_h + img.height), (16, 18, 22))
        draw = ImageDraw.Draw(canvas)
        draw.text((0, 0), title, fill=(240, 244, 248), font=title_font)
        draw.text((0, 34), subtitle, fill=(168, 181, 194), font=body_font)
        canvas.paste(img, (0, label_h))
        panels.append({"image": canvas, "title": title, "path": rel(path)})

    if not panels:
        return []

    cols = 2
    rows = (len(panels) + cols - 1) // cols
    row_heights = []
    for r in range(rows):
        row_panels = panels[r * cols : (r + 1) * cols]
        row_heights.append(max(p["image"].height for p in row_panels))
    sheet_w = margin * 2 + panel_w * cols + gap * (cols - 1)
    sheet_h = margin * 2 + sum(row_heights) + gap * (rows - 1) + 68
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "Source Reopen Requirements", fill=(244, 247, 250), font=font(32))
    draw.text(
        (margin, margin + 40),
        "Use these visual baselines before restarting extraction.",
        fill=(172, 184, 196),
        font=body_font,
    )
    y = margin + 68
    for r in range(rows):
        x = margin
        for panel in panels[r * cols : (r + 1) * cols]:
            sheet.paste(panel["image"], (x, y))
            x += panel_w + gap
        y += row_heights[r] + gap
    sheet.save(SHEET, quality=94)
    return [{"title": p["title"], "path": p["path"]} for p in panels]


def target_rows(priority: dict, tri: dict, obbo: dict) -> list[dict]:
    rows: list[dict] = []
    for crop in priority.get("crops", []):
        rows.append(
            {
                "id": crop.get("id"),
                "title": crop.get("title"),
                "text": crop.get("text"),
                "crop": crop.get("crop"),
                "image": rel(crop.get("output")),
                "boxes": crop.get("boxes", []),
            }
        )

    targets = tri.get("targets", {})
    anchors = obbo.get("anchors", [])
    return [
        {
            "name": "O5 primary",
            "label": targets.get("O5", {}).get("label") or "shitcoiner at heart",
            "box": targets.get("O5", {}).get("box"),
            "why": "highest-scoring target surface; lower page-76 orange highlight",
        },
        {
            "name": "G5 pair",
            "label": targets.get("G5", {}).get("label") or "Volcano Bonds",
            "box": targets.get("G5", {}).get("box"),
            "why": "paired black/grey target in the same lower corridor",
        },
        {
            "name": "OBBO anchor set",
            "label": "buying the dip / $1 billion / Volcano Bonds / shitcoiner at heart",
            "box": None,
            "anchors": anchors,
            "why": "compact O-B-B-O boundary signature; source changes must preserve or explain it",
        },
        {
            "name": "Priority crop pack",
            "label": "line-level p76 comparison crops",
            "box": None,
            "crops": rows,
            "why": "manual visual baseline for future physical or higher-resolution scan sources",
        },
    ]


def scan_orientation_guardrail(scan_lock: dict, topology: dict, bridge: dict) -> dict:
    pages = []
    for rec in scan_lock.get("records", []):
        if rec.get("articlePage") in {75, 76, 77, 78, 79, 80}:
            pages.append(
                {
                    "articlePage": rec.get("articlePage"),
                    "pdfPageNumber1": rec.get("pdfPageNumber1"),
                    "embeddedSize": rec.get("embeddedSize"),
                    "sourceBestOrientation": rec.get("sourceBestOrientation"),
                    "uprightBestOrientation": rec.get("uprightBestOrientation"),
                    "freshRot180Vs3dRms": rec.get("freshRot180Vs3dRms"),
                }
            )
    return {
        "sourceImagesAreNative": True,
        "cropAnd3dImagesAreReadableUpright": True,
        "rule": "Compare like with like: rotate fresh PDF/source_images 180 degrees before applying readable/upright crop coordinates.",
        "scanPages": pages,
        "physicalLeaves": topology.get("physicalLeaves", []),
        "facingSpreads": topology.get("facingSpreads", []),
        "bridgeRows": bridge.get("rows", []),
    }


def main() -> None:
    data = {name: load_json(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    tri_records = {row.get("name"): row for row in data["tri_contact"].get("records", [])}
    current = tri_records.get("current", {})
    repaired = tri_records.get("nearest_grid_dx_-40") or tri_records.get("g5_edge_touch", {})

    accepted_sources = [
        {
            "type": "physical magazine",
            "requirements": [
                "flat photos/scans of pages 75-80",
                "photos of physical leaves 75/76, 77/78, and 79/80 from both sides",
                "held-to-light shots only if the same leaf and orientation are visible",
                "enough resolution to read O5, G5, $1 billion, buying the dip, and p80 package text",
            ],
        },
        {
            "type": "higher-resolution scanned source/export",
            "requirements": [
                "higher-resolution scanned page image or scanned PDF, not a resaved screenshot",
                "visible page edges, scan provenance, or export metadata for the scanned page images",
                "must preserve or explain the p78 frame to p76 tri-contact benchmark",
            ],
        },
        {
            "type": "external clue/provenance",
            "requirements": [
                "wording that names an extraction unit/order such as word, letter, line, edge, font, first/last, left/right, or read direction",
                "must point back to the page-76 lower corridor or explain why it should be abandoned",
            ],
        },
    ]

    insufficient_inputs = [
        "the same Desktop/workspace magazine.pdf again",
        "requests for native/original PDF layout layers from the current source set",
        "resaved or downsampled screenshots of the same PDF",
        "OCR-PDF coordinate boxes used as geometry truth",
        "current 3D viewer focus/camera state without a new source image",
        "additional broad hashing, BIP39, WIF, minikey, Base58, or prose-hash passes",
        "more local G5/O5 text-unit permutations without a clue naming the unit/order",
    ]

    reopen_gates = [
        {
            "id": "R1",
            "name": "source identity",
            "passCondition": "new material must be physically or scanned-source distinct from the byte-locked current scan",
        },
        {
            "id": "R2",
            "name": "target preservation",
            "passCondition": "must preserve or clearly explain O5, G5, L26-L29, and the p78 frame contact pattern",
        },
        {
            "id": "R3",
            "name": "unit/order evidence",
            "passCondition": "must name or visibly supply the extraction unit/order before any key checks resume",
        },
        {
            "id": "R4",
            "name": "orientation discipline",
            "passCondition": "must state whether coordinates are readable/upright or native/source and apply the 180-degree guardrail",
        },
        {
            "id": "R5",
            "name": "controlled improvement",
            "passCondition": "must improve a compact benchmark, preferably dx -38/-40 G5 edge repair, O5 bottom contact, M3 right-edge cut, or the p77 one-line near miss",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-reopen requirements after local selector search pause; no extraction or key derivation",
        "inputReports": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "currentState": {
            "localSelectorSearch": "paused for current scan",
            "sourceConstraint": "2026-05-24 user clarification: no native/original PDF is expected; all available PDFs are scanned-page sources",
            "frontierDecision": data["frontier"].get("decision", {}),
            "byteLockedScan": {
                "pdfByteIdentical": data["scan_lock"].get("pdfByteIdentical"),
                "desktopSha256": data["scan_lock"].get("desktopSha256"),
                "workspaceSha256": data["scan_lock"].get("workspaceSha256"),
            },
            "triContactBenchmark": {
                "currentFrame": current.get("frame"),
                "currentO5OverlapVsTarget": current.get("o5OverlapVsTarget"),
                "currentG5GapPx": current.get("leftEdgeToG5RightPx"),
                "currentM3RightEdgeOverlapPx": current.get("rightEdgeM3VerticalOverlapPx"),
                "repairedFrame": repaired.get("frame"),
                "repairDx": repaired.get("dx"),
                "repairDy": repaired.get("dy"),
                "repairTriContactPass": repaired.get("triContactPass"),
            },
        },
        "validationTargets": target_rows(data["priority_crops"], data["tri_contact"], data["obbo"]),
        "orientationGuardrail": scan_orientation_guardrail(data["scan_lock"], data["topology"], data["native_bridge"]),
        "acceptedSources": accepted_sources,
        "insufficientInputs": insufficient_inputs,
        "reopenGates": reopen_gates,
        "decision": {
            "doNotResumeExtractionFrom": "current scan or duplicate/resaved derivatives alone",
            "resumeOnlyAfter": "a source/clue passes R1-R5 and names or materially supplies the extraction unit/order",
            "nextBestMove": "obtain or inspect physical scan, higher-resolution scanned-source provenance, or raw clue wording, then score it against this checklist before any selector/key test",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Reopen Requirements",
        "",
        "Scope: define what would be strong enough to reopen extraction after the current-scan local selector search was paused. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Current scan byte-identical: `{result['currentState']['byteLockedScan']['pdfByteIdentical']}`",
        f"- Desktop/workspace SHA-256: `{result['currentState']['byteLockedScan']['desktopSha256']}`",
        "",
        "## Current State",
        "",
        "- Page 76 lower corridor remains the validation surface, not solved key material.",
        "- Local text/format/layout permutations are closed for the current scan unless a new clue/source changes the rule space.",
        "- Source constraint: no native/original PDF is expected; all available PDFs are scanned-page sources.",
        "- The p78 frame benchmark remains useful only as a source-registration test.",
        "",
        "## Required Validation Targets",
        "",
    ]
    for target in result["validationTargets"]:
        lines.append(f"- `{target['name']}`: {target['label']} - {target['why']}")
        if target.get("box"):
            lines.append(f"  box: `{target['box']}`")
    lines.extend(
        [
            "",
            "## Reopen Gates",
            "",
            "| gate | name | pass condition |",
            "|---|---|---|",
        ]
    )
    for gate in reopen_gates:
        lines.append(f"| `{gate['id']}` | {gate['name']} | {gate['passCondition']} |")

    lines.extend(["", "## Acceptable New Evidence", ""])
    for source in accepted_sources:
        lines.append(f"### {source['type']}")
        for item in source["requirements"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## Not Enough To Reopen", ""])
    for item in insufficient_inputs:
        lines.append(f"- {item}")

    guard = result["orientationGuardrail"]
    lines.extend(
        [
            "",
            "## Orientation Guardrail",
            "",
            f"- {guard['rule']}",
            "- Current readable/upright coordinates are the ones used in the 3D map and crop pack.",
            "- Current `source_images` and fresh PDF extraction are native orientation and should be rotated 180 degrees before applying those crop coordinates.",
            "",
            "## Decision",
            "",
            f"- Do not resume extraction from: `{result['decision']['doNotResumeExtractionFrom']}`.",
            f"- Resume only after: `{result['decision']['resumeOnlyAfter']}`.",
            f"- Next best move: {result['decision']['nextBestMove']}.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    if SHEET.exists():
        print(f"wrote {SHEET}")
    print("reopen gates:", ", ".join(g["id"] for g in reopen_gates))


if __name__ == "__main__":
    main()
