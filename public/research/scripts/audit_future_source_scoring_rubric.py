#!/usr/bin/env python3
"""Build a bounded scoring rubric for future source evidence.

This pass turns the current page-76 and p78-frame evidence into explicit
acceptance thresholds. It is a source-validation aid only: no text extraction,
key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction,
or address checking is performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "future_source_scoring_rubric.json"
OUT_MD = OUT / "future_source_scoring_rubric.md"
SHEET = OUT / "future_source_scoring_rubric_sheet.jpg"

INPUTS = {
    "source_acquisition_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
    "source_acquisition_integrity": ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_packet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "priority_crops": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "p78_tricontact": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "p77_one_line": ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json",
    "active_unlock_matrix": ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json",
}

VISUALS = [
    ("page 76 targets", ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg"),
    ("p78 frame signature", ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg"),
    ("source packet", ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet_sheet.jpg"),
    ("integrity gate", ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity_sheet.jpg"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def text_wrap(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width_chars: int, fill, fnt, line_gap: int = 4) -> int:
    x, y = xy
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if len(trial) > width_chars and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + line_gap if hasattr(fnt, "size") else 18
    return y


def build_sheet(rubric_rows: list[dict[str, Any]], extraction_gate: dict[str, Any]) -> None:
    sheet_w = 1420
    margin = 28
    header_h = 92
    row_h = 72
    rubric_h = 42 + row_h * len(rubric_rows)
    thumb_h = 300
    thumb_w = 320
    gap = 18
    sheet_h = margin * 2 + header_h + rubric_h + 78 + thumb_h + 50

    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, margin), "Future Source Scoring Rubric", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 44),
        "Use before any new scan/export/raw clue can reopen extraction.",
        fill=(174, 184, 196),
        font=normal,
    )

    y = margin + header_h
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(29, 34, 42))
    draw.text((margin + 12, y + 8), "gate", fill=(236, 241, 247), font=small)
    draw.text((margin + 120, y + 8), "requirement", fill=(236, 241, 247), font=small)
    draw.text((margin + 540, y + 8), "current baseline", fill=(236, 241, 247), font=small)
    draw.text((margin + 925, y + 8), "pass threshold", fill=(236, 241, 247), font=small)
    y += 38

    for row in rubric_rows:
        draw.rectangle((margin, y, sheet_w - margin, y + row_h - 6), fill=(18, 23, 28), outline=(38, 46, 56))
        draw.text((margin + 12, y + 12), row["id"], fill=(113, 222, 154) if row["blocking"] else (174, 184, 196), font=mono)
        text_wrap(draw, (margin + 120, y + 10), row["requirement"], 48, (224, 232, 240), small)
        text_wrap(draw, (margin + 540, y + 10), row["currentBaseline"], 45, (174, 184, 196), small)
        text_wrap(draw, (margin + 925, y + 10), row["passThreshold"], 52, (224, 232, 240), small)
        y += row_h

    y += 16
    draw.rectangle((margin, y, sheet_w - margin, y + 54), fill=(37, 30, 18), outline=(90, 70, 32))
    text_wrap(
        draw,
        (margin + 12, y + 10),
        f"Extraction remains blocked unless: {extraction_gate['allowExtractionOnlyIf']}",
        150,
        (255, 218, 135),
        normal,
    )
    y += 78

    for idx, (label, path) in enumerate(VISUALS):
        x = margin + idx * (thumb_w + gap)
        draw.text((x, y), label, fill=(236, 241, 247), font=normal)
        yy = y + 28
        draw.rectangle((x, yy, x + thumb_w, yy + thumb_h), fill=(19, 22, 28), outline=(52, 62, 75))
        if path.exists():
            img = Image.open(path).convert("RGB")
            img.thumbnail((thumb_w - 8, thumb_h - 8))
            sheet.paste(img, (x + 4, yy + 4))
        else:
            draw.text((x + 12, yy + 130), "missing", fill=(255, 123, 123), font=normal)

    sheet.save(SHEET, quality=94)


def main() -> None:
    packet = load_json(INPUTS["source_acquisition_packet"])
    integrity = load_json(INPUTS["source_acquisition_integrity"])
    reopen = load_json(INPUTS["source_reopen"])
    future = load_json(INPUTS["future_packet"])
    priority = load_json(INPUTS["priority_crops"])
    tri = load_json(INPUTS["p78_tricontact"])
    p77 = load_json(INPUTS["p77_one_line"])
    unlock = load_json(INPUTS["active_unlock_matrix"])

    target_priority = priority.get("targetPriority", {})
    crops = priority.get("crops", [])
    tri_records = {row.get("name"): row for row in tri.get("records", [])}
    current = tri_records.get("current", {})
    repair = tri_records.get("nearest_grid_dx_-40", {})
    p77_gap = p77.get("gapVsLinePitch", {})

    rubric_rows = [
        {
            "id": "R1",
            "name": "source identity",
            "blocking": True,
            "requirement": "Material must be physically/original-layout distinct from the byte-locked current scan or duplicate exports.",
            "currentBaseline": "Current workspace and Desktop magazine.pdf are byte-identical; current local source set has zero actionable unknowns.",
            "passThreshold": "Physical scan/photo, native layout export, browser/source asset, or raw clue source with provenance that is not only a resave of the current PDF.",
            "evidenceToRecord": ["source path", "capture/source type", "timestamp/provenance", "whether derived from current scan"],
        },
        {
            "id": "R2",
            "name": "target preservation",
            "blocking": True,
            "requirement": "Must preserve or explain the active page-76 lower corridor: O5, G5, L26-L29, and O-B-B-O anchors.",
            "currentBaseline": "Active targets: O5 'shitcoiner at heart', G5 'Volcano Bonds', L26 future bitcoin earnings; crop pack has five line/context panels.",
            "passThreshold": "O5 and G5 are readable/locatable, plus at least one context band from L25-L32 is visible enough to compare against the crop pack.",
            "evidenceToRecord": [crop.get("id") for crop in crops],
        },
        {
            "id": "R3",
            "name": "unit/order evidence",
            "blocking": True,
            "requirement": "Must name or visibly supply an extraction unit/order before selector/key checks resume.",
            "currentBaseline": "Active unlock matrix checks 8 paths; all 8 fail R3. Existing raw-like clue intake has zero R3 passes.",
            "passThreshold": "Source-backed wording or layer metadata names word, letter, line, edge, font, first/last, left/right, fold, mirror read direction, page/order, key/private format, or equivalent.",
            "evidenceToRecord": ["exact quote/screenshot/source", "unit term", "order term", "why it points to page 76 or redirects"],
        },
        {
            "id": "R4",
            "name": "orientation discipline",
            "blocking": True,
            "requirement": "Coordinates must use the correct orientation before comparison.",
            "currentBaseline": "3D/crop layer is readable/upright; source_images and fresh PDF extraction are native upside-down and need rotate180.",
            "passThreshold": "New material states/readably shows orientation; comparisons are made in upright coordinates or with documented 180-degree rotation.",
            "evidenceToRecord": ["native orientation", "upright conversion", "page numbers/edges visible", "rotation applied"],
        },
        {
            "id": "R5",
            "name": "controlled improvement",
            "blocking": True,
            "requirement": "Must improve a compact benchmark without inventing a new arbitrary transform.",
            "currentBaseline": "C2 is partial: p78 frame clips O5, cuts M3, and is 38px from G5; dx -38/-40 repairs tri-contact but remains registration evidence only.",
            "passThreshold": "Natural source registration preserves/explains O5 bottom contact, M3 right-edge cut, and G5 edge repair, or creates repeated direct O5/G5 physical contacts.",
            "evidenceToRecord": ["O5 overlap", "G5 gap/overlap", "M3 right-edge contact", "p77 near-miss change", "same transform repeated"],
        },
    ]

    numeric_benchmarks = {
        "page76Targets": target_priority,
        "priorityCropSheet": priority.get("sheet"),
        "p78Frame": {
            "currentFrame": current.get("frame"),
            "currentG5GapPx": current.get("leftEdgeToG5RightPx"),
            "currentM3RightEdgeOverlapPx": current.get("rightEdgeM3VerticalOverlapPx"),
            "currentO5OverlapVsTarget": current.get("o5OverlapVsTarget"),
            "repairFrame": repair.get("frame"),
            "repairDx": repair.get("dx"),
            "repairDy": repair.get("dy"),
            "repairTriContactPass": repair.get("triContactPass"),
            "repairG5OverlapVsTarget": repair.get("g5OverlapVsTarget"),
            "repairO5OverlapVsTarget": repair.get("o5OverlapVsTarget"),
        },
        "p77NearMiss": {
            "baselineVerticalGapPx": p77_gap.get("baselineVerticalGapPx"),
            "contentBoxVerticalGapPx": p77_gap.get("contentBoxVerticalGapPx"),
            "medianLinePitchPx": p77_gap.get("medianLinePitchPx"),
            "oneLineUpO5HitCount": p77.get("hitSummary", {}).get("p77OneLineUpO5HitCount"),
        },
        "currentBlockers": {
            "activeEvidenceDecision": unlock.get("decision"),
            "allPathsBlockedOnR3": unlock.get("summary", {}).get("allPathsBlockedOnR3"),
            "integrityStatus": integrity.get("status"),
            "integrityDecision": integrity.get("decision"),
        },
    }

    extraction_gate = {
        "allowExtractionOnlyIf": "R1, R2, R3, R4, and R5 all pass on the same new source/clue item, with R3 providing a source-backed unit/order.",
        "blockIf": [
            "R3 is absent, even if target geometry improves.",
            "material is only a duplicate/resaved current scan.",
            "orientation is ambiguous or mixed between upright/native coordinates.",
            "geometry requires arbitrary shifts not explained by source/physical evidence.",
        ],
        "firstAllowedActionsAfterPass": [
            "transcribe exact selected unit/order",
            "run one low-parameter extraction following the source-backed rule",
            "only then test checksum-valid key-like output or address activity",
        ],
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "future source scoring rubric; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) if path.exists() else None for name, path in INPUTS.items()},
        "sheet": rel(SHEET),
        "rubricRows": rubric_rows,
        "numericBenchmarks": numeric_benchmarks,
        "extractionGate": extraction_gate,
        "decision": "future_source_scoring_rubric_created_no_selector_unlocked",
        "nextMove": "Use this rubric together with the source-acquisition packet when new physical/original-layout/raw clue material appears. Do not resume extraction from the current scan.",
    }
    build_sheet(rubric_rows, extraction_gate)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Future Source Scoring Rubric",
        "",
        "Scope: turn the current page-76 and p78-frame evidence into explicit acceptance thresholds for future physical/original-layout/raw-clue material. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## R1-R5 Rubric",
        "",
        "| gate | name | blocking | current baseline | pass threshold |",
        "|---|---|---:|---|---|",
    ]
    for row in rubric_rows:
        lines.append(
            f"| `{row['id']}` | {row['name']} | `{row['blocking']}` | {row['currentBaseline']} | {row['passThreshold']} |"
        )

    lines.extend(
        [
            "",
            "## Numeric Benchmarks",
            "",
            f"- p78 current frame: `{numeric_benchmarks['p78Frame']['currentFrame']}`",
            f"- p78 current G5 gap: `{numeric_benchmarks['p78Frame']['currentG5GapPx']}` px",
            f"- p78 current M3 right-edge overlap: `{numeric_benchmarks['p78Frame']['currentM3RightEdgeOverlapPx']}` px",
            f"- p78 current O5 overlap vs target: `{numeric_benchmarks['p78Frame']['currentO5OverlapVsTarget']}`",
            f"- p78 repair frame: `{numeric_benchmarks['p78Frame']['repairFrame']}` with dx `{numeric_benchmarks['p78Frame']['repairDx']}` and tri-contact pass `{numeric_benchmarks['p78Frame']['repairTriContactPass']}`",
            f"- p77 baseline vertical near-miss gap: `{numeric_benchmarks['p77NearMiss']['baselineVerticalGapPx']}` px",
            f"- p77 median lower-corridor line pitch: `{numeric_benchmarks['p77NearMiss']['medianLinePitchPx']}` px",
            "",
            "## Extraction Gate",
            "",
            f"- Allow extraction only if: {extraction_gate['allowExtractionOnlyIf']}",
            "",
            "Block extraction if:",
        ]
    )
    lines.extend(f"- {item}" for item in extraction_gate["blockIf"])
    lines.extend(
        [
            "",
            "First allowed actions after a full pass:",
        ]
    )
    lines.extend(f"- {item}" for item in extraction_gate["firstAllowedActionsAfterPass"])
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
