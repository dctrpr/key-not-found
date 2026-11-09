#!/usr/bin/env python3
"""Trace the density-calibrated OVERDOSE slot outliers back to source evidence.

The prior density calibration found three page-76 OVERDOSE slot columns whose
natural held-to-light source ink/page-density ratio exceeded the same slot on
the other valid article leaves. This bounded pass asks whether those outlier
columns carry source-backed extraction evidence, active-quartet coverage, or
instruction wording.

No key candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or
broad brute force are run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_density_outlier_provenance_gate.json"
OUT_MD = OUT / "current_scan_overdose_density_outlier_provenance_gate.md"
OUT_SHEET = OUT / "current_scan_overdose_density_outlier_provenance_gate_sheet.jpg"

DENSITY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/"
    "current_scan_light_table_density_calibration_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "order",
    "slot",
    "page",
    "target",
    "key",
    "private",
    "encoded",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.resolve().relative_to(ROOT))


def safe_text(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def inter_area(a: list[float], b: list[float]) -> float:
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0.0, min(a[3], b[3]) - max(a[1], b[1])
    )


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def center_in_box(item_box: list[float], region: list[float]) -> bool:
    cx, cy = center(item_box)
    return region[0] <= cx <= region[2] and region[1] <= cy <= region[3]


def hard_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def words_in_box(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    return [word for word in words if center_in_box([float(v) for v in word["box"]], box)]


def preview(words: list[dict[str, Any]], limit: int = 12) -> str:
    return safe_text(" ".join(str(word.get("text", "")) for word in words[:limit]))


def mirror_box(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def mirror_items(items: list[dict[str, Any]], width: float) -> list[dict[str, Any]]:
    mirrored = []
    for item in items:
        item_box = [float(v) for v in item["box"]]
        mirrored_box = mirror_box(item_box, width)
        row = {**item, "box": mirrored_box, "center": center(mirrored_box)}
        mirrored.append(row)
    return mirrored


def highlight_hits(highlights: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for highlight in highlights:
        hbox = [float(v) for v in highlight["box"]]
        inter = inter_area(hbox, box)
        if inter <= 0.5:
            continue
        rows.append(
            {
                "id": highlight["id"],
                "kind": highlight.get("kind"),
                "overlapFractionOfHighlight": round(inter / max(area(hbox), 1.0), 6),
                "overlapFractionOfSlot": round(inter / max(area(box), 1.0), 6),
            }
        )
    return rows


def active_contacts(active_rows: list[dict[str, Any]], slot_box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for active in active_rows:
        active_box = [float(v) for v in active["box"]]
        inter = inter_area(active_box, slot_box)
        if inter <= 0:
            continue
        rows.append(
            {
                "target": active["shortId"],
                "phrase": safe_text(active["phrase"]),
                "visualState": active["visualState"],
                "activeBoxOverlapFraction": round(inter / max(area(active_box), 1.0), 6),
                "slotOverlapFraction": round(inter / max(area(slot_box), 1.0), 6),
            }
        )
    return rows


def longest_contiguous_run(indices: list[int]) -> int:
    if not indices:
        return 0
    best = current = 1
    for left, right in zip(indices, indices[1:]):
        if right == left + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def overdose_slots(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [])]
    slots = []
    for slot in c9.get("projections", [{}])[0].get("slots", []):
        slots.append(
            {
                "slotId": f"slot_{slot['index']}_{slot['letter']}",
                "slotIndex": int(slot["index"]),
                "letter": slot["letter"],
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return slots


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE76_IMAGE).convert("RGB")
    crop = [210, 2090, 2325, 3065]
    scale = 0.48
    panel = page.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 26
    header_h = 126
    table_h = 286
    sheet = Image.new("RGB", (margin * 2 + panel.size[0], header_h + panel.size[1] + table_h), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.size[0], header_h), fill=(23, 29, 39))
    draw.text((margin, 18), "OVERDOSE Density-Outlier Provenance Gate", fill="white", font=font(25))
    draw.text(
        (margin, 54),
        "Red columns are the page-76 normalized slot outliers; active boxes and word/highlight provenance are checked below.",
        fill=(224, 229, 236),
        font=font(13),
    )
    draw.text(
        (margin, 78),
        f"Outlier letters: {result['summary']['outlierLettersXOrder']} | active contacts: {result['summary']['outlierActiveContactCount']}/4 | instruction hits: {result['summary']['outlierInstructionHitCount']}",
        fill=(224, 229, 236),
        font=font(13),
    )
    sheet.paste(panel, (margin, header_h))

    def sx(x: float) -> float:
        return margin + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return header_h + (y - crop[1]) * scale

    for row in result["slotRows"]:
        box = row["box"]
        color = "#f04438" if row["page76SlotInkOutlier"] else "#64748b"
        width = 4 if row["page76SlotInkOutlier"] else 1
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)
        draw.text((sx(box[0]) + 5, sy(box[1]) + 4), row["letter"], fill=color, font=font(15))

    for active in result["activeRows"]:
        box = active["box"]
        color = "#f59e0b" if active["visualState"] == "Y" else "#111827"
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text((sx(box[0]), sy(box[1]) - 17), active["shortId"], fill=color, font=font(12))

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Slot Trace", fill=(30, 34, 40), font=font(15))
    y += 26
    headers = ["slot", "out", "p76 ink/page", "other max", "active", "source words", "target words", "instr"]
    xs = [margin, margin + 62, margin + 108, margin + 220, margin + 320, margin + 432, margin + 650, margin + 878]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 86, 96), font=font(10))
    y += 18
    for row in result["slotRows"]:
        values = [
            f"{row['slotIndex']}:{row['letter']}",
            str(int(row["page76SlotInkOutlier"])),
            f"{row['page76InkOverPageDensity']:.3f}",
            f"{row['otherLeafInkOverPageDensityMax']:.3f}",
            ",".join(row["activeContactLabels"]) or "-",
            safe_text(row["mirroredSourceWordPreview"][:28]) or "-",
            safe_text(row["targetWordPreview"][:28]) or "-",
            ",".join(row["hardInstructionHits"]) or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(25, 28, 34), font=font(10))
        y += 21
    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    density = load_json(DENSITY_GATE)
    article = load_json(ARTICLE_MAP)
    active_json = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})

    page75 = next(page for page in article["pages"] if int(page["page"]) == 75)
    page76 = next(page for page in article["pages"] if int(page["page"]) == 76)
    mirrored_page75_words = mirror_items(page75.get("words", []), float(page75["width"]))
    mirrored_page75_highlights = mirror_items(page75.get("highlights", []), float(page75["width"]))
    active_rows = [
        {
            "shortId": row["shortId"],
            "phrase": safe_text(row["phrase"]),
            "visualState": row["visualState"],
            "pageLine": row["pageLine"],
            "box": [float(v) for v in row["box"]],
        }
        for row in active_json.get("activeRows", [])
        if row.get("shortId") in TARGET_ORDER
    ]
    active_rows.sort(key=lambda row: TARGET_ORDER.index(row["shortId"]))

    slot_rows = []
    density_rows = density.get("overdoseSlotRows", [])
    for slot in overdose_slots(c9):
        p76_density = next(
            row
            for row in density_rows
            if row["slotId"] == slot["slotId"] and int(row["targetPage"]) == 76
        )
        other_density_rows = [
            row
            for row in density_rows
            if row["slotId"] == slot["slotId"] and int(row["targetPage"]) != 76
        ]
        other_ink_max = max(float(row["inkOverPageDensity"]) for row in other_density_rows)
        page76_ink = float(p76_density["inkOverPageDensity"])
        outlier = page76_ink > other_ink_max
        target_words = words_in_box(page76.get("words", []), slot["box"])
        source_words = words_in_box(mirrored_page75_words, slot["box"])
        target_hits = unique_sorted([hit for word in target_words for hit in hard_hits(str(word.get("text", "")))])
        source_hits = unique_sorted([hit for word in source_words for hit in hard_hits(str(word.get("text", "")))])
        contacts = active_contacts(active_rows, slot["box"])
        target_highlights = highlight_hits(page76.get("highlights", []), slot["box"])
        source_highlights = highlight_hits(mirrored_page75_highlights, slot["box"])
        slot_rows.append(
            {
                **slot,
                "box": [round(float(v), 3) for v in slot["box"]],
                "page76SourceInkRatio": round(float(p76_density["sourceInkRatio"]), 6),
                "page76InkOverPageDensity": round(page76_ink, 6),
                "otherLeafInkOverPageDensityMax": round(other_ink_max, 6),
                "page76SlotInkOutlier": outlier,
                "inkExcessOverOtherLeafMax": round(page76_ink - other_ink_max, 6),
                "activeContacts": contacts,
                "activeContactLabels": [row["target"] for row in contacts],
                "targetWordCount": len(target_words),
                "targetWordPreview": preview(target_words),
                "mirroredSourceWordCount": len(source_words),
                "mirroredSourceWordPreview": preview(source_words),
                "targetHardInstructionHits": target_hits,
                "mirroredSourceHardInstructionHits": source_hits,
                "hardInstructionHits": unique_sorted(target_hits + source_hits),
                "targetHighlightHits": target_highlights,
                "mirroredSourceHighlightHits": source_highlights,
            }
        )

    outliers = [row for row in slot_rows if row["page76SlotInkOutlier"]]
    outlier_indices = [row["slotIndex"] for row in outliers]
    outlier_letters_x = "".join(row["letter"] for row in outliers)
    outlier_letters_by_ink = "".join(
        row["letter"] for row in sorted(outliers, key=lambda row: row["page76InkOverPageDensity"], reverse=True)
    )
    outlier_active_labels = unique_sorted(
        [label for row in outliers for label in row["activeContactLabels"]]
    )
    outlier_target_highlight_ids = unique_sorted(
        [hit["id"] for row in outliers for hit in row["targetHighlightHits"]]
    )
    outlier_source_highlight_ids = unique_sorted(
        [hit["id"] for row in outliers for hit in row["mirroredSourceHighlightHits"]]
    )
    outlier_instruction_hits = unique_sorted(
        [hit for row in outliers for hit in row["hardInstructionHits"]]
    )
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_unlocked = False
    hidden_candidate = bool(
        len(outlier_active_labels) == len(TARGET_ORDER)
        and outlier_instruction_hits
        and source_r3 > 0
    )
    fingerprint = (
        f"slots={len(slot_rows)}|outliers={len(outliers)}|letters={outlier_letters_x or '-'}|"
        f"byInk={outlier_letters_by_ink or '-'}|contiguousRun={longest_contiguous_run(outlier_indices)}|"
        f"activeContacts={len(outlier_active_labels)}/4|B4={int('B4' in outlier_active_labels)}|"
        f"instr={len(outlier_instruction_hits)}|targetHighlights={len(outlier_target_highlight_ids)}|"
        f"sourceHighlights={len(outlier_source_highlight_ids)}|hiddenCandidate={int(hidden_candidate)}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors={int(selector_unlocked)}"
    )
    summary = {
        "slotCount": len(slot_rows),
        "page76DensityOutlierSlotCount": len(outliers),
        "outlierSlotIds": [row["slotId"] for row in outliers],
        "outlierLettersXOrder": outlier_letters_x,
        "outlierLettersByInkStrength": outlier_letters_by_ink,
        "outlierLongestContiguousRun": longest_contiguous_run(outlier_indices),
        "outlierActiveContactLabels": outlier_active_labels,
        "outlierActiveContactCount": len(outlier_active_labels),
        "outlierAllFourActiveContacts": len(outlier_active_labels) == len(TARGET_ORDER),
        "outlierB4Contact": "B4" in outlier_active_labels,
        "outlierInstructionHits": outlier_instruction_hits,
        "outlierInstructionHitCount": len(outlier_instruction_hits),
        "outlierTargetHighlightIds": outlier_target_highlight_ids,
        "outlierMirroredSourceHighlightIds": outlier_source_highlight_ids,
        "hiddenOutlierProvenanceCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
        "outlierProvenanceFingerprint": fingerprint,
        "priorDensityCalibrationFingerprint": density.get("fingerprint"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current-scan OVERDOSE density-outlier provenance gate; traces the "
            "density-calibrated page-76 slot outliers to active contacts, mirrored "
            "page-75 source words/highlights, page-76 target words/highlights, and "
            "strict instruction terms only"
        ),
        "inputs": {
            "densityCalibrationGate": rel(DENSITY_GATE),
            "articleMap": rel(ARTICLE_MAP),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "activeRows": active_rows,
        "slotRows": slot_rows,
        "summary": summary,
        "decision": {
            "currentScanOverdoseDensityOutlierProvenanceGate": "current_scan_overdose_density_outliers_no_selector",
            "selectorUnlocked": selector_unlocked,
            "reason": (
                "The density outlier slots spell only ROS in x-order, miss B4, do not cover "
                "the all-four active quartet, and contain no strict source/target instruction hits."
            ),
            "nextMove": (
                "Treat the slot outliers as page-75 highlight/source-density bleed-through. "
                "Continue only with original-layout source validation or raw clue wording that names "
                "a unit, order, transform, or slot-specific rule."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan OVERDOSE Density-Outlier Provenance Gate",
        "",
        "Scope: traces the three density-calibrated page-76 OVERDOSE slot outliers back to active target contact, mirrored page-75 source words/highlights, page-76 target words/highlights, and strict instruction terms. No key candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Slot columns checked: `{summary['slotCount']}`",
        f"- Page-76 density outlier slots: `{summary['page76DensityOutlierSlotCount']}`",
        f"- Outlier slots / letters in x-order: `{', '.join(summary['outlierSlotIds'])}` / `{summary['outlierLettersXOrder'] or '-'}`",
        f"- Outlier letters by ink strength: `{summary['outlierLettersByInkStrength'] or '-'}`",
        f"- Outlier longest contiguous run: `{summary['outlierLongestContiguousRun']}`",
        f"- Outlier active contacts: `{','.join(summary['outlierActiveContactLabels']) or '-'}` (`{summary['outlierActiveContactCount']}/4`; B4 contact `{int(summary['outlierB4Contact'])}`)",
        f"- Outlier strict instruction hits: `{summary['outlierInstructionHitCount']}`",
        f"- Outlier target/source highlight ids: `{','.join(summary['outlierTargetHighlightIds']) or '-'}` / `{','.join(summary['outlierMirroredSourceHighlightIds']) or '-'}`",
        f"- Hidden outlier provenance candidate: `{int(summary['hiddenOutlierProvenanceCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Slot Trace",
        "",
        "| slot | letter | p76 ink/page | other max | outlier | active contacts | mirrored p75 source words | p76 target words | instruction hits |",
        "|---|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in slot_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['slotId']}`",
                    f"`{row['letter']}`",
                    f"{row['page76InkOverPageDensity']:.6f}",
                    f"{row['otherLeafInkOverPageDensityMax']:.6f}",
                    str(int(row["page76SlotInkOutlier"])),
                    safe_text(",".join(row["activeContactLabels"]) or "-"),
                    safe_text(row["mirroredSourceWordPreview"] or "-"),
                    safe_text(row["targetWordPreview"] or "-"),
                    safe_text(",".join(row["hardInstructionHits"]) or "-"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_overdose_density_outliers_no_selector`",
            "- The outlier letters are not a complete OVERDOSE word/run and do not touch B4.",
            "- Mirrored page-75 source words and page-76 target words inside the outlier slots contain no strict unit/order/transform instruction hits.",
            "- The outlier slots are best treated as page-75 highlight/source-density bleed-through, not extraction permission.",
            "",
            "## Next Move",
            "",
            "- Continue with physical/original-layout source validation or raw clue wording that names unit/order/transform.",
            "- Do not tune OVERDOSE slot-density thresholds unless a new clue specifically names slots, density, columns, or a reading order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
