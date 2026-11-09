#!/usr/bin/env python3
"""Control OVERDOSE overlap-width profile selection.

This bounded geometry pass checks whether the measured horizontal overlap
widths themselves produce a stable, source-backed selector. It records
guardrail status only; it does not derive key material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_overlap_width_profile_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_overlap_width_profile_control.json"
OUT_MD = OUT / "source_packet_overlap_width_profile_control.md"
OUT_SHEET = OUT / "source_packet_overlap_width_profile_control_sheet.jpg"

INPUTS = {
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_dominant_overlap_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/"
    "source_packet_dominant_overlap_slot_control.json",
    "source_packet_span_edge_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_edge_slot_control/"
    "source_packet_span_edge_slot_control.json",
    "source_packet_color_split_span_control": ROOT
    / "analysis_outputs/source_audit/source_packet_color_split_span_control/"
    "source_packet_color_split_span_control.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "missing_rule_frontier": ROOT
    / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json",
    "canonical_plain_article_body": ROOT
    / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "user_markdown_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "user_annotated_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "plain_article_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
}

WIDTH_PROFILE_CUES = [
    "overlap width",
    "overlap widths",
    "width profile",
    "coverage profile",
    "overlap profile",
    "slot width",
    "slot widths",
    "covered width",
    "coverage width",
    "full slot",
    "partial slot",
    "full overlap",
    "partial overlap",
    "coverage ratio",
    "dominance ratio",
    "most covered",
    "least covered",
    "widest span",
    "narrowest span",
    "highlight width",
    "measure the overlap",
    "measure overlap",
    "percent covered",
    "percentage covered",
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
        for cue in WIDTH_PROFILE_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def slot_width_from_variants(variants: list[dict]) -> float:
    values = []
    for variant in variants:
        for row in variant.get("activeRows", []) + variant.get("p75ControlRows", []):
            values.extend(float(value) for value in row.get("spanSlotOverlapsPx", []))
    return max(values) if values else 0.0


def edge_bias(left: float, right: float, balance_px: float = 8.0) -> str:
    if abs(left - right) <= balance_px:
        return "B"
    return "L" if left > right else "R"


def dominant_position(overlaps: list[float], tie_epsilon: float = 0.25) -> str:
    if not overlaps:
        return "-"
    max_overlap = max(overlaps)
    tied = [idx for idx, value in enumerate(overlaps) if abs(value - max_overlap) <= tie_epsilon]
    if len(tied) > 1:
        return "T" + "".join(str(idx + 1) for idx in tied)
    idx = tied[0]
    if idx == 0:
        return "L"
    if idx == len(overlaps) - 1:
        return "R"
    return "M"


def profile_for_row(row: dict, slot_width: float) -> dict:
    overlaps = [float(value) for value in row.get("spanSlotOverlapsPx", [])]
    slot_count = len(overlaps)
    total = round(sum(overlaps), 2)
    max_overlap = round(max(overlaps), 2) if overlaps else 0.0
    fullish_threshold = slot_width * 0.9 if slot_width else 0.0
    fullish_count = sum(1 for value in overlaps if value >= fullish_threshold)
    left = overlaps[0] if overlaps else 0.0
    right = overlaps[-1] if overlaps else 0.0
    bias = edge_bias(left, right)
    dominant = dominant_position(overlaps)
    dominance_ratio = round(max(overlaps) / total, 4) if total else 0.0
    width_bucket = "narrow"
    if total >= slot_width * 2.5:
        width_bucket = "wide"
    elif total >= slot_width * 1.5:
        width_bucket = "medium"
    return {
        "shortId": row.get("shortId"),
        "visualState": row.get("visualState"),
        "spanSlotLetters": row.get("spanSlotLetters"),
        "spanSlotIndexes": row.get("spanSlotIndexes", []),
        "spanSlotOverlapsPx": overlaps,
        "slotCount": slot_count,
        "fullishCount": fullish_count,
        "totalOverlapPx": total,
        "maxOverlapPx": max_overlap,
        "dominanceRatio": dominance_ratio,
        "dominantPosition": dominant,
        "edgeBias": bias,
        "edgeBalancePx": round(left - right, 2) if overlaps else 0.0,
        "widthBucket": width_bucket,
        "profileCode": f"S{slot_count}F{fullish_count}D{dominant}E{bias}",
        "countCode": str(slot_count),
        "fullishCode": str(fullish_count),
        "dominantCode": dominant,
        "biasCode": bias,
        "bucketCode": width_bucket[0].upper(),
    }


def make_profile_stream(variant: dict, mode: str, rows: list[dict], slot_width: float) -> dict:
    profiles = [profile_for_row(row, slot_width) for row in rows]
    return {
        "variant": variant.get("name"),
        "mode": mode,
        "targetOrder": [row.get("shortId") for row in rows],
        "slotCountStream": "-".join(row["countCode"] for row in profiles),
        "fullishCountStream": "-".join(row["fullishCode"] for row in profiles),
        "dominantPositionStream": "".join(row["dominantCode"] for row in profiles),
        "edgeBiasStream": "".join(row["biasCode"] for row in profiles),
        "widthBucketStream": "".join(row["bucketCode"] for row in profiles),
        "profileCodeStream": "|".join(row["profileCode"] for row in profiles),
        "totalOverlapStreamPx": "-".join(str(int(round(row["totalOverlapPx"]))) for row in profiles),
        "profiles": profiles,
    }


def draw_sheet(summary: dict, stream_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1840, 1020
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

    draw.rectangle((0, 0, width, 100), fill=(25, 31, 42))
    draw.text((24, 18), "OVERDOSE Overlap-Width Profile Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"variants {summary['variantCount']} | streams {summary['streamRowCount']} | "
            f"active slot-counts {', '.join(summary['activeSlotCountStreams'])} | "
            f"p75 slot-counts {', '.join(summary['p75SlotCountStreams'])} | "
            f"profile cues {summary['sourceWidthProfileCueHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 128
    draw.text((24, y), "Width-profile streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 610, 750, 910, 1070, 1230, 1390, 1580]
    headers = ["variant", "mode", "order", "slot count", "fullish", "dominant", "edge bias", "bucket", "width px"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows[:17]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["variant"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["mode"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(row["targetOrder"])[:20], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["slotCountStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["fullishCountStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), row["dominantPositionStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), row["edgeBiasStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y), row["widthBucketStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[8], y), row["totalOverlapStreamPx"], fill=(30, 30, 30), font=tiny)
        y += 44

    y += 20
    draw.text((24, y), "Source overlap-width cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:8]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text(
            (24, y),
            "No source witness names an overlap-width, coverage-profile, or ratio rule.",
            fill=(70, 70, 70),
            font=tiny,
        )
        y += 28
    y += 16
    draw.text((24, y), summary["overlapWidthFingerprint"], fill=(45, 45, 45), font=tiny)
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
    span_edge = data["source_packet_span_edge_slot_control"]
    color_split = data["source_packet_color_split_span_control"]
    format_stream = data["source_packet_active_format_stream_control"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    variants = mirrored.get("variants", [])
    slot_width = round(slot_width_from_variants(variants), 2)
    stream_rows = []
    for variant in variants:
        active = variant.get("activeRows", [])
        line_rows = sorted(active, key=lambda row: row.get("pageLine", 0))
        x_rows = sorted(active, key=lambda row: row.get("centerX", 0.0))
        black_x = [row for row in x_rows if row.get("visualState") == "K"]
        orange_x = [row for row in x_rows if row.get("visualState") == "Y"]
        p75_rows = variant.get("p75ControlRows", [])
        stream_rows.append(make_profile_stream(variant, "active_profile_line_order", line_rows, slot_width))
        stream_rows.append(make_profile_stream(variant, "active_profile_x_order", x_rows, slot_width))
        stream_rows.append(make_profile_stream(variant, "active_black_profile_x_order", black_x, slot_width))
        stream_rows.append(make_profile_stream(variant, "active_orange_profile_x_order", orange_x, slot_width))
        stream_rows.append(make_profile_stream(variant, "p75_control_profile", p75_rows, slot_width))

    active_rows = [
        row for row in stream_rows if row["mode"] in {"active_profile_line_order", "active_profile_x_order"}
    ]
    black_rows = [row for row in stream_rows if row["mode"] == "active_black_profile_x_order"]
    orange_rows = [row for row in stream_rows if row["mode"] == "active_orange_profile_x_order"]
    p75_rows = [row for row in stream_rows if row["mode"] == "p75_control_profile"]
    cue_rows = source_cue_hits(texts)

    active_slot_streams = sorted({row["slotCountStream"] for row in active_rows})
    active_fullish_streams = sorted({row["fullishCountStream"] for row in active_rows})
    active_dominant_streams = sorted({row["dominantPositionStream"] for row in active_rows})
    active_edge_bias_streams = sorted({row["edgeBiasStream"] for row in active_rows})
    black_profile_streams = sorted({row["profileCodeStream"] for row in black_rows})
    orange_profile_streams = sorted({row["profileCodeStream"] for row in orange_rows})
    p75_slot_streams = sorted({row["slotCountStream"] for row in p75_rows})
    p75_profile_streams = sorted({row["profileCodeStream"] for row in p75_rows})

    active_profile_rows = [profile for row in active_rows for profile in row["profiles"]]
    p75_profile_rows = [profile for row in p75_rows for profile in row["profiles"]]
    active_slot_counts = sorted({row["slotCount"] for row in active_profile_rows})
    p75_slot_counts = sorted({row["slotCount"] for row in p75_profile_rows})

    source_r3 = format_stream.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    selector_unlocked = bool(cue_rows) and source_r3 > 0 and triggers > 0

    summary = {
        "variantCount": mirrored.get("summary", {}).get("variantCount", len(variants)),
        "streamRowCount": len(stream_rows),
        "activeProfileStreamCount": len(active_rows),
        "slotWidthReferencePx": slot_width,
        "activeSlotCountStreams": active_slot_streams,
        "activeFullishCountStreams": active_fullish_streams,
        "activeDominantPositionStreams": active_dominant_streams,
        "activeEdgeBiasStreams": active_edge_bias_streams,
        "activeSlotCounts": active_slot_counts,
        "p75SlotCounts": p75_slot_counts,
        "blackProfileStreams": black_profile_streams,
        "orangeProfileStreams": orange_profile_streams,
        "p75SlotCountStreams": p75_slot_streams,
        "p75ProfileStreams": p75_profile_streams,
        "activeSharesP75SlotCount": bool(set(active_slot_counts) & set(p75_slot_counts)),
        "sourceWidthProfileCueHitCount": len(cue_rows),
        "dominantMatchesCenterStreamCount": dominant.get("summary", {}).get(
            "dominantMatchesCenterStreamCount"
        ),
        "spanEdgeLayoutHitRowCount": span_edge.get("summary", {}).get("layoutHitRowCount"),
        "colorSplitSourceCueHitCount": color_split.get("summary", {}).get(
            "sourceColorSplitCueHitCount"
        ),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
    }
    summary["overlapWidthFingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"activeStreams={summary['activeProfileStreamCount']}|slotWidth={summary['slotWidthReferencePx']}|"
        f"activeSlots={','.join(summary['activeSlotCountStreams'])}|"
        f"fullish={','.join(summary['activeFullishCountStreams'])}|"
        f"dom={','.join(summary['activeDominantPositionStreams'])}|"
        f"bias={','.join(summary['activeEdgeBiasStreams'])}|"
        f"p75Slots={','.join(summary['p75SlotCountStreams'])}|"
        f"shareP75Slots={int(summary['activeSharesP75SlotCount'])}|"
        f"widthCueHits={summary['sourceWidthProfileCueHitCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketOverlapWidthProfileControl": "overlap_width_profiles_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Measured overlap-width profiles are geometry scaffolding only: active profiles are two/three-slot "
            "phrase-width measurements, p75 is a separate four-slot control, mirror variants flip edge bias, "
            "and no checked source witness names an overlap-width, ratio, or coverage-profile rule."
        ),
        "nextMove": (
            "Keep overlap-width profiles as a registration diagnostic only. Reopen extraction only with distinct "
            "source-backed wording that names measuring overlap width, coverage ratio, or profile order."
        ),
    }

    draw_sheet(summary, active_rows + black_rows + orange_rows + p75_rows, cue_rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "OVERDOSE overlap-width profile control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "sourceWidthProfileCueRows": cue_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Overlap Width Profile Control",
                "",
                f"- Variant rows checked: `{summary['variantCount']}`.",
                f"- Overlap-width profile streams checked: `{summary['streamRowCount']}`.",
                f"- Active line/x profile streams checked: `{summary['activeProfileStreamCount']}`.",
                f"- Reference slot width: `{summary['slotWidthReferencePx']}` px.",
                f"- Active slot-count streams: `{', '.join(summary['activeSlotCountStreams'])}`.",
                f"- Active fullish-count streams: `{', '.join(summary['activeFullishCountStreams'])}`.",
                f"- Active dominant-position streams: `{', '.join(summary['activeDominantPositionStreams'])}`.",
                f"- Active edge-bias streams: `{', '.join(summary['activeEdgeBiasStreams'])}`.",
                f"- Active slot counts / p75 slot counts: `{active_slot_counts}` / `{p75_slot_counts}`.",
                f"- p75 slot-count streams: `{', '.join(summary['p75SlotCountStreams'])}`.",
                f"- Active shares p75 slot count: `{summary['activeSharesP75SlotCount']}`.",
                f"- Source overlap-width/profile cue hits: `{summary['sourceWidthProfileCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['overlapWidthFingerprint']}`.",
                "",
                "Decision: keep measured overlap-width profiles as source-registration diagnostics only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
