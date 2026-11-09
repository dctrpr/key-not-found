#!/usr/bin/env python3
"""Check whether the clean Y/K+frame quartet supplies a unit/order rule.

The previous pass found that Y/K inside the 3-up/1-down rescue frame isolates
O4/B4/G5/O5. This bounded pass tests whether that isolated quartet itself
contains a source-backed unit/order, or whether it remains only a target
validation surface.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
YK_FILTER_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json"
ACTIVE_CROPS_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ACTIVE_RECON_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
ORDER_TRAP_JSON = ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "o4_frame_yk_unit_order_gate.json"
OUT_MD = OUT / "o4_frame_yk_unit_order_gate.md"
SHEET = OUT / "o4_frame_yk_unit_order_gate_sheet.jpg"


HARD_INSTRUCTION_TERMS = [
    "address",
    "above",
    "below",
    "edge",
    "extract",
    "font",
    "fold",
    "frame",
    "key",
    "left",
    "letter",
    "line",
    "mirror",
    "private",
    "read",
    "right",
    "seed",
    "select",
    "take",
    "word",
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


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$']+", text)


def normalize(text: str) -> str:
    return " ".join(words(text)).lower()


def hits(text: str) -> list[str]:
    norm = normalize(text)
    return [term for term in HARD_INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", norm)]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def make_rows() -> list[dict[str, Any]]:
    yk = load_json(YK_FILTER_JSON)
    active_crops = load_json(ACTIVE_CROPS_JSON)
    active_recon = load_json(ACTIVE_RECON_JSON)

    by_target = {row["id"]: row for row in active_crops["targets"]}
    recon_by_target = {row["id"]: row for row in active_recon["records"]}
    rows = []
    for group in yk["frameYkGroups"]:
        target_id = group["targetId"]
        crop_row = by_target[target_id]
        recon = recon_by_target[target_id]
        cx, cy = center(crop_row["box"])
        rows.append(
            {
                "targetId": target_id,
                "groupIndex": group["groupIndex"],
                "layerCode": group["layerCode"],
                "text": group["text"],
                "phrase": crop_row["phrase"],
                "box": crop_row["box"],
                "center": [round(cx, 2), round(cy, 2)],
                "pageLine": crop_row["pageLine"],
                "corridorIndex": crop_row["corridorIndex"],
                "visualState": crop_row["visualState"],
                "docmDominantFont": crop_row["docmDominantFont"],
                "docmBoldFraction": crop_row["docmBoldFraction"],
                "sentenceRow": recon["sentenceRow"],
                "phraseInitials": recon["phraseInitials"],
                "phraseEdges": recon["phraseEdges"],
                "leftBoundaryWord": recon["leftBoundaryWord"],
                "rightBoundaryWord": recon["rightBoundaryWord"],
                "aboveWord": recon["aboveWord"],
                "belowWord": recon["belowWord"],
            }
        )
    return rows


def stream_record(name: str, values: list[Any], source: str) -> dict[str, Any]:
    as_strings = [str(value) for value in values]
    joined_space = " ".join(as_strings)
    joined_compact = "".join(as_strings)
    return {
        "name": name,
        "source": source,
        "values": as_strings,
        "joinedSpace": joined_space,
        "joinedCompact": joined_compact,
        "hardInstructionHits": sorted(set(hits(joined_space) + hits(joined_compact))),
    }


def make_streams(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_order = sorted(rows, key=lambda row: row["groupIndex"])
    reverse_group_order = list(reversed(group_order))
    left_to_right = sorted(rows, key=lambda row: row["center"][0])
    right_to_left = list(reversed(left_to_right))

    def gaps(items: list[int]) -> list[int]:
        return [b - a for a, b in zip(items, items[1:])]

    streams: list[dict[str, Any]] = []
    for name, ordered, source in [
        ("group_order_target_ids", group_order, "existing p76 signal group order"),
        ("reverse_group_order_target_ids", reverse_group_order, "reverse of p76 signal group order"),
        ("left_to_right_target_ids", left_to_right, "x-center spatial order"),
        ("right_to_left_target_ids", right_to_left, "reverse x-center spatial order"),
    ]:
        streams.append(stream_record(name, [row["targetId"] for row in ordered], source))

    streams.extend(
        [
            stream_record("group_order_layer_codes", [row["layerCode"] for row in group_order], "Y/K frame filter"),
            stream_record("group_indexes", [row["groupIndex"] for row in group_order], "p76 signal group order"),
            stream_record("group_index_gaps", gaps([row["groupIndex"] for row in group_order]), "p76 signal group order"),
            stream_record("page_lines", [row["pageLine"] for row in group_order], "readable/upright line order"),
            stream_record("page_line_gaps", gaps([row["pageLine"] for row in group_order]), "readable/upright line order"),
            stream_record("corridor_indexes", [row["corridorIndex"] for row in group_order], "lower-corridor line order"),
            stream_record("corridor_gaps", gaps([row["corridorIndex"] for row in group_order]), "lower-corridor line order"),
            stream_record("sentence_rows", [row["sentenceRow"] for row in group_order], "plain/DOCM sentence rows"),
            stream_record("phrase_initials", [row["phraseInitials"] for row in group_order], "target phrase text"),
            stream_record("phrase_edges", [row["phraseEdges"] for row in group_order], "target phrase text"),
            stream_record("left_boundary_words", [row["leftBoundaryWord"] for row in group_order], "active line unit reconciliation"),
            stream_record("right_boundary_words", [row["rightBoundaryWord"] for row in group_order], "active line unit reconciliation"),
            stream_record("above_words", [row["aboveWord"] for row in group_order], "active line unit reconciliation"),
            stream_record("below_words", [row["belowWord"] for row in group_order], "active line unit reconciliation"),
            stream_record("x_center_order_target_ids", [row["targetId"] for row in left_to_right], "x-center spatial order"),
            stream_record("y_center_order_target_ids", [row["targetId"] for row in group_order], "y-center/spread vertical order"),
        ]
    )
    return streams


def draw_sheet(result: dict[str, Any]) -> None:
    crop = [180, 2070, 2315, 3065]
    scale = 0.41
    panel = Image.open(PAGE_IMAGE).convert("RGB").crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 122
    footer_h = 455
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "O4 Frame Y/K Unit/Order Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 56),
        "The quartet is isolated; this checks whether a unit/order is actually supplied.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text((margin, 84), "Orange/grey boxes = Y/K targets. Cyan numbers show vertical/group order; magenta shows x-order.", fill=(176, 186, 198), font=small)
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    colors = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for order, row in enumerate(result["groupOrderRows"], start=1):
        box = row["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=colors[row["visualState"]], width=4)
        draw.ellipse([sx(box[0]) - 12, sy(box[1]) - 20, sx(box[0]) + 12, sy(box[1]) + 4], fill="#38bdf8")
        draw.text((sx(box[0]) - 4, sy(box[1]) - 19), str(order), fill="#07111f", font=small)

    for order, row in enumerate(result["leftToRightRows"], start=1):
        cx, cy = row["center"]
        draw.text((sx(cx) - 7, sy(cy) + 18), str(order), fill="#ff73c8", font=normal)

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Order Comparison", fill=(238, 243, 248), font=normal)
    y += 30
    notes = [
        f"Group/vertical order: {result['summary']['groupOrderTargetIds']}.",
        f"Left-to-right order: {result['summary']['leftToRightTargetIds']}.",
        f"Line/corridor order: {result['summary']['pageLines']} / {result['summary']['corridorIndexes']}.",
        f"Gap patterns: group {result['summary']['groupIndexGaps']}, line {result['summary']['pageLineGaps']}, corridor {result['summary']['corridorGaps']}.",
        f"Hard instruction hits across bounded streams: {result['summary']['totalHardInstructionHitCount']}.",
        "Result: the quartet is located, but unit/order permission is still absent.",
    ]
    for note in notes:
        draw.text((margin, y), note[:126], fill=(255, 219, 137), font=normal)
        y += 25

    y += 12
    draw.text((margin, y), "Selected Streams", fill=(238, 243, 248), font=normal)
    y += 26
    for stream in result["streamRecords"][:12]:
        draw.text((margin, y), f"{stream['name']}: {stream['joinedSpace']}"[:128], fill="#c6d1df", font=mono)
        y += 21

    sheet.save(SHEET, quality=94)


def main() -> None:
    rows = make_rows()
    group_order = sorted(rows, key=lambda row: row["groupIndex"])
    left_to_right = sorted(rows, key=lambda row: row["center"][0])
    streams = make_streams(rows)
    all_hits = sorted({hit for stream in streams for hit in stream["hardInstructionHits"]})
    order_trap = load_json(ORDER_TRAP_JSON)

    def gaps(values: list[int]) -> list[int]:
        return [b - a for a, b in zip(values, values[1:])]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Y/K+frame quartet unit/order gate; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "ykFilterControl": rel(YK_FILTER_JSON),
            "activeCropAuthority": rel(ACTIVE_CROPS_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_RECON_JSON),
            "activeOrderOrientationTrap": rel(ORDER_TRAP_JSON),
        },
        "groupOrderRows": group_order,
        "leftToRightRows": left_to_right,
        "streamRecords": streams,
        "orientationTrapSummary": order_trap.get("summary", {}),
        "summary": {
            "isolatedTargetCount": len(rows),
            "groupOrderTargetIds": [row["targetId"] for row in group_order],
            "leftToRightTargetIds": [row["targetId"] for row in left_to_right],
            "groupOrderLayerCodes": "".join(row["layerCode"] for row in group_order),
            "pageLines": [row["pageLine"] for row in group_order],
            "corridorIndexes": [row["corridorIndex"] for row in group_order],
            "groupIndexes": [row["groupIndex"] for row in group_order],
            "groupIndexGaps": gaps([row["groupIndex"] for row in group_order]),
            "pageLineGaps": gaps([row["pageLine"] for row in group_order]),
            "corridorGaps": gaps([row["corridorIndex"] for row in group_order]),
            "boundedStreamCount": len(streams),
            "totalHardInstructionHits": all_hits,
            "totalHardInstructionHitCount": len(all_hits),
            "orientationAmbiguity": "YKKY/OBBO are palindromic color-state patterns; line/corridor order remains the readable/upright authority.",
            "sourceBackedUnitOrder": False,
            "selectorUnlocked": False,
        },
        "decision": {
            "o4FrameYkUnitOrderGate": "target_surface_only_no_unit_order_rule",
            "selectorUnlocked": False,
            "reason": "Y/K+frame isolates the quartet, but bounded unit/order streams have zero hard instruction hits and spatial orders disagree unless line/corridor order is assumed from existing authority.",
            "nextMove": "Keep O4/B4/G5/O5 as a validation surface. Reopen extraction only if source wording names a unit and order such as group order, line order, word, letter, edge, or x-order.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O4 Frame Y/K Unit/Order Gate",
        "",
        "Scope: check whether the clean `Y/K + frame` quartet supplies a source-backed unit/order. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Isolated target count: `{result['summary']['isolatedTargetCount']}`",
        f"- Group/vertical target order: `{result['summary']['groupOrderTargetIds']}`",
        f"- Left-to-right target order: `{result['summary']['leftToRightTargetIds']}`",
        f"- Group-order layer codes: `{result['summary']['groupOrderLayerCodes']}`",
        f"- Page lines: `{result['summary']['pageLines']}`",
        f"- Corridor indexes: `{result['summary']['corridorIndexes']}`",
        f"- Group index gaps: `{result['summary']['groupIndexGaps']}`",
        f"- Page/corridor gaps: `{result['summary']['pageLineGaps']}` / `{result['summary']['corridorGaps']}`",
        f"- Bounded streams checked: `{result['summary']['boundedStreamCount']}`",
        f"- Total hard instruction hits: `{all_hits}`",
        f"- Source-backed unit/order: `{result['summary']['sourceBackedUnitOrder']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Order Comparison",
        "",
        "| order mode | target ids | source |",
        "|---|---|---|",
        f"| group/vertical | `{' -> '.join(result['summary']['groupOrderTargetIds'])}` | existing p76 signal group order / readable line order |",
        f"| left-to-right | `{' -> '.join(result['summary']['leftToRightTargetIds'])}` | x-center spatial order |",
        "",
        "## Bounded Streams",
        "",
        "| stream | values | hard hits |",
        "|---|---|---|",
    ]
    for stream in streams:
        lines.append(
            f"| `{stream['name']}` | `{stream['joinedSpace']}` | `{', '.join(stream['hardInstructionHits']) or '-'}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `Y/K + frame` is a strong locator: it isolates exactly O4/B4/G5/O5.",
            "- It still does not provide a source-backed unit/order rule.",
            "- Group/vertical order and left-to-right spatial order disagree, and color/state patterns are palindromic, so orientation/order cannot be inferred from color alone.",
            "- Keep the quartet as a validation surface only until source wording names a unit and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("groupOrderTargetIds:", result["summary"]["groupOrderTargetIds"])
    print("leftToRightTargetIds:", result["summary"]["leftToRightTargetIds"])
    print("boundedStreamCount:", result["summary"]["boundedStreamCount"])
    print("totalHardInstructionHitCount:", len(all_hits))
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()
