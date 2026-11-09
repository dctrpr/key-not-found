#!/usr/bin/env python3
"""Synthesize page-76 highlight-cluster evidence against the R1-R5 gate.

This consolidates active O4/B4/G5/O5 target convergence, edge reads, fill
residue, spill/tail direction, spill controls, color-swap, and priority-crop
reports. It does not generate extraction streams or key material; it asks
whether the page-76 orange/black highlight cluster supplies R3 unit/order
evidence or changes source/geometry status under the current scan.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_highlight_cluster_r3_gate_synthesis.json"
OUT_MD = OUT / "page76_highlight_cluster_r3_gate_synthesis.md"
SHEET = OUT / "page76_highlight_cluster_r3_gate_synthesis_sheet.jpg"

REPORTS = {
    "target_convergence": ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json",
    "next_target_chooser": ROOT / "analysis_outputs/source_audit/page76_next_target_chooser/page76_next_target_chooser.json",
    "highlight_edge_selector": ROOT / "analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector.json",
    "active_highlight_fill": ROOT / "analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill.json",
    "highlight_spill_direction": ROOT / "analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction.json",
    "spill_control_comparison": ROOT / "analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison.json",
    "color_swap_filter": ROOT / "analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter.json",
    "color_swap_take_right": ROOT / "analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule.json",
    "lower_mark_pointers": ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.md",
    "priority_crop_pack": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

SHEET_IMAGES = [
    (
        ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
        "page-76 priority crop pack",
        "O5/L32, G5/L27, L26-L29 baseline for future source checks",
    ),
    (
        ROOT / "analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector_overlay.jpg",
        "active highlight edges",
        "adjacent words/edge crossings do not create a selector",
    ),
    (
        ROOT / "analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill_sheet.jpg",
        "active highlight fill",
        "no readable hidden residue after glyph/fill review",
    ),
    (
        ROOT / "analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison_sheet.jpg",
        "spill control comparison",
        "active spill orders are not unique against controls",
    ),
]


def load(path: Path):
    if not path.exists():
        return {}
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return {"text": path.read_text(encoding="utf-8", errors="ignore")}


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
    draw.text((margin, margin), "Page 76 Highlight Cluster Gate", fill=(244, 247, 250), font=font(31))
    draw.text(
        (margin, margin + 38),
        "O-B-B-O is the strongest target surface, not a complete extraction rule.",
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


def top_targets(convergence: dict) -> list[dict]:
    rows = []
    for item in convergence.get("ranking", [])[:5]:
        rows.append(
            {
                "target": item.get("target"),
                "label": item.get("label"),
                "score": item.get("score"),
                "layers": item.get("independentLayerCount"),
            }
        )
    return rows


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    convergence = data["target_convergence"]
    chooser = data["next_target_chooser"]
    edge = data["highlight_edge_selector"]
    fill = data["active_highlight_fill"]
    spill = data["highlight_spill_direction"]
    spill_control = data["spill_control_comparison"]
    color_swap = data["color_swap_filter"]
    take_right = data["color_swap_take_right"]
    priority = data["priority_crop_pack"]
    marks = data["lower_mark_pointers"].get("text", "")

    edge_instruction_hits = stream_hits_count(edge.get("streamInstructionHits", {}))
    take_right_hits = stream_hits_count(take_right.get("instructionHits", {}))
    active_orders_in_controls = spill_control.get("activeOrdersAlsoSeenInControls", [])
    decision = chooser.get("decision", {})
    primary = decision.get("primaryManualTarget", {}) if isinstance(decision, dict) else {}
    paired = decision.get("pairedTarget", {}) if isinstance(decision, dict) else {}
    band = decision.get("sourceBandTarget", {}) if isinstance(decision, dict) else {}

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL/PARTIAL",
            "evidence": "The active O-B-B-O cluster is from the same locked high-res scan and crop cache, not new physical/original-layout evidence.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as locator",
            "evidence": f"O5 `{primary.get('text')}` and G5 `{paired.get('text')}` remain the strongest target pair; O5 score is {top_targets(convergence)[0].get('score') if top_targets(convergence) else 'n/a'}.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": f"edge instruction hits={edge_instruction_hits}; color-swap take/right instruction hits={take_right_hits}; fill/spill reports expose no read/take/word/letter/line/edge/font unit.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS as audited",
            "evidence": "priority crops and active highlight inspections use the readable/upright high-res page-76 layer; source_images/fresh PDF extraction must be rotate180 before comparison.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": f"hidden-fill readable residue is absent; large residual count={fill.get('largeResidualComponentTotal')}; active spill orders also occur in controls={active_orders_in_controls}; color-swap selects upper page-76, not G5/O5.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 O-B-B-O highlight-cluster synthesis against source-reopen gate; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "topTargets": top_targets(convergence),
        "nextTargetDecision": {
            "primary": primary,
            "paired": paired,
            "sourceBand": band,
        },
        "activeCluster": {
            "visualOrder": "O4 -> B4 -> G5 -> O5",
            "colorPattern": "O-B-B-O",
            "labels": ["buying the dip", "$1 billion", "Volcano Bonds", "shitcoiner at heart"],
        },
        "edgeSelector": {
            "instructionHitCount": edge_instruction_hits,
            "streams": edge.get("streams", {}),
            "decision": edge.get("decision"),
        },
        "fillResidue": {
            "largeResidualComponentTotal": fill.get("largeResidualComponentTotal"),
            "decision": fill.get("decision"),
            "sheet": fill.get("sheet"),
        },
        "spillDirection": {
            "dominantSideStream": spill.get("dominantSideStream"),
            "sideStrengthStreams": spill.get("sideStrengthStreams"),
            "decision": spill.get("decision"),
        },
        "spillControl": {
            "dominantSideCounts": spill_control.get("dominantSideCounts"),
            "sideOrderCounts": spill_control.get("sideOrderCounts"),
            "activeOrdersAlsoSeenInControls": active_orders_in_controls,
            "decision": spill_control.get("decision"),
        },
        "colorSwap": {
            "bidirectionalColorSwapPages": color_swap.get("bidirectionalColorSwapPages"),
            "targetIds": color_swap.get("streams", {}).get("targetIds"),
            "decision": color_swap.get("decision"),
            "takeRightDecision": take_right.get("decision"),
        },
        "markPointersClosed": "closes the lower page-76 mark-as-pointer branch" in marks,
        "priorityCropPack": {
            "sheet": priority.get("sheet"),
            "assessment": priority.get("assessment"),
            "nextMove": priority.get("nextMove"),
        },
        "gateRows": gate_rows,
        "decision": "page76_highlight_cluster_closed_for_current_scan_as_r3_selector",
        "nextMove": "Keep O4/B4/G5/O5, especially G5/O5, as page-76 target and future-source validation evidence only. Reopen highlight-cluster extraction only if a raw clue names a unit/order such as side, edge, fill, spill, color swap, word, line, or letter, or if new physical/original-layout evidence changes the active target contacts.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page 76 Highlight Cluster R3 Gate Synthesis",
        "",
        "Scope: consolidate O4/B4/G5/O5 target convergence, edge reads, fill residue, spill/tail direction, spill controls, color-swap, lower marks, and priority crops against the R1-R5 source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Active color pattern: `{result['activeCluster']['colorPattern']}`",
        f"- Active visual order: `{result['activeCluster']['visualOrder']}`",
        f"- Primary target: `L{primary.get('lineIndex')}` `{primary.get('text')}`",
        f"- Paired target: `L{paired.get('lineIndex')}` `{paired.get('text')}`",
        f"- Edge selector instruction hits: `{edge_instruction_hits}`",
        f"- Fill large residual components: `{fill.get('largeResidualComponentTotal')}`",
        f"- Spill dominant-side stream: `{spill.get('dominantSideStream')}`",
        f"- Active spill orders also seen in controls: `{active_orders_in_controls}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Gate Result",
        "",
        "| gate | status | evidence |",
        "|---|---|---|",
    ]
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")

    lines.extend(["", "## Top Target Evidence", ""])
    for item in result["topTargets"]:
        lines.append(f"- `{item['target']}` `{item['label']}`: score `{item['score']}`, independent layers `{item['layers']}`")

    lines.extend(
        [
            "",
            "## Consolidated Findings",
            "",
            "- The page-76 highlight cluster is real and important as a target surface: O5 `shitcoiner at heart` and G5 `Volcano Bonds` remain the strongest pair.",
            "- The O-B-B-O visual order does not itself name whether to read words, letters, edges, sides, fill, spill, or colors.",
            "- Active highlight edges produce local prose streams (`b$Vs`, `pnst`, adjacent words) with zero instruction hits.",
            "- Active highlight fill residue shows no readable hidden word, symbol sequence, or ordering mark after accounting for glyph/highlight pixels.",
            "- Active spill/tail direction is not unique against page-76 controls, so side imbalance cannot be promoted to a selector.",
            "- Color-swap mirroring reduces noise but selects the upper page-76 cluster, not lower G5/O5, and `take/right` is printed content rather than a rule.",
            "- Lower non-text marks reinforce the same El Salvador/Novogratz/O5 region but do not provide an independent order.",
            "",
            "## Decision",
            "",
            "- Close the page-76 O-B-B-O highlight cluster as a current-scan `R3` selector.",
            "- Keep O4/B4/G5/O5 as target-location and future source-validation evidence only.",
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
