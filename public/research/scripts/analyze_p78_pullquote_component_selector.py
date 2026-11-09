#!/usr/bin/env python3
"""Mirror individual p78 pull-quote graphic components onto page 76.

Prior p78 tests used the whole graphic mask/frame. This pass splits the lower
p78 graphic into connected visual components, mirrors each component bbox onto
page 76, and records the target words/highlights. It is a selector-quality
audit only; it does not generate keys, hashes, mnemonics, or addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from audit_p78_graphic_pullquote_reflection import GRAPHIC_TEXT, detect_graphic_mask, hflip_box
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
PAGE78 = ROOT / "analysis_outputs/3d_article_map/page_78_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_pullquote_component_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_pullquote_component_selector.json"
OUT_MD = OUT / "p78_pullquote_component_selector.md"
OUT_OVERLAY = OUT / "p78_pullquote_component_selector_overlay.jpg"
OUT_SOURCE = OUT / "p78_pullquote_component_source_overlay.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "seed",
    "wif",
    "address",
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def box_area(box: list[float] | tuple[float, float, float, float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_box(a, b) -> tuple[float, list[float] | None]:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0, None
    return box_area([x1, y1, x2, y2]), [x1, y1, x2, y2]


def center(box: list[float] | tuple[float, float, float, float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def lower_trusted_boxes() -> list[dict]:
    data = json.loads(LOWER_MARKS_JSON.read_text())
    rows = []
    for item in data["analyses"]:
        if item["classification"] == "text/highlight-false-positive":
            label = "$1 billion" if "$1 billion" in item.get("note", "") else "Volcano Bonds"
            rows.append({"id": f"M{item['index']}", "kind": "trusted-grey", "label": label, "box": item["box"]})
    return rows


def page76_highlight_targets(page: dict) -> list[dict]:
    labels = {
        "p76_orange_1": "Get some toxicity / Open your heart",
        "p76_orange_2": "Bitcoin",
        "p76_orange_3": "rancid catnip",
        "p76_orange_4": "buying the dip",
        "p76_orange_5": "shitcoiner at heart",
    }
    rows = []
    for h in page["highlights"]:
        rows.append({**h, "label": labels.get(h["id"], h["id"])})
    rows.extend(lower_trusted_boxes())
    return rows


def display_word(word: dict, targets: list[dict]) -> str:
    text = word["text"]
    if len(text) <= 14:
        return text
    for target in targets:
        if target["id"] == "p76_orange_5":
            overlap, _ = overlap_box(word["box"], target["box"])
            if overlap > 0:
                return "[O5: shitcoiner at heart]"
    return text


def component_rows(comps: list[dict]) -> list[dict]:
    # Component labels are visual only. Group by coarse y bands so the report
    # can show source order without pretending every component is a word.
    ordered = sorted(comps, key=lambda c: (c["center"][1], c["center"][0]))
    groups: list[list[dict]] = []
    for comp in ordered:
        if not groups:
            groups.append([comp])
            continue
        prev_y = sum(c["center"][1] for c in groups[-1]) / len(groups[-1])
        if abs(comp["center"][1] - prev_y) <= 70:
            groups[-1].append(comp)
        else:
            groups.append([comp])
    out = []
    index = 1
    for row_i, group in enumerate(groups, 1):
        for comp in sorted(group, key=lambda c: c["center"][0]):
            out.append({**comp, "componentId": f"C{index:02d}", "visualRow": row_i})
            index += 1
    return out


def words_hit_by_box(page: dict, box: list[float], targets: list[dict]) -> list[dict]:
    rows = []
    for word in page["words"]:
        cx, cy = word["center"]
        if not (2300 <= cy <= 3050):
            continue
        overlap, inter = overlap_box(box, word["box"])
        center_inside = box[0] <= cx <= box[2] and box[1] <= cy <= box[3]
        frac = overlap / max(1.0, box_area(word["box"]))
        if center_inside or frac >= 0.18:
            rows.append(
                {
                    "index": word["index"],
                    "text": word["text"],
                    "displayText": display_word(word, targets),
                    "box": word["box"],
                    "center": word["center"],
                    "overlapFracOfWord": round(frac, 4),
                    "centerInside": center_inside,
                }
            )
    return sorted(rows, key=lambda w: (w["center"][1], w["center"][0]))


def target_hits(box: list[float], targets: list[dict]) -> list[dict]:
    rows = []
    for target in targets:
        overlap, inter = overlap_box(box, target["box"])
        if not overlap:
            continue
        rows.append(
            {
                "id": target["id"],
                "kind": target["kind"],
                "label": target["label"],
                "overlapFracOfTarget": round(overlap / max(1.0, box_area(target["box"])), 4),
                "intersection": [round(v, 2) for v in inter],
            }
        )
    return rows


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    out = {}
    for name, value in streams.items():
        found = [
            term
            for term in INSTRUCTION_TERMS
            if re.search(rf"\b{re.escape(term)}\b", value.lower())
        ]
        if found:
            out[name] = found
    return out


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlays(component_records: list[dict], targets: list[dict]) -> None:
    p76 = Image.open(PAGE76).convert("RGB")
    crop76_box = [1080, 2320, 2544, 3055]
    crop76 = p76.crop(crop76_box)
    draw76 = ImageDraw.Draw(crop76)

    def tr76(box):
        return [box[0] - crop76_box[0], box[1] - crop76_box[1], box[2] - crop76_box[0], box[3] - crop76_box[1]]

    for target in targets:
        if target["box"][3] < crop76_box[1] or target["box"][1] > crop76_box[3]:
            continue
        color = (255, 120, 0) if target["kind"] == "orange" else (40, 40, 40)
        draw76.rectangle(tr76(target["box"]), outline=color, width=3)
    colors = [(0, 100, 255), (0, 160, 80), (180, 0, 180), (240, 90, 0)]
    for idx, record in enumerate(component_records):
        color = colors[idx % len(colors)]
        box = record["reflectedBoxOnP76"]
        if box[3] < crop76_box[1] or box[1] > crop76_box[3]:
            continue
        draw76.rectangle(tr76(box), outline=color, width=3)
        draw_label(draw76, (int(box[0] - crop76_box[0]), int(box[1] - crop76_box[1])), record["componentId"], color)
    crop76.save(OUT_OVERLAY, quality=95)

    p78 = Image.open(PAGE78).convert("RGB")
    crop78_box = [250, 2360, 1360, 2985]
    crop78 = p78.crop(crop78_box)
    draw78 = ImageDraw.Draw(crop78)

    def tr78(box):
        return [box[0] - crop78_box[0], box[1] - crop78_box[1], box[2] - crop78_box[0], box[3] - crop78_box[1]]

    for idx, record in enumerate(component_records):
        color = colors[idx % len(colors)]
        draw78.rectangle(tr78(record["sourceBox"]), outline=color, width=3)
        draw_label(draw78, (int(record["sourceBox"][0] - crop78_box[0]), int(record["sourceBox"][1] - crop78_box[1])), record["componentId"], color)
    crop78.save(OUT_SOURCE, quality=95)


def main() -> None:
    p78 = upright_image(78).convert("RGB")
    _mask, graphic_box, comps = detect_graphic_mask(p78)
    comps = component_rows(comps)
    page = load_page76()
    targets = page76_highlight_targets(page)

    records = []
    for comp in comps:
        source_box = [int(v) for v in comp["box"]]
        reflected = list(hflip_box(source_box, p78.width))
        words = words_hit_by_box(page, reflected, targets)
        highlights = target_hits(reflected, targets)
        records.append(
            {
                "componentId": comp["componentId"],
                "visualRow": comp["visualRow"],
                "sourceBox": source_box,
                "sourceCenter": [round(v, 2) for v in comp["center"]],
                "sourceArea": comp.get("area"),
                "reflectedBoxOnP76": reflected,
                "targetWords": words,
                "targetHighlights": highlights,
                "targetStream": clean(" ".join(w["displayText"] for w in words)),
            }
        )

    component_stream = " | ".join(r["targetStream"] for r in records if r["targetStream"])
    highlight_stream = " | ".join(
        f"{r['componentId']}:{','.join(h['id'] for h in r['targetHighlights'])}"
        for r in records
        if r["targetHighlights"]
    )
    sparse_stream = " | ".join(
        f"{r['componentId']}:{r['targetStream'] or '-'}"
        for r in records
        if r["targetStream"] or r["targetHighlights"]
    )
    streams = {
        "componentTargetStream": component_stream,
        "componentSparseStream": sparse_stream,
        "highlightStream": highlight_stream,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "individual p78 pull-quote graphic components mirrored onto p76; no key derivation",
        "graphicText": GRAPHIC_TEXT,
        "p78GraphicBox": list(map(int, graphic_box)),
        "componentCount": len(records),
        "componentRecords": records,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
        "overlayOnP76": str(OUT_OVERLAY.relative_to(ROOT)),
        "sourceOverlayOnP78": str(OUT_SOURCE.relative_to(ROOT)),
        "assessment": [
            "Splitting the p78 pull-quote into individual visual components does not produce a cleaner selector than the whole frame/mask.",
            "Several components land on the same broad lower p76 corridor words already seen in the full-mask pass, especially IMF/Mike/sell/trust/O5-adjacent material.",
            "No component isolates an instruction or a single decisive extraction unit.",
            "This closes p78 pull-quote components as a standalone selector while preserving the p78 frame as registration evidence.",
        ],
        "nextMove": "Use p78 pull-quote only as a frame/orientation layer. The missing rule must come from source registration, Schott mirror operation ordering, or an external/physical source, not from component-by-component p78 text.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_overlays(records, targets)

    lines = [
        "# P78 Pull-Quote Component Selector",
        "",
        "Scope: split the lower p78 graphic pull-quote into connected components, mirror each component onto page 76, and check whether any component becomes a clean selector. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Graphic text: `{GRAPHIC_TEXT}`",
        f"- Component count: `{len(records)}`",
        f"- P76 overlay: `{result['overlayOnP76']}`",
        f"- P78 source overlay: `{result['sourceOverlayOnP78']}`",
        "",
        "## Component Hits",
        "",
        "| component | source box | reflected p76 box | target words | target highlights |",
        "|---|---:|---:|---|---|",
    ]
    for record in records:
        words = record["targetStream"] or "-"
        hids = ", ".join(f"{h['id']}:{h['label']}({h['overlapFracOfTarget']})" for h in record["targetHighlights"]) or "-"
        lines.append(
            f"| `{record['componentId']}` | `{record['sourceBox']}` | `{record['reflectedBoxOnP76']}` | {words} | {hids} |"
        )
    lines.extend(
        [
            "",
            "## Streams",
            "",
            f"- `componentTargetStream`: `{component_stream}`",
            f"- `componentSparseStream`: `{sparse_stream}`",
            f"- `highlightStream`: `{highlight_stream}`",
            f"- Instruction-term hits: `{result['instructionTermHits']}`",
            "",
            "## Assessment",
            "",
        ]
    )
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print(f"wrote {OUT_SOURCE}")
    print("instruction hits:", result["instructionTermHits"])


if __name__ == "__main__":
    main()
