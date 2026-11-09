#!/usr/bin/env python3
"""Audit OVERDOSE glyph edges/centers as fold or mirror rulers.

This bounded geometry pass tests whether the actual page-76 OVERDOSE header
glyph edges, glyph centers, or their C9-projected equivalents can act as a
source-visible fold axis for O4/B4/G5/O5.

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
OUT = ROOT / "analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_glyph_axis_ruler_gate.json"
OUT_MD = OUT / "overdose_glyph_axis_ruler_gate.md"
OUT_SHEET = OUT / "overdose_glyph_axis_ruler_gate_sheet.jpg"

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

LETTERS = "OVERDOSE"
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
LINE_EPS = 8.0
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
LAYOUT_TERMS = ("OVERDOSE", "OVER", "DOSE", "REVO", "ESOD")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def token(text: str) -> str:
    return "".join(ch.lower() for ch in str(text) if ch.isalnum())


def ascii_safe(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def page76(article: dict[str, Any]) -> dict[str, Any]:
    return next(page for page in article["pages"] if page.get("page") == 76)


def header_word_and_chars(page: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    word = next(word for word in page["words"] if str(word.get("token", "")).lower() == "overdose")
    word_box = [float(v) for v in word["box"]]
    chars = []
    for char in page["chars"]:
        if char.get("c") not in LETTERS:
            continue
        box = [float(v) for v in char["box"]]
        if (
            box[0] >= word_box[0] - 2.0
            and box[2] <= word_box[2] + 2.0
            and abs(float(char.get("y", center(box)[1])) - float(word["center"][1])) <= 8.0
        ):
            chars.append({"letter": char["c"], "box": box})
    chars = sorted(chars, key=lambda row: row["box"][0])
    sequence = "".join(row["letter"] for row in chars)
    if sequence != LETTERS:
        raise RuntimeError(f"Unexpected OVERDOSE glyph sequence: {sequence}")
    return {"text": "OVERDOSE", "box": word_box, "center": [float(v) for v in word["center"]]}, chars


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


def slot_for_x(slots: list[dict[str, Any]], x: float) -> str:
    for slot in slots:
        if slot["left"] <= x <= slot["right"]:
            return slot["letter"]
    return "."


def layout_hits(stream: str) -> list[str]:
    compact = stream.replace(".", "")
    return [term for term in LAYOUT_TERMS if term in compact]


def words_near_axis(words: list[dict[str, Any]], axis_x: float) -> list[dict[str, Any]]:
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


def native_axes(chars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes = []
    axes.append({"family": "native_header", "role": "boundary_0", "letter": "|O", "axisX": chars[0]["box"][0]})
    for index, char in enumerate(chars):
        left, _, right, _ = char["box"]
        axes.append(
            {
                "family": "native_header",
                "role": f"center_{index}",
                "letter": char["letter"],
                "axisX": (left + right) / 2.0,
            }
        )
        suffix = LETTERS[index + 1] if index + 1 < len(LETTERS) else ""
        axes.append(
            {
                "family": "native_header",
                "role": f"boundary_{index + 1}",
                "letter": f"{char['letter']}|{suffix}",
                "axisX": right,
            }
        )
    return axes


def projected_axes(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes = []
    axes.append(
        {
            "family": "c9_projected_glyph",
            "role": "boundary_0",
            "letter": "|O",
            "axisX": slots[0]["left"],
        }
    )
    for slot in slots:
        axes.append(
            {
                "family": "c9_projected_glyph",
                "role": f"center_{slot['index']}",
                "letter": slot["letter"],
                "axisX": slot["center"],
            }
        )
        suffix = LETTERS[slot["index"] + 1] if slot["index"] + 1 < len(LETTERS) else ""
        axes.append(
            {
                "family": "c9_projected_glyph",
                "role": f"boundary_{slot['index'] + 1}",
                "letter": f"{slot['letter']}|{suffix}",
                "axisX": slot["right"],
            }
        )
    return axes


def analyze_axes(
    axes: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    slots: list[dict[str, Any]],
    words: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    direct_stream = "".join(slot_for_x(slots, target["center"][0]) for target in targets)
    for axis in axes:
        mirrored_points = []
        stream = ""
        inside = 0
        for target in targets:
            mirrored_x = 2.0 * axis["axisX"] - target["center"][0]
            letter = slot_for_x(slots, mirrored_x)
            stream += letter
            inside += int(letter != ".")
            mirrored_points.append(
                {
                    "target": target["shortId"],
                    "originalX": round(target["center"][0], 3),
                    "mirroredX": round(mirrored_x, 3),
                    "slotLetter": letter,
                }
            )
        near_words = words_near_axis(words, axis["axisX"])
        strict_words = [word for word in near_words if word["strictInstruction"]]
        rows.append(
            {
                **axis,
                "axisX": round(float(axis["axisX"]), 3),
                "directActiveStream": direct_stream,
                "mirroredActiveStream": stream,
                "mirroredInsideSlotCount": inside,
                "allFourMirroredInsideSlots": inside == len(targets),
                "layoutTermHits": layout_hits(stream),
                "axisWordHitCount": len(near_words),
                "strictInstructionHitCount": len(strict_words),
                "strictInstructionTerms": sorted({word["token"] for word in strict_words}),
                "axisTextPreview": ascii_safe(" ".join(word["text"] for word in near_words[:20])),
                "mirroredPoints": mirrored_points,
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
    crop = [220, 135, 2320, 3060]
    scale = 0.28
    panel = image.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    sheet = Image.new("RGB", (1780, 1120), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    sheet.paste(panel, (24, 132))
    draw.rectangle((0, 0, 1780, 104), fill=(24, 31, 42))
    draw.text((24, 16), "OVERDOSE Glyph Axis Ruler Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Actual header glyph edges/centers and C9-projected glyph axes mirrored against O4/B4/G5/O5.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1040, 18),
        f"native axes {summary['nativeAxisCount']} | projected axes {summary['projectedAxisCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1040, 48),
        f"projected all-four axes {summary['projectedAllFourInsideSlotAxisCount']} | layout hits {summary['layoutTermAxisCount']} | strict {summary['strictInstructionAxisHitCount']}",
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
    for target in result["targets"]:
        box = target["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(230, 110, 20), width=2)
        draw.text((sx(box[0]), sy(box[1]) - 14), target["shortId"], fill=(160, 60, 0), font=tiny)
    for row in result["axisRows"]:
        if row["family"] == "c9_projected_glyph" and row["allFourMirroredInsideSlots"]:
            draw.line([(sx(row["axisX"]), sy(frame[1])), (sx(row["axisX"]), sy(frame[3]))], fill=(220, 30, 30), width=2)
    header_box = result["headerWord"]["box"]
    draw.rectangle([sx(header_box[0]), sy(header_box[1]), sx(header_box[2]), sy(header_box[3])], outline=(130, 80, 210), width=2)

    y = 720
    draw.text((720, 132), "Best projected glyph axes", fill=(30, 34, 40), font=small)
    headers = ["axis", "x", "stream", "inside", "layout", "strict", "axis text"]
    xs = [720, 840, 910, 995, 1050, 1130, 1190]
    y = 160
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=tiny)
    y += 18
    rows = sorted(
        [row for row in result["axisRows"] if row["family"] == "c9_projected_glyph"],
        key=lambda row: (-row["mirroredInsideSlotCount"], row["role"]),
    )[:17]
    for row in rows:
        values = [
            f"{row['letter']} {row['role']}",
            f"{row['axisX']:.1f}",
            row["mirroredActiveStream"],
            str(row["mirroredInsideSlotCount"]),
            ",".join(row["layoutTermHits"]) or "-",
            str(row["strictInstructionHitCount"]),
            row["axisTextPreview"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:76], fill=(25, 28, 34), font=tiny)
        y += 22
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# OVERDOSE Glyph Axis Ruler Gate",
        "",
        "Scope: tested actual page-76 OVERDOSE glyph edges/centers and their C9-projected glyph axes as fold/mirror rulers for active O4/B4/G5/O5 centers. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Native header axes / C9-projected axes: `{summary['nativeAxisCount']}` / `{summary['projectedAxisCount']}`",
        f"- Native all-four mirrored-inside-slot axes: `{summary['nativeAllFourInsideSlotAxisCount']}`",
        f"- C9-projected all-four mirrored-inside-slot axes: `{summary['projectedAllFourInsideSlotAxisCount']}`",
        f"- Max native/projected mirrored centers inside slots: `{summary['nativeMaxMirroredInsideSlotCount']}` / `{summary['projectedMaxMirroredInsideSlotCount']}`",
        f"- Layout-term axis hits: `{summary['layoutTermAxisCount']}`",
        f"- Strict instruction axis hits: `{summary['strictInstructionAxisHitCount']}`",
        f"- All-four projected streams: `{', '.join(summary['allFourProjectedStreams']) or '-'}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Best Projected Axes",
        "",
        "| axis | x | stream | inside | layout hits | strict hits | text preview |",
        "|---|---:|---|---:|---|---:|---|",
    ]
    rows = sorted(
        [row for row in result["axisRows"] if row["family"] == "c9_projected_glyph"],
        key=lambda row: (-row["mirroredInsideSlotCount"], row["role"]),
    )
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['letter']} {row['role']}`",
                    f"{row['axisX']:.1f}",
                    f"`{row['mirroredActiveStream']}`",
                    str(row["mirroredInsideSlotCount"]),
                    ",".join(row["layoutTermHits"]) or "-",
                    str(row["strictInstructionHitCount"]),
                    row["axisTextPreview"].replace("|", "\\|")[:150],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote OVERDOSE glyph edges/centers as fold or mirror rulers.",
            "- Native header axes mirror the active centers completely outside the C9 slot frame.",
            "- C9-projected glyph axes can place all four mirrored centers inside slots in four cases, but the resulting streams are fragments (`VODE`, `RESD`, `ODRV`, `ESOR`), not `OVER`, `DOSE`, `REVO`, `ESOD`, or a source-backed unit/order instruction.",
            "",
            "## Next Move",
            "",
            "- Keep OVERDOSE glyph axes as source-validation geometry only. The best next move remains external/original-layout source validation or raw clue wording that names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    article = load_json(ARTICLE_MAP)
    page = page76(article)
    header_word, header_chars = header_word_and_chars(page)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    slots = slot_rows(c9)
    targets = active_rows(c9)
    frame = [float(v) for v in c9.get("c9Frame")]
    axes = native_axes(header_chars) + projected_axes(slots)
    axis_rows = analyze_axes(axes, targets, slots, page.get("words", []))
    native_rows = [row for row in axis_rows if row["family"] == "native_header"]
    projected_rows = [row for row in axis_rows if row["family"] == "c9_projected_glyph"]
    layout_axis_rows = [row for row in axis_rows if row["layoutTermHits"]]
    strict_axis_hits = sum(row["strictInstructionHitCount"] for row in axis_rows)
    all_four_projected = [row for row in projected_rows if row["allFourMirroredInsideSlots"]]
    all_four_projected_streams = sorted({row["mirroredActiveStream"] for row in all_four_projected})
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    summary = {
        "decision": "overdose_glyph_axis_ruler_no_selector",
        "nativeAxisCount": len(native_rows),
        "projectedAxisCount": len(projected_rows),
        "nativeAllFourInsideSlotAxisCount": sum(row["allFourMirroredInsideSlots"] for row in native_rows),
        "projectedAllFourInsideSlotAxisCount": sum(row["allFourMirroredInsideSlots"] for row in projected_rows),
        "nativeMaxMirroredInsideSlotCount": max((row["mirroredInsideSlotCount"] for row in native_rows), default=0),
        "projectedMaxMirroredInsideSlotCount": max((row["mirroredInsideSlotCount"] for row in projected_rows), default=0),
        "layoutTermAxisCount": len(layout_axis_rows),
        "strictInstructionAxisHitCount": strict_axis_hits,
        "allFourProjectedStreams": all_four_projected_streams,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"nativeAxes={summary['nativeAxisCount']}|projectedAxes={summary['projectedAxisCount']}|"
        f"nativeAllSlot={summary['nativeAllFourInsideSlotAxisCount']}|"
        f"projectedAllSlot={summary['projectedAllFourInsideSlotAxisCount']}|"
        f"nativeMax={summary['nativeMaxMirroredInsideSlotCount']}|"
        f"projectedMax={summary['projectedMaxMirroredInsideSlotCount']}|"
        f"layoutAxes={summary['layoutTermAxisCount']}|strictAxis={summary['strictInstructionAxisHitCount']}|"
        f"streams={','.join(all_four_projected_streams) or '-'}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "OVERDOSE glyph edges/centers tested as fold/mirror axes against active O4/B4/G5/O5 centers and C9 glyph slots.",
        "inputs": {
            "articleMap": rel(ARTICLE_MAP),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "headerWord": header_word,
        "headerChars": header_chars,
        "c9Frame": frame,
        "slots": slots,
        "targets": targets,
        "axisRows": axis_rows,
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
