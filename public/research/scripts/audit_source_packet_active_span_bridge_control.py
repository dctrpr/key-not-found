#!/usr/bin/env python3
"""Audit adjacent active OVERDOSE span bridges against controls.

This bounded source-packet pass asks whether holding/bridging neighboring
active target spans creates a selective OVER/DOSE/OVERDOSE rule. It uses the
current scan/PDF-derived source packet rows and control rows only. It does not
perform OCR extraction, key derivation, hashing, seed/WIF/address checks, or
broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_active_span_bridge_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_active_span_bridge_control.json"
OUT_MD = OUT / "source_packet_active_span_bridge_control.md"
OUT_SHEET = OUT / "source_packet_active_span_bridge_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_GREY_BLACK = ROOT / (
    "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_WITNESSES = [
    ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
]
GENERATED_WITNESSES = [
    ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.md",
]

LAYOUT_TERMS = ["OVERDOSE", "OVER", "DOSE"]
STRICT_TERMS = [
    "read",
    "take",
    "select",
    "choose",
    "letter",
    "letters",
    "word",
    "words",
    "line",
    "lines",
    "key",
    "seed",
    "private",
]
BRIDGE_CUE_TERMS = [
    "adjacent spans",
    "adjacent highlighted",
    "neighboring highlights",
    "span bridge",
    "bridge spans",
    "join spans",
    "join the spans",
    "combine spans",
    "combine the spans",
    "hold to light",
    "held to light",
    "line up the spans",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def norm_stream(text: str | None) -> str:
    return re.sub(r"[^A-Z]", "", (text or "").upper())


def term_hits(stream: str, terms: list[str]) -> list[str]:
    upper = stream.upper()
    return [term for term in terms if term in upper]


def exact_hits(stream: str, terms: list[str]) -> list[str]:
    upper = stream.upper()
    return [term for term in terms if term == upper]


def phrase(row: dict) -> str:
    return row.get("phrase") or row.get("expected") or row.get("label") or row.get("text") or ""


def cue_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [term for term in BRIDGE_CUE_TERMS if term in text]
        if hits:
            rows.append({"path": rel(path), "hits": hits})
    return rows


def row_summary(row: dict, kind: str) -> dict:
    raw_stream = row.get("spanSlotLetters")
    stream = norm_stream(raw_stream)
    return {
        "kind": kind,
        "id": row.get("id"),
        "shortId": row.get("shortId") or row.get("id"),
        "page": row.get("page", 76 if kind == "active" else None),
        "text": phrase(row),
        "visualState": row.get("visualState"),
        "color": row.get("color"),
        "pageLine": row.get("pageLine"),
        "corridorIndex": row.get("corridorIndex"),
        "centerX": row.get("centerX"),
        "box": row.get("box"),
        "spanSlotLetters": stream,
        "spanSlotCount": len(row.get("spanSlotIndexes", [])),
        "layoutHits": term_hits(stream, LAYOUT_TERMS),
        "exactLayoutHits": exact_hits(stream, LAYOUT_TERMS),
        "strictInstructionHits": term_hits(stream, STRICT_TERMS),
    }


def adjacent_pairs(rows: list[dict], group: str, order_basis: str) -> list[dict]:
    pair_rows = []
    for left, right in zip(rows, rows[1:]):
        stream = norm_stream(left.get("spanSlotLetters", "") + right.get("spanSlotLetters", ""))
        texts = [left.get("text", ""), right.get("text", "")]
        text_join = " | ".join(texts)
        pair_rows.append(
            {
                "group": group,
                "orderBasis": order_basis,
                "page": left.get("page") if left.get("page") == right.get("page") else "mixed",
                "pairIds": [left.get("shortId"), right.get("shortId")],
                "pairText": texts,
                "pairVisualState": "".join(v or "-" for v in [left.get("visualState"), right.get("visualState")]),
                "pairColor": "+".join(c or "-" for c in [left.get("color"), right.get("color")]),
                "stream": stream,
                "layoutHits": term_hits(stream, LAYOUT_TERMS),
                "exactLayoutHits": exact_hits(stream, LAYOUT_TERMS),
                "strictInstructionHitsInText": term_hits(text_join, STRICT_TERMS),
            }
        )
    return pair_rows


def control_adjacent_pairs(control_rows: list[dict]) -> list[dict]:
    pairs = []
    pages = sorted({row.get("page") for row in control_rows})
    for page in pages:
        page_rows = [row for row in control_rows if row.get("page") == page]
        page_rows.sort(
            key=lambda row: (
                (row.get("box") or [0, 0, 0, 0])[1],
                (row.get("box") or [0, 0, 0, 0])[0],
                row.get("shortId") or "",
            )
        )
        pairs.extend(adjacent_pairs(page_rows, "nonactive_page_adjacency", f"page_{page}_top_to_bottom"))
    return pairs


def draw_sheet(summary: dict, single_rows: list[dict], pair_rows: list[dict]) -> None:
    width, height = 1880, 1040
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

    draw.rectangle((0, 0, width, 104), fill=(24, 30, 39))
    draw.text((24, 18), "Active Span Bridge / OVERDOSE Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"active line exact OVER {summary['activeLineExactOverPairCount']} | "
            f"active unique exact OVER {summary['activeUniqueExactOverPairCount']} | "
            f"nonactive single layout {summary['nonactiveSingleLayoutRowCount']} | "
            f"control adjacent layout {summary['controlAdjacentLayoutPairCount']} | "
            f"source cues {summary['sourceBridgeCueHitCount']} | R3/triggers "
            f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/"
            f"{summary['triggerCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 132
    draw.text((24, y), "Single span controls", fill=(45, 45, 45), font=small)
    y += 32
    xs = [24, 112, 260, 390, 890, 1015, 1130, 1240, 1400]
    headers = ["kind", "id", "page", "text", "state", "color", "span", "exact", "contains"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(single_rows[:13]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        values = [
            row["kind"],
            str(row["shortId"]),
            str(row["page"]),
            row["text"][:58],
            row.get("visualState") or "-",
            row.get("color") or "-",
            row["spanSlotLetters"],
            ",".join(row["exactLayoutHits"]) or "-",
            ",".join(row["layoutHits"]) or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 30, 30), font=tiny)
        y += 48

    y += 18
    draw.text((24, y), "Adjacent bridges", fill=(45, 45, 45), font=small)
    y += 32
    xs = [24, 235, 455, 610, 740, 1010, 1140, 1300, 1455]
    headers = ["group", "basis", "page", "pair", "text", "stream", "exact", "contains", "text terms"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(pair_rows[:12]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        values = [
            row["group"][:24],
            row["orderBasis"][:24],
            str(row["page"]),
            "+".join(str(v) for v in row["pairIds"]),
            " / ".join(row["pairText"])[:34],
            row["stream"],
            ",".join(row["exactLayoutHits"]) or "-",
            ",".join(row["layoutHits"]) or "-",
            ",".join(row["strictInstructionHitsInText"]) or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 30, 30), font=tiny)
        y += 48

    y += 12
    draw.text((24, y), summary["activeSpanBridgeFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_GREY_BLACK)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [row_summary(row, "active") for row in active_index.get("activeRows", [])]
    active_line_order = sorted(active_rows, key=lambda row: row.get("pageLine") or 0)
    active_x_order = sorted(active_rows, key=lambda row: row.get("centerX") or 0.0)

    nonactive_rows = [
        row_summary(row, "nonactive_grey")
        for row in c9.get("greyBlackRows", [])
        if not row.get("isActiveCorrectedBlack")
    ]

    active_line_pairs = adjacent_pairs(active_line_order, "active_line_adjacency", "readable_line_order")
    active_x_pairs = adjacent_pairs(active_x_order, "active_x_adjacency", "left_to_right_x_order")
    control_pairs = control_adjacent_pairs(nonactive_rows)
    all_active_pair_rows = active_line_pairs + active_x_pairs
    all_pair_rows = all_active_pair_rows + control_pairs

    source_cues = cue_rows(SOURCE_WITNESSES)
    generated_cues = cue_rows(GENERATED_WITNESSES)
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0
    active_unique_exact_over = {
        tuple(row["pairIds"])
        for row in all_active_pair_rows
        if "OVER" in row["exactLayoutHits"]
    }

    summary = {
        "activeRowCount": len(active_rows),
        "nonactiveRowCount": len(nonactive_rows),
        "activeLinePairCount": len(active_line_pairs),
        "activeXPairCount": len(active_x_pairs),
        "activeLineExactOverPairCount": sum("OVER" in row["exactLayoutHits"] for row in active_line_pairs),
        "activeXExactOverPairCount": sum("OVER" in row["exactLayoutHits"] for row in active_x_pairs),
        "activeUniqueExactOverPairCount": len(active_unique_exact_over),
        "activeLayoutPairCount": sum(bool(row["layoutHits"]) for row in all_active_pair_rows),
        "controlAdjacentPairCount": len(control_pairs),
        "controlAdjacentLayoutPairCount": sum(bool(row["layoutHits"]) for row in control_pairs),
        "controlAdjacentExactOverPairCount": sum("OVER" in row["exactLayoutHits"] for row in control_pairs),
        "nonactiveSingleLayoutRowCount": sum(bool(row["layoutHits"]) for row in nonactive_rows),
        "nonactiveSingleExactOverRowCount": sum("OVER" in row["exactLayoutHits"] for row in nonactive_rows),
        "nonactiveSingleExactOverdoseRowCount": sum("OVERDOSE" in row["exactLayoutHits"] for row in nonactive_rows),
        "sourceBridgeCueHitCount": sum(len(row["hits"]) for row in source_cues),
        "generatedBridgeCueHitCount": sum(len(row["hits"]) for row in generated_cues),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
    }
    summary["activeSpanBridgeFingerprint"] = (
        f"activeRows={summary['activeRowCount']}|nonactiveRows={summary['nonactiveRowCount']}|"
        f"linePairs={summary['activeLinePairCount']}|xPairs={summary['activeXPairCount']}|"
        f"lineExactOVER={summary['activeLineExactOverPairCount']}|"
        f"xExactOVER={summary['activeXExactOverPairCount']}|"
        f"uniqueActiveExactOVER={summary['activeUniqueExactOverPairCount']}|"
        f"activeLayoutPairs={summary['activeLayoutPairCount']}|"
        f"controlPairs={summary['controlAdjacentPairCount']}|"
        f"controlLayoutPairs={summary['controlAdjacentLayoutPairCount']}|"
        f"controlExactOVER={summary['controlAdjacentExactOverPairCount']}|"
        f"nonactiveSingleLayout={summary['nonactiveSingleLayoutRowCount']}|"
        f"nonactiveExactOVER={summary['nonactiveSingleExactOverRowCount']}|"
        f"nonactiveExactOVERDOSE={summary['nonactiveSingleExactOverdoseRowCount']}|"
        f"bridgeCues={summary['sourceBridgeCueHitCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors=0"
    )

    bridge_rows = [
        row
        for row in all_pair_rows
        if row["layoutHits"] or row["exactLayoutHits"] or row["group"].startswith("active")
    ]
    single_focus_rows = [
        row
        for row in active_line_order + nonactive_rows
        if row["kind"] == "active" or row["layoutHits"] or row["exactLayoutHits"]
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Adjacent active span bridge control using current scan/PDF source-packet active rows "
            "and grey/black control rows; no key material or brute force."
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9GreyBlack": rel(C9_GREY_BLACK),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourceWitnesses": [rel(path) for path in SOURCE_WITNESSES],
            "generatedWitnesses": [rel(path) for path in GENERATED_WITNESSES],
        },
        "singleSpanRows": single_focus_rows,
        "activeLineBridgeRows": active_line_pairs,
        "activeXBridgeRows": active_x_pairs,
        "controlAdjacentBridgeRows": control_pairs,
        "bridgeCueRows": source_cues,
        "generatedBridgeCueRows": generated_cues,
        "summary": summary,
        "decision": {
            "sourcePacketActiveSpanBridgeControl": "adjacent_span_bridge_controlled_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "B4+G5 produces exact OVER when adjacent active spans are bridged, but it is the "
                "same already-known black-pair OVER. Non-active controls already contain exact "
                "OVER and exact OVERDOSE as single spans and also produce layout hits under page "
                "adjacency. No checked source witness names an adjacent-span bridge unit/order."
            ),
            "nextMove": (
                "Treat adjacent active span bridging as a visual/layout echo only. The best next "
                "move remains source/physical/original-layout or raw clue validation that names "
                "the transform, unit, and order."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(summary, single_focus_rows, bridge_rows)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    active_line_streams = ", ".join(
        f"{'+'.join(row['pairIds'])}={row['stream']}" for row in active_line_pairs
    )
    control_layout_examples = [
        row for row in control_pairs if row["layoutHits"] or row["exactLayoutHits"]
    ][:6]
    control_example_text = "\n".join(
        f"  - `{'+'.join(row['pairIds'])}` -> `{row['stream']}` hits `{','.join(row['layoutHits'])}`"
        for row in control_layout_examples
    ) or "  - none"

    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Active Span Bridge Control",
                "",
                f"- Created: `{result['createdAt']}`",
                f"- Scope: {result['scope']}",
                f"- Fingerprint: `{summary['activeSpanBridgeFingerprint']}`",
                "",
                "## Findings",
                "",
                f"- Active readable-line adjacent span streams: `{active_line_streams}`.",
                (
                    "- The only active exact `OVER` bridge is `B4+G5`; this is the known "
                    "black-pair span bridge, not a new ordering rule."
                ),
                (
                    f"- Non-active single-span controls with layout hits: "
                    f"`{summary['nonactiveSingleLayoutRowCount']}`; exact `OVER`: "
                    f"`{summary['nonactiveSingleExactOverRowCount']}`; exact `OVERDOSE`: "
                    f"`{summary['nonactiveSingleExactOverdoseRowCount']}`."
                ),
                (
                    f"- Non-active page-adjacent control pairs with layout hits: "
                    f"`{summary['controlAdjacentLayoutPairCount']}` of "
                    f"`{summary['controlAdjacentPairCount']}`."
                ),
                "- Example non-active page-adjacent layout bridges:",
                control_example_text,
                (
                    f"- Source bridge-cue hits: `{summary['sourceBridgeCueHitCount']}`; "
                    f"source-backed R3 hits: `{summary['sourceBackedR3BridgeHitCount']}`; "
                    f"reopen triggers: `{summary['satisfiedReopenTriggerCount']}/"
                    f"{summary['triggerCount']}`."
                ),
                "",
                "## Decision",
                "",
                (
                    "Adjacent active span bridging is controlled as a layout echo. It can recreate "
                    "`OVER` only through the same B4/G5 black-pair bridge already seen in source "
                    "packet controls, while non-active spans already provide `OVER`, `DOSE`, and "
                    "`OVERDOSE` without unlocking any source-backed unit/order."
                ),
                "",
                "## Next Move",
                "",
                (
                    "Do not continue local adjacent-span variants. Keep O4/B4/G5/O5 as validation "
                    "targets and move back to source/physical/original-layout or raw clue evidence "
                    "that explicitly names transform, unit, and order."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(summary["activeSpanBridgeFingerprint"])


if __name__ == "__main__":
    main()
