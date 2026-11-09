#!/usr/bin/env python3
"""Audit how specific the p78 graphic support is for #4 landings.

The line-offset landing evidence pass found that the #4 landing lines are
supported by p78 graphic/reflection evidence. This script asks a stricter
question: does p78 select those #4 lines specifically, or does it cover a
broader lower-page band?

No key candidates or hashing are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P78_WORD_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json"
LANDING_JSON = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
OUT = ROOT / "analysis_outputs/source_audit/p78_graphic_band_specificity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_graphic_band_specificity.json"
OUT_MD = OUT / "p78_graphic_band_specificity.md"

STOP = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "into",
    "from",
    "because",
    "worth",
    "future",
    "would",
    "could",
    "should",
    "have",
    "been",
    "were",
    "they",
    "their",
    "your",
    "here",
    "there",
}


def token_list(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Za-z0-9]+", text)]


def interesting(text: str) -> set[str]:
    return {w for w in token_list(text) if len(w) >= 4 and w not in STOP}


def group_by_y(rows: list[dict], tolerance: float = 35.0) -> list[dict]:
    groups: list[dict] = []
    for row in sorted(rows, key=lambda item: (item["center"][1], item["center"][0])):
        y = row["center"][1]
        if not groups or abs(groups[-1]["y"] - y) > tolerance:
            groups.append({"y": y, "rows": []})
        groups[-1]["rows"].append(row)
        groups[-1]["y"] = sum(item["center"][1] for item in groups[-1]["rows"]) / len(groups[-1]["rows"])
    out = []
    for idx, group in enumerate(groups, 1):
        ordered = sorted(group["rows"], key=lambda item: item["center"][0])
        text = " ".join(item["text"] for item in ordered)
        out.append(
            {
                "bandRow": idx,
                "y": round(group["y"], 1),
                "wordCount": len(ordered),
                "text": text,
                "tokens": sorted(interesting(text)),
                "wordIndexes": [item["index"] for item in ordered],
            }
        )
    return out


def row_terms(rows: list[dict]) -> set[str]:
    return {row.get("token", "").lower() for row in rows if len(row.get("token", "")) >= 4 and row.get("token", "").lower() not in STOP}


def landing_hits(landings: list[dict], terms: set[str]) -> list[dict]:
    out = []
    for row in landings:
        text_terms = interesting(row["targetText"])
        hits = sorted(text_terms & terms)
        out.append(
            {
                "sourceId": row["sourceId"],
                "sourceIndex": row["sourceIndex"],
                "targetLine": row["targetLine"],
                "targetUnits": row.get("targetUnits", []),
                "targetText": row["targetText"],
                "hitTerms": hits,
                "hit": bool(hits),
            }
        )
    return out


def main() -> None:
    p78 = json.loads(P78_WORD_JSON.read_text())
    landing = json.loads(LANDING_JSON.read_text())
    down_landings = [row for row in landing["scoredLandings"] if row["targetText"]]

    bbox_words = p78.get("bboxWords", [])
    dark_words = p78.get("darkHits", [])
    hole_words = p78.get("holeHits", [])
    bbox_rows = group_by_y(bbox_words)
    dark_rows = group_by_y(dark_words)
    hole_rows = group_by_y(hole_words)

    terms = {
        "bbox": row_terms(bbox_words),
        "dark": row_terms(dark_words),
        "hole": row_terms(hole_words),
    }
    landing_term_hits = {
        "bbox": landing_hits(down_landings, terms["bbox"]),
        "dark": landing_hits(down_landings, terms["dark"]),
        "hole": landing_hits(down_landings, terms["hole"]),
    }

    hit_landing_ids = {
        layer: [f"{row['sourceId']}+{row['sourceIndex']}" for row in rows if row["hit"]]
        for layer, rows in landing_term_hits.items()
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Specificity audit for p78 graphic support of page-76 line-offset landings; no key derivation.",
        "reflectedBoxOnP76": p78["reflectedBoxOnP76"],
        "bboxRows": bbox_rows,
        "darkRows": dark_rows,
        "holeRows": hole_rows,
        "terms": {key: sorted(value) for key, value in terms.items()},
        "landingTermHits": landing_term_hits,
        "hitLandingIds": hit_landing_ids,
        "assessment": [
            "The p78 graphic reflection covers a broad lower page-76 band, not only the #4 landing lines.",
            "Bbox rows span ordinary corridor fragments including `should sell`, `earnings`, `pay off the IMF`, `I tagged Mike`, `could sell`, `trust that guy`, and the final OCR blob for `shitcoiner at heart`.",
            "#4 landing support is real but not specific: it is part of a wider p78 graphic band over lines 25-32.",
            "Treat #4 as broad source-layer corroboration for the lower corridor, not as an extraction rule or precise selector.",
        ],
        "nextMove": "Look for an external/source rule that tells which word(s) inside the broad p78 band to use; do not promote every p78-band word equally.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# P78 Graphic Band Specificity Audit",
        "",
        "Scope: test whether p78 graphic support for #4 landing lines is specific or just broad lower-corridor coverage. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Reflected p76 box: `{result['reflectedBoxOnP76']}`",
        "",
        "## Bbox Word Rows",
        "",
        "| row | y | text |",
        "|---:|---:|---|",
    ]
    for row in bbox_rows:
        text = row["text"].replace("|", "\\|")
        md.append(f"| {row['bandRow']} | {row['y']} | {text} |")

    md.extend(
        [
            "",
            "## Landing Term Hits",
            "",
            "| layer | landings hit |",
            "|---|---|",
        ]
    )
    for layer, ids in hit_landing_ids.items():
        md.append(f"| `{layer}` | `{', '.join(ids) or '-'}` |")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The p78 graphic reflection is a broad lower-corridor band, not a precise #4-only selector.",
            "- #4 remains supported because its landing lines are inside this band, but the same band also covers IMF/Mike/trust/heart material.",
            "- This reduces the evidentiary weight of #4 as a unique clue and preserves it only as source-layer corroboration.",
            "- Next best move: find a source/provenance rule that says which word or line inside the p78 band should be read.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
