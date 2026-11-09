#!/usr/bin/env python3
"""Audit bold/highlight phrase counts against OVERDOSE slot spans.

This is a bounded source-packet control pass. It asks whether the active
O4/B4/G5/O5 bold/highlight phrase word counts or character counts supply a
usable OVERDOSE slot-selection rule. It does not perform OCR extraction, key
derivation, hashing, seed/WIF/address checks, or broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_bold_phrase_length_slot_control.json"
OUT_MD = OUT / "source_packet_bold_phrase_length_slot_control.md"
OUT_SHEET = OUT / "source_packet_bold_phrase_length_slot_control_sheet.jpg"

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

COUNT_CUE_TERMS = [
    "word count",
    "letter count",
    "count words",
    "count letters",
    "number of words",
    "number of letters",
    "phrase length",
    "highlight count",
    "bold count",
    "slot count",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$']+", text)


def alnum_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]", text))


def glyph_count_no_space(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def highlight_count(summary: str | None) -> int | None:
    if not summary:
        return None
    match = re.search(r":(\d+)", summary)
    return int(match.group(1)) if match else None


def cue_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [term for term in COUNT_CUE_TERMS if term in text]
        if hits:
            rows.append({"path": rel(path), "hits": hits})
    return rows


def make_metric_row(row: dict, kind: str) -> dict:
    text = row.get("phrase") or row.get("expected") or row.get("label") or ""
    word_list = words(text)
    wc = len(word_list)
    span_count = len(row.get("spanSlotIndexes", []))
    hcount = highlight_count(row.get("docmHighlightSummary"))
    center_slot = row.get("centerSlotIndex")
    count_values = {
        "wordCount": wc,
        "alnumCount": alnum_count(text),
        "glyphNoSpaceCount": glyph_count_no_space(text),
    }
    if hcount is not None:
        count_values["docmHighlightCount"] = hcount
    center_mod_hits = {
        name: (value % 8 == center_slot if center_slot is not None else False)
        for name, value in count_values.items()
    }
    center_one_based_hits = {
        name: ((value - 1) % 8 == center_slot if center_slot is not None else False)
        for name, value in count_values.items()
    }
    return {
        "kind": kind,
        "id": row.get("id"),
        "shortId": row.get("shortId") or row.get("id"),
        "page": row.get("page", 76 if kind == "active" else None),
        "text": text,
        "color": row.get("color") or ("black" if "grey" in str(row.get("id")) else None),
        "visualState": row.get("visualState"),
        "pageLine": row.get("pageLine"),
        "corridorIndex": row.get("corridorIndex"),
        "centerSlotIndex": center_slot,
        "centerSlotLetter": row.get("centerSlotLetter"),
        "spanSlotLetters": row.get("spanSlotLetters"),
        "spanSlotCount": span_count,
        "wordCount": wc,
        "wordLengthsCsv": ",".join(str(len(w)) for w in word_list),
        "alnumCount": count_values["alnumCount"],
        "glyphNoSpaceCount": count_values["glyphNoSpaceCount"],
        "docmHighlightCount": hcount,
        "wordCountEqualsSpanSlotCount": wc == span_count,
        "centerModuloHits": center_mod_hits,
        "centerOneBasedModuloHits": center_one_based_hits,
        "layoutHits": row.get("singleRowLayoutHits", []),
        "strictInstructionHits": row.get("strictInstructionHitsInText", []),
    }


def draw_sheet(summary: dict, rows: list[dict]) -> None:
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

    draw.rectangle((0, 0, width, 104), fill=(25, 31, 42))
    draw.text((24, 18), "Bold Phrase Length / OVERDOSE Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"active word/span {summary['activeWordCountSpanSlotMatchCount']}/"
            f"{summary['activeRowCount']} | controls {summary['controlWordCountSpanSlotMatchCount']}/"
            f"{summary['controlRowCount']} | all-count center fits {summary['allActiveCenterCountFitMetricCount']} | "
            f"source cues {summary['sourceCountCueHitCount']} | R3/triggers "
            f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 132
    draw.text((24, y), "Phrase counts vs touched OVERDOSE slots", fill=(45, 45, 45), font=small)
    y += 34
    xs = [24, 88, 176, 520, 745, 845, 948, 1060, 1180, 1310, 1470, 1600]
    headers = ["kind", "id", "text", "span", "words", "lens", "alnum", "glyph", "hl", "w=span", "mod hits", "layout"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows[:16]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 46), fill=fill)
        mod_hits = []
        for name, ok in row["centerModuloHits"].items():
            if ok:
                mod_hits.append(f"{name}%8")
        for name, ok in row["centerOneBasedModuloHits"].items():
            if ok:
                mod_hits.append(f"{name}-1")
        values = [
            row["kind"],
            str(row["shortId"]),
            row["text"][:34],
            row["spanSlotLetters"] or "-",
            str(row["wordCount"]),
            row["wordLengthsCsv"] or "-",
            str(row["alnumCount"]),
            str(row["glyphNoSpaceCount"]),
            str(row["docmHighlightCount"] or "-"),
            str(row["wordCountEqualsSpanSlotCount"]),
            ",".join(mod_hits) or "-",
            ",".join(row["layoutHits"]) or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 30, 30), font=tiny)
        y += 52

    y += 18
    draw.text((24, y), summary["boldPhraseLengthSlotFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_GREY_BLACK)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [make_metric_row(row, "active") for row in active_index.get("activeRows", [])]
    grey_rows = [
        make_metric_row(row, "control_grey")
        for row in c9.get("greyBlackRows", [])
        if not row.get("isActiveCorrectedBlack")
    ]
    focused_control_rows = [
        row for row in grey_rows if row["id"] == "p75_grey_3" or row["layoutHits"]
    ]
    all_rows = active_rows + focused_control_rows

    count_metric_names = ["wordCount", "alnumCount", "glyphNoSpaceCount", "docmHighlightCount"]
    all_active_center_fit_metric_count = 0
    partial_center_fit_max = 0
    for metric in count_metric_names:
        if all(row.get(metric) is not None for row in active_rows):
            direct = sum(row["centerModuloHits"].get(metric, False) for row in active_rows)
            one_based = sum(row["centerOneBasedModuloHits"].get(metric, False) for row in active_rows)
            partial_center_fit_max = max(partial_center_fit_max, direct, one_based)
            if direct == len(active_rows) or one_based == len(active_rows):
                all_active_center_fit_metric_count += 1

    source_cues = cue_rows(SOURCE_WITNESSES)
    generated_cues = cue_rows(GENERATED_WITNESSES)
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0

    summary = {
        "activeRowCount": len(active_rows),
        "controlRowCount": len(grey_rows),
        "focusedControlRowCount": len(focused_control_rows),
        "activeWordCountSpanSlotMatchCount": sum(
            row["wordCountEqualsSpanSlotCount"] for row in active_rows
        ),
        "controlWordCountSpanSlotMatchCount": sum(
            row["wordCountEqualsSpanSlotCount"] for row in grey_rows
        ),
        "focusedControlWordCountSpanSlotMatchCount": sum(
            row["wordCountEqualsSpanSlotCount"] for row in focused_control_rows
        ),
        "activeAllWordCountSpanSlotMatch": all(
            row["wordCountEqualsSpanSlotCount"] for row in active_rows
        ),
        "p75OverControlWordCountSpanSlotMatch": any(
            row["id"] == "p75_grey_3" and row["wordCountEqualsSpanSlotCount"]
            for row in grey_rows
        ),
        "allActiveCenterCountFitMetricCount": all_active_center_fit_metric_count,
        "partialCenterCountFitMax": partial_center_fit_max,
        "sourceCountCueHitCount": len(source_cues),
        "generatedCountCueHitCount": len(generated_cues),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
    }
    summary["boldPhraseLengthSlotFingerprint"] = (
        f"active={summary['activeRowCount']}|controls={summary['controlRowCount']}|"
        f"activeWordSpan={summary['activeWordCountSpanSlotMatchCount']}/{summary['activeRowCount']}|"
        f"controlWordSpan={summary['controlWordCountSpanSlotMatchCount']}/{summary['controlRowCount']}|"
        f"p75OverWordSpan={int(summary['p75OverControlWordCountSpanSlotMatch'])}|"
        f"allCenterFitMetrics={summary['allActiveCenterCountFitMetricCount']}|"
        f"partialCenterFitMax={summary['partialCenterCountFitMax']}|"
        f"sourceCountCues={summary['sourceCountCueHitCount']}|generatedCountCues={summary['generatedCountCueHitCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )

    decision = {
        "sourcePacketBoldPhraseLengthSlotControl": "phrase_length_slot_counts_controlled_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "The active bold/highlight phrases do have a 4/4 word-count equals touched-slot-count "
            "pattern, but the non-active p75 grey OVER control has the same word-count/span-count "
            "property. Character/highlight counts do not give an all-active center-slot fit, and no "
            "source witness names word-count, letter-count, or phrase-length extraction."
        ),
        "nextMove": (
            "Keep active phrase counts as source-validation descriptors only. Reopen only with a "
            "new source-backed count/length/slot instruction that also defeats the p75 grey OVER control."
        ),
    }

    draw_sheet(summary, all_rows)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "active bold/highlight phrase word/character counts vs OVERDOSE slots; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9GreyBlackControl": rel(C9_GREY_BLACK),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourceWitnesses": [rel(path) for path in SOURCE_WITNESSES if path.exists()],
            "generatedWitnesses": [rel(path) for path in GENERATED_WITNESSES if path.exists()],
        },
        "activeRows": active_rows,
        "focusedControlRows": focused_control_rows,
        "allGreyControlRows": grey_rows,
        "sourceCountCueRows": source_cues,
        "generatedCountCueRows": generated_cues,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Bold Phrase Length Slot Control",
                "",
                f"- Active rows checked: `{summary['activeRowCount']}`.",
                f"- Non-active grey control rows checked: `{summary['controlRowCount']}`.",
                f"- Active word-count equals touched-slot-count rows: `{summary['activeWordCountSpanSlotMatchCount']}/{summary['activeRowCount']}`.",
                f"- Non-active grey control word-count equals touched-slot-count rows: `{summary['controlWordCountSpanSlotMatchCount']}/{summary['controlRowCount']}`.",
                f"- p75 `OVER` control also matches word-count/span-count: `{summary['p75OverControlWordCountSpanSlotMatch']}`.",
                f"- All-active count-to-center-slot fit metrics: `{summary['allActiveCenterCountFitMetricCount']}`.",
                f"- Best partial count-to-center-slot fit: `{summary['partialCenterCountFitMax']}/{summary['activeRowCount']}`.",
                f"- Source count/length cue hits: `{summary['sourceCountCueHitCount']}`.",
                f"- Generated/report count cue hits: `{summary['generatedCountCueHitCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Fingerprint: `{summary['boldPhraseLengthSlotFingerprint']}`.",
                "",
                "Focused rows:",
                "",
            ]
            + [
                (
                    f"- `{row['kind']}` `{row['shortId']}`: text `{row['text']}`, span `{row['spanSlotLetters']}`, "
                    f"word count `{row['wordCount']}`, word lengths `{row['wordLengthsCsv']}`, "
                    f"alnum `{row['alnumCount']}`, glyph/no-space `{row['glyphNoSpaceCount']}`, "
                    f"highlight count `{row['docmHighlightCount']}`, word-count/span-count match "
                    f"`{row['wordCountEqualsSpanSlotCount']}`, layout `{','.join(row['layoutHits']) or '-'}`."
                )
                for row in all_rows
            ]
            + [
                "",
                "Decision: phrase count and length mechanics do not reopen OVERDOSE-slot extraction.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
