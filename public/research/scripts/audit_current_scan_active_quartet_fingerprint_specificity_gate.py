#!/usr/bin/env python3
"""Check whether the active p76 quartet fingerprint is specific in scan boxes.

This bounded pass does not generate key material or try extraction. It uses the
current scan/PDF-derived page-76 highlight and annotation boxes as available
controls, then asks whether any top-to-bottom quartet besides O4/B4/G5/O5
matches the combined active fingerprint:

Y/K state stream YKKY, color stream OBBO, line-gap estimate 3/2/5, and C9
OVERDOSE center-slot stream OVED.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from math import comb
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_quartet_fingerprint_specificity_gate.json"
OUT_MD = OUT / "current_scan_active_quartet_fingerprint_specificity_gate.md"
OUT_SHEET = OUT / "current_scan_active_quartet_fingerprint_specificity_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HIGHLIGHT_AUDIT = ROOT / "analysis_outputs/highlight_audit/highres_highlight_audit.json"
C9_SLOTS = ROOT / (
    "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_STATE_STREAM = "YKKY"
TARGET_COLOR_STREAM = "OBBO"
TARGET_LINE_GAPS = [3, 2, 5]
TARGET_SLOT_STREAM = "OVED"


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def center(box: list[float]) -> tuple[float, float]:
    return ((float(box[0]) + float(box[2])) / 2.0, (float(box[1]) + float(box[3])) / 2.0)


def area(box: list[float]) -> float:
    return max(0.0, float(box[2]) - float(box[0])) * max(0.0, float(box[3]) - float(box[1]))


def iou(left: list[float], right: list[float]) -> float:
    x0 = max(float(left[0]), float(right[0]))
    y0 = max(float(left[1]), float(right[1]))
    x1 = min(float(left[2]), float(right[2]))
    y1 = min(float(left[3]), float(right[3]))
    inter = area([x0, y0, x1, y1])
    denom = area(left) + area(right) - inter
    return 0.0 if denom <= 0 else inter / denom


def fit_line_pitch(active_rows: list[dict[str, Any]]) -> dict[str, float]:
    xs = [float(row["pageLine"]) for row in active_rows]
    ys = [center(row["box"])[1] for row in active_rows]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    residuals = [round(y - (slope * x + intercept), 6) for x, y in zip(xs, ys)]
    return {"slopePxPerLine": slope, "interceptPx": intercept, "activeResidualsPx": residuals}


def slot_for_x(slots: list[dict[str, Any]], x: float) -> dict[str, Any]:
    for slot in slots:
        if float(slot["left"]) <= x < float(slot["right"]):
            return {"index": int(slot["index"]), "letter": str(slot["letter"]), "inside": True}
    nearest = min(
        slots,
        key=lambda slot: min(abs(x - float(slot["left"])), abs(x - float(slot["right"]))),
    )
    return {"index": int(nearest["index"]), "letter": str(nearest["letter"]), "inside": False}


def state_and_color_from_kind(kind: str) -> tuple[str, str]:
    if "orange" in kind:
        return "Y", "O"
    if "grey" in kind or "black" in kind:
        return "K", "B"
    return "?", "?"


def active_candidates(active_index: dict[str, Any], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        short_id = row.get("shortId")
        if short_id not in TARGET_ORDER:
            continue
        box = [float(v) for v in row["box"]]
        cx, cy = center(box)
        slot = slot_for_x(slots, cx)
        rows.append(
            {
                "id": short_id,
                "source": "active_index_slot",
                "label": row.get("phrase", ""),
                "box": box,
                "centerX": round(cx, 3),
                "centerY": round(cy, 3),
                "visualState": row.get("visualState"),
                "colorCode": "O" if row.get("color") == "orange" else "B",
                "pageLine": int(row.get("pageLine")),
                "corridorIndex": int(row.get("corridorIndex")),
                "slotIndex": slot["index"],
                "slotLetter": slot["letter"],
                "slotInside": slot["inside"],
                "isActiveTarget": True,
                "activeShortId": short_id,
            }
        )
    return sorted(rows, key=lambda row: TARGET_ORDER.index(row["id"]))


def highlight_candidates(highlight_audit: dict[str, Any], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in highlight_audit.get("annotatedColorRows", []):
        if row.get("page") != 76 or not row.get("box"):
            continue
        state, color = state_and_color_from_kind(str(row.get("kind", "")))
        box = [float(v) for v in row["box"]]
        cx, cy = center(box)
        slot = slot_for_x(slots, cx)
        rows.append(
            {
                "id": row.get("id"),
                "source": "annotated_color",
                "label": row.get("expected") or row.get("ocrText", ""),
                "box": box,
                "centerX": round(cx, 3),
                "centerY": round(cy, 3),
                "visualState": state,
                "colorCode": color,
                "pageLine": None,
                "corridorIndex": None,
                "slotIndex": slot["index"],
                "slotLetter": slot["letter"],
                "slotInside": slot["inside"],
                "isActiveTarget": False,
                "activeShortId": None,
            }
        )
    for row in highlight_audit.get("visualOrangeRows", []):
        if row.get("page") != 76 or not row.get("box"):
            continue
        box = [float(v) for v in row["box"]]
        cx, cy = center(box)
        slot = slot_for_x(slots, cx)
        rows.append(
            {
                "id": row.get("id"),
                "source": "visual_orange",
                "label": row.get("ocrText", ""),
                "box": box,
                "centerX": round(cx, 3),
                "centerY": round(cy, 3),
                "visualState": "Y",
                "colorCode": "O",
                "pageLine": None,
                "corridorIndex": None,
                "slotIndex": slot["index"],
                "slotLetter": slot["letter"],
                "slotInside": slot["inside"],
                "isActiveTarget": False,
                "activeShortId": None,
            }
        )
    return rows


def dedupe_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"active_index_slot": 0, "visual_orange": 1, "annotated_color": 2}
    kept: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: (priority[item["source"]], item["centerY"])):
        duplicate = False
        for existing in kept:
            same_center = (
                abs(float(row["centerX"]) - float(existing["centerX"])) < 2.0
                and abs(float(row["centerY"]) - float(existing["centerY"])) < 2.0
            )
            if same_center or iou(row["box"], existing["box"]) > 0.90:
                duplicate = True
                break
        if not duplicate:
            kept.append(row)
    return sorted(kept, key=lambda item: item["centerY"])


def quartet_row(
    ordinal: int, rows: tuple[dict[str, Any], ...], line_pitch_px: float
) -> dict[str, Any]:
    ordered = tuple(sorted(rows, key=lambda row: row["centerY"]))
    y_gaps_px = [
        round(float(b["centerY"]) - float(a["centerY"]), 3)
        for a, b in zip(ordered, ordered[1:])
    ]
    estimated_line_gaps = [int(round(gap / line_pitch_px)) for gap in y_gaps_px]
    state_stream = "".join(str(row["visualState"]) for row in ordered)
    color_stream = "".join(str(row["colorCode"]) for row in ordered)
    slot_stream = "".join(str(row["slotLetter"]) for row in ordered)
    active_short_ids = [row["activeShortId"] for row in ordered if row.get("activeShortId")]
    flags = {
        "matchesStateStream": state_stream == TARGET_STATE_STREAM,
        "matchesColorStream": color_stream == TARGET_COLOR_STREAM,
        "matchesLineGapEstimate": estimated_line_gaps == TARGET_LINE_GAPS,
        "matchesSlotStream": slot_stream == TARGET_SLOT_STREAM,
        "exactActiveQuartet": active_short_ids == TARGET_ORDER and len(active_short_ids) == 4,
    }
    flags["matchesCombinedFingerprint"] = all(
        [
            flags["matchesStateStream"],
            flags["matchesColorStream"],
            flags["matchesLineGapEstimate"],
            flags["matchesSlotStream"],
        ]
    )
    return {
        "ordinal": ordinal,
        "ids": [str(row["id"]) for row in ordered],
        "sources": [str(row["source"]) for row in ordered],
        "labels": [str(row.get("label", "")) for row in ordered],
        "activeShortIds": active_short_ids,
        "activeTargetCount": len(active_short_ids),
        "centerXs": [row["centerX"] for row in ordered],
        "centerYs": [row["centerY"] for row in ordered],
        "visualStateStream": state_stream,
        "colorStream": color_stream,
        "slotStream": slot_stream,
        "slotIndexes": [row["slotIndex"] for row in ordered],
        "yGapsPx": y_gaps_px,
        "estimatedLineGaps": estimated_line_gaps,
        **flags,
    }


def build_quartets(candidates: list[dict[str, Any]], line_pitch_px: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, combo_rows in enumerate(itertools.combinations(candidates, 4), start=1):
        rows.append(quartet_row(ordinal, combo_rows, line_pitch_px))
    return rows


def count(rows: list[dict[str, Any]], key: str) -> int:
    return sum(1 for row in rows if row.get(key))


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


def draw_sheet(
    candidates: list[dict[str, Any]],
    summary: dict[str, Any],
    line_gap_hits: list[dict[str, Any]],
    slot_hits: list[dict[str, Any]],
    combined_hits: list[dict[str, Any]],
) -> None:
    width, height = 1800, 1180
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = font(28)
    small_font = font(16)
    tiny_font = font(13)

    draw.rectangle((0, 0, width, 104), fill=(28, 32, 38))
    draw.text((24, 18), "Current Scan Active Quartet Fingerprint Specificity", fill="white", font=title_font)
    draw.text(
        (24, 62),
        (
            f"candidates {summary['candidateRowCount']} | quartets {summary['quartetCount']} | "
            f"YKKY/OBBO {summary['stateColorHitCount']} | gap 3/2/5 {summary['stateColorLineGapHitCount']} | "
            f"combined {summary['combinedFingerprintHitCount']} | fingerprint {summary['specificityFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny_font,
    )

    y = 126
    draw.text((24, y), "Candidate rows, top to bottom", fill=(40, 40, 40), font=small_font)
    y += 28
    headers = ["id", "src", "state", "color", "slot", "center", "label"]
    xs = [24, 230, 390, 470, 560, 650, 840]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 22
    for idx, row in enumerate(candidates):
        fill = (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        outline = (242, 164, 54) if row["isActiveTarget"] else None
        draw.rectangle((18, y - 4, width - 18, y + 36), fill=fill, outline=outline)
        draw.text((xs[0], y), str(row["id"])[:22], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[1], y), str(row["source"])[:16], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[2], y), str(row["visualState"]), fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[3], y), str(row["colorCode"]), fill=(30, 30, 30), font=tiny_font)
        draw.text(
            (xs[4], y),
            f"{row['slotLetter']}{row['slotIndex']}",
            fill=(30, 30, 30),
            font=tiny_font,
        )
        draw.text(
            (xs[5], y),
            f"{row['centerX']:.1f},{row['centerY']:.1f}",
            fill=(30, 30, 30),
            font=tiny_font,
        )
        draw.text((xs[6], y), str(row.get("label", ""))[:106], fill=(30, 30, 30), font=tiny_font)
        y += 42

    y += 18
    draw.text((24, y), "State/color plus 3/2/5 line-gap hits", fill=(40, 40, 40), font=small_font)
    y += 28
    for idx, row in enumerate(line_gap_hits[:8]):
        fill = (252, 247, 238) if idx % 2 == 0 else (244, 239, 230)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text(
            (24, y),
            (
                f"{idx + 1}. {' | '.join(row['ids'])}  slots={row['slotStream']} "
                f"gaps={'/'.join(map(str, row['estimatedLineGaps']))} active={row['activeTargetCount']}/4"
            ),
            fill=(35, 35, 35),
            font=tiny_font,
        )
        y += 44

    y += 12
    draw.text((24, y), "Slot-stream OVED hits", fill=(40, 40, 40), font=small_font)
    y += 28
    for idx, row in enumerate(slot_hits[:8]):
        fill = (240, 247, 252) if idx % 2 == 0 else (230, 240, 248)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text(
            (24, y),
            (
                f"{idx + 1}. {' | '.join(row['ids'])}  state={row['visualStateStream']} "
                f"color={row['colorStream']} gaps={'/'.join(map(str, row['estimatedLineGaps']))} "
                f"active={row['activeTargetCount']}/4"
            ),
            fill=(35, 35, 35),
            font=tiny_font,
        )
        y += 44

    y += 12
    draw.text((24, y), "Combined fingerprint hits", fill=(40, 40, 40), font=small_font)
    y += 28
    for idx, row in enumerate(combined_hits):
        fill = (238, 249, 239)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        draw.text(
            (24, y),
            (
                f"{idx + 1}. {' | '.join(row['ids'])}  "
                f"{row['visualStateStream']}/{row['colorStream']}/"
                f"{'/'.join(map(str, row['estimatedLineGaps']))}/{row['slotStream']} "
                f"exactActive={row['exactActiveQuartet']}"
            ),
            fill=(25, 105, 50),
            font=tiny_font,
        )
        y += 48

    img.save(OUT_SHEET, quality=92)


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    line_gap_hits = result["quartetControls"]["stateColorLineGapHits"]
    slot_hits = result["quartetControls"]["slotStreamHits"]
    combined_hits = result["quartetControls"]["combinedFingerprintHits"]
    lines = [
        "# Current Scan Active Quartet Fingerprint Specificity Gate",
        "",
        "Scope: bounded current-scan/PDF box-geometry control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Candidate page-76 rows after duplicate collapse: `{summary['candidateRowCount']}`",
        f"- Top-to-bottom quartets checked: `{summary['quartetCount']}`",
        f"- YKKY / OBBO hits: `{summary['stateColorHitCount']}`",
        f"- YKKY / OBBO / line-gap `3/2/5` hits: `{summary['stateColorLineGapHitCount']}`",
        f"- Slot-stream `OVED` hits: `{summary['slotStreamHitCount']}`",
        f"- Combined fingerprint hits: `{summary['combinedFingerprintHitCount']}`",
        f"- Non-active combined hits: `{summary['combinedNonActiveHitCount']}`",
        f"- Line pitch fitted from active boxes: `{summary['fittedLinePitchPx']}` px/line",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['specificityFingerprint']}`",
        "",
        "## Candidate Rows",
        "",
        "| id | source | state | color | slot | center | label |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in result["candidateRows"]:
        label = str(row.get("label", "")).replace("|", "/")
        lines.append(
            f"| `{row['id']}` | `{row['source']}` | `{row['visualState']}` | `{row['colorCode']}` | "
            f"`{row['slotLetter']}{row['slotIndex']}` | `{row['centerX']},{row['centerY']}` | {label} |"
        )

    lines.extend(["", "## Near Hits", ""])
    if line_gap_hits:
        lines.append("State/color plus line-gap hits:")
        for row in line_gap_hits:
            lines.append(
                f"- `{' | '.join(row['ids'])}` -> slots `{row['slotStream']}`, "
                f"active `{row['activeTargetCount']}/4`, exact active `{row['exactActiveQuartet']}`"
            )
    if slot_hits:
        lines.append("")
        lines.append("Slot-stream OVED hits:")
        for row in slot_hits:
            lines.append(
                f"- `{' | '.join(row['ids'])}` -> state `{row['visualStateStream']}`, "
                f"color `{row['colorStream']}`, gaps `{'/'.join(map(str, row['estimatedLineGaps']))}`, "
                f"active `{row['activeTargetCount']}/4`"
            )
    if combined_hits:
        lines.append("")
        lines.append("Combined fingerprint hits:")
        for row in combined_hits:
            lines.append(
                f"- `{' | '.join(row['ids'])}` -> `YKKY/OBBO/3-2-5/OVED`, exact active `{row['exactActiveQuartet']}`"
            )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanActiveQuartetFingerprintSpecificityGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    highlight_audit = load_json(HIGHLIGHT_AUDIT)
    c9_slots = load_json(C9_SLOTS)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)
    slots = c9_slots.get("slots", [])

    active_rows = active_candidates(active_index, slots)
    line_fit = fit_line_pitch(active_rows)
    candidates = dedupe_candidates(active_rows + highlight_candidates(highlight_audit, slots))
    quartets = build_quartets(candidates, line_fit["slopePxPerLine"])

    state_color_hits = [
        row for row in quartets if row["matchesStateStream"] and row["matchesColorStream"]
    ]
    state_color_line_gap_hits = [
        row
        for row in state_color_hits
        if row["matchesLineGapEstimate"]
    ]
    slot_stream_hits = [row for row in quartets if row["matchesSlotStream"]]
    combined_hits = [row for row in quartets if row["matchesCombinedFingerprint"]]
    non_active_combined_hits = [row for row in combined_hits if not row["exactActiveQuartet"]]

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)
    hidden_candidate = 1 if non_active_combined_hits else 0
    selector_unlocked = False
    fingerprint = (
        f"candidates={len(candidates)}|quartets={len(quartets)}|"
        f"YKKYOBBO={len(state_color_hits)}|gap325={len(state_color_line_gap_hits)}|"
        f"slotOVED={len(slot_stream_hits)}|combined={len(combined_hits)}|"
        f"nonActiveCombined={len(non_active_combined_hits)}|hiddenCandidate={hidden_candidate}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "candidateRowCount": len(candidates),
        "activeCandidateRowCount": sum(1 for row in candidates if row["isActiveTarget"]),
        "controlCandidateRowCount": sum(1 for row in candidates if not row["isActiveTarget"]),
        "quartetCount": comb(len(candidates), 4) if len(candidates) >= 4 else 0,
        "stateStreamHitCount": count(quartets, "matchesStateStream"),
        "colorStreamHitCount": count(quartets, "matchesColorStream"),
        "stateColorHitCount": len(state_color_hits),
        "lineGapHitCount": count(quartets, "matchesLineGapEstimate"),
        "stateColorLineGapHitCount": len(state_color_line_gap_hits),
        "slotStreamHitCount": len(slot_stream_hits),
        "combinedFingerprintHitCount": len(combined_hits),
        "combinedExactActiveHitCount": sum(1 for row in combined_hits if row["exactActiveQuartet"]),
        "combinedNonActiveHitCount": len(non_active_combined_hits),
        "hiddenCurrentScanFingerprintCandidate": hidden_candidate,
        "targetStateStream": TARGET_STATE_STREAM,
        "targetColorStream": TARGET_COLOR_STREAM,
        "targetLineGaps": "/".join(map(str, TARGET_LINE_GAPS)),
        "targetSlotStream": TARGET_SLOT_STREAM,
        "fittedLinePitchPx": round(line_fit["slopePxPerLine"], 6),
        "fittedLineInterceptPx": round(line_fit["interceptPx"], 6),
        "activeLineFitResidualsPx": line_fit["activeResidualsPx"],
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
        "specificityFingerprint": fingerprint,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan page-76 active quartet fingerprint specificity control; "
            "no key derivation, hashing, WIF, seed, address, or broad brute force"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "highlightAudit": rel(HIGHLIGHT_AUDIT),
            "c9Slots": rel(C9_SLOTS),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "candidateSource": (
                "active-index boxes plus p76 annotated color rows and visual-orange rows "
                "from the current scan/PDF highlight audit"
            ),
            "duplicateCollapse": "IoU > 0.90 or center distance < 2 px; active boxes keep priority",
            "lineGapEstimate": "least-squares active pageLine-to-centerY fit, then rounded y gaps",
            "combinedFingerprint": "YKKY state, OBBO color, estimated line gaps 3/2/5, C9 center-slot stream OVED",
        },
        "candidateRows": candidates,
        "quartetControls": {
            "stateColorLineGapHits": state_color_line_gap_hits,
            "slotStreamHits": slot_stream_hits,
            "combinedFingerprintHits": combined_hits,
            "nonActiveCombinedFingerprintHits": non_active_combined_hits,
        },
        "summary": summary,
        "decision": {
            "currentScanActiveQuartetFingerprintSpecificityGate": (
                "keep_as_registration_fingerprint_not_extraction_selector"
            ),
            "reason": (
                "The combined scan-box fingerprint selects only O4/B4/G5/O5 among the "
                "available page-76 highlight/annotation controls, but it still supplies "
                "no source-backed R3 unit/order wording and unlocks no selector."
            ),
            "selectorUnlocked": selector_unlocked,
        },
        "nextMove": (
            "Use the active quartet fingerprint as a future source-validation signature; "
            "do not extract until a physical/original-layout source or raw clue names the "
            "registration unit, order, transform, or read direction."
        ),
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(
        candidates,
        summary,
        state_color_line_gap_hits,
        slot_stream_hits,
        combined_hits,
    )
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
