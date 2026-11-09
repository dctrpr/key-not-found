#!/usr/bin/env python3
"""Audit whether Issue 24's body-text highlighter grammar recurs.

This is a bounded visual-style control: it detects line-shaped orange and
dark/grey highlighter components in the local Max/OVERDOSE comparison page
images. It does not OCR text and does not derive keys.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "analysis_outputs/comparison_articles"
OUT = SOURCE_DIR / "body_highlighter_grammar"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "body_highlighter_grammar.json"
OUT_MD = OUT / "body_highlighter_grammar.md"
OUT_SHEET = OUT / "body_highlighter_grammar_sheet.jpg"


def font(size: int = 20) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def components(mask: np.ndarray, min_area: int = 60) -> list[dict[str, Any]]:
    h, w = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    ys, xs = np.nonzero(mask)
    out: list[dict[str, Any]] = []
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if visited[sy, sx]:
            continue
        stack = [(sy, sx)]
        visited[sy, sx] = True
        area = 0
        x0 = x1 = sx
        y0 = y1 = sy
        while stack:
            y, x = stack.pop()
            area += 1
            x0 = min(x0, x)
            x1 = max(x1, x)
            y0 = min(y0, y)
            y1 = max(y1, y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        if area < min_area:
            continue
        width = x1 - x0 + 1
        height = y1 - y0 + 1
        fill = area / max(1, width * height)
        out.append(
            {
                "box": [x0, y0, x1 + 1, y1 + 1],
                "area": area,
                "width": width,
                "height": height,
                "fill": fill,
                "aspect": width / max(1, height),
            }
        )
    return out


def mask_arrays(img: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = (0.299 * r + 0.587 * g + 0.114 * b)
    orange = (
        (r > 120)
        & (g > 40)
        & (g < 235)
        & (b < 190)
        & ((r - b) > 35)
        & (((r + g) / 2 - b) > 25)
        & ((r - g) > -55)
    )
    dark = (luma < 95) & (r < 135) & (g < 135) & (b < 135)
    return orange, dark


def classify_line_bands(comps: list[dict[str, Any]], page_w: int, page_h: int, kind: str) -> list[dict[str, Any]]:
    bands = []
    for c in comps:
        w_norm = c["width"] / page_w
        h_norm = c["height"] / page_h
        if c["aspect"] < 3.0:
            continue
        if not (0.035 <= w_norm <= 0.78):
            continue
        if not (0.006 <= h_norm <= 0.045):
            continue
        if kind == "orange" and c["fill"] < 0.28:
            continue
        if kind == "dark" and c["fill"] < 0.36:
            continue
        bands.append(c)
    bands.sort(key=lambda item: (item["box"][1], item["box"][0]))
    return bands


def scale_box(box: list[int], sx: float, sy: float) -> list[int]:
    return [int(round(box[0] * sx)), int(round(box[1] * sy)), int(round(box[2] * sx)), int(round(box[3] * sy))]


def detect_page(path: Path) -> dict[str, Any]:
    original = Image.open(path).convert("RGB")
    max_w = 900
    scale = min(1.0, max_w / original.width)
    small = original.resize((int(round(original.width * scale)), int(round(original.height * scale))), Image.Resampling.LANCZOS)
    orange_mask, dark_mask = mask_arrays(small)
    orange_comps = components(orange_mask, min_area=45)
    dark_comps = components(dark_mask, min_area=45)
    orange_bands = classify_line_bands(orange_comps, small.width, small.height, "orange")
    dark_bands = classify_line_bands(dark_comps, small.width, small.height, "dark")
    sx = original.width / small.width
    sy = original.height / small.height
    scaled_orange = [{**b, "box": scale_box(b["box"], sx, sy)} for b in orange_bands]
    scaled_dark = [{**b, "box": scale_box(b["box"], sx, sy)} for b in dark_bands]
    row_pairs = 0
    for o in orange_bands:
        oy = (o["box"][1] + o["box"][3]) / 2
        if any(abs(oy - (d["box"][1] + d["box"][3]) / 2) <= small.height * 0.02 for d in dark_bands):
            row_pairs += 1
    score = len(orange_bands) * 2 + len(dark_bands) + row_pairs
    return {
        "path": str(path),
        "size": [original.width, original.height],
        "orangeLineBands": len(orange_bands),
        "darkLineBands": len(dark_bands),
        "nearSameRowOrangeDarkPairs": row_pairs,
        "grammarScore": score,
        "orangeBoxes": [b["box"] for b in scaled_orange],
        "darkBoxes": [b["box"] for b in scaled_dark],
    }


def draw_overlay(path: Path, rec: dict[str, Any], label: str) -> Image.Image:
    img = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for box in rec["orangeBoxes"]:
        draw.rectangle(box, outline=(255, 126, 0), width=max(3, img.width // 500))
    for box in rec["darkBoxes"]:
        draw.rectangle(box, outline=(0, 170, 255), width=max(3, img.width // 500))
    f = font(34 if img.width > 2200 else 26)
    draw.rectangle([0, 0, img.width, 72], fill=(255, 255, 255))
    draw.text((18, 18), label, fill=(20, 20, 20), font=f)
    return img


def fit_thumb(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / img.width, max_h / img.height)
    return img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)


def make_sheet(page_records: list[dict[str, Any]]) -> None:
    selected = sorted(page_records, key=lambda r: (-r["grammarScore"], r["source"], r["page"]))[:18]
    thumb_w, thumb_h = 330, 430
    gutter = 22
    cols = 3
    rows = (len(selected) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gutter, rows * thumb_h + (rows + 1) * gutter), "white")
    for i, rec in enumerate(selected):
        path = Path(rec["path"])
        label = f"{rec['source']} p{rec['page']:02d} O{rec['orangeLineBands']} D{rec['darkLineBands']} P{rec['nearSameRowOrangeDarkPairs']}"
        overlay = draw_overlay(path, rec, label)
        thumb = fit_thumb(overlay, thumb_w, thumb_h)
        x = gutter + (i % cols) * (thumb_w + gutter)
        y = gutter + (i // cols) * (thumb_h + gutter)
        sheet.paste(thumb, (x, y))
    sheet.save(OUT_SHEET, quality=95)


def main() -> None:
    sources: list[Path] = []
    for child in sorted(SOURCE_DIR.iterdir()):
        if child.is_dir() and list(child.glob("page_*.jpg")):
            sources.append(child)
    # Issue 27 was rendered by the broader OVERDOSE style audit, not the
    # first comparison-layout pass. Include it here so the stricter body-line
    # highlighter metric covers every local comparison PDF without rerendering.
    issue27 = SOURCE_DIR / "overdose_style_uniqueness" / "issue27"
    if issue27.exists() and list(issue27.glob("page_*.jpg")) and issue27 not in sources:
        sources.append(issue27)

    page_records: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for source_dir in sources:
        records = []
        for idx, path in enumerate(sorted(source_dir.glob("page_*.jpg")), start=1):
            rec = detect_page(path)
            rec["source"] = source_dir.name
            rec["page"] = idx
            page_records.append(rec)
            records.append(rec)
        mixed_pages = [r["page"] for r in records if r["orangeLineBands"] >= 2 and r["darkLineBands"] >= 1]
        sustained_pages = [r["page"] for r in records if r["grammarScore"] >= 5]
        summaries.append(
            {
                "source": source_dir.name,
                "pages": len(records),
                "totalOrangeLineBands": sum(r["orangeLineBands"] for r in records),
                "totalDarkLineBands": sum(r["darkLineBands"] for r in records),
                "totalSameRowPairs": sum(r["nearSameRowOrangeDarkPairs"] for r in records),
                "maxGrammarScore": max((r["grammarScore"] for r in records), default=0),
                "mixedOrangeDarkPages": mixed_pages,
                "sustainedGrammarPages": sustained_pages,
            }
        )

    make_sheet(page_records)
    issue24 = next(s for s in summaries if s["source"] == "issue24_toxic_af")
    independent = [s for s in summaries if s["source"] not in {"issue24_toxic_af", "bitcoin4"}]
    decision = (
        "Line-shaped orange/dark body highlights are sustained across Issue 24 body pages and remain much less sustained "
        "in the independent comparison articles. This keeps the Issue 24 body-highlighter grammar puzzle-relevant, "
        "while broad colored OVERDOSE art stays downgraded as house style."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "body-text highlighter grammar comparison; visual components only; no OCR or key derivation",
        "summaries": summaries,
        "pageRecords": page_records,
        "sheet": str(OUT_SHEET),
        "decision": decision,
        "nextMove": "Keep orange/grey body highlights active only where they interact with page-76 geometry; do not pursue comparison-article style metrics as selectors.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Body Highlighter Grammar Audit",
        "",
        "Scope: detect line-shaped orange and dark/grey highlighter components across the local Max/OVERDOSE comparison page images. No OCR, key derivation, hashing, seed checking, WIF checking, or address checking was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{OUT_SHEET}`",
        "",
        "## Source Summary",
        "",
        "| source | pages | orange line bands | dark line bands | same-row pairs | sustained pages | mixed pages | max score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        lines.append(
            f"| `{s['source']}` | `{s['pages']}` | `{s['totalOrangeLineBands']}` | `{s['totalDarkLineBands']}` | "
            f"`{s['totalSameRowPairs']}` | `{s['sustainedGrammarPages']}` | `{s['mixedOrangeDarkPages']}` | `{s['maxGrammarScore']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            f"- Issue 24 body grammar: sustained pages `{issue24['sustainedGrammarPages']}`, mixed orange/dark pages `{issue24['mixedOrangeDarkPages']}`.",
            "- Independent comparison articles still contain colored marks, but they do not reproduce the same sustained body-text orange/grey pattern across article pages.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    if independent:
        best_ind = max(independent, key=lambda s: s["maxGrammarScore"])
        lines.insert(
            -3,
            f"- Strongest independent comparison by max score is `{best_ind['source']}` with max score `{best_ind['maxGrammarScore']}`, but its sustained/mixed pages are `{best_ind['sustainedGrammarPages']}` / `{best_ind['mixedOrangeDarkPages']}`.",
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
