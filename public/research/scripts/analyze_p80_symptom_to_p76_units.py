#!/usr/bin/env python3
"""Test whether p80's five symptom labels map cleanly to page-76 units.

This is a bounded follow-up to the dose-number audit. Page 80 has exactly five
symptoms under "5 SYMPTOM RELIEF", while page 76 has five verified orange boxes
and five verified grey boxes. If the package text is a selector, the clean
human-solvable version would likely be a five-to-five mapping.

No key candidates are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
MANUAL_GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
OUT = ROOT / "analysis_outputs/source_audit/p80_symptom_to_p76_units"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p80_symptom_to_p76_units.json"
OUT_MD = OUT / "p80_symptom_to_p76_units.md"

SYMPTOM_TERMS = {
    "NAUSEA": ["nausea", "nauseous", "sick"],
    "HEARTBURN": ["heart", "burn"],
    "INDIGESTION": ["indigestion", "digest"],
    "UPSET STOMACH": ["upset", "stomach"],
    "SHITCOINS": ["shitcoin", "shitcoins", "shitcoiner"],
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def package_symptoms() -> list[dict]:
    text = json.loads(MANUAL_ORANGE.read_text())["visualOrangeBoxes"]["p80_orange_1"]
    parts = [part.strip() for part in text.split("/") if part.strip()]
    # First part is the heading "5 SYMPTOM RELIEF"; the five following parts
    # are the actual symptom list.
    symptoms = parts[1:]
    return [
        {
            "index": i,
            "symptom": symptom,
            "initial": symptom[0],
            "terms": SYMPTOM_TERMS.get(symptom, [normalize(symptom)]),
        }
        for i, symptom in enumerate(symptoms, 1)
    ]


def p76_orange_units() -> list[dict]:
    data = json.loads(MANUAL_ORANGE.read_text())["visualOrangeBoxes"]
    rows = []
    for key, text in data.items():
        if key.startswith("p76_orange_"):
            rows.append({"id": key, "index": int(key.rsplit("_", 1)[1]), "kind": "orange", "text": text})
    return sorted(rows, key=lambda row: row["index"])


def p76_grey_units() -> list[dict]:
    data = json.loads(MANUAL_GREY.read_text())
    rows = []
    for row in data["rows"]:
        if row["page"] == 76:
            rows.append(
                {
                    "id": row["id"],
                    "index": int(row["id"].rsplit("_", 1)[1]),
                    "kind": "grey",
                    "text": row["expected"],
                }
            )
    return sorted(rows, key=lambda row: row["index"])


def lexical_hits(symptom: dict, unit: dict) -> list[str]:
    text = normalize(unit["text"])
    hits = []
    for term in symptom["terms"]:
        if normalize(term) and normalize(term) in text:
            hits.append(term)
    return hits


def ordered_mapping(symptoms: list[dict], units: list[dict], order: str) -> dict:
    ordered_units = units if order == "forward" else list(reversed(units))
    pairs = []
    for symptom, unit in zip(symptoms, ordered_units):
        hits = lexical_hits(symptom, unit)
        pairs.append(
            {
                "symptomIndex": symptom["index"],
                "symptom": symptom["symptom"],
                "unitId": unit["id"],
                "unitKind": unit["kind"],
                "unitIndex": unit["index"],
                "unitText": unit["text"],
                "lexicalHits": hits,
            }
        )
    return {
        "surface": units[0]["kind"] if units else "empty",
        "order": order,
        "pairs": pairs,
        "lexicalHitCount": sum(1 for pair in pairs if pair["lexicalHits"]),
        "directHitPattern": "".join("1" if pair["lexicalHits"] else "0" for pair in pairs),
    }


def unordered_hits(symptoms: list[dict], units: list[dict]) -> list[dict]:
    rows = []
    for symptom in symptoms:
        for unit in units:
            hits = lexical_hits(symptom, unit)
            if hits:
                rows.append(
                    {
                        "symptomIndex": symptom["index"],
                        "symptom": symptom["symptom"],
                        "unitId": unit["id"],
                        "unitKind": unit["kind"],
                        "unitIndex": unit["index"],
                        "unitText": unit["text"],
                        "lexicalHits": hits,
                    }
                )
    return rows


def initials(rows: list[dict], key: str) -> str:
    return "".join((row[key].strip()[0] if row[key].strip() else "?") for row in rows)


def main() -> None:
    symptoms = package_symptoms()
    orange = p76_orange_units()
    grey = p76_grey_units()
    all_units = orange + grey
    mappings = [
        ordered_mapping(symptoms, orange, "forward"),
        ordered_mapping(symptoms, orange, "reverse"),
        ordered_mapping(symptoms, grey, "forward"),
        ordered_mapping(symptoms, grey, "reverse"),
    ]
    unordered = {
        "orange": unordered_hits(symptoms, orange),
        "grey": unordered_hits(symptoms, grey),
        "all": unordered_hits(symptoms, all_units),
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p80 five-symptom list mapped to five page-76 orange/grey units; no key derivation",
        "symptoms": symptoms,
        "symptomInitials": initials(symptoms, "symptom"),
        "page76Orange": orange,
        "page76Grey": grey,
        "orangeInitials": initials(orange, "text"),
        "greyInitials": initials(grey, "text"),
        "orderedMappings": mappings,
        "unorderedLexicalHits": unordered,
        "assessment": [
            "The only exact forward five-to-five orange hit is symptom 5 SHITCOINS -> p76 orange 5 shitcoiner at heart.",
            "HEARTBURN has an unordered lexical hit on p76 orange 1 because that phrase contains heart, but it is off-order if the five boxes are used literally.",
            "No forward or reverse five-to-five mapping gives a clean multi-hit instruction or ordered phrase.",
            "The package symptom list corroborates the O5/B5 lower-corridor anchor, but it does not define a complete selector.",
        ],
        "nextMove": "Keep SHITCOINS->shitcoiner as corroboration only. Search for an external/source instruction before applying symptom words as selectors.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# P80 Symptom List To Page-76 Units",
        "",
        "Scope: map p80's five symptom labels to the five verified page-76 orange boxes and five verified page-76 grey boxes. No key candidates are generated.",
        "",
        f"- Symptom initials: `{result['symptomInitials']}`",
        f"- Page-76 orange initials: `{result['orangeInitials']}`",
        f"- Page-76 grey initials: `{result['greyInitials']}`",
        "",
        "## Ordered Five-To-Five Checks",
        "",
    ]
    for mapping in mappings:
        lines.append(f"### {mapping['surface']} / {mapping['order']}")
        lines.append(f"- direct lexical hit pattern: `{mapping['directHitPattern']}`")
        lines.append(f"- direct lexical hit count: `{mapping['lexicalHitCount']}`")
        for pair in mapping["pairs"]:
            hit = ", ".join(pair["lexicalHits"]) if pair["lexicalHits"] else "-"
            lines.append(
                f"- {pair['symptomIndex']} `{pair['symptom']}` -> `{pair['unitId']}` `{pair['unitText']}` hits `{hit}`"
            )
        lines.append("")
    lines.extend(["## Unordered Lexical Hits", ""])
    for surface, rows in unordered.items():
        lines.append(f"### {surface}")
        if not rows:
            lines.append("- none")
        for row in rows:
            lines.append(
                f"- `{row['symptom']}` -> `{row['unitId']}` `{row['unitText']}` hits `{', '.join(row['lexicalHits'])}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Assessment",
            "",
            "- The cleanest ordered hit is only #5: `SHITCOINS` -> p76 orange #5 `shitcoiner at heart.`",
            "- `HEARTBURN` can see `heart` in p76 orange #1, but that is not in the five-to-five order. It is a weak semantic echo, not a selector.",
            "- The grey boxes do not produce a direct lexical symptom mapping; `Volcano Bonds` remains linked only through the already-known B5/O5 mirror anchor.",
            "- The symptom list supports the same lower-corridor hypothesis but does not tell us how to extract a key.",
            "",
            "## Next Best Move",
            "",
            "- Do not use symptom words as selectors by themselves. Look for an external/source instruction that says which p76 unit to read and how.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
