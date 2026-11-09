#!/usr/bin/env python3
"""
Audit the 3D viewer itself as an evidence surface.

This is not a key-generation pass. It checks what the browser viewer actually
draws from its source files, which layers are precomputed, and whether the UI
adds any hidden mirror/fold selector beyond the data already analyzed.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "3d_article_map" / "viewer_layer_provenance"
DATA_PATH = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
VIEWER_PATH = ROOT / "analysis_outputs" / "3d_article_map" / "viewer.js"
HTML_PATH = ROOT / "analysis_outputs" / "3d_article_map" / "index.html"


def page_of(value):
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        return value.get("page")
    return None


def extract_layout_block(viewer_js: str) -> dict[str, dict[str, list[float]]]:
    """Small parser for the fixed layout object inside viewer.js."""
    layouts: dict[str, dict[str, list[float]]] = {}
    for mode in ("spread", "stack", "fold"):
        match = re.search(rf"{mode}:\s*\{{(.*?)\n\s*\}}", viewer_js, re.S)
        if not match:
            continue
        rows: dict[str, list[float]] = {}
        for page, values in re.findall(r"(\d+):\s*\[([^\]]+)\]", match.group(1)):
            rows[page] = [float(item.strip()) for item in values.split(",")]
        layouts[mode] = rows
    return layouts


def read_controls(html: str) -> dict[str, list[str]]:
    layout_modes = re.findall(r'data-layout="([^"]+)"', html)
    toggles = re.findall(r'id="(toggle[^"]+)"', html)
    focus_options = re.findall(r'<option value="([^"]+)">Page \d+</option>', html)
    asset_links = re.findall(r'<a class="asset-link" href="([^"]+)"', html)
    return {
        "layoutModes": layout_modes,
        "toggles": toggles,
        "focusPageOptions": focus_options,
        "assetLinks": asset_links,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA_PATH.read_text())
    viewer_js = VIEWER_PATH.read_text()
    html = HTML_PATH.read_text()

    controls = read_controls(html)
    layouts = extract_layout_block(viewer_js)

    anchors = {anchor["id"]: anchor for anchor in data["anchors"]}
    anchor_page_counts = Counter(anchor["page"] for anchor in data["anchors"])
    reflection_pairs = Counter(
        (page_of(reflection["source"]), page_of(reflection["target"]))
        for reflection in data["reflections"]
    )

    ray_rows = []
    ray_endpoint_page_pairs: Counter[tuple[int | None, int | None]] = Counter()
    original_p79_ray_uses = 0
    mirrored_p79_ray_uses = 0
    for selection in data["raySelections"]:
        a = anchors.get(selection["a"])
        b = anchors.get(selection["b"])
        pair = (a.get("page") if a else None, b.get("page") if b else None)
        ray_endpoint_page_pairs[pair] += 1
        endpoint_ids = [selection["a"], selection["b"]]
        original_p79_ray_uses += sum("_original" in endpoint for endpoint in endpoint_ids)
        mirrored_p79_ray_uses += sum("_mirror" in endpoint for endpoint in endpoint_ids)
        ray_rows.append(
            {
                "rank": selection["rank"],
                "mode": selection["mode"],
                "a": selection["a"],
                "aPage": pair[0],
                "b": selection["b"],
                "bPage": pair[1],
                "visibleInViewer": selection["rank"] <= 28,
                "text": selection.get("text", ""),
            }
        )

    add_rays_forces_page76 = (
        "const start = pageWorld(76" in viewer_js
        and "const end = pageWorld(76" in viewer_js
    )
    reflection_uses_precomputed_target_box = (
        "reflection.targetBox" in viewer_js and "reflection.sourceBox" not in viewer_js.split("function addReflections()", 1)[1].split("function addAnchors()", 1)[0]
    )
    visible_ray_limit_match = re.search(r"data\.raySelections\.slice\(0,\s*(\d+)\)", viewer_js)
    visible_ray_limit = int(visible_ray_limit_match.group(1)) if visible_ray_limit_match else None

    fold_positions = layouts.get("fold", {})
    fold_pairs = {
        "topRow": ["75", "79"],
        "bottomRow": ["76", "78"],
        "centerBack": ["77"],
        "sideBack": ["80"],
    }
    fold_pair_geometry = {
        name: {page: fold_positions.get(page) for page in pages}
        for name, pages in fold_pairs.items()
    }

    hidden_or_extra_modes = sorted(
        set(controls["layoutModes"]) - {"spread", "fold", "stack"}
    )
    source_hierarchy = {
        "dataMeta": data.get("meta", {}),
        "viewerDrawsPageImages": True,
        "viewerTextSource": "OCR words from article_3d_map_data.json plus browser-local corrections if manually applied",
        "manualCorrectionPersistence": "localStorage only; not part of source geometry or exported reports unless explicitly exported",
    }

    findings = [
        "The 3D viewer exposes only the expected layout modes: spread, fold, and stack.",
        "Mirror boxes are drawn from precomputed targetBox coordinates in article_3d_map_data.json; the viewer does not calculate a new fold/mirror solution at runtime.",
        "Ray selectors are a page-76 hypothesis layer: all ray endpoint anchors used by raySelections are page-76 anchors, including mirrored p79-pill anchors already projected onto page 76.",
        "The viewer draws only the first 28 of 40 raySelections, so the browser view is an inspection aid rather than the complete ray dataset.",
        "The fold layout pairs pages 75/79 and 76/78 visually; it does not make 79/76 a physical contact pair.",
        "Browser-local text corrections can change the visible labels, but they are not geometry truth and do not alter the JSON source model.",
    ]

    decision = (
        "Keep the 3D viewer as a manual orientation/review surface. Do not treat viewer fold depth, "
        "ray visibility, or browser-local correction state as a new selector. Measurements and source "
        "truth must come from high-res scan geometry, corrected/DOCM text witnesses, and generated reports."
    )
    next_move = (
        "If the 3D view is used again, inspect it through the Text Authority/bridge sheets and avoid "
        "drawing conclusions from hidden rays or runtime layout depth. The next meaningful progress "
        "requires a new source image/original layout clue or an explicit unit/order rule."
    )

    report = {
        "scope": "3D viewer layer/source provenance; no key derivation",
        "sourceHierarchy": source_hierarchy,
        "controls": controls,
        "layouts": layouts,
        "foldPairGeometry": fold_pair_geometry,
        "anchorPageCounts": dict(anchor_page_counts),
        "reflectionPairs": {f"{a}->{b}": count for (a, b), count in reflection_pairs.items()},
        "rayEndpointPagePairs": {f"{a}->{b}": count for (a, b), count in ray_endpoint_page_pairs.items()},
        "rayCounts": {
            "total": len(data["raySelections"]),
            "visibleInViewer": sum(1 for row in ray_rows if row["visibleInViewer"]),
            "hiddenByViewerLimit": sum(1 for row in ray_rows if not row["visibleInViewer"]),
            "visibleRayLimit": visible_ray_limit,
            "originalP79EndpointUses": original_p79_ray_uses,
            "mirroredP79EndpointUses": mirrored_p79_ray_uses,
            "addRaysForcesPage76": add_rays_forces_page76,
        },
        "layerImplementation": {
            "reflectionUsesPrecomputedTargetBox": reflection_uses_precomputed_target_box,
            "hiddenOrExtraLayoutModes": hidden_or_extra_modes,
            "assetLinks": controls["assetLinks"],
        },
        "hiddenRayRows": [row for row in ray_rows if not row["visibleInViewer"]],
        "findings": findings,
        "decision": decision,
        "nextMove": next_move,
    }

    (OUT_DIR / "viewer_layer_provenance.json").write_text(json.dumps(report, indent=2))

    lines = [
        "# 3D Viewer Layer Provenance",
        "",
        "Scope: audit what the 3D browser viewer itself draws and whether it adds any hidden fold/mirror selector. No key derivation, hashing, seed phrase, WIF, or address checks were run.",
        "",
        "## Viewer Controls",
        "",
        f"- Layout modes: `{', '.join(controls['layoutModes'])}`",
        f"- Layer toggles: `{', '.join(controls['toggles'])}`",
        f"- Hidden/extra layout modes: `{hidden_or_extra_modes or 'none'}`",
        f"- Data source: `{source_hierarchy['dataMeta'].get('highresSource')}` with OCR source `{source_hierarchy['dataMeta'].get('sourcePdf')}`",
        "",
        "## Layer Findings",
        "",
        f"- Reflection pairs in JSON: `{dict(reflection_pairs)}`",
        f"- Mirror boxes use precomputed `targetBox`: `{reflection_uses_precomputed_target_box}`",
        f"- Ray endpoint page pairs: `{dict(ray_endpoint_page_pairs)}`",
        f"- Rays total/visible/hidden: `{len(data['raySelections'])}` / `{sum(1 for row in ray_rows if row['visibleInViewer'])}` / `{sum(1 for row in ray_rows if not row['visibleInViewer'])}`",
        f"- `addRays()` forces page-76 world coordinates: `{add_rays_forces_page76}`",
        f"- Original p79 anchor endpoint uses in raySelections: `{original_p79_ray_uses}`",
        f"- Mirrored p79 anchor endpoint uses in raySelections: `{mirrored_p79_ray_uses}`",
        "",
        "## Fold Geometry",
        "",
        "| fold group | pages | fixed positions `[x,y,z,rotY]` |",
        "|---|---|---|",
    ]
    for name, pages in fold_pairs.items():
        lines.append(
            f"| `{name}` | `{', '.join(pages)}` | `{fold_pair_geometry[name]}` |"
        )

    lines.extend(
        [
            "",
            "## Hidden Ray Rows",
            "",
            "| rank | mode | endpoints | text preview |",
            "|---:|---|---|---|",
        ]
    )
    for row in report["hiddenRayRows"]:
        text = row["text"].replace("|", "\\|")
        lines.append(
            f"| {row['rank']} | `{row['mode']}` | `{row['a']} -> {row['b']}` | `{text[:90]}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend([f"- {item}" for item in findings])
    lines.extend(["", "## Decision", "", f"- {decision}", "", "## Next Move", "", f"- {next_move}"])

    (OUT_DIR / "viewer_layer_provenance.md").write_text("\n".join(lines) + "\n")

    print(f"Wrote {OUT_DIR / 'viewer_layer_provenance.md'}")
    print(f"Wrote {OUT_DIR / 'viewer_layer_provenance.json'}")


if __name__ == "__main__":
    main()
