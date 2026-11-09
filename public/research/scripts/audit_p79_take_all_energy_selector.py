#!/usr/bin/env python3
"""Focused audit of p79 "That's right, Bitcoin will take all the energy" as a selector."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MIRROR_JSON = ROOT / "analysis_outputs/source_audit/highres_page76_mirror_selector.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
P76_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
P79_IMG = ROOT / "analysis_outputs/3d_article_map/page_79_upright.jpg"
OUT_DIR = ROOT / "analysis_outputs/source_audit/p79_take_all_energy_selector"
OUT_MD = OUT_DIR / "p79_take_all_energy_selector.md"
OUT_JSON = OUT_DIR / "p79_take_all_energy_selector.json"
OUT_SHEET = OUT_DIR / "p79_take_all_energy_selector_sheet.jpg"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "select",
    "choose",
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "mirror",
    "fold",
    "reverse",
    "key",
    "private",
    "seed",
    "address",
    "first",
    "last",
    "right",
    "left",
}


def area(box: list[float] | tuple[float, ...]) -> float:
    return max(0.0, float(box[2]) - float(box[0])) * max(0.0, float(box[3]) - float(box[1]))


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def words_in_box(words: list[dict], box: list[float]) -> list[dict]:
    out = []
    for word in words:
        x, y = word["center"]
        if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
            out.append(word)
    return out


def words_on_line_side(words: list[dict], line_box: list[float], x_cut: float, side: str) -> list[dict]:
    out = []
    for word in words:
        x, y = word["center"]
        if not (line_box[1] <= y <= line_box[3]):
            continue
        if side == "right" and x > x_cut:
            out.append(word)
        elif side == "left" and x < x_cut:
            out.append(word)
    return out


def text_for(words: list[dict]) -> str:
    return " ".join(w["text"] for w in sorted(words, key=lambda w: w["index"]))


def instruction_hits(text: str) -> list[str]:
    toks = {
        "".join(ch for ch in raw.lower() if ch.isalnum())
        for raw in text.replace("-", " ").split()
    }
    return sorted(t for t in INSTRUCTION_TERMS if t in toks)


def crop_with_box(img: Image.Image, boxes: list[tuple[list[float], str, tuple[int, int, int]]], pad: int = 80) -> Image.Image:
    x1 = max(0, int(min(b[0][0] for b in boxes)) - pad)
    y1 = max(0, int(min(b[0][1] for b in boxes)) - pad)
    x2 = min(img.width, int(max(b[0][2] for b in boxes)) + pad)
    y2 = min(img.height, int(max(b[0][3] for b in boxes)) + pad)
    crop = img.crop((x1, y1, x2, y2)).convert("RGB")
    draw = ImageDraw.Draw(crop)
    for box, label, color in boxes:
        shifted = [box[0] - x1, box[1] - y1, box[2] - x1, box[3] - y1]
        draw.rectangle(shifted, outline=color, width=5)
        draw.text((shifted[0] + 6, max(4, shifted[1] - 24)), label, fill=color)
    return crop


def build_sheet(source_crop: Image.Image, target_crop: Image.Image, summary: list[str]) -> None:
    width = max(source_crop.width, target_crop.width, 1200)
    height = source_crop.height + target_crop.height + 220
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    y = 18
    draw.text((20, y), "p79 highlighted phrase as selector: source crop", fill=(0, 0, 0))
    y += 28
    sheet.paste(source_crop, (20, y))
    y += source_crop.height + 26
    draw.text((20, y), "p76 result after raw high-res horizontal mirror", fill=(0, 0, 0))
    y += 28
    sheet.paste(target_crop, (20, y))
    y += target_crop.height + 22
    for line in summary:
        draw.text((20, y), line, fill=(0, 0, 0))
        y += 24
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mirror = json.loads(MIRROR_JSON.read_text())
    article_map = json.loads(MAP_JSON.read_text())

    source = next(
        s
        for s in mirror["reflectedSources"]
        if s["sourcePage"] == 79 and s["index"] == 2
    )
    edges = [
        e
        for e in mirror["meaningfulEdges"]
        if e["sourcePage"] == 79 and e["sourceIndex"] == 2
    ]

    page76 = next(p for p in article_map["pages"] if p["page"] == 76)
    p76_words = page76["words"]

    reflected_box = [float(v) for v in source["reflectedBox"]]
    direct_words = words_in_box(p76_words, reflected_box)

    edge_records = []
    for edge in edges:
        target_box = [float(v) for v in edge["targetBox"]]
        overlap = intersection(reflected_box, target_box)
        target_words = words_in_box(p76_words, target_box)
        overlap_words = words_in_box(p76_words, overlap) if overlap else []
        right_words = words_on_line_side(p76_words, target_box, reflected_box[2], "right")
        left_words = words_on_line_side(p76_words, target_box, reflected_box[0], "left")
        edge_records.append(
            {
                "target": f"{edge['targetColor']}{edge['targetIndex']}",
                "targetLabel": edge["targetLabel"],
                "targetBox": target_box,
                "overlapBox": overlap,
                "overlapVsSource": edge["overlapVsSource"],
                "overlapVsTarget": edge["overlapVsTarget"],
                "targetWords": text_for(target_words),
                "overlapWords": text_for(overlap_words),
                "rightOfReflectedBoxWords": text_for(right_words),
                "leftOfReflectedBoxWords": text_for(left_words),
                "targetInstructionHits": instruction_hits(text_for(target_words)),
                "overlapInstructionHits": instruction_hits(text_for(overlap_words)),
                "rightInstructionHits": instruction_hits(text_for(right_words)),
                "leftInstructionHits": instruction_hits(text_for(left_words)),
            }
        )

    source_img = Image.open(P79_IMG)
    target_img = Image.open(P76_IMG)
    source_crop = crop_with_box(
        source_img,
        [([float(v) for v in source["sourceBox"]], "p79 O2 source", (220, 90, 0))],
        pad=80,
    )
    target_boxes = [(reflected_box, "reflected p79 O2", (180, 0, 220))]
    for rec in edge_records:
        target_boxes.append((rec["targetBox"], rec["target"], (0, 120, 220)))
    target_crop = crop_with_box(target_img, target_boxes, pad=90)
    build_sheet(
        source_crop,
        target_crop,
        [
            f"direct reflected words: {text_for(direct_words)}",
            "decision: lands on upper p76 grey prose, not lower p76 target corridor",
        ],
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "focused high-res mirror audit of p79 highlighted action phrase; no key derivation",
        "inputs": {
            "mirrorSelector": str(MIRROR_JSON.relative_to(ROOT)),
            "articleMap": str(MAP_JSON.relative_to(ROOT)),
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "source": {
            "page": 79,
            "index": source["index"],
            "label": source["label"],
            "sourceBox": source["sourceBox"],
            "reflectedBoxOn76": source["reflectedBox"],
            "sourceInstructionHits": instruction_hits(source["label"]),
        },
        "directReflectedWordsOn76": text_for(direct_words),
        "directInstructionHits": instruction_hits(text_for(direct_words)),
        "edgeRecords": edge_records,
        "assessment": [
            "The p79 phrase is legitimately tempting because it contains `right` and `take`, and it is a highlighted Typeka-bold run.",
            "Under the current high-res horizontal mirror, it lands on p76 upper grey text (`Gotta be this way... post-1971 fiat money`) and grazes `nonsense`; it does not land on the lower El Salvador/IMF/G5/O5 corridor.",
            "Taking the right side of the overlapped p76 grey row yields ordinary prose (`of dumb post-1971 fiat money`) and no extraction unit.",
            "The phrase itself still lacks a concrete unit such as word, letter, line, font, key, private, seed, or address.",
        ],
        "decision": {
            "p79TakeAllEnergyAsCurrentScanSelector": "closed_current_scan",
            "p79TakeAllEnergyAsContext": "keep_as_thematic_energy_wording",
            "nextMove": "Do not promote p79 O2 as selector unless a new source transform moves it onto the lower page-76 corridor or an external clue explains the unit/order.",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# P79 Take-All-Energy Selector Audit",
        "",
        "Scope: focused high-res mirror audit of the p79 highlighted action phrase `That's right, Bitcoin will take all the energy.` No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Source Phrase",
        "",
        f"- Source: p79 orange/highlight box `{source['index']}`",
        f"- Text: `{source['label']}`",
        f"- Source instruction hits: `{result['source']['sourceInstructionHits']}`",
        f"- Reflected box on p76: `{source['reflectedBox']}`",
        "",
        "## Page-76 Landing",
        "",
        f"- Direct words inside reflected box: `{result['directReflectedWordsOn76']}`",
        f"- Direct instruction hits: `{result['directInstructionHits']}`",
        "",
        "| target | target label | overlap source | overlap target | overlap words | right-side words | hits |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for rec in edge_records:
        hits = sorted(set(rec["overlapInstructionHits"] + rec["rightInstructionHits"]))
        lines.append(
            f"| `{rec['target']}` | `{rec['targetLabel']}` | `{rec['overlapVsSource']}` | `{rec['overlapVsTarget']}` | "
            f"`{rec['overlapWords']}` | `{rec['rightOfReflectedBoxWords']}` | `{hits}` |"
        )

    lines += [
        "",
        "## Findings",
        "",
        "- The source phrase is not ignored: it is one of the few font-state runs with action-like wording (`right`, `take`).",
        "- Under the current high-res mirror, it lands on p76 upper grey prose: `Gotta be this way... post-1971 fiat money`, not on the lower El Salvador / IMF / `Volcano Bonds` / `shitcoiner at heart` target corridor.",
        "- The literal `right` side of that landing yields ordinary article prose and no `word`, `letter`, `line`, `key`, `private`, `seed`, or `address` unit.",
        "",
        "## Decision",
        "",
        "- Close p79 `That's right, Bitcoin will take all the energy` as a standalone current-scan selector.",
        "- Keep it only as thematic energy/action wording unless a new source transform moves this phrase onto the lower page-76 corridor or a clue supplies the unit/order.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("p79TakeAllEnergyAsCurrentScanSelector: closed_current_scan")


if __name__ == "__main__":
    main()
