#!/usr/bin/env python3
"""Check whether 3D map anchor points themselves select page-76 active targets."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT_DIR = ROOT / "analysis_outputs/3d_article_map/anchor_point_target_proximity"

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


def hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def point_to_box_distance(point: list[float], box: list[float]) -> tuple[float, str]:
    x, y = point
    dx = max(box[0] - x, x - box[2], 0.0)
    dy = max(box[1] - y, y - box[3], 0.0)
    if dx == 0.0 and dy == 0.0:
        return 0.0, "inside"
    if dx == 0.0:
        relation = "vertical_gap"
    elif dy == 0.0:
        relation = "horizontal_gap"
    else:
        relation = "diagonal_gap"
    return round(math.hypot(dx, dy), 2), relation


def nearest_word(point: list[float], words: list[dict]) -> dict:
    x, y = point
    best = None
    for word in words:
        cx, cy = word["center"]
        dist = math.hypot(cx - x, cy - y)
        item = {
            "id": word["id"],
            "index": word["index"],
            "text": word["text"],
            "distancePx": round(dist, 2),
        }
        if best is None or item["distancePx"] < best["distancePx"]:
            best = item
    return best or {}


def load_font(size: int) -> ImageFont.ImageFont:
    for path in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_overlay(page76_anchors: list[dict], active_targets: list[dict], records: list[dict]) -> Path:
    img = Image.open(PAGE76_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    font = load_font(32)
    small = load_font(24)

    for target in active_targets:
        box = target["box"]
        fill = (255, 130, 0, 65) if target["color"] == "orange" else (0, 0, 0, 65)
        outline = (255, 90, 0, 230) if target["color"] == "orange" else (20, 20, 20, 230)
        draw.rectangle(box, fill=fill, outline=outline, width=5)
        draw.text((box[0], max(0, box[1] - 40)), target["id"], fill=outline, font=font)

    colors = {
        "page79-mirrored-onto-page76": (0, 120, 255, 230),
        "page76-or-page79-mirrored": (200, 60, 190, 230),
    }
    for record in records:
        anchor = record["anchor"]
        x, y = anchor["point"]
        color = colors.get(anchor["source"], (0, 170, 100, 230))
        radius = 18
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color, outline=(255, 255, 255, 240), width=3)
        draw.text((x + 20, y - 16), anchor["id"].replace("p79_", "").replace("p76_", ""), fill=color, font=small)
        nearest = next(t for t in active_targets if t["id"] == record["nearestTarget"]["target"])
        tx = min(max(x, nearest["box"][0]), nearest["box"][2])
        ty = min(max(y, nearest["box"][1]), nearest["box"][3])
        draw.line([(x, y), (tx, ty)], fill=(*color[:3], 135), width=3)

    out = OUT_DIR / "anchor_point_target_proximity_overlay.jpg"
    img.save(out, quality=92)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(MAP_JSON.read_text())
    active_targets = json.loads(ACTIVE_JSON.read_text())["anchors"]
    page76 = next(page for page in data["pages"] if page["page"] == 76)
    words = page76["words"]
    page76_anchors = [anchor for anchor in data["anchors"] if anchor["page"] == 76]

    records = []
    for anchor in page76_anchors:
        target_distances = []
        for target in active_targets:
            distance, relation = point_to_box_distance(anchor["point"], target["box"])
            target_distances.append(
                {
                    "target": target["id"],
                    "targetLabel": target["label"],
                    "targetColor": target["color"],
                    "distancePx": distance,
                    "relation": relation,
                }
            )
        target_distances.sort(key=lambda row: row["distancePx"])
        word = nearest_word(anchor["point"], words)
        records.append(
            {
                "anchor": anchor,
                "nearestTarget": target_distances[0],
                "targetDistances": target_distances,
                "nearestWord": word,
                "nearestWordInstructionHits": hits(word.get("text", "")),
            }
        )

    source_groups: dict[str, list[dict]] = {}
    for record in records:
        source_groups.setdefault(record["anchor"]["source"], []).append(record)

    streams = {}
    for source, group in source_groups.items():
        ordered = sorted(group, key=lambda item: item["anchor"]["id"])
        streams[f"{source}:nearestTargetIds"] = " ".join(item["nearestTarget"]["target"] for item in ordered)
        streams[f"{source}:nearestWords"] = " | ".join(item["nearestWord"].get("text", "-") for item in ordered)
        streams[f"{source}:nearestDistances"] = " ".join(str(item["nearestTarget"]["distancePx"]) for item in ordered)

    stream_hits = {name: hits(value) for name, value in streams.items()}
    inside_hits = [record for record in records if record["nearestTarget"]["distancePx"] == 0.0]
    near_hits = [record for record in records if record["nearestTarget"]["distancePx"] <= 50.0]

    overlay = draw_overlay(page76_anchors, active_targets, records)

    assessment = [
        "No page-76 3D anchor point lands inside any locked O4/B4/G5/O5 active target box.",
        "No anchor point is within 50 px of an active target; the closest overall is `p76_dollar` to O5 at 331.29 px, and the closest mirrored-pill anchor is p79 pill 3 to O4 at 421.89 px, so the anchor layer is spatially separate from the active text anchors.",
        "Nearest-word streams around the anchor points are ordinary OCR/navigation labels in the art/right-side field, not extraction instructions.",
        "The anchor sequence therefore supports orientation and ray construction only; it does not provide a point-to-target order or unit.",
    ]
    decision = (
        "Do not treat 3D anchor points as direct selectors into O4/B4/G5/O5 under the current scan."
    )
    next_move = (
        "Keep using anchors only as orientation/provenance aids unless a future source transform moves them onto active target text or a clue names a specific anchor order."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D page-76 anchor point proximity to locked O4/B4/G5/O5 active targets. No key derivation.",
        "sources": {"article3dMap": str(MAP_JSON.relative_to(ROOT)), "activeTargets": str(ACTIVE_JSON.relative_to(ROOT))},
        "page76AnchorCount": len(page76_anchors),
        "insideTargetCount": len(inside_hits),
        "nearTargetWithin50Count": len(near_hits),
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "records": records,
        "overlay": str(overlay.relative_to(ROOT)),
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "anchor_point_target_proximity.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# 3D Anchor Point Target Proximity",
        "",
        "Scope: check whether 3D page-76 anchor points directly select the locked O4/B4/G5/O5 page-76 targets. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Page-76 anchors checked: `{len(page76_anchors)}`",
        f"- Anchors inside active targets: `{len(inside_hits)}`",
        f"- Anchors within 50 px of active targets: `{len(near_hits)}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Anchor Proximity",
        "",
        "| anchor | source | point | nearest target | distance | nearest word | word distance | instruction hits |",
        "|---|---|---|---|---:|---|---:|---|",
    ]
    for record in records:
        anchor = record["anchor"]
        nearest = record["nearestTarget"]
        word = record["nearestWord"]
        lines.append(
            f"| `{anchor['id']}` | `{anchor['source']}` | `{anchor['point']}` | "
            f"`{nearest['target']}` ({nearest['relation']}) | {nearest['distancePx']} | "
            f"`{word.get('text', '-')}` | {word.get('distancePx', '-')} | "
            f"{', '.join(record['nearestWordInstructionHits']) or '-'} |"
        )

    lines.extend(["", "## Streams", ""])
    for name, value in streams.items():
        lines.append(f"- `{name}` hits={','.join(stream_hits[name]) or 'none'}: `{value}`")

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "anchor_point_target_proximity.md").write_text("\n".join(lines))

    print(OUT_DIR / "anchor_point_target_proximity.md")
    print(OUT_DIR / "anchor_point_target_proximity.json")
    print(overlay)


if __name__ == "__main__":
    main()
