#!/usr/bin/env python3
"""Audit 3D map reflection boxes against the locked page-76 active targets."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT_DIR = ROOT / "analysis_outputs/3d_article_map/reflection_box_target_overlap"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]

TARGET_TERMS = [
    "salvador",
    "imf",
    "bukele",
    "volcano",
    "bonds",
    "buying",
    "dip",
    "billion",
    "sell",
    "novogratz",
    "trust",
    "shitcoiner",
    "heart",
]


def hit_terms(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", lower)]


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


def gap(a: list[float], b: list[float]) -> dict:
    if intersection(a, b):
        return {"gapPx": 0.0, "relation": "overlap"}
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    if dx == 0.0:
        relation = "vertical_gap"
    elif dy == 0.0:
        relation = "horizontal_gap"
    else:
        relation = "diagonal_gap"
    return {"gapPx": round((dx * dx + dy * dy) ** 0.5, 2), "relation": relation}


def load_font(size: int) -> ImageFont.ImageFont:
    for path in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def contact_records(ref_box: list[float], active_targets: list[dict]) -> list[dict]:
    contacts = []
    for target in active_targets:
        active_box = target["box"]
        inter = intersection(ref_box, active_box)
        gap_info = gap(ref_box, active_box)
        overlap = area(inter) if inter else 0.0
        contacts.append(
            {
                "target": target["id"],
                "targetLabel": target["label"],
                "targetColor": target["color"],
                "overlapPx2": round(overlap, 2),
                "overlapOfTarget": round(overlap / max(area(active_box), 1.0), 5),
                "overlapOfReflection": round(overlap / max(area(ref_box), 1.0), 5),
                **gap_info,
            }
        )
    contacts.sort(key=lambda row: (-row["overlapPx2"], row["gapPx"]))
    return contacts


def draw_overlay(reflections: list[dict], active_targets: list[dict]) -> Path:
    img = Image.open(PAGE76_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    font = load_font(32)
    small = load_font(24)

    for target in active_targets:
        box = target["box"]
        if target["color"] == "orange":
            fill = (255, 130, 0, 75)
            outline = (255, 90, 0, 240)
        else:
            fill = (0, 0, 0, 65)
            outline = (20, 20, 20, 240)
        draw.rectangle(box, fill=fill, outline=outline, width=5)
        draw.text((box[0], max(0, box[1] - 38)), target["id"], fill=outline, font=font)

    palette = [
        (0, 110, 255, 145),
        (0, 180, 120, 145),
        (190, 70, 210, 145),
        (210, 120, 0, 145),
        (230, 40, 70, 145),
    ]
    for i, record in enumerate(reflections):
        box = record["targetBox"]
        color = palette[i % len(palette)]
        draw.rectangle(box, outline=color, width=4)
        draw.text((box[0], box[1] + 4), record["id"], fill=color, font=small)
        for contact in record["activeContacts"]:
            if contact["overlapPx2"] > 0:
                target = next(t for t in active_targets if t["id"] == contact["target"])
                inter = intersection(box, target["box"])
                if inter:
                    draw.rectangle(inter, fill=(255, 255, 255, 110), outline=(255, 255, 255, 230), width=2)

    out = OUT_DIR / "reflection_box_target_overlap_overlay.jpg"
    img.save(out, quality=92)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(MAP_JSON.read_text())
    active = json.loads(ACTIVE_JSON.read_text())["anchors"]
    page76_refs = []

    for reflection in data["reflections"]:
        if reflection["target"] != 76:
            continue
        contacts = contact_records(reflection["targetBox"], active)
        page76_refs.append(
            {
                **reflection,
                "instructionHits": hit_terms(reflection.get("text", ""), INSTRUCTION_TERMS),
                "targetTermHits": hit_terms(reflection.get("text", ""), TARGET_TERMS),
                "activeContacts": contacts,
                "overlapContacts": [c for c in contacts if c["overlapPx2"] > 0],
                "nearestActiveContact": contacts[0],
            }
        )

    overlap_refs = [r for r in page76_refs if r["overlapContacts"]]
    instruction_refs = [r for r in page76_refs if r["instructionHits"]]
    target_term_refs = [r for r in page76_refs if r["targetTermHits"]]
    nearest_g5_o5 = []
    for target_id in ["volcano_bonds", "shitcoiner_heart"]:
        candidates = []
        for ref in page76_refs:
            contact = next(c for c in ref["activeContacts"] if c["target"] == target_id)
            candidates.append((contact["gapPx"], ref["id"], contact))
        candidates.sort()
        nearest_g5_o5.append({"target": target_id, "nearest": candidates[:3]})

    overlay = draw_overlay(page76_refs, active)

    assessment = [
        "The direct reflection-box layer has one active-target overlap: `79_76_5` grazes O4 `buying the dip` at the bottom of the reflected IMF/Twitter line.",
        "No reflection target box overlaps the locked G5 `Volcano Bonds` or O5 `shitcoiner at heart` boxes; their closest contacts remain visual/registration near-misses rather than exact selectors.",
        "The reflection texts that contain target terms are contextual corridor confirmations (`El Salvador`, `IMF`, `miss buying bitcoin`) but do not contain procedural extraction terms.",
        "Empty reflected visual boxes from p79 land on the far-right/lower page-76 art field and do not touch the active O-B-B-O target text boxes.",
        "This confirms the 3D reflection boxes as orientation/corridor evidence, not a hidden page-76 word/letter selector.",
    ]
    decision = (
        "Do not extract directly from 3D reflection target boxes under the current scan. Reopen only if a new source transform makes G5/O5 direct reflection-box contacts or a clue names a specific reflection id."
    )
    next_move = (
        "Keep the page-76 lower corridor as the validation surface; further progress needs a new source/clue that names the unit/order."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D reflection target-box overlap against locked page-76 O4/B4/G5/O5 targets. No key derivation.",
        "sources": {
            "article3dMap": str(MAP_JSON.relative_to(ROOT)),
            "activeTargets": str(ACTIVE_JSON.relative_to(ROOT)),
        },
        "page76ReflectionCount": len(page76_refs),
        "overlapReflectionCount": len(overlap_refs),
        "instructionReflectionCount": len(instruction_refs),
        "targetTermReflectionCount": len(target_term_refs),
        "nearestG5O5": nearest_g5_o5,
        "reflections": page76_refs,
        "overlay": str(overlay.relative_to(ROOT)),
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "reflection_box_target_overlap.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# 3D Reflection Box Target Overlap",
        "",
        "Scope: check whether reflected boxes stored in the 3D map directly select the locked page-76 O4/B4/G5/O5 targets. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Page-76 reflection boxes: `{len(page76_refs)}`",
        f"- Reflection boxes with active-target overlap: `{len(overlap_refs)}`",
        f"- Reflection boxes with instruction-term hits: `{len(instruction_refs)}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Page-76 Reflection Contacts",
        "",
        "| reflection | source | text hits | instruction hits | overlap contacts | nearest active target | text |",
        "|---|---|---|---|---|---|---|",
    ]
    for ref in page76_refs:
        overlap_contacts = ", ".join(
            f"{c['target']} {c['overlapOfTarget']:.3f}" for c in ref["overlapContacts"]
        ) or "-"
        nearest = ref["nearestActiveContact"]
        nearest_label = f"{nearest['target']} {nearest['relation']} {nearest['gapPx']}px"
        text = ref.get("text", "").replace("|", "\\|") or "-"
        lines.append(
            f"| `{ref['id']}` | `{ref['source']} -> {ref['target']}` | "
            f"{', '.join(ref['targetTermHits']) or '-'} | {', '.join(ref['instructionHits']) or '-'} | "
            f"{overlap_contacts} | {nearest_label} | {text} |"
        )

    lines.extend(["", "## G5/O5 Nearest Reflection Boxes", ""])
    for item in nearest_g5_o5:
        lines.append(f"- `{item['target']}`:")
        for gap_px, ref_id, contact in item["nearest"]:
            lines.append(f"  - `{ref_id}`: {contact['relation']} `{gap_px}` px")

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "reflection_box_target_overlap.md").write_text("\n".join(lines))

    print(OUT_DIR / "reflection_box_target_overlap.md")
    print(OUT_DIR / "reflection_box_target_overlap.json")
    print(overlay)


if __name__ == "__main__":
    main()
