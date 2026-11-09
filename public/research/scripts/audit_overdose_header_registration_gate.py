#!/usr/bin/env python3
"""Test whether repeated OVERDOSE header placement explains the p78 -> p76 target geometry.

This is a bounded layout/registration pass. It compares the current p78
horizontal mirror frame against a same-layout/OVERDOSE-header registration of
the p78 source graphic onto page 76. It does not perform OCR, key derivation,
hashing, seed/WIF checks, or address checks.
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
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_TARGETS_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
P78_SOURCE_JSON = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json"
P78_FRAME_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json"
P76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/overdose_header_registration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_header_registration_gate.json"
OUT_MD = OUT / "overdose_header_registration_gate.md"
SHEET = OUT / "overdose_header_registration_gate_sheet.jpg"

UNIT_TERMS = [
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
    return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]


def translate_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def mirror_box_x(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_fraction(frame: list[float], target: list[float]) -> float:
    inter = intersection(frame, target)
    return 0.0 if not inter else round(area(inter) / max(area(target), 1.0), 6)


def edge_gap(frame: list[float], target: list[float]) -> float:
    """Smallest outside gap from target to frame edges; 0 for overlap/cut."""
    if intersection(frame, target):
        return 0.0
    cx, cy = center(target)
    dx = 0.0
    dy = 0.0
    if cx < frame[0]:
        dx = frame[0] - cx
    elif cx > frame[2]:
        dx = cx - frame[2]
    if cy < frame[1]:
        dy = frame[1] - cy
    elif cy > frame[3]:
        dy = cy - frame[3]
    if dx == 0.0:
        if target[2] <= frame[0]:
            dx = frame[0] - target[2]
        elif target[0] >= frame[2]:
            dx = target[0] - frame[2]
    if dy == 0.0:
        if target[3] <= frame[1]:
            dy = frame[1] - target[3]
        elif target[1] >= frame[3]:
            dy = target[1] - frame[3]
    return round(math.hypot(max(dx, 0.0), max(dy, 0.0)), 2)


def unit_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in UNIT_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def find_overdose_word(article: dict[str, Any], page_no: int) -> dict[str, Any]:
    page = next(page for page in article["pages"] if page["page"] == page_no)
    matches = [word for word in page.get("words", []) if word.get("token") == "overdose"]
    if not matches:
        raise RuntimeError(f"no OVERDOSE word found on page {page_no}")
    return matches[0]


def unique_frame_candidates(frame_report: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for group in [frame_report.get("edgeEvents", {}), frame_report.get("cornerEvents", {})]:
        for rows in group.values():
            for row in rows:
                if "box" not in row:
                    continue
                candidates[row["id"]] = {
                    "id": row["id"],
                    "label": row["label"],
                    "kind": row.get("role", row.get("kind", "frame-candidate")),
                    "box": row["box"],
                    "source": "p78_frame_order_read",
                }
    return list(candidates.values())


def evaluate_scenario(scenario: dict[str, Any], candidates: list[dict[str, Any]], active_ids: set[str]) -> dict[str, Any]:
    rows = []
    unit_hit_terms: set[str] = set()
    for cand in candidates:
        frac = overlap_fraction(scenario["p76Box"], cand["box"])
        gap = edge_gap(scenario["p76Box"], cand["box"])
        relation = "full" if frac >= 0.75 else "partial" if frac > 0 else "near" if gap <= 50 else "miss"
        hits = unit_hits(cand["label"])
        unit_hit_terms.update(hits)
        rows.append(
            {
                "id": cand["id"],
                "label": cand["label"],
                "kind": cand["kind"],
                "isActiveTarget": cand["id"] in active_ids,
                "overlapVsTarget": frac,
                "edgeGapPx": gap,
                "relation": relation,
                "unitTermHits": hits,
            }
        )
    active_rows = [row for row in rows if row["isActiveTarget"]]
    return {
        **scenario,
        "rows": sorted(rows, key=lambda row: (-row["overlapVsTarget"], row["edgeGapPx"], row["id"])),
        "summary": {
            "activeFullHitCount": sum(1 for row in active_rows if row["relation"] == "full"),
            "activePartialHitCount": sum(1 for row in active_rows if row["relation"] == "partial"),
            "activeMissCount": sum(1 for row in active_rows if row["relation"] in {"miss", "near"}),
            "activeHitIds": [row["id"] for row in active_rows if row["relation"] in {"full", "partial"}],
            "allFullHitLabels": [row["label"] for row in rows if row["relation"] == "full"],
            "allPartialHitLabels": [row["label"] for row in rows if row["relation"] == "partial"],
            "strictUnitTermHitCount": len(unit_hit_terms),
            "strictUnitTermHits": sorted(unit_hit_terms),
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(P76_IMAGE).convert("RGB")
    crop = [230, 2100, 2310, 3040]
    panel = page.crop(crop)
    scale = 0.72
    panel = panel.resize((int(panel.width * scale), int(panel.height * scale)))
    sheet_w = panel.width + 620
    sheet_h = max(panel.height + 80, 900)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)

    draw.text((24, 20), "OVERDOSE Header Registration Gate", fill=(240, 244, 248), font=title)
    draw.text((24, 58), "Page-78 source graphic projected onto page 76 by mirror vs repeated-header layout.", fill=(176, 186, 198), font=normal)
    sheet.paste(panel, (24, 92))

    colors = {
        "current_horizontal_mirror": "#55d6ff",
        "same_layout_slot": "#ff9b2e",
        "overdose_header_translation": "#ff5ebc",
    }
    target_colors = {
        "O4": "#ff9b2e",
        "B4_text": "#8f98a5",
        "G5": "#aab3bf",
        "O5": "#ff9b2e",
    }

    def sx(v: float) -> float:
        return (v - crop[0]) * scale + 24

    def sy(v: float) -> float:
        return (v - crop[1]) * scale + 92

    for target in result["activeTargets"]:
        box = target["box"]
        color = target_colors.get(target["id"], "#ffffff")
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text((sx(box[0]), max(92, sy(box[1]) - 16)), target["id"], fill=color, font=small)

    for scenario in result["scenarios"]:
        box = scenario["p76Box"]
        color = colors[scenario["id"]]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=5)
        draw.text((sx(box[0]) + 6, sy(box[1]) + 6), scenario["label"], fill=color, font=small)

    x0 = panel.width + 60
    y = 100
    draw.text((x0, y), "Summary", fill=(240, 244, 248), font=normal)
    y += 36
    draw.text((x0, y), f"Header delta: dx={result['headerRegistration']['dx']:.2f}, dy={result['headerRegistration']['dy']:.2f}", fill=(202, 211, 221), font=small)
    y += 30
    for scenario in result["scenarios"]:
        color = colors[scenario["id"]]
        draw.rectangle([x0, y, x0 + 520, y + 116], fill=(24, 30, 38), outline=color, width=2)
        draw.text((x0 + 12, y + 10), scenario["label"], fill=color, font=normal)
        summary = scenario["summary"]
        draw.text((x0 + 12, y + 42), f"Active full/partial/miss: {summary['activeFullHitCount']} / {summary['activePartialHitCount']} / {summary['activeMissCount']}", fill=(232, 238, 244), font=small)
        draw.text((x0 + 12, y + 64), f"Active hits: {', '.join(summary['activeHitIds']) or 'none'}", fill=(202, 211, 221), font=small)
        draw.text((x0 + 12, y + 86), f"Strict unit hits: {summary['strictUnitTermHitCount']}", fill=(202, 211, 221), font=small)
        y += 136

    y += 8
    draw.rectangle([x0, y, x0 + 520, y + 112], fill=(40, 28, 18), outline=(111, 74, 30), width=2)
    draw.text((x0 + 12, y + 12), "Decision", fill=(255, 219, 137), font=normal)
    for i, line in enumerate(result["assessment"][:3]):
        draw.text((x0 + 12, y + 40 + i * 21), line[:78], fill=(255, 219, 137), font=small)
    sheet.save(SHEET, quality=94)


def main() -> None:
    article = load_json(ARTICLE_JSON)
    active = load_json(ACTIVE_TARGETS_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    p78_frame = load_json(P78_FRAME_JSON)

    page76 = next(page for page in article["pages"] if page["page"] == 76)
    width = page76["width"]
    overdose76 = find_overdose_word(article, 76)
    overdose78 = find_overdose_word(article, 78)
    c76 = center(overdose76["box"])
    c78 = center(overdose78["box"])
    dx = c76[0] - c78[0]
    dy = c76[1] - c78[1]

    p78_box = [float(v) for v in p78_source["sourceGraphic"]["box"]]
    active_targets = []
    id_map = {
        "buying_dip": "O4",
        "one_billion": "B4_text",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    for row in active["targets"]:
        active_targets.append(
            {
                "id": id_map[row["id"]],
                "sourceId": row["id"],
                "label": row["label"],
                "kind": "active-target",
                "box": [float(v) for v in row["box"]],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "visualState": row["visualState"],
                "source": "page76_active_target_crop_completion",
            }
        )
    candidates = active_targets + [row for row in unique_frame_candidates(p78_frame) if row["id"] not in {t["id"] for t in active_targets}]
    active_ids = {row["id"] for row in active_targets}

    scenarios = [
        {
            "id": "current_horizontal_mirror",
            "label": "current p78 horizontal mirror",
            "p76Box": mirror_box_x(p78_box, width),
            "transform": "p78 source box mirrored horizontally onto p76",
        },
        {
            "id": "same_layout_slot",
            "label": "same layout slot / no mirror",
            "p76Box": p78_box,
            "transform": "p78 source box placed at same page coordinates on p76",
        },
        {
            "id": "overdose_header_translation",
            "label": "OVERDOSE header translation",
            "p76Box": translate_box(p78_box, dx, dy),
            "transform": "p78 source box translated by p78->p76 OVERDOSE header center delta",
        },
    ]
    evaluated = [evaluate_scenario(scenario, candidates, active_ids) for scenario in scenarios]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "OVERDOSE header/layout registration test for p78 source graphic against page-76 active targets; no OCR or key derivation",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "activeTargets": rel(ACTIVE_TARGETS_JSON),
            "p78SourceGraphic": rel(P78_SOURCE_JSON),
            "p78FrameOrderRead": rel(P78_FRAME_JSON),
        },
        "overdoseWords": {
            "page76": {"box": overdose76["box"], "center": c76, "text": overdose76["text"]},
            "page78": {"box": overdose78["box"], "center": c78, "text": overdose78["text"]},
        },
        "headerRegistration": {"dx": round(dx, 4), "dy": round(dy, 4)},
        "p78SourceGraphicBox": p78_box,
        "activeTargets": active_targets,
        "scenarios": evaluated,
        "sheet": rel(SHEET),
        "assessment": [
            "The repeated OVERDOSE header placement gives only a tiny p78->p76 translation and is effectively a same-layout-slot test, not a fold/mirror instruction.",
            "The same-layout/header-translation frame fully covers B4 and G5 and partially clips O5, but it misses O4 and supplies no strict unit/order term.",
            "The current horizontal mirror frame preserves the known p78 registration benchmark, but it only clips O5 among the four active targets and also supplies no unit/order term.",
            "Therefore OVERDOSE header/layout registration is useful as a source-comparison benchmark only; it does not unlock extraction under the current scan.",
        ],
        "decision": {
            "overdoseHeaderRegistrationAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Use same-layout-slot contacts as a secondary validation check only if a future original-layout/source item explicitly points to repeated OVERDOSE page layout; otherwise keep the source/physical R1-R5 gate.",
        },
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# OVERDOSE Header Registration Gate",
        "",
        "Scope: compare the p78 source graphic against page-76 active targets using the repeated `OVERDOSE` header placement. No OCR, key derivation, hashing, seed/WIF checks, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- p76 OVERDOSE center: `{[round(v, 2) for v in c76]}`",
        f"- p78 OVERDOSE center: `{[round(v, 2) for v in c78]}`",
        f"- Header translation: `dx={dx:.2f}, dy={dy:.2f}`",
        "",
        "## Scenario Summary",
        "",
        "| scenario | p76 frame box | active full | active partial | active hits | strict unit hits |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for scenario in evaluated:
        summary = scenario["summary"]
        lines.append(
            f"| {scenario['label']} | `{[round(v, 2) for v in scenario['p76Box']]}` | "
            f"`{summary['activeFullHitCount']}` | `{summary['activePartialHitCount']}` | "
            f"{', '.join(summary['activeHitIds']) or '-'} | `{summary['strictUnitTermHitCount']}` |"
        )
    lines.extend(["", "## Active Target Contacts", ""])
    for scenario in evaluated:
        lines.append(f"### {scenario['label']}")
        lines.append("")
        lines.append("| target | overlap vs target | gap px | relation |")
        lines.append("|---|---:|---:|---|")
        for row in [r for r in scenario["rows"] if r["isActiveTarget"]]:
            lines.append(f"| `{row['id']}` {row['label']} | `{row['overlapVsTarget']}` | `{row['edgeGapPx']}` | `{row['relation']}` |")
        lines.append("")
    lines.extend(["## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", ""])
    lines.append("- `OVERDOSE` header/layout registration is closed as a current-scan selector.")
    lines.append("- Keep same-layout-slot contacts as source-comparison validation only; no selector was unlocked.")
    lines.append(f"- Next move: {result['decision']['nextMove']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("headerTranslation:", {"dx": round(dx, 4), "dy": round(dy, 4)})
    for scenario in evaluated:
        print(
            scenario["id"],
            "activeFull",
            scenario["summary"]["activeFullHitCount"],
            "activePartial",
            scenario["summary"]["activePartialHitCount"],
            "activeHits",
            ",".join(scenario["summary"]["activeHitIds"]) or "-",
            "unitHits",
            scenario["summary"]["strictUnitTermHitCount"],
        )


if __name__ == "__main__":
    main()
