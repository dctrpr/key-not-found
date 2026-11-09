#!/usr/bin/env python3
"""Build a visual bridge from trusted crops to exact corrected wording.

This is a navigation/source-fidelity artifact. It pairs the current page-76
priority crops with the corrected wording and the 3D-label status, so future
visual inspection does not accidentally treat noisy OCR labels as exact text.
No key material is derived or checked.
"""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/3d_article_map/active_target_label_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_SHEET = OUT / "target_wording_bridge_sheet.jpg"
OUT_JSON = OUT / "target_wording_bridge.json"
OUT_MD = OUT / "target_wording_bridge.md"

CROP_DIR = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack"
LABEL_GATE = ROOT / "analysis_outputs/3d_article_map/active_target_label_gate/active_target_label_gate.json"


ROWS = [
    {
        "id": "L32_O5_primary",
        "crop": CROP_DIR / "L32_O5_primary.jpg",
        "exactText": "Maybe because he's a shitcoiner at heart.",
        "labelIds": ["p76_shitcoiner_heart"],
        "status": "primary O5 target; exact text absent from 3D labels",
    },
    {
        "id": "L27_G5_pair",
        "crop": CROP_DIR / "L27_G5_pair.jpg",
        "exactText": 'collateralized "Volcano Bonds" to pay off the IMF loan',
        "labelIds": ["p76_volcano_bonds", "p76_imf_loan"],
        "status": "G5 pair; Volcano Bonds absent from 3D labels, IMF loan present",
    },
    {
        "id": "L25_should_sell",
        "crop": CROP_DIR / "L25_should_sell.jpg",
        "exactText": "$1 billion in bitcoin - that he should sell",
        "labelIds": ["p76_one_billion", "p76_should_sell"],
        "status": "$1 billion absent from 3D labels; should sell present",
    },
    {
        "id": "L26_L29_source_band",
        "crop": CROP_DIR / "L26_L29_source_band.jpg",
        "exactText": "billions worth of future bitcoin earnings / Volcano Bonds / IMF loan / Mike Novogratz",
        "labelIds": ["p76_future_earnings", "p76_volcano_bonds", "p76_imf_loan", "p76_mike_novogratz"],
        "status": "mixed reliability; use crop and corrected transcript for exact wording",
    },
    {
        "id": "L25_L32_frame_context",
        "crop": CROP_DIR / "L25_L32_frame_context.jpg",
        "exactText": "should sell -> Volcano Bonds -> shitcoiner at heart",
        "labelIds": ["p76_should_sell", "p76_volcano_bonds", "p76_shitcoiner_heart"],
        "status": "compact p78-frame benchmark; registration evidence only",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main() -> None:
    gate = json.loads(LABEL_GATE.read_text(encoding="utf-8"))
    gate_by_id = {row["id"]: row for row in gate["rows"]}

    title_f = font(36, True)
    head_f = font(24, True)
    body_f = font(21)
    small_f = font(17)
    mono_f = font(17)

    width = 1800
    margin = 46
    row_h = 300
    header_h = 210
    height = header_h + row_h * len(ROWS) + margin
    sheet = Image.new("RGB", (width, height), (248, 248, 246))
    draw = ImageDraw.Draw(sheet)

    draw.rectangle([0, 0, width, header_h], fill=(28, 31, 36))
    draw.text((margin, 38), "3D Target Wording Bridge", font=title_f, fill="white")
    draw.text(
        (margin, 92),
        "Trusted page-76 crops + corrected wording. 3D OCR labels are navigation only.",
        font=body_f,
        fill=(225, 225, 220),
    )
    draw.text(
        (margin, 134),
        "No key derivation, hashing, seed/WIF/address checks, or broad extraction was run.",
        font=small_f,
        fill=(195, 205, 210),
    )

    y = header_h
    for idx, row in enumerate(ROWS):
        fill = (255, 255, 255) if idx % 2 == 0 else (241, 243, 245)
        draw.rectangle([margin // 2, y + 16, width - margin // 2, y + row_h - 16], fill=fill, outline=(215, 218, 220))
        crop = fit_image(row["crop"], (640, 210))
        sheet.paste(crop, (margin, y + 52))

        x_text = margin + 690
        draw.text((x_text, y + 44), row["id"], font=head_f, fill=(22, 28, 35))

        exact_lines = wrap(draw, f"Exact: {row['exactText']}", body_f, width - x_text - margin)
        yy = y + 84
        for line in exact_lines[:3]:
            draw.text((x_text, yy), line, font=body_f, fill=(45, 52, 59))
            yy += 31

        label_bits = []
        for label_id in row["labelIds"]:
            label = gate_by_id.get(label_id, {})
            label_bits.append(f"{label_id}={'3D-yes' if label.get('threeDHasPhrase') else '3D-no'}")
        draw.text((x_text, yy + 8), "Labels: " + "; ".join(label_bits), font=mono_f, fill=(87, 91, 97))
        yy += 38
        status_lines = wrap(draw, "Use: " + row["status"], small_f, width - x_text - margin)
        for line in status_lines[:2]:
            draw.text((x_text, yy + 8), line, font=small_f, fill=(120, 72, 32))
            yy += 25
        y += row_h

    sheet.save(OUT_SHEET, quality=94)

    result_rows = []
    for row in ROWS:
        labels = []
        for label_id in row["labelIds"]:
            label = gate_by_id.get(label_id, {})
            labels.append(
                {
                    "id": label_id,
                    "canonicalHasPhrase": label.get("canonicalHasPhrase"),
                    "threeDHasPhrase": label.get("threeDHasPhrase"),
                }
            )
        result_rows.append({**{k: v for k, v in row.items() if k != "crop"}, "crop": str(row["crop"].relative_to(ROOT)), "labels": labels})

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual bridge from trusted page-76 crops to exact corrected wording; no key derivation",
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "sourceGate": str(LABEL_GATE.relative_to(ROOT)),
        "rows": result_rows,
        "assessment": [
            "The active page-76 visual targets need exact transcript text, not 3D OCR labels.",
            "The sheet preserves the current crop/geometry baselines while making the text authority explicit.",
            "This supports future source comparison and manual inspection; it does not reopen extraction.",
        ],
        "decision": "Use this bridge when inspecting the 3D view or future source images for the lower page-76 corridor.",
        "nextMove": "Continue source-gated investigation; a new source/clue must still name the extraction unit/order before key work resumes.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 3D Target Wording Bridge",
        "",
        "Scope: pair trusted page-76 crop images with corrected wording and 3D-label status. No key derivation, hashing, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Rows",
        "",
        "| crop | exact wording | 3D-label status | use |",
        "|---|---|---|---|",
    ]
    for row in result_rows:
        label_status = "; ".join(f"{item['id']}={item['threeDHasPhrase']}" for item in row["labels"])
        lines.append(f"| `{row['id']}` | `{row['exactText']}` | `{label_status}` | {row['status']} |")
    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_SHEET}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("rows:", len(ROWS))


if __name__ == "__main__":
    main()
