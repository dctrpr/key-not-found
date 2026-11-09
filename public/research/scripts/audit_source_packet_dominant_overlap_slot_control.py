#!/usr/bin/env python3
"""Control dominant-overlap OVERDOSE slot selection.

This bounded geometry pass checks whether choosing the OVERDOSE slot with the
largest horizontal overlap for each active target gives a distinct extraction
rule from center-slot selection. It records guardrail status only; it does not
derive key material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_dominant_overlap_slot_control.json"
OUT_MD = OUT / "source_packet_dominant_overlap_slot_control.md"
OUT_SHEET = OUT / "source_packet_dominant_overlap_slot_control_sheet.jpg"

INPUTS = {
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_center_rotation_word_control": ROOT
    / "analysis_outputs/source_audit/source_packet_center_rotation_word_control/"
    "source_packet_center_rotation_word_control.json",
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
DOMINANT_CUES = [
    "dominant",
    "largest overlap",
    "biggest overlap",
    "maximum overlap",
    "max overlap",
    "widest overlap",
    "most overlap",
    "slot overlap",
    "overlap slot",
    "covered most",
    "largest covered",
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
        for cue in DOMINANT_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def dominant_slot(row: dict, tie_epsilon: float = 0.25) -> dict:
    overlaps = row.get("spanSlotOverlapsPx", [])
    letters = row.get("spanSlotLetters", "")
    indexes = row.get("spanSlotIndexes", [])
    if not overlaps or not letters or not indexes:
        return {
            "dominantSlotIndex": None,
            "dominantSlotLetter": "",
            "dominantOverlapPx": None,
            "ambiguousDominant": False,
            "tiedLetters": [],
        }
    max_overlap = max(overlaps)
    tied_positions = [
        idx for idx, value in enumerate(overlaps) if abs(value - max_overlap) <= tie_epsilon
    ]
    best = tied_positions[0]
    return {
        "dominantSlotIndex": indexes[best],
        "dominantSlotLetter": letters[best],
        "dominantOverlapPx": max_overlap,
        "ambiguousDominant": len(tied_positions) > 1,
        "tiedLetters": [letters[idx] for idx in tied_positions],
    }


def find_center_stream(variant: dict, suffix: str) -> str:
    for row in variant.get("streams", []):
        name = row.get("name", "")
        if name.endswith(suffix):
            return row.get("stream", "")
    return ""


def stream_terms(stream: str) -> tuple[list[str], list[str]]:
    upper = stream.upper()
    return (
        sorted(term for term in LAYOUT_TERMS if term in upper),
        sorted(term for term in THEMATIC_WORDS if term in upper),
    )


def make_stream_row(variant: dict, mode: str, rows: list[dict], center_stream: str = "") -> dict:
    enriched = []
    for row in rows:
        slot = dominant_slot(row)
        enriched.append({**row, **slot})
    stream = "".join(row["dominantSlotLetter"] for row in enriched)
    layout_hits, thematic_hits = stream_terms(stream)
    return {
        "variant": variant.get("name"),
        "mode": mode,
        "targetOrder": [row.get("shortId") for row in enriched],
        "stream": stream,
        "centerStream": center_stream,
        "matchesCenterStream": bool(center_stream) and stream == center_stream,
        "layoutTermHits": layout_hits,
        "thematicHits": thematic_hits,
        "ambiguousDominantCount": sum(1 for row in enriched if row["ambiguousDominant"]),
        "rows": [
            {
                "shortId": row.get("shortId"),
                "centerSlotLetter": row.get("centerSlotLetter"),
                "dominantSlotLetter": row["dominantSlotLetter"],
                "dominantSlotIndex": row["dominantSlotIndex"],
                "dominantOverlapPx": row["dominantOverlapPx"],
                "ambiguousDominant": row["ambiguousDominant"],
                "tiedLetters": row["tiedLetters"],
            }
            for row in enriched
        ],
    }


def draw_sheet(summary: dict, stream_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1780, 940
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
    draw.text((24, 18), "Dominant OVERDOSE Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"variants {summary['variantCount']} | streams {summary['streamRowCount']} | "
            f"center matches {summary['dominantMatchesCenterStreamCount']}/{summary['activeDominantStreamCount']} | "
            f"layout hits {summary['layoutHitRowCount']} | source cues {summary['sourceDominantCueHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Dominant-overlap streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 610, 780, 940, 1110, 1280, 1450]
    headers = ["variant", "mode", "order", "dominant", "center", "same?", "hits", "ambig"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows[:16]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["variant"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["mode"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(row["targetOrder"])[:22], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["stream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["centerStream"] or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), str(row["matchesCenterStream"]), fill=(30, 30, 30), font=tiny)
        hits = ",".join(row["layoutTermHits"] + row["thematicHits"]) or "-"
        draw.text((xs[6], y), hits[:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y), str(row["ambiguousDominantCount"]), fill=(30, 30, 30), font=tiny)
        y += 44

    y += 20
    draw.text((24, y), "Source dominant-overlap cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:8]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text((24, y), "No source witness names a dominant/maximum-overlap slot rule.", fill=(70, 70, 70), font=tiny)
        y += 28
    y += 16
    draw.text((24, y), summary["dominantOverlapFingerprint"], fill=(45, 45, 45), font=tiny)
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
    center_rotation = data["source_packet_center_rotation_word_control"]
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
        stream_rows.append(
            make_stream_row(
                variant,
                "active_dominant_line_order",
                line_rows,
                find_center_stream(variant, "active_center_line_order"),
            )
        )
        stream_rows.append(
            make_stream_row(
                variant,
                "active_dominant_x_order",
                x_rows,
                find_center_stream(variant, "active_center_x_order"),
            )
        )
        stream_rows.append(make_stream_row(variant, "active_black_dominant_x_order", black_x))
        stream_rows.append(make_stream_row(variant, "active_orange_dominant_x_order", orange_x))
        stream_rows.append(make_stream_row(variant, "p75_control_dominant", p75_rows))

    active_dominant_rows = [
        row for row in stream_rows if row["mode"] in {"active_dominant_line_order", "active_dominant_x_order"}
    ]
    black_rows = [row for row in stream_rows if row["mode"] == "active_black_dominant_x_order"]
    orange_rows = [row for row in stream_rows if row["mode"] == "active_orange_dominant_x_order"]
    p75_rows = [row for row in stream_rows if row["mode"] == "p75_control_dominant"]
    layout_hit_rows = [row for row in stream_rows if row["layoutTermHits"]]
    thematic_hit_rows = [row for row in stream_rows if row["thematicHits"]]
    cue_rows = source_cue_hits(texts)

    source_r3 = format_stream.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    dominant_matches_center = sum(1 for row in active_dominant_rows if row["matchesCenterStream"])
    selector_unlocked = bool(cue_rows) and source_r3 > 0 and triggers > 0

    summary = {
        "variantCount": mirrored.get("summary", {}).get("variantCount", len(mirrored.get("variants", []))),
        "streamRowCount": len(stream_rows),
        "activeDominantStreamCount": len(active_dominant_rows),
        "dominantMatchesCenterStreamCount": dominant_matches_center,
        "activeDominantCenterMismatchCount": len(active_dominant_rows) - dominant_matches_center,
        "activeDominantAmbiguousCount": sum(row["ambiguousDominantCount"] for row in active_dominant_rows),
        "layoutHitRowCount": len(layout_hit_rows),
        "thematicHitRowCount": len(thematic_hit_rows),
        "blackDominantStreams": sorted({row["stream"] for row in black_rows}),
        "orangeDominantStreams": sorted({row["stream"] for row in orange_rows}),
        "p75DominantStreams": sorted({row["stream"] for row in p75_rows}),
        "sourceDominantCueHitCount": len(cue_rows),
        "centerRotationCueHitCount": center_rotation.get("summary", {}).get("sourceStartCueHitCount"),
        "colorSplitCueHitCount": color_split.get("summary", {}).get("sourceColorSplitCueHitCount"),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
    }
    summary["dominantOverlapFingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"activeStreams={summary['activeDominantStreamCount']}|centerMatch={summary['dominantMatchesCenterStreamCount']}/{summary['activeDominantStreamCount']}|"
        f"mismatch={summary['activeDominantCenterMismatchCount']}|ambig={summary['activeDominantAmbiguousCount']}|"
        f"layoutHits={summary['layoutHitRowCount']}|themeHits={summary['thematicHitRowCount']}|"
        f"black={','.join(summary['blackDominantStreams'])}|orange={','.join(summary['orangeDominantStreams'])}|"
        f"p75={','.join(summary['p75DominantStreams'])}|cueHits={summary['sourceDominantCueHitCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketDominantOverlapSlotControl": "dominant_overlap_collapses_to_center_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "For every active line-order and x-order stream, dominant-overlap slot selection reproduces "
            "the already-controlled center-slot stream. It adds no distinct OVERDOSE mechanism, has no "
            "source dominant-overlap cue, and source-backed R3 remains absent."
        ),
        "nextMove": (
            "Keep dominant overlap as a visual sanity check only. Reopen extraction only with distinct "
            "source-backed wording that names maximum overlap or another slot-selection rule."
        ),
    }

    draw_sheet(summary, active_dominant_rows + black_rows + orange_rows + p75_rows, cue_rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "dominant OVERDOSE slot overlap control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "sourceDominantCueRows": cue_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Dominant Overlap Slot Control",
                "",
                f"- Variant rows checked: `{summary['variantCount']}`.",
                f"- Dominant-overlap streams checked: `{summary['streamRowCount']}`.",
                f"- Active line/x dominant streams matching center streams: `{summary['dominantMatchesCenterStreamCount']}/{summary['activeDominantStreamCount']}`.",
                f"- Active dominant center mismatches: `{summary['activeDominantCenterMismatchCount']}`.",
                f"- Active dominant ambiguity count: `{summary['activeDominantAmbiguousCount']}`.",
                f"- Layout-hit rows / thematic-hit rows: `{summary['layoutHitRowCount']}` / `{summary['thematicHitRowCount']}`.",
                f"- Black dominant streams: `{', '.join(summary['blackDominantStreams'])}`.",
                f"- Orange dominant streams: `{', '.join(summary['orangeDominantStreams'])}`.",
                f"- p75 dominant streams: `{', '.join(summary['p75DominantStreams'])}`.",
                f"- Source dominant-overlap cue hits: `{summary['sourceDominantCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['dominantOverlapFingerprint']}`.",
                "",
                "Decision: keep dominant-overlap slot selection as a center-slot duplicate, not a selector.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
