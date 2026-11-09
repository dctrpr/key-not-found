#!/usr/bin/env python3
"""Manual audit of page-80 package/bottle copy.

The page-80 text is graphic/package copy, so it sits outside the article-body
transcript. This checks whether its visible labels and numbers provide a
simple selector for the now-established page-76 target groups.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
OUT_MD = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.md"


PACKAGE_LINES = [
    {"label": "top_right", "text": "FAKE AD"},
    {"label": "cap_front", "text": "5 SYMPTOM RELIEF"},
    {"label": "product", "text": "Bitcoin FixesThis"},
    {"label": "claim_1", "text": "100% Proof of Work Liquid"},
    {"label": "claim_2", "text": "Fiat Humiditus Reliever / Anticentralization"},
    {"label": "bottle_front", "text": "5 SYMPTOM RELIEF"},
    {"label": "symptoms", "text": "NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS"},
    {"label": "volume_visible_likely", "text": "16 FL OZ (473 mL)"},
    {"label": "volume_crop_recorded", "text": "6 FL OZ (473 mL)"},
    {"label": "footer", "text": "TOXIC BTB"},
    {"label": "page_number", "text": "80"},
]

KNOWN_PAGE76_GROUPS = [
    "Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.",
    "by the rancid catnip of fiat money.",
    "buying the dip.",
    "It’s a stun gun to the genitals.",
    "$1 billion",
]

KNOWN_PAGE76_GROUP_INITIALS = "GbbI$"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def initials(text: str) -> str:
    return "".join(w[0] for w in words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1] for w in words(text) if w)


def numbers(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", text)]


def page76_stats() -> dict:
    data = json.loads(CANONICAL_JSON.read_text())
    page = next(p for p in data["pages"].values() if p["articlePage"] == 76)
    nonblank_lines = [ln for ln in page["lines"] if ln["text"].strip()]
    return {
        "lineCount": len(nonblank_lines),
        "wordCount": len(page["words"]),
        "line16": next((ln["text"].strip() for ln in page["lines"] if ln["lineIndex"] == 16), ""),
        "word5_1based": page["words"][4]["text"] if len(page["words"]) >= 5 else "",
        "word16_1based": page["words"][15]["text"] if len(page["words"]) >= 16 else "",
        "word80_1based": page["words"][79]["text"] if len(page["words"]) >= 80 else "",
        "word100_1based": page["words"][99]["text"] if len(page["words"]) >= 100 else "",
        "word473_1based": page["words"][472]["text"] if len(page["words"]) >= 473 else "",
    }


def main() -> None:
    line_records = []
    all_text = " ".join(row["text"] for row in PACKAGE_LINES)
    for row in PACKAGE_LINES:
        line_records.append(
            {
                **row,
                "initials": initials(row["text"]),
                "lasts": lasts(row["text"]),
                "numbers": numbers(row["text"]),
            }
        )

    all_numbers = numbers(all_text)
    p76 = page76_stats()
    numeric_checks = {
        "5_matches_page76_target_group_count": len(KNOWN_PAGE76_GROUPS) == 5,
        "5_matches_page76_group_initials": KNOWN_PAGE76_GROUP_INITIALS,
        "16_as_page76_line": p76["line16"],
        "1based_page76_words": {
            "5": p76["word5_1based"],
            "16": p76["word16_1based"],
            "80": p76["word80_1based"],
            "100": p76["word100_1based"],
            "473": p76["word473_1based"],
        },
    }

    streams = {
        "package_all_initials": "".join(r["initials"] for r in line_records),
        "package_all_lasts": "".join(r["lasts"] for r in line_records),
        "numbers_joined": "".join(str(n) for n in all_numbers),
        "numbers_csv": ",".join(str(n) for n in all_numbers),
        "known_page76_group_initials": KNOWN_PAGE76_GROUP_INITIALS,
        "symptom_initials": initials("NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS"),
        "claims_initials": initials(PACKAGE_LINES[3]["text"] + " " + PACKAGE_LINES[4]["text"]),
    }

    result = {
        "sourceImage": str(ROOT / "analysis_outputs/3d_article_map/page_80_upright.jpg"),
        "manualTranscription": line_records,
        "streams": streams,
        "page76Stats": p76,
        "numericChecks": numeric_checks,
        "assessment": [
            "The package copy is useful as an unresolved visual layer, but it does not contain a direct instruction.",
            "The strongest low-parameter link is count-based: '5 SYMPTOM RELIEF' appears twice and the label lists exactly five symptoms: nausea, heartburn, indigestion, upset stomach, and shitcoins. This matches the five page-76 target groups from the reflected graph.",
            "The volume is visually and semantically likely '16 FL OZ (473 mL)'; an existing crop-only source records '6 FL OZ' because the left edge is clipped. If using p80 numbers, keep this ambiguity registered.",
            "The number 16 lands on the page-76 line containing 'It's a stun gun to the genitals.', but this is not enough by itself because other package numbers do not produce a coherent index stream.",
            "Treat p80 as thematic/count support unless a source/physical alignment shows the bottle copy lining up with another page.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page-80 Package Copy Audit",
        "",
        "Scope: manual transcription and low-parameter selector checks for page-80 graphic/package copy. No private-key candidates are generated.",
        "",
        f"- Source image: `{result['sourceImage']}`",
        "",
        "## Manual Transcription",
        "",
    ]
    for r in line_records:
        md.append(
            f"- {r['label']}: `{r['text']}` initials=`{r['initials']}` lasts=`{r['lasts']}` numbers={r['numbers']}"
        )
    md.extend(["", "## Streams", ""])
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value}`")
    md.extend(["", "## Numeric Checks", ""])
    md.append(f"- `5` matches known page-76 target group count: `{numeric_checks['5_matches_page76_target_group_count']}`")
    md.append(f"- Known page-76 group initials: `{KNOWN_PAGE76_GROUP_INITIALS}`")
    md.append(f"- `16` as page-76 line: `{p76['line16']}`")
    md.append("- Volume ambiguity: full-page visual and 473 mL imply `16 FL OZ`; crop-only source records `6 FL OZ` because the left edge is clipped.")
    md.append("- 1-based page-76 word checks:")
    for key, value in numeric_checks["1based_page76_words"].items():
        md.append(f"  - `{key}` -> `{value}`")
    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    OUT_MD.write_text("\n".join(md) + "\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
