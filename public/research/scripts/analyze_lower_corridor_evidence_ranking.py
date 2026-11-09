#!/usr/bin/env python3
"""Rank exact lower-corridor units after the bridge-normalized chain.

The goal is not to produce key material. It compares the narrowed O4/B4/B5
area against the independent evidence layers we have already logged, so future
passes do not treat every lower-corridor word as equally plausible.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
BRIDGE_CHAIN_JSON = ROOT / "analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain.json"
P78_WORDS_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json"
P78_BAND_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_band_specificity/p78_graphic_band_specificity.json"
TARGET_CONVERGENCE_JSON = ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json"
P80_SYMPTOM_JSON = ROOT / "analysis_outputs/source_audit/p80_symptom_to_p76_units/p80_symptom_to_p76_units.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"

OUT = ROOT / "analysis_outputs/source_audit/lower_corridor_evidence_ranking"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "lower_corridor_evidence_ranking.json"
OUT_MD = OUT / "lower_corridor_evidence_ranking.md"
OUT_OVERLAY = OUT / "lower_corridor_evidence_ranking_overlay.jpg"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def token_set(text: str) -> set[str]:
    return {norm(t) for t in re.findall(r"[A-Za-z0-9']+", text) if norm(t)}


def union_box(words: list[dict]) -> list[float] | None:
    if not words:
        return None
    return [
        min(w["box"][0] for w in words),
        min(w["box"][1] for w in words),
        max(w["box"][2] for w in words),
        max(w["box"][3] for w in words),
    ]


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def words_by_index(page: dict) -> dict[int, dict]:
    return {w["index"]: w for w in page["words"]}


def words_by_token(page: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for word in page["words"]:
        tok = norm(word.get("token") or word.get("text") or "")
        if tok:
            out[tok].append(word)
    return out


def box_for_indices(indexes: list[int], by_index: dict[int, dict]) -> list[float] | None:
    return union_box([by_index[i] for i in indexes if i in by_index])


def p78_word_hit_maps() -> tuple[dict[str, list[dict]], dict[str, list[dict]], dict[str, list[dict]]]:
    data = json.loads(P78_WORDS_JSON.read_text())
    bbox = defaultdict(list)
    dark = defaultdict(list)
    hole = defaultdict(list)
    for word in data.get("bboxWords", []):
        bbox[norm(word["token"] or word["text"])].append(word)
    for word in data.get("darkHits", []):
        dark[norm(word["token"] or word["text"])].append(word)
    for word in data.get("holeHits", []):
        hole[norm(word["token"] or word["text"])].append(word)
    return bbox, dark, hole


def target_convergence_scores() -> dict[str, dict]:
    data = json.loads(TARGET_CONVERGENCE_JSON.read_text())
    out = {}
    for row in data.get("ranking", []):
        out[row["target"]] = row
    return out


def chain_roles() -> dict[str, dict]:
    data = json.loads(BRIDGE_CHAIN_JSON.read_text())
    out = {}
    for rec in data.get("strictChainRecords", []):
        out[rec["sourceId"]] = rec
    return out


def symptom_support_labels() -> dict[str, list[str]]:
    data = json.loads(P80_SYMPTOM_JSON.read_text())
    out = defaultdict(list)
    for hit in data.get("unorderedLexicalHits", {}).get("all", []):
        label = hit.get("unitLabel", "") or hit.get("targetText", "") or hit.get("page76Text", "")
        symptom = hit.get("symptom", "")
        if "heart" in label.lower() or "shitcoin" in label.lower():
            out["O5"].append(symptom)
    return out


def lower_mark_hits() -> dict[str, list[str]]:
    data = json.loads(LOWER_MARKS_JSON.read_text())
    out = defaultdict(list)
    for analysis in data.get("analyses", []):
        if analysis.get("classification") == "text/highlight-false-positive":
            note = analysis.get("note", "")
            if "$1 billion" in note:
                out["B4"].append("detected as grey highlighted text")
            if "Volcano Bonds" in note:
                out["G5"].append("detected as grey highlighted text")
        for word in analysis.get("rayHits", {}).get("leftAxisWords", []):
            tok = norm(word.get("token") or word.get("text") or "")
            if tok in {"trust", "that", "guy"}:
                out["trust_that_guy"].append(f"mark {analysis['index']} ray")
            if tok == "siukbeodmensertslveaarty":
                out["O5"].append(f"mark {analysis['index']} ray OCR blob")
    return out


def main() -> None:
    page = load_page76()
    by_index = words_by_index(page)
    bbox_hits, dark_hits, hole_hits = p78_word_hit_maps()
    convergence = target_convergence_scores()
    chain = chain_roles()
    symptom = symptom_support_labels()
    mark_hits = lower_mark_hits()
    highlights = {h["id"]: h["box"] for h in page["highlights"]}

    candidates = [
        {
            "id": "O4",
            "label": "buying the dip",
            "role": "bridge target / orange highlight",
            "sourceId": "B3",
            "targetId": "O4",
            "tokens": {"buying", "dip"},
            "box": highlights["p76_orange_4"],
        },
        {
            "id": "B4_source",
            "label": "$1 billion / should sell",
            "role": "B4 source line",
            "sourceId": "B4",
            "targetId": "B4",
            "tokens": {"billion", "should", "sell"},
            "box": box_for_indices([201, 202, 203, 204, 205, 206, 207, 208], by_index),
        },
        {
            "id": "O4_target",
            "label": "future bitcoin earnings",
            "role": "O4 +4 landing",
            "sourceId": "O4",
            "tokens": {"future", "bitcoin", "earnings"},
            "box": box_for_indices([212, 213, 214], by_index),
        },
        {
            "id": "IMF_band",
            "label": "pay off the IMF",
            "role": "p78 dark/negative band, not chain target",
            "tokens": {"pay", "off", "the", "imf"},
            "box": box_for_indices([217, 218, 219, 220], by_index),
        },
        {
            "id": "MIKE_band",
            "label": "I tagged Mike",
            "role": "p78 dark/negative band, not chain target",
            "tokens": {"tagged", "mike"},
            "box": box_for_indices([228, 229, 230], by_index),
        },
        {
            "id": "B4_target",
            "label": "could sell",
            "role": "B4 +4 landing",
            "sourceId": "B4",
            "tokens": {"could", "sell", "sella"},
            "box": box_for_indices([237, 238], by_index),
        },
        {
            "id": "trust_that_guy",
            "label": "trust that guy",
            "role": "lower mark / p78 band, not chain target",
            "tokens": {"trust", "that", "guy"},
            "box": box_for_indices([257, 258, 259], by_index),
        },
        {
            "id": "G5",
            "label": "Volcano Bonds",
            "role": "B5 source / grey highlight",
            "sourceId": "B5",
            "targetId": "G5",
            "tokens": {"volcano", "bonds"},
            "box": [795, 2544, 1196, 2592],
        },
        {
            "id": "O5",
            "label": "shitcoiner at heart",
            "role": "B5 +5 target / orange highlight",
            "sourceId": "B5",
            "targetId": "O5",
            "tokens": {"shitcoiner", "heart"},
            "box": highlights["p76_orange_5"],
        },
    ]

    ranked = []
    for candidate in candidates:
        score = 0
        evidence = []
        layers = set()
        candidate_tokens = set(candidate["tokens"])

        source_id = candidate.get("sourceId")
        if source_id and source_id in chain:
            rec = chain[source_id]
            if candidate["label"].split()[0].lower() in rec["preferredTerm"] or any(tok in rec["preferredTerm"] for tok in candidate_tokens):
                score += 3
                layers.add("bridge-normalized chain")
                evidence.append(f"chain preferred term for {source_id}: {rec['preferredTerm']}")
            elif candidate["id"] in {"B4_source", "G5"}:
                score += 1
                layers.add("bridge-normalized chain")
                evidence.append(f"{candidate['id']} is a source unit in the strict chain")

        if candidate["id"] in {"O4", "B4_source", "G5", "O5"}:
            score += 2
            layers.add("page-76 highlight/source unit")
            evidence.append("page-76 highlighted/source unit")

        for tok in candidate_tokens:
            if tok in bbox_hits:
                score += 1
                layers.add("p78 bbox")
                evidence.append(f"p78 reflected bbox includes `{tok}`")
                break
        dark_tok_hits = []
        for tok in candidate_tokens:
            dark_tok_hits.extend(dark_hits.get(tok, []))
        if dark_tok_hits:
            score += 2
            layers.add("p78 dark mask")
            names = sorted({w["text"] for w in dark_tok_hits})
            evidence.append(f"p78 dark-mask hit(s): {', '.join(names)}")
            if any(w.get("darkCenter") for w in dark_tok_hits):
                score += 1
                evidence.append("p78 dark-mask center hit")
        hole_tok_hits = []
        for tok in candidate_tokens:
            hole_tok_hits.extend(hole_hits.get(tok, []))
        if hole_tok_hits:
            score += 2
            layers.add("p78 negative holes")
            names = sorted({w["text"] for w in hole_tok_hits})
            evidence.append(f"p78 negative-hole hit(s): {', '.join(names)}")
            if any(w.get("holeCenter") for w in hole_tok_hits):
                score += 1
                evidence.append("p78 negative-hole center hit")

        target_id = candidate.get("targetId")
        if target_id in convergence:
            row = convergence[target_id]
            bonus = 5 if target_id == "O5" else 4 if target_id == "G5" else 0
            if bonus:
                score += bonus
                layers.add("target convergence")
                evidence.append(f"target convergence score {row['score']} over {row['independentLayerCount']} layers")

        if candidate["id"] in symptom:
            score += 2
            layers.add("p80 symptoms")
            evidence.append(f"p80 symptom echo: {', '.join(symptom[candidate['id']])}")

        if candidate["id"] in mark_hits:
            score += 1
            layers.add("lower page marks")
            evidence.append(f"lower mark support: {', '.join(sorted(set(mark_hits[candidate['id']]))) }")

        if candidate["id"] == "G5":
            score += 2
            layers.add("OVERDOSE number 5")
            evidence.append("OVERDOSE `5` selects grey #5 Volcano Bonds")
        if candidate["id"] == "O5":
            score += 2
            layers.add("OVERDOSE number 5")
            evidence.append("OVERDOSE `5` selects orange #5 shitcoiner at heart")

        ranked.append(
            {
                **candidate,
                "tokens": sorted(candidate["tokens"]),
                "score": score,
                "independentLayerCount": len(layers),
                "layers": sorted(layers),
                "evidence": evidence,
            }
        )

    ranked.sort(key=lambda r: (-r["score"], -r["independentLayerCount"], r["id"]))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Compare exact lower-corridor units under the bridge-normalized chain; no key derivation.",
        "rankedCandidates": ranked,
        "streams": {
            "rankedLabels": " | ".join(r["label"] for r in ranked),
            "rankedInitials": "".join(norm(r["label"])[:1] for r in ranked if norm(r["label"])),
            "strictChainLowerLabels": "buying the dip | future bitcoin earnings | could sell | Volcano Bonds | shitcoiner at heart",
            "strictChainLowerInitials": "bfccs",
        },
        "assessment": [
            "The lower corridor has two competing evidence families, not one decisive selector.",
            "Convergence/OVERDOSE/self-mirror evidence favors the #5 pair: O5 `shitcoiner at heart` and G5 `Volcano Bonds`.",
            "The p78 reflected graphic favors the #4 band around `earnings`, `pay off the IMF`, `I tagged Mike`, and `could sell`; it is broad and not a precise word selector.",
            "The bridge-normalized chain makes O4/B4/B5 the right area, but does not choose between the convergence pair and the p78 graphic band.",
            "Do not promote `earnings/sell/heart` or any ranked-label stream to key material without a new source rule.",
        ],
        "nextMove": "Look for a source rule that reconciles the two evidence families: either p78 graphic edges must point into G5/O5, or the #5 convergence pair must explain how to order/select the #4 words.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    palette = [
        (255, 128, 0, 220),
        (30, 90, 230, 220),
        (50, 160, 90, 220),
        (160, 60, 180, 220),
        (0, 0, 0, 220),
        (180, 100, 30, 220),
    ]
    for i, cand in enumerate(ranked):
        box = cand.get("box")
        if not box:
            continue
        color = palette[i % len(palette)]
        pad = 8
        rect = [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad]
        draw.rectangle(rect, outline=color, width=5, fill=(color[0], color[1], color[2], 30))
        label = f"{i + 1}. {cand['label']} ({cand['score']})"
        draw.text((rect[0], max(0, rect[1] - 24)), label, fill=color, font=small)

    crop = image.crop((350, 2050, 2250, 3060))
    crop.save(OUT_OVERLAY, quality=92)

    md = [
        "# Lower Corridor Evidence Ranking",
        "",
        "Scope: rank exact lower-corridor units after the bridge-normalized chain. This is evidence comparison only; no key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## Ranking",
        "",
        "| rank | candidate | score | layers | role | evidence |",
        "|---:|---|---:|---:|---|---|",
    ]
    for i, cand in enumerate(ranked, 1):
        md.append(
            f"| {i} | `{cand['label']}` | {cand['score']} | {cand['independentLayerCount']} | "
            f"{cand['role']} | {'; '.join(cand['evidence']) or '-'} |"
        )

    md.extend(["", "## Streams", ""])
    for key, value in result["streams"].items():
        md.append(f"- `{key}`: `{value}`")

    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    md.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    print(OUT_OVERLAY)


if __name__ == "__main__":
    main()
