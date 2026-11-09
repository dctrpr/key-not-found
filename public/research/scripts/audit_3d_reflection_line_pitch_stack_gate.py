#!/usr/bin/env python3
"""Line-pitch stack gate for 3D reflected boxes on page 76.

The direct 3D reflection boxes only graze O4 and miss G5/O5. This bounded pass
asks whether shifting those already-registered reflected boxes by integer
page-76 line pitches creates a source-backed selector for O4/B4/G5/O5, or only
a broad lower-page sweep.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REFLECTION_JSON = ROOT / "analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap.json"
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ALL_HIGHLIGHTS_JSON = (
    ROOT / "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
PITCH_JSON = ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "reflection_line_pitch_stack_gate.json"
OUT_MD = OUT / "reflection_line_pitch_stack_gate.md"
SHEET = OUT / "reflection_line_pitch_stack_gate_sheet.jpg"

SHIFT_RANGE = range(-14, 15)
STRONG_OVERLAP_OF_TARGET = 0.20
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


def shift_box(box: list[float], line_pitch: float, shift: int) -> list[float]:
    dy = line_pitch * shift
    return [float(box[0]), float(box[1]) + dy, float(box[2]), float(box[3]) + dy]


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def hit_rows_for_targets(
    shifted_box: list[float],
    targets: list[dict[str, Any]],
    prefix: str,
) -> list[dict[str, Any]]:
    hits = []
    for target in targets:
        target_box = [float(v) for v in target["box"]]
        inter = intersection(shifted_box, target_box)
        if not inter:
            continue
        overlap = area(inter)
        overlap_of_target = overlap / max(area(target_box), 1.0)
        overlap_of_reflection = overlap / max(area(shifted_box), 1.0)
        hits.append(
            {
                "targetId": f"{prefix}:{target['id']}",
                "rawTargetId": target["id"],
                "label": target.get("label") or target.get("phrase"),
                "kind": target.get("kind") or target.get("visualState") or target.get("color"),
                "overlapPx2": round(overlap, 2),
                "overlapOfTarget": round(overlap_of_target, 6),
                "overlapOfReflection": round(overlap_of_reflection, 6),
                "strong": overlap_of_target >= STRONG_OVERLAP_OF_TARGET,
            }
        )
    hits.sort(key=lambda row: (-row["overlapOfTarget"], row["targetId"]))
    return hits


def best_by_target(rows: list[dict[str, Any]], target_prefix: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        for hit in row[f"{target_prefix}Hits"]:
            if not hit["strong"]:
                continue
            existing = out.get(hit["rawTargetId"])
            candidate = {
                **hit,
                "shift": row["shift"],
                "reflectionId": row["reflectionId"],
                "source": row["source"],
                "text": row["text"],
            }
            if not existing or candidate["overlapOfTarget"] > existing["overlapOfTarget"]:
                out[hit["rawTargetId"]] = candidate
    return out


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [260, 2100, 2050, 3055]
    scale = 0.52
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 145
    footer_h = 260
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(15)
    small = font(12)

    draw.text((margin, 20), "3D Reflection Line-Pitch Stack Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 56),
        "Integer line-pitch shifts of reflected boxes against O4/B4/G5/O5 and all page-76 highlight controls.",
        fill=(178, 188, 200),
        font=normal,
    )
    summary = result["summary"]
    draw.text(
        (margin, 86),
        f"linePitch={summary['linePitchPx']} shifts={summary['shiftRange']} all-four carriers={summary['allFourActiveCarrierCount']} "
        f"single-shift all-four={summary['singleShiftAllFourCount']} strictHits={summary['strictInstructionHitCount']}",
        fill=(178, 188, 200),
        font=small,
    )

    y0 = header_h
    sheet.paste(panel, (margin, y0))
    overlay = ImageDraw.Draw(sheet, "RGBA")
    for target in result["activeTargets"]:
        box = [float(v) for v in target["box"]]
        x0 = margin + (box[0] - crop[0]) * scale
        yb0 = y0 + (box[1] - crop[1]) * scale
        x1 = margin + (box[2] - crop[0]) * scale
        yb1 = y0 + (box[3] - crop[1]) * scale
        color = (255, 120, 0, 230) if target["visualState"] == "Y" else (20, 20, 20, 235)
        overlay.rectangle([x0, yb0, x1, yb1], outline=color, width=4)
        overlay.text((x0, max(y0, yb0 - 18)), target["id"], fill=color, font=small)

    palette = [(0, 130, 255, 120), (0, 180, 130, 120), (210, 80, 210, 120)]
    for i, carrier in enumerate(result["allFourActiveCarriers"][:3]):
        color = palette[i % len(palette)]
        for target_id, hit in carrier["bestActiveHitsByTarget"].items():
            shifted = hit["shiftedBox"]
            x0 = margin + (shifted[0] - crop[0]) * scale
            yb0 = y0 + (shifted[1] - crop[1]) * scale
            x1 = margin + (shifted[2] - crop[0]) * scale
            yb1 = y0 + (shifted[3] - crop[1]) * scale
            overlay.rectangle([x0, yb0, x1, yb1], outline=color, width=2)
            overlay.text((x0, yb0 + 3), f"{carrier['reflectionId']} {hit['shift']:+d}", fill=color, font=small)

    y = y0 + panel.size[1] + 22
    for carrier in result["allFourActiveCarriers"][:3]:
        text = (
            f"{carrier['reflectionId']} {carrier['source']} text={carrier['text'][:45]!r}; "
            f"active={carrier['activeCoverageIds']} controls={carrier['allHighlightCoverageIds']}"
        )
        draw.text((margin, y), text[:150], fill=(218, 226, 235), font=small)
        y += 68

    sheet.save(SHEET, quality=92)


def main() -> None:
    reflections = load_json(REFLECTION_JSON)["reflections"]
    active_targets = load_json(ACTIVE_JSON)["targets"]
    all_targets = load_json(ALL_HIGHLIGHTS_JSON)["targets"]
    pitch_data = load_json(PITCH_JSON)
    line_pitch = float(pitch_data["gapVsLinePitch"]["medianLinePitchPx"])

    reflection_records = []
    single_shift_coverage: dict[int, set[str]] = {shift: set() for shift in SHIFT_RANGE}
    strict_terms: set[str] = set()

    for reflection in reflections:
        rows = []
        for shift in SHIFT_RANGE:
            shifted = shift_box(reflection["targetBox"], line_pitch, shift)
            active_hits = hit_rows_for_targets(shifted, active_targets, "active")
            all_hits = hit_rows_for_targets(shifted, all_targets, "all")
            for hit in active_hits:
                if hit["strong"]:
                    single_shift_coverage[shift].add(hit["rawTargetId"])
            rows.append(
                {
                    "reflectionId": reflection["id"],
                    "source": f"{reflection['source']}->{reflection['target']}",
                    "shift": shift,
                    "shiftDyPx": round(shift * line_pitch, 2),
                    "shiftedBox": [round(v, 2) for v in shifted],
                    "text": reflection.get("text", ""),
                    "activeHits": active_hits,
                    "allHits": all_hits,
                }
            )
        best_active = best_by_target(rows, "active")
        best_all = best_by_target(rows, "all")
        hits = instruction_hits(reflection.get("text", ""))
        strict_terms.update(hits)
        reflection_records.append(
            {
                "reflectionId": reflection["id"],
                "source": f"{reflection['source']}->{reflection['target']}",
                "text": reflection.get("text", ""),
                "instructionHits": hits,
                "activeCoverageIds": sorted(best_active),
                "activeCoverageCount": len(best_active),
                "allHighlightCoverageIds": sorted(best_all),
                "allHighlightCoverageCount": len(best_all),
                "bestActiveHitsByTarget": {
                    target_id: {
                        **hit,
                        "shiftedBox": next(
                            row["shiftedBox"]
                            for row in rows
                            if row["reflectionId"] == hit["reflectionId"] and row["shift"] == hit["shift"]
                        ),
                    }
                    for target_id, hit in best_active.items()
                },
                "bestAllHitsByTarget": best_all,
                "rows": rows,
            }
        )

    all_four = [row for row in reflection_records if row["activeCoverageCount"] == len(active_targets)]
    all_four.sort(key=lambda row: (-row["allHighlightCoverageCount"], row["reflectionId"]))
    single_shift_all_four = [
        {"shift": shift, "activeCoverageIds": sorted(ids)}
        for shift, ids in sorted(single_shift_coverage.items())
        if len(ids) == len(active_targets)
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D reflection line-pitch stack gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "reflectionBoxTargetOverlap": rel(REFLECTION_JSON),
            "activeTargetCropCompletion": rel(ACTIVE_JSON),
            "allSourceHighlightMirrorBenchmark": rel(ALL_HIGHLIGHTS_JSON),
            "p77OneLineNearMissPitch": rel(PITCH_JSON),
        },
        "activeTargets": active_targets,
        "summary": {
            "linePitchPx": line_pitch,
            "shiftRange": [min(SHIFT_RANGE), max(SHIFT_RANGE)],
            "reflectionCount": len(reflection_records),
            "allFourActiveCarrierCount": len(all_four),
            "allFourActiveCarrierIds": [row["reflectionId"] for row in all_four],
            "singleShiftAllFourCount": len(single_shift_all_four),
            "singleShiftAllFour": single_shift_all_four,
            "strictInstructionHitCount": len(strict_terms),
            "strictInstructionHits": sorted(strict_terms),
            "strongOverlapOfTargetThreshold": STRONG_OVERLAP_OF_TARGET,
            "selectorUnlocked": False,
        },
        "allFourActiveCarriers": all_four,
        "reflectionRecords": reflection_records,
        "assessment": [
            "Integer line-pitch walking can make three contextual p78/p79 reflection boxes touch all four active targets, but only at different target-specific shifts.",
            "No single global line-pitch shift covers O4/B4/G5/O5 together.",
            "The all-four carriers also sweep broad page-76 highlight controls, especially O3/O4/O5 and G3/G4/G5, so the operation is not active-specific.",
            "The carrier texts are contextual El Salvador/IMF/Bitcoin prose and contain no strict unit/order instruction terms.",
        ],
        "decision": {
            "reflectionLinePitchStackGate": "line_pitch_stack_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not promote line-pitch walking of 3D reflected boxes as a selector. Reopen only if a source/clue names a specific reflection id plus target-specific line offsets or a global line-shift rule.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 3D Reflection Line-Pitch Stack Gate",
        "",
        "Scope: shift the already-registered page-76 reflected boxes by integer page-76 line pitches and compare contacts with active O4/B4/G5/O5 plus all page-76 highlighted controls. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        "",
        "## Summary",
        "",
        f"- Line pitch: `{line_pitch}` px.",
        f"- Reflections tested: `{len(reflection_records)}`.",
        f"- Integer shifts tested: `{min(SHIFT_RANGE)}` through `{max(SHIFT_RANGE)}`.",
        f"- Strong overlap threshold: `{STRONG_OVERLAP_OF_TARGET}` of target area.",
        f"- All-four active carriers: `{len(all_four)}`.",
        f"- Single global shifts covering all four active targets: `{len(single_shift_all_four)}`.",
        f"- Strict instruction hits in carrier text: `{len(strict_terms)}`.",
        "",
        "## All-Four Active Carriers",
        "",
    ]
    if not all_four:
        lines.append("- None.")
    for carrier in all_four:
        active_bits = []
        for target_id, hit in carrier["bestActiveHitsByTarget"].items():
            active_bits.append(f"{target_id}@{hit['shift']:+d}({hit['overlapOfTarget']:.3f})")
        lines.append(
            f"- `{carrier['reflectionId']}` `{carrier['source']}` text `{carrier['text']}`: active `{', '.join(active_bits)}`; all-highlight controls `{', '.join(carrier['allHighlightCoverageIds'])}`; instruction hits `{carrier['instructionHits']}`"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote line-pitch walking of 3D reflected boxes as a selector.",
            "- The operation can recover O4/B4/G5/O5 only by using different shifts per target; no single global shift covers the quartet.",
            "- The same carriers also sweep broad page-76 highlighted controls, so the hits are not active-specific.",
            "- Reopen only if a new source/clue names a specific reflection id plus target-specific line offsets or a global line-shift rule.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print(f"allFourActiveCarrierCount: {len(all_four)}")
    print(f"singleShiftAllFourCount: {len(single_shift_all_four)}")
    print(f"strictInstructionHitCount: {len(strict_terms)}")


if __name__ == "__main__":
    main()
