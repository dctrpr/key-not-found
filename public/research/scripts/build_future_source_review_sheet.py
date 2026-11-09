#!/usr/bin/env python3
"""Build a visual review sheet for future source comparisons.

The validation packet is the source-gate checklist. This companion sheet puts
the key geometry/provenance images on one page so a new physical scan, Canva
export, or browser capture can be compared visually before any extraction work
is reopened.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/future_source_validation_packet"
OUT.mkdir(parents=True, exist_ok=True)
OUT_IMG = OUT / "future_source_validation_review_sheet.jpg"
OUT_JSON = OUT / "future_source_validation_review_sheet.json"
OUT_MD = OUT / "future_source_validation_review_sheet.md"

PACKET = OUT / "future_source_validation_packet.json"

PANELS = [
    {
        "id": "page76_priority_crops",
        "title": "Page 76 Priority Crops",
        "image": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
        "caption": "O5, G5, and lower corridor crop baseline. Future geometry must be compared in readable/upright orientation.",
    },
    {
        "id": "p78_frame_tricontact",
        "title": "P78 Frame Tri-Contact",
        "image": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg",
        "caption": "Current frame clips O5, cuts M3, and sits 38 px from G5; dx=-38/-40 is the compact repair signature.",
    },
    {
        "id": "repaired_exact_edge_style",
        "title": "Exact-Edge Phrase / Style",
        "image": ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states_sheet.jpg",
        "caption": "Repaired exact-edge trio is should sell | Volcano Bonds | shitcoiner at heart, style code RKY.",
    },
    {
        "id": "typeka_typography_authority",
        "title": "Typeka Typography Authority",
        "image": ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg",
        "caption": "DOCM font/highlight witness for the active lower corridor. Markdown bold is annotation-only; $1 billion and Volcano Bonds are bold/black in DOCM.",
    },
    {
        "id": "zero_hash0_hotspots",
        "title": "Zero / #0 Hotspots",
        "image": ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg",
        "caption": "Current trusted scan reads the main hotspot as 100,000. Any source claiming 1000,000 must beat this crop.",
    },
    {
        "id": "p79_pill_fragments",
        "title": "P79 Pill Fragment Baseline",
        "image": ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry_sheet.jpg",
        "caption": "Trusted baseline has five lower-left p79 pill fragments. A new source must change count, order, or placement to reopen pills.",
    },
    {
        "id": "source_gate",
        "title": "Source Gate Summary",
        "image": ROOT / "analysis_outputs/source_audit/source_validation_gate/source_validation_gate_sheet.jpg",
        "caption": "Current scan is target/provenance-valid but not extraction-valid: C3/C4/C8 remain the blockers.",
    },
]

TEXT_PANELS = [
    {
        "id": "p77_line_gap",
        "title": "P77 One-Line Near Miss",
        "caption": "Benchmark: p77 `It does this by monetizing` -> p76 O5 misses by 71.93 px; page-76 median line pitch is 73.73 px. This is useful only if a future physical/source transform makes it a repeated direct contact.",
    },
    {
        "id": "minimum_reopen_conditions",
        "title": "Minimum Reopen Conditions",
        "caption": "Reopen extraction only if future material improves one gate: C3 names an extraction unit, C4 improves physical registration, C8 provides source-quality image evidence, or C2 naturally explains the p78 frame signature.",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE = font(26, bold=True)
BODY = font(18)
SMALL = font(15)


def resize_to_fit(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    image = image.convert("RGB")
    scale = min(max_w / image.width, max_h / image.height, 1.0)
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def wrapped_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def draw_text_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, max_chars: int, fill=(50, 50, 50)) -> int:
    x, y = xy
    for line in wrapped_lines(text, max_chars):
        draw.text((x, y), line, font=BODY, fill=fill)
        y += 24
    return y


def make_panel(title: str, caption: str, image_path: Path | None, panel_w: int = 900, panel_h: int = 680) -> Image.Image:
    panel = Image.new("RGB", (panel_w, panel_h), (248, 248, 246))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, panel_w - 1, panel_h - 1), outline=(190, 190, 185), width=2)
    draw.text((26, 22), title, font=TITLE, fill=(25, 25, 25))
    y = 62
    y = draw_text_block(draw, (26, y), caption, 74)

    image_top = max(136, y + 14)
    image_box = (26, image_top, panel_w - 26, panel_h - 26)
    if image_path and image_path.exists():
        try:
            img = Image.open(image_path)
            thumb = resize_to_fit(img, image_box[2] - image_box[0], image_box[3] - image_box[1])
            x = image_box[0] + ((image_box[2] - image_box[0]) - thumb.width) // 2
            y_img = image_box[1] + ((image_box[3] - image_box[1]) - thumb.height) // 2
            panel.paste(thumb, (x, y_img))
            draw.rectangle((x, y_img, x + thumb.width - 1, y_img + thumb.height - 1), outline=(120, 120, 120), width=1)
        except Exception as exc:
            draw.text((26, image_top), f"Image load failed: {exc}", font=BODY, fill=(130, 0, 0))
    else:
        draw.rectangle(image_box, outline=(210, 210, 205), width=2)
        draw.text((image_box[0] + 20, image_box[1] + 20), "Text-only benchmark", font=BODY, fill=(80, 80, 80))
    return panel


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8")) if PACKET.exists() else {}
    panels = []
    for row in PANELS:
        panels.append(make_panel(row["title"], row["caption"], row["image"]))
    for row in TEXT_PANELS:
        panels.append(make_panel(row["title"], row["caption"], None))

    cols = 2
    panel_w, panel_h = panels[0].size
    margin = 34
    header_h = 130
    rows = (len(panels) + cols - 1) // cols
    sheet_w = cols * panel_w + (cols + 1) * margin
    sheet_h = header_h + rows * panel_h + (rows + 1) * margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (232, 232, 228))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 28), "Future Source Validation Review Sheet", font=font(34, bold=True), fill=(20, 20, 20))
    subtitle = "Use this sheet before reopening extraction: a new source must improve C3, C4, C8, or naturally explain C2."
    draw.text((margin, 78), subtitle, font=BODY, fill=(55, 55, 55))
    draw.text((sheet_w - 430, 30), datetime.now().isoformat(timespec="seconds"), font=SMALL, fill=(85, 85, 85))

    for i, panel in enumerate(panels):
        col = i % cols
        row = i // cols
        x = margin + col * (panel_w + margin)
        y = header_h + margin + row * (panel_h + margin)
        sheet.paste(panel, (x, y))

    sheet.save(OUT_IMG, quality=92)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual source-validation review sheet; no key derivation",
        "packet": str(PACKET.relative_to(ROOT)),
        "sheet": str(OUT_IMG.relative_to(ROOT)),
        "panelCount": len(panels),
        "sourceDeltaDecision": packet.get("currentDecision", {}).get("sourceDeltaDecision"),
        "minimumReopenConditions": [item.get("condition") for item in packet.get("minimumReopenConditions", [])],
        "panels": [
            {
                "id": row["id"],
                "title": row["title"],
                "image": str(row["image"].relative_to(ROOT)) if row.get("image") else None,
                "caption": row["caption"],
            }
            for row in [*PANELS, *TEXT_PANELS]
        ],
        "decision": "review_sheet_ready_for_future_source_comparison",
        "nextMove": "When a new source image appears, compare it visually against this sheet and then score it against the validation packet before extraction.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Future Source Validation Review Sheet",
        "",
        "Scope: visual side-by-side sheet for future source/physical comparisons. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Panel count: `{result['panelCount']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Panels",
        "",
    ]
    for row in result["panels"]:
        image = f"`{row['image']}`" if row["image"] else "text-only"
        lines.append(f"- `{row['id']}`: {row['title']} ({image})")
    lines.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_IMG}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print("panelCount:", len(panels))


if __name__ == "__main__":
    main()
