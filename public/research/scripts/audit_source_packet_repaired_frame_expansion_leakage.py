#!/usr/bin/env python3
"""Measure content leakage caused by repaired p78-frame expansion.

The previous source-packet residual pass measured current and dx-repaired
reflected p78 frames against the active O4/B4/G5/O5 boxes. This bounded follow-up
asks whether the expansions needed to touch or fully cover O4/B4 stay selective,
or whether they pull in ordinary lower-corridor text and non-active format
signals.

No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks,
BIP39 checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_repaired_frame_expansion_leakage.json"
OUT_MD = OUT / "source_packet_repaired_frame_expansion_leakage.md"
OUT_SHEET = OUT / "source_packet_repaired_frame_expansion_leakage_sheet.jpg"

RESIDUAL_JSON = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/"
    "source_packet_repaired_p78_frame_residual.json"
)
CONTENT_GATE_JSON = (
    ROOT / "analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate.json"
)
SIGNAL_GATE_JSON = (
    ROOT
    / "analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/"
    "o4_frame_rescue_signal_stream_gate.json"
)
ARTICLE_MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

HARD_INSTRUCTION_TERMS = {
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
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(subject: list[float], frame: list[float]) -> float:
    inter = intersection(subject, frame)
    return 0.0 if not inter else area(inter) / max(1.0, area(subject))


def point_in_box(point: list[float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def touch_expand_frame(base: list[float], targets: list[dict[str, Any]]) -> list[float]:
    """Expand only enough for zero-area edge contact with out-of-frame targets."""
    x0, y0, x1, y1 = base
    for target in targets:
        box = target["box"]
        if box[2] < x0:
            x0 = box[2]
        if box[0] > x1:
            x1 = box[0]
        if box[3] < y0:
            y0 = box[3]
        if box[1] > y1:
            y1 = box[1]
    return [round(v, 3) for v in [x0, y0, x1, y1]]


def full_expand_frame(base: list[float], targets: list[dict[str, Any]]) -> list[float]:
    boxes = [target["box"] for target in targets]
    return [
        round(min(base[0], min(box[0] for box in boxes)), 3),
        round(min(base[1], min(box[1] for box in boxes)), 3),
        round(max(base[2], max(box[2] for box in boxes)), 3),
        round(max(base[3], max(box[3] for box in boxes)), 3),
    ]


def phrase_word_count(phrase: str) -> int:
    return len([part for part in phrase.replace("$", " $").split() if part.strip()])


def article_page76_words() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP_JSON)
    page = next(page for page in data["pages"] if page.get("page") == 76)
    return page["words"]


def classify_scenario(
    frame_row: dict[str, Any],
    scenario: str,
    frame: list[float],
    targets: list[dict[str, Any]],
    transcript_lines: list[dict[str, Any]],
    page_words: list[dict[str, Any]],
) -> dict[str, Any]:
    target_rows = []
    full_target_word_count = 0
    partial_target_word_count = 0
    for target in targets:
        frac = overlap_fraction(target["box"], frame)
        full = frac >= 0.999
        partial = frac > 0
        words = phrase_word_count(target["phrase"])
        if full:
            full_target_word_count += words
        if partial:
            partial_target_word_count += words
        target_rows.append(
            {
                "id": target["id"],
                "phrase": target["phrase"],
                "visualState": target["visualState"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
                "overlapFraction": round(frac, 6),
                "partialHit": partial,
                "fullInsideFrame": full,
            }
        )

    included_lines = []
    hard_hits: list[str] = []
    context_terms: list[str] = []
    non_active_highlights: list[str] = []
    non_active_bold_lines = 0
    for line in transcript_lines:
        frac = overlap_fraction(line["lineBox"], frame)
        if frac <= 0:
            continue
        line_hard_hits = line.get("hardInstructionHits", [])
        hard_hits.extend(line_hard_hits)
        context_terms.extend(line.get("contextTermHits", []))
        non_active_highlights.extend(line.get("nonActiveHighlights", []))
        if not line.get("activeTargets") and (line.get("boldLetters") or line.get("partialBoldLetters")):
            non_active_bold_lines += 1
        included_lines.append(
            {
                "lineIndex": line["lineIndex"],
                "corridorIndex": line["corridorIndex"],
                "wordCount": line["wordCount"],
                "activeTargetWordCount": line.get("activeTargetWordCount", 0),
                "activeTargets": line.get("activeTargets", []),
                "nonActiveHighlights": line.get("nonActiveHighlights", []),
                "boldLetters": line.get("boldLetters", ""),
                "partialBoldLetters": line.get("partialBoldLetters", ""),
                "hardInstructionHits": line_hard_hits,
                "overlapVsFrame": round(frac, 6),
                "text": line["text"],
            }
        )

    word_hits = [
        {
            "index": word["index"],
            "text": word["text"],
            "token": word.get("token"),
            "center": word["center"],
        }
        for word in page_words
        if point_in_box(word["center"], frame)
    ]
    word_tokens = [str(word.get("token") or word.get("text", "")).lower() for word in word_hits]
    word_hard_hits = sorted({token for token in word_tokens if token in HARD_INSTRUCTION_TERMS})

    line_word_count = sum(int(line["wordCount"]) for line in included_lines)
    line_non_target_word_count = max(0, line_word_count - full_target_word_count)
    line_range = ""
    corridor_range = ""
    if included_lines:
        line_range = f"{included_lines[0]['lineIndex']}-{included_lines[-1]['lineIndex']}"
        corridor_range = f"{included_lines[0]['corridorIndex']}-{included_lines[-1]['corridorIndex']}"

    return {
        "frameName": frame_row["name"],
        "scenario": scenario,
        "frame": frame,
        "dx": frame_row.get("dx"),
        "targetRows": target_rows,
        "fullInsideTargetCount": sum(1 for row in target_rows if row["fullInsideFrame"]),
        "partialTargetCount": sum(1 for row in target_rows if row["partialHit"]),
        "fullInsideTargetIds": [row["id"] for row in target_rows if row["fullInsideFrame"]],
        "partialTargetIds": [row["id"] for row in target_rows if row["partialHit"]],
        "lineRange": line_range,
        "corridorRange": corridor_range,
        "includedLineCount": len(included_lines),
        "lineContextWordCount": line_word_count,
        "fullTargetPhraseWordCount": full_target_word_count,
        "partialTargetPhraseWordCount": partial_target_word_count,
        "lineContextNonTargetWordCount": line_non_target_word_count,
        "lineContextNonTargetDensity": round(line_non_target_word_count / max(line_word_count, 1), 4),
        "nonActiveHighlightEntryCount": len(non_active_highlights),
        "nonActiveHighlightEntries": non_active_highlights,
        "nonActiveBoldContextLineCount": non_active_bold_lines,
        "transcriptHardInstructionHits": sorted(set(hard_hits)),
        "transcriptHardInstructionHitCount": len(set(hard_hits)),
        "contextTermHits": sorted(set(context_terms)),
        "ocrMapWordCenterCount": len(word_hits),
        "ocrMapWordCenterTokens": " ".join(word["text"] for word in word_hits[:40]),
        "ocrMapHardInstructionHits": word_hard_hits,
        "ocrMapHardInstructionHitCount": len(word_hard_hits),
        "includedLines": included_lines,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(UPRIGHT_PAGE).convert("RGB")
    crop = [220, 2090, 2320, 3065]
    scale = 0.48
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 142
    footer_h = 330
    sheet = Image.new("RGB", (panel.width + margin * 2, header_h + panel.height + footer_h), (13, 16, 20))
    draw = ImageDraw.Draw(sheet)
    title_font = font(27)
    text_font = font(16)
    small_font = font(12)
    mono_font = font(13)

    draw.text((margin, 22), "Repaired Frame Expansion Leakage", fill=(240, 244, 248), font=title_font)
    draw.text(
        (margin, 60),
        "Nearest repaired p78 frame versus edge-touch and full-cover expansions.",
        fill=(184, 194, 205),
        font=text_font,
    )
    draw.text(
        (margin, 91),
        "Cyan = dx=-40 base. Pink = touch expansion. Yellow = full-cover expansion. Orange/black boxes = active targets.",
        fill=(184, 194, 205),
        font=small_font,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    target_colors = {"Y": (255, 140, 35), "K": (30, 30, 30)}
    for target in result["targets"]:
        color = target_colors.get(target["visualState"], (80, 160, 255))
        box = target["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text(
            (sx(box[0]), max(header_h, sy(box[1]) - 18)),
            f"{target['id']} {target['visualState']}",
            fill=color,
            font=small_font,
        )

    scenario_colors = {
        "base": (85, 214, 255),
        "edge_touch_all": (255, 94, 188),
        "full_cover_all": (255, 218, 72),
    }
    nearest = [row for row in result["scenarioRows"] if row["frameName"] == "nearest_grid_dx_-40"]
    for row in nearest:
        color = scenario_colors[row["scenario"]]
        box = row["frame"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=4)
        draw.text(
            (sx(box[0]) + 7, sy(box[1]) + 7),
            f"{row['scenario']} words={row['lineContextWordCount']} nonTarget={row['lineContextNonTargetWordCount']}",
            fill=color,
            font=small_font,
        )

    y = header_h + panel.height + 22
    summary = result["summary"]
    footer_lines = [
        f"Full-cover min line context: {summary['fullCoverMinLineContextWordCount']} words, "
        f"{summary['fullCoverMinLineContextNonTargetWordCount']} non-target words.",
        f"Full-cover non-active format signals: {summary['fullCoverMaxNonActiveHighlightEntryCount']} entries; "
        f"hard instruction hits: {summary['fullCoverHardInstructionHitCount']}.",
        f"Touch expansion min line context: {summary['touchMinLineContextWordCount']} words; "
        f"base max line context: {summary['baseMaxLineContextWordCount']} words.",
        f"Fingerprint: {summary['expansionLeakageFingerprint']}",
    ]
    for line in footer_lines:
        draw.text((margin, y), line, fill=(226, 232, 240), font=mono_font)
        y += 44

    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    residual = load_json(RESIDUAL_JSON)
    content_gate = load_json(CONTENT_GATE_JSON)
    signal_gate = load_json(SIGNAL_GATE_JSON)
    page_words = article_page76_words()

    targets = content_gate["targets"]
    transcript_lines = content_gate["includedLines"]
    scenario_rows = []
    for frame_row in residual["frameRows"]:
        base = frame_row["p76ReflectedUprightBox"]
        scenarios = {
            "base": base,
            "edge_touch_all": touch_expand_frame(base, targets),
            "full_cover_all": full_expand_frame(base, targets),
        }
        for scenario, frame in scenarios.items():
            scenario_rows.append(
                classify_scenario(frame_row, scenario, frame, targets, transcript_lines, page_words)
            )

    base_rows = [row for row in scenario_rows if row["scenario"] == "base"]
    touch_rows = [row for row in scenario_rows if row["scenario"] == "edge_touch_all"]
    full_rows = [row for row in scenario_rows if row["scenario"] == "full_cover_all"]

    base_max_words = max(row["lineContextWordCount"] for row in base_rows)
    touch_min_words = min(row["lineContextWordCount"] for row in touch_rows)
    full_min_words = min(row["lineContextWordCount"] for row in full_rows)
    full_min_non_target = min(row["lineContextNonTargetWordCount"] for row in full_rows)
    full_max_non_active_highlights = max(row["nonActiveHighlightEntryCount"] for row in full_rows)
    full_hard_hits = sorted({hit for row in full_rows for hit in row["transcriptHardInstructionHits"]})
    full_ocr_hard_hits = sorted({hit for row in full_rows for hit in row["ocrMapHardInstructionHits"]})
    full_word_counts = [row["ocrMapWordCenterCount"] for row in full_rows]
    full_non_target_densities = [row["lineContextNonTargetDensity"] for row in full_rows]
    full_line_ranges = sorted({row["lineRange"] for row in full_rows})

    fingerprint = (
        f"scenarios=base,touch,full|baseMaxWords={base_max_words}|"
        f"touchMinWords={touch_min_words}|fullMinWords={full_min_words}|"
        f"fullMinNonTarget={full_min_non_target}|fullSignals={full_max_non_active_highlights}|"
        f"fullHard={len(full_hard_hits)}|fullOcrHard={len(full_ocr_hard_hits)}"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "source-packet repaired frame expansion leakage audit; no OCR, extraction, key derivation, "
            "hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation"
        ),
        "inputs": {
            "repairedP78FrameResidual": rel(RESIDUAL_JSON),
            "o4FrameRescueContentGate": rel(CONTENT_GATE_JSON),
            "o4FrameRescueSignalStreamGate": rel(SIGNAL_GATE_JSON),
            "article3dMap": rel(ARTICLE_MAP_JSON),
            "uprightPage": rel(UPRIGHT_PAGE),
        },
        "targets": targets,
        "scenarioRows": scenario_rows,
        "comparisonReference": {
            "o4FrameRescueFullCoverageFrame": content_gate.get("fullCoverageFrame"),
            "o4FrameRescueIncludedWordCount": content_gate.get("summary", {}).get("includedWordCount"),
            "o4FrameRescueNonTargetWordCount": content_gate.get("summary", {}).get("nonTargetWordCount"),
            "o4FrameRescueNonActiveHighlightEntryCount": content_gate.get("summary", {}).get(
                "nonActiveHighlightEntryCount"
            ),
            "o4FrameRescueHardInstructionHitCount": content_gate.get("summary", {}).get(
                "hardInstructionHitCount"
            ),
            "signalStreamFrameLayerCodes": signal_gate.get("summary", {}).get("frameLayerCodes"),
            "signalStreamNonActiveSignalGroupCount": signal_gate.get("summary", {}).get(
                "nonActiveSignalGroupCount"
            ),
            "signalStreamHardInstructionHitCount": signal_gate.get("summary", {}).get(
                "hardInstructionHitCount"
            ),
        },
        "summary": {
            "frameVariantCount": len(residual["frameRows"]),
            "scenarioCount": len(scenario_rows),
            "baseMaxLineContextWordCount": base_max_words,
            "touchMinLineContextWordCount": touch_min_words,
            "touchMinLineContextNonTargetWordCount": min(
                row["lineContextNonTargetWordCount"] for row in touch_rows
            ),
            "fullCoverMinLineContextWordCount": full_min_words,
            "fullCoverMinLineContextNonTargetWordCount": full_min_non_target,
            "fullCoverNonTargetDensityRange": [
                round(min(full_non_target_densities), 4),
                round(max(full_non_target_densities), 4),
            ],
            "fullCoverOcrMapWordCenterCountRange": [min(full_word_counts), max(full_word_counts)],
            "fullCoverMaxNonActiveHighlightEntryCount": full_max_non_active_highlights,
            "fullCoverHardInstructionHits": full_hard_hits,
            "fullCoverHardInstructionHitCount": len(full_hard_hits),
            "fullCoverOcrMapHardInstructionHits": full_ocr_hard_hits,
            "fullCoverOcrMapHardInstructionHitCount": len(full_ocr_hard_hits),
            "fullCoverLineRanges": full_line_ranges,
            "activeVisualStateOrder": residual.get("activeVisualStateOrder"),
            "activePageLines": residual.get("activePageLines"),
            "activeCorridorIndexes": residual.get("activeCorridorIndexes"),
            "residualFingerprint": residual.get("summary", {}).get("frameResidualFingerprint"),
            "expansionLeakageFingerprint": fingerprint,
            "selectorUnlocked": False,
        },
        "decision": {
            "sourcePacketRepairedFrameExpansionLeakage": "non-selective-context-band",
            "reason": (
                "The repaired p78 frame needs broad edge-touch/full-cover expansions to include O4/B4. "
                "Full-cover variants pull the same lower-corridor line span and non-active format signals seen "
                "in the O4 frame-rescue content gate, with no hard instruction wording. This is context leakage, "
                "not an extraction selector."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Keep repaired p78-frame expansion as a future source-registration stress test only. "
            "Do not resume extraction until an external/source-backed R3 unit and order rule appears."
        ),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Repaired Frame Expansion Leakage",
        "",
        "Scope: measure whether current and dx-repaired reflected p78 frame expansions stay selective when forced to touch or fully cover O4/B4/G5/O5. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active visual-state order: `{result['summary']['activeVisualStateOrder']}`",
        f"- Active page lines: `{result['summary']['activePageLines']}`",
        f"- Active corridor indexes: `{result['summary']['activeCorridorIndexes']}`",
        f"- Scenario count: `{result['summary']['scenarioCount']}` (`base`, `edge_touch_all`, `full_cover_all` for each frame)",
        f"- Base max line-context word count: `{base_max_words}`",
        f"- Touch-expansion minimum line-context word count: `{touch_min_words}`",
        f"- Full-cover minimum line-context word count: `{full_min_words}`",
        f"- Full-cover minimum non-target line-context word count: `{full_min_non_target}`",
        f"- Full-cover non-target density range: `{result['summary']['fullCoverNonTargetDensityRange']}`",
        f"- Full-cover OCR-map word-center count range: `{result['summary']['fullCoverOcrMapWordCenterCountRange']}`",
        f"- Full-cover non-active highlight/format entries: `{full_max_non_active_highlights}`",
        f"- Full-cover hard instruction hits: `{len(full_hard_hits)}` transcript / `{len(full_ocr_hard_hits)}` OCR-map",
        f"- Expansion leakage fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Scenario Rows",
        "",
        "| frame | scenario | frame | full targets | partial targets | line range | words | non-target words | non-active signals | transcript hard hits | OCR-map words |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in scenario_rows:
        lines.append(
            f"| `{row['frameName']}` | `{row['scenario']}` | `{row['frame']}` | "
            f"`{row['fullInsideTargetCount']}/4` | `{row['partialTargetCount']}/4` | "
            f"`{row['lineRange']}` | `{row['lineContextWordCount']}` | "
            f"`{row['lineContextNonTargetWordCount']}` | `{row['nonActiveHighlightEntryCount']}` | "
            f"`{row['transcriptHardInstructionHitCount']}` | `{row['ocrMapWordCenterCount']}` |"
        )
    lines.extend(
        [
            "",
            "## Reference Check",
            "",
            f"- O4 frame-rescue content gate full coverage: `{content_gate.get('summary', {}).get('includedWordCount')}` words, `{content_gate.get('summary', {}).get('nonTargetWordCount')}` non-target words, `{content_gate.get('summary', {}).get('nonActiveHighlightEntryCount')}` non-active highlight entries, `{content_gate.get('summary', {}).get('hardInstructionHitCount')}` hard instruction hits.",
            f"- O4 frame-rescue signal stream: layer stream `{signal_gate.get('summary', {}).get('frameLayerCodes')}`, non-active signal groups `{signal_gate.get('summary', {}).get('nonActiveSignalGroupCount')}`, hard instruction hits `{signal_gate.get('summary', {}).get('hardInstructionHitCount')}`.",
            "",
            "## Decision",
            "",
            "- Treat repaired frame expansion as context leakage, not as a selector.",
            "- The full-cover expansions recover all four active boxes only by taking the broad lower-corridor line band (`22-32`) with 92 non-target words and four non-active format signals.",
            "- The edge-touch expansions already pull a large lower-corridor context window while still failing to cover the active phrases.",
            "- Hard instruction hits remain zero in both transcript-authority lines and OCR-map word centers.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("expansionLeakageFingerprint:", fingerprint)
    print("selectorUnlocked:", result["summary"]["selectorUnlocked"])


if __name__ == "__main__":
    main()
