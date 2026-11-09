#!/usr/bin/env python3
"""Control color-split OVERDOSE span streams.

This bounded pass checks whether the active orange/black split, applied to
OVERDOSE slot spans rather than center letters, creates an extraction stream
that survives the existing p75 lower-frame control. It records guardrail status
only; it does not derive key material.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_color_split_span_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_color_split_span_control.json"
OUT_MD = OUT / "source_packet_color_split_span_control.md"
OUT_SHEET = OUT / "source_packet_color_split_span_control_sheet.jpg"

INPUTS = {
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
    "source_packet_active_index_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json",
    "source_packet_center_rotation_word_control": ROOT
    / "analysis_outputs/source_audit/source_packet_center_rotation_word_control/"
    "source_packet_center_rotation_word_control.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "canonical_plain_article_body": ROOT
    / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "user_markdown_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "user_annotated_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "plain_article_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
}

LAYOUT_TERMS = {"OVER", "DOSE", "REVO", "ESOD", "OVERDOSE"}
STRICT_INSTRUCTION_TERMS = {
    "word",
    "words",
    "letter",
    "letters",
    "read",
    "take",
    "count",
    "key",
    "private key",
    "seed",
}
COLOR_SPLIT_CUES = [
    "orange then black",
    "black then orange",
    "yellow then black",
    "black then yellow",
    "orange and black",
    "black and orange",
    "yellow and black",
    "black and yellow",
    "split by color",
    "color split",
    "highlight color",
    "highlight order",
    "grey and black",
    "gray and black",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def stream_hits(stream: str) -> tuple[list[str], list[str]]:
    upper = stream.upper()
    lower = stream.lower()
    layout = sorted(term for term in LAYOUT_TERMS if term in upper)
    strict = sorted(term for term in STRICT_INSTRUCTION_TERMS if term in lower)
    return layout, strict


def cue_hits(texts: dict[str, str]) -> list[dict]:
    rows = []
    for source, text in texts.items():
        lower = text.lower()
        for cue in COLOR_SPLIT_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def variant_streams(variant: dict) -> list[dict]:
    by_name = {row.get("name"): row for row in variant.get("streams", [])}
    rows = []
    for key in [
        "active_span_line_order",
        "active_span_x_order",
        "active_black_span_x_order",
        "active_orange_span_x_order",
        "p75_control_span",
    ]:
        stream = next((row for name, row in by_name.items() if name and name.endswith(key)), {})
        if stream:
            rows.append(
                {
                    "variant": variant.get("name"),
                    "mode": key,
                    "stream": stream.get("stream", ""),
                    "targetOrder": stream.get("targetOrder", []),
                    "mirrorGeometry": variant.get("mirrorGeometry"),
                    "reverseLabels": variant.get("reverseLabels"),
                    "slotLetters": variant.get("slotLetters"),
                }
            )

    active_rows = variant.get("activeRows", [])
    line_rows = sorted(active_rows, key=lambda row: row.get("pageLine", 0))
    x_rows = sorted(active_rows, key=lambda row: row.get("centerX", 0.0))
    black_line = [row for row in line_rows if row.get("visualState") == "K"]
    orange_line = [row for row in line_rows if row.get("visualState") == "Y"]
    black_x = [row for row in x_rows if row.get("visualState") == "K"]
    orange_x = [row for row in x_rows if row.get("visualState") == "Y"]
    derived_specs = [
        ("black_then_orange_line_span", black_line + orange_line),
        ("orange_then_black_line_span", orange_line + black_line),
        ("black_then_orange_x_span", black_x + orange_x),
        ("orange_then_black_x_span", orange_x + black_x),
    ]
    for mode, ordered_rows in derived_specs:
        rows.append(
            {
                "variant": variant.get("name"),
                "mode": mode,
                "stream": "".join(row.get("spanSlotLetters", "") for row in ordered_rows),
                "targetOrder": [row.get("shortId") for row in ordered_rows],
                "mirrorGeometry": variant.get("mirrorGeometry"),
                "reverseLabels": variant.get("reverseLabels"),
                "slotLetters": variant.get("slotLetters"),
            }
        )
    for row in rows:
        layout, strict = stream_hits(row["stream"])
        row["layoutTermHits"] = layout
        row["strictInstructionHits"] = strict
    return rows


def draw_sheet(summary: dict, stream_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1840, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Color-Split OVERDOSE Span Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"variants {summary['variantCount']} | streams {summary['streamRowCount']} | "
            f"layout hits {summary['layoutHitRowCount']} | strict hits "
            f"{summary['strictInstructionHitCount']} | p75 matches "
            f"{summary['p75ControlMatchesActiveBlackCount']}/{summary['variantCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Color split and p75-control streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 610, 850, 1010, 1220, 1430]
    headers = ["variant", "mode", "order", "stream", "layout hits", "strict hits", "status"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows[:15]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 40), fill=fill)
        draw.text((xs[0], y), row["variant"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["mode"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(row["targetOrder"])[:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["stream"][:22], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), ",".join(row["layoutTermHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), ",".join(row["strictInstructionHits"]) or "-", fill=(30, 30, 30), font=tiny)
        status = "controlled" if row["mode"] == "p75_control_span" or "black" in row["mode"] else "context"
        draw.text((xs[6], y), status, fill=(70, 70, 70), font=tiny)
        y += 46

    y += 20
    draw.text((24, y), "Source color-split cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:8]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text((24, y), "No source witness names a color-split reading rule.", fill=(70, 70, 70), font=tiny)
        y += 28
    y += 16
    draw.text((24, y), summary["colorSplitSpanFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items() if path.suffix == ".json"}
    texts = {
        name: load_text(path)
        for name, path in INPUTS.items()
        if path.suffix != ".json"
    }
    texts["plain_article_correction_report"] = json.dumps(
        data.get("plain_article_correction_report", {}), ensure_ascii=False
    )

    mirrored = data["c9_mirrored_header_glyph_gate"]
    grey_black = data["c9_grey_black_over_slot_control"]
    format_stream = data["source_packet_active_format_stream_control"]
    index_slot = data["source_packet_active_index_slot_control"]
    center_rotation = data["source_packet_center_rotation_word_control"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    stream_rows = []
    for variant in mirrored.get("variants", []):
        stream_rows.extend(variant_streams(variant))

    black_rows = [row for row in stream_rows if row["mode"] == "active_black_span_x_order"]
    p75_rows = [row for row in stream_rows if row["mode"] == "p75_control_span"]
    orange_rows = [row for row in stream_rows if row["mode"] == "active_orange_span_x_order"]
    grouped_rows = [row for row in stream_rows if "then" in row["mode"]]
    layout_hit_rows = [row for row in stream_rows if row["layoutTermHits"]]
    strict_hit_rows = [row for row in stream_rows if row["strictInstructionHits"]]
    source_cues = cue_hits(texts)

    source_r3 = format_stream.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    p75_match_count = mirrored.get("summary", {}).get("p75ControlMatchesActiveBlackCount", 0)
    variant_count = mirrored.get("summary", {}).get("variantCount", len(mirrored.get("variants", [])))
    selector_unlocked = bool(source_cues) and source_r3 > 0 and triggers > 0

    summary = {
        "variantCount": variant_count,
        "streamRowCount": len(stream_rows),
        "blackSpanRowCount": len(black_rows),
        "orangeSpanRowCount": len(orange_rows),
        "groupedColorSpanRowCount": len(grouped_rows),
        "layoutHitRowCount": len(layout_hit_rows),
        "blackLayoutHitRowCount": sum(1 for row in black_rows if row["layoutTermHits"]),
        "orangeLayoutHitRowCount": sum(1 for row in orange_rows if row["layoutTermHits"]),
        "groupedLayoutHitRowCount": sum(1 for row in grouped_rows if row["layoutTermHits"]),
        "strictInstructionHitCount": len(strict_hit_rows),
        "sourceColorSplitCueHitCount": len(source_cues),
        "uniqueBlackStreams": sorted({row["stream"] for row in black_rows}),
        "uniqueOrangeStreams": sorted({row["stream"] for row in orange_rows}),
        "uniqueLayoutHits": sorted({hit for row in layout_hit_rows for hit in row["layoutTermHits"]}),
        "p75ControlMatchesActiveBlackCount": p75_match_count,
        "p75SingleRowOverCount": grey_black.get("summary", {}).get("controlSingleRowOverCount"),
        "activeBlackOverProjectionCount": format_stream.get("summary", {}).get("activeOverStreamCount"),
        "slotOrderRotationIndex": index_slot.get("summary", {}).get("slotOrderRotationIndex"),
        "centerRotationCueHitCount": center_rotation.get("summary", {}).get("sourceStartCueHitCount"),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
    }
    summary["colorSplitSpanFingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"layoutHits={summary['layoutHitRowCount']}|blackLayout={summary['blackLayoutHitRowCount']}|"
        f"orangeLayout={summary['orangeLayoutHitRowCount']}|groupedLayout={summary['groupedLayoutHitRowCount']}|"
        f"strictHits={summary['strictInstructionHitCount']}|colorCueHits={summary['sourceColorSplitCueHitCount']}|"
        f"blackStreams={','.join(summary['uniqueBlackStreams'])}|p75match={summary['p75ControlMatchesActiveBlackCount']}/{summary['variantCount']}|"
        f"p75Over={summary['p75SingleRowOverCount']}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketColorSplitSpanControl": "color_split_spans_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Color-split OVERDOSE span streams create layout words only in the already-known black "
            "B4/G5 span and grouped variants; p75 matches the active black stream in every mirrored/reversed "
            "variant, and no checked source witness names a color-split reading rule."
        ),
        "nextMove": (
            "Keep orange/black span streams as OVERDOSE-layout controls only. Reopen extraction only with "
            "distinct source-backed color/order wording that also defeats the p75 lower-frame control."
        ),
    }

    sorted_rows = sorted(
        stream_rows,
        key=lambda row: (
            0 if row["layoutTermHits"] else 1,
            row["variant"],
            row["mode"],
        ),
    )
    draw_sheet(summary, sorted_rows, source_cues)

    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "active orange/black OVERDOSE span control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "sourceColorSplitCueRows": source_cues,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Color Split Span Control",
                "",
                f"- Variant rows checked: `{summary['variantCount']}`.",
                f"- Color/slot span streams checked: `{summary['streamRowCount']}`.",
                f"- Layout-hit rows: `{summary['layoutHitRowCount']}`.",
                f"- Black span layout-hit rows: `{summary['blackLayoutHitRowCount']}`.",
                f"- Orange span layout-hit rows: `{summary['orangeLayoutHitRowCount']}`.",
                f"- Grouped color layout-hit rows: `{summary['groupedLayoutHitRowCount']}`.",
                f"- Strict instruction stream hits: `{summary['strictInstructionHitCount']}`.",
                f"- Source color-split cue hits: `{summary['sourceColorSplitCueHitCount']}`.",
                f"- Unique active black streams: `{', '.join(summary['uniqueBlackStreams'])}`.",
                f"- p75 active-black mirror matches: `{summary['p75ControlMatchesActiveBlackCount']}/{summary['variantCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['colorSplitSpanFingerprint']}`.",
                "",
                "Decision: keep color-split OVERDOSE span words as controlled layout artifacts.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
