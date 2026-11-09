#!/usr/bin/env python3
"""Test whether the page-76 OVERDOSE header acts as a ray origin.

This bounded geometry pass draws straight segments from the OVERDOSE header
center to the locked O4/B4/G5/O5 target centers and compares them with
segments to non-active page-76 highlight centers. It asks whether those rays
carry instruction-bearing words, uniquely traverse the active highlight
quartet, or improve the current OVERDOSE layout evidence.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/overdose_header_ray_fan_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_header_ray_fan_gate.json"
OUT_MD = OUT / "overdose_header_ray_fan_gate.md"
OUT_SHEET = OUT / "overdose_header_ray_fan_gate_sheet.jpg"

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


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def strict_hits(text: str) -> list[str]:
    hits: list[str] = []
    for term in STRICT_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", text, re.I):
            hits.append(term)
    return hits


def segment_intersects_rect(p0: list[float], p1: list[float], rect: list[float]) -> bool:
    """Liang-Barsky segment/rectangle intersection."""
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    t0 = 0.0
    t1 = 1.0
    for p, q in [
        (-dx, x0 - rect[0]),
        (dx, rect[2] - x0),
        (-dy, y0 - rect[1]),
        (dy, rect[3] - y0),
    ]:
        if p == 0:
            if q < 0:
                return False
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r
        else:
            if r < t0:
                return False
            if r < t1:
                t1 = r
    return True


def distance_to_segment(point: list[float], p0: list[float], p1: list[float]) -> float:
    px, py = point
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.hypot(px - x0, py - y0)
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / denom))
    cx = x0 + t * dx
    cy = y0 + t * dy
    return math.hypot(px - cx, py - cy)


def analyze_ray(
    origin: list[float],
    target: dict[str, Any],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    active_ids_by_highlight: dict[str, str],
) -> dict[str, Any]:
    target_center = target["center"]
    word_hits = []
    strict: set[str] = set()
    for word in words:
        if word.get("token") == "overdose":
            continue
        if not segment_intersects_rect(origin, target_center, word["box"]):
            continue
        dist = distance_to_segment(word["center"], origin, target_center)
        hits = strict_hits(word.get("text", ""))
        strict.update(hits)
        word_hits.append(
            {
                "id": word["id"],
                "index": word.get("index"),
                "text": word.get("text", ""),
                "importance": word.get("importance", 0),
                "centerDistanceToRayPx": round(dist, 2),
                "strictInstructionHits": hits,
            }
        )

    highlight_hits = []
    active_hit_ids: set[str] = set()
    for h in highlights:
        if not segment_intersects_rect(origin, target_center, h["box"]):
            continue
        active_id = active_ids_by_highlight.get(h["id"])
        if active_id:
            active_hit_ids.add(active_id)
        highlight_hits.append(
            {
                "id": h["id"],
                "kind": h["kind"],
                "activeTargetId": active_id,
                "centerDistanceToRayPx": round(distance_to_segment(center(h["box"]), origin, target_center), 2),
            }
        )

    target_hits = [
        h["activeTargetId"] for h in highlight_hits if h.get("activeTargetId")
    ]
    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetKind": target["kind"],
        "targetCenter": [round(target_center[0], 2), round(target_center[1], 2)],
        "rayLengthPx": round(math.hypot(target_center[0] - origin[0], target_center[1] - origin[1]), 2),
        "angleDegrees": round(math.degrees(math.atan2(target_center[1] - origin[1], target_center[0] - origin[0])), 3),
        "wordHitCount": len(word_hits),
        "focusWordHitCount": sum(1 for row in word_hits if row["importance"] >= 3),
        "wordPreview": " ".join(row["text"] for row in word_hits[:20]),
        "highlightHitCount": len(highlight_hits),
        "highlightHitIds": [row["id"] for row in highlight_hits],
        "activeHighlightHitCount": len(active_hit_ids),
        "activeHighlightHitIds": sorted(active_hit_ids),
        "activeTargetHitStream": "|".join(target_hits) or "-",
        "strictInstructionHits": sorted(strict),
        "strictInstructionHitCount": len(strict),
        "wordHits": word_hits,
        "highlightHits": highlight_hits,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [250, 100, 2380, 3065]
    scale = 0.43
    panel = page.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    right_w = 650
    header_h = 150
    sheet_w = margin * 3 + panel.width + right_w
    sheet_h = max(header_h + panel.height + margin, 1260)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 14, 19))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 24), "OVERDOSE Header Ray Fan Gate", fill=(242, 246, 250), font=title)
    draw.text(
        (margin, 65),
        "Segments from the page-76 OVERDOSE header center to active and non-active highlight centers.",
        fill=(178, 188, 199),
        font=normal,
    )

    s = result["summary"]
    chips = [
        ("active rays", s["activeRayCount"]),
        ("control rays", s["controlRayCount"]),
        ("active strict hits", s["activeStrictInstructionHitCount"]),
        ("control strict hits", s["controlStrictInstructionHitCount"]),
        ("active all-quartet rays", s["activeAllQuartetRayCount"]),
    ]
    x = margin
    y = 102
    for label, value in chips:
        draw.rectangle((x, y, x + 205, y + 42), fill=(25, 31, 39), outline=(50, 58, 70))
        draw.text((x + 9, y + 6), label, fill=(130, 145, 160), font=small)
        draw.text((x + 9, y + 23), str(value)[:22], fill=(232, 238, 245), font=mono)
        x += 217

    px0, py0 = margin, header_h
    sheet.paste(panel, (px0, py0))

    def sx(v: float) -> float:
        return px0 + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return py0 + (v - crop[1]) * scale

    origin = result["origin"]["center"]
    draw.ellipse((sx(origin[0]) - 6, sy(origin[1]) - 6, sx(origin[0]) + 6, sy(origin[1]) + 6), fill="#ffffff")
    draw.rectangle((sx(result["origin"]["box"][0]), sy(result["origin"]["box"][1]), sx(result["origin"]["box"][2]), sy(result["origin"]["box"][3])), outline="#ffffff", width=2)

    for ray in result["controlRays"]:
        tx, ty = ray["targetCenter"]
        draw.line((sx(origin[0]), sy(origin[1]), sx(tx), sy(ty)), fill="#596273", width=1)
    for ray in result["activeRays"]:
        tx, ty = ray["targetCenter"]
        color = "#ff9b2e" if "O" in ray["targetLabel"] else "#c5ccd6"
        draw.line((sx(origin[0]), sy(origin[1]), sx(tx), sy(ty)), fill=color, width=3)
        draw.ellipse((sx(tx) - 5, sy(ty) - 5, sx(tx) + 5, sy(ty) + 5), fill=color)
        draw.text((sx(tx) + 6, sy(ty) - 8), ray["targetId"], fill="#ffffff", font=small)

    rx = px0 + panel.width + margin
    ry = header_h
    draw.text((rx, ry), "Active Rays", fill=(242, 246, 250), font=normal)
    ry += 30
    for ray in result["activeRays"]:
        draw.rectangle((rx, ry, sheet_w - margin, ry + 102), fill=(21, 26, 34), outline=(48, 58, 70))
        draw.text((rx + 10, ry + 8), ray["targetLabel"], fill=(238, 243, 248), font=normal)
        lines = [
            f"angle {ray['angleDegrees']} len {ray['rayLengthPx']} words {ray['wordHitCount']}",
            f"highlights {ray['highlightHitCount']} active hits {ray['activeTargetHitStream']}",
            f"strict {ray['strictInstructionHitCount']} preview {ray['wordPreview'][:42] or '-'}",
        ]
        yy = ry + 34
        for line in lines:
            draw.text((rx + 14, yy), line[:78], fill=(196, 206, 217), font=mono)
            yy += 19
        ry += 116

    ry += 10
    draw.text((rx, ry), "Control Rays", fill=(242, 246, 250), font=normal)
    ry += 28
    for ray in result["controlRays"][:12]:
        line = (
            f"{ray['targetId']}: angle {ray['angleDegrees']} words {ray['wordHitCount']} "
            f"highlights {ray['highlightHitCount']} strict {ray['strictInstructionHitCount']}"
        )
        draw.text((rx + 8, ry), line[:82], fill=(178, 188, 199), font=small)
        ry += 18
        if ry > sheet_h - 40:
            break

    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    header = next(word for word in page["words"] if word.get("token") == "overdose")
    origin = header["center"]

    active_targets = []
    active_ids_by_highlight: dict[str, str] = {}
    for row in active["targets"]:
        target_center = center(row["box"])
        active_targets.append(
            {
                "id": row["id"],
                "label": row["label"],
                "kind": "active",
                "box": row["box"],
                "center": target_center,
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "visualState": row["visualState"],
            }
        )
        for h in page["highlights"]:
            hx, hy = center(h["box"])
            if row["box"][0] <= hx <= row["box"][2] and row["box"][1] <= hy <= row["box"][3]:
                active_ids_by_highlight[h["id"]] = row["id"]

    active_center_boxes = [row["box"] for row in active_targets]
    control_targets = []
    for h in page["highlights"]:
        h_center = center(h["box"])
        is_active = any(box[0] <= h_center[0] <= box[2] and box[1] <= h_center[1] <= box[3] for box in active_center_boxes)
        if is_active:
            continue
        control_targets.append(
            {
                "id": h["id"],
                "label": f"{h['kind']} {h['id']}",
                "kind": "non_active_highlight_control",
                "box": h["box"],
                "center": h_center,
            }
        )

    active_rays = [analyze_ray(origin, target, page["words"], page["highlights"], active_ids_by_highlight) for target in active_targets]
    control_rays = [analyze_ray(origin, target, page["words"], page["highlights"], active_ids_by_highlight) for target in control_targets]

    active_strict = sorted({hit for ray in active_rays for hit in ray["strictInstructionHits"]})
    control_strict = sorted({hit for ray in control_rays for hit in ray["strictInstructionHits"]})
    all_active_ids = sorted(row["id"] for row in active_targets)
    active_all_quartet = [
        ray for ray in active_rays if sorted(ray["activeHighlightHitIds"]) == all_active_ids
    ]
    summary = {
        "activeRayCount": len(active_rays),
        "controlRayCount": len(control_rays),
        "activeStrictInstructionHits": active_strict,
        "activeStrictInstructionHitCount": len(active_strict),
        "controlStrictInstructionHits": control_strict,
        "controlStrictInstructionHitCount": len(control_strict),
        "activeAllQuartetRayCount": len(active_all_quartet),
        "activeRayHighlightHitCounts": [ray["highlightHitCount"] for ray in active_rays],
        "controlRayHighlightHitCounts": [ray["highlightHitCount"] for ray in control_rays],
        "activeRayFocusWordCounts": [ray["focusWordHitCount"] for ray in active_rays],
        "controlRayFocusWordCounts": [ray["focusWordHitCount"] for ray in control_rays],
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": [
            "Draw straight rays from the page-76 OVERDOSE header center to O4/B4/G5/O5 target centers.",
            "Compare active rays with rays from the same origin to non-active page-76 highlight centers.",
            "Measure existing word/highlight intersections and strict instruction words only.",
            "No OCR, hashing, key derivation, private-key checks, seed/WIF checks, address checks, or broad candidate generation.",
        ],
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "articleMap": rel(ARTICLE_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "origin": {
            "wordId": header["id"],
            "text": header["text"],
            "box": header["box"],
            "center": [round(origin[0], 2), round(origin[1], 2)],
        },
        "summary": summary,
        "activeRays": active_rays,
        "controlRays": control_rays,
        "decision": {
            "overdoseHeaderRayFanAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": (
                "Keep OVERDOSE header ray geometry as a visual inspection aid only. Reopen only if a source/clue "
                "explicitly names rays, header origin, or a ray-based unit/order rule."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "outputs": {"json": rel(OUT_JSON), "markdown": rel(OUT_MD), "sheet": rel(OUT_SHEET)},
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# OVERDOSE Header Ray Fan Gate",
        "",
        "Scope: draw straight segments from the page-76 OVERDOSE header center to the locked O4/B4/G5/O5 target centers, then compare them with rays to non-active page-76 highlight centers. This pass only measures existing word/highlight intersections and strict instruction terms; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.",
        "",
        "## Summary",
        f"- active rays: `{summary['activeRayCount']}`",
        f"- control rays: `{summary['controlRayCount']}`",
        f"- active strict instruction hits: `{summary['activeStrictInstructionHitCount']}`",
        f"- control strict instruction hits: `{summary['controlStrictInstructionHitCount']}`",
        f"- active all-quartet rays: `{summary['activeAllQuartetRayCount']}`",
        f"- active ray highlight-hit counts: `{summary['activeRayHighlightHitCounts']}`",
        f"- control ray highlight-hit counts: `{summary['controlRayHighlightHitCounts']}`",
        f"- selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Active Rays",
        "",
        "| target | angle | words | focus words | highlights | active highlight stream | strict hits | preview |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for ray in active_rays:
        lines.append(
            "| {target} | {angle} | {words} | {focus} | {highlights} | {stream} | {strict} | {preview} |".format(
                target=ray["targetId"],
                angle=ray["angleDegrees"],
                words=ray["wordHitCount"],
                focus=ray["focusWordHitCount"],
                highlights=ray["highlightHitCount"],
                stream=ray["activeTargetHitStream"],
                strict=", ".join(ray["strictInstructionHits"]) or "-",
                preview=(ray["wordPreview"] or "-").replace("|", "/")[:80],
            )
        )
    lines.extend(["", "## Control Rays", ""])
    for ray in control_rays:
        lines.append(
            "- `{target}` angle `{angle}` words `{words}` focus `{focus}` highlights `{highlights}` strict `{strict}` preview `{preview}`".format(
                target=ray["targetId"],
                angle=ray["angleDegrees"],
                words=ray["wordHitCount"],
                focus=ray["focusWordHitCount"],
                highlights=ray["highlightHitCount"],
                strict=", ".join(ray["strictInstructionHits"]) or "-",
                preview=(ray["wordPreview"] or "-").replace("|", "/")[:100],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote OVERDOSE header rays as a selector.",
            "- Active rays do not traverse the full active quartet and do not produce strict instruction wording.",
            "- Control highlight rays are not worse in kind, so the ray fan is a visual aid rather than extraction permission.",
            "",
            "## Outputs",
            f"- JSON: `{rel(OUT_JSON)}`",
            f"- visual sheet: `{rel(OUT_SHEET)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
