#!/usr/bin/env python3
"""Word-level audit of the strongest registered 76/79 line alignment."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_registered_76_79_selector import BEST_TRANSFORM, center, intersection, transform_box
from analyze_highres_page76_mirror_selector import hflip_box
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REGISTERED = ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json"
RUNS = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
OUT_MD = ROOT / "analysis_outputs/source_audit/registered_76_79_word_alignment.md"
OUT_JSON = ROOT / "analysis_outputs/source_audit/registered_76_79_word_alignment.json"
OUT_IMG = ROOT / "analysis_outputs/source_audit/registered_76_79_word_alignment.jpg"


def area(box: list[float] | tuple[float, ...]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_area(a: list[float] | tuple[float, ...], b: list[float] | tuple[float, ...]) -> float:
    inter = intersection(a, b)
    return area(inter) if inter else 0.0


def words_for_page(article_map: dict, page: int) -> list[dict]:
    for row in article_map["pages"]:
        if row["page"] == page:
            return row.get("words", [])
    raise ValueError(f"page {page} not found")


def word_records_in_box(words: list[dict], box: list[float]) -> list[dict]:
    return [w for w in words if overlap_area(w["box"], box) > 0]


def transform_word(word: dict, page_width: int, page_height: int) -> dict:
    hflipped = hflip_box(word["box"], page_width)
    mapped = transform_box(tuple(int(round(v)) for v in hflipped), page_width, page_height, BEST_TRANSFORM)
    return {
        "index": word["index"],
        "text": word["text"],
        "token": word.get("token", ""),
        "sourceBox": word["box"],
        "hflipBox": hflipped,
        "mappedBox": mapped,
        "mappedCenter": center(mapped),
    }


def nearest_pairs(sources: list[dict], targets: list[dict]) -> list[dict]:
    rows = []
    for src in sources:
        ranked = []
        for tgt in targets:
            sc = center(src["mappedBox"])
            tc = center(tgt["box"])
            dist = math.hypot(sc[0] - tc[0], sc[1] - tc[1])
            ranked.append((dist, tgt))
        if not ranked:
            continue
        dist, tgt = min(ranked, key=lambda item: item[0])
        rows.append(
            {
                "source": src["text"],
                "target": tgt["text"],
                "distance": round(dist, 1),
                "sourceCenter": [round(v, 1) for v in center(src["mappedBox"])],
                "targetCenter": [round(v, 1) for v in center(tgt["box"])],
            }
        )
    return rows


def direct_word_overlaps(sources: list[dict], targets: list[dict]) -> list[dict]:
    rows = []
    for src in sources:
        for tgt in targets:
            ia = overlap_area(src["mappedBox"], tgt["box"])
            if ia <= 0:
                continue
            rows.append(
                {
                    "source": src["text"],
                    "target": tgt["text"],
                    "overlapArea": round(ia, 1),
                    "overlapVsSource": round(ia / max(1.0, area(src["mappedBox"])), 4),
                    "overlapVsTarget": round(ia / max(1.0, area(tgt["box"])), 4),
                }
            )
    rows.sort(key=lambda row: row["overlapArea"], reverse=True)
    return rows


def group_rows(records: list[dict], box_key: str) -> list[dict]:
    buckets: list[list[dict]] = []
    for rec in sorted(records, key=lambda r: center(r[box_key])[1]):
        cy = center(rec[box_key])[1]
        for bucket in buckets:
            if abs(center(bucket[0][box_key])[1] - cy) < 45:
                bucket.append(rec)
                break
        else:
            buckets.append([rec])
    out = []
    for bucket in buckets:
        bucket.sort(key=lambda r: center(r[box_key])[0])
        out.append(
            {
                "y": round(sum(center(r[box_key])[1] for r in bucket) / len(bucket), 1),
                "words": [r["text"] for r in bucket],
                "text": " ".join(r["text"] for r in bucket),
            }
        )
    return out


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def variant_name(run: dict) -> str:
    font = run.get("fontAscii") or ""
    if font == "Typeka Mix":
        return "MIX"
    if font == "Typeka" and run.get("bold"):
        return "TYPEKA_BOLD"
    if font == "Typeka":
        return "TYPEKA"
    return font or "OTHER"


def page_for_para(paragraph_index: int, boundaries: list[dict]) -> int | None:
    for row in boundaries:
        if row["paragraphStart"] <= paragraph_index <= row["paragraphEnd"]:
            return row["page"]
    return None


def relevant_docm_runs() -> dict:
    runs = json.loads(RUNS.read_text())
    boundaries = json.loads(FONT_AUDIT.read_text())["pageBoundariesByParagraph"]
    source = []
    target = []
    for run in runs:
        page = page_for_para(run["paragraphIndex"], boundaries)
        text = clean(run["text"])
        if not text:
            continue
        row = {
            "runIndex": run["runIndex"],
            "page": page,
            "text": text,
            "variant": variant_name(run),
            "highlight": run.get("highlight"),
            "bold": bool(run.get("bold")),
        }
        if page == 79 and run.get("highlight") == "yellow" and (
            "infinitely more efficient" in text or "to transact" in text or "or gold" in text
        ):
            source.append(row)
        if page == 76 and run.get("highlight") == "black" and (
            "Gotta be this way" in text or text == "nonsense"
        ):
            target.append(row)
    return {"sourceP79": source, "targetP76": target}


def draw_overlay(target_words: list[dict], source_words: list[dict], target_boxes: list[list[float]]) -> None:
    img = upright_image(76).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for box in target_boxes:
        draw.rectangle(tuple(int(round(v)) for v in box), outline=(0, 210, 255, 255), width=5)
    for tgt in target_words:
        draw.rectangle(tuple(int(round(v)) for v in tgt["box"]), outline=(0, 170, 220, 220), width=3)
    for src in source_words:
        draw.rectangle(tuple(int(round(v)) for v in src["mappedBox"]), outline=(190, 0, 255, 220), width=3)
        x, y = src["mappedBox"][0], src["mappedBox"][1]
        draw.text((x, max(0, y - 18)), src["text"][:12], fill=(190, 0, 255, 255))
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.crop((350, 690, 2200, 1020)).save(OUT_IMG, quality=94)


def main() -> None:
    article_map = json.loads(ARTICLE_MAP.read_text())
    registered = json.loads(REGISTERED.read_text())
    page_width, page_height = 2544, 3264

    source = next(item for item in registered["registeredSources"] if item["index"] == 1)
    target_b1 = next(item for item in registered["targetGrey"] if item["index"] == 1)
    target_b2 = next(item for item in registered["targetGrey"] if item["index"] == 2)

    p79_words = word_records_in_box(words_for_page(article_map, 79), source["sourceBox"])
    p76_words = [
        *word_records_in_box(words_for_page(article_map, 76), target_b1["box"]),
        *word_records_in_box(words_for_page(article_map, 76), target_b2["box"]),
    ]
    transformed = [transform_word(word, page_width, page_height) for word in p79_words]
    overlaps = direct_word_overlaps(transformed, p76_words)
    nearest = nearest_pairs(transformed, p76_words)
    source_rows = group_rows(transformed, "mappedBox")
    target_rows = group_rows(p76_words, "box")
    docm = relevant_docm_runs()

    source_variants = Counter(row["variant"] for row in docm["sourceP79"])
    target_variants = Counter(row["variant"] for row in docm["targetP76"])
    source_highlights = Counter(row["highlight"] for row in docm["sourceP79"])
    target_highlights = Counter(row["highlight"] for row in docm["targetP76"])

    draw_overlay(p76_words, transformed, [target_b1["box"], target_b2["box"]])

    result = {
        "source": "registered 76/79 line alignment; OCR words used only as approximate labels",
        "transform": BEST_TRANSFORM,
        "sourceHighlight": source,
        "targetHighlights": [target_b1, target_b2],
        "sourceWords": transformed,
        "targetWords": p76_words,
        "directWordOverlaps": overlaps,
        "nearestPairs": nearest,
        "sourceRowsAfterTransform": source_rows,
        "targetRows": target_rows,
        "docmRuns": docm,
        "summary": {
            "sourceWordCount": len(transformed),
            "targetWordCount": len(p76_words),
            "directWordOverlapCount": len(overlaps),
            "sourceVariantCounts": dict(source_variants),
            "targetVariantCounts": dict(target_variants),
            "sourceHighlightCounts": dict(source_highlights),
            "targetHighlightCounts": dict(target_highlights),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Registered 76/79 Word Alignment Audit",
        "",
        "Scope: inspect the strongest registered 76/79 line pair at word level. OCR word boxes are used only as approximate labels after the high-res visual registration. No key derivation was run.",
        "",
        f"- Source p79 highlight: `{source['label']}`",
        f"- Target p76 highlights: `B1 {target_b1['label']}` + `B2 {target_b2['label']}`",
        f"- Overlay crop: `{OUT_IMG}`",
        "",
        "## Word-Level Geometry",
        "",
        f"- Source OCR words inside p79 highlight: {len(transformed)}",
        f"- Target OCR words inside p76 B1/B2: {len(p76_words)}",
        f"- Direct transformed-word overlaps: {len(overlaps)}",
    ]
    if overlaps:
        for row in overlaps[:12]:
            md.append(
                f"  - `{row['source']}` -> `{row['target']}` "
                f"(source={row['overlapVsSource']:.3f}, target={row['overlapVsTarget']:.3f})"
            )
    else:
        md.append("  - None. The alignment is box/line-level, not word-box-level.")
    md.extend(["", "## Row Structure", ""])
    md.append("- Transformed p79 source rows:")
    for row in source_rows:
        md.append(f"  - y={row['y']}: `{row['text']}`")
    md.append("- p76 target rows:")
    for row in target_rows:
        md.append(f"  - y={row['y']}: `{row['text']}`")
    md.extend(["", "## Nearest Word Pairs", ""])
    for row in nearest[:16]:
        md.append(f"- `{row['source']}` -> `{row['target']}` dist={row['distance']}")
    md.extend(["", "## DOCM Font/Highlight State", ""])
    md.append(f"- p79 source run variants: `{dict(source_variants)}` highlights: `{dict(source_highlights)}`")
    md.append(f"- p76 target run variants: `{dict(target_variants)}` highlights: `{dict(target_highlights)}`")
    md.append("- Relevant DOCM runs:")
    for group_name, rows in docm.items():
        md.append(f"  - {group_name}:")
        for row in rows:
            md.append(
                f"    - run {row['runIndex']} p{row['page']} `{row['text']}` "
                f"variant={row['variant']} highlight={row['highlight']} bold={row['bold']}"
            )
    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The strong 76/79 match is a real line/highlight-block alignment, but it does not resolve to word-level intersections under the current high-res transform.",
            "- The nearest word pairs are positional neighbors only; they do not form readable instruction text or an obvious ordered selector.",
            "- Both sides of the aligned pair are `TYPEKA_BOLD`; the source is yellow/orange highlight and the target is black/grey highlight. `Typeka Mix` is absent from this local anchor.",
            "- This rules out the simple local rule “use the registered 76/79 line pair to pick overlapping words or Typeka Mix words.”",
            "- Next best move: inspect line offsets around this anchor, especially whether the target row intentionally sits between transformed p79 source rows, or shift to the original Canva/source clue for a missing alignment instruction.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
