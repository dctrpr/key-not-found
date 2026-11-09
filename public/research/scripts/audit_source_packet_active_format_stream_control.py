#!/usr/bin/env python3
"""Control active target format-derived streams.

This bounded pass checks whether the confirmed O4/B4/G5/O5 target text,
bold/highlight state, and OVERDOSE slot labels produce any non-arbitrary
letter stream under explicitly named order modes. It records guardrail status
only; it does not generate key material.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_active_format_stream_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_active_format_stream_control.json"
OUT_MD = OUT / "source_packet_active_format_stream_control.md"
OUT_SHEET = OUT / "source_packet_active_format_stream_control_sheet.jpg"

INPUTS = {
    "source_packet_active_target_authority_crosscheck": ROOT
    / "analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/"
    "source_packet_active_target_authority_crosscheck.json",
    "page76_target_format_authority_lock": ROOT
    / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/"
    "page76_target_format_authority_lock.json",
    "c9_header_glyph_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
}

STRICT_TERMS = {
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "read",
    "take",
    "right",
    "left",
    "fold",
    "mirror",
    "reverse",
    "count",
    "key",
    "seed",
}

LAYOUT_TERMS = {"OVER", "DOSE", "OVERDOSE"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def alpha_tokens(label: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", label)


def initials(label: str) -> str:
    return "".join(token[0].lower() for token in alpha_tokens(label))


def first_char(label: str) -> str:
    tokens = alpha_tokens(label)
    return tokens[0][0].lower() if tokens else ""


def last_char(label: str) -> str:
    tokens = alpha_tokens(label)
    return tokens[-1][-1].lower() if tokens else ""


def edges(label: str) -> str:
    return f"{first_char(label)}{last_char(label)}"


def stream_hits(stream: str) -> tuple[list[str], list[str]]:
    lower = stream.lower()
    strict = sorted(term for term in STRICT_TERMS if term in lower)
    layout = sorted(term for term in LAYOUT_TERMS if term in stream.upper())
    return strict, layout


def by_name(streams: list[dict], name: str) -> dict:
    for stream in streams:
        if stream.get("name") == name:
            return stream
    return {}


def draw_sheet(summary: dict, stream_rows: list[dict], control_rows: list[dict]) -> None:
    width, height = 1860, 960
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

    draw.rectangle((0, 0, width, 96), fill=(26, 30, 40))
    draw.text((24, 18), "Active Format Stream Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"streams {summary['streamModeCount']} | strict hits "
            f"{summary['strictInstructionHitCount']} | layout OVER streams "
            f"{summary['layoutOverStreamCount']} | selector corrections "
            f"{summary['selectorPermissionCorrectionCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Named source-authority streams", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 360, 560, 760, 990, 1220, 1430]
    headers = ["mode", "order", "state", "initials", "edges", "OVERDOSE", "hits"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(stream_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        draw.text((xs[0], y), row["mode"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["targetOrderText"][:20], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["visualStateStream"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["phraseInitialsStream"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["phraseEdgeStream"][:28], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), row["overdoseSlotStream"][:28], fill=(30, 30, 30), font=tiny)
        hits = ",".join(row["strictInstructionHits"] + row["layoutTermHits"])
        draw.text((xs[6], y), hits[:46] if hits else "-", fill=(70, 70, 70), font=tiny)
        y += 48

    y += 20
    draw.text((24, y), "Controls", fill=(45, 45, 45), font=small)
    y += 28
    xs = [24, 540, 1000]
    for x, header in zip(xs, ["control", "value", "meaning"]):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(control_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["control"][:58], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), str(row["value"])[:48], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["meaning"][:90], fill=(70, 70, 70), font=tiny)
        y += 44

    y += 14
    draw.text((24, y), summary["formatStreamFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items()}
    authority = data["source_packet_active_target_authority_crosscheck"]
    format_lock = data["page76_target_format_authority_lock"]
    header = data["c9_header_glyph_slot_gate"]
    grey_black = data["c9_grey_black_over_slot_control"]
    mirrored = data["c9_mirrored_header_glyph_gate"]
    orientation = data["source_packet_orientation_control_quartets"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    target_rows = authority.get("targetRows") or []
    c9_rows = header.get("projections", [{}])[0].get("activeRows", [])
    c9_by_short = {row.get("shortId"): row for row in c9_rows}

    def target(sort_key) -> list[dict]:
        return sorted(target_rows, key=sort_key)

    def with_c9(row: dict) -> dict:
        merged = dict(row)
        merged.update(c9_by_short.get(row.get("shortId"), {}))
        return merged

    line_order = [with_c9(row) for row in target(lambda row: row.get("pageLine", 0))]
    x_order = sorted(line_order, key=lambda row: row.get("centerX", 0.0))
    black_x_order = [row for row in x_order if row.get("visualState") == "K"]
    orange_x_order = [row for row in x_order if row.get("visualState") == "Y"]
    orange_line_order = [row for row in line_order if row.get("visualState") == "Y"]
    black_line_order = [row for row in line_order if row.get("visualState") == "K"]

    stream_specs = [
        ("readable_line_order", line_order, "source line/corridor order"),
        ("x_order", x_order, "left-to-right page geometry"),
        ("black_x_order", black_x_order, "black/grey targets in x-order"),
        ("orange_x_order", orange_x_order, "orange/yellow targets in x-order"),
        (
            "orange_then_black_line_order",
            orange_line_order + black_line_order,
            "color group, then readable line order",
        ),
        (
            "black_then_orange_line_order",
            black_line_order + orange_line_order,
            "color group, then readable line order",
        ),
    ]

    stream_rows = []
    for mode, rows, basis in stream_specs:
        labels = [row.get("label") or row.get("phrase") or "" for row in rows]
        target_order = [row.get("shortId") for row in rows]
        state_stream = "".join(row.get("visualState", "") for row in rows)
        color_stream = "".join((row.get("color") or "")[:1].upper() for row in rows)
        initials_stream = "-".join(initials(label) for label in labels)
        first_stream = "".join(first_char(label) for label in labels)
        last_stream = "".join(last_char(label) for label in labels)
        edge_stream = "-".join(edges(label) for label in labels)
        overdose_stream = "".join(row.get("centerSlotLetter", "") for row in rows)
        strict, layout = stream_hits(
            " ".join([state_stream, color_stream, initials_stream, first_stream, last_stream, edge_stream, overdose_stream])
        )
        stream_rows.append(
            {
                "mode": mode,
                "basis": basis,
                "targetOrder": target_order,
                "targetOrderText": " ".join(target_order),
                "visualStateStream": state_stream,
                "colorStream": color_stream,
                "phraseInitialsStream": initials_stream,
                "phraseFirstLetterStream": first_stream,
                "phraseLastLetterStream": last_stream,
                "phraseEdgeStream": edge_stream,
                "overdoseSlotStream": overdose_stream,
                "strictInstructionHits": strict,
                "layoutTermHits": layout,
            }
        )

    header_streams = header.get("projections", [{}])[0].get("streams", [])
    named_header_streams = [
        "p76_header_glyph_active_center_line_order",
        "p76_header_glyph_active_center_x_order",
        "p76_header_glyph_active_span_x_order",
        "p76_header_glyph_active_black_span_x_order",
        "p76_header_glyph_active_orange_span_x_order",
        "p76_header_glyph_p75_control_span",
    ]
    for name in named_header_streams:
        item = by_name(header_streams, name)
        if not item:
            continue
        strict, layout = stream_hits(item.get("stream", ""))
        stream_rows.append(
            {
                "mode": name,
                "basis": "measured OVERDOSE header glyph projection",
                "targetOrder": item.get("targetOrder", []),
                "targetOrderText": " ".join(item.get("targetOrder", [])),
                "visualStateStream": "",
                "colorStream": "",
                "phraseInitialsStream": "",
                "phraseFirstLetterStream": "",
                "phraseLastLetterStream": "",
                "phraseEdgeStream": "",
                "overdoseSlotStream": item.get("stream", ""),
                "strictInstructionHits": strict,
                "layoutTermHits": layout,
            }
        )

    strict_hit_count = sum(len(row["strictInstructionHits"]) for row in stream_rows)
    layout_over_count = sum(1 for row in stream_rows if "OVER" in row["layoutTermHits"])
    selector_permission = authority.get("summary", {}).get("selectorPermissionCorrectionCount", 0)
    source_r3 = authority.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)

    orientation_summary = orientation.get("summary", {})
    grey_summary = grey_black.get("summary", {})
    mirrored_summary = mirrored.get("summary", {})
    reopen_summary = reopen.get("summary", {})

    control_rows = [
        {
            "control": "full-page Y/K YKKY combinations",
            "value": orientation_summary.get("fullPageYkYkkyCombinationCount"),
            "meaning": "the visual state stream is not unique enough by itself",
        },
        {
            "control": "contiguous full-page Y/K YKKY windows",
            "value": orientation_summary.get("fullPageYkSlidingYkkyCount"),
            "meaning": "contiguous filtering helps locate, but does not supply unit/order wording",
        },
        {
            "control": "p75 non-active single-row OVER control",
            "value": grey_summary.get("controlSingleRowOverCount"),
            "meaning": "active black B4/G5 OVER is reproduced by a non-active page-75 grey row",
        },
        {
            "control": "mirrored variants where p75 matches active black",
            "value": f"{mirrored_summary.get('p75ControlMatchesActiveBlackCount')}/{mirrored_summary.get('variantCount')}",
            "meaning": "mirroring/reversing OVERDOSE slots does not separate the active black pair",
        },
        {
            "control": "satisfied reopen triggers",
            "value": f"{reopen_summary.get('satisfiedTriggerCount')}/{reopen_summary.get('triggerCount')}",
            "meaning": "no external/source trigger currently licenses these streams as extraction",
        },
    ]

    selector_unlocked = (
        strict_hit_count > 0
        and selector_permission > 0
        and source_r3 > 0
        and grey_summary.get("controlSingleRowOverCount", 0) == 0
    )

    summary = {
        "streamModeCount": len(stream_rows),
        "sourceAuthorityOrderModeCount": len(stream_specs),
        "overdoseProjectionStreamCount": len(stream_rows) - len(stream_specs),
        "strictInstructionHitCount": strict_hit_count,
        "layoutOverStreamCount": layout_over_count,
        "activeVisualStateOrder": format_lock.get("summary", {}).get("activeVisualStateOrder"),
        "activeColorPattern": format_lock.get("summary", {}).get("activeColorPattern"),
        "readableLineOrder": " ".join(row.get("shortId", "") for row in line_order),
        "xOrder": " ".join(row.get("shortId", "") for row in x_order),
        "blackXOrder": " ".join(row.get("shortId", "") for row in black_x_order),
        "orangeXOrder": " ".join(row.get("shortId", "") for row in orange_x_order),
        "selectorPermissionCorrectionCount": selector_permission,
        "sourceBackedR3BridgeHitCount": source_r3,
        "controlSingleRowOverCount": grey_summary.get("controlSingleRowOverCount"),
        "p75ControlMatchesActiveBlackCount": mirrored_summary.get(
            "p75ControlMatchesActiveBlackCount"
        ),
        "mirrorVariantCount": mirrored_summary.get("variantCount"),
        "fullPageYkYkkyCombinationCount": orientation_summary.get(
            "fullPageYkYkkyCombinationCount"
        ),
        "fullPageYkSlidingYkkyCount": orientation_summary.get("fullPageYkSlidingYkkyCount"),
        "satisfiedReopenTriggerCount": reopen_summary.get("satisfiedTriggerCount"),
        "triggerCount": reopen_summary.get("triggerCount"),
        "selectorUnlocked": selector_unlocked,
    }
    summary["formatStreamFingerprint"] = (
        f"streams={summary['streamModeCount']}|strictHits={strict_hit_count}|"
        f"overStreams={layout_over_count}|p75Over={summary['controlSingleRowOverCount']}|"
        f"ykky={summary['fullPageYkYkkyCombinationCount']}|"
        f"selectorCorr={selector_permission}|sourceR3={source_r3}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(selector_unlocked)}"
    )

    decision = {
        "sourcePacketActiveFormatStreamControl": "format_streams_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Named active text/format streams produce no strict unit/order instruction; "
            "the only meaningful OVERDOSE word is the already-controlled OVER span, "
            "which p75 reproduces under the same lower-frame geometry."
        ),
        "nextMove": (
            "Keep active initials/edges, YKKY/OBBO state, and OVERDOSE slot labels as "
            "source-validation descriptors only unless a distinct source supplies "
            "the missing unit/order rule."
        ),
    }

    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active target text/format stream control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "streamRows": stream_rows,
        "controlRows": control_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Active Format Stream Control",
                "",
                f"- Stream modes checked: `{summary['streamModeCount']}`.",
                f"- Strict instruction hits: `{summary['strictInstructionHitCount']}`.",
                f"- OVER layout streams: `{summary['layoutOverStreamCount']}`.",
                f"- p75 single-row OVER controls: `{summary['controlSingleRowOverCount']}`.",
                f"- Full-page YKKY combinations: `{summary['fullPageYkYkkyCombinationCount']}`.",
                f"- Selector-permission corrections: `{summary['selectorPermissionCorrectionCount']}`.",
                f"- Source-backed R3 hits: `{summary['sourceBackedR3BridgeHitCount']}`.",
                f"- Satisfied reopen triggers: `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['formatStreamFingerprint']}`.",
                "",
                "Decision: keep active text/format/OVERDOSE streams as validation descriptors only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    draw_sheet(summary, stream_rows, control_rows)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(summary["formatStreamFingerprint"])


if __name__ == "__main__":
    main()
