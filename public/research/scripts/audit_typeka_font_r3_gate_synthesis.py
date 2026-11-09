#!/usr/bin/env python3
"""Synthesize Typeka/font-state evidence against the R1-R5 gate.

This consolidates existing DOCM/Typeka/BOLD/font reports into one current-scan
decision. It does not generate extraction streams or key material; it asks
whether the font layer supplies source-backed R3 unit/order evidence or changes
the source/geometry status.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "typeka_font_r3_gate_synthesis.json"
OUT_MD = OUT / "typeka_font_r3_gate_synthesis.md"
SHEET = OUT / "typeka_font_r3_gate_synthesis_sheet.jpg"

REPORTS = {
    "typeka_instruction_surface": ROOT / "analysis_outputs/docm_format_sources/typeka_instruction_surface/typeka_instruction_surface.json",
    "lower_corridor_font_state_selector": ROOT / "analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.json",
    "typeka_manual_bold_disambiguation": ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json",
    "repaired_frame_font_contact_states": ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json",
    "typeka_transition_boundaries": ROOT / "analysis_outputs/docm_format_sources/typeka_transition_boundaries/typeka_transition_boundaries.json",
    "typeka_highlight_boundary_alignment": ROOT / "analysis_outputs/docm_format_sources/typeka_highlight_boundary_alignment/typeka_highlight_boundary_alignment.json",
    "docm_visual_highlight_consistency": ROOT / "analysis_outputs/docm_format_sources/docm_visual_highlight_consistency/docm_visual_highlight_consistency.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

SHEET_IMAGES = [
    (
        ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg",
        "page 76 target surface",
        "readable/upright scan; font layer labels the active corridor",
    ),
    (
        ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg",
        "DOCM vs manual bold",
        "Article with Fonts.docm is the font witness; manual bold is annotation",
    ),
    (
        ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states_sheet.jpg",
        "repaired p78 frame contacts",
        "clean R-K-Y contact is registration evidence, not an extraction rule",
    ),
    (
        ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg",
        "source reopen gate",
        "R1-R5 still required before extraction/key checks resume",
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
    draw.text((margin, margin), "Typeka / Font-State Gate Synthesis", fill=(244, 247, 250), font=font(31))
    draw.text(
        (margin, margin + 38),
        "The font layer marks the active corridor but does not name the extraction unit/order.",
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


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    instruction = data["typeka_instruction_surface"]
    lower = data["lower_corridor_font_state_selector"]
    manual = data["typeka_manual_bold_disambiguation"]
    repaired = data["repaired_frame_font_contact_states"]
    transition = data["typeka_transition_boundaries"]
    boundary = data["typeka_highlight_boundary_alignment"]
    visual = data["docm_visual_highlight_consistency"]

    strong_instruction_count = len(instruction.get("strongInstructionRecords", []))
    procedural_no_unit_count = len(instruction.get("proceduralNoUnitRecords", []))
    unit_no_action_count = len(instruction.get("unitNoActionRecords", []))
    lower_stream_hits = lower.get("streamInstructionHits", {})
    repaired_instruction_hits = repaired.get("allInstructionTermHits", {})
    boundary_hits = boundary.get("instructionHits", {})
    boundary_counts = boundary.get("counts", {})
    manual_summary = manual.get("summary", {})
    visual_counts = visual.get("counts", {})

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL/PARTIAL",
            "evidence": "Article with Fonts.docm is a local formatting witness, not a new physical/original-layout source; BOLD.docm is annotation/generated sanity material unless original workflow files reappear.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as corroboration",
            "evidence": "Typeka/font states label the active page-76 corridor and the repaired R-K-Y contact trio: should sell | Volcano Bonds | shitcoiner at heart.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": f"strong Typeka instruction records: {strong_instruction_count}; unit-without-action records: {unit_no_action_count}; procedural/directional/index terms without unit: {procedural_no_unit_count}.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS as audited",
            "evidence": "DOCM font labels are used as a text/run witness after visual region selection; manual Markdown bold is explicitly separated from original typography.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": "Font/style streams and repaired contact states produce no instruction hits and do not improve the source-registration benchmark without a separate source/clue.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Typeka/font-state synthesis against source-reopen gate; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "variantRunCounts": instruction.get("variantRunCounts", {}),
        "strongInstructionRecordCount": strong_instruction_count,
        "proceduralNoUnitRecordCount": procedural_no_unit_count,
        "unitNoActionRecordCount": unit_no_action_count,
        "lowerCorridorStreams": lower.get("streams", {}),
        "lowerCorridorInstructionHits": lower_stream_hits,
        "manualBoldSummary": manual_summary,
        "repairedFrameInstructionHits": repaired_instruction_hits,
        "typekaTransitionDecision": transition.get("decision"),
        "typekaBoundaryCounts": {
            "fontChangeBoundaryCount": boundary_counts.get("fontChangeBoundaryCount"),
            "typekaMixBoundaryCount": boundary_counts.get("typekaMixBoundaryCount"),
            "highlightChangeBoundaryCount": boundary_counts.get("highlightChangeBoundaryCount"),
            "highlightedTypekaMixRunCount": boundary_counts.get("highlightedTypekaMixRunCount"),
            "highlightedTypekaMixCharCount": boundary_counts.get("highlightedTypekaMixCharCount"),
        },
        "typekaBoundaryInstructionHits": boundary_hits,
        "docmVisualHighlightCounts": visual_counts,
        "gateRows": gate_rows,
        "decision": "typeka_font_layer_closed_for_current_scan_as_r3_selector",
        "nextMove": "Keep Article with Fonts.docm as a formatting/font witness and Typeka as corridor/provenance support only. Reopen font-state extraction only if a raw clue names font/Typeka/Mix/bold as the unit or if a new physical/original-layout source selects exact font-run units.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Typeka / Font-State R3 Gate Synthesis",
        "",
        "Scope: consolidate existing Typeka, BOLD, DOCM, lower-corridor font, boundary, and repaired-frame reports against the R1-R5 source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Variant run counts: `{result['variantRunCounts']}`",
        f"- Strong Typeka instruction records: `{strong_instruction_count}`",
        f"- Procedural/directional/index terms without unit: `{procedural_no_unit_count}`",
        f"- Unit terms without action: `{unit_no_action_count}`",
        f"- Lower-corridor stream instruction hits: `{lower_stream_hits}`",
        f"- Repaired-frame instruction hits: `{repaired_instruction_hits}`",
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
            "- `Article with Fonts.docm` remains the local authority for Typeka, Typeka Mix, bold, and highlight labels; old Markdown bold is a user annotation layer.",
            "- Typeka Mix/Bold marks real active-corridor text: El Salvador, buying the dip, `$1 billion`, Volcano Bonds, IMF, Mike/Novogratz, trust, and shitcoiner at heart.",
            "- The repaired p78 frame gives a compact `R-K-Y` contact signature (`should sell | Volcano Bonds | shitcoiner at heart`), but `R-K-Y`, initials, lasts, and contact classes have no instruction hits.",
            "- Typeka transition/boundary reports show formatting structure, including Mix boundaries and highlight boundaries, but highlighted Typeka Mix run count is zero.",
            "- The only font-boundary instruction-like hit is weak context (`first`) without a unit/order; it cannot promote the font layer to a selector.",
            "- Comparison PDFs and local source intake do not promote Typeka metadata into Issue 24 extraction geometry.",
            "",
            "## Decision",
            "",
            "- Close Typeka/font-state as a current-scan `R3` selector.",
            "- Keep Typeka as formatting witness, target-corridor corroboration, and future source-validation evidence.",
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
