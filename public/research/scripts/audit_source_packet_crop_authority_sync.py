#!/usr/bin/env python3
"""Sync-check the source-acquisition packet against the completed crop authority.

The source-acquisition packet was created before the O4/B4/G5/O5 crop sheet was
completed. This pass creates a supplemental handoff report so future source
comparisons use the current 4/4 visual authority without rewriting historical
packet evidence. It does not run extraction, hashing, key derivation,
WIF/Base58 scans, OCR, or address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_crop_authority_sync"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_crop_authority_sync.json"
OUT_MD = OUT / "source_packet_crop_authority_sync.md"
SHEET = OUT / "source_packet_crop_authority_sync_sheet.jpg"

INPUTS = {
    "source_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
    "packet_integrity": ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.json",
    "crop_completion": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
    "format_lock": ROOT
    / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
    "text_lock": ROOT
    / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.json",
    "future_rubric": ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json",
}

THUMBNAILS = [
    {
        "title": "source packet",
        "path": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet_sheet.jpg",
    },
    {
        "title": "completed O4/B4/G5/O5 crops",
        "path": ROOT
        / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion_sheet.jpg",
    },
    {
        "title": "format authority",
        "path": ROOT
        / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock_sheet.jpg",
    },
    {
        "title": "future rubric",
        "path": ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric_sheet.jpg",
    },
]

ACTIVE_TARGET_IDS = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]


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


def file_row(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {"path": None, "exists": False, "size": 0}
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return {"path": rel(p), "exists": p.exists(), "size": p.stat().st_size if p.exists() else 0}


def paste_thumb(sheet: Image.Image, path: Path, box: tuple[int, int, int, int], title: str) -> None:
    draw = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(18, 22, 28), outline=(50, 58, 70))
    draw.text((x0 + 12, y0 + 10), title, fill=(238, 243, 248), font=font(17))
    if not path.exists():
        draw.text((x0 + 12, y0 + 42), "missing", fill=(255, 130, 130), font=font(14))
        return
    image = Image.open(path).convert("RGB")
    max_w = x1 - x0 - 24
    max_h = y1 - y0 - 58
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resample = getattr(Image, "Resampling", Image).LANCZOS
    resized = image.resize(new_size, resample)
    sheet.paste(resized, (x0 + 12, y0 + 44))


def build_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1760, 1460
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Source Packet Crop Authority Sync", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 45),
        "Supplemental handoff check: source packet remains valid, but active visual authority is now the 4/4 crop sheet.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("sync status", result["summary"]["syncStatus"]),
        ("crop coverage", result["summary"]["cropCoverage"]),
        ("old packet panel", "3/4 crop sheet"),
        ("selector", "blocked"),
        ("dead branches", result["summary"]["deadBranchCount"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 310, y + 52), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 27), str(value)[:30], fill=(232, 239, 246), font=mono)
        x += 330

    y += 82
    draw.rectangle((margin, y, sheet_w - margin, y + 150), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Handoff Rule", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Use source-acquisition packet for jobs/gates, then use completed O4/B4/G5/O5 crop sheet for page-76 visual comparison.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 78),
        "Do not use old projected p76 grey boxes for B4/G5 geometry; they are documented as landing on unrelated lower-page text.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 110),
        "This sync does not unlock extraction; R3 unit/order evidence is still required before selector/key checks resume.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 180
    headers = [("target", 12), ("visual", 270), ("line/corr", 420), ("box", 570), ("crop file", 830)]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["targetRows"]:
        fill = (18, 22, 28) if row["exists"] else (45, 25, 25)
        draw.rectangle((margin, y, sheet_w - margin, y + 44), fill=fill, outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["label"], fill=(238, 243, 248), font=small)
        draw.text((margin + 270, y + 12), row["visualState"], fill=(238, 243, 248), font=mono)
        draw.text((margin + 420, y + 12), f"L{row['pageLine']}/C{row['corridorIndex']}", fill=(238, 243, 248), font=mono)
        draw.text((margin + 570, y + 12), str(row["box"]), fill=(176, 186, 198), font=small)
        draw.text((margin + 830, y + 12), Path(row["output"]).name, fill=(176, 186, 198), font=small)
        y += 48

    y += 24
    thumb_w = (sheet_w - margin * 2 - 28) // 2
    thumb_h = 360
    for idx, thumb in enumerate(THUMBNAILS):
        col = idx % 2
        row = idx // 2
        x0 = margin + col * (thumb_w + 28)
        y0 = y + row * (thumb_h + 22)
        paste_thumb(sheet, thumb["path"], (x0, y0, x0 + thumb_w, y0 + thumb_h), thumb["title"])

    sheet.save(SHEET, quality=94)


def count_dead_branches() -> int:
    path = ROOT / "analysis_outputs/dead_branch_blacklist.md"
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- "))


def main() -> None:
    source_packet = load_json(INPUTS["source_packet"])
    integrity = load_json(INPUTS["packet_integrity"])
    crop_completion = load_json(INPUTS["crop_completion"])
    format_lock = load_json(INPUTS["format_lock"])
    text_lock = load_json(INPUTS["text_lock"])
    future_rubric = load_json(INPUTS["future_rubric"])

    packet_panels = source_packet.get("sheetPanels", [])
    old_priority_panel_present = any(
        "page76_priority_crop_pack/page76_priority_crop_sheet.jpg" in (panel.get("path") or "")
        for panel in packet_panels
    )
    completed_panel_in_historical_packet = any(
        "page76_active_target_crop_completion" in (panel.get("path") or "") for panel in packet_panels
    )

    target_rows = []
    for target in crop_completion.get("targets", []):
        output_info = file_row(target.get("output"))
        target_rows.append(
            {
                "id": target.get("id"),
                "label": target.get("label"),
                "visualState": target.get("visualState"),
                "pageLine": target.get("pageLine"),
                "corridorIndex": target.get("corridorIndex"),
                "box": target.get("box"),
                "output": output_info["path"],
                "exists": output_info["exists"],
                "size": output_info["size"],
            }
        )

    all_target_crops_present = len(target_rows) == 4 and all(row["exists"] for row in target_rows)
    active_ids_present = sorted(row["id"] for row in target_rows) == sorted(ACTIVE_TARGET_IDS)
    packet_still_valid = integrity.get("status") == "PASS" and source_packet.get("decision") == "source_acquisition_packet_created_no_current_selector_unlocked"
    sync_status = (
        "PASS_WITH_SUPPLEMENTAL_APPENDIX"
        if packet_still_valid and all_target_crops_present and old_priority_panel_present
        else "REVIEW_NEEDED"
    )

    summary = {
        "syncStatus": sync_status,
        "historicalPacketStillValid": packet_still_valid,
        "historicalPacketUsesOldPriorityCropPanel": old_priority_panel_present,
        "completedCropPanelAlreadyInHistoricalPacket": completed_panel_in_historical_packet,
        "cropCoverage": crop_completion.get("summary", {}).get("cropCoverage"),
        "allTargetCropsPresent": all_target_crops_present,
        "activeIdsPresent": active_ids_present,
        "formatAuthority": format_lock.get("authorityLock", {}).get("formatAuthority"),
        "textAuthority": text_lock.get("authorityLock", {}).get("targetTextAuthority"),
        "futureRubricExtractionGate": future_rubric.get("extractionGate", {}).get("allowExtractionOnlyIf"),
        "selectorUnlocked": False,
        "deadBranchCount": count_dead_branches(),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source packet crop authority sync; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "targetRows": target_rows,
        "handoffRule": {
            "useForJobsAndGates": "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.md",
            "useForActivePage76VisualComparison": "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.md",
            "doNotUseForB4G5Geometry": "old projected p76 grey boxes from the grey-reading audit",
            "r3GateStillRequired": True,
        },
        "sheet": rel(SHEET),
        "decision": "source_packet_crop_authority_synced_with_supplemental_appendix_no_selector",
        "nextMove": "When new source material appears, score it with the source-acquisition packet/R1-R5 rubric and compare page-76 targets against the completed O4/B4/G5/O5 crop sheet before any extraction attempt.",
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Crop Authority Sync",
        "",
        "Scope: check whether the source-acquisition handoff now points future source comparisons at the completed O4/B4/G5/O5 crop authority. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Sync status: `{summary['syncStatus']}`",
        f"- Historical source packet still valid: `{summary['historicalPacketStillValid']}`",
        f"- Historical packet uses old priority-crop panel: `{summary['historicalPacketUsesOldPriorityCropPanel']}`",
        f"- Completed crop panel already in historical packet: `{summary['completedCropPanelAlreadyInHistoricalPacket']}`",
        f"- Completed active crop coverage: `{summary['cropCoverage']}`",
        f"- All target crops present: `{summary['allTargetCropsPresent']}`",
        f"- Selector unlocked: `{summary['selectorUnlocked']}`",
        f"- Dead-branch count: `{summary['deadBranchCount']}`",
        "",
        "## Handoff Rule",
        "",
        f"- Use for jobs/gates: `{result['handoffRule']['useForJobsAndGates']}`",
        f"- Use for active page-76 visual comparison: `{result['handoffRule']['useForActivePage76VisualComparison']}`",
        f"- Do not use for B4/G5 geometry: {result['handoffRule']['doNotUseForB4G5Geometry']}",
        f"- R3 gate still required: `{result['handoffRule']['r3GateStillRequired']}`",
        "",
        "## Target Crop Files",
        "",
        "| target | visual | line/corridor | box | output | exists |",
        "|---|---|---|---|---|---:|",
    ]
    for row in target_rows:
        lines.append(
            f"| `{row['label']}` | `{row['visualState']}` | `L{row['pageLine']}/C{row['corridorIndex']}` | `{row['box']}` | `{row['output']}` | `{row['exists']}` |"
        )
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
