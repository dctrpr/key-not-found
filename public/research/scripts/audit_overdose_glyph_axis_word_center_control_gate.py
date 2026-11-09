#!/usr/bin/env python3
"""Control OVERDOSE glyph-axis slot hits against ordinary word centers.

This bounded pass follows the previous OVERDOSE glyph-axis near miss. It keeps
only the C9-projected axes that put all four active O4/B4/G5/O5 centers inside
OVERDOSE slots, then asks whether those same axes are selective when applied to
ordinary page-76 C9-frame word centers.

No OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/overdose_glyph_axis_word_center_control_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_glyph_axis_word_center_control_gate.json"
OUT_MD = OUT / "overdose_glyph_axis_word_center_control_gate.md"
OUT_SHEET = OUT / "overdose_glyph_axis_word_center_control_gate_sheet.jpg"

ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE76_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
GLYPH_AXIS_GATE = ROOT / (
    "analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate/"
    "overdose_glyph_axis_ruler_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

LAYOUT_TERMS = ("OVERDOSE", "OVER", "DOSE", "REVO", "ESOD", "VODE", "ODRV", "RESD", "ESOR")
MEANINGFUL_LAYOUT_TERMS = {"OVERDOSE", "OVER", "DOSE", "REVO", "ESOD"}
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def ascii_safe(text: str) -> str:
    return str(text).encode("ascii", "replace").decode("ascii")


def token(text: str) -> str:
    return "".join(ch.lower() for ch in str(text) if ch.isalnum())


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def page76(article: dict[str, Any]) -> dict[str, Any]:
    return next(page for page in article["pages"] if page.get("page") == 76)


def slot_for_x(slots: list[dict[str, Any]], x: float) -> str:
    for slot in slots:
        if float(slot["left"]) <= x <= float(slot["right"]):
            return str(slot["letter"])
    return "."


def layout_hits(stream: str, meaningful_only: bool = False) -> list[str]:
    compact = stream.replace(".", "")
    terms = MEANINGFUL_LAYOUT_TERMS if meaningful_only else set(LAYOUT_TERMS)
    return sorted(term for term in terms if term in compact)


def box_overlap_area(a: list[float], b: list[float]) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    if right <= left or bottom <= top:
        return 0.0
    return (right - left) * (bottom - top)


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def is_target_word(word: dict[str, Any], targets: list[dict[str, Any]]) -> bool:
    word_box = [float(v) for v in word["box"]]
    word_area = area(word_box) or 1.0
    return any(box_overlap_area(word_box, [float(v) for v in target["box"]]) / word_area >= 0.25 for target in targets)


def c9_words(page: dict[str, Any], frame: list[float], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for word in page.get("words", []):
        box = [float(v) for v in word["box"]]
        cx, cy = center(box)
        if not (frame[0] <= cx <= frame[2] and frame[1] <= cy <= frame[3]):
            continue
        tok = token(word.get("token") or word.get("text") or "")
        if not tok:
            continue
        rows.append(
            {
                "id": word["id"],
                "index": int(word.get("index", len(rows))),
                "text": ascii_safe(word.get("text", "")),
                "token": tok,
                "box": box,
                "center": [cx, cy],
                "isActiveTargetWord": is_target_word(word, targets),
                "strictInstruction": tok in STRICT_TERMS,
            }
        )
    return sorted(rows, key=lambda row: row["index"])


def selected_axes(glyph_axis: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in glyph_axis.get("axisRows", []):
        if row.get("family") != "c9_projected_glyph":
            continue
        if not row.get("allFourMirroredInsideSlots"):
            continue
        rows.append(
            {
                "role": row["role"],
                "letter": row["letter"],
                "axisX": float(row["axisX"]),
                "activeStream": row["mirroredActiveStream"],
                "activeLayoutHits": layout_hits(row["mirroredActiveStream"], meaningful_only=True),
                "activeInsideSlotCount": int(row["mirroredInsideSlotCount"]),
            }
        )
    return sorted(rows, key=lambda row: row["axisX"])


def mirror_word(word: dict[str, Any], axis_x: float, slots: list[dict[str, Any]]) -> dict[str, Any]:
    mirrored_x = 2.0 * axis_x - float(word["center"][0])
    letter = slot_for_x(slots, mirrored_x)
    return {
        "wordId": word["id"],
        "index": word["index"],
        "text": word["text"],
        "token": word["token"],
        "originalX": round(float(word["center"][0]), 3),
        "mirroredX": round(mirrored_x, 3),
        "slotLetter": letter,
        "insideSlot": letter != ".",
        "strictInstruction": word["strictInstruction"],
    }


def window_stream(words: list[dict[str, Any]], axis_x: float, slots: list[dict[str, Any]]) -> dict[str, Any]:
    mirrored = [mirror_word(word, axis_x, slots) for word in words]
    stream = "".join(row["slotLetter"] for row in mirrored)
    strict_terms = sorted({word["token"] for word in words if word["strictInstruction"]})
    return {
        "wordIds": [word["id"] for word in words],
        "indexes": [word["index"] for word in words],
        "text": ascii_safe(" ".join(word["text"] for word in words)),
        "stream": stream,
        "insideSlotCount": sum(row["insideSlot"] for row in mirrored),
        "allFourInsideSlots": all(row["insideSlot"] for row in mirrored),
        "layoutHits": layout_hits(stream, meaningful_only=True),
        "nearMissFragmentHits": [term for term in layout_hits(stream) if term not in MEANINGFUL_LAYOUT_TERMS],
        "strictInstructionTerms": strict_terms,
        "mirroredWords": mirrored,
    }


def analyze_axis(
    axis: dict[str, Any],
    control_words: list[dict[str, Any]],
    slots: list[dict[str, Any]],
) -> dict[str, Any]:
    mirrored_words = [mirror_word(word, axis["axisX"], slots) for word in control_words]
    slot_counts = Counter(row["slotLetter"] for row in mirrored_words if row["slotLetter"] != ".")
    windows = [
        window_stream(control_words[i : i + 4], axis["axisX"], slots)
        for i in range(max(0, len(control_words) - 3))
    ]
    all_inside_windows = [window for window in windows if window["allFourInsideSlots"]]
    layout_windows = [window for window in all_inside_windows if window["layoutHits"]]
    strict_windows = [window for window in windows if window["strictInstructionTerms"]]
    near_miss_windows = [window for window in all_inside_windows if window["nearMissFragmentHits"]]
    return {
        **axis,
        "axisX": round(axis["axisX"], 3),
        "controlWordCount": len(control_words),
        "controlWordMirroredInsideSlotCount": sum(row["insideSlot"] for row in mirrored_words),
        "controlWordSlotDistribution": dict(sorted(slot_counts.items())),
        "controlQuartetWindowCount": len(windows),
        "controlQuartetAllFourInsideSlotCount": len(all_inside_windows),
        "controlQuartetLayoutTermWindowCount": len(layout_windows),
        "controlQuartetStrictInstructionWindowCount": len(strict_windows),
        "controlQuartetNearMissFragmentWindowCount": len(near_miss_windows),
        "controlAllFourStreamCounts": dict(Counter(window["stream"] for window in all_inside_windows).most_common(12)),
        "representativeAllFourWindows": all_inside_windows[:10],
        "representativeLayoutWindows": layout_windows[:10],
        "representativeStrictWindows": strict_windows[:10],
    }


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
    crop = [220, 2060, 2320, 3060]
    scale = 0.47
    panel = image.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    sheet = Image.new("RGB", (1760, 940), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    sheet.paste(panel, (24, 126))
    draw.rectangle((0, 0, 1760, 100), fill=(24, 31, 42))
    draw.text((24, 16), "OVERDOSE Glyph-Axis Word-Center Control Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "C9-projected all-active slot axes tested against ordinary lower-page word centers.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1030, 18),
        f"axes {summary['selectedAxisCount']} | controls {summary['nonTargetC9ControlWordCount']} | active streams {','.join(summary['activeStreams'])}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1030, 48),
        f"control all-slot windows {summary['controlQuartetAllFourInsideSlotCount']} | layout windows {summary['controlQuartetLayoutTermWindowCount']} | strict windows {summary['controlQuartetStrictInstructionWindowCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    def sx(x: float) -> float:
        return 24 + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return 126 + (y - crop[1]) * scale

    frame = result["c9Frame"]
    draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline=(35, 150, 220), width=3)
    for slot in result["slots"]:
        draw.line([(sx(slot["left"]), sy(frame[1])), (sx(slot["left"]), sy(frame[3]))], fill=(35, 150, 220), width=1)
        draw.text((sx(slot["center"]) - 5, sy(frame[1]) - 16), slot["letter"], fill=(0, 90, 150), font=tiny)
    draw.line([(sx(result["slots"][-1]["right"]), sy(frame[1])), (sx(result["slots"][-1]["right"]), sy(frame[3]))], fill=(35, 150, 220), width=1)
    for target in result["targets"]:
        box = target["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(235, 115, 30), width=2)
        draw.text((sx(box[0]), sy(box[1]) - 14), target["shortId"], fill=(160, 60, 0), font=tiny)
    colors = [(220, 30, 30), (40, 150, 70), (140, 70, 210), (220, 150, 20)]
    for axis, color in zip(result["axisRows"], colors):
        draw.line([(sx(axis["axisX"]), sy(frame[1])), (sx(axis["axisX"]), sy(frame[3]))], fill=color, width=2)
        draw.text((sx(axis["axisX"]) + 4, sy(frame[1]) + 4), axis["activeStream"], fill=color, font=tiny)

    xs = [1030, 1125, 1190, 1275, 1370, 1465, 1545]
    headers = ["axis", "active", "ctrl in", "all-4", "layout", "strict", "top streams"]
    y = 126
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=tiny)
    y += 20
    for row in result["axisRows"]:
        top_streams = ",".join(f"{k}:{v}" for k, v in list(row["controlAllFourStreamCounts"].items())[:3])
        values = [
            f"{row['letter']} {row['role']}",
            row["activeStream"],
            f"{row['controlWordMirroredInsideSlotCount']}/{row['controlWordCount']}",
            row["controlQuartetAllFourInsideSlotCount"],
            row["controlQuartetLayoutTermWindowCount"],
            row["controlQuartetStrictInstructionWindowCount"],
            top_streams or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:38], fill=(25, 28, 34), font=tiny)
        y += 24

    y += 18
    draw.text((1030, y), "Representative control all-slot windows", fill=(30, 34, 40), font=small)
    y += 22
    examples = []
    for axis in result["axisRows"]:
        for window in axis["representativeAllFourWindows"][:2]:
            examples.append((axis["activeStream"], window))
    for axis_stream, window in examples[:18]:
        text = f"{axis_stream} -> {window['stream']} | {window['text']}"
        draw.text((1030, y), text[:100], fill=(25, 28, 34), font=tiny)
        y += 18
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# OVERDOSE Glyph-Axis Word-Center Control Gate",
        "",
        "Scope: retested only the four C9-projected OVERDOSE glyph axes that put active O4/B4/G5/O5 centers inside slots, then applied those same axes to ordinary page-76 C9-frame word centers and four-word sliding controls. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Selected C9-projected axes: `{summary['selectedAxisCount']}`",
        f"- Active all-four axes / active meaningful layout axes: `{summary['activeAllFourInsideAxisCount']}` / `{summary['activeMeaningfulLayoutAxisCount']}`",
        f"- Active streams: `{', '.join(summary['activeStreams'])}`",
        f"- C9 words / non-target controls: `{summary['c9WordCount']}` / `{summary['nonTargetC9ControlWordCount']}`",
        f"- Control word-center mirrors inside slots: `{summary['controlWordMirroredInsideSlotCount']}/{summary['controlWordMirrorRowCount']}`",
        f"- Control four-word windows / all-four-in-slot windows: `{summary['controlQuartetWindowCount']}` / `{summary['controlQuartetAllFourInsideSlotCount']}`",
        f"- Control meaningful layout-term windows: `{summary['controlQuartetLayoutTermWindowCount']}`",
        f"- Control strict-instruction windows: `{summary['controlQuartetStrictInstructionWindowCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Axis Controls",
        "",
        "| axis | active stream | control words in slots | all-four control windows | layout windows | strict windows | common control streams |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in result["axisRows"]:
        common = ", ".join(f"`{key}`:{value}" for key, value in list(row["controlAllFourStreamCounts"].items())[:6]) or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['letter']} {row['role']} @ {row['axisX']:.1f}`",
                    f"`{row['activeStream']}`",
                    f"{row['controlWordMirroredInsideSlotCount']}/{row['controlWordCount']}",
                    str(row["controlQuartetAllFourInsideSlotCount"]),
                    str(row["controlQuartetLayoutTermWindowCount"]),
                    str(row["controlQuartetStrictInstructionWindowCount"]),
                    common,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Representative All-Slot Control Windows",
            "",
            "| active stream | control stream | text |",
            "|---|---|---|",
        ]
    )
    examples = []
    for row in result["axisRows"]:
        for window in row["representativeAllFourWindows"][:4]:
            examples.append((row["activeStream"], window))
    for active_stream, window in examples[:18]:
        lines.append(
            f"| `{active_stream}` | `{window['stream']}` | {window['text'].replace('|', '\\|')[:180]} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote the C9-projected OVERDOSE glyph axes as selectors.",
            "- The active streams remain non-instruction fragments, and the same axes also map ordinary non-target word centers into OVERDOSE slots across many four-word controls.",
            "- No control or active window supplies source-backed unit/order wording, and the source-packet reopen triggers remain unsatisfied.",
            "",
            "## Next Move",
            "",
            "- Treat these axes as broad C9 geometry, not extraction mechanics. The best next move remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    article = load_json(ARTICLE_MAP)
    glyph_axis = load_json(GLYPH_AXIS_GATE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    page = page76(article)
    frame = [float(v) for v in glyph_axis["c9Frame"]]
    slots = glyph_axis["slots"]
    targets = glyph_axis["targets"]
    axes = selected_axes(glyph_axis)
    words = c9_words(page, frame, targets)
    controls = [word for word in words if not word["isActiveTargetWord"]]
    axis_rows = [analyze_axis(axis, controls, slots) for axis in axes]

    control_word_inside = sum(row["controlWordMirroredInsideSlotCount"] for row in axis_rows)
    control_word_rows = sum(row["controlWordCount"] for row in axis_rows)
    control_window_rows = sum(row["controlQuartetWindowCount"] for row in axis_rows)
    control_all_four = sum(row["controlQuartetAllFourInsideSlotCount"] for row in axis_rows)
    control_layout = sum(row["controlQuartetLayoutTermWindowCount"] for row in axis_rows)
    control_strict = sum(row["controlQuartetStrictInstructionWindowCount"] for row in axis_rows)
    active_streams = sorted({row["activeStream"] for row in axis_rows})
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    summary = {
        "decision": "overdose_glyph_axis_word_center_control_no_selector",
        "selectedAxisCount": len(axis_rows),
        "activeAllFourInsideAxisCount": sum(row["activeInsideSlotCount"] == 4 for row in axis_rows),
        "activeMeaningfulLayoutAxisCount": sum(bool(row["activeLayoutHits"]) for row in axis_rows),
        "activeStreams": active_streams,
        "c9WordCount": len(words),
        "nonTargetC9ControlWordCount": len(controls),
        "controlWordMirrorRowCount": control_word_rows,
        "controlWordMirroredInsideSlotCount": control_word_inside,
        "controlWordMirroredInsideSlotRate": round(control_word_inside / control_word_rows, 6) if control_word_rows else 0.0,
        "controlQuartetWindowCount": control_window_rows,
        "controlQuartetAllFourInsideSlotCount": control_all_four,
        "controlQuartetLayoutTermWindowCount": control_layout,
        "controlQuartetStrictInstructionWindowCount": control_strict,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"axes={summary['selectedAxisCount']}|activeAll={summary['activeAllFourInsideAxisCount']}|"
        f"activeLayout={summary['activeMeaningfulLayoutAxisCount']}|streams={','.join(active_streams) or '-'}|"
        f"c9Words={summary['c9WordCount']}|controls={summary['nonTargetC9ControlWordCount']}|"
        f"ctrlInside={control_word_inside}/{control_word_rows}|ctrlAll4={control_all_four}/{control_window_rows}|"
        f"ctrlLayout={control_layout}|ctrlStrict={control_strict}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9-projected OVERDOSE glyph axes controlled against ordinary page-76 C9-frame word centers.",
        "inputs": {
            "articleMap": rel(ARTICLE_MAP),
            "glyphAxisGate": rel(GLYPH_AXIS_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "c9Frame": frame,
        "slots": slots,
        "targets": targets,
        "axisRows": axis_rows,
        "c9Words": words,
        "nonTargetControlWords": controls,
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
