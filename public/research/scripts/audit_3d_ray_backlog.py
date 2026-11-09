#!/usr/bin/env python3
"""Audit ray selections stored in the 3D map but not rendered by the viewer."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
OBBO_JSON = ROOT / "analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json"
OUT_DIR = ROOT / "analysis_outputs/3d_article_map/ray_backlog_audit"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

DISPLAYED_LIMIT = 28

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
    "above",
    "below",
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
    "volcano",
    "bonds",
    "imf",
    "bukele",
    "salvador",
    "buying",
    "dip",
    "billion",
    "shitcoiner",
    "heart",
    "sell",
    "trust",
    "novogratz",
]


def hits(text: str, terms: list[str]) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for term in terms:
        if re.search(rf"\b{re.escape(term)}\b", lower):
            found.append(term)
    return found


def box_center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def center_in_box(point: tuple[float, float], box: list[float]) -> bool:
    x, y = point
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def overlap_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def load_font(size: int = 34) -> ImageFont.ImageFont:
    for path in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_overlay(page: dict, anchors: dict, active_boxes: list[dict], hidden_records: list[dict]) -> Path:
    img = Image.open(PAGE76_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    font = load_font(34)
    small_font = load_font(28)

    for anchor in active_boxes:
        box = anchor["box"]
        color = (255, 150, 0, 90) if anchor["color"] == "orange" else (0, 0, 0, 75)
        outline = (255, 100, 0, 230) if anchor["color"] == "orange" else (20, 20, 20, 230)
        draw.rectangle(box, fill=color, outline=outline, width=5)
        draw.text((box[0], box[1] - 42), anchor["id"], fill=outline, font=font)

    palette = [
        (0, 120, 255, 170),
        (0, 180, 120, 170),
        (220, 70, 180, 170),
        (160, 90, 0, 170),
    ]
    for i, record in enumerate(hidden_records):
        color = palette[i % len(palette)]
        ray = record["selection"]
        a = anchors.get(ray["a"])
        b = anchors.get(ray["b"])
        if a and b:
            draw.line([tuple(a["point"]), tuple(b["point"])], fill=color, width=5)
            mx = (a["point"][0] + b["point"][0]) / 2
            my = (a["point"][1] + b["point"][1]) / 2
            draw.text((mx, my), f"r{ray['rank']}", fill=color, font=small_font)
        for word in record["resolvedWords"]:
            box = word["box"]
            draw.rectangle(box, outline=color, width=2)

    out = OUT_DIR / "ray_backlog_overlay.jpg"
    img.save(out, quality=92)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(MAP_JSON.read_text())
    obbo = json.loads(OBBO_JSON.read_text())
    page76 = next(page for page in data["pages"] if page["page"] == 76)
    page76_words = {word["index"]: word for word in page76["words"]}
    anchors = {anchor["id"]: anchor for anchor in data["anchors"]}
    active_boxes = obbo["anchors"]

    records = []
    for pos, selection in enumerate(data["raySelections"], start=1):
        resolved_words = [page76_words[i] for i in selection["wordIndexes"] if i in page76_words]
        active_hits = []
        for word in resolved_words:
            center = tuple(word["center"])
            for active in active_boxes:
                overlaps = overlap_area(word["box"], active["box"])
                if center_in_box(center, active["box"]) or overlaps > 0:
                    active_hits.append(
                        {
                            "word": word["text"],
                            "wordIndex": word["index"],
                            "target": active["id"],
                            "targetLabel": active["label"],
                            "centerInside": center_in_box(center, active["box"]),
                            "overlapPx2": round(overlaps, 2),
                        }
                    )
        record = {
            "position": pos,
            "renderedByViewer": pos <= DISPLAYED_LIMIT,
            "selection": selection,
            "instructionHits": hits(selection["text"], INSTRUCTION_TERMS),
            "targetHits": hits(selection["text"], TARGET_TERMS),
            "resolvedWords": resolved_words,
            "activeTargetHits": active_hits,
        }
        records.append(record)

    hidden = [record for record in records if not record["renderedByViewer"]]
    hidden_with_instruction = [r for r in hidden if r["instructionHits"]]
    hidden_with_targets = [r for r in hidden if r["targetHits"]]
    hidden_with_active_target_hits = [r for r in hidden if r["activeTargetHits"]]

    endpoint_groups: dict[tuple[str, str, str, int], list[int]] = {}
    for record in records:
        selection = record["selection"]
        key = (selection["a"], selection["b"], selection["mode"], selection["threshold"])
        endpoint_groups.setdefault(key, []).append(record["position"])
    hidden_pairs_with_displayed_counterpart = []
    for record in hidden:
        selection = record["selection"]
        key = (selection["a"], selection["b"], selection["mode"], selection["threshold"])
        partners = endpoint_groups[key]
        displayed = [pos for pos in partners if pos <= DISPLAYED_LIMIT]
        if displayed:
            hidden_pairs_with_displayed_counterpart.append(
                {"hiddenPosition": record["position"], "displayedCounterparts": displayed, "key": key}
            )

    overlay = draw_overlay(page76, anchors, active_boxes, hidden)

    assessment = [
        f"The viewer-rendered cap accounts for ranks 1-{DISPLAYED_LIMIT}; ranks {DISPLAYED_LIMIT + 1}-40 are stored only in JSON/backlog.",
        "The backlog rays are mostly lower-score alternates or reading-order duplicates of the already-rendered pill/black-bar/wire rays.",
        "Backlog target-term hits are contextual only: they include IMF/Novogratz, `should sell`, and a generic `heart`, but not trusted G5/O5 box contacts.",
        "No backlog ray text contains an extraction instruction term such as read/take/word/letter/edge/font/mirror/key.",
        "No backlog selected word center or word box intersects the active O4/B4/G5/O5 target boxes, so the hidden ray list does not recover a missed selector into the locked page-76 targets.",
    ]
    decision = (
        "Do not treat the 12 non-rendered ray selections as hidden 3D-view evidence. Keep them as low-score diagnostic alternates unless a future rule explicitly chooses ray ranks 29-40 or the unrendered JSON layer."
    )
    next_move = (
        "Return to source/clue acquisition or validation; the local 3D map ray backlog does not name the missing unit/order."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D map ray backlog audit; inspect JSON ranks not rendered by viewer. No key derivation.",
        "sources": {
            "article3dMap": str(MAP_JSON.relative_to(ROOT)),
            "activeTargets": str(OBBO_JSON.relative_to(ROOT)),
        },
        "displayedLimit": DISPLAYED_LIMIT,
        "rayCount": len(records),
        "hiddenRayCount": len(hidden),
        "hiddenWithInstructionHits": [
            {"position": r["position"], "rank": r["selection"]["rank"], "hits": r["instructionHits"], "text": r["selection"]["text"]}
            for r in hidden_with_instruction
        ],
        "hiddenWithTargetHits": [
            {"position": r["position"], "rank": r["selection"]["rank"], "hits": r["targetHits"], "text": r["selection"]["text"]}
            for r in hidden_with_targets
        ],
        "hiddenWithActiveTargetHits": [
            {"position": r["position"], "rank": r["selection"]["rank"], "hits": r["activeTargetHits"], "text": r["selection"]["text"]}
            for r in hidden_with_active_target_hits
        ],
        "hiddenPairsWithDisplayedCounterpart": hidden_pairs_with_displayed_counterpart,
        "hiddenRecords": [
            {
                "position": r["position"],
                "rank": r["selection"]["rank"],
                "score": r["selection"]["score"],
                "a": r["selection"]["a"],
                "b": r["selection"]["b"],
                "mode": r["selection"]["mode"],
                "threshold": r["selection"]["threshold"],
                "order": r["selection"]["order"],
                "text": r["selection"]["text"],
                "instructionHits": r["instructionHits"],
                "targetHits": r["targetHits"],
                "activeTargetHits": r["activeTargetHits"],
            }
            for r in hidden
        ],
        "overlay": str(overlay.relative_to(ROOT)),
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }

    (OUT_DIR / "ray_backlog_audit.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# 3D Ray Backlog Audit",
        "",
        "Scope: inspect ray selections stored in the 3D map JSON but not rendered by the runtime viewer. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Rays stored: `{result['rayCount']}`",
        f"- Viewer-rendered limit: `{DISPLAYED_LIMIT}`",
        f"- Backlog rays: `{result['hiddenRayCount']}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Backlog Rays",
        "",
        "| pos | rank | score | endpoints | mode | order | instruction hits | target hits | active target box hits | text |",
        "|---:|---:|---:|---|---|---|---|---|---|---|",
    ]
    for record in result["hiddenRecords"]:
        active = ", ".join(f"{hit['word']}->{hit['target']}" for hit in record["activeTargetHits"]) or "-"
        lines.append(
            f"| {record['position']} | {record['rank']} | {record['score']} | `{record['a']} -> {record['b']}` | "
            f"`{record['mode']}/{record['threshold']}` | `{record['order']}` | "
            f"{', '.join(record['instructionHits']) or '-'} | {', '.join(record['targetHits']) or '-'} | {active} | "
            f"{record['text']} |"
        )

    lines.extend(
        [
            "",
            "## Duplicate/Alternate Check",
            "",
            f"- Hidden rays sharing endpoint/mode/threshold with a displayed ray: `{len(hidden_pairs_with_displayed_counterpart)}`",
        ]
    )
    for item in hidden_pairs_with_displayed_counterpart:
        lines.append(
            f"  - hidden pos `{item['hiddenPosition']}` shares `{item['key']}` with displayed pos `{item['displayedCounterparts']}`"
        )

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "ray_backlog_audit.md").write_text("\n".join(lines))

    print(OUT_DIR / "ray_backlog_audit.md")
    print(OUT_DIR / "ray_backlog_audit.json")
    print(overlay)


if __name__ == "__main__":
    main()
