#!/usr/bin/env python3
"""Test whether page-80 package/pill copy chooses among the four page-76 anchors.

This is a bounded selector audit. It uses only manual p80 package transcription
and the four active page-76 anchors. It does not derive keys, hashes, seed
phrases, WIFs, or addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P80 = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
ANCHORS = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
OBBO = ROOT / "analysis_outputs/comparison_articles/obbo_anchor_signature/obbo_anchor_signature.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/p80_four_anchor_choice"
OUT_JSON = OUT_DIR / "p80_four_anchor_choice.json"
OUT_MD = OUT_DIR / "p80_four_anchor_choice.md"


def tokens(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9]+", text.lower())
    normalized = []
    for token in raw:
        if token.endswith("s") and len(token) > 3:
            token = token[:-1]
        if token.endswith("er") and len(token) > 5:
            normalized.append(token[:-2])
        normalized.append(token)
    return normalized


def p80_terms(transcription: list[dict[str, Any]]) -> list[dict[str, Any]]:
    terms = []
    for item in transcription:
        label = item["label"]
        text = item["text"]
        term_tokens = tokens(text)
        terms.append({"label": label, "text": text, "tokens": term_tokens, "numbers": item.get("numbers", [])})
        if label == "symptoms":
            for symptom in text.split():
                terms.append({"label": f"symptom:{symptom}", "text": symptom, "tokens": tokens(symptom), "numbers": []})
    return terms


def score_match(term: dict[str, Any], anchor: dict[str, Any]) -> dict[str, Any]:
    anchor_label = anchor["label"]
    anchor_text = f"{anchor_label} {anchor['canonicalLine']}"
    term_set = set(term["tokens"])
    label_set = set(tokens(anchor_label))
    anchor_set = set(tokens(anchor_text))
    label_overlap = sorted(term_set & label_set)
    context_overlap = sorted((term_set & anchor_set) - set(label_overlap))
    substring_hits = []
    for term_token in term_set:
        if len(term_token) < 4:
            continue
        for anchor_token in label_set:
            if len(anchor_token) < 4:
                continue
            if term_token in anchor_token or anchor_token in term_token:
                if term_token != anchor_token:
                    substring_hits.append(f"{term_token}<->{anchor_token}")
    substring_hits = sorted(set(substring_hits))
    score = len(label_overlap) * 4 + len(substring_hits) * 2 + len(context_overlap)
    return {
        "anchorId": anchor["id"],
        "anchor": anchor["label"],
        "score": score,
        "labelOverlap": label_overlap,
        "contextOverlap": context_overlap,
        "substringHits": substring_hits,
    }


def modulo_choices(numbers: list[int], anchor_ids: list[str]) -> list[dict[str, Any]]:
    choices = []
    n = len(anchor_ids)
    for value in numbers:
        choices.append(
            {
                "number": value,
                "oneBasedModuloAnchor": anchor_ids[(value - 1) % n],
                "zeroBasedModuloAnchor": anchor_ids[value % n],
            }
        )
    return choices


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p80 = json.loads(P80.read_text(encoding="utf-8"))
    anchors_data = json.loads(ANCHORS.read_text(encoding="utf-8"))
    obbo = json.loads(OBBO.read_text(encoding="utf-8"))
    anchors = anchors_data["anchors"]
    anchor_ids = [anchor["id"] for anchor in anchors]
    terms = p80_terms(p80["manualTranscription"])

    term_results = []
    for term in terms:
        matches = [score_match(term, anchor) for anchor in anchors]
        matches.sort(key=lambda item: (-item["score"], item["anchorId"]))
        if matches[0]["score"]:
            term_results.append({**term, "bestMatches": matches[:4]})

    symptom_hits = [item for item in term_results if item["label"].startswith("symptom:")]
    package_hits = [item for item in term_results if not item["label"].startswith("symptom:")]
    all_numbers: list[int] = []
    for term in terms:
        all_numbers.extend(term.get("numbers", []))
    all_numbers = list(dict.fromkeys(all_numbers))

    modulo = modulo_choices(all_numbers, anchor_ids)
    hit_by_anchor = {anchor["id"]: [] for anchor in anchors}
    for item in term_results:
        for match in item["bestMatches"]:
            if match["score"] == item["bestMatches"][0]["score"] and match["score"] > 0:
                hit_by_anchor[match["anchorId"]].append(item["label"])

    assessment = [
        "The p80 copy does not choose all four page-76 anchors.",
        "Lexical signal collapses onto O5/shitcoiner at heart: SHITCOINS matches shitcoiner, and HEARTBURN weakly matches heart.",
        "The black-anchor hits are context-only or absent: Bitcoin FixesThis touches the $1 billion line because the line contains bitcoin, while no p80 term names amount/billion/Volcano/Bonds.",
        "The repeated number 5 conflicts with a four-anchor selector unless an extra rule supplies a fifth unit; modulo-4 number choices are arbitrary and repeat only anchors 1/4.",
        "P80 therefore remains thematic/count corroboration, not the missing chooser for OBBO.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded test of whether p80 package/pill copy chooses among the four active page-76 anchors; no key derivation",
        "sources": {
            "p80PackageCopy": str(P80.relative_to(ROOT)),
            "anchorAdjacency": str(ANCHORS.relative_to(ROOT)),
            "obboSignature": str(OBBO.relative_to(ROOT)),
        },
        "anchorOrder": anchor_ids,
        "obboSummary": obbo.get("summary"),
        "termMatches": term_results,
        "symptomHits": symptom_hits,
        "hitByAnchor": hit_by_anchor,
        "numbers": all_numbers,
        "moduloFourChoices": modulo,
        "assessment": assessment,
        "decision": "Do not use p80 package copy as a four-anchor chooser without a new alignment/source clue.",
        "nextMove": "Return to geometry: inspect whether p80 bottle/package regions physically align to page 76 anchors under the existing fold/mirror models; if not, keep p80 closed.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P80 Four-Anchor Choice Audit",
        "",
        "Scope: bounded test of whether p80 package/pill copy chooses among the four active page-76 anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- P80 source: `{result['sources']['p80PackageCopy']}`",
        f"- Anchor source: `{result['sources']['anchorAdjacency']}`",
        "",
        "## Anchor Order",
        "",
        "| index | anchor | color |",
        "|---:|---|---|",
    ]
    for idx, anchor in enumerate(anchors, 1):
        lines.append(f"| `{idx}` | `{anchor['label']}` | `{anchor['color']}` |")
    lines.extend(["", "## Direct P80 Matches", "", "| p80 term | best anchor(s) | evidence |", "|---|---|---|"])
    for item in term_results:
        best_score = item["bestMatches"][0]["score"]
        best = [match for match in item["bestMatches"] if match["score"] == best_score]
        evidence = "; ".join(
            f"{match['anchor']}: label={match['labelOverlap']} context={match['contextOverlap']} substr={match['substringHits']}" for match in best
        )
        lines.append(f"| `{item['label']}`: `{item['text']}` | `{', '.join(match['anchor'] for match in best)}` | {evidence} |")
    lines.extend(["", "## Number Check", "", f"- Numbers seen on p80: `{all_numbers}`"])
    lines.append("- Four-anchor modulo choices are registered in JSON only; they are treated as arbitrary because no p80/source text asks for modulo.")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
