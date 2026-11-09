#!/usr/bin/env python3
"""Standalone lower page-76 mark-as-pointer audit.

This pass separates real non-text brush/X marks from highlighted text boxes and
asks whether the remaining marks provide a line/word ordering cue.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
MARKS_JSON = OUT / "page76_nontext_marks.json"
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT_JSON = OUT / "lower_page76_mark_pointers.json"
OUT_MD = OUT / "lower_page76_mark_pointers.md"
OUT_IMG = OUT / "lower_page76_mark_pointers_overlay.jpg"


FALSE_POSITIVE_NOTES = {
    1: "$1 billion grey highlighted text box; detector caught text/highlight, not a separate mark.",
    2: "Volcano Bonds grey highlighted text box; detector caught text/highlight, not a separate mark.",
}

ROW_TO_CANONICAL_LINE = {
    20: 19,
    21: 20,
    22: 21,
    23: 22,
    24: 23,
    25: 24,
    26: 25,
    27: 26,
    28: 27,
    29: 28,
    30: 29,
    31: 30,
    32: 31,
    33: 32,
}

HIGHLIGHT_LABELS = {
    22: "orange: buying the dip",
    25: "grey: $1 billion",
    27: "grey: Volcano Bonds / IMF",
    31: "bold: I don't really trust that guy",
    32: "orange: shitcoiner at heart",
}


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def load_page76_words() -> list[dict]:
    data = json.loads(ARTICLE_MAP.read_text())
    page = next(p for p in data["pages"] if p["page"] == 76)
    return page["words"]


def load_canonical_lines() -> dict[int, str]:
    data = json.loads(CANONICAL.read_text())
    page = next(p for p in data["pages"].values() if p["articlePage"] == 76)
    return {line["lineIndex"]: line["text"].strip() for line in page["lines"]}


def visual_rows(words: list[dict]) -> list[dict]:
    rows: list[list[dict]] = []
    for word in sorted(words, key=lambda w: (w["center"][1], w["center"][0])):
        y = word["center"][1]
        if not rows:
            rows.append([word])
            continue
        median_y = statistics.median(w["center"][1] for w in rows[-1])
        if abs(median_y - y) > 45:
            rows.append([word])
        else:
            rows[-1].append(word)

    out = []
    canonical = load_canonical_lines()
    for i, row_words in enumerate(rows):
        y = statistics.median(w["center"][1] for w in row_words)
        ordered = sorted(row_words, key=lambda w: w["center"][0])
        line_index = ROW_TO_CANONICAL_LINE.get(i)
        out.append(
            {
                "visualRow": i,
                "y": round(y, 2),
                "words": ordered,
                "ocrText": " ".join(w["text"] for w in ordered),
                "canonicalLineIndex": line_index,
                "canonicalText": canonical.get(line_index, ""),
                "highlight": HIGHLIGHT_LABELS.get(line_index, ""),
            }
        )
    return out


def distance_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / denom))
    cx, cy = ax + t * vx, ay + t * vy
    return math.hypot(px - cx, py - cy)


def pca_axis(img: Image.Image, box: list[int]) -> dict:
    x1, y1, x2, y2 = [int(v) for v in box]
    crop = np.asarray(img.crop((x1, y1, x2, y2)).convert("L"))
    mask = crop < 90
    ys, xs = np.where(mask)
    if len(xs) < 20:
        return {"angleDeg": None, "vector": [0.0, 0.0], "blackPixels": int(len(xs))}
    pts = np.column_stack([xs + x1, ys + y1]).astype(float)
    pts -= pts.mean(axis=0)
    cov = np.cov(pts, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    vx, vy = vecs[:, int(np.argmax(vals))]
    if vx > 0:
        vx, vy = -vx, -vy
    angle = math.degrees(math.atan2(vy, vx))
    return {"angleDeg": round(angle, 2), "vector": [round(float(vx), 4), round(float(vy), 4)], "blackPixels": int(len(xs))}


def row_hits_for_mark(mark: dict, rows: list[dict]) -> dict:
    x1, y1, x2, y2 = mark["box"]
    cx, cy = center(mark["box"])
    inside_rows = [r for r in rows if y1 <= r["y"] <= y2]
    closest_rows = sorted(rows, key=lambda r: abs(r["y"] - cy))[:4]

    horizontal = []
    for r in closest_rows:
        left_words = [w for w in r["words"] if w["box"][2] < x1]
        nearest = sorted(left_words, key=lambda w: x1 - w["box"][2])[-12:]
        horizontal.append(
            {
                "visualRow": r["visualRow"],
                "y": r["y"],
                "canonicalLineIndex": r["canonicalLineIndex"],
                "canonicalText": r["canonicalText"],
                "highlight": r["highlight"],
                "nearestLeftWords": " ".join(w["text"] for w in nearest),
            }
        )

    return {
        "insideRows": [
            {
                "visualRow": r["visualRow"],
                "y": r["y"],
                "canonicalLineIndex": r["canonicalLineIndex"],
                "canonicalText": r["canonicalText"],
                "highlight": r["highlight"],
            }
            for r in inside_rows
        ],
        "closestRows": [
            {
                "visualRow": r["visualRow"],
                "y": r["y"],
                "canonicalLineIndex": r["canonicalLineIndex"],
                "canonicalText": r["canonicalText"],
                "highlight": r["highlight"],
            }
            for r in closest_rows
        ],
        "horizontalLeftRows": horizontal,
    }


def ray_hits_for_mark(mark: dict, axis: dict, words: list[dict]) -> dict:
    cx, cy = center(mark["box"])
    vx, vy = axis["vector"]
    if vx == 0 and vy == 0:
        return {"leftAxisWords": [], "rightAxisWords": []}

    hits = {"leftAxisWords": [], "rightAxisWords": []}
    for direction, key in [(1, "leftAxisWords"), (-1, "rightAxisWords")]:
        ax, ay = cx, cy
        bx, by = cx + direction * vx * 1800, cy + direction * vy * 1800
        candidates = []
        for word in words:
            wx, wy = word["center"]
            # Projection along the directed ray.
            proj = (wx - ax) * (direction * vx) + (wy - ay) * (direction * vy)
            if proj <= 0:
                continue
            d = distance_to_segment(wx, wy, ax, ay, bx, by)
            if d <= 45:
                candidates.append((proj, d, word))
        candidates.sort(key=lambda t: t[0])
        hits[key] = [
            {
                "text": w["text"],
                "box": w["box"],
                "center": w["center"],
                "projection": round(float(proj), 2),
                "distance": round(float(d), 2),
            }
            for proj, d, w in candidates[:14]
        ]
    return hits


def draw_overlay(img: Image.Image, marks: list[dict], analyses: list[dict]) -> None:
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("Arial.ttf", 30)
    except Exception:
        font = ImageFont.load_default()

    for mark in marks:
        x1, y1, x2, y2 = mark["box"]
        idx = mark["index"]
        if idx in FALSE_POSITIVE_NOTES:
            color = (0, 190, 255, 230)
            label = f"M{idx} text/highlight"
        else:
            color = (255, 70, 0, 245)
            label = f"M{idx} true mark"
        draw.rectangle((x1, y1, x2, y2), outline=color, width=6)
        draw.text((x1, max(0, y1 - 35)), label, fill=color, font=font)

    for item in analyses:
        if item["classification"] != "standalone-mark":
            continue
        cx, cy = item["center"]
        vx, vy = item["axis"]["vector"]
        if vx == 0 and vy == 0:
            continue
        for mul, color in [(1400, (255, 70, 0, 210)), (-500, (150, 0, 255, 170))]:
            draw.line((cx, cy, cx + vx * mul, cy + vy * mul), fill=color, width=5)
        for row in item["rowHits"]["insideRows"]:
            y = row["y"]
            draw.line((350, y, 1680, y), fill=(255, 70, 0, 170), width=3)

    Image.alpha_composite(out, overlay).convert("RGB").save(OUT_IMG, quality=94)


def main() -> None:
    marks_data = json.loads(MARKS_JSON.read_text())
    marks = marks_data["marks"]
    words = load_page76_words()
    rows = visual_rows(words)
    img = upright_image(76)

    analyses = []
    for mark in marks:
        cx, cy = center(mark["box"])
        item = {
            "index": mark["index"],
            "box": mark["box"],
            "center": [round(cx, 2), round(cy, 2)],
            "classification": "text/highlight-false-positive"
            if mark["index"] in FALSE_POSITIVE_NOTES
            else "standalone-mark",
            "note": FALSE_POSITIVE_NOTES.get(mark["index"], ""),
        }
        if item["classification"] == "standalone-mark":
            axis = pca_axis(img, mark["box"])
            item["axis"] = axis
            item["rowHits"] = row_hits_for_mark(mark, rows)
            item["rayHits"] = ray_hits_for_mark(mark, axis, words)
        analyses.append(item)

    draw_overlay(img, marks, analyses)

    result = {
        "source": "high-res page 76 standalone lower-mark pointer audit",
        "inputMarks": str(MARKS_JSON),
        "overlay": str(OUT_IMG),
        "rowsUsed": [
            {
                "visualRow": r["visualRow"],
                "y": r["y"],
                "canonicalLineIndex": r["canonicalLineIndex"],
                "canonicalText": r["canonicalText"],
                "highlight": r["highlight"],
            }
            for r in rows
            if r["visualRow"] >= 20
        ],
        "analyses": analyses,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Lower Page 76 Mark Pointers",
        "",
        "Scope: retest the lower page-76 visual marks as a standalone pointer/order system. This separates highlighted text boxes from true non-text brush/X marks and uses high-res page geometry only.",
        "",
        f"- Source marks: `{MARKS_JSON}`",
        f"- Overlay: `{OUT_IMG}`",
        "",
        "## Classification",
        "",
    ]
    for item in analyses:
        if item["classification"] == "text/highlight-false-positive":
            lines.append(f"- M{item['index']}: false positive, {item['note']}")
        else:
            axis = item["axis"]
            inside = item["rowHits"]["insideRows"]
            inside_desc = "; ".join(
                f"L{r['canonicalLineIndex']} `{r['canonicalText']}`" + (f" [{r['highlight']}]" if r["highlight"] else "")
                for r in inside
            )
            lines.append(
                f"- M{item['index']}: standalone mark, box={item['box']}, center={item['center']}, "
                f"PCA angle={axis['angleDeg']} deg, rows crossed={inside_desc or 'none'}"
            )

    lines.extend(["", "## Pointer Reads", ""])
    for item in analyses:
        if item["classification"] != "standalone-mark":
            continue
        lines.append(f"### M{item['index']}")
        lines.append("")
        lines.append("- Horizontal left-row candidates:")
        for row in item["rowHits"]["horizontalLeftRows"]:
            text = row["canonicalText"] or row["ocrText"] if "ocrText" in row else row["canonicalText"]
            flag = f" [{row['highlight']}]" if row["highlight"] else ""
            lines.append(
                f"  - row {row['visualRow']} / L{row['canonicalLineIndex']}: `{text}`{flag}; nearest-left words `{row['nearestLeftWords']}`"
            )
        left_words = " ".join(w["text"] for w in item["rayHits"]["leftAxisWords"])
        right_words = " ".join(w["text"] for w in item["rayHits"]["rightAxisWords"])
        lines.append(f"- PCA-axis left/down read: `{left_words or '-'}`")
        lines.append(f"- PCA-axis opposite read: `{right_words or '-'}`")
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- M1 and M2 are not standalone symbols; they are the detected black/grey highlighted text around `$1 billion` and `Volcano Bonds`.",
            "- The true marks, M3 and M4, sit at the right/lower edge of the same El Salvador / Novogratz / shitcoiner corridor, so they reinforce the region selection.",
            "- They do not provide a clean independent order: horizontal reads return ordinary adjacent prose, and the principal-axis rays either hit no text or clipped normal words.",
            "- This closes the lower page-76 mark-as-pointer branch for now. Keep page 76 as the target surface, but the missing selector is still outside these lower brush/X marks.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
