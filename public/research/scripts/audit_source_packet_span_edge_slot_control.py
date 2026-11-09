#!/usr/bin/env python3
"""Control OVERDOSE span-edge slot selection.

This bounded geometry pass checks whether taking the first/last OVERDOSE slot
touched by each active highlighted phrase creates a source-backed selector. It
records guardrail status only; it does not derive key material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_span_edge_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_span_edge_slot_control.json"
OUT_MD = OUT / "source_packet_span_edge_slot_control.md"
OUT_SHEET = OUT / "source_packet_span_edge_slot_control_sheet.jpg"

INPUTS = {
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_dominant_overlap_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/"
    "source_packet_dominant_overlap_slot_control.json",
    "source_packet_color_split_span_control": ROOT
    / "analysis_outputs/source_audit/source_packet_color_split_span_control/"
    "source_packet_color_split_span_control.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
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
THEMATIC_WORDS = {"DOVE", "EROS", "ROSE", "SORE"}
EDGE_CUES = [
    "left edge",
    "right edge",
    "edge slot",
    "slot edge",
    "span edge",
    "leftmost slot",
    "rightmost slot",
    "first slot",
    "last slot",
    "start slot",
    "end slot",
    "boundary slot",
    "outer slot",
    "inner slot",
    "highlight edge",
    "start of highlight",
    "end of highlight",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def source_cue_hits(texts: dict[str, str]) -> list[dict]:
    rows = []
    for source, text in texts.items():
        lower = text.lower()
        for cue in EDGE_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def edge_letters(row: dict) -> dict:
    letters = row.get("spanSlotLetters", "")
    indexes = row.get("spanSlotIndexes", [])
    overlaps = row.get("spanSlotOverlapsPx", [])
    if not letters or not indexes:
        return {
            "leftSlotIndex": None,
            "leftSlotLetter": "",
            "leftOverlapPx": None,
            "rightSlotIndex": None,
            "rightSlotLetter": "",
            "rightOverlapPx": None,
        }
    return {
        "leftSlotIndex": indexes[0],
        "leftSlotLetter": letters[0],
        "leftOverlapPx": overlaps[0] if overlaps else None,
        "rightSlotIndex": indexes[-1],
        "rightSlotLetter": letters[-1],
        "rightOverlapPx": overlaps[-1] if overlaps else None,
    }


def stream_terms(stream: str) -> tuple[list[str], list[str]]:
    upper = stream.upper()
    return (
        sorted(term for term in LAYOUT_TERMS if term in upper),
        sorted(term for term in THEMATIC_WORDS if term in upper),
    )


def make_stream_row(variant: dict, mode: str, side: str, rows: list[dict]) -> dict:
    enriched = [{**row, **edge_letters(row)} for row in rows]
    key = "leftSlotLetter" if side == "left" else "rightSlotLetter"
    stream = "".join(row[key] for row in enriched)
    layout_hits, thematic_hits = stream_terms(stream)
    return {
        "variant": variant.get("name"),
        "mode": mode,
        "side": side,
        "targetOrder": [row.get("shortId") for row in enriched],
        "stream": stream,
        "layoutTermHits": layout_hits,
        "thematicHits": thematic_hits,
        "rows": [
            {
                "shortId": row.get("shortId"),
                "spanSlotLetters": row.get("spanSlotLetters"),
                "leftSlotLetter": row["leftSlotLetter"],
                "rightSlotLetter": row["rightSlotLetter"],
                "leftOverlapPx": row["leftOverlapPx"],
                "rightOverlapPx": row["rightOverlapPx"],
            }
            for row in enriched
        ],
    }


def draw_sheet(summary: dict, stream_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1800, 980
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
    draw.text((24, 18), "Span-Edge OVERDOSE Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"variants {summary['variantCount']} | streams {summary['streamRowCount']} | "
            f"layout hits {summary['layoutHitRowCount']} | thematic hits {summary['thematicHitRowCount']} | "
            f"edge cues {summary['sourceEdgeCueHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Left/right boundary slot streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 620, 760, 930, 1120, 1290, 1460]
    headers = ["variant", "mode", "side", "order", "stream", "layout", "theme", "status"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows[:17]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["variant"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["mode"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["side"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), " ".join(row["targetOrder"])[:22], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["stream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), ",".join(row["layoutTermHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), ",".join(row["thematicHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y), "controlled" if row["layoutTermHits"] or row["thematicHits"] else "plain", fill=(70, 70, 70), font=tiny)
        y += 44

    y += 20
    draw.text((24, y), "Source edge-slot cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:8]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text((24, y), "No source witness names a first/last, left/right, or boundary-slot rule.", fill=(70, 70, 70), font=tiny)
        y += 28
    y += 16
    draw.text((24, y), summary["spanEdgeFingerprint"], fill=(45, 45, 45), font=tiny)
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
    dominant = data["source_packet_dominant_overlap_slot_control"]
    color_split = data["source_packet_color_split_span_control"]
    format_stream = data["source_packet_active_format_stream_control"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    stream_rows = []
    for variant in mirrored.get("variants", []):
        active = variant.get("activeRows", [])
        line_rows = sorted(active, key=lambda row: row.get("pageLine", 0))
        x_rows = sorted(active, key=lambda row: row.get("centerX", 0.0))
        black_x = [row for row in x_rows if row.get("visualState") == "K"]
        orange_x = [row for row in x_rows if row.get("visualState") == "Y"]
        p75_rows = variant.get("p75ControlRows", [])
        for side in ["left", "right"]:
            stream_rows.append(make_stream_row(variant, "active_edge_line_order", side, line_rows))
            stream_rows.append(make_stream_row(variant, "active_edge_x_order", side, x_rows))
            stream_rows.append(make_stream_row(variant, "active_black_edge_x_order", side, black_x))
            stream_rows.append(make_stream_row(variant, "active_orange_edge_x_order", side, orange_x))
            stream_rows.append(make_stream_row(variant, "p75_control_edge", side, p75_rows))

    active_rows = [
        row for row in stream_rows if row["mode"] in {"active_edge_line_order", "active_edge_x_order"}
    ]
    black_rows = [row for row in stream_rows if row["mode"] == "active_black_edge_x_order"]
    orange_rows = [row for row in stream_rows if row["mode"] == "active_orange_edge_x_order"]
    p75_rows = [row for row in stream_rows if row["mode"] == "p75_control_edge"]
    layout_hit_rows = [row for row in stream_rows if row["layoutTermHits"]]
    thematic_hit_rows = [row for row in stream_rows if row["thematicHits"]]
    cue_rows = source_cue_hits(texts)

    source_r3 = format_stream.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    selector_unlocked = bool(cue_rows) and source_r3 > 0 and triggers > 0
    active_layout_count = sum(1 for row in active_rows if row["layoutTermHits"])
    active_theme_count = sum(1 for row in active_rows if row["thematicHits"])

    summary = {
        "variantCount": mirrored.get("summary", {}).get("variantCount", len(mirrored.get("variants", []))),
        "streamRowCount": len(stream_rows),
        "activeEdgeStreamCount": len(active_rows),
        "layoutHitRowCount": len(layout_hit_rows),
        "thematicHitRowCount": len(thematic_hit_rows),
        "activeLayoutHitRowCount": active_layout_count,
        "activeThematicHitRowCount": active_theme_count,
        "blackEdgeStreams": sorted({row["stream"] for row in black_rows}),
        "orangeEdgeStreams": sorted({row["stream"] for row in orange_rows}),
        "p75EdgeStreams": sorted({row["stream"] for row in p75_rows}),
        "sourceEdgeCueHitCount": len(cue_rows),
        "dominantCenterMatchCount": dominant.get("summary", {}).get("dominantMatchesCenterStreamCount"),
        "colorSplitCueHitCount": color_split.get("summary", {}).get("sourceColorSplitCueHitCount"),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
    }
    summary["spanEdgeFingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"activeStreams={summary['activeEdgeStreamCount']}|layoutHits={summary['layoutHitRowCount']}|"
        f"activeLayout={summary['activeLayoutHitRowCount']}|themeHits={summary['thematicHitRowCount']}|"
        f"activeTheme={summary['activeThematicHitRowCount']}|black={','.join(summary['blackEdgeStreams'])}|"
        f"orange={','.join(summary['orangeEdgeStreams'])}|p75={','.join(summary['p75EdgeStreams'])}|"
        f"edgeCueHits={summary['sourceEdgeCueHitCount']}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketSpanEdgeSlotControl": "span_edge_slots_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "First/last touched OVERDOSE slot streams create only controlled layout/short-word artifacts, "
            "and no checked source witness names a left/right or boundary-slot reading rule."
        ),
        "nextMove": (
            "Keep span-edge slot selection as a visual control only. Reopen extraction only with distinct "
            "source-backed first/last, left/right, or boundary-slot wording."
        ),
    }

    sorted_rows = sorted(
        stream_rows,
        key=lambda row: (
            0 if row["layoutTermHits"] or row["thematicHits"] else 1,
            row["variant"],
            row["mode"],
            row["side"],
        ),
    )
    draw_sheet(summary, sorted_rows, cue_rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "OVERDOSE span-edge slot control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "sourceEdgeCueRows": cue_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Span Edge Slot Control",
                "",
                f"- Variant rows checked: `{summary['variantCount']}`.",
                f"- Span-edge streams checked: `{summary['streamRowCount']}`.",
                f"- Active line/x edge streams checked: `{summary['activeEdgeStreamCount']}`.",
                f"- Layout-hit rows / active layout-hit rows: `{summary['layoutHitRowCount']}` / `{summary['activeLayoutHitRowCount']}`.",
                f"- Thematic-hit rows / active thematic-hit rows: `{summary['thematicHitRowCount']}` / `{summary['activeThematicHitRowCount']}`.",
                f"- Black edge streams: `{', '.join(summary['blackEdgeStreams'])}`.",
                f"- Orange edge streams: `{', '.join(summary['orangeEdgeStreams'])}`.",
                f"- p75 edge streams: `{', '.join(summary['p75EdgeStreams'])}`.",
                f"- Source edge-slot cue hits: `{summary['sourceEdgeCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['spanEdgeFingerprint']}`.",
                "",
                "Decision: keep first/last touched OVERDOSE slot edges as controlled layout artifacts.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
