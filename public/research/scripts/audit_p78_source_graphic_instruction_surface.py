#!/usr/bin/env python3
"""Audit the p78 source graphic itself as an instruction surface.

The p78 pull-quote/frame is one of the strongest surviving registration
objects. This pass asks only whether the source-side visible text/graphic
surface supplies the missing extraction unit before it is mirrored onto p76.
No key derivation or broad stream testing is performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PULLQUOTE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json"
SOURCE_FIT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit.json"
TRICONTACT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"

OUT_JSON = OUT_DIR / "p78_source_graphic_instruction_surface.json"
OUT_MD = OUT_DIR / "p78_source_graphic_instruction_surface.md"
OUT_SHEET = OUT_DIR / "p78_source_graphic_instruction_surface_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "select",
    "choose",
    "use",
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "edge",
    "edges",
    "font",
    "typeka",
    "mix",
    "bold",
    "mirror",
    "fold",
    "reverse",
    "backward",
    "left",
    "right",
    "up",
    "down",
    "first",
    "last",
    "key",
    "private",
    "seed",
    "address",
]
THEMATIC_TERMS = ["economy", "love", "efficient", "hate", "war", "heart", "bitcoin"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text.lower())


def term_hits(text: str, terms: list[str]) -> list[str]:
    toks = set(words(text))
    return [term for term in terms if term.lower() in toks]


def center(box: list[float] | tuple[float, ...]) -> tuple[float, float]:
    return ((float(box[0]) + float(box[2])) / 2, (float(box[1]) + float(box[3])) / 2)


def inside(cx: float, cy: float, box: list[float] | tuple[float, ...]) -> bool:
    return float(box[0]) <= cx <= float(box[2]) and float(box[1]) <= cy <= float(box[3])


def inflate(box: list[float] | tuple[float, ...], margin: float, image_size: tuple[int, int]) -> tuple[int, int, int, int]:
    w, h = image_size
    return (
        max(0, int(round(float(box[0]) - margin))),
        max(0, int(round(float(box[1]) - margin))),
        min(w, int(round(float(box[2]) + margin))),
        min(h, int(round(float(box[3]) + margin))),
    )


def offset_box(box: list[float] | tuple[float, ...], crop: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (
        int(round(float(box[0]) - crop[0])),
        int(round(float(box[1]) - crop[1])),
        int(round(float(box[2]) - crop[0])),
        int(round(float(box[3]) - crop[1])),
    )


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, color: tuple[int, int, int], width: int = 4) -> None:
    draw.rectangle(box, outline=color, width=width)
    draw.rectangle((box[0], max(0, box[1] - 24), box[0] + max(80, len(label) * 7), box[1]), fill=(255, 255, 255))
    draw.text((box[0] + 4, max(0, box[1] - 20)), label, fill=color)


def page_words(page_no: int) -> list[dict[str, Any]]:
    data = load_json(MAP_JSON)
    page = next(page for page in data["pages"] if page["page"] == page_no)
    return page["words"]


def ocr_words_in_and_near_source(box: list[int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inside_words: list[dict[str, Any]] = []
    nearby_words: list[dict[str, Any]] = []
    near = [box[0] - 120, box[1] - 120, box[2] + 120, box[3] + 120]
    for word in page_words(78):
        cx, cy = word["center"]
        if inside(cx, cy, box):
            inside_words.append(word)
        elif inside(cx, cy, near):
            nearby_words.append(word)
    inside_words.sort(key=lambda w: (w["center"][1], w["center"][0]))
    nearby_words.sort(key=lambda w: (w["center"][1], w["center"][0]))
    return inside_words, nearby_words


def make_sheet(source_box: list[int], repair_box: list[int], reflected_box: list[int], tri: dict[str, Any]) -> None:
    p78 = upright_image(78).convert("RGB")
    p76 = upright_image(76).convert("RGB")

    src_crop_box = inflate(source_box, 170, p78.size)
    tgt_crop_box = inflate(reflected_box, 170, p76.size)

    src_panel = p78.crop(src_crop_box)
    tgt_panel = p76.crop(tgt_crop_box)
    src_draw = ImageDraw.Draw(src_panel)
    tgt_draw = ImageDraw.Draw(tgt_panel)

    draw_box(src_draw, offset_box(source_box, src_crop_box), "p78 source graphic", (0, 155, 220), 5)
    draw_box(src_draw, offset_box(repair_box, src_crop_box), "dx -38 source frame", (220, 0, 160), 4)
    src_draw.text((10, 12), "Source side: pull-quote/frame object", fill=(0, 0, 0))

    draw_box(tgt_draw, offset_box(reflected_box, tgt_crop_box), "p76 reflected frame", (0, 155, 220), 5)
    for name, color in [("G5", (0, 170, 170)), ("O5", (255, 90, 0))]:
        target = tri["targets"][name]
        draw_box(tgt_draw, offset_box(target["box"], tgt_crop_box), f"{name} {target['label']}", color, 4)
    draw_box(tgt_draw, offset_box(tri["m3"]["box"], tgt_crop_box), "M3 mark", (120, 0, 220), 4)
    tgt_draw.text((10, 12), "Target side: registration contacts only", fill=(0, 0, 0))

    max_w = 760
    for panel in [src_panel, tgt_panel]:
        if panel.width > max_w:
            ratio = max_w / panel.width
            panel.thumbnail((max_w, int(panel.height * ratio)), Image.Resampling.LANCZOS)

    width = max(src_panel.width, tgt_panel.width)
    height = src_panel.height + tgt_panel.height + 18
    sheet = Image.new("RGB", (width, height), "white")
    sheet.paste(src_panel, (0, 0))
    sheet.paste(tgt_panel, (0, src_panel.height + 18))
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    pullquote = load_json(PULLQUOTE_JSON)
    source_fit = load_json(SOURCE_FIT_JSON)
    tri = load_json(TRICONTACT_JSON)

    source_text = pullquote["graphicText"]
    source_box = source_fit["detectedP78GraphicBox"]
    repair_row = next(row for row in source_fit["rows"] if row["name"] == "g5_edge_touch_dx_-38")
    repair_box = repair_row["p78UprightBox"]
    reflected_box = repair_row["p76ReflectedUprightBox"]

    inside_words, nearby_words = ocr_words_in_and_near_source(source_box)
    inside_text = " ".join(word["text"] for word in inside_words)
    nearby_text = " ".join(word["text"] for word in nearby_words)

    make_sheet(source_box, repair_box, reflected_box, tri)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 source graphic instruction-surface audit; no key derivation",
        "inputs": {
            "pullquoteReflection": str(PULLQUOTE_JSON.relative_to(ROOT)),
            "sourceSideFit": str(SOURCE_FIT_JSON.relative_to(ROOT)),
            "triContact": str(TRICONTACT_JSON.relative_to(ROOT)),
            "article3dMap": str(MAP_JSON.relative_to(ROOT)),
        },
        "sourceGraphic": {
            "box": source_box,
            "manualVisibleText": source_text,
            "manualWordCount": len(words(source_text)),
            "instructionHits": term_hits(source_text, INSTRUCTION_TERMS),
            "thematicHits": term_hits(source_text, THEMATIC_TERMS),
        },
        "sourceSideOcrLabelCheck": {
            "insideWordCount": len(inside_words),
            "insideText": inside_text,
            "insideInstructionHits": term_hits(inside_text, INSTRUCTION_TERMS),
            "nearbyWordCount": len(nearby_words),
            "nearbyText": nearby_text,
            "nearbyInstructionHits": term_hits(nearby_text, INSTRUCTION_TERMS),
        },
        "registrationContext": {
            "currentSourceFrameCapturesGraphicMask": source_fit["summary"]["sourceSideFitFavorsCurrentDetectedBox"],
            "dxMinus38SourceMaskCapture": repair_row["graphicMaskCapture"],
            "dxMinus38ReflectedP76Frame": reflected_box,
            "triContactPass": next(row for row in tri["records"] if row["name"] == "g5_edge_touch")["triContactPass"],
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "The p78 source object is a visible pull-quote/frame, not a hidden instruction label.",
            "Manual visible source text has thematic terms (`economy`, `love`, `efficient`, `hate`, `war`) but no extraction terms such as read/take/word/letter/line/mirror/fold/key/private.",
            "The 3D/OCR labels inside the graphic are low-quality graphic-text artifacts and also contain no extraction unit.",
            "The p78 object remains a registration/orientation source for the p76 lower corridor; it does not supply the missing unit/order by itself.",
        ],
        "decision": {
            "p78SourceGraphicAsInstructionSurface": "closed_current_scan",
            "nextMove": "Keep p78 frame only as validation evidence. Continue toward explicit source/external wording or new physical/original-layout imagery before extracting from G5/O5.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# P78 Source Graphic Instruction Surface",
        "",
        "Scope: inspect the p78 pull-quote/frame source object itself for a visible instruction or ordering rule before using it as a p76 mirror source. No key derivation, hashing, seed checking, WIF/minikey checking, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Source Object",
        "",
        f"- p78 graphic box: `{source_box}`",
        f"- Manual visible graphic text: `{source_text}`",
        f"- Manual word count: `{result['sourceGraphic']['manualWordCount']}`",
        f"- Instruction hits in manual visible text: `{result['sourceGraphic']['instructionHits']}`",
        f"- Thematic hits in manual visible text: `{result['sourceGraphic']['thematicHits']}`",
        "",
        "## Source-Side OCR Label Check",
        "",
        f"- OCR/3D words whose centers fall inside the p78 graphic box: `{len(inside_words)}`",
        f"- Inside OCR text: `{inside_text}`",
        f"- Instruction hits inside OCR labels: `{result['sourceSideOcrLabelCheck']['insideInstructionHits']}`",
        f"- Nearby OCR words within 120px of the source graphic but outside it: `{len(nearby_words)}`",
        f"- Nearby OCR instruction hits: `{result['sourceSideOcrLabelCheck']['nearbyInstructionHits']}`",
        "",
        "## Registration Context",
        "",
        f"- Current p78 source frame captures graphic mask: `{source_fit['summary']['sourceSideFitFavorsCurrentDetectedBox']}`",
        f"- dx=-38 source-frame mask capture: `{repair_row['graphicMaskCapture']}`",
        f"- dx=-38 reflected p76 frame: `{reflected_box}`",
        f"- dx=-38 p76 tri-contact pass: `{result['registrationContext']['triContactPass']}`",
        "",
        "## Assessment",
        "",
        "- The p78 graphic remains strong as a registration object because it bridges to the p76 lower corridor.",
        "- Its own visible text is thematic prose, not an instruction surface: no `read`, `take`, `word`, `letter`, `line`, `mirror`, `fold`, `key`, or `private` term appears.",
        "- The source-side OCR layer is not reliable enough to recover the graphic text and still adds no extraction unit.",
        "- Close p78 source graphic text as a standalone selector under the current scan; keep the p78 frame only as a validation benchmark.",
        "",
        "## Next Move",
        "",
        "- Continue looking for explicit source/external wording or new physical/original-layout imagery before extracting from G5/O5. Do not treat p78 pull-quote wording as key material.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("p78SourceGraphicAsInstructionSurface: closed_current_scan")


if __name__ == "__main__":
    main()
