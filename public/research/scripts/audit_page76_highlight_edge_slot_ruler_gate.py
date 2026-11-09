#!/usr/bin/env python3
"""Audit page-76 highlight edges as OVERDOSE slot/fold rulers.

This bounded geometry pass tests whether page-76 highlight edges/centers can
act as a source-visible ruler for folded or mirrored OVERDOSE-slot reading.
It uses the existing 3D article map and actual C9 OVERDOSE header glyph slots.

No OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_highlight_edge_slot_ruler_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_highlight_edge_slot_ruler_gate.json"
OUT_MD = OUT / "page76_highlight_edge_slot_ruler_gate.md"
OUT_SHEET = OUT / "page76_highlight_edge_slot_ruler_gate_sheet.jpg"

ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE76_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
ACTIVE_HIGHLIGHT_IDS = {"p76_orange_4", "p76_orange_5"}
STRICT_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "first",
    "fold",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "line",
    "mirror",
    "order",
    "outside",
    "read",
    "reverse",
    "right",
    "row",
    "side",
    "slot",
    "take",
    "top",
    "word",
    "words",
}
LAYOUT_TERMS = ("OVER", "DOSE")
LINE_EPS = 8.0
STRICT_SLOT_THRESHOLD = 4.0
LOOSE_SLOT_THRESHOLD = 25.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def token(text: str) -> str:
    return "".join(ch.lower() for ch in str(text) if ch.isalnum())


def page76(article: dict[str, Any]) -> dict[str, Any]:
    return next(page for page in article["pages"] if page.get("page") == 76)


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def active_rows(c9: dict[str, Any]) -> list[dict[str, Any]]:
    projection = next(
        item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"
    )
    by_short = {row["shortId"]: row for row in projection.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        row["center"] = center(row["box"])
        rows.append(row)
    return rows


def slot_rows(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame")]
    projection = next(
        item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"
    )
    rows = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "index": int(slot["index"]),
                "letter": str(slot["letter"]),
                "left": float(slot["left"]),
                "right": float(slot["right"]),
                "center": (float(slot["left"]) + float(slot["right"])) / 2.0,
            }
        )
    return rows


def slot_boundaries(slots: list[dict[str, Any]]) -> list[float]:
    if not slots:
        return []
    return [slots[0]["left"]] + [slot["right"] for slot in slots]


def slot_for_x(slots: list[dict[str, Any]], x: float) -> str:
    for slot in slots:
        if slot["left"] <= x <= slot["right"]:
            return slot["letter"]
    return "."


def layout_hits(stream: str) -> list[str]:
    compact = stream.replace(".", "")
    return [term for term in LAYOUT_TERMS if term in compact]


def collect_axes(highlights: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    vertical = []
    horizontal = []
    for highlight in highlights:
        box = [float(v) for v in highlight["box"]]
        cx, cy = center(box)
        base = {
            "highlightId": highlight["id"],
            "kind": highlight.get("kind"),
            "box": [round(v, 2) for v in box],
            "isActiveHighlight": highlight["id"] in ACTIVE_HIGHLIGHT_IDS,
        }
        for role, value in [("left", box[0]), ("centerX", cx), ("right", box[2])]:
            vertical.append({**base, "axisRole": role, "axisX": value})
        for role, value in [("top", box[1]), ("centerY", cy), ("bottom", box[3])]:
            horizontal.append({**base, "axisRole": role, "axisY": value})
    return vertical, horizontal


def words_near_vertical_axis(words: list[dict[str, Any]], axis_x: float) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        box = [float(v) for v in word["box"]]
        if box[0] - LINE_EPS <= axis_x <= box[2] + LINE_EPS:
            tok = token(word.get("token") or word.get("text") or "")
            if tok:
                hits.append(
                    {
                        "text": word.get("text", ""),
                        "token": tok,
                        "box": [round(v, 2) for v in box],
                        "strictInstruction": tok in STRICT_TERMS,
                    }
                )
    return hits


def words_near_horizontal_axis(words: list[dict[str, Any]], axis_y: float) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        box = [float(v) for v in word["box"]]
        if box[1] - LINE_EPS <= axis_y <= box[3] + LINE_EPS:
            tok = token(word.get("token") or word.get("text") or "")
            if tok:
                hits.append(
                    {
                        "text": word.get("text", ""),
                        "token": tok,
                        "box": [round(v, 2) for v in box],
                        "strictInstruction": tok in STRICT_TERMS,
                    }
                )
    return hits


def analyze_vertical_axes(
    axes: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    slots: list[dict[str, Any]],
    words: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    boundaries = slot_boundaries(slots)
    direct_stream = "".join(slot_for_x(slots, target["center"][0]) for target in targets)
    for axis in axes:
        mirrored_points = []
        stream = ""
        inside = 0
        for target in targets:
            mirrored_x = 2.0 * axis["axisX"] - target["center"][0]
            letter = slot_for_x(slots, mirrored_x)
            if letter != ".":
                inside += 1
            stream += letter
            mirrored_points.append(
                {
                    "target": target["shortId"],
                    "originalX": round(target["center"][0], 3),
                    "mirroredX": round(mirrored_x, 3),
                    "slotLetter": letter,
                }
            )
        near_words = words_near_vertical_axis(words, axis["axisX"])
        strict_words = [word for word in near_words if word["strictInstruction"]]
        nearest_boundary_delta = min((abs(axis["axisX"] - b) for b in boundaries), default=9999.0)
        rows.append(
            {
                **axis,
                "axisX": round(axis["axisX"], 3),
                "directActiveStream": direct_stream,
                "mirroredActiveStream": stream,
                "mirroredInsideSlotCount": inside,
                "allFourMirroredInsideSlots": inside == len(targets),
                "layoutTermHits": layout_hits(stream),
                "nearestSlotBoundaryDeltaPx": round(nearest_boundary_delta, 3),
                "strictSlotBoundaryContact": nearest_boundary_delta <= STRICT_SLOT_THRESHOLD,
                "looseSlotBoundaryContact": nearest_boundary_delta <= LOOSE_SLOT_THRESHOLD,
                "axisWordHitCount": len(near_words),
                "strictInstructionHitCount": len(strict_words),
                "strictInstructionTerms": sorted({word["token"] for word in strict_words}),
                "axisTextPreview": " ".join(word["text"] for word in near_words[:24]),
                "mirroredPoints": mirrored_points,
            }
        )
    return rows


def analyze_horizontal_axes(
    axes: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    frame: list[float],
    words: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for axis in axes:
        points = []
        inside = 0
        for target in targets:
            mirrored_y = 2.0 * axis["axisY"] - target["center"][1]
            is_inside = frame[1] <= mirrored_y <= frame[3]
            inside += int(is_inside)
            points.append(
                {
                    "target": target["shortId"],
                    "originalY": round(target["center"][1], 3),
                    "mirroredY": round(mirrored_y, 3),
                    "insideC9FrameY": is_inside,
                }
            )
        near_words = words_near_horizontal_axis(words, axis["axisY"])
        strict_words = [word for word in near_words if word["strictInstruction"]]
        rows.append(
            {
                **axis,
                "axisY": round(axis["axisY"], 3),
                "mirroredInsideC9FrameYCount": inside,
                "allFourMirroredInsideC9FrameY": inside == len(targets),
                "axisWordHitCount": len(near_words),
                "strictInstructionHitCount": len(strict_words),
                "strictInstructionTerms": sorted({word["token"] for word in strict_words}),
                "axisTextPreview": " ".join(word["text"] for word in near_words[:24]),
                "mirroredPoints": points,
            }
        )
    return rows


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_sheet(result: dict[str, Any]) -> None:
    image = Image.open(PAGE76_IMG).convert("RGB")
    crop = [220, 2050, 2320, 3060]
    scale = 0.42
    panel = image.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    width = 1780
    height = 1120
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    sheet.paste(panel, (24, 132))
    draw.rectangle((0, 0, width, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Page 76 Highlight Edge Slot Ruler Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Highlight left/center/right axes mirrored against active centers and actual OVERDOSE glyph slots.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1020, 18),
        f"vertical axes {summary['verticalAxisCount']} | all-four mirrored slots {summary['allFourMirroredInsideSlotAxisCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1020, 48),
        f"strict instruction axis hits {summary['strictInstructionAxisHitCount']} | sourceR3 {summary['sourceBackedR3BridgeHitCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    def sx(x: float) -> float:
        return 24 + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return 132 + (y - crop[1]) * scale

    frame = result["c9Frame"]
    draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline=(40, 170, 230), width=3)
    for slot in result["slots"]:
        draw.line([(sx(slot["left"]), sy(frame[1])), (sx(slot["left"]), sy(frame[3]))], fill=(40, 170, 230), width=1)
        draw.text((sx(slot["center"]) - 5, sy(frame[1]) - 18), slot["letter"], fill=(0, 90, 150), font=tiny)
    for highlight in result["page76Highlights"]:
        box = highlight["box"]
        color = (230, 95, 20) if highlight["id"] in ACTIVE_HIGHLIGHT_IDS else (230, 180, 20)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
    for row in result["verticalRows"]:
        if row["isActiveHighlight"]:
            draw.line([(sx(row["axisX"]), sy(frame[1])), (sx(row["axisX"]), sy(frame[3]))], fill=(220, 30, 30), width=2)

    table_y = 590
    draw.text((24, table_y), "Closest vertical highlight rulers", fill=(30, 34, 40), font=small)
    table_y += 24
    headers = ["highlight", "role", "x", "mirror stream", "inside", "layout", "slot gap", "strict", "axis text"]
    xs = [24, 160, 245, 320, 440, 505, 585, 665, 730]
    for x, header in zip(xs, headers):
        draw.text((x, table_y), header, fill=(65, 70, 78), font=tiny)
    table_y += 18
    rows = sorted(
        result["verticalRows"],
        key=lambda row: (
            -row["mirroredInsideSlotCount"],
            row["nearestSlotBoundaryDeltaPx"],
            row["highlightId"],
            row["axisRole"],
        ),
    )[:16]
    for row in rows:
        values = [
            row["highlightId"],
            row["axisRole"],
            f"{row['axisX']:.1f}",
            row["mirroredActiveStream"],
            str(row["mirroredInsideSlotCount"]),
            ",".join(row["layoutTermHits"]),
            f"{row['nearestSlotBoundaryDeltaPx']:.1f}",
            str(row["strictInstructionHitCount"]),
            row["axisTextPreview"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, table_y), str(value)[:72], fill=(25, 28, 34), font=tiny)
        table_y += 22
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Page 76 Highlight Edge Slot Ruler Gate",
        "",
        "Scope: tested page-76 highlight edges/centers as possible fold or mirror rulers against actual C9 OVERDOSE header glyph slots and active O4/B4/G5/O5 centers. No key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Highlights / vertical axes / horizontal axes: `{summary['highlightCount']}` / `{summary['verticalAxisCount']}` / `{summary['horizontalAxisCount']}`",
        f"- Direct active center stream: `{summary['directActiveStream']}`",
        f"- All-four mirrored-inside-slot vertical axes: `{summary['allFourMirroredInsideSlotAxisCount']}`",
        f"- Max mirrored active centers inside slots: `{summary['maxMirroredInsideSlotCount']}`",
        f"- Vertical axes with layout-term stream hits: `{summary['verticalLayoutTermAxisCount']}`",
        f"- Strict / loose slot-boundary contacts: `{summary['strictSlotBoundaryContactCount']}` / `{summary['looseSlotBoundaryContactCount']}`",
        f"- Horizontal axes with all-four mirrored inside C9 frame Y: `{summary['horizontalAllFourInsideFrameYCount']}`",
        f"- Strict instruction axis hits: `{summary['strictInstructionAxisHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Vertical Rulers",
        "",
        "| highlight | role | active? | x | mirrored stream | inside | layout hits | slot gap | strict hits | axis text preview |",
        "|---|---|---:|---:|---|---:|---|---:|---:|---|",
    ]
    for row in result["verticalRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['highlightId']}`",
                    f"`{row['axisRole']}`",
                    str(row["isActiveHighlight"]),
                    f"{row['axisX']:.1f}",
                    f"`{row['mirroredActiveStream']}`",
                    str(row["mirroredInsideSlotCount"]),
                    ",".join(row["layoutTermHits"]) or "-",
                    f"{row['nearestSlotBoundaryDeltaPx']:.1f}",
                    str(row["strictInstructionHitCount"]),
                    row["axisTextPreview"].replace("|", "\\|")[:140],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote page-76 highlight edges/centers as OVERDOSE slot rulers or fold axes.",
            "- The direct active center stream remains the already-known `OVED`; highlight-edge mirroring does not produce an all-four in-slot active stream or source-backed unit/order wording.",
            "- Slot-boundary contacts and layout-term fragments occur as broad geometry coincidences, not as a complete active-quartet selector.",
            "",
            "## Next Move",
            "",
            "- Keep highlight edges as visual/source-validation context only. The best next move remains external/original-layout source validation or raw clue wording that names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    article = load_json(ARTICLE_MAP)
    page = page76(article)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    frame = [float(v) for v in c9.get("c9Frame")]
    targets = active_rows(c9)
    slots = slot_rows(c9)
    highlights = [{**h, "box": [float(v) for v in h["box"]]} for h in page.get("highlights", [])]
    vertical_axes, horizontal_axes = collect_axes(highlights)
    vertical_rows = analyze_vertical_axes(vertical_axes, targets, slots, page.get("words", []))
    horizontal_rows = analyze_horizontal_axes(horizontal_axes, targets, frame, page.get("words", []))
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))

    direct_stream = "".join(slot_for_x(slots, target["center"][0]) for target in targets)
    strict_axis_hits = sum(row["strictInstructionHitCount"] for row in vertical_rows + horizontal_rows)
    vertical_layout_axes = [row for row in vertical_rows if row["layoutTermHits"]]
    summary = {
        "decision": "page76_highlight_edge_slot_ruler_no_selector",
        "highlightCount": len(highlights),
        "verticalAxisCount": len(vertical_rows),
        "horizontalAxisCount": len(horizontal_rows),
        "directActiveStream": direct_stream,
        "allFourMirroredInsideSlotAxisCount": sum(
            row["allFourMirroredInsideSlots"] for row in vertical_rows
        ),
        "maxMirroredInsideSlotCount": max(
            (row["mirroredInsideSlotCount"] for row in vertical_rows), default=0
        ),
        "verticalLayoutTermAxisCount": len(vertical_layout_axes),
        "strictSlotBoundaryContactCount": sum(
            row["strictSlotBoundaryContact"] for row in vertical_rows
        ),
        "looseSlotBoundaryContactCount": sum(
            row["looseSlotBoundaryContact"] for row in vertical_rows
        ),
        "activeHighlightLooseSlotBoundaryContactCount": sum(
            row["looseSlotBoundaryContact"] and row["isActiveHighlight"] for row in vertical_rows
        ),
        "horizontalAllFourInsideFrameYCount": sum(
            row["allFourMirroredInsideC9FrameY"] for row in horizontal_rows
        ),
        "strictInstructionAxisHitCount": strict_axis_hits,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"highlights={summary['highlightCount']}|vAxes={summary['verticalAxisCount']}|"
        f"hAxes={summary['horizontalAxisCount']}|direct={direct_stream}|"
        f"allSlot={summary['allFourMirroredInsideSlotAxisCount']}|"
        f"maxSlot={summary['maxMirroredInsideSlotCount']}|"
        f"layoutAxes={summary['verticalLayoutTermAxisCount']}|"
        f"strictSlot={summary['strictSlotBoundaryContactCount']}|"
        f"looseSlot={summary['looseSlotBoundaryContactCount']}|"
        f"hAllY={summary['horizontalAllFourInsideFrameYCount']}|"
        f"strictAxis={strict_axis_hits}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 highlight edges/centers tested as fold/mirror rulers against C9 OVERDOSE glyph slots and active target centers.",
        "inputs": {
            "articleMap": rel(ARTICLE_MAP),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "c9Frame": frame,
        "slots": slots,
        "targets": targets,
        "page76Highlights": highlights,
        "verticalRows": vertical_rows,
        "horizontalRows": horizontal_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()
