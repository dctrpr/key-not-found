#!/usr/bin/env python3
"""Benchmark raw highlight mirroring from every Issue 24 page onto page 76.

This is a geometry-control pass. It asks whether the p78/p79-to-p76 emphasis is
special when the same raw horizontal mirror is applied to all non-76 highlight
boxes. No OCR extraction or key derivation is performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from analyze_highres_spread_fold_pairs import (
    area,
    center,
    grey_items,
    hflip_box,
    intersection,
    orange_items,
)
from highres_reflection_extract import ensure_highres_sources, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_all_source_highlight_mirror_benchmark.json"
OUT_MD = OUT / "page76_all_source_highlight_mirror_benchmark.md"
OUT_SHEET = OUT / "page76_all_source_highlight_mirror_benchmark_sheet.jpg"


def font(size: int = 22) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def p76_targets() -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for item in orange_items(76) + grey_items(76):
        target = dict(item)
        target["targetId"] = ("O" if item["kind"] == "orange" else "G") + str(item["index"])
        targets.append(target)
    return targets


def source_items(page: int) -> list[dict[str, Any]]:
    items = orange_items(page) + grey_items(page)
    items.sort(key=lambda item: (item["box"][1], item["box"][0], item["kind"], item["index"]))
    return items


def overlap_record(src: dict[str, Any], reflected_box: tuple[float, float, float, float], tgt: dict[str, Any]) -> dict[str, Any] | None:
    inter = intersection(reflected_box, tgt["box"])
    if not inter:
        return None
    ia = area(inter)
    if ia <= 0:
        return None
    ca = center(reflected_box)
    cb = center(tgt["box"])
    ovs = ia / max(1.0, area(reflected_box))
    ovt = ia / max(1.0, area(tgt["box"]))
    if ovs < 0.01 and ovt < 0.01:
        return None
    return {
        "sourcePage": src["page"],
        "sourceKind": src["kind"],
        "sourceIndex": src["index"],
        "sourceLabel": src["label"],
        "sourceBox": [round(float(v), 3) for v in src["box"]],
        "reflectedBox": [round(float(v), 3) for v in reflected_box],
        "targetId": tgt["targetId"],
        "targetKind": tgt["kind"],
        "targetIndex": tgt["index"],
        "targetLabel": tgt["label"],
        "targetBox": [round(float(v), 3) for v in tgt["box"]],
        "intersection": [round(float(v), 3) for v in inter],
        "overlapArea": round(float(ia), 3),
        "overlapVsSource": round(float(ovs), 5),
        "overlapVsTarget": round(float(ovt), 5),
        "centerDistance": round(float(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5), 2),
    }


def score_edge(edge: dict[str, Any]) -> float:
    return max(edge["overlapVsSource"], edge["overlapVsTarget"]) * 100.0 + max(0.0, 600.0 - edge["centerDistance"]) / 100.0


def audit_source_page(page: int, targets: list[dict[str, Any]]) -> dict[str, Any]:
    width = upright_image(page).width
    edges = []
    reflected_sources = []
    for src in source_items(page):
        reflected_box = hflip_box(src["box"], width)
        reflected_sources.append({**src, "reflectedBox": reflected_box})
        for tgt in targets:
            rec = overlap_record(src, reflected_box, tgt)
            if rec:
                rec["score"] = round(score_edge(rec), 3)
                edges.append(rec)

    edges.sort(key=lambda e: (-e["score"], e["targetId"], e["sourcePage"], e["sourceIndex"]))
    strong = [e for e in edges if e["overlapVsSource"] >= 0.05 or e["overlapVsTarget"] >= 0.05]
    hit_targets = sorted({e["targetId"] for e in edges}, key=lambda x: (x[0], int(x[1:])))
    hit_targets_strong = sorted({e["targetId"] for e in strong}, key=lambda x: (x[0], int(x[1:])))
    return {
        "sourcePage": page,
        "sourceCount": len(reflected_sources),
        "rawMeaningfulEdges": len(edges),
        "strongEdges": len(strong),
        "hitTargets": hit_targets,
        "strongHitTargets": hit_targets_strong,
        "targetPattern": "".join(e["targetId"] for e in edges),
        "strongTargetPattern": "".join(e["targetId"] for e in strong),
        "score": round(sum(e["score"] for e in strong), 3),
        "edges": edges,
        "topEdges": edges[:8],
        "reflectedSources": [
            {
                "kind": item["kind"],
                "index": item["index"],
                "label": item["label"],
                "reflectedBox": [round(float(v), 3) for v in item["reflectedBox"]],
            }
            for item in reflected_sources
        ],
    }


def draw_panel(page_report: dict[str, Any], targets: list[dict[str, Any]]) -> Image.Image:
    img = upright_image(76).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    f = font(38)
    small = font(24)

    for tgt in targets:
        color = (255, 90, 0, 255) if tgt["kind"] == "orange" else (0, 190, 230, 255)
        draw.rectangle(tgt["box"], outline=color, width=5)
        draw.text((tgt["box"][0], max(0, tgt["box"][1] - 28)), tgt["targetId"], fill=color, font=small)

    for item in page_report["reflectedSources"]:
        color = (160, 0, 255, 150) if item["kind"] == "orange" else (0, 80, 255, 135)
        box = tuple(int(round(v)) for v in item["reflectedBox"])
        draw.rectangle(box, outline=color, width=3)

    for edge in page_report["topEdges"][:5]:
        box = tuple(int(round(v)) for v in edge["intersection"])
        draw.rectangle(box, outline=(0, 255, 80, 255), width=5)

    title = (
        f"p{page_report['sourcePage']} -> p76 | strong {page_report['strongEdges']} | "
        f"targets {' '.join(page_report['strongHitTargets']) or '-'}"
    )
    draw.rectangle([0, 0, img.width, 86], fill=(255, 255, 255, 230))
    draw.text((28, 24), title, fill=(20, 20, 20, 255), font=f)
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.thumbnail((680, 880), Image.Resampling.LANCZOS)
    return combined


def make_sheet(reports: list[dict[str, Any]], targets: list[dict[str, Any]]) -> None:
    panels = [draw_panel(r, targets) for r in reports]
    panel_w = max(p.width for p in panels)
    panel_h = max(p.height for p in panels)
    gutter = 28
    cols = 2
    rows = (len(panels) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * panel_w + (cols + 1) * gutter, rows * panel_h + (rows + 1) * gutter), "white")
    for i, panel in enumerate(panels):
        x = gutter + (i % cols) * (panel_w + gutter)
        y = gutter + (i // cols) * (panel_h + gutter)
        sheet.paste(panel, (x, y))
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    ensure_highres_sources()
    targets = p76_targets()
    source_pages = [75, 77, 78, 79, 80]
    reports = [audit_source_page(page, targets) for page in source_pages]
    reports.sort(key=lambda r: (-r["score"], -r["strongEdges"], r["sourcePage"]))
    make_sheet(reports, targets)

    p78 = next(r for r in reports if r["sourcePage"] == 78)
    p79 = next(r for r in reports if r["sourcePage"] == 79)
    p78p79_targets = sorted(set(p78["strongHitTargets"]) | set(p79["strongHitTargets"]), key=lambda x: (x[0], int(x[1:])))
    other_targets = sorted(
        {target for r in reports if r["sourcePage"] not in {78, 79} for target in r["strongHitTargets"]},
        key=lambda x: (x[0], int(x[1:])),
    )

    decision = (
        "Raw page-center highlight mirroring to page 76 does not produce a final selector. It makes p79 the strongest "
        "uniform source and leaves p75/p80 empty, but p77 also creates mid-page contacts; therefore raw mirrored highlight "
        "boxes alone are too permissive. The useful contacts remain regional, not a word/letter extraction unit."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Raw hflip all non-76 Issue 24 orange/grey highlight boxes onto page 76; geometry benchmark only; no OCR/key derivation.",
        "targetPage": 76,
        "targetCount": len(targets),
        "targets": [
            {"id": t["targetId"], "kind": t["kind"], "index": t["index"], "label": t["label"], "box": list(t["box"])}
            for t in targets
        ],
        "reports": reports,
        "p78p79StrongTargets": p78p79_targets,
        "otherStrongTargets": other_targets,
        "sheet": str(OUT_SHEET),
        "decision": decision,
        "nextMove": "Keep p78/p79-to-page76 highlight mirror evidence as orientation/target evidence only; the next useful move is a source/physical transform or an external rule naming exact unit/order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page 76 All-Source Highlight Mirror Benchmark",
        "",
        "Scope: apply the same raw horizontal mirror to every non-page-76 orange/grey highlight set and measure contacts against verified page-76 orange/grey targets. No OCR extraction, key derivation, hashing, seed checking, WIF checking, or address checking was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{OUT_SHEET}`",
        "",
        "## Summary",
        "",
        "| source page | source boxes | meaningful edges | strong edges | strong targets | score |",
        "|---:|---:|---:|---:|---|---:|",
    ]
    for r in reports:
        lines.append(
            f"| `{r['sourcePage']}` | `{r['sourceCount']}` | `{r['rawMeaningfulEdges']}` | `{r['strongEdges']}` | "
            f"`{' '.join(r['strongHitTargets']) or '-'}` | `{r['score']}` |"
        )
    lines.extend(["", "## Top Edges", ""])
    for r in reports:
        lines.append(f"### p{r['sourcePage']} -> p76")
        if not r["topEdges"]:
            lines.append("- No meaningful contacts.")
        for edge in r["topEdges"][:5]:
            lines.append(
                f"- {edge['sourceKind']} {edge['sourceIndex']} `{edge['sourceLabel']}` -> "
                f"{edge['targetId']} `{edge['targetLabel']}` "
                f"(source={edge['overlapVsSource']}, target={edge['overlapVsTarget']}, dist={edge['centerDistance']})"
            )
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            f"- {decision}",
            f"- p78/p79 strong targets: `{' '.join(p78p79_targets) or '-'}`.",
            f"- Other-page strong targets: `{' '.join(other_targets) or '-'}`.",
            "- This benchmark reinforces the current priority stack but does not supply the missing selector.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
