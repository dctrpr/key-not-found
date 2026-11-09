#!/usr/bin/env python3
"""Test page-80 `5 SYMPTOM RELIEF` as a literal removal selector.

The package copy is one of the few remaining OVERDOSE-specific visual layers:
it names five symptoms and includes the verb/noun "relief". This pass tests the
cleanest human-readable interpretation: map symptoms onto page-76 highlight
units, then "relieve" the symptom words from those targets.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
P80 = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
OUT = ROOT / "analysis_outputs/source_audit/p80_symptom_relief_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p80_symptom_relief_rule.json"
OUT_MD = OUT / "p80_symptom_relief_rule.md"

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
]

SYMPTOM_ROOTS = {
    "NAUSEA": ["nausea", "sick", "vomit"],
    "HEARTBURN": ["heart", "burn"],
    "INDIGESTION": ["indigestion", "indigest", "digest"],
    "UPSET STOMACH": ["upset", "stomach"],
    "SHITCOINS": ["shitcoins", "shitcoiners", "shitcoiner", "shitcoin"],
}

SEMANTIC_ROOTS = {
    # Kept separate from literal roots so the report can distinguish clean text
    # matches from broader theme matches.
    "UPSET STOMACH": ["genitals"],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%']+", text)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def p76_units() -> list[dict]:
    orange = load_json(ORANGE)["visualOrangeBoxes"]
    grey = load_json(GREY)["rows"]
    units = []
    # Combine the opening two-line orange highlight because visually it is one
    # phrase split by a line break.
    units.append(
        {
            "id": "O1_2",
            "kind": "orange",
            "index": 1,
            "text": normalize(f"{orange['p76_orange_1']} {orange['p76_orange_2']}"),
        }
    )
    for idx in [3, 4, 5]:
        units.append({"id": f"O{idx}", "kind": "orange", "index": idx, "text": orange[f"p76_orange_{idx}"]})
    for row in grey:
        if row["page"] == 76:
            idx = int(row["id"].rsplit("_", 1)[1])
            units.append({"id": f"B{idx}", "kind": "grey", "index": idx, "text": row["expected"]})
    return units


def p80_symptoms() -> list[str]:
    p80 = load_json(P80)
    row = next(item for item in p80["manualTranscription"] if item["label"] == "symptoms")
    # Preserve UPSET STOMACH as one symptom.
    text = row["text"]
    return ["NAUSEA", "HEARTBURN", "INDIGESTION", "UPSET STOMACH", "SHITCOINS"] if "UPSET STOMACH" in text else words(text)


def remove_roots(text: str, roots: list[str]) -> str:
    out = text
    for root in sorted(roots, key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(root)}\b", "", out, flags=re.IGNORECASE)
    return normalize(re.sub(r"\s+([.,;:!?])", r"\1", out))


def direct_matches(units: list[dict], symptoms: list[str]) -> list[dict]:
    rows = []
    for symptom in symptoms:
        literal_roots = SYMPTOM_ROOTS[symptom]
        semantic_roots = SEMANTIC_ROOTS.get(symptom, [])
        for unit in units:
            text = unit["text"]
            low = text.lower()
            literal_hits = [root for root in literal_roots if re.search(rf"\b{re.escape(root)}", low)]
            semantic_hits = [root for root in semantic_roots if re.search(rf"\b{re.escape(root)}", low)]
            if not literal_hits and not semantic_hits:
                continue
            relieved_literal = remove_roots(text, literal_hits)
            relieved_all = remove_roots(text, literal_hits + semantic_hits)
            rows.append(
                {
                    "symptom": symptom,
                    "unitId": unit["id"],
                    "unitKind": unit["kind"],
                    "unitText": text,
                    "literalHits": literal_hits,
                    "semanticHits": semantic_hits,
                    "relievedLiteral": relieved_literal,
                    "relievedAll": relieved_all,
                    "relievedLiteralInitials": "".join(word[0] for word in words(relieved_literal)),
                    "relievedAllInitials": "".join(word[0] for word in words(relieved_all)),
                    "instructionHits": instruction_hits(relieved_literal + " " + relieved_all),
                }
            )
    return rows


def ordered_assignment(symptoms: list[str], units: list[dict]) -> list[dict]:
    # Existing five-symptom mapping used these five graph targets. Keep it as a
    # control to see whether "relief" works when the printed symptom order is
    # forced onto the five target order.
    target_order = [
        next(unit for unit in units if unit["id"] == "O1_2"),
        next(unit for unit in units if unit["id"] == "O3"),
        next(unit for unit in units if unit["id"] == "O4"),
        next(unit for unit in units if unit["id"] == "B3"),
        next(unit for unit in units if unit["id"] == "B4"),
    ]
    rows = []
    for symptom, unit in zip(symptoms, target_order):
        literal_roots = SYMPTOM_ROOTS[symptom]
        relieved = remove_roots(unit["text"], literal_roots)
        rows.append(
            {
                "symptom": symptom,
                "unitId": unit["id"],
                "unitText": unit["text"],
                "literalRoots": literal_roots,
                "relieved": relieved,
                "changed": relieved != unit["text"],
                "relievedInitials": "".join(word[0] for word in words(relieved)),
            }
        )
    return rows


def package_term_audit() -> dict:
    p80 = load_json(P80)
    text = " ".join(row["text"] for row in p80["manualTranscription"])
    terms = {
        "possibleActionTerms": [term for term in ["relief", "reliever", "fixes", "proof", "work", "anti", "fake"] if re.search(rf"\b{term}", text, re.I)],
        "explicitExtractionTerms": instruction_hits(text),
        "numbers": p80.get("streams", {}).get("numbers_csv", ""),
    }
    return terms


def main() -> None:
    symptoms = p80_symptoms()
    units = p76_units()
    matches = direct_matches(units, symptoms)
    forced = ordered_assignment(symptoms, units)
    term_audit = package_term_audit()

    literal_stream = " | ".join(row["relievedLiteral"] for row in matches)
    all_stream = " | ".join(row["relievedAll"] for row in matches)
    forced_stream = " | ".join(row["relieved"] for row in forced)
    streams = {
        "directLiteralRelief": literal_stream,
        "directAllRelief": all_stream,
        "orderedForcedRelief": forced_stream,
        "directLiteralInitials": "".join(row["relievedLiteralInitials"] for row in matches),
        "directAllInitials": "".join(row["relievedAllInitials"] for row in matches),
        "orderedForcedInitials": "".join(row["relievedInitials"] for row in forced),
    }
    stream_hits = {name: instruction_hits(text) for name, text in streams.items() if instruction_hits(text)}

    changed_forced = [row for row in forced if row["changed"]]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-80 `5 SYMPTOM RELIEF` literal relief/removal test; no key derivation",
        "symptoms": symptoms,
        "packageTermAudit": term_audit,
        "p76UnitCount": len(units),
        "directMatches": matches,
        "orderedAssignment": forced,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": [
            "`5 SYMPTOM RELIEF` is real count/theme evidence, and `relief` is the cleanest action word on the package.",
            "Literal symptom removal has no complete five-of-five mapping into the ordered page-76 targets; in the forced printed order, none of the five target texts changes.",
            "Direct literal matches cluster on `heart` and `shitcoiner at heart`, but relieving HEARTBURN and SHITCOINS from O5 collapses to short leftovers like `shitcoiner at` / `at heart` / `at`, not an instruction.",
            f"Instruction hits in relief streams: {stream_hits or 'none'}.",
            "This keeps p80 as a five-count locator and theme validator, not the missing extraction-unit rule.",
        ],
        "decision": "do_not_promote_relief_to_selector",
        "nextMove": "Keep p80 package copy in the C6 locator evidence. Reopen only if source geometry places the bottle/package copy onto page 76 or an external clue explicitly says to relieve/remove symptoms.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P80 Symptom Relief Rule Audit",
        "",
        "Scope: test page-80 `5 SYMPTOM RELIEF` as a literal remove/relieve operation on page-76 highlight units. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Symptoms: `{', '.join(symptoms)}`",
        f"- Package action terms: `{', '.join(term_audit['possibleActionTerms']) or 'none'}`",
        f"- Explicit extraction terms on package: `{', '.join(term_audit['explicitExtractionTerms']) or 'none'}`",
        "",
        "## Direct Symptom Matches",
        "",
        "| symptom | unit | hits | relieved literal | relieved all | instruction hits |",
        "|---|---|---|---|---|---|",
    ]
    for row in matches:
        hits = ", ".join(row["literalHits"] + [f"semantic:{h}" for h in row["semanticHits"]]) or "-"
        inst = ", ".join(row["instructionHits"]) or "none"
        lines.append(
            f"| {row['symptom']} | `{row['unitId']}` `{row['unitText']}` | `{hits}` | `{row['relievedLiteral']}` | `{row['relievedAll']}` | `{inst}` |"
        )

    lines.extend(["", "## Forced Five-Order Relief", "", "| symptom | target unit | changed | relieved text | initials |", "|---|---|---:|---|---|"])
    for row in forced:
        lines.append(f"| {row['symptom']} | `{row['unitId']}` `{row['unitText']}` | `{row['changed']}` | `{row['relieved']}` | `{row['relievedInitials']}` |")

    lines.extend(["", "## Streams", ""])
    for name, text in streams.items():
        hits = ", ".join(instruction_hits(text)) or "none"
        lines.append(f"- `{name}` hits `{hits}`: `{text}`")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Decision: `{result['decision']}`.", "", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("direct matches:", len(matches))
    print("forced changed:", len(changed_forced))
    print("stream instruction hits:", stream_hits)


if __name__ == "__main__":
    main()
