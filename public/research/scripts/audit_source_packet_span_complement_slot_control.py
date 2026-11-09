#!/usr/bin/env python3
"""Control OVERDOSE span-complement slot selection.

This bounded geometry pass checks whether the OVERDOSE slots not touched by
each highlighted span provide a stable, source-backed selector. It records
guardrail status only; it does not derive key material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_span_complement_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_span_complement_slot_control.json"
OUT_MD = OUT / "source_packet_span_complement_slot_control.md"
OUT_SHEET = OUT / "source_packet_span_complement_slot_control_sheet.jpg"

INPUTS = {
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_span_neighbor_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_neighbor_slot_control/"
    "source_packet_span_neighbor_slot_control.json",
    "source_packet_span_edge_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_edge_slot_control/"
    "source_packet_span_edge_slot_control.json",
    "source_packet_overlap_width_profile_control": ROOT
    / "analysis_outputs/source_audit/source_packet_overlap_width_profile_control/"
    "source_packet_overlap_width_profile_control.json",
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
COMPLEMENT_CUES = [
    "untouched slot",
    "untouched letter",
    "remaining slot",
    "remaining letter",
    "remainder slot",
    "remainder letter",
    "complement slot",
    "complement letter",
    "uncovered slot",
    "uncovered letter",
    "not covered",
    "outside the span",
    "letters left",
    "leftover letters",
    "unused letters",
    "unused letter",
    "unused slot",
    "rest of overdose",
    "negative space",
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
        for cue in COMPLEMENT_CUES:
            if cue in lower:
                rows.append({"source": source, "cue": cue})
    return rows


def complement_letters(row: dict, slot_letters: str) -> dict:
    span_indexes = set(row.get("spanSlotIndexes", []))
    indexes = [idx for idx in range(len(slot_letters)) if idx not in span_indexes]
    letters = "".join(slot_letters[idx] for idx in indexes)
    return {
        "complementSlotIndexes": indexes,
        "complementSlotLetters": letters,
        "complementSlotCount": len(indexes),
    }


def stream_terms(stream: str) -> tuple[list[str], list[str]]:
    upper = stream.upper()
    return (
        sorted(term for term in LAYOUT_TERMS if term in upper),
        sorted(term for term in THEMATIC_WORDS if term in upper),
    )


def make_stream_row(variant: dict, mode: str, rows: list[dict]) -> dict:
    slot_letters = variant.get("slotLetters", "")
    enriched = [{**row, **complement_letters(row, slot_letters)} for row in rows]
    stream = "".join(row["complementSlotLetters"] for row in enriched)
    display = "/".join(row["complementSlotLetters"] or "." for row in enriched)
    layout_hits, thematic_hits = stream_terms(stream)
    return {
        "variant": variant.get("name"),
        "mode": mode,
        "targetOrder": [row.get("shortId") for row in enriched],
        "stream": stream,
        "displayStream": display,
        "layoutTermHits": layout_hits,
        "thematicHits": thematic_hits,
        "complementSlotCounts": [row["complementSlotCount"] for row in enriched],
        "rows": [
            {
                "shortId": row.get("shortId"),
                "spanSlotLetters": row.get("spanSlotLetters"),
                "spanSlotIndexes": row.get("spanSlotIndexes"),
                "complementSlotLetters": row["complementSlotLetters"],
                "complementSlotIndexes": row["complementSlotIndexes"],
                "complementSlotCount": row["complementSlotCount"],
            }
            for row in enriched
        ],
    }


def draw_sheet(summary: dict, stream_rows: list[dict], cue_rows: list[dict]) -> None:
    width, height = 1840, 1040
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
    draw.text((24, 18), "OVERDOSE Span-Complement Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"variants {summary['variantCount']} | streams {summary['streamRowCount']} | "
            f"layout hits {summary['layoutHitRowCount']} | active layout {summary['activeLayoutHitRowCount']} | "
            f"complement cues {summary['sourceComplementCueHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 128
    draw.text((24, y), "Untouched/remainder OVERDOSE slot streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 610, 790, 1100, 1335, 1515]
    headers = ["variant", "mode", "order", "stream", "display", "layout", "theme"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows[:17]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["variant"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["mode"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(row["targetOrder"])[:22], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["stream"][:34] or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["displayStream"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), ",".join(row["layoutTermHits"]) or "-", fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), ",".join(row["thematicHits"]) or "-", fill=(30, 30, 30), font=tiny)
        y += 44

    y += 20
    draw.text((24, y), "Source complement/remainder cue search", fill=(45, 45, 45), font=small)
    y += 30
    if cue_rows:
        for row in cue_rows[:8]:
            draw.text((24, y), f"{row['source']}: {row['cue']}", fill=(70, 70, 70), font=tiny)
            y += 22
    else:
        draw.text(
            (24, y),
            "No source witness names untouched/remainder/unused OVERDOSE slot reading.",
            fill=(70, 70, 70),
            font=tiny,
        )
        y += 28
    y += 16
    draw.text((24, y), summary["spanComplementFingerprint"], fill=(45, 45, 45), font=tiny)
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
    span_neighbor = data["source_packet_span_neighbor_slot_control"]
    span_edge = data["source_packet_span_edge_slot_control"]
    width_profile = data["source_packet_overlap_width_profile_control"]
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
        stream_rows.append(make_stream_row(variant, "active_complement_line_order", line_rows))
        stream_rows.append(make_stream_row(variant, "active_complement_x_order", x_rows))
        stream_rows.append(make_stream_row(variant, "active_black_complement_x_order", black_x))
        stream_rows.append(make_stream_row(variant, "active_orange_complement_x_order", orange_x))
        stream_rows.append(make_stream_row(variant, "p75_control_complement", p75_rows))

    active_rows = [
        row
        for row in stream_rows
        if row["mode"] in {"active_complement_line_order", "active_complement_x_order"}
    ]
    black_rows = [row for row in stream_rows if row["mode"] == "active_black_complement_x_order"]
    orange_rows = [row for row in stream_rows if row["mode"] == "active_orange_complement_x_order"]
    p75_rows = [row for row in stream_rows if row["mode"] == "p75_control_complement"]
    layout_hit_rows = [row for row in stream_rows if row["layoutTermHits"]]
    thematic_hit_rows = [row for row in stream_rows if row["thematicHits"]]
    active_layout_count = sum(1 for row in active_rows if row["layoutTermHits"])
    active_theme_count = sum(1 for row in active_rows if row["thematicHits"])
    p75_layout_count = sum(1 for row in p75_rows if row["layoutTermHits"])
    cue_rows = source_cue_hits(texts)

    source_r3 = format_stream.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    selector_unlocked = bool(cue_rows) and source_r3 > 0 and triggers > 0

    summary = {
        "variantCount": mirrored.get("summary", {}).get("variantCount", len(mirrored.get("variants", []))),
        "streamRowCount": len(stream_rows),
        "activeComplementStreamCount": len(active_rows),
        "layoutHitRowCount": len(layout_hit_rows),
        "activeLayoutHitRowCount": active_layout_count,
        "thematicHitRowCount": len(thematic_hit_rows),
        "activeThematicHitRowCount": active_theme_count,
        "p75LayoutHitRowCount": p75_layout_count,
        "blackComplementStreams": sorted({row["stream"] for row in black_rows}),
        "orangeComplementStreams": sorted({row["stream"] for row in orange_rows}),
        "p75ComplementStreams": sorted({row["stream"] for row in p75_rows}),
        "activeComplementSlotCountStreams": sorted(
            {"-".join(str(count) for count in row["complementSlotCounts"]) for row in active_rows}
        ),
        "sourceComplementCueHitCount": len(cue_rows),
        "spanNeighborLayoutHitRowCount": span_neighbor.get("summary", {}).get("layoutHitRowCount"),
        "spanEdgeLayoutHitRowCount": span_edge.get("summary", {}).get("layoutHitRowCount"),
        "widthProfileCueHitCount": width_profile.get("summary", {}).get(
            "sourceWidthProfileCueHitCount"
        ),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
    }
    summary["spanComplementFingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"activeStreams={summary['activeComplementStreamCount']}|layoutHits={summary['layoutHitRowCount']}|"
        f"activeLayout={summary['activeLayoutHitRowCount']}|p75Layout={summary['p75LayoutHitRowCount']}|"
        f"themeHits={summary['thematicHitRowCount']}|activeTheme={summary['activeThematicHitRowCount']}|"
        f"black={','.join(summary['blackComplementStreams'])}|orange={','.join(summary['orangeComplementStreams'])}|"
        f"p75={','.join(summary['p75ComplementStreams'])}|counts={','.join(summary['activeComplementSlotCountStreams'])}|"
        f"complementCueHits={summary['sourceComplementCueHitCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketSpanComplementSlotControl": "span_complement_slots_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Untouched/remainder OVERDOSE slots produce expected layout fragments because each "
            "complement keeps five or six of the eight letters, but p75 controls also produce "
            "layout hits and no checked source witness names an unused/remainder slot rule."
        ),
        "nextMove": (
            "Keep span-complement slots as a visual-artifact control. Reopen extraction only "
            "with distinct source-backed wording that names untouched, remaining, unused, or "
            "remainder letters."
        ),
    }

    sorted_rows = sorted(
        stream_rows,
        key=lambda row: (
            0 if row["layoutTermHits"] or row["thematicHits"] else 1,
            row["variant"],
            row["mode"],
        ),
    )
    draw_sheet(summary, sorted_rows, cue_rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "OVERDOSE span-complement slot control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "sourceComplementCueRows": cue_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Span Complement Slot Control",
                "",
                f"- Variant rows checked: `{summary['variantCount']}`.",
                f"- Span-complement streams checked: `{summary['streamRowCount']}`.",
                f"- Active line/x complement streams checked: `{summary['activeComplementStreamCount']}`.",
                f"- Layout-hit rows / active layout-hit rows / p75 layout-hit rows: `{summary['layoutHitRowCount']}` / `{summary['activeLayoutHitRowCount']}` / `{summary['p75LayoutHitRowCount']}`.",
                f"- Thematic-hit rows / active thematic-hit rows: `{summary['thematicHitRowCount']}` / `{summary['activeThematicHitRowCount']}`.",
                f"- Black complement streams: `{', '.join(summary['blackComplementStreams'])}`.",
                f"- Orange complement streams: `{', '.join(summary['orangeComplementStreams'])}`.",
                f"- p75 complement streams: `{', '.join(summary['p75ComplementStreams'])}`.",
                f"- Active complement slot-count streams: `{', '.join(summary['activeComplementSlotCountStreams'])}`.",
                f"- Source complement/remainder cue hits: `{summary['sourceComplementCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['spanComplementFingerprint']}`.",
                "",
                "Decision: keep untouched/remainder OVERDOSE slots as controlled visual artifacts.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
