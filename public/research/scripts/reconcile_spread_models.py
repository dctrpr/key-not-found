#!/usr/bin/env python3
"""Reconcile physical spread assumptions after the opener-spread discovery.

The announcement photo proves the opener pages 73-74 were presented as a
visible spread, while earlier geometry passes tested standard parity spreads
(76/77, 78/79) and front/back leaves. This pass compares the competing spread
models in one place using only raw high-res hflip geometry and highlight-box
intersections. No key candidates are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image

from analyze_front_back_leaf_box_registration import (
    area,
    center,
    grey_items,
    hflip_box,
    intersection,
    orange_items as body_orange_items,
)
from analyze_opener_pill_cash_inventory import (
    P73,
    P74,
    classify_p73_orange_components,
    p74_orange_components,
)
from highres_reflection_extract import ensure_highres_sources, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/spread_model_reconciliation"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "spread_model_reconciliation.json"
OUT_MD = OUT / "spread_model_reconciliation.md"


PDF_ADJACENT_SPREADS = [(73, 74), (75, 76), (77, 78), (79, 80)]
STANDARD_PARITY_SPREADS = [(76, 77), (78, 79)]


def page_image(page: int) -> Image.Image:
    if page == 73:
        return Image.open(P73).convert("RGB")
    if page == 74:
        return Image.open(P74).convert("RGB")
    return upright_image(page)


def opener_orange_items(page: int) -> list[dict]:
    if page == 73:
        img = page_image(73)
        capsules, other = classify_p73_orange_components(img)
        items = []
        for cap in capsules:
            idx = cap["capsuleIndexTopToBottom"]
            items.append(
                {
                    "kind": "orange",
                    "page": 73,
                    "index": idx,
                    "id": f"p73_capsule_{idx}",
                    "box": tuple(float(v) for v in cap["box"]),
                    "label": f"opener capsule {idx}",
                }
            )
        # Keep the orange OVERDOSE label as a separate component if detected.
        label_like = [row for row in other if row["center"][1] < 350]
        for row in label_like:
            items.append(
                {
                    "kind": "orange",
                    "page": 73,
                    "index": len(items) + 1,
                    "id": f"p73_orange_{len(items) + 1}",
                    "box": tuple(float(v) for v in row["box"]),
                    "label": "small OVERDOSE section label",
                }
            )
        return items
    if page == 74:
        img = page_image(74)
        rows = p74_orange_components(img)
        return [
            {
                "kind": "orange",
                "page": 74,
                "index": i + 1,
                "id": f"p74_orange_{i + 1}",
                "box": tuple(float(v) for v in row["box"]),
                "label": "small OVERDOSE section label component",
            }
            for i, row in enumerate(rows)
        ]
    return []


def orange_items(page: int) -> list[dict]:
    if page in {73, 74}:
        return opener_orange_items(page)
    return body_orange_items(page)


def target_items(page: int) -> list[dict]:
    items = orange_items(page)
    if page >= 75:
        items += grey_items(page)
    return items


def edge_score(source: dict, target: dict, width: int) -> dict | None:
    flipped = hflip_box(source["box"], width)
    inter = intersection(flipped, target["box"])
    if not inter:
        return None
    ia = area(inter)
    if ia <= 0:
        return None
    ca = center(flipped)
    cb = center(target["box"])
    source_area = area(flipped)
    target_area = area(target["box"])
    if source_area <= 0 or target_area <= 0:
        return None
    overlap_source = ia / source_area
    overlap_target = ia / target_area
    if overlap_source < 0.05 and overlap_target < 0.05:
        return None
    return {
        "sourcePage": source["page"],
        "targetPage": target["page"],
        "sourceIndex": source["index"],
        "sourceId": source["id"],
        "sourceLabel": source["label"],
        "sourceBox": source["box"],
        "hflipBox": flipped,
        "targetKind": target["kind"],
        "targetIndex": target["index"],
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetBox": target["box"],
        "intersection": inter,
        "overlapArea": round(ia, 2),
        "overlapVsSource": round(overlap_source, 5),
        "overlapVsTarget": round(overlap_target, 5),
        "centerDistance": round(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5, 2),
    }


def audit_direction(source_page: int, target_page: int, model: str) -> dict:
    width = page_image(source_page).width
    sources = orange_items(source_page)
    targets = target_items(target_page)
    edges = []
    for source in sources:
        for target in targets:
            edge = edge_score(source, target, width)
            if edge:
                edges.append(edge)
    edges.sort(key=lambda e: (-max(e["overlapVsSource"], e["overlapVsTarget"]), e["targetKind"], e["targetIndex"], e["sourceIndex"]))
    return {
        "model": model,
        "sourcePage": source_page,
        "targetPage": target_page,
        "sourceOrangeCount": len(sources),
        "targetHighlightCount": len(targets),
        "meaningfulEdges": edges,
        "targetPattern": "".join(("O" if e["targetKind"] == "orange" else "G") + str(e["targetIndex"]) for e in edges),
    }


def paired_directions(pairs: list[tuple[int, int]], model: str) -> list[dict]:
    rows = []
    for left, right in pairs:
        rows.append(audit_direction(left, right, model))
        rows.append(audit_direction(right, left, model))
    return rows


def main() -> None:
    ensure_highres_sources()
    adjacent = paired_directions(PDF_ADJACENT_SPREADS, "pdf_adjacent_or_photographed_spread")
    standard = paired_directions(STANDARD_PARITY_SPREADS, "standard_even_left_odd_right")
    all_rows = adjacent + standard

    page76_rows = [r for r in all_rows if r["targetPage"] == 76]
    page80_rows = [r for r in all_rows if r["targetPage"] == 80 or r["sourcePage"] == 80]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "spread model reconciliation; raw high-res hflip intersections only; no key derivation",
        "models": {
            "pdfAdjacentOrPhotographedSpread": PDF_ADJACENT_SPREADS,
            "standardEvenLeftOddRight": STANDARD_PARITY_SPREADS,
        },
        "directions": all_rows,
        "summary": {
            "directionsTested": len(all_rows),
            "directionsWithEdges": sum(1 for r in all_rows if r["meaningfulEdges"]),
            "page76TargetDirections": page76_rows,
            "page80InvolvedDirections": page80_rows,
        },
        "assessment": [
            "The photographed opener proves pages 73-74 are a visible source spread, so the source model must remember PDF-adjacent spread evidence.",
            "Raw PDF-adjacent folds do not create a new page-76 selector: 75->76 has no meaningful raw hit.",
            "The only repeated adjacent-spread hit is the known 79/80 package-label interaction, which supports the medicine/pill theme but still does not specify a page-76 extraction rule.",
            "The standard parity spread tests remain weak and do not override the stronger page-76 reflected-highlight graph.",
        ],
        "nextMove": "Treat 73-74 and 79-80 as source/provenance/theme spreads, but do not reopen generic spread folding. Continue only with a rule that targets page 76 or with new physical-source registration.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Spread Model Reconciliation",
        "",
        "Scope: reconcile the photographed opener spread with earlier high-res spread and front/back tests. This uses raw horizontal reflection of source orange boxes onto target orange/grey boxes. No key candidates are generated.",
        "",
        "## Models Tested",
        "",
        f"- PDF-adjacent / photographed spread candidates: `{PDF_ADJACENT_SPREADS}`",
        f"- Standard even-left / odd-right spread candidates: `{STANDARD_PARITY_SPREADS}`",
        "",
        "## Direction Results",
        "",
    ]
    for row in all_rows:
        lines.append(
            f"### {row['model']} {row['sourcePage']} -> {row['targetPage']}"
        )
        lines.append(f"- source orange boxes: `{row['sourceOrangeCount']}`")
        lines.append(f"- target highlight boxes: `{row['targetHighlightCount']}`")
        lines.append(f"- meaningful raw intersections: `{len(row['meaningfulEdges'])}`")
        lines.append(f"- target pattern: `{row['targetPattern']}`")
        for edge in row["meaningfulEdges"][:6]:
            lines.append(
                f"- p{edge['sourcePage']} `{edge['sourceLabel']}` -> p{edge['targetPage']} {edge['targetKind']} {edge['targetIndex']} `{edge['targetLabel']}` "
                f"(src={edge['overlapVsSource']:.3f}, tgt={edge['overlapVsTarget']:.3f}, dist={edge['centerDistance']:.1f})"
            )
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- The opener photo requires us to keep a PDF-adjacent spread layer in the source model, at least for pages 73-74.",
            "- That does not rescue page 76: raw `75 -> 76` in the PDF-adjacent model has no meaningful hit.",
            "- The `79 <-> 80` adjacent interaction is the only repeated nearby source/theme signal, tying page 79 end-text to the page-80 medicine/package artwork.",
            "- This reinforces the medicine/five-capsule provenance layer, but it still does not define page-76 target text, ordering, or letter extraction.",
            "- The next useful move remains a source/physical registration improvement or a specific mirror-writing rule, not more unconstrained spread folding.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"directions={len(all_rows)} directions_with_edges={sum(1 for r in all_rows if r['meaningfulEdges'])}")


if __name__ == "__main__":
    main()
