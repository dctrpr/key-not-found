#!/usr/bin/env python3
"""Test exact target-x vertical chords through the C9 OVERDOSE frame.

Earlier C9 passes tested slot bands, equal/glyph slots, header-origin rays, and
assigned glyph-center rays. This bounded pass asks whether the exact vertical
line through each active target center, inside the C9 frame, supplies a cleaner
word/highlight/instruction surface than non-active page-76 highlight controls.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
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
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
C9_HEADER_JSON = ROOT / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_target_vertical_chord_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_target_vertical_chord_gate.json"
OUT_MD = OUT / "c9_target_vertical_chord_gate.md"
OUT_SHEET = OUT / "c9_target_vertical_chord_gate_sheet.jpg"

STRICT_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "order",
    "key",
    "private",
    "encoded",
    "seed",
    "wif",
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
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def strict_hits(text: str) -> list[str]:
    return [term for term in STRICT_TERMS if re.search(rf"\b{re.escape(term)}\b", text, re.I)]


def segment_intersects_rect(p0: list[float], p1: list[float], rect: list[float]) -> bool:
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in [(-dx, x0 - rect[0]), (dx, rect[2] - x0), (-dy, y0 - rect[1]), (dy, rect[3] - y0)]:
        if p == 0:
            if q < 0:
                return False
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return False
            t0 = max(t0, r)
        else:
            if r < t0:
                return False
            t1 = min(t1, r)
    return True


def slot_for_x(slots: list[dict[str, Any]], x: float) -> dict[str, Any]:
    for slot in slots:
        if slot["left"] <= x <= slot["right"]:
            return slot
    return min(slots, key=lambda slot: min(abs(x - slot["left"]), abs(x - slot["right"])))


def analyze_chord(
    target: dict[str, Any],
    slots: list[dict[str, Any]],
    c9_frame: list[float],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    active_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    target_center = center(target["box"])
    x = target_center[0]
    top = [x, c9_frame[1]]
    bottom = [x, c9_frame[3]]
    slot = slot_for_x(slots, x)
    word_hits = []
    strict: set[str] = set()
    for word in words:
        if word.get("token") == "overdose":
            continue
        if not segment_intersects_rect(top, bottom, word["box"]):
            continue
        hits = strict_hits(word.get("text", ""))
        strict.update(hits)
        word_hits.append(
            {
                "id": word["id"],
                "index": word.get("index"),
                "text": word.get("text", ""),
                "importance": word.get("importance", 0),
                "strictInstructionHits": hits,
            }
        )

    highlight_hits = []
    for h in highlights:
        if segment_intersects_rect(top, bottom, h["box"]):
            highlight_hits.append({"id": h["id"], "kind": h["kind"]})

    active_hits = []
    for active in active_targets:
        if segment_intersects_rect(top, bottom, active["box"]):
            active_hits.append(active["id"])

    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetKind": target["kind"],
        "x": round(x, 2),
        "slotIndex": slot["index"],
        "slotLetter": slot["letter"],
        "top": [round(top[0], 2), round(top[1], 2)],
        "bottom": [round(bottom[0], 2), round(bottom[1], 2)],
        "targetCenter": [round(target_center[0], 2), round(target_center[1], 2)],
        "chordLengthPx": round(math.hypot(bottom[0] - top[0], bottom[1] - top[1]), 2),
        "wordHitCount": len(word_hits),
        "focusWordHitCount": sum(1 for row in word_hits if row["importance"] >= 3),
        "wordPreview": " ".join(row["text"] for row in word_hits[:22]),
        "highlightHitCount": len(highlight_hits),
        "highlightHitIds": [row["id"] for row in highlight_hits],
        "activeTargetHitCount": len(set(active_hits)),
        "activeTargetHitIds": sorted(set(active_hits)),
        "strictInstructionHits": sorted(strict),
        "strictInstructionHitCount": len(strict),
        "wordHits": word_hits,
        "highlightHits": highlight_hits,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [250, 2070, 2350, 3065]
    scale = 0.55
    panel = page.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 142
    right_w = 620
    sheet_w = margin * 3 + panel.width + right_w
    sheet_h = max(header_h + panel.height + margin, 1030)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 14, 19))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)
    draw.text((margin, 22), "C9 Target Vertical Chord Gate", fill=(242, 246, 250), font=title)
    draw.text((margin, 62), "Exact target-x vertical chords through the C9 lower frame, with non-active highlight controls.", fill=(178, 188, 199), font=normal)
    s = result["summary"]
    chips = [
        ("active chords", s["activeChordCount"]),
        ("control chords", s["controlChordCount"]),
        ("active all-quartet", s["activeAllQuartetChordCount"]),
        ("active strict", s["activeStrictInstructionHitCount"]),
        ("control strict", s["controlStrictInstructionHitCount"]),
    ]
    x, y = margin, 96
    for label, value in chips:
        draw.rectangle((x, y, x + 205, y + 40), fill=(25, 31, 39), outline=(50, 58, 70))
        draw.text((x + 9, y + 5), label, fill=(130, 145, 160), font=small)
        draw.text((x + 9, y + 22), str(value), fill=(232, 238, 245), font=mono)
        x += 217

    px0, py0 = margin, header_h
    sheet.paste(panel, (px0, py0))

    def sx(v: float) -> float:
        return px0 + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return py0 + (v - crop[1]) * scale

    frame = result["c9Frame"]
    draw.rectangle((sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])), outline="#78d4ff", width=2)
    for chord in result["controlChords"]:
        draw.line((sx(chord["top"][0]), sy(chord["top"][1]), sx(chord["bottom"][0]), sy(chord["bottom"][1])), fill="#596273", width=1)
    for chord in result["activeChords"]:
        color = "#ff9b2e" if "O" in chord["targetLabel"] else "#c5ccd6"
        draw.line((sx(chord["top"][0]), sy(chord["top"][1]), sx(chord["bottom"][0]), sy(chord["bottom"][1])), fill=color, width=3)
        draw.text((sx(chord["x"]) + 4, sy(chord["targetCenter"][1]) - 7), chord["targetId"], fill="#ffffff", font=small)
        draw.text((sx(chord["x"]) - 4, sy(frame[1]) - 18), chord["slotLetter"], fill="#ffffff", font=small)

    rx, ry = px0 + panel.width + margin, header_h
    draw.text((rx, ry), "Active Chords", fill=(242, 246, 250), font=normal)
    ry += 30
    for chord in result["activeChords"]:
        draw.rectangle((rx, ry, sheet_w - margin, ry + 100), fill=(21, 26, 34), outline=(48, 58, 70))
        draw.text((rx + 10, ry + 8), f"{chord['targetLabel']} x={chord['x']} slot {chord['slotLetter']}{chord['slotIndex']}", fill=(238, 243, 248), font=normal)
        lines = [
            f"active hits {chord['activeTargetHitIds']} highlights {chord['highlightHitCount']}",
            f"words {chord['wordHitCount']} focus {chord['focusWordHitCount']} strict {chord['strictInstructionHitCount']}",
            f"preview {chord['wordPreview'][:48] or '-'}",
        ]
        yy = ry + 34
        for line in lines:
            draw.text((rx + 14, yy), line[:78], fill=(196, 206, 217), font=mono)
            yy += 19
        ry += 114
    ry += 8
    draw.text((rx, ry), "Controls", fill=(242, 246, 250), font=normal)
    ry += 28
    for chord in result["controlChords"]:
        line = f"{chord['targetId']} slot {chord['slotLetter']}{chord['slotIndex']} active {chord['activeTargetHitIds']} strict {chord['strictInstructionHitCount']}"
        draw.text((rx + 8, ry), line[:82], fill=(178, 188, 199), font=small)
        ry += 18
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    c9 = load_json(C9_HEADER_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    projection = next(row for row in c9["projections"] if row["name"] == "p76_header_glyph")
    slots = projection["slots"]
    c9_frame = c9["c9Frame"]

    active_targets = [
        {
            "id": row["id"],
            "label": row["label"],
            "kind": "active",
            "box": row["box"],
            "pageLine": row["pageLine"],
            "corridorIndex": row["corridorIndex"],
            "visualState": row["visualState"],
        }
        for row in active["targets"]
    ]
    active_boxes = [row["box"] for row in active_targets]
    control_targets = []
    for h in page["highlights"]:
        h_center = center(h["box"])
        if any(box[0] <= h_center[0] <= box[2] and box[1] <= h_center[1] <= box[3] for box in active_boxes):
            continue
        control_targets.append(
            {
                "id": h["id"],
                "label": f"{h['kind']} {h['id']}",
                "kind": "non_active_highlight_control",
                "box": h["box"],
            }
        )

    active_chords = [
        analyze_chord(target, slots, c9_frame, page["words"], page["highlights"], active_targets)
        for target in active_targets
    ]
    control_chords = [
        analyze_chord(target, slots, c9_frame, page["words"], page["highlights"], active_targets)
        for target in control_targets
    ]
    active_strict = sorted({hit for chord in active_chords for hit in chord["strictInstructionHits"]})
    control_strict = sorted({hit for chord in control_chords for hit in chord["strictInstructionHits"]})
    all_active_ids = sorted(row["id"] for row in active_targets)
    active_all_quartet = [
        chord for chord in active_chords if sorted(chord["activeTargetHitIds"]) == all_active_ids
    ]
    summary = {
        "activeChordCount": len(active_chords),
        "controlChordCount": len(control_chords),
        "activeSlotStream": "".join(chord["slotLetter"] for chord in active_chords),
        "controlSlotStream": "".join(chord["slotLetter"] for chord in control_chords),
        "activeStrictInstructionHitCount": len(active_strict),
        "controlStrictInstructionHitCount": len(control_strict),
        "activeAllQuartetChordCount": len(active_all_quartet),
        "activeChordActiveTargetHitCounts": [chord["activeTargetHitCount"] for chord in active_chords],
        "controlChordActiveTargetHitCounts": [chord["activeTargetHitCount"] for chord in control_chords],
        "activeChordHighlightHitCounts": [chord["highlightHitCount"] for chord in active_chords],
        "controlChordHighlightHitCounts": [chord["highlightHitCount"] for chord in control_chords],
        "selectorUnlocked": False,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": [
            "Use exact target-center x coordinates as vertical C9-frame chords.",
            "Compare active O4/B4/G5/O5 chords with non-active page-76 highlight control chords.",
            "Measure existing word/highlight/active-target intersections and strict instruction terms only.",
            "No OCR, hashing, key derivation, private-key checks, seed/WIF checks, address checks, or broad candidate generation.",
        ],
        "inputs": {"activeTargets": rel(ACTIVE_JSON), "articleMap": rel(ARTICLE_JSON), "c9HeaderGlyphSlotGate": rel(C9_HEADER_JSON)},
        "c9Frame": c9_frame,
        "slots": slots,
        "summary": summary,
        "activeChords": active_chords,
        "controlChords": control_chords,
        "decision": {
            "c9TargetVerticalChordAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep exact target-x C9 vertical chords as visual/layout context only. Reopen only if a source/clue explicitly names vertical slot chords or a chord-based unit/order rule.",
        },
        "sheet": rel(OUT_SHEET),
        "outputs": {"json": rel(OUT_JSON), "markdown": rel(OUT_MD), "sheet": rel(OUT_SHEET)},
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Target Vertical Chord Gate",
        "",
        "Scope: use exact O4/B4/G5/O5 target-center x coordinates as vertical chords through the p76 C9 OVERDOSE frame, with non-active page-76 highlight controls. This measures existing word/highlight/active-target intersections and strict instruction terms only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.",
        "",
        "## Summary",
        f"- active chords: `{summary['activeChordCount']}`",
        f"- control chords: `{summary['controlChordCount']}`",
        f"- active slot stream: `{summary['activeSlotStream']}`",
        f"- control slot stream: `{summary['controlSlotStream']}`",
        f"- active strict instruction hits: `{summary['activeStrictInstructionHitCount']}`",
        f"- control strict instruction hits: `{summary['controlStrictInstructionHitCount']}`",
        f"- active all-quartet chords: `{summary['activeAllQuartetChordCount']}`",
        f"- active chord active-target hit counts: `{summary['activeChordActiveTargetHitCounts']}`",
        f"- control chord active-target hit counts: `{summary['controlChordActiveTargetHitCounts']}`",
        f"- active chord highlight-hit counts: `{summary['activeChordHighlightHitCounts']}`",
        f"- control chord highlight-hit counts: `{summary['controlChordHighlightHitCounts']}`",
        f"- selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Active Chords",
        "",
        "| target | slot | active hits | words | highlights | strict hits | preview |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for chord in active_chords:
        lines.append(
            "| {target} | {slot}{idx} | {active} | {words} | {highlights} | {strict} | {preview} |".format(
                target=chord["targetId"],
                slot=chord["slotLetter"],
                idx=chord["slotIndex"],
                active=chord["activeTargetHitCount"],
                words=chord["wordHitCount"],
                highlights=chord["highlightHitCount"],
                strict=", ".join(chord["strictInstructionHits"]) or "-",
                preview=(chord["wordPreview"] or "-").replace("|", "/")[:90],
            )
        )
    lines.extend(["", "## Control Chords", ""])
    for chord in control_chords:
        lines.append(
            "- `{target}` slot `{slot}{idx}` active hits `{active}` words `{words}` highlights `{highlights}` strict `{strict}` preview `{preview}`".format(
                target=chord["targetId"],
                slot=chord["slotLetter"],
                idx=chord["slotIndex"],
                active=chord["activeTargetHitCount"],
                words=chord["wordHitCount"],
                highlights=chord["highlightHitCount"],
                strict=", ".join(chord["strictInstructionHits"]) or "-",
                preview=(chord["wordPreview"] or "-").replace("|", "/")[:110],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote exact target-x C9 vertical chords as a selector.",
            "- The active slot stream again repeats the already-known `OVED` center-slot result and adds no unit/order instruction.",
            "- Active chords do not traverse the full active quartet; control chords can touch active targets too, so this remains visual/layout context.",
            "",
            "## Outputs",
            f"- JSON: `{rel(OUT_JSON)}`",
            f"- visual sheet: `{rel(OUT_SHEET)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
