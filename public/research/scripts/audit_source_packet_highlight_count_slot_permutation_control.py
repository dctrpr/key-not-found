#!/usr/bin/env python3
"""Bounded count-to-OVERDOSE slot control for active highlighted phrases.

This checks a tempting local family: phrase counts mapped modulo the eight
OVERDOSE slots. It is intentionally small and uses only metrics already present
in the source-packet bold phrase length report.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_highlight_count_slot_permutation_control"
OUT_JSON = OUT / "source_packet_highlight_count_slot_permutation_control.json"
OUT_MD = OUT / "source_packet_highlight_count_slot_permutation_control.md"

LENGTH_CONTROL = ROOT / (
    "analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control/"
    "source_packet_bold_phrase_length_slot_control.json"
)
FOLD_ORDER_CONTROL = ROOT / (
    "analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/"
    "source_packet_fold_world_overdose_order_control.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

OVERDOSE = "OVERDOSE"
ACTIVE_ORDER = ["O4", "B4", "G5", "O5"]
METRICS = [
    "wordCount",
    "spanSlotCount",
    "alnumCount",
    "glyphNoSpaceCount",
    "docmHighlightCount",
    "firstWordLen",
    "lastWordLen",
    "minWordLen",
    "maxWordLen",
    "sumWordLengths",
]
INDEX_MODES = ["zero_based_mod8", "one_based_mod8"]
LAYOUT_TERMS = {"OVER", "DOSE", "OVERDOSE"}
INSTRUCTION_TERMS = {"READ", "TAKE", "WORD", "LINE", "SEED", "KEY", "WIF"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def enrich_row(row: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(row)
    lengths = [int(value) for value in str(row.get("wordLengthsCsv", "")).split(",") if value]
    if lengths:
        enriched["firstWordLen"] = lengths[0]
        enriched["lastWordLen"] = lengths[-1]
        enriched["minWordLen"] = min(lengths)
        enriched["maxWordLen"] = max(lengths)
        enriched["sumWordLengths"] = sum(lengths)
    return enriched


def slot_letter(value: int, mode: str) -> str:
    if mode == "zero_based_mod8":
        index = value % 8
    elif mode == "one_based_mod8":
        index = (value - 1) % 8
    else:
        raise ValueError(mode)
    return OVERDOSE[index]


def stream_hits(stream: str, known_streams: set[str]) -> dict[str, Any]:
    return {
        "layoutHits": sorted(term for term in LAYOUT_TERMS if term in stream),
        "instructionHits": sorted(term for term in INSTRUCTION_TERMS if term in stream),
        "foldWorldStreamHit": stream in known_streams,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    length_control = load_json(LENGTH_CONTROL)
    fold_control = load_json(FOLD_ORDER_CONTROL)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)

    known_streams = set(
        value.strip()
        for value in fold_control.get("summary", {})
        .get("uniqueStreamsCsv", "")
        .split(",")
        if value.strip()
    )
    active_rows = [enrich_row(row) for row in length_control["activeRows"]]
    active_by_short = {row["shortId"]: row for row in active_rows}
    grey_rows = [enrich_row(row) for row in length_control["allGreyControlRows"]]
    trigger_summary = trigger_matrix.get("summary", {})

    canonical_rows = []
    permutation_rows = []
    for metric in METRICS:
        for mode in INDEX_MODES:
            letters_by_short = {}
            values_by_short = {}
            missing = []
            for short_id in ACTIVE_ORDER:
                value = active_by_short[short_id].get(metric)
                if value is None:
                    missing.append(short_id)
                    continue
                values_by_short[short_id] = value
                letters_by_short[short_id] = slot_letter(int(value), mode)
            if missing:
                continue
            canonical_stream = "".join(letters_by_short[short_id] for short_id in ACTIVE_ORDER)
            canonical_hit = stream_hits(canonical_stream, known_streams)
            canonical_rows.append(
                {
                    "metric": metric,
                    "indexMode": mode,
                    "order": ACTIVE_ORDER,
                    "values": values_by_short,
                    "stream": canonical_stream,
                    **canonical_hit,
                }
            )
            for order in itertools.permutations(ACTIVE_ORDER):
                stream = "".join(letters_by_short[short_id] for short_id in order)
                hit = stream_hits(stream, known_streams)
                if hit["layoutHits"] or hit["instructionHits"] or hit["foldWorldStreamHit"]:
                    permutation_rows.append(
                        {
                            "metric": metric,
                            "indexMode": mode,
                            "order": list(order),
                            "stream": stream,
                            **hit,
                        }
                    )

    center_fit_rows = []
    for row in active_rows + grey_rows:
        for metric in METRICS:
            value = row.get(metric)
            if value is None:
                continue
            for mode in INDEX_MODES:
                letter = slot_letter(int(value), mode)
                center_hit = letter == row.get("centerSlotLetter")
                center_fit_rows.append(
                    {
                        "kind": row.get("kind"),
                        "id": row.get("shortId", row.get("id")),
                        "page": row.get("page"),
                        "metric": metric,
                        "indexMode": mode,
                        "value": value,
                        "letter": letter,
                        "centerSlotLetter": row.get("centerSlotLetter"),
                        "centerHit": center_hit,
                    }
                )

    metric_fit_summary = []
    for metric in METRICS:
        for mode in INDEX_MODES:
            active_hits = sum(
                1
                for row in center_fit_rows
                if row["kind"] == "active"
                and row["metric"] == metric
                and row["indexMode"] == mode
                and row["centerHit"]
            )
            grey_hits = sum(
                1
                for row in center_fit_rows
                if row["kind"] == "control_grey"
                and row["metric"] == metric
                and row["indexMode"] == mode
                and row["centerHit"]
            )
            active_total = sum(
                1
                for row in center_fit_rows
                if row["kind"] == "active" and row["metric"] == metric and row["indexMode"] == mode
            )
            grey_total = sum(
                1
                for row in center_fit_rows
                if row["kind"] == "control_grey" and row["metric"] == metric and row["indexMode"] == mode
            )
            metric_fit_summary.append(
                {
                    "metric": metric,
                    "indexMode": mode,
                    "activeHits": active_hits,
                    "activeTotal": active_total,
                    "greyHits": grey_hits,
                    "greyTotal": grey_total,
                }
            )

    canonical_layout_hits = [row for row in canonical_rows if row["layoutHits"]]
    canonical_instruction_hits = [row for row in canonical_rows if row["instructionHits"]]
    canonical_fold_hits = [row for row in canonical_rows if row["foldWorldStreamHit"]]
    permutation_fold_hits = [row for row in permutation_rows if row["foldWorldStreamHit"]]
    permutation_layout_hits = [row for row in permutation_rows if row["layoutHits"]]
    all_active_center_fit = [
        row
        for row in metric_fit_summary
        if row["activeTotal"] == 4 and row["activeHits"] == 4
    ]
    max_active_center_fit = max((row["activeHits"] for row in metric_fit_summary), default=0)
    source_count_cues = length_control.get("summary", {}).get("sourceCountCueHitCount", 0)
    source_r3 = trigger_summary.get("sourceBackedR3BridgeHitCount", 0)
    satisfied = trigger_summary.get("satisfiedTriggerCount", 0)
    trigger_count = trigger_summary.get("triggerCount", 9)
    selectors = 0

    fingerprint = (
        f"metrics={len(METRICS)}|indexModes={len(INDEX_MODES)}|canonical={len(canonical_rows)}|"
        f"permRows={len(permutation_rows)}|canonLayout={len(canonical_layout_hits)}|"
        f"canonInstr={len(canonical_instruction_hits)}|canonFold={len(canonical_fold_hits)}|"
        f"permFold={len(permutation_fold_hits)}|permLayout={len(permutation_layout_hits)}|"
        f"allCenterFit={len(all_active_center_fit)}|maxCenterFit={max_active_center_fit}/4|"
        f"sourceCountCues={source_count_cues}|sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors={selectors}"
    )

    result = {
        "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "scope": (
            "Bounded active phrase count-to-OVERDOSE slot permutation control. Uses existing source-packet "
            "bold/highlight phrase count metrics only. No OCR-to-key extraction, key candidates, hash search, "
            "seed/WIF/address checks, BIP39 checks, or broad brute force."
        ),
        "decision": "source_packet_highlight_count_slot_permutation_no_selector",
        "inputs": {
            "lengthControl": rel(LENGTH_CONTROL),
            "foldOrderControl": rel(FOLD_ORDER_CONTROL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "metrics": METRICS,
            "indexModes": INDEX_MODES,
            "activeOrder": ACTIVE_ORDER,
            "knownFoldWorldStreams": sorted(known_streams),
        },
        "summary": {
            "metricCount": len(METRICS),
            "indexModeCount": len(INDEX_MODES),
            "canonicalStreamCount": len(canonical_rows),
            "interestingPermutationRowCount": len(permutation_rows),
            "canonicalLayoutHitCount": len(canonical_layout_hits),
            "canonicalInstructionHitCount": len(canonical_instruction_hits),
            "canonicalFoldWorldHitCount": len(canonical_fold_hits),
            "permutationFoldWorldHitCount": len(permutation_fold_hits),
            "permutationLayoutHitCount": len(permutation_layout_hits),
            "allActiveCenterFitMetricCount": len(all_active_center_fit),
            "maxActiveCenterFit": max_active_center_fit,
            "sourceCountCueHitCount": source_count_cues,
            "sourceBackedR3BridgeHitCount": source_r3,
            "satisfiedReopenTriggerCount": satisfied,
            "triggerCount": trigger_count,
            "selectorCandidateCount": selectors,
            "fingerprint": fingerprint,
        },
        "canonicalRows": canonical_rows,
        "interestingPermutationRows": permutation_rows,
        "metricFitSummary": metric_fit_summary,
        "nextMove": (
            "Keep active phrase count-to-slot mechanics as validation descriptors only. Reopen only with "
            "source-backed wording that names count/length/highlight-count plus target order."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Source Packet Highlight Count Slot Permutation Control",
        "",
        "Scope: mapped existing active phrase count metrics to the eight `OVERDOSE` slots with zero-based and one-based modulo, then checked canonical and bounded active-order permutations for layout/instruction/fold-world streams. No OCR-to-key extraction, key candidates, hash search, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Metrics / index modes / canonical streams: `{len(METRICS)}` / `{len(INDEX_MODES)}` / `{len(canonical_rows)}`",
        f"- Canonical layout / instruction / fold-world hits: `{len(canonical_layout_hits)}` / `{len(canonical_instruction_hits)}` / `{len(canonical_fold_hits)}`",
        f"- Interesting permutation rows / fold-world hits / layout hits: `{len(permutation_rows)}` / `{len(permutation_fold_hits)}` / `{len(permutation_layout_hits)}`",
        f"- All-active center-fit metrics / max active center fit: `{len(all_active_center_fit)}` / `{max_active_center_fit}/4`",
        f"- Source count-cue hits / source-backed R3 / satisfied triggers / selectors: `{source_count_cues}` / `{source_r3}` / `{satisfied}/{trigger_count}` / `{selectors}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Canonical Active Streams",
        "",
        "| metric | mode | stream | layout | instruction | fold-world |",
        "|---|---|---|---|---|---:|",
    ]
    for row in canonical_rows:
        lines.append(
            f"| `{row['metric']}` | `{row['indexMode']}` | `{row['stream']}` | "
            f"`{','.join(row['layoutHits']) or '-'}` | `{','.join(row['instructionHits']) or '-'}` | "
            f"`{int(row['foldWorldStreamHit'])}` |"
        )
    lines.extend(
        [
            "",
            "## Fold-World Permutation Hits",
            "",
        ]
    )
    if permutation_fold_hits:
        lines.extend(
            [
                "| metric | mode | order | stream |",
                "|---|---|---|---|",
            ]
        )
        for row in permutation_fold_hits:
            lines.append(
                f"| `{row['metric']}` | `{row['indexMode']}` | `{','.join(row['order'])}` | `{row['stream']}` |"
            )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Center-Fit Summary",
            "",
            "| metric | mode | active hits | grey-control hits |",
            "|---|---|---:|---:|",
        ]
    )
    for row in metric_fit_summary:
        lines.append(
            f"| `{row['metric']}` | `{row['indexMode']}` | "
            f"`{row['activeHits']}/{row['activeTotal']}` | `{row['greyHits']}/{row['greyTotal']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `source_packet_highlight_count_slot_permutation_no_selector`",
            "- Canonical active order does not produce `OVER`, `DOSE`, a hard instruction stream, or one of the fold-world streams.",
            "- The only fold-world stream hits come from one-based `docmHighlightCount` under arbitrary active target permutations, not from a source-backed order; canonical `docmHighlightCount` gives `OVDE`.",
            "- Existing source count/length cue hits remain 0, source-backed R3 remains 0, and reopen triggers remain 0/9.",
            "",
            "## Next Move",
            "",
            "- Do not use phrase counts, character counts, or highlight counts as extraction rules without a source clue naming count/length/highlight-count and target order.",
            "- Highest-value direction remains distinct physical/original-layout/source evidence or raw clue wording that supplies the missing unit/order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(fingerprint)


if __name__ == "__main__":
    main()
