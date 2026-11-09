#!/usr/bin/env python3
"""Audit whether the repeated five-count system gives an extraction rule.

The capsule motif is now Issue-24-specific enough to keep as provenance/order
evidence. This pass asks a narrower question: does the repeated "five" across
p73 capsules, p79 fragments, p80 symptoms, and p76 highlight units select a
human-readable instruction or only reconfirm the G5/O5 target corridor?

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPENER = ROOT / "analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory.json"
ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
OFFSET = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"

OUT = ROOT / "analysis_outputs/source_audit/five_index_convergence"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "five_index_convergence.json"
OUT_MD = OUT / "five_index_convergence.md"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "seed",
    "first",
    "last",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def first_word(text: str) -> str:
    ws = words(text)
    return ws[0] if ws else ""


def last_word(text: str) -> str:
    ws = words(text)
    return ws[-1] if ws else ""


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, text in streams.items():
        found = []
        low = text.lower()
        for term in INSTRUCTION_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", low):
                found.append(term)
        if found:
            hits[name] = found
    return hits


def p80_symptoms(orange_boxes: dict[str, str]) -> list[str]:
    text = orange_boxes["p80_orange_1"]
    parts = [part.strip() for part in text.split("/") if part.strip()]
    return parts[1:]


def p76_units(orange_boxes: dict[str, str], grey_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    orange = [
        {
            "id": key,
            "index": int(key.rsplit("_", 1)[1]),
            "text": value,
            "kind": "orange",
        }
        for key, value in orange_boxes.items()
        if key.startswith("p76_orange_")
    ]
    grey = [
        {
            "id": row["id"],
            "index": int(row["id"].rsplit("_", 1)[1]),
            "text": row["expected"],
            "kind": "grey",
        }
        for row in grey_rows
        if row["page"] == 76
    ]
    return sorted(orange, key=lambda r: r["index"]), sorted(grey, key=lambda r: r["index"])


def step_signature(points: list[list[float]]) -> dict:
    signs = []
    deltas = []
    for a, b in zip(points, points[1:]):
        dx = round(b[0] - a[0], 2)
        dy = round(b[1] - a[1], 2)
        signs.append("R" if dx > 0 else "L" if dx < 0 else "S")
        deltas.append({"dx": dx, "dy": dy})
    x_sorted = sorted((x, i + 1) for i, (x, _y) in enumerate(points))
    rank_by_index = {}
    for rank, (_x, index) in enumerate(x_sorted, 1):
        rank_by_index[index] = rank
    return {
        "stepSigns": "".join(signs),
        "stepBits_R1_L0": "".join("1" if s == "R" else "0" if s == "L" else "?" for s in signs),
        "deltas": deltas,
        "xRanksTopToBottom": "".join(str(rank_by_index[i]) for i in range(1, len(points) + 1)),
    }


def directional_stream(units: list[dict], signs: str, mode: str) -> dict:
    # mode=outgoing maps step i to unit i. mode=incoming maps step i to unit i+1.
    selected = []
    rows = []
    for i, sign in enumerate(signs):
        unit_index = i if mode == "outgoing" else i + 1
        if unit_index >= len(units):
            continue
        unit = units[unit_index]
        picked = last_word(unit["text"]) if sign == "R" else first_word(unit["text"])
        rows.append(
            {
                "step": i + 1,
                "sign": sign,
                "unitId": unit["id"],
                "unitText": unit["text"],
                "picked": picked,
                "rule": "last word for R, first word for L",
            }
        )
        selected.append(picked)
    stream = " ".join(selected)
    return {"mode": mode, "rows": rows, "stream": stream, "reverse": " ".join(reversed(selected))}


def main() -> None:
    opener = load_json(OPENER)
    orange_boxes = load_json(ORANGE)["visualOrangeBoxes"]
    grey_rows = load_json(GREY)["rows"]
    offset = load_json(OFFSET)

    symptoms = p80_symptoms(orange_boxes)
    p76_orange, p76_grey = p76_units(orange_boxes, grey_rows)

    p73_capsules = opener["p73CapsulesTopToBottom"]
    p79_fragments = opener["p79PillFragmentsFromManualOrangeBoxes"]
    p73_points = [row["center"] for row in p73_capsules]
    p79_points = [row["center"] for row in p79_fragments]

    p73_sig = step_signature(p73_points)
    p79_sig = step_signature(p79_points)
    same_step_signature = p73_sig["stepSigns"] == p79_sig["stepSigns"]
    p79_indexes = [row["orangeBoxIndex"] for row in p79_fragments]
    index_offset = [p79 - p73 for p73, p79 in zip(range(1, 6), p79_indexes)]

    same_index_pairs = offset.get("sameIndexGapPairs", [])
    b5_o5 = [row for row in same_index_pairs if row.get("sourceId") == "B5" and row.get("targetId") == "O5"]

    fifths = [
        {"surface": "p73 capsules", "count": len(p73_capsules), "fifth": "capsule 5 (graphic, no text)"},
        {
            "surface": "p79 pill fragments",
            "count": len(p79_fragments),
            "fifth": f"orange box {p79_fragments[4]['orangeBoxIndex']} (graphic fragment, no article text)",
        },
        {"surface": "p80 symptoms", "count": len(symptoms), "fifth": symptoms[4]},
        {"surface": "p76 orange boxes", "count": len(p76_orange), "fifth": p76_orange[4]["text"]},
        {"surface": "p76 grey boxes", "count": len(p76_grey), "fifth": p76_grey[4]["text"]},
        {
            "surface": "p76 line-offset pairs",
            "count": len(same_index_pairs),
            "fifth": "B5 + 5 lines -> O5" if b5_o5 else "no B5/O5 pair",
        },
    ]

    streams = {
        "fifthSelectedText": " | ".join(row["fifth"] for row in fifths),
        "fifthTextOnly": " | ".join([symptoms[4], p76_orange[4]["text"], p76_grey[4]["text"]]),
        "p73StepSigns": p73_sig["stepSigns"],
        "p79StepSigns": p79_sig["stepSigns"],
        "p73StepBits": p73_sig["stepBits_R1_L0"],
        "p79StepBits": p79_sig["stepBits_R1_L0"],
        "p73XRanks": p73_sig["xRanksTopToBottom"],
        "p79XRanks": p79_sig["xRanksTopToBottom"],
    }

    directional = []
    for units, unit_name in [(p76_orange, "p76_orange"), (p76_grey, "p76_grey")]:
        for sign_source, signs in [("p73", p73_sig["stepSigns"]), ("p79", p79_sig["stepSigns"])]:
            for mode in ["outgoing", "incoming"]:
                row = directional_stream(units, signs, mode)
                row.update({"unitSurface": unit_name, "signSource": sign_source})
                streams[f"{sign_source}_{unit_name}_{mode}"] = row["stream"]
                streams[f"{sign_source}_{unit_name}_{mode}_reverse"] = row["reverse"]
                directional.append(row)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "five-index convergence and capsule direction audit; no key derivation",
        "counts": {
            "p73Capsules": len(p73_capsules),
            "p79PillFragments": len(p79_fragments),
            "p80Symptoms": len(symptoms),
            "p76OrangeBoxes": len(p76_orange),
            "p76GreyBoxes": len(p76_grey),
        },
        "p73StepSignature": p73_sig,
        "p79StepSignature": p79_sig,
        "sameStepSignature": same_step_signature,
        "p79OrangeBoxIndexes": p79_indexes,
        "p79MinusP73IndexOffsets": index_offset,
        "sameIndexGapPairs": same_index_pairs,
        "fifthSelections": fifths,
        "directionalStreams": directional,
        "instructionTermHits": instruction_hits(streams),
        "assessment": [
            "The five-index system is real across independent visual layers: five opener capsules, five p79 fragments, five p80 symptoms, and five p76 orange/grey units.",
            "The p73 and p79 capsule chains share the same simple left/right step signature RRLL, and p79 fragment indexes are p73 indexes plus 5.",
            "The fifth selections converge on the known lower-corridor anchors: p80 SHITCOINS, p76 orange 5 shitcoiner at heart, and p76 grey 5 Volcano Bonds.",
            "Simple direction-derived first/last-word streams from RRLL do not produce read/take/word/letter/key instructions.",
            "This strengthens five as a locator/order signal, but not as the missing extraction unit.",
        ],
        "nextMove": "Keep five as a locator that validates O5/G5 and p73/p79 provenance. Do not turn RRLL or fifth selections into key material unless a source clue names a word/letter/edge extraction unit.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Five-Index Convergence Audit",
        "",
        "Scope: test whether the repeated five-count system gives an extraction rule. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- p73 step signature: `{p73_sig['stepSigns']}` / bits `{p73_sig['stepBits_R1_L0']}` / x-ranks `{p73_sig['xRanksTopToBottom']}`",
        f"- p79 step signature: `{p79_sig['stepSigns']}` / bits `{p79_sig['stepBits_R1_L0']}` / x-ranks `{p79_sig['xRanksTopToBottom']}`",
        f"- p79 orange indexes: `{p79_indexes}`; offsets from p73 indexes: `{index_offset}`",
        f"- Instruction hits: `{result['instructionTermHits']}`",
        "",
        "## Fifth Selections",
        "",
        "| surface | count | fifth / index-5 result |",
        "|---|---:|---|",
    ]
    for row in fifths:
        lines.append(f"| {row['surface']} | {row['count']} | `{row['fifth']}` |")

    lines.extend(["", "## Directional First/Last Word Streams", ""])
    for row in directional:
        lines.append(
            f"- `{row['signSource']}` signs on `{row['unitSurface']}` / `{row['mode']}`: `{row['stream']}`; reverse `{row['reverse']}`"
        )

    lines.extend(["", "## Same-Index Line-Gap Pairs", ""])
    for row in same_index_pairs:
        lines.append(
            f"- `{row['sourceId']} -> {row['targetId']}` gap `{row['lineGap']}`: `{row['sourceLabel']}` -> `{row['targetLabel']}`"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("sameStepSignature:", same_step_signature)
    print("instructionHits:", result["instructionTermHits"])


if __name__ == "__main__":
    main()
