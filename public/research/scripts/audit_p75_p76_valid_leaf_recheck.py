#!/usr/bin/env python3
"""Topology-constrained p75->p76 same-leaf recheck.

This pass does not derive keys. It consolidates the only physically valid
same-leaf path into page 76 under normal magazine pagination and records
whether it supplies the lower-corridor selector we keep looking for.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/p75_p76_valid_leaf_recheck"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRONT_BACK_JSON = ROOT / "analysis_outputs/source_audit/front_back_leaf_box_registration.json"
PHYSICAL_JSON = ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.json"
HOLD_MD = ROOT / "analysis_outputs/source_audit/leaf_hold_to_light_sheet.md"

OUT_JSON = OUT_DIR / "p75_p76_valid_leaf_recheck.json"
OUT_MD = OUT_DIR / "p75_p76_valid_leaf_recheck.md"
OUT_SHEET = OUT_DIR / "p75_p76_valid_leaf_recheck_sheet.jpg"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def direction_75_to_76(front_back: dict[str, Any]) -> dict[str, Any]:
    for item in front_back["directions"]:
        if item["sourcePage"] == 75 and item["targetPage"] == 76:
            return item
    raise RuntimeError("75->76 direction not found in front/back registration JSON")


def score_75_hold_to_light() -> dict[str, float | None]:
    if not HOLD_MD.exists():
        return {"balanced": None, "jaccard": None, "highlightBalanced": None, "highlightJaccard": None}
    text = HOLD_MD.read_text()
    match = re.search(
        r"75_view_76_through: balanced=([0-9.]+) jaccard=([0-9.]+).*?"
        r"highlightBalanced=([0-9.]+) highlightJaccard=([0-9.]+)",
        text,
    )
    if not match:
        return {"balanced": None, "jaccard": None, "highlightBalanced": None, "highlightJaccard": None}
    return {
        "balanced": float(match.group(1)),
        "jaccard": float(match.group(2)),
        "highlightBalanced": float(match.group(3)),
        "highlightJaccard": float(match.group(4)),
    }


def model_75_to_76(physical: dict[str, Any]) -> dict[str, Any] | None:
    for model in physical.get("physicalModels", []):
        if model.get("sourcePage") == 75 and "75 -> 76" in model.get("model", ""):
            return model
    return None


def short_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourceId": edge["sourceId"],
        "sourceLabel": edge["sourceLabel"],
        "mappedBox": edge["mappedBox"],
        "targetId": edge["targetId"],
        "targetKind": edge["targetKind"],
        "targetIndex": edge["targetIndex"],
        "targetLabel": edge["targetLabel"],
        "targetBox": edge["targetBox"],
        "overlapVsSource": edge["overlapVsSource"],
        "overlapVsTarget": edge["overlapVsTarget"],
        "centerDistance": edge["centerDistance"],
    }


def box_tuple(box: list[float] | tuple[float, ...]) -> tuple[int, int, int, int]:
    return tuple(int(round(v)) for v in box)  # type: ignore[return-value]


def draw_labeled_box(
    draw: ImageDraw.ImageDraw,
    box: list[float] | tuple[float, ...],
    label: str,
    color: tuple[int, int, int, int],
    width: int = 4,
) -> None:
    x1, y1, x2, y2 = box_tuple(box)
    draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
    draw.rectangle((x1, max(0, y1 - 30), x1 + max(80, len(label) * 8), y1), fill=(255, 255, 255, 220))
    draw.text((x1 + 4, max(0, y1 - 24)), label, fill=color)


def draw_panel(page76: Image.Image, state: dict[str, Any], lower_targets: dict[str, Any], title: str) -> Image.Image:
    base = page76.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for src in state["mappedSources"]:
        draw_labeled_box(draw, src["mappedBox"], f"p75 O{src['index']}", (150, 0, 220, 190), width=3)

    for edge in state["meaningfulEdges"]:
        draw_labeled_box(draw, edge["targetBox"], f"p76 {edge['targetKind'][0].upper()}{edge['targetIndex']}", (0, 150, 220, 230), width=5)
        draw_labeled_box(draw, edge["intersection"], "intersection", (0, 220, 70, 255), width=5)

    if lower_targets.get("O5"):
        draw_labeled_box(draw, lower_targets["O5"]["box"], "trusted O5", (255, 90, 0, 240), width=5)
    if lower_targets.get("G5"):
        draw_labeled_box(draw, lower_targets["G5"]["box"], "trusted G5", (0, 180, 180, 240), width=5)

    draw.rectangle((0, 0, base.width, 72), fill=(255, 255, 255, 235))
    draw.text((18, 18), title, fill=(0, 0, 0, 255))
    combined = Image.alpha_composite(base, overlay).convert("RGB")
    combined.thumbnail((760, 990), Image.Resampling.LANCZOS)
    return combined


def write_sheet(direction: dict[str, Any], physical: dict[str, Any]) -> None:
    page76 = upright_image(76)
    lower_targets = physical.get("targets", {}) if physical else {}
    raw = direction["raw"]
    best = direction["bestSmallTranslation"]
    raw_panel = draw_panel(
        page76,
        raw,
        lower_targets,
        f"75->76 raw hflip: edges={len(raw['meaningfulEdges'])}, score={raw['score']}",
    )
    best_panel = draw_panel(
        page76,
        best,
        lower_targets,
        f"75->76 best bounded translation: dx={best['dx']} dy={best['dy']}, edges={len(best['meaningfulEdges'])}",
    )
    w = raw_panel.width + best_panel.width
    h = max(raw_panel.height, best_panel.height)
    sheet = Image.new("RGB", (w, h), "white")
    sheet.paste(raw_panel, (0, 0))
    sheet.paste(best_panel, (raw_panel.width, 0))
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    front_back = load_json(FRONT_BACK_JSON)
    physical = load_json(PHYSICAL_JSON)
    direction = direction_75_to_76(front_back)
    hold_scores = score_75_hold_to_light()
    physical_model = model_75_to_76(physical)

    raw = direction["raw"]
    best = direction["bestSmallTranslation"]
    trusted_target_overlaps = physical_model["overlapCount"] if physical_model else None
    nearest = physical_model["nearestItems"][0] if physical_model and physical_model.get("nearestItems") else None

    write_sheet(direction, physical)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p75->p76 valid same-leaf hold-to-light recheck under locked current scan; no key derivation",
        "inputs": {
            "frontBackRegistration": str(FRONT_BACK_JSON.relative_to(ROOT)),
            "physicalModelValidation": str(PHYSICAL_JSON.relative_to(ROOT)),
            "holdToLightSheet": str(HOLD_MD.relative_to(ROOT)),
        },
        "topology": {
            "sourcePage": 75,
            "targetPage": 76,
            "relationship": "same physical leaf",
            "reason": "magazine page 75 is recto/right/odd; page 76 is verso/left/even on the same leaf",
        },
        "rawHflip": {
            "dx": raw["dx"],
            "dy": raw["dy"],
            "score": raw["score"],
            "edgeCount": len(raw["meaningfulEdges"]),
            "edges": [short_edge(edge) for edge in raw["meaningfulEdges"]],
        },
        "bestBoundedTranslation": {
            "dx": best["dx"],
            "dy": best["dy"],
            "score": best["score"],
            "edgeCount": len(best["meaningfulEdges"]),
            "edges": [short_edge(edge) for edge in best["meaningfulEdges"]],
        },
        "holdToLightImageScores": hold_scores,
        "trustedLowerCorridorValidation": {
            "checkedTargets": list(physical.get("targets", {}).keys()),
            "overlapCount": trusted_target_overlaps,
            "nearestItemSummary": nearest,
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "The only current-scan same-leaf path into page 76 is p75->p76.",
            "Raw horizontal flip gives zero meaningful page-76 target intersections.",
            "The best bounded translation is dx=0 dy=-180 and only maps p75 orange O1/O2 into p76 upper grey G1.",
            "The same-leaf model has zero overlap with trusted lower O5/G5 targets.",
            "This does not explain the lower page-76 corridor; keep it only as a physical/source benchmark if a new scan appears.",
        ],
        "decision": {
            "p75P76ValidLeafAsCurrentScanSelector": "closed",
            "nextMove": "Return to non-physical registration/orientation sources for the lower page-76 corridor, especially p78 frame/O5 adjacency and explicit source ordering cues.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# P75/P76 Valid Same-Leaf Recheck",
        "",
        "Scope: topology-constrained recheck of the only physically valid same-leaf path into page 76 under the locked current scan. No hashing, seed generation, WIF/minikey checking, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Inputs Checked",
        "",
        f"- Front/back registration: `{FRONT_BACK_JSON.relative_to(ROOT)}`",
        f"- Physical O5/G5 validation: `{PHYSICAL_JSON.relative_to(ROOT)}`",
        f"- Hold-to-light score sheet: `{HOLD_MD.relative_to(ROOT)}`",
        "",
        "## Result",
        "",
        f"- Relationship: `75 -> 76` is the valid same-leaf path into page 76.",
        f"- Raw hflip: edges=`{len(raw['meaningfulEdges'])}`, score=`{raw['score']:.5f}`.",
        f"- Best bounded translation: dx=`{best['dx']}`, dy=`{best['dy']}`, edges=`{len(best['meaningfulEdges'])}`, score=`{best['score']:.5f}`.",
    ]
    for edge in best["meaningfulEdges"]:
        lines.append(
            "- Best edge: "
            f"p75 `{edge['sourceLabel']}` -> p76 {edge['targetKind']} `{edge['targetLabel']}` "
            f"(src overlap `{edge['overlapVsSource']:.5f}`, target overlap `{edge['overlapVsTarget']:.5f}`, distance `{edge['centerDistance']}` px)."
        )
    lines += [
        f"- Hold-to-light highlight score for `75_view_76_through`: balanced=`{hold_scores['highlightBalanced']}`, jaccard=`{hold_scores['highlightJaccard']}`.",
        f"- Trusted lower O5/G5 overlaps under same-leaf model: `{trusted_target_overlaps}`.",
    ]
    if nearest:
        lines.append(
            f"- Nearest same-leaf item to trusted lower corridor remains `{nearest['label']}`; it does not overlap O5/G5."
        )
    lines += [
        "",
        "## Assessment",
        "",
        "- The raw physical mirror gives no page-76 target hit.",
        "- The only bounded-translation hits are upper-page grey prose around `Gotta be this way... post-1971 fiat money`, not the lower El Salvador/IMF/Bukele/Volcano/O5 corridor.",
        "- This closes `75 -> 76` as a current-scan selector. It stays useful only as a benchmark for a future physical scan/photo or original layout export.",
        "",
        "## Next Move",
        "",
        "- Work from the non-physical registration/orientation evidence that actually touches the lower page-76 corridor: p78 frame/O5 adjacency, p80 package anchors, and explicit ordering cues. Do not promote same-leaf hold-to-light again unless a new source changes the physical registration.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("p75P76ValidLeafAsCurrentScanSelector: closed")


if __name__ == "__main__":
    main()
