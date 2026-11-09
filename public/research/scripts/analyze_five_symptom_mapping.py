#!/usr/bin/env python3
"""Test whether p80's five symptoms order the five page-76 targets.

This is a scan-native selector check motivated by page 80:

    5 SYMPTOM RELIEF
    NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS

It tests only simple human-solvable mappings; no key derivation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "analysis_outputs/3d_article_map/five_symptom_mapping.md"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/five_symptom_mapping.json"


SYMPTOMS = [
    "NAUSEA",
    "HEARTBURN",
    "INDIGESTION",
    "UPSET STOMACH",
    "SHITCOINS",
]

GRAPH_TARGETS = [
    {"id": "G", "color": "orange", "text": "Get some toxicity. Get some bitcoin. Open your heart to Bitcoin."},
    {"id": "b1", "color": "orange", "text": "by the rancid catnip of fiat money."},
    {"id": "b2", "color": "orange", "text": "“buying the dip.”"},
    {"id": "I", "color": "grey", "text": "It’s a stun gun to the genitals."},
    {"id": "$", "color": "grey", "text": "$1 billion"},
]

ALL_P76_HIGHLIGHTS = [
    {"id": "orange_open_heart", "color": "orange", "text": "Get some toxicity. Get some bitcoin. Open your heart to Bitcoin."},
    {"id": "orange_rancid_money", "color": "orange", "text": "by the rancid catnip of fiat money."},
    {"id": "orange_buy_dip", "color": "orange", "text": "“buying the dip.”"},
    {"id": "orange_shitcoiner_heart", "color": "orange", "text": "shitcoiner at heart."},
    {"id": "grey_fiat_nonsense", "color": "grey", "text": "Gotta be this way. Forty years of dumb post-1971 fiat money nonsense"},
    {"id": "grey_stun_gun", "color": "grey", "text": "It’s a stun gun to the genitals."},
    {"id": "grey_1b", "color": "grey", "text": "$1 billion"},
    {"id": "grey_volcano", "color": "grey", "text": "“Volcano Bonds”"},
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9$]", text))


def initial(text: str) -> str:
    ws = words(text)
    return ws[0][0] if ws else ""


def last_initial(text: str) -> str:
    ws = words(text)
    return ws[-1][0] if ws else ""


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def symptom_terms(symptom: str) -> set[str]:
    terms = {w.lower() for w in words(symptom)}
    if "shitcoins" in terms:
        terms |= {"shitcoin", "shitcoiner", "shitcoiners"}
    if "heartburn" in terms:
        terms |= {"heart"}
    if "indigestion" in terms:
        terms |= {"digest", "digestion", "ghetto"}
    if "nausea" in terms:
        terms |= {"sick", "stun"}
    if "upset" in terms or "stomach" in terms:
        terms |= {"stomach", "genitals", "ghetto"}
    return terms


def direct_matches(symptoms: list[str], targets: list[dict]) -> list[dict]:
    rows = []
    for symptom in symptoms:
        terms = symptom_terms(symptom)
        for target in targets:
            target_norm = normalize(target["text"])
            hits = sorted(t for t in terms if normalize(t) and normalize(t) in target_norm)
            if hits:
                rows.append({"symptom": symptom, "target": target["id"], "targetText": target["text"], "hits": hits})
    return rows


def select_letter_by_length(symptom: str, target: str) -> dict:
    idx = len(letters(symptom))
    target_letters = letters(target)
    if not target_letters:
        char = ""
    else:
        char = target_letters[(idx - 1) % len(target_letters)]
    target_words = words(target)
    word = target_words[(idx - 1) % len(target_words)] if target_words else ""
    return {"symptomLength": idx, "charModulo": char, "wordModulo": word}


def main() -> None:
    ordered_rows = []
    for symptom, target in zip(SYMPTOMS, GRAPH_TARGETS):
        selected = select_letter_by_length(symptom, target["text"])
        ordered_rows.append(
            {
                "symptom": symptom,
                "targetId": target["id"],
                "targetText": target["text"],
                "targetInitial": initial(target["text"]),
                "targetLastInitial": last_initial(target["text"]),
                **selected,
            }
        )

    streams = {
        "symptom_initials": "".join(initial(s) for s in SYMPTOMS),
        "symptom_last_initials": "".join(last_initial(s) for s in SYMPTOMS),
        "symptom_lengths": ",".join(str(len(letters(s))) for s in SYMPTOMS),
        "graph_target_initials": "".join(r["targetInitial"] for r in ordered_rows),
        "graph_target_last_initials": "".join(r["targetLastInitial"] for r in ordered_rows),
        "length_selected_chars": "".join(r["charModulo"] for r in ordered_rows),
        "length_selected_words": " ".join(r["wordModulo"] for r in ordered_rows),
    }

    matches = direct_matches(SYMPTOMS, ALL_P76_HIGHLIGHTS)
    result = {
        "source": "best locked scan / page-80 package copy",
        "symptoms": SYMPTOMS,
        "graphTargets": GRAPH_TARGETS,
        "streams": streams,
        "orderedRows": ordered_rows,
        "directMatchesAcrossAllP76Highlights": matches,
        "assessment": [
            "The five-symptom count supports the five page-76 target-group model.",
            "The symptom order does not create readable initials, last initials, or length-indexed text over the five graph targets.",
            "Direct lexical/semantic matches mostly point HEARTBURN to heart phrases and SHITCOINS to 'shitcoiner at heart'; they do not order the graph targets cleanly.",
            "Treat p80 as count/theme support, not the final selector.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Five-Symptom Mapping",
        "",
        "Scope: test whether page 80's `5 SYMPTOM RELIEF` label orders/selects the five page-76 reflected-graph target groups. No private-key candidates are generated.",
        "",
        "## Streams",
        "",
    ]
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value}`")
    md.extend(["", "## Ordered Symptom -> Graph Target Rows", ""])
    for r in ordered_rows:
        md.append(
            f"- `{r['symptom']}` -> {r['targetId']} `{r['targetText']}` "
            f"initial=`{r['targetInitial']}` lastInitial=`{r['targetLastInitial']}` "
            f"len={r['symptomLength']} charModulo=`{r['charModulo']}` wordModulo=`{r['wordModulo']}`"
        )
    md.extend(["", "## Direct Matches Across All Page-76 Highlights", ""])
    if matches:
        for row in matches:
            md.append(f"- `{row['symptom']}` -> {row['target']} hits={row['hits']} text=`{row['targetText']}`")
    else:
        md.append("- none")
    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
