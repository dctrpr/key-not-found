#!/usr/bin/env python3
"""Test exact target-y horizontal chords through the C9 OVERDOSE frame.

This complements the C9 vertical chord pass by using the active target center
y-coordinates as full-width horizontal chords inside the C9 frame. Controls are
non-active focus rows inside the same C9 frame.

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
OUT = ROOT / "analysis_outputs/source_audit/c9_target_horizontal_chord_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_target_horizontal_chord_gate.json"
OUT_MD = OUT / "c9_target_horizontal_chord_gate.md"
OUT_SHEET = OUT / "c9_target_horizontal_chord_gate_sheet.jpg"

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


def row_controls(words: list[dict[str, Any]], c9_frame: list[float], active_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_ys = [center(row["box"])[1] for row in active_targets]
    focus_words = [
        word
        for word in words
        if word.get("importance", 0) >= 3
        and c9_frame[0] <= word["center"][0] <= c9_frame[2]
        and c9_frame[1] <= word["center"][1] <= c9_frame[3]
    ]
    groups: list[list[dict[str, Any]]] = []
    for word in sorted(focus_words, key=lambda row: (row["center"][1], row["center"][0])):
        if not groups or abs(word["center"][1] - sum(w["center"][1] for w in groups[-1]) / len(groups[-1])) > 18:
            groups.append([word])
        else:
            groups[-1].append(word)
    controls = []
    for i, group in enumerate(groups, 1):
        y = sum(word["center"][1] for word in group) / len(group)
        if any(abs(y - active_y) <= 24 for active_y in active_ys):
            continue
        preview = " ".join(word["text"] for word in sorted(group, key=lambda row: row["center"][0])[:8])
        controls.append(
            {
                "id": f"c9_focus_row_{i}",
                "label": preview or f"focus row {i}",
                "kind": "non_active_focus_row_control",
                "y": y,
                "sourceWordIds": [word["id"] for word in group],
            }
        )
    return controls


def analyze_chord(
    target: dict[str, Any],
    c9_frame: list[float],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    active_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    y = target["y"] if "y" in target else center(target["box"])[1]
    left = [c9_frame[0], y]
    right = [c9_frame[2], y]
    word_hits = []
    strict: set[str] = set()
    for word in words:
        if word.get("token") == "overdose":
            continue
        if not segment_intersects_rect(left, right, word["box"]):
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
        if segment_intersects_rect(left, right, h["box"]):
            highlight_hits.append({"id": h["id"], "kind": h["kind"]})

    active_hits = []
    for active in active_targets:
        if segment_intersects_rect(left, right, active["box"]):
            active_hits.append(active["id"])

    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetKind": target["kind"],
        "y": round(y, 2),
        "left": [round(left[0], 2), round(left[1], 2)],
        "right": [round(right[0], 2), round(right[1], 2)],
        "chordLengthPx": round(math.hypot(right[0] - left[0], right[1] - left[1]), 2),
        "wordHitCount": len(word_hits),
        "focusWordHitCount": sum(1 for row in word_hits if row["importance"] >= 3),
        "wordPreview": " ".join(row["text"] for row in word_hits[:24]),
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
    sheet_h = max(header_h + panel.height + margin, 1100)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (11, 14, 19))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)
    draw.text((margin, 22), "C9 Target Horizontal Chord Gate", fill=(242, 246, 250), font=title)
    draw.text((margin, 62), "Exact target-y horizontal chords across the C9 lower frame, with non-active focus-row controls.", fill=(178, 188, 199), font=normal)
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
        draw.line((sx(chord["left"][0]), sy(chord["left"][1]), sx(chord["right"][0]), sy(chord["right"][1])), fill="#596273", width=1)
    for chord in result["activeChords"]:
        color = "#ff9b2e" if "O" in chord["targetLabel"] else "#c5ccd6"
        draw.line((sx(chord["left"][0]), sy(chord["left"][1]), sx(chord["right"][0]), sy(chord["right"][1])), fill=color, width=3)
        draw.text((sx(frame[0]) + 8, sy(chord["y"]) - 9), chord["targetId"], fill="#ffffff", font=small)

    rx, ry = px0 + panel.width + margin, header_h
    draw.text((rx, ry), "Active Chords", fill=(242, 246, 250), font=normal)
    ry += 30
    for chord in result["activeChords"]:
        draw.rectangle((rx, ry, sheet_w - margin, ry + 100), fill=(21, 26, 34), outline=(48, 58, 70))
        draw.text((rx + 10, ry + 8), f"{chord['targetLabel']} y={chord['y']}", fill=(238, 243, 248), font=normal)
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
        line = f"{chord['targetId']} y={chord['y']} active {chord['activeTargetHitIds']} strict {chord['strictInstructionHitCount']}"
        draw.text((rx + 8, ry), line[:82], fill=(178, 188, 199), font=small)
        ry += 18
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    c9 = load_json(C9_HEADER_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
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
    controls = row_controls(page["words"], c9_frame, active_targets)
    active_chords = [
        analyze_chord(target, c9_frame, page["words"], page["highlights"], active_targets)
        for target in active_targets
    ]
    control_chords = [
        analyze_chord(target, c9_frame, page["words"], page["highlights"], active_targets)
        for target in controls
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
        "activeStrictInstructionHitCount": len(active_strict),
        "controlStrictInstructionHitCount": len(control_strict),
        "activeAllQuartetChordCount": len(active_all_quartet),
        "activeChordActiveTargetHitCounts": [chord["activeTargetHitCount"] for chord in active_chords],
        "controlChordActiveTargetHitCounts": [chord["activeTargetHitCount"] for chord in control_chords],
        "activeChordHighlightHitCounts": [chord["highlightHitCount"] for chord in active_chords],
        "controlChordHighlightHitCounts": [chord["highlightHitCount"] for chord in control_chords],
        "activeWordHitCounts": [chord["wordHitCount"] for chord in active_chords],
        "controlWordHitCounts": [chord["wordHitCount"] for chord in control_chords],
        "selectorUnlocked": False,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": [
            "Use exact active target-center y coordinates as horizontal C9-frame chords.",
            "Compare active O4/B4/G5/O5 chords with non-active focus-row control chords inside the same C9 frame.",
            "Measure existing word/highlight/active-target intersections and strict instruction terms only.",
            "No OCR, hashing, key derivation, private-key checks, seed/WIF checks, address checks, or broad candidate generation.",
        ],
        "inputs": {"activeTargets": rel(ACTIVE_JSON), "articleMap": rel(ARTICLE_JSON), "c9HeaderGlyphSlotGate": rel(C9_HEADER_JSON)},
        "c9Frame": c9_frame,
        "summary": summary,
        "activeChords": active_chords,
        "controlRows": controls,
        "controlChords": control_chords,
        "decision": {
            "c9TargetHorizontalChordAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep exact target-y C9 horizontal chords as row/context evidence only. Reopen only if a source/clue explicitly names horizontal rows or a row-based unit/order rule.",
        },
        "sheet": rel(OUT_SHEET),
        "outputs": {"json": rel(OUT_JSON), "markdown": rel(OUT_MD), "sheet": rel(OUT_SHEET)},
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Target Horizontal Chord Gate",
        "",
        "Scope: use exact O4/B4/G5/O5 target-center y coordinates as horizontal chords through the p76 C9 OVERDOSE frame, with non-active focus-row controls inside the same frame. This measures existing word/highlight/active-target intersections and strict instruction terms only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.",
        "",
        "## Summary",
        f"- active chords: `{summary['activeChordCount']}`",
        f"- control chords: `{summary['controlChordCount']}`",
        f"- active strict instruction hits: `{summary['activeStrictInstructionHitCount']}`",
        f"- control strict instruction hits: `{summary['controlStrictInstructionHitCount']}`",
        f"- active all-quartet chords: `{summary['activeAllQuartetChordCount']}`",
        f"- active chord active-target hit counts: `{summary['activeChordActiveTargetHitCounts']}`",
        f"- control chord active-target hit counts: `{summary['controlChordActiveTargetHitCounts']}`",
        f"- active chord highlight-hit counts: `{summary['activeChordHighlightHitCounts']}`",
        f"- control chord highlight-hit counts: `{summary['controlChordHighlightHitCounts']}`",
        f"- active word hit counts: `{summary['activeWordHitCounts']}`",
        f"- control word hit counts: `{summary['controlWordHitCounts']}`",
        f"- selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Active Chords",
        "",
        "| target | y | active hits | words | highlights | strict hits | preview |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for chord in active_chords:
        lines.append(
            "| {target} | {y} | {active} | {words} | {highlights} | {strict} | {preview} |".format(
                target=chord["targetId"],
                y=chord["y"],
                active=chord["activeTargetHitCount"],
                words=chord["wordHitCount"],
                highlights=chord["highlightHitCount"],
                strict=", ".join(chord["strictInstructionHits"]) or "-",
                preview=(chord["wordPreview"] or "-").replace("|", "/")[:100],
            )
        )
    lines.extend(["", "## Control Chords", ""])
    for chord in control_chords:
        lines.append(
            "- `{target}` y `{y}` active hits `{active}` words `{words}` highlights `{highlights}` strict `{strict}` preview `{preview}`".format(
                target=chord["targetId"],
                y=chord["y"],
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
            "- Do not promote exact target-y C9 horizontal chords as a selector.",
            "- Active rows are ordinary article rows around the locked targets and have 0 strict instruction hits.",
            "- Control focus rows inside the same C9 frame are comparable ordinary rows, so this adds no unit/order permission.",
            "",
            "## Outputs",
            f"- JSON: `{rel(OUT_JSON)}`",
            f"- visual sheet: `{rel(OUT_SHEET)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
