#!/usr/bin/env python3
"""Create a concrete source-acquisition target packet.

The current evidence stack finds the page-76 target surface but fails R3
unit/order evidence. This packet turns the remaining open dependency into a
shot/export/checklist for physical scans, original layout exports, or raw clue
wording. No extraction streams, key candidates, or address checks are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_acquisition_target_packet.json"
OUT_MD = OUT / "source_acquisition_target_packet.md"
SHEET = OUT / "source_acquisition_target_packet_sheet.jpg"

REPORTS = {
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_packet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "unlock_matrix": ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json",
    "priority_crops": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "p78_tricontact": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "p78_sensitivity": ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.json",
    "p77_one_line": ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json",
    "capsule_recurrence": ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.json",
    "p80_package": ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json",
    "post_unlock_arrival": ROOT / "analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch.json",
}

VISUAL_PANELS = [
    (
        ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
        "page-76 priority targets",
        "O5/G5/L26-L32 baseline",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg",
        "p78 frame tri-contact",
        "should sell | G5 | O5 + M3 edge",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity_overlay.jpg",
        "p78 frame sensitivity",
        "38px G5 near-miss / O5 clip",
    ),
    (
        ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation_overlay.jpg",
        "physical model check",
        "current scan lacks true O5/G5 leaf hits",
    ),
    (
        ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg",
        "zero/#0 hotspots",
        "p77 100,000 is primary future check",
    ),
    (
        ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg",
        "five-capsule motif",
        "Issue-24-specific provenance/order evidence",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis_sheet.jpg",
        "p80 package layer",
        "dose/package count theme, not selector",
    ),
    (
        ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis_sheet.jpg",
        "Typeka/font witness",
        "format/source-validation evidence only",
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
    panel_w = 560
    label_h = 72
    for path, title, subtitle in VISUAL_PANELS:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((panel_w, 320))
        panel = Image.new("RGB", (panel_w, label_h + img.height), (16, 18, 22))
        draw = ImageDraw.Draw(panel)
        draw.text((0, 0), title, fill=(240, 244, 248), font=font(23))
        draw.text((0, 34), subtitle, fill=(168, 181, 194), font=font(15))
        panel.paste(img, (0, label_h))
        panels.append({"title": title, "path": rel(path), "image": panel})

    cols = 2
    margin = 24
    gap = 20
    rows = (len(panels) + cols - 1) // cols
    row_heights = [
        max(p["image"].height for p in panels[r * cols : (r + 1) * cols])
        for r in range(rows)
    ] if rows else []
    sheet_w = margin * 2 + panel_w * cols + gap
    sheet_h = margin * 2 + 66 + sum(row_heights) + gap * max(0, rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "Source Acquisition Target Packet", fill=(244, 247, 250), font=font(31))
    draw.text(
        (margin, margin + 38),
        "Use these visual benchmarks before reopening extraction/key checks.",
        fill=(172, 184, 196),
        font=font(16),
    )
    y = margin + 66
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

    priority = data["priority_crops"]
    future = data["future_packet"]
    reopen = data["source_reopen"]
    unlock = data["unlock_matrix"]
    p77 = data["p77_one_line"]
    p80 = data["p80_package"]

    target_priority = priority.get("targetPriority", {})
    minimum_conditions = future.get("minimumReopenConditions", [])
    reopen_gates = reopen.get("reopenGates", [])
    p78_frame = priority.get("reflectedP78FrameOnP76")
    p77_gap = p77.get("gapVsLinePitch", {})

    capture_jobs = [
        {
            "id": "physical_flat_pages_75_80",
            "kind": "physical scan/photo",
            "priority": 1,
            "ask": "Flat, high-resolution scans/photos of pages 75, 76, 77, 78, 79, and 80.",
            "mustShow": "Readable O4/B4/G5/O5 on page 76; p78 graphic frame; p79 capsules/XX/barbed wire; p80 package copy.",
            "rGates": ["R1", "R2", "R4"],
            "acceptance": "Materially distinct physical/original capture with orientation visible and enough detail to compare priority crops.",
        },
        {
            "id": "physical_leaf_light_pairs",
            "kind": "physical leaf/spread",
            "priority": 2,
            "ask": "Front/back and held-to-light photos for leaves 75/76, 77/78, and 79/80, plus spreads 76/77 and 78/79.",
            "mustShow": "Same leaf edges, page numbers/orientation, and whether any natural bleed/fold selects O5/G5 or the p77 one-line near miss.",
            "rGates": ["R2", "R4", "R5"],
            "acceptance": "Repeated direct O5/G5 contacts or a natural improvement to the p77 71.93px near miss under one transform.",
        },
        {
            "id": "page76_lower_corridor_closeups",
            "kind": "physical/source closeup",
            "priority": 3,
            "ask": "Closeups of page 76 O4/B4/G5/O5 and L25-L32 frame context.",
            "mustShow": "O4 `buying the dip`, B4 `$1 billion`, G5 `Volcano Bonds`, O5 `shitcoiner at heart`, plus adjacent line/edge details.",
            "rGates": ["R2", "R5"],
            "acceptance": "Preserves or explains O-B-B-O, G5/O5, and the p78-frame contact corridor.",
        },
        {
            "id": "original_layout_export",
            "kind": "original layout/export",
            "priority": 4,
            "ask": "Native layout/export source for pages 73-80, including images, highlight rectangles, fonts, and layer names if available.",
            "mustShow": "Higher-resolution assets or layer metadata for highlights, Typeka states, p78 frame, p79 capsules, p80 package, and #0/zero hotspots.",
            "rGates": ["R1", "R3", "R5"],
            "acceptance": "Names or visibly supplies unit/order, or improves source-image quality beyond current scan/668x376 Canva thumbnail.",
        },
        {
            "id": "raw_clue_wording",
            "kind": "external clue/provenance",
            "priority": 5,
            "ask": "Exact raw wording/screenshots/URLs/timestamps for Max/PRIVATE_CONTRIBUTOR/announcement clues, not generated analysis paraphrase.",
            "mustShow": "Any wording naming word, letter, line, edge, font, first/last, left/right, mirror/read direction, page, fold, or order.",
            "rGates": ["R3"],
            "acceptance": "Source-backed instruction language that points to page 76 lower corridor or clearly redirects away from it.",
        },
    ]

    benchmark_checks = [
        {
            "id": "C3",
            "name": "extraction unit/order",
            "current": "FAIL",
            "mustImprove": "Name or visibly supply unit/order before any key checks resume.",
        },
        {
            "id": "C2",
            "name": "p78 frame signature",
            "current": "PARTIAL",
            "mustImprove": "Naturally preserve/explain p78 frame on page 76, O5 clip, M3 right-edge cut, and dx≈-38/-40 G5 repair.",
            "currentFrame": p78_frame,
        },
        {
            "id": "C4",
            "name": "physical registration",
            "current": "FAIL",
            "mustImprove": f"Create repeated direct O5/G5 physical contacts or improve p77 near miss. Current p77 vertical gap={p77_gap.get('baselineVerticalGapPx')} px; median line pitch={p77_gap.get('medianLinePitchPx')} px.",
        },
        {
            "id": "C8",
            "name": "source image quality",
            "current": "FAIL",
            "mustImprove": "Resolve p79 pills/XX/barbed wire, p80 package, #0/zero hotspots, and p78 frame beyond current thumbnail/source limits.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source acquisition target packet; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "unlockMatrixSummary": unlock.get("summary"),
        "sourceReopenDecision": reopen.get("decision"),
        "minimumReopenConditions": minimum_conditions,
        "reopenGates": reopen_gates,
        "targetPriority": target_priority,
        "p80PackageNumbers": p80.get("streams", {}).get("numbers_csv"),
        "captureJobs": capture_jobs,
        "benchmarkChecks": benchmark_checks,
        "decision": "source_acquisition_packet_created_no_current_selector_unlocked",
        "nextMove": "Use this packet to collect or evaluate new physical/original-layout/raw clue evidence. Do not run extraction or key checks until a new item passes R1-R5, especially R3 unit/order evidence.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Acquisition Target Packet",
        "",
        "Scope: convert the current blocker into a concrete shot/export/clue checklist. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Active Target Priority",
        "",
    ]
    for key, value in target_priority.items():
        lines.append(f"- `{key}`: line `{value.get('lineIndex')}`, text `{value.get('text')}`, score `{value.get('score')}`")

    lines.extend(["", "## Capture / Evidence Jobs", "", "| priority | id | kind | ask | must show | gates | acceptance |", "|---:|---|---|---|---|---|---|"])
    for job in capture_jobs:
        lines.append(
            f"| {job['priority']} | `{job['id']}` | {job['kind']} | {job['ask']} | {job['mustShow']} | `{','.join(job['rGates'])}` | {job['acceptance']} |"
        )

    lines.extend(["", "## Benchmark Checks", "", "| id | name | current | must improve |", "|---|---|---|---|"])
    for check in benchmark_checks:
        lines.append(f"| `{check['id']}` | {check['name']} | `{check['current']}` | {check['mustImprove']} |")

    lines.extend(
        [
            "",
            "## Minimum Reopen Conditions",
            "",
        ]
    )
    for item in minimum_conditions:
        lines.append(f"- `{item.get('condition')}`: {item.get('requiredEvidence')}")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- No current selector was unlocked by this packet.",
            "- This packet is an operational checklist for the only high-value open path: new physical/original-layout/source material or raw clue wording.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    if SHEET.exists():
        print(f"wrote {SHEET}")
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
