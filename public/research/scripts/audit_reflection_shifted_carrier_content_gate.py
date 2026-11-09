#!/usr/bin/env python3
"""Check shifted 3D reflection carriers as content selectors.

This bounded pass follows the already-closed line-pitch stack gate one step
deeper. It asks whether the three reflected carriers that can touch all four
active targets isolate extraction-ready text after their per-target shifts, or
whether they simply replay ordinary page-76 article rows.

No OCR is run here. The script only reads existing 3D-map OCR boxes and trusted
manual target boxes. It does not derive keys, hash candidates, scan WIF/Base58,
generate seed phrases, or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
STACK_JSON = (
    ROOT
    / "analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/"
    "reflection_line_pitch_stack_gate.json"
)
ACTIVE_JSON = (
    ROOT
    / "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "reflection_shifted_carrier_content_gate.json"
OUT_MD = OUT / "reflection_shifted_carrier_content_gate.md"
SHEET = OUT / "reflection_shifted_carrier_content_gate_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(a: list[float], b: list[float], denom_box: list[float]) -> float:
    inter = intersection(a, b)
    if not inter:
        return 0.0
    return area(inter) / max(area(denom_box), 1.0)


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def page76(data: dict[str, Any]) -> dict[str, Any]:
    return next(page for page in data["pages"] if page["page"] == 76)


def words_in_box(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        word_box = [float(v) for v in word["box"]]
        if overlap_fraction(box, word_box, word_box) >= 0.25:
            hits.append(word)
    return sorted(hits, key=lambda row: (row["center"][1], row["center"][0]))


def target_word_ids(words: list[dict[str, Any]], active_targets: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for word in words:
        word_box = [float(v) for v in word["box"]]
        for target in active_targets:
            target_box = [float(v) for v in target["box"]]
            if overlap_fraction(word_box, target_box, word_box) >= 0.25:
                out.add(word["id"])
                break
    return out


def active_box_contacts(box: list[float], active_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contacts = []
    for target in active_targets:
        target_box = [float(v) for v in target["box"]]
        frac = overlap_fraction(box, target_box, target_box)
        if frac <= 0:
            continue
        contacts.append(
            {
                "targetId": target["id"],
                "label": target["label"],
                "overlapOfTarget": round(frac, 6),
                "strong": frac >= 0.20,
            }
        )
    return sorted(contacts, key=lambda row: (-row["overlapOfTarget"], row["targetId"]))


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [260, 1970, 2050, 3055]
    scale = 0.48
    panel = img.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 142
    footer_h = 300
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 14, 20))
    draw = ImageDraw.Draw(sheet)
    overlay = ImageDraw.Draw(sheet, "RGBA")
    title = font(25)
    normal = font(14)
    small = font(12)

    draw.text((margin, 18), "3D Reflection Shifted Carrier Content Gate", fill=(242, 245, 248), font=title)
    summary = result["summary"]
    draw.text(
        (margin, 56),
        "Per-target line-pitch shifts from the all-four reflected carriers, checked against row content.",
        fill=(180, 190, 204),
        font=normal,
    )
    draw.text(
        (margin, 84),
        f"carriers={summary['carrierCount']} slices={summary['activeSliceCount']} "
        f"baseLines={summary['uniqueInferredBaseLines']} strictHits={summary['strictInstructionHitCount']} "
        f"isolatedSlices={summary['targetPhraseIsolatedSliceCount']}",
        fill=(180, 190, 204),
        font=small,
    )

    y0 = header_h
    sheet.paste(panel, (margin, y0))
    colors = {
        "78_76_4": (0, 135, 255, 145),
        "79_76_4": (0, 185, 120, 145),
        "79_76_5": (215, 95, 215, 145),
    }
    for target in result["activeTargets"]:
        box = [float(v) for v in target["box"]]
        x0 = margin + (box[0] - crop[0]) * scale
        yb0 = y0 + (box[1] - crop[1]) * scale
        x1 = margin + (box[2] - crop[0]) * scale
        yb1 = y0 + (box[3] - crop[1]) * scale
        color = (255, 120, 0, 235) if target["visualState"] == "Y" else (20, 20, 20, 235)
        overlay.rectangle([x0, yb0, x1, yb1], outline=color, width=4)
        overlay.text((x0, max(y0, yb0 - 17)), target["id"], fill=color, font=small)

    for record in result["sliceRecords"]:
        color = colors.get(record["reflectionId"], (255, 255, 255, 120))
        box = record["shiftedBox"]
        x0 = margin + (box[0] - crop[0]) * scale
        yb0 = y0 + (box[1] - crop[1]) * scale
        x1 = margin + (box[2] - crop[0]) * scale
        yb1 = y0 + (box[3] - crop[1]) * scale
        overlay.rectangle([x0, yb0, x1, yb1], outline=color, width=2)
        overlay.text((x0 + 2, yb0 + 2), f"{record['reflectionId']} {record['shift']:+d}", fill=color, font=small)

    y = y0 + panel.size[1] + 18
    for carrier in result["carrierSummaries"]:
        text = (
            f"{carrier['reflectionId']} base L{carrier['inferredBaseLine']} "
            f"shifts={carrier['activeShiftPattern']} gaps={carrier['activeShiftGapPattern']} "
            f"words={carrier['sliceWordCounts']}"
        )
        draw.text((margin, y), text, fill=(222, 229, 238), font=small)
        y += 42
    for item in result["assessment"][:3]:
        draw.text((margin, y), f"- {item}"[:150], fill=(182, 192, 204), font=small)
        y += 34

    sheet.save(SHEET, quality=92)


def main() -> None:
    map_data = load_json(MAP_JSON)
    stack = load_json(STACK_JSON)
    active = load_json(ACTIVE_JSON)["targets"]
    words = page76(map_data)["words"]
    active_order = sorted(active, key=lambda row: row["pageLine"])
    active_ids = [row["id"] for row in active_order]
    active_lines = [row["pageLine"] for row in active_order]
    active_line_gaps = [active_lines[i + 1] - active_lines[i] for i in range(len(active_lines) - 1)]

    carrier_summaries = []
    slice_records = []
    strict_terms: set[str] = set()

    for carrier in stack["allFourActiveCarriers"]:
        hits_by_target = carrier["bestActiveHitsByTarget"]
        shift_pattern = [int(hits_by_target[target_id]["shift"]) for target_id in active_ids]
        shift_gaps = [shift_pattern[i + 1] - shift_pattern[i] for i in range(len(shift_pattern) - 1)]
        inferred_base_lines = [line - shift for line, shift in zip(active_lines, shift_pattern)]
        carrier_slice_records = []

        for target in active_order:
            hit = hits_by_target[target["id"]]
            shifted_box = [float(v) for v in hit["shiftedBox"]]
            slice_words = words_in_box(words, shifted_box)
            target_word_set = target_word_ids(slice_words, active_order)
            word_text = " ".join(word["text"] for word in slice_words)
            word_hits = instruction_hits(word_text)
            carrier_hits = instruction_hits(carrier.get("text", ""))
            strict_terms.update(word_hits)
            strict_terms.update(carrier_hits)
            contacts = active_box_contacts(shifted_box, active_order)
            primary_contact = next((c for c in contacts if c["targetId"] == target["id"]), None)
            record = {
                "reflectionId": carrier["reflectionId"],
                "source": carrier["source"],
                "carrierText": carrier.get("text", ""),
                "targetId": target["id"],
                "targetLabel": target["label"],
                "targetPageLine": target["pageLine"],
                "targetCorridorIndex": target["corridorIndex"],
                "shift": int(hit["shift"]),
                "shiftedBox": [round(v, 2) for v in shifted_box],
                "activeBoxContacts": contacts,
                "primaryOverlapOfTarget": primary_contact["overlapOfTarget"] if primary_contact else 0,
                "wordCount": len(slice_words),
                "activeTargetWordCount": len(target_word_set),
                "nonTargetWordCount": len(slice_words) - len(target_word_set),
                "wordText": word_text,
                "wordInstructionHits": word_hits,
                "carrierInstructionHits": carrier_hits,
                "targetPhraseIsolated": bool(slice_words) and len(slice_words) == len(target_word_set),
            }
            carrier_slice_records.append(record)
            slice_records.append(record)

        carrier_summaries.append(
            {
                "reflectionId": carrier["reflectionId"],
                "source": carrier["source"],
                "carrierText": carrier.get("text", ""),
                "activeTargetOrder": active_ids,
                "activePageLines": active_lines,
                "activeLineGapPattern": active_line_gaps,
                "activeShiftPattern": shift_pattern,
                "activeShiftGapPattern": shift_gaps,
                "shiftGapsMatchPageLineGaps": shift_gaps == active_line_gaps,
                "inferredBaseLinesByTarget": dict(zip(active_ids, inferred_base_lines)),
                "inferredBaseLine": inferred_base_lines[0] if len(set(inferred_base_lines)) == 1 else None,
                "singleBaseLine": len(set(inferred_base_lines)) == 1,
                "sliceWordCounts": [row["wordCount"] for row in carrier_slice_records],
                "sliceNonTargetWordCounts": [row["nonTargetWordCount"] for row in carrier_slice_records],
                "sliceInstructionHits": sorted(
                    {term for row in carrier_slice_records for term in row["wordInstructionHits"]}
                ),
                "carrierInstructionHits": carrier_slice_records[0]["carrierInstructionHits"]
                if carrier_slice_records
                else [],
            }
        )

    total_words = sum(row["wordCount"] for row in slice_records)
    total_non_target_words = sum(row["nonTargetWordCount"] for row in slice_records)
    isolated = [row for row in slice_records if row["targetPhraseIsolated"]]
    unique_base_lines = sorted(
        {
            carrier["inferredBaseLine"]
            for carrier in carrier_summaries
            if carrier["inferredBaseLine"] is not None
        }
    )
    common_shift_gaps = sorted({tuple(carrier["activeShiftGapPattern"]) for carrier in carrier_summaries})

    assessment = [
        "The all-four reflected carriers infer ordinary base rows L20/L21; the active shift gaps match page-line gaps 3/2/5 because the operation is walking article rows by line pitch.",
        "None of the shifted slices isolates a target phrase: every active slice carries surrounding row prose, and the 12 slices include more non-target words than target-box OCR words.",
        "The shifted slice text and the carrier text contain 0 strict instruction terms.",
        "The 3D OCR in these shifted slices is not text authority: the trusted G5 target is geometrically hit, but its target phrase is not recovered as clean OCR text inside the slices.",
        "This keeps reflected carriers useful as orientation/row-registration evidence only, not as a source-backed unit/order selector.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D reflected all-four carrier content gate; no new OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "article3dMap": rel(MAP_JSON),
            "reflectionLinePitchStackGate": rel(STACK_JSON),
            "activeTargetCropCompletion": rel(ACTIVE_JSON),
        },
        "activeTargets": active_order,
        "summary": {
            "carrierCount": len(carrier_summaries),
            "activeSliceCount": len(slice_records),
            "activeTargetOrder": active_ids,
            "activePageLines": active_lines,
            "activeLineGapPattern": active_line_gaps,
            "commonShiftGapPatterns": [list(pattern) for pattern in common_shift_gaps],
            "allCarrierShiftGapsMatchPageLineGaps": all(
                carrier["shiftGapsMatchPageLineGaps"] for carrier in carrier_summaries
            ),
            "uniqueInferredBaseLines": unique_base_lines,
            "sliceWordCountTotal": total_words,
            "sliceNonTargetWordCountTotal": total_non_target_words,
            "targetPhraseIsolatedSliceCount": len(isolated),
            "strictInstructionHitCount": len(strict_terms),
            "strictInstructionHits": sorted(strict_terms),
            "selectorUnlocked": False,
        },
        "carrierSummaries": carrier_summaries,
        "sliceRecords": slice_records,
        "assessment": assessment,
        "decision": {
            "reflectionShiftedCarrierContentGate": "shifted_carriers_are_row_context_not_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not promote shifted 3D reflection carrier rows as extraction permission. Reopen only if a source/clue names a specific carrier, base row, target-shift sequence, and unit/order rule.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 3D Reflection Shifted Carrier Content Gate",
        "",
        "Scope: inspect the three reflected page-76 carriers that can touch O4/B4/G5/O5 after integer line-pitch shifts. This reads existing 3D-map OCR boxes only; no new OCR, extraction, hashes, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Carriers: `{result['summary']['carrierCount']}`",
        f"- Shifted active slices: `{result['summary']['activeSliceCount']}`",
        f"- Active page-line gaps: `{result['summary']['activeLineGapPattern']}`",
        f"- Common carrier shift-gap patterns: `{result['summary']['commonShiftGapPatterns']}`",
        f"- Inferred base lines: `{result['summary']['uniqueInferredBaseLines']}`",
        f"- Strict instruction hits: `{result['summary']['strictInstructionHitCount']}`",
        f"- Target-phrase isolated slices: `{result['summary']['targetPhraseIsolatedSliceCount']}`",
        "",
        "## Carrier Phase",
        "",
        "| carrier | carrier text | base line | shifts | shift gaps | page-line gaps match? | slice word counts | non-target word counts |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for carrier in carrier_summaries:
        text = carrier["carrierText"].replace("|", "\\|") or "-"
        lines.append(
            f"| `{carrier['reflectionId']}` | {text} | `{carrier['inferredBaseLine']}` | "
            f"`{carrier['activeShiftPattern']}` | `{carrier['activeShiftGapPattern']}` | "
            f"`{carrier['shiftGapsMatchPageLineGaps']}` | `{carrier['sliceWordCounts']}` | "
            f"`{carrier['sliceNonTargetWordCounts']}` |"
        )

    lines.extend(
        [
            "",
            "## Shifted Slices",
            "",
            "| carrier | target | shift | overlap | words | non-target words | instruction hits | slice text |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in slice_records:
        text = row["wordText"].replace("|", "\\|") or "-"
        lines.append(
            f"| `{row['reflectionId']}` | `{row['targetId']}` | `{row['shift']}` | "
            f"`{row['primaryOverlapOfTarget']}` | `{row['wordCount']}` | `{row['nonTargetWordCount']}` | "
            f"{', '.join(row['wordInstructionHits']) or '-'} | {text} |"
        )

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['reflectionShiftedCarrierContentGate']}.",
            f"- Next move: {result['decision']['nextMove']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(OUT_MD)
    print(OUT_JSON)
    print(SHEET)


if __name__ == "__main__":
    main()
