#!/usr/bin/env python3
"""Audit bold/highlight phrase edge letters against OVERDOSE slots.

This bounded source-packet pass checks whether active bold/highlight phrase
initials, finals, or word-edge streams supply a source-backed OVERDOSE slot
selector. It does not perform OCR extraction, key derivation, hashing,
seed/WIF/address checks, or broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_bold_phrase_edge_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_bold_phrase_edge_slot_control.json"
OUT_MD = OUT / "source_packet_bold_phrase_edge_slot_control.md"
OUT_SHEET = OUT / "source_packet_bold_phrase_edge_slot_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
FOLD_WORLD_ORDER = ROOT / (
    "analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/"
    "source_packet_fold_world_overdose_order_control.json"
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

EDGE_CUE_TERMS = [
    "first letter",
    "last letter",
    "initial letters",
    "word initials",
    "phrase initials",
    "acrostic",
    "edge letters",
    "take initials",
    "take first",
    "take last",
]
STRICT_INSTRUCTION_TERMS = [
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
LAYOUT_TERMS = ["OVER", "DOSE", "OVERDOSE", "DOVE", "DOV", "VEDO", "OVED"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def first_alpha(text: str) -> str:
    match = re.search(r"[A-Za-z]", text)
    return match.group(0).upper() if match else ""


def last_alpha(text: str) -> str:
    matches = re.findall(r"[A-Za-z]", text)
    return matches[-1].upper() if matches else ""


def word_initials(text: str) -> str:
    return "".join(first_alpha(token) for token in tokens(text))


def word_finals(text: str) -> str:
    return "".join(last_alpha(token) for token in tokens(text))


def hits(text: str, terms: list[str]) -> list[str]:
    upper = text.upper()
    return [term for term in terms if term.upper() in upper]


def cue_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        found = [term for term in EDGE_CUE_TERMS if term in text]
        if found:
            rows.append({"path": rel(path), "hits": found})
    return rows


def edge_row(row: dict, kind: str) -> dict:
    text = row.get("phrase") or row.get("expected") or row.get("label") or ""
    phrase_first = first_alpha(text)
    phrase_last = last_alpha(text)
    initials = word_initials(text)
    finals = word_finals(text)
    edge_combo = f"{phrase_first}{phrase_last}" if phrase_first or phrase_last else ""
    center = row.get("centerSlotLetter") or ""
    span = row.get("spanSlotLetters") or ""
    edge_streams = {
        "phraseFirst": phrase_first,
        "phraseLast": phrase_last,
        "wordInitials": initials,
        "wordFinals": finals,
        "phraseFirstLast": edge_combo,
    }
    center_hits = {
        name: bool(value and center and value == center)
        for name, value in edge_streams.items()
    }
    span_contains = {
        name: bool(value and span and value in span)
        for name, value in edge_streams.items()
    }
    return {
        "kind": kind,
        "id": row.get("id"),
        "shortId": row.get("shortId") or row.get("id"),
        "page": row.get("page", 76 if kind == "active" else None),
        "text": text,
        "visualState": row.get("visualState"),
        "color": row.get("color"),
        "centerSlotLetter": center,
        "spanSlotLetters": span,
        "edgeStreams": edge_streams,
        "centerEdgeHits": center_hits,
        "spanContainsEdgeHits": span_contains,
        "layoutHits": sorted({hit for value in edge_streams.values() for hit in hits(value, LAYOUT_TERMS)}),
        "instructionHits": sorted({hit for value in edge_streams.values() for hit in hits(value, STRICT_INSTRUCTION_TERMS)}),
    }


def order_edge_rows(active_rows: list[dict], fold_rows: list[dict]) -> list[dict]:
    by_short = {row["shortId"]: row for row in active_rows}
    rows = []
    for fold in fold_rows:
        short_ids = fold.get("shortIds", "").split()
        ordered = [by_short[sid] for sid in short_ids if sid in by_short]
        streams = {
            "phraseFirstStream": "".join(row["edgeStreams"]["phraseFirst"] for row in ordered),
            "phraseLastStream": "".join(row["edgeStreams"]["phraseLast"] for row in ordered),
            "wordInitialStream": "".join(row["edgeStreams"]["wordInitials"] for row in ordered),
            "wordFinalStream": "".join(row["edgeStreams"]["wordFinals"] for row in ordered),
            "firstLastPairStream": "".join(row["edgeStreams"]["phraseFirstLast"] for row in ordered),
        }
        all_stream_text = " ".join(streams.values())
        rows.append(
            {
                "orderName": fold.get("orderName"),
                "shortIds": " ".join(short_ids),
                "centerSlotStream": fold.get("centerSlotStream"),
                "edgeStreams": streams,
                "layoutHits": sorted({hit for value in streams.values() for hit in hits(value, LAYOUT_TERMS)}),
                "instructionHits": sorted({hit for value in streams.values() for hit in hits(value, STRICT_INSTRUCTION_TERMS)}),
                "sourceFoldLayoutHits": fold.get("layoutHits", []),
                "sourceFoldInstructionHits": fold.get("instructionHits", []),
                "streamContainsCenterSlotStream": bool(fold.get("centerSlotStream") and fold.get("centerSlotStream") in all_stream_text),
            }
        )
    return rows


def draw_sheet(summary: dict, active_rows: list[dict], control_rows: list[dict], order_rows: list[dict]) -> None:
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

    draw.rectangle((0, 0, width, 104), fill=(26, 30, 39))
    draw.text((24, 18), "Bold Phrase Edge / Acrostic Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"active center-edge hits {summary['activeCenterEdgeHitRows']}/"
            f"{summary['activeRowCount']} | order instruction/layout "
            f"{summary['orderInstructionHitRows']}/{summary['orderLayoutHitRows']} | "
            f"source cues {summary['sourceEdgeCueHitCount']} | R3/triggers "
            f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/"
            f"{summary['triggerCount']}"
        ),
        fill=(235, 235, 235),
        font=tiny,
    )

    y = 132
    draw.text((24, y), "Active and focused control edge streams", fill=(45, 45, 45), font=small)
    y += 34
    xs = [24, 90, 170, 520, 680, 780, 910, 1030, 1170, 1330, 1510]
    headers = ["kind", "id", "text", "center", "span", "first", "last", "initials", "finals", "center hit", "layout"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    display_rows = active_rows + control_rows[:6]
    for idx, row in enumerate(display_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        center_hit = any(row["centerEdgeHits"].values())
        values = [
            row["kind"],
            str(row["shortId"]),
            row["text"][:36],
            row["centerSlotLetter"] or "-",
            row["spanSlotLetters"] or "-",
            row["edgeStreams"]["phraseFirst"] or "-",
            row["edgeStreams"]["phraseLast"] or "-",
            row["edgeStreams"]["wordInitials"] or "-",
            row["edgeStreams"]["wordFinals"] or "-",
            str(center_hit),
            ",".join(row["layoutHits"]) or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 30, 30), font=tiny)
        y += 48

    y += 20
    draw.text((24, y), "Fold/order edge streams", fill=(45, 45, 45), font=small)
    y += 34
    for idx, row in enumerate(order_rows[:9]):
        fill = (250, 250, 250) if idx % 2 == 0 else (240, 244, 248)
        draw.rectangle((18, y - 4, width - 18, y + 36), fill=fill)
        text = (
            f"{row['orderName']} | {row['shortIds']} | center {row['centerSlotStream']} | "
            f"first {row['edgeStreams']['phraseFirstStream']} | last {row['edgeStreams']['phraseLastStream']} | "
            f"word-initials {row['edgeStreams']['wordInitialStream']} | hits I/L "
            f"{len(row['instructionHits'])}/{len(row['layoutHits'])}"
        )
        draw.text((24, y), text[:240], fill=(30, 30, 30), font=tiny)
        y += 42

    y += 8
    draw.text((24, y), summary["boldPhraseEdgeSlotFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    fold_world = load_json(FOLD_WORLD_ORDER)
    c9 = load_json(C9_GREY_BLACK)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [edge_row(row, "active") for row in active_index.get("activeRows", [])]
    grey_rows = [
        edge_row(row, "control_grey")
        for row in c9.get("greyBlackRows", [])
        if not row.get("isActiveCorrectedBlack")
    ]
    focused_control_rows = [
        row
        for row in grey_rows
        if row["id"] == "p75_grey_3" or row["layoutHits"] or row["instructionHits"]
    ]
    order_rows = order_edge_rows(active_rows, fold_world.get("orderRows", []))

    source_cues = cue_rows(SOURCE_WITNESSES)
    generated_cues = cue_rows(GENERATED_WITNESSES)
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0

    active_center_edge_hit_rows = sum(any(row["centerEdgeHits"].values()) for row in active_rows)
    active_span_edge_hit_rows = sum(any(row["spanContainsEdgeHits"].values()) for row in active_rows)
    control_center_edge_hit_rows = sum(any(row["centerEdgeHits"].values()) for row in grey_rows)
    control_span_edge_hit_rows = sum(any(row["spanContainsEdgeHits"].values()) for row in grey_rows)
    order_instruction_hit_rows = sum(bool(row["instructionHits"]) for row in order_rows)
    order_layout_hit_rows = sum(bool(row["layoutHits"]) for row in order_rows)
    order_contains_center_stream_rows = sum(row["streamContainsCenterSlotStream"] for row in order_rows)

    summary = {
        "activeRowCount": len(active_rows),
        "controlRowCount": len(grey_rows),
        "focusedControlRowCount": len(focused_control_rows),
        "foldOrderRowCount": len(order_rows),
        "activeCenterEdgeHitRows": active_center_edge_hit_rows,
        "activeSpanEdgeHitRows": active_span_edge_hit_rows,
        "controlCenterEdgeHitRows": control_center_edge_hit_rows,
        "controlSpanEdgeHitRows": control_span_edge_hit_rows,
        "orderInstructionHitRows": order_instruction_hit_rows,
        "orderLayoutHitRows": order_layout_hit_rows,
        "orderContainsCenterSlotStreamRows": order_contains_center_stream_rows,
        "sourceEdgeCueHitCount": len(source_cues),
        "generatedEdgeCueHitCount": len(generated_cues),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
    }
    summary["boldPhraseEdgeSlotFingerprint"] = (
        f"active={summary['activeRowCount']}|controls={summary['controlRowCount']}|"
        f"orders={summary['foldOrderRowCount']}|activeCenterEdge={active_center_edge_hit_rows}|"
        f"activeSpanEdge={active_span_edge_hit_rows}|controlCenterEdge={control_center_edge_hit_rows}|"
        f"controlSpanEdge={control_span_edge_hit_rows}|orderInstruction={order_instruction_hit_rows}|"
        f"orderLayout={order_layout_hit_rows}|orderContainsCenter={order_contains_center_stream_rows}|"
        f"sourceEdgeCues={len(source_cues)}|generatedEdgeCues={len(generated_cues)}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active bold/highlight phrase edge/acrostic streams vs OVERDOSE slots and fold-order controls; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "foldWorldOrder": rel(FOLD_WORLD_ORDER),
            "c9GreyBlackOverSlotControl": rel(C9_GREY_BLACK),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "activeRows": active_rows,
        "focusedControlRows": focused_control_rows,
        "allGreyControlRows": grey_rows,
        "orderRows": order_rows,
        "sourceEdgeCueRows": source_cues,
        "generatedEdgeCueRows": generated_cues,
        "summary": summary,
        "decision": {
            "sourcePacketBoldPhraseEdgeSlotControl": "phrase_edge_acrostic_streams_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Active phrase-edge streams do not match the active OVERDOSE center-slot stream, "
                "do not produce extraction/layout instructions under the fold-world orders, and "
                "no source witness names an initial/final/acrostic rule. Existing source-backed R3 "
                "and reopen triggers remain at zero."
            ),
            "nextMove": (
                "Keep phrase initials/finals as source-validation descriptors only. Reopen only "
                "with a source-backed acrostic/first-letter/last-letter instruction that also "
                "survives grey-control comparison."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Bold Phrase Edge Slot Control",
        "",
        "Scope: checked active bold/highlight phrase initials, finals, word-edge streams, and fold-order edge streams against OVERDOSE slots and grey controls. No OCR extraction, key derivation, hashing, seed/WIF/address checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active rows / controls / fold orders: `{len(active_rows)}` / `{len(grey_rows)}` / `{len(order_rows)}`",
        f"- Active center-edge hits: `{active_center_edge_hit_rows}`",
        f"- Active span-edge hits: `{active_span_edge_hit_rows}`",
        f"- Control center/span edge hits: `{control_center_edge_hit_rows}` / `{control_span_edge_hit_rows}`",
        f"- Fold-order instruction/layout hit rows: `{order_instruction_hit_rows}` / `{order_layout_hit_rows}`",
        f"- Fold-order edge streams containing their center-slot stream: `{order_contains_center_stream_rows}`",
        f"- Source/generated edge cue rows: `{len(source_cues)}` / `{len(generated_cues)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Fingerprint: `{summary['boldPhraseEdgeSlotFingerprint']}`",
        "",
        "## Active Rows",
        "",
        "| id | text | center | span | first | last | initials | finals | center hit | span hit | layout hits |",
        "|---|---|---|---|---|---|---|---|---:|---:|---|",
    ]
    for row in active_rows:
        lines.append(
            "| {id} | `{text}` | `{center}` | `{span}` | `{first}` | `{last}` | `{initials}` | `{finals}` | `{center_hit}` | `{span_hit}` | {layout} |".format(
                id=row["shortId"],
                text=row["text"],
                center=row["centerSlotLetter"] or "-",
                span=row["spanSlotLetters"] or "-",
                first=row["edgeStreams"]["phraseFirst"] or "-",
                last=row["edgeStreams"]["phraseLast"] or "-",
                initials=row["edgeStreams"]["wordInitials"] or "-",
                finals=row["edgeStreams"]["wordFinals"] or "-",
                center_hit=any(row["centerEdgeHits"].values()),
                span_hit=any(row["spanContainsEdgeHits"].values()),
                layout=", ".join(row["layoutHits"]) or "-",
            )
        )

    lines.extend(
        [
            "",
            "## Fold Orders",
            "",
            "| order | ids | center stream | first stream | last stream | word-initial stream | instruction hits | layout hits |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in order_rows:
        lines.append(
            "| {order} | `{ids}` | `{center}` | `{first}` | `{last}` | `{initials}` | {instructions} | {layout} |".format(
                order=row["orderName"],
                ids=row["shortIds"],
                center=row["centerSlotStream"],
                first=row["edgeStreams"]["phraseFirstStream"] or "-",
                last=row["edgeStreams"]["phraseLastStream"] or "-",
                initials=row["edgeStreams"]["wordInitialStream"] or "-",
                instructions=", ".join(row["instructionHits"]) or "-",
                layout=", ".join(row["layoutHits"]) or "-",
            )
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['sourcePacketBoldPhraseEdgeSlotControl']}`",
            f"- {result['decision']['reason']}",
            f"- {result['decision']['nextMove']}",
            f"- Sheet: `{rel(OUT_SHEET)}`",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    draw_sheet(summary, active_rows, focused_control_rows, order_rows)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
