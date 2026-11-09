#!/usr/bin/env python3
"""Refined front/back leaf registration audit.

This is a constrained follow-up to the raw hold-to-light sheet. It uses the
high-resolution scan as geometry truth, mirrors orange highlight boxes through
physical leaves, allows only a small x/y crop correction, and measures whether
those source boxes land cleanly on manually verified orange/grey target spans.
No text hashing or key generation is performed.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)

MANUAL_ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
MANUAL_GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
OUT_JSON = OUT / "front_back_leaf_box_registration.json"
OUT_MD = OUT / "front_back_leaf_box_registration.md"
OUT_IMG = OUT / "front_back_leaf_box_registration_sheet.jpg"

LEAF_DIRECTIONS = [(75, 76), (76, 75), (77, 78), (78, 77), (79, 80), (80, 79)]
GRID_RANGE = range(-180, 181, 20)


def area(box: tuple[float, float, float, float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> tuple[float, float, float, float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def hflip_box(box: tuple[float, float, float, float], width: int) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def translate_box(box: tuple[float, float, float, float], dx: float, dy: float) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    return (x1 + dx, y1 + dy, x2 + dx, y2 + dy)


def labels_for_orange(page: int) -> list[str]:
    data = json.loads(MANUAL_ORANGE.read_text())
    prefix = f"p{page}_orange_"
    numbered: list[tuple[int, str]] = []
    for key, text in data["visualOrangeBoxes"].items():
        if key.startswith(prefix):
            numbered.append((int(key.rsplit("_", 1)[1]), text))
    return [text for _, text in sorted(numbered)]


def orange_items(page: int) -> list[dict]:
    labels = labels_for_orange(page)
    boxes, _ = orange_boxes(page)
    items = []
    for idx, box in enumerate(boxes, 1):
        label = labels[idx - 1] if idx - 1 < len(labels) else f"orange {idx}"
        items.append(
            {
                "kind": "orange",
                "page": page,
                "index": idx,
                "id": f"p{page}_orange_{idx}",
                "box": tuple(float(v) for v in box),
                "label": label,
            }
        )
    return items


def grey_items(page: int) -> list[dict]:
    data = json.loads(MANUAL_GREY.read_text())
    rows = [row for row in data["rows"] if row["page"] == page]
    rows.sort(key=lambda row: row["id"])
    items = []
    for idx, row in enumerate(rows, 1):
        items.append(
            {
                "kind": "grey",
                "page": page,
                "index": idx,
                "id": row["id"],
                "box": tuple(float(v) for v in row["highresBox"]),
                "label": row["expected"],
            }
        )
    return items


def target_items(page: int) -> list[dict]:
    return orange_items(page) + grey_items(page)


def edge_score(mapped_source: dict, target: dict) -> dict | None:
    inter = intersection(mapped_source["mappedBox"], target["box"])
    if not inter:
        return None
    ia = area(inter)
    if ia <= 0:
        return None
    ca = center(mapped_source["mappedBox"])
    cb = center(target["box"])
    return {
        "sourcePage": mapped_source["page"],
        "sourceIndex": mapped_source["index"],
        "sourceId": mapped_source["id"],
        "sourceLabel": mapped_source["label"],
        "sourceBox": mapped_source["sourceBox"],
        "hflipBox": mapped_source["hflipBox"],
        "mappedBox": mapped_source["mappedBox"],
        "targetPage": target["page"],
        "targetKind": target["kind"],
        "targetIndex": target["index"],
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetBox": target["box"],
        "intersection": inter,
        "overlapArea": round(ia, 2),
        "overlapVsSource": round(ia / area(mapped_source["mappedBox"]), 5),
        "overlapVsTarget": round(ia / area(target["box"]), 5),
        "centerDistance": round(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5, 2),
    }


def meaningful_edges(mapped_sources: list[dict], targets: list[dict]) -> list[dict]:
    edges: list[dict] = []
    for src in mapped_sources:
        for target in targets:
            edge = edge_score(src, target)
            if not edge:
                continue
            if edge["overlapVsSource"] >= 0.05 or edge["overlapVsTarget"] >= 0.05:
                edges.append(edge)
    edges.sort(
        key=lambda e: (
            -max(e["overlapVsSource"], e["overlapVsTarget"]),
            e["targetKind"],
            e["targetIndex"],
            e["sourceIndex"],
        )
    )
    return edges


def score_direction(source_items: list[dict], targets: list[dict], width: int, dx: int, dy: int) -> tuple[float, list[dict], list[dict]]:
    mapped_sources = []
    for item in source_items:
        flipped = hflip_box(item["box"], width)
        mapped_sources.append(
            {
                **item,
                "sourceBox": item["box"],
                "hflipBox": flipped,
                "mappedBox": translate_box(flipped, dx, dy),
            }
        )
    edges = meaningful_edges(mapped_sources, targets)
    # Prefer compact, repeated overlap but penalize large arbitrary translations.
    overlap_score = sum(max(edge["overlapVsSource"], edge["overlapVsTarget"]) for edge in edges)
    distance_penalty = (abs(dx) + abs(dy)) / 1500.0
    score = overlap_score + 0.15 * len(edges) - distance_penalty
    return score, mapped_sources, edges


def audit_direction(source_page: int, target_page: int) -> dict:
    page_img = upright_image(target_page)
    width = page_img.width
    sources = orange_items(source_page)
    targets = target_items(target_page)

    best = None
    raw_score, raw_sources, raw_edges = score_direction(sources, targets, width, 0, 0)
    for dx in GRID_RANGE:
        for dy in GRID_RANGE:
            score, mapped_sources, edges = score_direction(sources, targets, width, dx, dy)
            candidate = {
                "dx": dx,
                "dy": dy,
                "score": round(score, 5),
                "mappedSources": mapped_sources,
                "meaningfulEdges": edges,
            }
            if best is None:
                best = candidate
                continue
            if (candidate["score"], -abs(dx) - abs(dy), len(edges)) > (
                best["score"],
                -abs(best["dx"]) - abs(best["dy"]),
                len(best["meaningfulEdges"]),
            ):
                best = candidate

    assert best is not None
    raw = {
        "dx": 0,
        "dy": 0,
        "score": round(raw_score, 5),
        "mappedSources": raw_sources,
        "meaningfulEdges": raw_edges,
    }
    return {
        "sourcePage": source_page,
        "targetPage": target_page,
        "sourceCount": len(sources),
        "targetCount": len(targets),
        "raw": raw,
        "bestSmallTranslation": best,
    }


def compact_edge(edge: dict) -> str:
    return (
        f"p{edge['sourcePage']} O{edge['sourceIndex']} `{edge['sourceLabel']}` -> "
        f"p{edge['targetPage']} {edge['targetKind'][0].upper()}{edge['targetIndex']} `{edge['targetLabel']}` "
        f"(src={edge['overlapVsSource']:.3f}, tgt={edge['overlapVsTarget']:.3f}, dist={edge['centerDistance']:.1f})"
    )


def draw_panel(result: dict) -> Image.Image:
    target_page = result["targetPage"]
    img = upright_image(target_page).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for target in target_items(target_page):
        color = (255, 85, 0, 255) if target["kind"] == "orange" else (0, 190, 240, 255)
        prefix = "O" if target["kind"] == "orange" else "G"
        box = tuple(int(round(v)) for v in target["box"])
        draw.rectangle(box, outline=color, width=5)
        draw.text((box[0], max(0, box[1] - 24)), f"{prefix}{target['index']}", fill=color)

    best = result["bestSmallTranslation"]
    for src in best["mappedSources"]:
        box = tuple(int(round(v)) for v in src["mappedBox"])
        draw.rectangle(box, outline=(190, 0, 255, 210), width=4)
        draw.text((box[0], max(0, box[1] - 22)), f"{result['sourcePage']}:{src['index']}", fill=(190, 0, 255, 255))
    for edge in best["meaningfulEdges"]:
        box = tuple(int(round(v)) for v in edge["intersection"])
        draw.rectangle(box, outline=(30, 255, 30, 255), width=4)

    label = f"{result['sourcePage']} through to {result['targetPage']}  dx={best['dx']} dy={best['dy']}  edges={len(best['meaningfulEdges'])}"
    draw.rectangle((0, 0, img.width, 58), fill=(255, 255, 255, 235))
    draw.text((14, 18), label, fill=(0, 0, 0, 255))

    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.thumbnail((760, 980), Image.Resampling.LANCZOS)
    return combined


def serialize(obj):
    if isinstance(obj, tuple):
        return [serialize(item) for item in obj]
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    return obj


def main() -> None:
    ensure_highres_sources()
    results = [audit_direction(source, target) for source, target in LEAF_DIRECTIONS]

    panels = [draw_panel(result) for result in results]
    panel_w = max(panel.width for panel in panels)
    panel_h = max(panel.height for panel in panels)
    sheet = Image.new("RGB", (2 * panel_w, 3 * panel_h), "white")
    for idx, panel in enumerate(panels):
        sheet.paste(panel, ((idx % 2) * panel_w, (idx // 2) * panel_h))
    sheet.save(OUT_IMG, quality=92)

    page76_results = [r for r in results if r["targetPage"] == 76]
    result = {
        "scope": "front/back leaf box registration using high-res scan and manual highlight labels",
        "gridRange": [min(GRID_RANGE), max(GRID_RANGE), 20],
        "contactSheet": str(OUT_IMG),
        "directions": serialize(results),
        "page76TargetDirections": serialize(page76_results),
        "assessment": [
            "This is a refined physical-leaf test, not the raw hold-to-light final-selector branch.",
            "A genuine leaf selector should produce either a near-zero/small-translation clean page-76 target hit, or repeated coherent hits under the same physical transform.",
            "Large one-off translations and isolated label coincidences should remain calibration/orientation evidence only.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Front/Back Leaf Box Registration Audit",
        "",
        "Scope: refine the physical hold-to-light idea by using the high-res scan as geometry truth, mirroring orange highlight boxes through the actual front/back leaves, and allowing only a bounded crop-correction translation (`-180..180` px, step `20`). OCR is not used as geometry and no key candidates are generated.",
        "",
        f"- Contact sheet: `{OUT_IMG}`",
        "",
        "## Direction Results",
        "",
    ]
    for r in results:
        raw = r["raw"]
        best = r["bestSmallTranslation"]
        lines.append(f"### {r['sourcePage']} -> {r['targetPage']}")
        lines.append(f"- Source orange boxes: {r['sourceCount']}")
        lines.append(f"- Target orange/grey boxes: {r['targetCount']}")
        lines.append(f"- Raw hflip: edges={len(raw['meaningfulEdges'])} score={raw['score']:.5f}")
        lines.append(f"- Best small translation: dx={best['dx']} dy={best['dy']} edges={len(best['meaningfulEdges'])} score={best['score']:.5f}")
        if best["meaningfulEdges"]:
            for edge in best["meaningfulEdges"][:8]:
                lines.append(f"- {compact_edge(edge)}")
        else:
            lines.append("- No meaningful target intersections.")
        lines.append("")

    page76 = page76_results[0] if page76_results else None
    lines.extend(["## Page-76 Check", ""])
    if page76:
        best = page76["bestSmallTranslation"]
        lines.append(
            f"- The only true leaf direction targeting page 76 is `{page76['sourcePage']} -> 76`; its best bounded translation is dx={best['dx']} dy={best['dy']} with {len(best['meaningfulEdges'])} meaningful edge(s)."
        )
        if best["meaningfulEdges"]:
            for edge in best["meaningfulEdges"]:
                lines.append(f"- {compact_edge(edge)}")
        else:
            lines.append("- No p75-through-p76 orange box lands cleanly on the verified page-76 corridor.")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- This refined front/back leaf pass does not reproduce the strong page-76 corridor behavior seen in the 78/79 -> 76 mirrored-highlight graph.",
            "- Any best translations are isolated box coincidences; they do not give a repeated page-76 selector or a human-readable ordering rule.",
            "- Treat true front/back leaf overlay as downgraded unless a physical scan/photo reveals bleed-through marks that are not present in the digital source.",
            "- Next best move: stop spending cycles on generic leaf overlays and inspect the original Canva thumbnail/export or page-76 corridor typography for an explicit ordering/instruction cue.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
