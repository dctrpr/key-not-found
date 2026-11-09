#!/usr/bin/env python3
"""Build a complete O4/B4/G5/O5 page-76 target crop sheet.

This closes a documentation gap in the visual source packet: the previous
priority crop pack had manual/crop coverage for 3 of the 4 active targets, with
O4 covered by consistency evidence only. This pass creates one complete visual
reference sheet. It does not run extraction, hashing, key derivation, WIF/Base58
scans, OCR, or address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_active_target_crop_completion.json"
OUT_MD = OUT / "page76_active_target_crop_completion.md"
SHEET = OUT / "page76_active_target_crop_completion_sheet.jpg"

PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
INPUTS = {
    "active_line": ROOT
    / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json",
    "format_lock": ROOT
    / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
    "priority_crop_pack": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "orange_highres_audit": ROOT / "analysis_outputs/highlight_audit/highres_highlight_audit.json",
    "grey_reading": ROOT / "analysis_outputs/highlight_audit/highres_manual_grey_reading.json",
}

TARGETS = [
    {
        "id": "buying_dip",
        "label": "O4 buying the dip",
        "phrase": "buying the dip",
        "source": "highres_highlight_audit.visualOrangeRows.p76_orange_4",
        "box": [1334, 2177, 1801, 2225],
        "crop": [1120, 2125, 1910, 2265],
        "color": "#ff9b2e",
        "note": "Completes the prior crop-pack gap for O4.",
    },
    {
        "id": "one_billion",
        "label": "B4 $1 billion",
        "phrase": "$1 billion",
        "source": "full-page visual inspection; old projected grey box was known wrong",
        "box": [428, 2398, 691, 2445],
        "crop": [250, 2350, 1520, 2460],
        "color": "#8f98a5",
        "note": "Uses direct full-page visual boxing because old p76_grey_4 projection landed on unrelated text.",
    },
    {
        "id": "volcano_bonds",
        "label": "G5 Volcano Bonds",
        "phrase": "Volcano Bonds",
        "source": "page76_priority_crop_pack.L27_G5_pair",
        "box": [795, 2544, 1196, 2592],
        "crop": [720, 2505, 1650, 2625],
        "color": "#8f98a5",
        "note": "Uses newer priority crop/manual box rather than old projected grey coordinates.",
    },
    {
        "id": "shitcoiner_heart",
        "label": "O5 shitcoiner at heart",
        "phrase": "shitcoiner at heart",
        "source": "highres_highlight_audit.visualOrangeRows.p76_orange_5 + page76_priority_crop_pack.L32_O5_primary",
        "box": [1040, 2932, 1661, 2982],
        "crop": [850, 2860, 1770, 3038],
        "color": "#ff9b2e",
        "note": "Primary lower-corridor target already covered by priority crop pack.",
    },
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


def draw_labeled_crop(page: Image.Image, target: dict[str, Any]) -> tuple[Image.Image, Path]:
    crop_box = tuple(int(v) for v in target["crop"])
    target_box = [int(v) for v in target["box"]]
    crop = page.crop(crop_box).convert("RGB")
    draw = ImageDraw.Draw(crop)
    x0, y0, x1, y1 = crop_box
    local = [target_box[0] - x0, target_box[1] - y0, target_box[2] - x0, target_box[3] - y0]
    outline = target["color"]
    for offset in range(3):
        draw.rectangle(
            (local[0] - offset, local[1] - offset, local[2] + offset, local[3] + offset),
            outline=outline,
        )
    label_font = font(18)
    label = target["label"]
    label_w = int(draw.textlength(label, font=label_font)) + 12
    label_h = 26
    lx = max(0, min(local[0], crop.width - label_w))
    ly = max(0, local[1] - label_h - 4)
    draw.rectangle((lx, ly, lx + label_w, ly + label_h), fill=(20, 24, 30))
    draw.text((lx + 6, ly + 4), label, fill=(245, 248, 250), font=label_font)

    out_path = OUT / f"{target['id']}_crop.jpg"
    crop.save(out_path, quality=95)
    return crop, out_path


def paste_fit(sheet: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    max_w, max_h = x1 - x0, y1 - y0
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resample = getattr(Image, "Resampling", Image).LANCZOS
    resized = image.resize(new_size, resample)
    sheet.paste(resized, (x0 + (max_w - new_size[0]) // 2, y0 + (max_h - new_size[1]) // 2))


def build_sheet(records: list[dict[str, Any]]) -> None:
    sheet_w, sheet_h = 1680, 1320
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Page-76 Active Target Crop Completion", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 45),
        "Complete O4/B4/G5/O5 crop authority sheet for future source comparison. No extraction performed.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("targets", len(records)),
        ("crop coverage", "4/4"),
        ("pattern", "OBBO / YKKY"),
        ("source layer", "page_76_upright"),
        ("selector", "blocked"),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 255, y + 48), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 24), str(value), fill=(232, 239, 246), font=mono)
        x += 275

    y += 76
    cell_w = (sheet_w - margin * 2 - 24) // 2
    cell_h = 430
    for idx, record in enumerate(records):
        col = idx % 2
        row = idx // 2
        x0 = margin + col * (cell_w + 24)
        y0 = y + row * (cell_h + 24)
        draw.rectangle((x0, y0, x0 + cell_w, y0 + cell_h), fill=(18, 22, 28), outline=(50, 58, 70))
        draw.text((x0 + 14, y0 + 12), record["label"], fill=(242, 247, 250), font=normal)
        draw.text((x0 + 14, y0 + 38), f"box {record['box']} | crop {record['crop']}", fill=(176, 186, 198), font=small)
        crop_img = Image.open(ROOT / record["output"]).convert("RGB")
        paste_fit(sheet, crop_img, (x0 + 14, y0 + 68, x0 + cell_w - 14, y0 + 338))
        draw.text((x0 + 14, y0 + 354), record["source"][:92], fill=(176, 186, 198), font=small)
        draw.text((x0 + 14, y0 + 380), record["note"][:100], fill=(176, 186, 198), font=small)

    y = sheet_h - 105
    draw.rectangle((margin, y, sheet_w - margin, y + 75), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text(
        (margin + 14, y + 14),
        "Decision: the active target crop artifact is now complete for source comparison, but it still supplies no R3 unit/order.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 42),
        "Use this as visual authority only; do not treat the crop boxes as extraction permission.",
        fill=(255, 219, 137),
        font=normal,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    page = Image.open(PAGE).convert("RGB")
    active_line = load_json(INPUTS["active_line"])
    format_lock = load_json(INPUTS["format_lock"])
    priority_crop_pack = load_json(INPUTS["priority_crop_pack"])
    grey_reading = load_json(INPUTS["grey_reading"])

    active_records = {row["id"]: row for row in active_line.get("records", [])}
    records: list[dict[str, Any]] = []
    for target in TARGETS:
        _, out_path = draw_labeled_crop(page, target)
        active = active_records.get(target["id"], {})
        records.append(
            {
                **target,
                "output": rel(out_path),
                "pageLine": active.get("pageLine"),
                "corridorIndex": active.get("corridorIndex"),
                "visualState": active.get("visualState"),
                "docmDominantFont": active.get("docmDominantFont"),
                "docmBoldFraction": active.get("docmBoldFraction"),
                "docmHighlights": active.get("docmHighlights"),
            }
        )

    summary = {
        "targetCount": len(records),
        "cropCoverage": "4/4",
        "activeColorPattern": format_lock.get("summary", {}).get("activeColorPattern", "OBBO"),
        "activeVisualStateOrder": format_lock.get("summary", {}).get("activeVisualStateOrder", "YKKY"),
        "pageLines": " ".join(str(row.get("pageLine")) for row in records),
        "corridorIndexes": " ".join(str(row.get("corridorIndex")) for row in records),
        "previousFormatLockCropCoverage": format_lock.get("summary", {}).get("cropPackActiveCoverageCount"),
        "oldGreyProjectionCaveats": grey_reading.get("caveats", []),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "complete O4/B4/G5/O5 page-76 target crop authority sheet; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "sourceImage": rel(PAGE),
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "targets": records,
        "priorityCropContext": {
            "previousSheet": priority_crop_pack.get("sheet"),
            "previousCrops": [row.get("id") for row in priority_crop_pack.get("crops", [])],
        },
        "sheet": rel(SHEET),
        "decision": "page76_active_target_crop_authority_complete_no_selector",
        "nextMove": "Use this completed O4/B4/G5/O5 sheet for future physical/original-layout/source comparison. Do not reopen current-scan extraction without R3 unit/order evidence.",
    }

    build_sheet(records)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Active Target Crop Completion",
        "",
        "Scope: build a complete visual reference for O4/B4/G5/O5 on the high-res upright page-76 image. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Crop coverage: `{summary['cropCoverage']}`",
        f"- Active color pattern: `{summary['activeColorPattern']}`",
        f"- Active visual-state order: `{summary['activeVisualStateOrder']}`",
        f"- Page lines: `{summary['pageLines']}`",
        f"- Corridor indexes: `{summary['corridorIndexes']}`",
        f"- Selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Targets",
        "",
        "| target | line/corridor | visual | box | crop | source | output |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in records:
        lines.append(
            f"| `{row['label']}` | `L{row['pageLine']}/C{row['corridorIndex']}` | `{row['visualState']}` | `{row['box']}` | `{row['crop']}` | {row['source']} | `{row['output']}` |"
        )
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            "- The older grey projection boxes for p76 `$1 billion` and `Volcano Bonds` are not used as geometry authority here because the grey-reading audit already flags them as landing on wrong lower-page text.",
            "- This sheet completes crop documentation only; it does not add unit/order evidence.",
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
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
