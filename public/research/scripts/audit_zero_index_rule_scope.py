#!/usr/bin/env python3
"""Test the Canva `#0` / zero clue as a bounded index rule.

The existing source-fidelity audit established that the current trusted scan
reads the top hotspot as `100,000`, while one user/browser transcript had the
variant `1000,000`. This pass asks the smaller question: if `#0` or zero-counts
are meant as an instruction, do they select a repeatable page-76 unit/order?

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZERO = ROOT / "analysis_outputs/source_audit/zero_source_fidelity/zero_source_fidelity.json"
CORRIDOR = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
UNITS = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"
OUT = ROOT / "analysis_outputs/source_audit/zero_index_rule_scope"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "zero_index_rule_scope.json"
OUT_MD = OUT / "zero_index_rule_scope.md"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "word",
    "letter",
    "line",
    "edge",
    "font",
    "first",
    "last",
    "left",
    "right",
    "mirror",
    "reverse",
    "fold",
    "key",
    "zero",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%']+", text)


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def zero_rows() -> list[dict]:
    rows = load_json(ZERO)["canonicalPageRows"]
    out = []
    for row in rows:
        out.append(
            {
                "id": f"p{row['articlePage']}_l{row['lineIndex']}_{row['token'].replace(',', '')}",
                "articlePage": row["articlePage"],
                "lineIndex": row["lineIndex"],
                "token": row["token"],
                "digits": row["digits"],
                "zeroCount": row["zeroCount"],
                "context": row["context"],
                "source": "trusted_scan",
            }
        )

    # Keep the disputed transcript form in the table explicitly. The current
    # scan does not support it, but it is the only known `#0`-related variant.
    row_100k = next(row for row in rows if row["token"] == "100,000")
    out.append(
        {
            "id": "p77_l3_1000000_variant",
            "articlePage": row_100k["articlePage"],
            "lineIndex": row_100k["lineIndex"],
            "token": "1000,000",
            "digits": "1000000",
            "zeroCount": 6,
            "context": row_100k["context"],
            "source": "unsupported_variant_from_user_annotated_transcript",
        }
    )
    return out


def unit_groups() -> dict[str, list[dict]]:
    units = load_json(UNITS)["units"]
    by_line = sorted(units, key=lambda item: item["line"])
    orange = sorted([item for item in units if item["kind"] == "orange"], key=lambda item: item["index"])
    grey = sorted([item for item in units if item["kind"] == "grey"], key=lambda item: item["index"])
    return {"allByLine": by_line, "orange": orange, "grey": grey}


def corridor_rows() -> list[dict]:
    return load_json(CORRIDOR)["records"]


def nth(items: list[dict], index: int, zero_based: bool = False) -> dict | None:
    pos = index if zero_based else index - 1
    if 0 <= pos < len(items):
        return items[pos]
    return None


def unit_ref(unit: dict | None) -> dict | None:
    if unit is None:
        return None
    return {"id": unit["id"], "kind": unit["kind"], "index": unit["index"], "line": unit["line"], "label": unit["label"]}


def corridor_ref(row: dict | None) -> dict | None:
    if row is None:
        return None
    return {
        "corridorIndex": row["corridorIndex"],
        "lineIndex": row["lineIndex"],
        "text": row["text"],
        "initial": row["initial"],
        "lastInitial": row["lastInitial"],
    }


def build_rows(zrows: list[dict], groups: dict[str, list[dict]], corridor: list[dict]) -> list[dict]:
    rows = []
    for row in zrows:
        count = int(row["zeroCount"])
        digits_value = int(row["digits"])
        count_orange = nth(groups["orange"], count)
        count_grey = nth(groups["grey"], count)
        count_all = nth(groups["allByLine"], count)
        count_corridor = nth(corridor, count)
        modulo_zero_based = digits_value % len(corridor)
        modulo_corridor = nth(corridor, modulo_zero_based, zero_based=True)
        line_index_corridor = nth(corridor, int(row["lineIndex"]))
        selected_text = " ".join(
            item
            for item in [
                count_orange["label"] if count_orange else "",
                count_grey["label"] if count_grey else "",
                count_all["label"] if count_all else "",
                count_corridor["text"] if count_corridor else "",
                modulo_corridor["text"] if modulo_corridor else "",
                line_index_corridor["text"] if line_index_corridor else "",
            ]
            if item
        )
        rows.append(
            {
                **row,
                "zeroCountAsOrangeUnit": unit_ref(count_orange),
                "zeroCountAsGreyUnit": unit_ref(count_grey),
                "zeroCountAsAllUnitByLine": unit_ref(count_all),
                "zeroCountAsCorridorLine": corridor_ref(count_corridor),
                "digitsModuloCorridorZeroBasedIndex": modulo_zero_based,
                "digitsModuloCorridorLine": corridor_ref(modulo_corridor),
                "sourceLineIndexAsCorridorLine": corridor_ref(line_index_corridor),
                "selectsActiveO5": any(
                    item and item.get("id") == "O5"
                    for item in [unit_ref(count_orange), unit_ref(count_grey), unit_ref(count_all)]
                ),
                "selectsActiveG5": any(
                    item and item.get("id") == "B5"
                    for item in [unit_ref(count_orange), unit_ref(count_grey), unit_ref(count_all)]
                ),
                "instructionHits": instruction_hits(selected_text),
            }
        )
    return rows


def zero_based_controls(groups: dict[str, list[dict]], corridor: list[dict]) -> dict:
    selected = {
        "hash0AsOrangeZeroBased": unit_ref(nth(groups["orange"], 0, zero_based=True)),
        "hash0AsGreyZeroBased": unit_ref(nth(groups["grey"], 0, zero_based=True)),
        "hash0AsAllUnitZeroBased": unit_ref(nth(groups["allByLine"], 0, zero_based=True)),
        "hash0AsCorridorZeroBased": corridor_ref(nth(corridor, 0, zero_based=True)),
    }
    text = " ".join(
        item.get("label") or item.get("text")
        for item in selected.values()
        if item
    )
    return {**selected, "instructionHits": instruction_hits(text)}


def streams(rows: list[dict], controls: dict) -> dict:
    trusted = [row for row in rows if row["source"] == "trusted_scan"]
    def unit_ids(key: str) -> str:
        return " ".join(row[key]["id"] if row[key] else "-" for row in trusted)

    count_corridor = [row["zeroCountAsCorridorLine"] for row in trusted if row["zeroCountAsCorridorLine"]]
    modulo_corridor = [row["digitsModuloCorridorLine"] for row in trusted if row["digitsModuloCorridorLine"]]
    source_line_corridor = [row["sourceLineIndexAsCorridorLine"] for row in trusted if row["sourceLineIndexAsCorridorLine"]]

    return {
        "zeroCountOrangeUnitIds": unit_ids("zeroCountAsOrangeUnit"),
        "zeroCountGreyUnitIds": unit_ids("zeroCountAsGreyUnit"),
        "zeroCountAllUnitIds": unit_ids("zeroCountAsAllUnitByLine"),
        "zeroCountCorridorInitials": "".join(row["initial"] for row in count_corridor),
        "zeroCountCorridorLastInitials": "".join(row["lastInitial"] for row in count_corridor),
        "digitsModuloCorridorInitials": "".join(row["initial"] for row in modulo_corridor),
        "sourceLineIndexCorridorInitials": "".join(row["initial"] for row in source_line_corridor),
        "hash0SelectedIds": " ".join(
            item["id"] if "id" in item else f"corridor{item['corridorIndex']}"
            for item in [
                controls["hash0AsOrangeZeroBased"],
                controls["hash0AsGreyZeroBased"],
                controls["hash0AsAllUnitZeroBased"],
                controls["hash0AsCorridorZeroBased"],
            ]
            if item
        ),
    }


def main() -> None:
    zrows = zero_rows()
    groups = unit_groups()
    corridor = corridor_rows()
    rows = build_rows(zrows, groups, corridor)
    controls = zero_based_controls(groups, corridor)
    stream_map = streams(rows, controls)
    stream_hits = {name: instruction_hits(text) for name, text in stream_map.items() if instruction_hits(text)}
    trusted_100k = next(row for row in rows if row["token"] == "100,000")
    variant_1000k = next(row for row in rows if row["token"] == "1000,000")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Canva `#0` / zero-count rule scope; no key derivation",
        "zeroRows": rows,
        "zeroBasedControls": controls,
        "streams": stream_map,
        "streamInstructionHits": stream_hits,
        "trusted100000Effect": {
            "zeroCount": trusted_100k["zeroCount"],
            "orangeUnit": trusted_100k["zeroCountAsOrangeUnit"],
            "greyUnit": trusted_100k["zeroCountAsGreyUnit"],
            "selectsActiveO5": trusted_100k["selectsActiveO5"],
            "selectsActiveG5": trusted_100k["selectsActiveG5"],
        },
        "unsupported1000000VariantEffect": {
            "zeroCount": variant_1000k["zeroCount"],
            "orangeUnit": variant_1000k["zeroCountAsOrangeUnit"],
            "greyUnit": variant_1000k["zeroCountAsGreyUnit"],
            "selectsActiveO5": variant_1000k["selectsActiveO5"],
            "selectsActiveG5": variant_1000k["selectsActiveG5"],
        },
        "assessment": [
            "`#0` as a literal zero-based selector chooses the first page-76 units/corridor line, not the active O5/G5 lower-corridor target.",
            "Trusted-scan `100,000` has five zeros, so a zero-count-as-highlight-index rule redundantly lands on O5/B5; this supports the existing five/O5 locator but does not name a unit, order, or extraction operation.",
            "The unsupported `1000,000` variant would have six zeros and no fifth page-76 orange/grey unit target, so it weakens rather than clarifies the selector under current materials.",
            "The all-zero streams do not produce instruction terms such as read/take/word/letter/line/first/last.",
        ],
        "decision": "keep_zero_hash0_as_source_fidelity_and_five_locator_evidence_only",
        "nextMove": "If the exact Canva/browser/original source that showed a missed `#0` appears, compare it to the existing zero crop sheet first; do not promote zero-count indexing under the current trusted scan.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Zero / #0 Index Rule Scope",
        "",
        "Scope: test the Canva `#0` / zero clue as a zero-based or zero-count selector. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Trusted scan top hotspot: `100,000` with `{trusted_100k['zeroCount']}` zeros.",
        f"- Unsupported transcript variant: `1000,000` with `{variant_1000k['zeroCount']}` zeros.",
        f"- Stream instruction hits: `{stream_hits or {}}`",
        "",
        "## #0 Controls",
        "",
        "| interpretation | selected |",
        "|---|---|",
        f"| orange zero-based | `{controls['hash0AsOrangeZeroBased']['id']}` `{controls['hash0AsOrangeZeroBased']['label']}` |",
        f"| grey zero-based | `{controls['hash0AsGreyZeroBased']['id']}` `{controls['hash0AsGreyZeroBased']['label']}` |",
        f"| all-units zero-based | `{controls['hash0AsAllUnitZeroBased']['id']}` `{controls['hash0AsAllUnitZeroBased']['label']}` |",
        f"| corridor zero-based | corridor `{controls['hash0AsCorridorZeroBased']['corridorIndex']}` `{controls['hash0AsCorridorZeroBased']['text']}` |",
        "",
        "## Zero-Count Rows",
        "",
        "| source | page | token | zeros | orange | grey | corridor-by-count | modulo-corridor | active O5/G5? | instruction hits |",
        "|---|---:|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        orange = row["zeroCountAsOrangeUnit"]["id"] if row["zeroCountAsOrangeUnit"] else "-"
        grey = row["zeroCountAsGreyUnit"]["id"] if row["zeroCountAsGreyUnit"] else "-"
        count_corridor = (
            f"{row['zeroCountAsCorridorLine']['corridorIndex']}:{row['zeroCountAsCorridorLine']['initial']}"
            if row["zeroCountAsCorridorLine"]
            else "-"
        )
        mod_corridor = (
            f"{row['digitsModuloCorridorLine']['corridorIndex']}:{row['digitsModuloCorridorLine']['initial']}"
            if row["digitsModuloCorridorLine"]
            else "-"
        )
        active = []
        if row["selectsActiveO5"]:
            active.append("O5")
        if row["selectsActiveG5"]:
            active.append("G5")
        lines.append(
            f"| `{row['source']}` | `{row['articlePage']}` | `{row['token']}` | `{row['zeroCount']}` | `{orange}` | `{grey}` | `{count_corridor}` | `{mod_corridor}` | `{','.join(active) or '-'}` | `{row['instructionHits'] or []}` |"
        )

    lines.extend(["", "## Streams", ""])
    for name, text in stream_map.items():
        lines.append(f"- `{name}`: `{text}`")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Decision: `{result['decision']}`.", "", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("trusted_100000_selects:", trusted_100k["selectsActiveO5"], trusted_100k["selectsActiveG5"])
    print("unsupported_1000000_selects:", variant_1000k["selectsActiveO5"], variant_1000k["selectsActiveG5"])
    print("stream_instruction_hits:", stream_hits)


if __name__ == "__main__":
    main()
