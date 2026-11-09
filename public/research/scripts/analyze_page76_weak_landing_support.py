#!/usr/bin/env python3
"""Audit secondary support for weak page-76 line-offset landings.

The earlier line-offset score treated O2+2 and B2+2 as unsupported because
they did not land on highlighted boxes or p78 graphic-band terms. This checks
whether those lines are nevertheless supported by other already-logged layers:
the reflected-highlight graph and page-80 package number/term evidence.

No key candidates, hashes, seed phrases, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDING_JSON = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
GRAPH_JSON = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json"
PACKAGE_JSON = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
P80_VOLUME_JSON = ROOT / "analysis_outputs/source_audit/p80_volume_number_impact/p80_volume_number_impact.json"

OUT = ROOT / "analysis_outputs/source_audit/page76_weak_landing_support"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_weak_landing_support.json"
OUT_MD = OUT / "page76_weak_landing_support.md"


STOP = {
    "the",
    "and",
    "but",
    "its",
    "it's",
    "with",
    "that",
    "this",
    "have",
    "from",
    "into",
    "your",
    "they",
    "their",
    "there",
    "were",
    "been",
    "being",
    "will",
    "would",
    "could",
    "should",
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def signal_tokens(text: str) -> set[str]:
    return {tok for tok in tokens(text) if len(tok) >= 4 and tok not in STOP}


def family_match(a: str, b: str) -> bool:
    if a == b:
        return True
    families = ("shitcoin", "bitcoin", "nocoin", "heart", "proof", "work", "dulled")
    return any(a.startswith(root) and b.startswith(root) for root in families)


def family_hits(left: set[str], right: set[str]) -> list[dict]:
    hits = []
    for a in sorted(left):
        for b in sorted(right):
            if family_match(a, b):
                hits.append({"landingToken": a, "sourceToken": b})
    return hits


def graph_support(line_text: str) -> list[dict]:
    data = json.loads(GRAPH_JSON.read_text())
    line_terms = signal_tokens(line_text)
    out = []
    for edge in data["edges"]:
        if edge.get("targetPage") != 76:
            continue
        reflection_terms = signal_tokens(edge.get("reflectionText", ""))
        hits = sorted(line_terms & reflection_terms)
        if not hits:
            continue
        out.append(
            {
                "targetId": edge["targetId"],
                "targetText": edge["targetText"],
                "sourcePage": edge["sourcePage"],
                "reflectionId": edge["reflectionId"],
                "reflectionText": edge["reflectionText"],
                "strength": edge["strength"],
                "overlapVsSpan": edge["overlapVsSpan"],
                "overlapVsReflection": edge["overlapVsReflection"],
                "centerDistance": edge["centerDistance"],
                "matchedTerms": hits,
            }
        )
    return out


def package_term_support(line_text: str) -> list[dict]:
    package = json.loads(PACKAGE_JSON.read_text())
    line_terms = signal_tokens(line_text)
    out = []
    for row in package["manualTranscription"]:
        source_terms = signal_tokens(row["text"])
        exact = sorted(line_terms & source_terms)
        family = family_hits(line_terms, source_terms)
        if exact or family:
            out.append(
                {
                    "packageLabel": row["label"],
                    "packageText": row["text"],
                    "exactTerms": exact,
                    "familyTerms": family,
                }
            )
    return out


def package_number_support(line_text: str) -> list[dict]:
    data = json.loads(P80_VOLUME_JSON.read_text())
    line_terms = signal_tokens(line_text)
    out = []
    for row in data["numberChecks"]:
        hits = {}
        word = str(row.get("page76WordOneBased", ""))
        if word and word.lower() in line_terms:
            hits["oneBasedWord"] = word
        zero_line = row.get("page76LineZeroBased", "")
        one_line = row.get("page76LineOneBased", "")
        if signal_tokens(zero_line) & line_terms:
            hits["zeroBasedLine"] = zero_line
        if signal_tokens(one_line) & line_terms:
            hits["oneBasedLine"] = one_line
        if hits:
            out.append(
                {
                    "numberLabel": row["label"],
                    "number": row["number"],
                    "hits": hits,
                }
            )
    return out


def support_score(row: dict) -> tuple[int, list[str]]:
    score = 0
    labels = []
    graph = row["graphSupport"]
    strong = [item for item in graph if item["strength"] == "strong"]
    medium = [item for item in graph if item["strength"] == "medium"]
    if strong:
        score += 3
        labels.append("strong reflected carrier")
    if medium:
        score += 2
        labels.append("medium reflected carrier")
    if row["packageNumberSupport"]:
        score += 2
        labels.append("p80 number/word hit")
    if row["packageTermSupport"]:
        score += 1
        labels.append("p80 package term/family hit")
    return score, labels


def main() -> None:
    landing = json.loads(LANDING_JSON.read_text())
    weak = [
        row
        for row in landing["unsupportedMisses"]
        if row["targetText"].strip()
    ]

    audited = []
    for row in weak:
        item = {
            "sourceId": row["sourceId"],
            "sourceIndex": row["sourceIndex"],
            "targetLine": row["targetLine"],
            "targetText": row["targetText"],
            "graphSupport": graph_support(row["targetText"]),
            "packageTermSupport": package_term_support(row["targetText"]),
            "packageNumberSupport": package_number_support(row["targetText"]),
        }
        score, labels = support_score(item)
        item["secondarySupportScore"] = score
        item["secondarySupportLabels"] = labels
        audited.append(item)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Secondary-support audit for non-empty weak page-76 line-offset landings; no key derivation.",
        "auditedLandings": audited,
        "assessment": [
            "O2+2 is not actually unsupported in the full evidence stack: the `George Clinton / Martin Luther` line is the same p79 reflected carrier that strongly overlaps O1 and medium-overlaps B3 in the reflected-highlight graph.",
            "B2+2 gains weak p80 support: `100% Proof of Work Liquid` maps through the existing p80 number check to page-76 word 100, `dulled`, and the p80 symptom `SHITCOINS` shares the same family as `shitcoiners` in the landing line.",
            "This does not make #2 a final selector. It means the earlier score-0 label was too strict because it ignored reflected-carrier and package-number evidence.",
            "The line-offset model now looks more like a cross-reference/locator map than a direct highlight-to-highlight rule. It still does not specify the word or letter to extract.",
        ],
        "nextMove": "Run one local unit audit on the secondary-supported landing set: for each supported landing, use only the externally named term/carrier word and test whether those named terms form a readable instruction before any key derivation.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page-76 Weak Landing Support Audit",
        "",
        "Scope: re-check the non-empty line-offset landings that previously scored `0`, using only already-logged secondary layers: reflected-highlight graph and p80 package number/term evidence. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Results",
        "",
        "| landing | line | secondary score | secondary layers | line text |",
        "|---|---:|---:|---|---|",
    ]
    for row in audited:
        labels = ", ".join(row["secondarySupportLabels"]) or "-"
        text = row["targetText"].replace("|", "\\|")
        md.append(f"| `{row['sourceId']}+{row['sourceIndex']}` | {row['targetLine']} | {row['secondarySupportScore']} | {labels} | {text} |")

    md.extend(["", "## Details", ""])
    for row in audited:
        md.append(f"### {row['sourceId']}+{row['sourceIndex']} -> line {row['targetLine']}")
        md.append("")
        md.append(f"- Text: `{row['targetText']}`")
        if row["graphSupport"]:
            for edge in row["graphSupport"]:
                md.append(
                    f"- Reflected graph: `{edge['reflectionId']}` {edge['strength']} -> `{edge['targetId']}` "
                    f"terms=`{','.join(edge['matchedTerms'])}` reflectedCoverage=`{edge['overlapVsReflection']}`"
                )
        if row["packageNumberSupport"]:
            for hit in row["packageNumberSupport"]:
                md.append(f"- P80 number: `{hit['numberLabel']}` `{hit['number']}` hits `{hit['hits']}`")
        if row["packageTermSupport"]:
            for hit in row["packageTermSupport"]:
                family = ",".join(f"{x['landingToken']}~{x['sourceToken']}" for x in hit["familyTerms"])
                exact = ",".join(hit["exactTerms"])
                md.append(f"- P80 term: `{hit['packageLabel']}` `{hit['packageText']}` exact=`{exact}` family=`{family}`")
        if not row["secondarySupportLabels"]:
            md.append("- No secondary support found.")
        md.append("")

    md.extend(["## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    md.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
