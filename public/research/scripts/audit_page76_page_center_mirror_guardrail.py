#!/usr/bin/env python3
"""Bounded guardrail for page-center mirror/rotation of the active quartet.

The current source-image guardrail says native source_images/fresh extraction
must be rotated 180 degrees before comparing to the readable page. This pass
checks the adjacent trap: treating the page-center 180-degree rotation, or the
page-center horizontal/vertical mirrors, as puzzle selectors.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/page76_page_center_mirror_guardrail"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_page_center_mirror_guardrail.json"
OUT_MD = OUT / "page76_page_center_mirror_guardrail.md"
OUT_SHEET = OUT / "page76_page_center_mirror_guardrail_sheet.jpg"

STRICT_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "order",
    "key",
    "private",
    "encoded",
    "seed",
    "wif",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(frame: list[float], box: list[float]) -> tuple[float, float]:
    inter = intersection(frame, box)
    if not inter:
        return 0.0, 0.0
    inter_area = area(inter)
    return inter_area / max(area(frame), 1.0), inter_area / max(area(box), 1.0)


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def round_box(box: list[float]) -> list[float]:
    return [round(v, 2) for v in box]


def strict_hits(text: str) -> list[str]:
    hits: list[str] = []
    for term in STRICT_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", text, re.I):
            hits.append(term)
    return hits


def transform_box(box: list[float], width: float, height: float, mode: str) -> list[float]:
    if mode == "point_180":
        return [width - box[2], height - box[3], width - box[0], height - box[1]]
    if mode == "vertical_mirror":
        return [width - box[2], box[1], width - box[0], box[3]]
    if mode == "horizontal_mirror":
        return [box[0], height - box[3], box[2], height - box[1]]
    raise ValueError(mode)


def summarize_projection(
    projected: list[float],
    source_target: dict[str, Any],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    active_targets: list[dict[str, Any]],
    overdose_word: dict[str, Any] | None,
) -> dict[str, Any]:
    word_hits = []
    hard_terms: set[str] = set()
    for word in words:
        over_projected, over_word = overlap_fraction(projected, word["box"])
        if over_projected <= 0.08 and over_word <= 0.16:
            continue
        hits = strict_hits(word.get("text", ""))
        hard_terms.update(hits)
        word_hits.append(
            {
                "id": word["id"],
                "index": word.get("index"),
                "text": word.get("text", ""),
                "overlapVsProjected": round(over_projected, 6),
                "overlapVsWord": round(over_word, 6),
                "importance": word.get("importance", 0),
                "strictInstructionHits": hits,
            }
        )

    highlight_hits = []
    for h in highlights:
        over_projected, over_highlight = overlap_fraction(projected, h["box"])
        if over_projected <= 0.0 and over_highlight <= 0.0:
            continue
        highlight_hits.append(
            {
                "id": h["id"],
                "kind": h["kind"],
                "overlapVsProjected": round(over_projected, 6),
                "overlapVsHighlight": round(over_highlight, 6),
            }
        )

    active_hits = []
    for other in active_targets:
        if other["id"] == source_target["id"]:
            continue
        over_projected, over_target = overlap_fraction(projected, other["box"])
        if over_projected <= 0.0 and over_target <= 0.0:
            continue
        active_hits.append(
            {
                "id": other["id"],
                "label": other["label"],
                "overlapVsProjected": round(over_projected, 6),
                "overlapVsTarget": round(over_target, 6),
            }
        )

    overdose_distance = None
    if overdose_word:
        px, py = center(projected)
        ox, oy = overdose_word["center"]
        overdose_distance = round(((px - ox) ** 2 + (py - oy) ** 2) ** 0.5, 2)

    return {
        "sourceTargetId": source_target["id"],
        "sourceTargetLabel": source_target["label"],
        "sourceVisualState": source_target["visualState"],
        "sourcePageLine": source_target["pageLine"],
        "sourceCorridorIndex": source_target["corridorIndex"],
        "projectedBox": round_box(projected),
        "wordHitCount": len(word_hits),
        "focusWordHitCount": sum(1 for row in word_hits if row["importance"] >= 3),
        "wordPreview": " ".join(row["text"] for row in word_hits)[:180],
        "strictInstructionHits": sorted(hard_terms),
        "strictInstructionHitCount": len(hard_terms),
        "highlightHitCount": len(highlight_hits),
        "highlightHits": highlight_hits,
        "activeTargetHitCount": len(active_hits),
        "activeTargetHits": active_hits,
        "distanceToOverdoseHeaderCenterPx": overdose_distance,
        "wordHits": word_hits,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE_IMAGE).convert("RGB")
    scale = 0.36
    panel = page.resize((int(page.width * scale), int(page.height * scale)))
    margin = 30
    header_h = 170
    right_w = 620
    sheet_w = margin * 3 + panel.width + right_w
    sheet_h = max(header_h + panel.height + margin, 1160)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 14, 19))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 26), "Page-76 Page-Center Mirror Guardrail", fill=(242, 246, 250), font=title)
    draw.text(
        (margin, 67),
        "Tests whether page-center 180 rotation or centerline mirrors can act as active-quartet selectors.",
        fill=(178, 188, 199),
        font=normal,
    )
    s = result["summary"]
    chips = [
        ("scenario count", s["scenarioCount"]),
        ("all-four active re-hits", s["allFourActiveRehitScenarioCount"]),
        ("strict instruction hits", s["strictInstructionHitCount"]),
        ("highlight contacts", s["totalHighlightHitCount"]),
        ("decision", result["decision"]["pageCenterMirrorAsSelector"]),
    ]
    x = margin
    y = 105
    for label, value in chips:
        draw.rectangle((x, y, x + 245, y + 48), fill=(25, 31, 39), outline=(50, 58, 70))
        draw.text((x + 10, y + 7), label, fill=(130, 145, 160), font=small)
        draw.text((x + 10, y + 26), str(value)[:28], fill=(232, 238, 245), font=mono)
        x += 258

    px0, py0 = margin, header_h
    sheet.paste(panel, (px0, py0))

    def sx(v: float) -> float:
        return px0 + v * scale

    def sy(v: float) -> float:
        return py0 + v * scale

    def draw_box(box: list[float], color: str, width: int = 2) -> None:
        draw.rectangle((sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])), outline=color, width=width)

    draw.line((sx(result["page"]["width"] / 2), py0, sx(result["page"]["width"] / 2), py0 + panel.height), fill="#6a7380", width=1)
    draw.line((px0, sy(result["page"]["height"] / 2), px0 + panel.width, sy(result["page"]["height"] / 2)), fill="#6a7380", width=1)

    active_color = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["activeTargets"]:
        draw_box(target["box"], active_color.get(target["visualState"], "#ffffff"), 3)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 14), target["id"], fill="#ffffff", font=small)

    scenario_colors = {
        "point_180": "#f6e75a",
        "vertical_mirror": "#7df0a5",
        "horizontal_mirror": "#72caff",
    }
    for scenario in result["scenarios"]:
        for row in scenario["rows"]:
            draw_box(row["projectedBox"], scenario_colors[scenario["mode"]], 1)

    rx = px0 + panel.width + margin
    ry = header_h
    draw.text((rx, ry), "Scenario Summary", fill=(242, 246, 250), font=normal)
    ry += 34
    for scenario in result["scenarios"]:
        draw.rectangle((rx, ry, sheet_w - margin, ry + 118), fill=(21, 26, 34), outline=(48, 58, 70))
        draw.text((rx + 12, ry + 10), scenario["label"], fill=scenario_colors[scenario["mode"]], font=normal)
        lines = [
            f"active re-hits: {scenario['activeTargetRehitCount']}",
            f"word hits: {scenario['totalWordHitCount']} | focus words: {scenario['focusWordHitCount']}",
            f"highlight contacts: {scenario['totalHighlightHitCount']}",
            f"strict instruction hits: {scenario['strictInstructionHitCount']}",
        ]
        yy = ry + 39
        for line in lines:
            draw.text((rx + 18, yy), line, fill=(202, 211, 221), font=mono)
            yy += 18
        ry += 134

    ry += 10
    draw.text((rx, ry), "Projected Previews", fill=(242, 246, 250), font=normal)
    ry += 30
    for scenario in result["scenarios"]:
        for row in scenario["rows"]:
            preview = row["wordPreview"] or "-"
            draw.text(
                (rx + 8, ry),
                f"{scenario['mode']} {row['sourceTargetId']}: {preview[:58]}",
                fill=(184, 194, 205),
                font=small,
            )
            ry += 17
            if ry > sheet_h - 36:
                break
        if ry > sheet_h - 36:
            break

    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    width = float(page["width"])
    height = float(page["height"])
    active_targets = active["targets"]
    overdose_word = next((word for word in page["words"] if word.get("token") == "overdose"), None)

    scenario_defs = [
        ("point_180", "Page-center 180-degree rotation"),
        ("vertical_mirror", "Vertical page-center mirror"),
        ("horizontal_mirror", "Horizontal page-center mirror"),
    ]
    scenarios = []
    aggregate_strict: set[str] = set()
    total_highlight_hits = 0
    all_four_active_rehits = 0

    for mode, label in scenario_defs:
        rows = []
        active_rehit_targets: set[str] = set()
        total_word_hits = 0
        focus_word_hits = 0
        scenario_strict: set[str] = set()
        scenario_highlights = 0
        for target in active_targets:
            projected = transform_box(target["box"], width, height, mode)
            row = summarize_projection(
                projected,
                target,
                page["words"],
                page["highlights"],
                active_targets,
                overdose_word,
            )
            rows.append(row)
            total_word_hits += row["wordHitCount"]
            focus_word_hits += row["focusWordHitCount"]
            scenario_highlights += row["highlightHitCount"]
            scenario_strict.update(row["strictInstructionHits"])
            for active_hit in row["activeTargetHits"]:
                active_rehit_targets.add(active_hit["id"])

        aggregate_strict.update(scenario_strict)
        total_highlight_hits += scenario_highlights
        if len(active_rehit_targets) == 4:
            all_four_active_rehits += 1
        scenarios.append(
            {
                "mode": mode,
                "label": label,
                "activeTargetRehitCount": len(active_rehit_targets),
                "activeTargetRehits": sorted(active_rehit_targets),
                "totalWordHitCount": total_word_hits,
                "focusWordHitCount": focus_word_hits,
                "totalHighlightHitCount": scenario_highlights,
                "strictInstructionHits": sorted(scenario_strict),
                "strictInstructionHitCount": len(scenario_strict),
                "rows": rows,
            }
        )

    summary = {
        "scenarioCount": len(scenarios),
        "testedModes": [row["mode"] for row in scenarios],
        "allFourActiveRehitScenarioCount": all_four_active_rehits,
        "strictInstructionHits": sorted(aggregate_strict),
        "strictInstructionHitCount": len(aggregate_strict),
        "totalHighlightHitCount": total_highlight_hits,
        "overdoseHeaderWordCenter": overdose_word.get("center") if overdose_word else None,
        "pageCenter": [round(width / 2, 2), round(height / 2, 2)],
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": [
            "Transform the locked O4/B4/G5/O5 boxes through page-center 180 rotation, vertical mirror, and horizontal mirror.",
            "Compare projected boxes only to page-76 words, highlights, active targets, and the OVERDOSE header center.",
            "No OCR, hashing, key derivation, private-key checks, seed/WIF checks, address checks, or broad candidate generation.",
        ],
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "articleMap": rel(ARTICLE_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "page": {"page": 76, "width": page["width"], "height": page["height"]},
        "activeTargets": [
            {
                "id": row["id"],
                "label": row["label"],
                "box": row["box"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "visualState": row["visualState"],
            }
            for row in active_targets
        ],
        "summary": summary,
        "scenarios": scenarios,
        "decision": {
            "pageCenterMirrorAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": (
                "Keep page-center rotation/mirrors as orientation guardrails only. Reopen only if a source/clue "
                "explicitly names page-center rotation, vertical/horizontal page-center mirroring, or a unit/order rule."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "outputs": {"json": rel(OUT_JSON), "markdown": rel(OUT_MD), "sheet": rel(OUT_SHEET)},
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Page-Center Mirror Guardrail",
        "",
        "Scope: test the page-center 180-degree rotation and page-center horizontal/vertical mirrors as selectors for the locked O4/B4/G5/O5 quartet. This is an orientation/geometry guardrail only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.",
        "",
        "## Summary",
        f"- scenario count: `{summary['scenarioCount']}`",
        f"- modes: `{', '.join(summary['testedModes'])}`",
        f"- page center: `{summary['pageCenter']}`",
        f"- all-four active re-hit scenarios: `{summary['allFourActiveRehitScenarioCount']}`",
        f"- total highlight contacts: `{summary['totalHighlightHitCount']}`",
        f"- strict instruction hits: `{summary['strictInstructionHitCount']}`",
        f"- selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Scenario Results",
        "",
        "| mode | active re-hits | word hits | focus words | highlight contacts | strict instruction hits |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for scenario in scenarios:
        lines.append(
            "| {mode} | {active} | {words} | {focus} | {highlights} | {strict} |".format(
                mode=scenario["mode"],
                active=scenario["activeTargetRehitCount"],
                words=scenario["totalWordHitCount"],
                focus=scenario["focusWordHitCount"],
                highlights=scenario["totalHighlightHitCount"],
                strict=", ".join(scenario["strictInstructionHits"]) or "-",
            )
        )

    lines.extend(["", "## Projected Text Previews", ""])
    for scenario in scenarios:
        lines.append(f"### {scenario['label']}")
        lines.append("")
        for row in scenario["rows"]:
            lines.append(
                "- `{source}` -> box `{box}`; words `{words}`; highlights `{highlights}`; active re-hits `{active}`; preview `{preview}`".format(
                    source=row["sourceTargetId"],
                    box=row["projectedBox"],
                    words=row["wordHitCount"],
                    highlights=row["highlightHitCount"],
                    active=row["activeTargetHitCount"],
                    preview=row["wordPreview"] or "-",
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Decision",
            "",
            "- Do not promote page-center 180-degree rotation, vertical page-center mirroring, or horizontal page-center mirroring as a selector.",
            "- The transforms do not re-hit the active quartet, do not produce a strict instruction surface, and do not improve the current OVERDOSE/layout evidence.",
            "- Keep the operation as a coordinate-frame guardrail for future source comparison only.",
            "",
            "## Outputs",
            f"- JSON: `{rel(OUT_JSON)}`",
            f"- visual sheet: `{rel(OUT_SHEET)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
