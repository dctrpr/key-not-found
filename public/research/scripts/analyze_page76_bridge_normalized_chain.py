#!/usr/bin/env python3
"""Build the page-76 locator chain with the B3 bridge normalized.

This is an explanation-first audit. It promotes B3+3 -> prompt -> O4 as a
bridge edge, then asks whether the resulting ordered chain itself names an
extraction unit. It does not generate private-key candidates, hashes, seeds,
or address checks.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LINE_OFFSET_JSON = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"
LANDING_EVIDENCE_JSON = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
WEAK_SUPPORT_JSON = ROOT / "analysis_outputs/source_audit/page76_weak_landing_support/page76_weak_landing_support.json"
B3_BRIDGE_JSON = ROOT / "analysis_outputs/source_audit/b3_gap_bridge/b3_gap_bridge.json"
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/page76_bridge_normalized_chain"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_bridge_normalized_chain.json"
OUT_MD = OUT / "page76_bridge_normalized_chain.md"
OUT_OVERLAY = OUT / "page76_bridge_normalized_chain_overlay.jpg"


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
    "wif",
    "address",
]


PREFERRED_TERMS = {
    "O1": "bitcoin",
    "B1": "nonsense",
    "O3": "stun",
    "B3": "buying dip",
    "O4": "earnings",
    "B4": "sell",
    "B5": "heart",
}


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_page76() -> dict:
    data = json.loads(CANONICAL_JSON.read_text())
    return next(page for page in data["pages"].values() if page["articlePage"] == 76)


def load_highres_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def highres_rows(page: dict) -> list[dict]:
    rows: list[list[dict]] = []
    for word in sorted(page["words"], key=lambda w: (w["center"][1], w["center"][0])):
        if word.get("token") == "overdose":
            continue
        placed = False
        for row in rows:
            if abs(row[0]["center"][1] - word["center"][1]) < 16:
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])

    out = []
    for row in rows:
        row.sort(key=lambda w: w["center"][0])
        out.append(
            {
                "y": sum(w["center"][1] for w in row) / len(row),
                "tokens": [norm(w.get("token") or w.get("text") or "") for w in row if norm(w.get("token") or w.get("text") or "")],
                "words": row,
                "box": [
                    min(w["box"][0] for w in row),
                    min(w["box"][1] for w in row),
                    max(w["box"][2] for w in row),
                    max(w["box"][3] for w in row),
                ],
                "text": " ".join(w["text"] for w in row),
            }
        )
    return out


def page_line_text(page: dict, line_index: int) -> str:
    if 0 <= line_index < len(page["lines"]):
        return clean(page["lines"][line_index]["text"])
    return ""


def line_tokens(page: dict, line_index: int) -> list[str]:
    return [norm(w["letters"] or w["text"]) for w in page["words"] if w["lineIndex"] == line_index and norm(w["letters"] or w["text"])]


def best_row_for_line(tokens: list[str], rows: list[dict]) -> dict | None:
    if not tokens:
        return None
    best = None
    best_score = -1
    for row in rows:
        score = 0
        for token in set(tokens):
            score += min(tokens.count(token), row["tokens"].count(token))
        if score > best_score:
            best = row
            best_score = score
    return best if best_score > 0 else None


def units_by_id(units: list[dict]) -> dict[str, dict]:
    return {unit["id"]: unit for unit in units}


def units_by_line(units: list[dict]) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = defaultdict(list)
    for unit in units:
        out[unit["line"]].append(unit)
    return out


def evidence_by_source() -> dict[str, dict]:
    if not LANDING_EVIDENCE_JSON.exists():
        return {}
    data = json.loads(LANDING_EVIDENCE_JSON.read_text())
    return {row["sourceId"]: row for row in data.get("scoredLandings", []) if row.get("sourceId")}


def weak_by_source() -> dict[str, dict]:
    if not WEAK_SUPPORT_JSON.exists():
        return {}
    data = json.loads(WEAK_SUPPORT_JSON.read_text())
    return {row["sourceId"]: row for row in data.get("auditedLandings", []) if row.get("sourceId")}


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, value in streams.items():
        value_norm = value.lower()
        found = [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", value_norm)]
        if found:
            hits[name] = found
    return hits


def main() -> None:
    offset = json.loads(LINE_OFFSET_JSON.read_text())
    bridge = json.loads(B3_BRIDGE_JSON.read_text())
    page = load_page76()
    highres = load_highres_page76()
    rows = highres_rows(highres)
    unit_by_id = units_by_id(offset["units"])
    unit_by_line = units_by_line(offset["units"])
    evidence = evidence_by_source()
    weak = weak_by_source()

    records = []
    for row in [r for r in offset["landingRows"] if r.get("direction") == "down"]:
        source_id = row["sourceId"]
        classification = "unsupported"
        normalized_line = row["targetLine"]
        normalized_units = row["targetUnits"]
        normalized_text = row["targetText"]
        bridge_prompt = ""
        total_steps = f"+{row['sourceIndex']}"
        evidence_layers = evidence.get(source_id, {}).get("layers", [])
        score = evidence.get(source_id, {}).get("score", 0)

        if row["targetUnits"]:
            classification = "highlight-hit"
        elif source_id == "B3" and bridge["b3Bridge"]["secondUnits"]:
            classification = "bridge-hit"
            bridge_prompt = bridge["b3Bridge"]["firstText"]
            normalized_line = bridge["b3Bridge"]["secondLine"]
            normalized_units = bridge["b3Bridge"]["secondUnits"]
            normalized_text = bridge["b3Bridge"]["secondText"]
            total_steps = f"+{row['sourceIndex']} then +{row['sourceIndex']}"
            evidence_layers = ["bridge prompt", "highlight target"]
            score = 4
        elif score > 0:
            classification = "source-supported-line"
        elif weak.get(source_id, {}).get("secondarySupportScore", 0) > 0:
            classification = "weak-secondary-line"
            score = weak[source_id]["secondarySupportScore"]
            evidence_layers = weak[source_id].get("supportLabels", [])
        elif row.get("outOfRange"):
            classification = "out-of-range"

        preferred = PREFERRED_TERMS.get(source_id)
        if not preferred and normalized_units:
            preferred = " ".join(unit_by_id[u]["label"] for u in normalized_units if u in unit_by_id)
        if not preferred:
            line_words = words(normalized_text)
            preferred = " ".join(line_words[:2]).lower() if line_words else ""

        line_row = best_row_for_line(line_tokens(page, normalized_line), rows)
        source = unit_by_id.get(source_id)
        source_row = best_row_for_line(line_tokens(page, source["line"]), rows) if source else None

        records.append(
            {
                "sourceId": source_id,
                "sourceColor": source_id[0],
                "sourceIndex": row["sourceIndex"],
                "sourceLine": row["sourceLine"],
                "sourceLabel": row["sourceLabel"],
                "firstLandingLine": row["targetLine"],
                "firstLandingText": row["targetText"],
                "bridgePrompt": bridge_prompt,
                "normalizedTargetLine": normalized_line,
                "normalizedTargetText": normalized_text,
                "normalizedUnits": normalized_units,
                "classification": classification,
                "score": score,
                "evidenceLayers": evidence_layers,
                "totalSteps": total_steps,
                "preferredTerm": preferred,
                "sourceRowBox": [round(v, 2) for v in source_row["box"]] if source_row else None,
                "targetRowBox": [round(v, 2) for v in line_row["box"]] if line_row else None,
            }
        )

    strict = [r for r in records if r["classification"] in {"highlight-hit", "bridge-hit", "source-supported-line"}]
    all_nondead = [r for r in records if r["classification"] not in {"unsupported", "out-of-range"}]

    streams = {
        "strictSourceIds": " ".join(r["sourceId"] for r in strict),
        "strictColors": "".join(r["sourceColor"] for r in strict),
        "strictIndices": "".join(str(r["sourceIndex"]) for r in strict),
        "strictTargetLines": " ".join(str(r["normalizedTargetLine"]) for r in strict),
        "strictPreferredTerms": " ".join(r["preferredTerm"] for r in strict if r["preferredTerm"]),
        "strictPreferredInitials": "".join((r["preferredTerm"][:1] or "") for r in strict),
        "strictPreferredLastLetters": "".join((norm(r["preferredTerm"])[-1:] or "") for r in strict if norm(r["preferredTerm"])),
        "allNondeadSourceIds": " ".join(r["sourceId"] for r in all_nondead),
        "allNondeadPreferredTerms": " ".join(r["preferredTerm"] for r in all_nondead if r["preferredTerm"]),
    }
    streams["strictPreferredTermsReversed"] = " ".join(reversed(streams["strictPreferredTerms"].split()))
    streams["strictPreferredInitialsReversed"] = streams["strictPreferredInitials"][::-1]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 line-offset chain with B3 bridge normalized; no key derivation.",
        "records": records,
        "strictChainRecords": strict,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
        "assessment": [
            "The B3 bridge makes the locator map cleaner: the strict chain is O1, B1, O3, B3, O4, B4, B5.",
            "The resulting strict color/index stream is OBOBOBB / 1133445, and the preferred term stream is `bitcoin nonsense stun buying dip earnings sell heart`.",
            "Those streams do not contain extraction instructions such as read/take/use/fold/mirror/word/letter/key.",
            "The bridge strengthens O4 as part of the path, but it still does not specify whether to extract a word, letter, row, edge, or adjacent phrase.",
            "Keep the bridge-normalized chain as structural evidence; close the chain streams as standalone instructions.",
        ],
        "nextMove": "Use the bridge-normalized chain to inspect the #4 lower corridor more narrowly: O4/B4/B5 are now the unresolved segment where exact unit/order still needs a source rule.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    colors = {
        "highlight-hit": (40, 120, 255, 220),
        "bridge-hit": (255, 128, 0, 235),
        "source-supported-line": (80, 170, 90, 230),
        "weak-secondary-line": (180, 120, 30, 180),
        "unsupported": (120, 120, 120, 150),
        "out-of-range": (120, 120, 120, 90),
    }

    for rec in records:
        for key, prefix in (("sourceRowBox", "S"), ("targetRowBox", "T")):
            box = rec.get(key)
            if not box:
                continue
            color = colors.get(rec["classification"], (120, 120, 120, 180))
            pad = 7 if prefix == "T" else 3
            rect = [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad]
            alpha_fill = 28 if prefix == "T" else 12
            draw.rectangle(rect, outline=color, width=4 if prefix == "T" else 2, fill=(color[0], color[1], color[2], alpha_fill))
            if prefix == "T":
                label = f"{rec['sourceId']} -> {rec['preferredTerm']} ({rec['classification']})"
                draw.text((rect[0], max(0, rect[1] - 22)), label, fill=color, font=small)

    # Keep the visual focused on the page-76 text column and lower corridor.
    image.save(OUT_OVERLAY, quality=92)

    md = [
        "# Page 76 Bridge-Normalized Chain",
        "",
        "Scope: normalize the page-76 line-offset chain using the B3 bridge (`B3 -> Don't believe me? -> O4`) and check whether the resulting ordered chain names an extraction unit. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## Strict Chain",
        "",
        "| source | class | steps | normalized target | preferred term | evidence |",
        "|---|---|---|---|---|---|",
    ]
    for rec in strict:
        evidence_text = ", ".join(rec["evidenceLayers"]) or "-"
        md.append(
            f"| `{rec['sourceId']}` | `{rec['classification']}` | `{rec['totalSteps']}` | "
            f"L{rec['normalizedTargetLine']} `{rec['normalizedTargetText'] or '-'}` | "
            f"`{rec['preferredTerm'] or '-'}` | {evidence_text} |"
        )

    md.extend(["", "## Streams", ""])
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value or '-'}`")
    if result["instructionTermHits"]:
        md.append(f"- Instruction-term hits: `{result['instructionTermHits']}`")
    else:
        md.append("- Instruction-term hits: none")

    md.extend(["", "## All Records", "", "| source | class | first landing | normalized target |", "|---|---|---|---|"])
    for rec in records:
        md.append(
            f"| `{rec['sourceId']}` | `{rec['classification']}` | "
            f"L{rec['firstLandingLine']} `{rec['firstLandingText'] or '-'}` | "
            f"L{rec['normalizedTargetLine']} `{rec['normalizedTargetText'] or '-'}` |"
        )

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
