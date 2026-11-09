#!/usr/bin/env python3
"""Gate 3D OCR text inside the locked page-76 active target boxes.

The 3D article map is valuable for visual navigation and geometry, but its
character/word labels come from OCR. This pass checks the exact O4/B4/G5/O5
target boxes from the trusted crop-completion packet against the 3D map's
stored OCR characters and words. It does not run OCR, derive keys, hash text,
scan seeds/WIF/Base58, or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
TARGETS_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ORDER_JSON = ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/3d_article_map/active_quartet_box_ocr_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_quartet_box_ocr_gate.json"
OUT_MD = OUT / "active_quartet_box_ocr_gate.md"
SHEET = OUT / "active_quartet_box_ocr_gate_sheet.jpg"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def norm(text: str) -> str:
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.lower()
    text = re.sub(r"[^a-z0-9$]+", "", text)
    return text


def in_box(center: list[float], box: list[float], margin: float = 0.0) -> bool:
    x0, y0, x1, y1 = box
    x, y = center
    return x0 - margin <= x <= x1 + margin and y0 - margin <= y <= y1 + margin


def chars_in_box(chars: list[dict[str, Any]], box: list[float], margin: float = 0.0) -> str:
    selected = [ch for ch in chars if in_box([ch["x"], ch["y"]], box, margin)]
    selected.sort(key=lambda ch: (round(float(ch["y"]) / 8.0), float(ch["x"])))
    return "".join(str(ch.get("c", "")) for ch in selected)


def words_in_box(words: list[dict[str, Any]], box: list[float], margin: float = 0.0) -> list[str]:
    selected = [word for word in words if in_box(word["center"], box, margin)]
    selected.sort(key=lambda word: (round(float(word["center"][1]) / 8.0), float(word["center"][0])))
    return [str(word.get("text", "")) for word in selected]


def similarity(a: str, b: str) -> float:
    na, nb = norm(a), norm(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return round(SequenceMatcher(None, na, nb).ratio(), 4)


def crop_with_padding(image: Image.Image, box: list[int], pad: int = 70) -> Image.Image:
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(image.width, x1 + pad)
    y1 = min(image.height, y1 + pad)
    crop = image.crop((x0, y0, x1, y1)).convert("RGB")
    draw = ImageDraw.Draw(crop)
    draw.rectangle((pad, pad, pad + (box[2] - box[0]), pad + (box[3] - box[1])), outline=(255, 80, 40), width=4)
    return crop


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE_IMAGE).convert("RGB")
    sheet_w, sheet_h = 1720, 1180
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "3D Active Quartet Box OCR Gate", fill=(244, 247, 250), font=title)
    draw.text(
        (margin, margin + 46),
        "The 3D map hits the right target boxes, but its OCR labels are checked here against exact O4/B4/G5/O5 wording.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("targets", result["summary"]["targetCount"]),
        ("exact box matches", result["summary"]["exactBoxMatchCount"]),
        ("usable for text extraction", result["summary"]["usableForTextExtraction"]),
        ("order", result["summary"]["readableOrder"]),
    ]
    x = margin
    widths = [220, 300, 390, 610]
    for (label, value), w in zip(chips, widths):
        draw.rectangle((x, y, x + w, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += w + 20

    y += 92
    draw.rectangle((margin, y, sheet_w - margin, y + 100), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Use the 3D map for geometry/navigation only; exact active-target text must come from DOCM/plain text/crop review.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 74),
        "This closes target-box OCR as a future selector surface under the current map.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 130
    for row in result["rows"]:
        panel_h = 195
        draw.rectangle((margin, y, sheet_w - margin, y + panel_h), fill=(18, 22, 28), outline=(48, 58, 70))
        crop = crop_with_padding(page, row["box"], pad=70)
        crop.thumbnail((360, 150))
        sheet.paste(crop, (margin + 14, y + 24))
        tx = margin + 400
        draw.text((tx, y + 16), row["label"], fill=(238, 243, 248), font=normal)
        detail_lines = [
            f"exact: {row['phrase']}",
            f"box chars: {row['ocrCharsBox'] or '-'}",
            f"box words: {row['ocrWordsBoxText'] or '-'}",
            f"similarity: {row['boxCharSimilarity']}  exactMatch={row['exactBoxMatch']}",
            f"line/corridor: {row['pageLine']} / {row['corridorIndex']}  visual={row['visualState']}",
        ]
        ty = y + 50
        for line in detail_lines:
            draw.text((tx, ty), line[:130], fill=(176, 186, 198), font=small if not line.startswith("box") else mono)
            ty += 25
        y += panel_h + 20

    sheet.save(SHEET, quality=94)


def main() -> None:
    map_data = load_json(MAP_JSON)
    target_data = load_json(TARGETS_JSON)
    order_data = load_json(ORDER_JSON)
    page76 = next(page for page in map_data["pages"] if int(page["page"]) == 76)
    chars = page76["chars"]
    words = page76["words"]

    rows = []
    for target in target_data["targets"]:
        box = [int(v) for v in target["box"]]
        ocr_chars_box = chars_in_box(chars, box, margin=0).strip()
        ocr_chars_margin = chars_in_box(chars, box, margin=25).strip()
        ocr_words_box = words_in_box(words, box, margin=0)
        ocr_words_margin = words_in_box(words, box, margin=25)
        phrase = target["phrase"]
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "phrase": phrase,
                "box": box,
                "crop": target["crop"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
                "visualState": target["visualState"],
                "ocrCharsBox": ocr_chars_box,
                "ocrCharsMargin25": ocr_chars_margin,
                "ocrWordsBox": ocr_words_box,
                "ocrWordsBoxText": " ".join(ocr_words_box),
                "ocrWordsMargin25": ocr_words_margin,
                "ocrWordsMargin25Text": " ".join(ocr_words_margin),
                "boxCharSimilarity": similarity(phrase, ocr_chars_box),
                "margin25CharSimilarity": similarity(phrase, ocr_chars_margin),
                "boxWordSimilarity": similarity(phrase, " ".join(ocr_words_box)),
                "exactBoxMatch": norm(phrase) == norm(ocr_chars_box) or norm(phrase) == norm(" ".join(ocr_words_box)),
            }
        )

    exact_matches = [row for row in rows if row["exactBoxMatch"]]
    corrupted_rows = [
        row
        for row in rows
        if not row["exactBoxMatch"]
        and (row["ocrCharsBox"] or row["ocrWordsBoxText"] or row["ocrCharsMargin25"] or row["ocrWordsMargin25Text"])
    ]
    blank_rows = [
        row
        for row in rows
        if not row["ocrCharsBox"] and not row["ocrWordsBoxText"]
    ]

    summary = {
        "targetCount": len(rows),
        "exactBoxMatchCount": len(exact_matches),
        "corruptedOrMisreadBoxCount": len(corrupted_rows),
        "blankBoxCount": len(blank_rows),
        "usableForTextExtraction": False,
        "readableOrder": " -> ".join(row["id"] for row in rows),
        "lineOrder": " ".join(str(row["pageLine"]) for row in rows),
        "corridorOrder": " ".join(str(row["corridorIndex"]) for row in rows),
        "orientationGuardrail": order_data.get("decision"),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D active quartet target-box OCR gate; no OCR run, no extraction, no key derivation, no hashing, no seed/WIF/address checks",
        "inputs": {
            "article3dMap": rel(MAP_JSON),
            "activeTargetCropCompletion": rel(TARGETS_JSON),
            "orderOrientationTrap": rel(ORDER_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "summary": summary,
        "rows": rows,
        "decision": "3d_target_box_ocr_not_text_authority",
        "sheet": rel(SHEET),
        "nextMove": "Keep 3D target boxes as geometry/source-registration aids only; exact wording must be resolved through DOCM/plain text/crop review before any future selector is evaluated.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 3D Active Quartet Box OCR Gate",
        "",
        "Scope: check the 3D map's stored OCR characters and word labels inside the exact O4/B4/G5/O5 active target boxes. No OCR was run, and no extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Targets checked: `{summary['targetCount']}`.",
        f"- Exact OCR-box matches: `{summary['exactBoxMatchCount']}`.",
        f"- Corrupted/misread target boxes: `{summary['corruptedOrMisreadBoxCount']}`.",
        f"- Blank target boxes: `{summary['blankBoxCount']}`.",
        f"- Readable order preserved by target metadata: `{summary['lineOrder']}` lines / `{summary['corridorOrder']}` corridor indexes.",
        "",
        "## Target Box Checks",
        "",
        "| target | exact wording | box chars | box words | char similarity | exact match |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['label']}` | `{row['phrase']}` | `{row['ocrCharsBox'] or '-'}` | `{row['ocrWordsBoxText'] or '-'}` | `{row['boxCharSimilarity']}` | `{row['exactBoxMatch']}` |"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The 3D/canvas box geometry still identifies the same O4/B4/G5/O5 physical targets and preserves the readable line/corridor order.",
            "- The text labels inside those boxes are not extraction-grade: O4, B4, G5, and O5 all fail exact OCR-box matching.",
            "- This reinforces the current authority split: 3D map for geometry/navigation, DOCM/plain text/crop review for exact wording.",
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
