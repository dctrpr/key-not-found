#!/usr/bin/env python3
"""Synthesize folded/mirrored 3D geometry evidence against the R1-R5 gate.

This consolidates existing 3D viewer, reflected-highlight, mirror-read,
two-hand, reflection-box, anchor-point, and fold-ordering reports into one
current-scan decision. It does not generate extraction streams or key material;
it asks whether the 3D geometry itself supplies R3 unit/order evidence or a
controlled R5 improvement.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "fold_mirror_r3_gate_synthesis.json"
OUT_MD = OUT / "fold_mirror_r3_gate_synthesis.md"
SHEET = OUT / "fold_mirror_r3_gate_synthesis_sheet.jpg"

REPORTS = {
    "reflected_highlight_graph": ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json",
    "exact_highres_reflection_geometry": ROOT / "analysis_outputs/3d_article_map/exact_highres_reflection_geometry.json",
    "page76_twohand_selector": ROOT / "analysis_outputs/3d_article_map/page76_twohand_selector.json",
    "page76_mirror_read_rule": ROOT / "analysis_outputs/3d_article_map/page76_mirror_read_rule.json",
    "reflection_box_target_overlap": ROOT / "analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap.json",
    "anchor_point_target_proximity": ROOT / "analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity.json",
    "fold_nonboundary_ordering": ROOT / "analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering.json",
    "runtime_view_modes": ROOT / "analysis_outputs/3d_article_map/runtime_view_modes/runtime_view_modes.json",
    "selector_intersection_analysis": ROOT / "analysis_outputs/3d_article_map/selector_intersection_analysis.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

SHEET_IMAGES = [
    (
        ROOT / "analysis_outputs/3d_article_map/runtime_view_modes/fold_page76.png",
        "3D fold view, page 76 focus",
        "display/orientation layer; no recomputed selector",
    ),
    (
        ROOT / "analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap_overlay.jpg",
        "reflection boxes vs active targets",
        "one O4 graze; no G5/O5 direct hit",
    ),
    (
        ROOT / "analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity_overlay.jpg",
        "3D anchors vs active targets",
        "zero anchors inside or near O4/B4/G5/O5",
    ),
    (
        ROOT / "analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering_plan.jpg",
        "fold non-boundary ordering",
        "fold display does not create a physical contact/order cue",
    ),
]


def load(path: Path) -> dict:
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


def build_sheet() -> list[dict]:
    panels = []
    panel_w = 620
    label_h = 72
    for path, title, subtitle in SHEET_IMAGES:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((panel_w, 360))
        panel = Image.new("RGB", (panel_w, label_h + img.height), (16, 18, 22))
        draw = ImageDraw.Draw(panel)
        draw.text((0, 0), title, fill=(240, 244, 248), font=font(23))
        draw.text((0, 34), subtitle, fill=(168, 181, 194), font=font(15))
        panel.paste(img, (0, label_h))
        panels.append({"title": title, "path": rel(path), "image": panel})

    if not panels:
        return []

    cols = 2
    margin = 24
    gap = 20
    rows = (len(panels) + cols - 1) // cols
    row_heights = [
        max(p["image"].height for p in panels[r * cols : (r + 1) * cols])
        for r in range(rows)
    ]
    sheet_w = margin * 2 + panel_w * cols + gap
    sheet_h = margin * 2 + 60 + sum(row_heights) + gap * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "3D Fold / Mirror Gate Synthesis", fill=(244, 247, 250), font=font(31))
    draw.text(
        (margin, margin + 38),
        "Geometry confirms page 76 as target surface, but does not supply the extraction unit/order.",
        fill=(172, 184, 196),
        font=font(16),
    )

    y = margin + 60
    for r in range(rows):
        x = margin
        for panel in panels[r * cols : (r + 1) * cols]:
            sheet.paste(panel["image"], (x, y))
            x += panel_w + gap
        y += row_heights[r] + gap
    sheet.save(SHEET, quality=94)
    return [{"title": p["title"], "path": p["path"]} for p in panels]


def stream_hits_count(mapping: dict) -> int:
    total = 0
    for value in mapping.values():
        if isinstance(value, list):
            total += len(value)
        elif value:
            total += 1
    return total


def unit_order_hits_count(mapping: dict) -> int:
    unit_terms = {
        "word",
        "words",
        "letter",
        "letters",
        "line",
        "lines",
        "edge",
        "edges",
        "font",
        "fonts",
        "page",
        "pages",
        "char",
        "chars",
        "character",
        "characters",
        "read",
        "take",
        "select",
        "first",
        "last",
        "key",
        "private",
        "seed",
        "address",
        "wif",
    }
    total = 0
    for value in mapping.values():
        if isinstance(value, list):
            total += sum(1 for item in value if str(item).lower() in unit_terms)
        elif str(value).lower() in unit_terms:
            total += 1
    return total


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    graph = data["reflected_highlight_graph"].get("summary", {})
    twohand = data["page76_twohand_selector"]
    mirror = data["page76_mirror_read_rule"].get("summary", {})
    boxes = data["reflection_box_target_overlap"]
    anchors = data["anchor_point_target_proximity"]
    fold = data["fold_nonboundary_ordering"]
    runtime = data["runtime_view_modes"]
    highres = data["exact_highres_reflection_geometry"]

    twohand_all_term_hits = stream_hits_count(twohand.get("streamInstructionHits", {}))
    twohand_unit_order_hits = unit_order_hits_count(twohand.get("streamInstructionHits", {}))
    anchor_hits = stream_hits_count(anchors.get("streamInstructionHits", {}))
    active_target_overlap_count = boxes.get("overlapReflectionCount", 0)
    reflection_instruction_count = boxes.get("instructionReflectionCount", 0)
    anchors_inside = anchors.get("insideTargetCount", 0)
    anchors_near = anchors.get("nearTargetWithin50Count", 0)
    page76_stable = highres.get("page76Stable", [])

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL/PARTIAL",
            "evidence": "3D geometry is derived from the current locked scan/viewer cache, not a new physical/original-layout source.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as locator",
            "evidence": f"reflected graph has {graph.get('page76MediumPlusEdges')} page-76 medium/strong edges and preserves the El Salvador/IMF/$1B/buying corridor.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": f"two-hand unit/order hits={twohand_unit_order_hits} (all weak term hits={twohand_all_term_hits}); reflection-box instruction hits={reflection_instruction_count}; anchor stream instruction hits={anchor_hits}; literal mirror-read hits are semantic corridor words only.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS as review layer",
            "evidence": "runtime viewer is nonblank under SwiftShader/ANGLE, and the current orientation rule is known: 3D/crop layer is upright; source_images/fresh extraction need rotate180.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": f"direct reflection boxes overlap active targets {active_target_overlap_count} time(s), only O4; anchors inside active targets={anchors_inside}, within 50px={anchors_near}; no direct G5/O5 geometry improvement.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "folded/mirrored 3D geometry synthesis against source-reopen gate; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "reflectedGraphSummary": graph,
        "exactHighresPage76StableCount": len(page76_stable),
        "twoHandWeakTermHitCount": twohand_all_term_hits,
        "twoHandUnitOrderHitCount": twohand_unit_order_hits,
        "mirrorReadSummary": {
            "graphRows": mirror.get("graphRows"),
            "highresRows": mirror.get("highresRows"),
            "sourcePages": mirror.get("streams", {}).get("source_pages"),
        },
        "reflectionBox": {
            "page76ReflectionCount": boxes.get("page76ReflectionCount"),
            "activeTargetOverlapCount": active_target_overlap_count,
            "instructionReflectionCount": reflection_instruction_count,
            "decision": boxes.get("decision"),
        },
        "anchorPoint": {
            "page76AnchorCount": anchors.get("page76AnchorCount"),
            "insideTargetCount": anchors_inside,
            "nearTargetWithin50Count": anchors_near,
            "streamInstructionHitCount": anchor_hits,
            "decision": anchors.get("decision"),
        },
        "foldOrdering": {
            "pairSymmetry": fold.get("pairSymmetry"),
            "orders": fold.get("orders"),
            "decision": fold.get("decision"),
        },
        "runtimeViewModes": {
            "nonblankCaptures": runtime.get("nonblankCaptures"),
            "decision": runtime.get("decision"),
        },
        "gateRows": gate_rows,
        "decision": "3d_fold_mirror_geometry_closed_for_current_scan_as_r3_selector",
        "nextMove": "Keep 3D fold/mirror geometry as orientation, target-location, and source-validation evidence only. Reopen extraction only if new physical/original-layout material changes G5/O5 registration or a raw clue names a specific geometry unit/order such as reflection id, anchor order, fold contact, word, line, or letter.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 3D Fold / Mirror R3 Gate Synthesis",
        "",
        "Scope: consolidate reflected-highlight graph, exact high-res reflection geometry, literal mirror-read, two-hand selector, reflection boxes, anchor points, fold ordering, runtime view modes, and selector-intersection reports against the R1-R5 source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Page-76 medium/strong reflected edges: `{graph.get('page76MediumPlusEdges')}`",
        f"- Page-pair counts: `{graph.get('pairCounts')}`",
        f"- Two-hand weak term hits: `{twohand_all_term_hits}`",
        f"- Two-hand unit/order hits: `{twohand_unit_order_hits}`",
        f"- Direct reflection-box active-target overlaps: `{active_target_overlap_count}`",
        f"- Direct reflection-box instruction hits: `{reflection_instruction_count}`",
        f"- Anchors inside active targets: `{anchors_inside}`",
        f"- Anchors within 50px of active targets: `{anchors_near}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Gate Result",
        "",
        "| gate | status | evidence |",
        "|---|---|---|",
    ]
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")

    lines.extend(
        [
            "",
            "## Consolidated Findings",
            "",
            "- The reflected graph remains meaningful as a locator: all medium/strong reflected hits concentrate on page 76, with balanced `78->76` and `79->76` support.",
            "- Literal mirror reading and two-hand source-page rules produce semantic words already present in the corridor (`buy`, `dip`, `IMF`, `Salvador`, `billion`) rather than a new instruction.",
            "- Direct 3D reflection boxes provide one O4 `buying the dip` graze and no direct G5 `Volcano Bonds` or O5 `shitcoiner at heart` overlap.",
            "- 3D anchors are far from O4/B4/G5/O5; nearest-word streams are navigation/context words, not selector instructions.",
            "- The fold display pairs pages visually for review, but it does not create a physical contact/order cue; page 79 and page 76 are diagonal in that view.",
            "- Runtime viewer modes are verified nonblank and useful for inspection, but focus/layout toggles are display filters, not puzzle rules.",
            "",
            "## Decision",
            "",
            "- Close folded/mirrored 3D geometry as a current-scan `R3` selector.",
            "- Keep 3D geometry as page-76 locator, orientation, and future source-validation evidence only.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
