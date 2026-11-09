#!/usr/bin/env python3
"""Audit order/orientation ambiguity for the active page-76 target quartet.

The active O4/B4/G5/O5 colors and visual states are palindromic (`OBBO` and
`YKKY`). That means a 180-degree orientation mistake can preserve the
highlight/color signature while reversing the actual line/corridor order. This
guardrail records which order is authoritative for future source comparisons.
It does not run extraction, hashing, key derivation, WIF/Base58 scans, OCR, or
address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_active_order_orientation_trap.json"
OUT_MD = OUT / "page76_active_order_orientation_trap.md"
SHEET = OUT / "page76_active_order_orientation_trap_sheet.jpg"

INPUTS = {
    "crop_completion": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
    "orientation_guardrail": ROOT / "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail.json",
    "format_authority": ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
    "line_corridor": ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json",
}


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


def color_code(row: dict[str, Any]) -> str:
    return "O" if str(row.get("color", "")).lower() == "#ff9b2e" else "B"


def box_center_y(box: list[int | float]) -> float:
    return (float(box[1]) + float(box[3])) / 2.0


def box_center_x(box: list[int | float]) -> float:
    return (float(box[0]) + float(box[2])) / 2.0


def signature(rows: list[dict[str, Any]], box_key: str) -> dict[str, Any]:
    return {
        "labels": [row["label"] for row in rows],
        "codes": [row["label"].split(" ", 1)[0] for row in rows],
        "ids": [row["id"] for row in rows],
        "colorPattern": "".join(color_code(row) for row in rows),
        "visualStatePattern": "".join(str(row.get("visualState", "")) for row in rows),
        "pageLines": " ".join(str(row.get("pageLine")) for row in rows),
        "corridorIndexes": " ".join(str(row.get("corridorIndex")) for row in rows),
        "centerY": [round(box_center_y(row[box_key]), 2) for row in rows],
        "centerX": [round(box_center_x(row[box_key]), 2) for row in rows],
    }


def is_palindrome(text: str) -> bool:
    return text == text[::-1]


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1640, 1180
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(18)
    small = font(14)
    mono = font(15)

    draw.text((margin, margin), "Page-76 Active Order Orientation Trap", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 46),
        "OBBO / YKKY survives a 180-degree flip, so line and corridor order must be the orientation check.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("color palindrome", result["summary"]["colorPatternIsPalindrome"]),
        ("visual palindrome", result["summary"]["visualStatePatternIsPalindrome"]),
        ("line order trap", result["summary"]["lineOrderDetectsFlip"]),
        ("corridor order trap", result["summary"]["corridorOrderDetectsFlip"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 370, y + 56), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 30), str(value), fill=(232, 239, 246), font=mono)
        x += 390

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 112), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Guardrail", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 47),
        "Do not use color/visual-state order alone to validate source orientation: both patterns are palindromes.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 77),
        "Authoritative readable order is O4 -> B4 -> G5 -> O5 with page lines 22 -> 25 -> 27 -> 32.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 145
    col_w = (sheet_w - margin * 2 - 30) // 2
    panels = [
        ("Readable/upright top-to-bottom order", result["orders"]["uprightTopToBottom"]),
        ("Native unnormalized top-to-bottom order", result["orders"]["nativeUnnormalizedTopToBottom"]),
    ]
    for idx, (title, order) in enumerate(panels):
        x0 = margin + idx * (col_w + 30)
        draw.rectangle((x0, y, x0 + col_w, y + 470), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((x0 + 14, y + 14), title, fill=(238, 243, 248), font=normal)
        rows = [
            ("sequence", " -> ".join(order["codes"])),
            ("colors", order["colorPattern"]),
            ("visual", order["visualStatePattern"]),
            ("lines", order["pageLines"]),
            ("corridors", order["corridorIndexes"]),
            ("center y", ", ".join(str(v) for v in order["centerY"])),
        ]
        ty = y + 56
        for label, value in rows:
            draw.text((x0 + 18, ty), label, fill=(129, 143, 158), font=small)
            draw.text((x0 + 150, ty), value[:62], fill=(232, 239, 246), font=mono)
            ty += 42

    y += 505
    draw.rectangle((margin, y, sheet_w - margin, y + 215), fill=(18, 22, 28), outline=(48, 58, 70))
    draw.text((margin + 14, y + 14), "Decision", fill=(238, 243, 248), font=normal)
    decision_lines = [
        result["decision"],
        "Color/visual state can confirm the quartet but cannot establish orientation.",
        "Use page-line and corridor order, plus the 180-degree transform guardrail, before comparing any new source.",
        "No selector or key material was generated.",
    ]
    ty = y + 54
    for line in decision_lines:
        draw.text((margin + 18, ty), f"- {line}", fill=(176, 186, 198), font=small)
        ty += 36

    sheet.save(SHEET, quality=94)


def main() -> None:
    crop_completion = load_json(INPUTS["crop_completion"])
    orientation = load_json(INPUTS["orientation_guardrail"])
    format_authority = load_json(INPUTS["format_authority"])
    line_corridor = load_json(INPUTS["line_corridor"])

    rows_by_id = {row["id"]: row for row in crop_completion.get("targets", [])}
    for guard in orientation.get("targetRows", []):
        if guard["id"] in rows_by_id:
            rows_by_id[guard["id"]].update(
                {
                    "uprightBox": guard["uprightBox"],
                    "nativeRot180Box": guard["nativeRot180Box"],
                }
            )

    rows = list(rows_by_id.values())
    upright_order = sorted(rows, key=lambda row: (box_center_y(row["uprightBox"]), box_center_x(row["uprightBox"])))
    native_unnormalized_order = sorted(
        rows, key=lambda row: (box_center_y(row["nativeRot180Box"]), box_center_x(row["nativeRot180Box"]))
    )
    native_normalized_order = upright_order[:]

    upright_sig = signature(upright_order, "uprightBox")
    native_unnormalized_sig = signature(native_unnormalized_order, "nativeRot180Box")
    native_normalized_sig = signature(native_normalized_order, "uprightBox")

    line_corridor_streams = line_corridor.get("streams", {})
    summary = {
        "targetCount": len(rows),
        "uprightOrderIds": upright_sig["ids"],
        "nativeUnnormalizedOrderIds": native_unnormalized_sig["ids"],
        "nativeNormalizedOrderIds": native_normalized_sig["ids"],
        "colorPattern": upright_sig["colorPattern"],
        "visualStatePattern": upright_sig["visualStatePattern"],
        "colorPatternIsPalindrome": is_palindrome(upright_sig["colorPattern"]),
        "visualStatePatternIsPalindrome": is_palindrome(upright_sig["visualStatePattern"]),
        "uprightPageLines": upright_sig["pageLines"],
        "nativeUnnormalizedPageLines": native_unnormalized_sig["pageLines"],
        "formatAuthorityPageLines": format_authority.get("summary", {}).get("pageLines"),
        "uprightCorridorIndexes": upright_sig["corridorIndexes"],
        "nativeUnnormalizedCorridorIndexes": native_unnormalized_sig["corridorIndexes"],
        "formatAuthorityCorridorIndexes": format_authority.get("summary", {}).get("corridorIndexes"),
        "lineOrderDetectsFlip": upright_sig["pageLines"] != native_unnormalized_sig["pageLines"],
        "corridorOrderDetectsFlip": upright_sig["corridorIndexes"] != native_unnormalized_sig["corridorIndexes"],
        "lineCorridorHighlightedPositions": line_corridor_streams.get("highlighted_corridor_positions"),
        "lineCorridorHighlightedPageLines": line_corridor_streams.get("highlighted_page_line_indexes"),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 active target order/orientation guardrail; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "orders": {
            "uprightTopToBottom": upright_sig,
            "nativeUnnormalizedTopToBottom": native_unnormalized_sig,
            "nativeNormalizedTopToBottom": native_normalized_sig,
        },
        "interpretation": {
            "trap": "OBBO and YKKY are palindromes, so an upside-down/native ordering error preserves the same color/visual signature.",
            "orientationCheck": "Use line order 22 25 27 32 and corridor order 4 7 9 14, plus the recorded 180-degree image transform.",
            "selectorUnlocked": False,
        },
        "sheet": rel(SHEET),
        "decision": "page76_active_order_orientation_trap_guardrail_no_selector",
        "nextMove": "For future source comparisons, accept color/visual-state matching only after line/corridor order also matches the readable/upright O4->B4->G5->O5 order.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Active Order Orientation Trap",
        "",
        "Scope: audit whether the active O4/B4/G5/O5 color and visual-state sequence can validate source orientation. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Finding",
        "",
        f"- Upright/readable order: `{' -> '.join(upright_sig['labels'])}`.",
        f"- Native unnormalized top-to-bottom order: `{' -> '.join(native_unnormalized_sig['labels'])}`.",
        f"- Color pattern in upright order: `{upright_sig['colorPattern']}`; palindrome: `{summary['colorPatternIsPalindrome']}`.",
        f"- Visual-state pattern in upright order: `{upright_sig['visualStatePattern']}`; palindrome: `{summary['visualStatePatternIsPalindrome']}`.",
        f"- Upright page-line order: `{upright_sig['pageLines']}`; native unnormalized page-line order: `{native_unnormalized_sig['pageLines']}`.",
        f"- Upright corridor order: `{upright_sig['corridorIndexes']}`; native unnormalized corridor order: `{native_unnormalized_sig['corridorIndexes']}`.",
        "",
        "## Assessment",
        "",
        "- The active color and visual-state signatures are useful quartet identifiers, but they cannot validate orientation because both survive reversal.",
        "- Page-line order and corridor order are the practical orientation checks: the authoritative readable order is `O4 -> B4 -> G5 -> O5`, lines `22 25 27 32`, corridors `4 7 9 14`.",
        "- A future source that matches `OBBO/YKKY` but reverses lines/corridors should be treated as unnormalized/native orientation, not as a new selector.",
        "",
        "## Next Move",
        "",
        f"- {result['nextMove']}",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
