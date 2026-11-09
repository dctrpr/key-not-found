#!/usr/bin/env python3
"""Integrate the latest user-supplied plain article text as a corrected witness."""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "plain_text_transcript"
RAW = OUT / "user_plain_article_latest.txt"
DOCM_TEXT = ROOT / "analysis_outputs" / "docm_format_sources" / "article_with_fonts_text.txt"
FIXED_BODY = OUT / "canonical_plain_article_body.txt"
FIXED_WITH_SIGNATURE = OUT / "canonical_plain_article_with_signature.txt"
REPORT = OUT / "plain_article_correction_report.md"
JSON_OUT = OUT / "plain_article_correction_report.json"


MANUAL_CORRECTIONS = [
    {
        "raw": "Bitcoin is toxic af",
        "fixed": "BITCOIN IS TOXIC AF",
        "reason": "Article title is uppercase in the scan and DOCM witness.",
    },
    {
        "raw": "Really? Yes",
        "fixed": "Really? Yes.",
        "reason": "DOCM witness includes the period after Yes.",
    },
    {
        "raw": "hands I\\nn the muck",
        "fixed": "hands in the muck",
        "reason": "The raw plain text split the word `in` across lines incorrectly.",
    },
    {
        "raw": "puts and end",
        "fixed": "puts an end",
        "reason": "DOCM/Markdown witness agree on `an end`.",
    },
    {
        "raw": '"buying the dip".',
        "fixed": '"buying the dip."',
        "reason": "DOCM witness places the period inside the quote.",
    },
    {
        "raw": "collateralized to pay off the IMF",
        "fixed": "collateralized “Volcano Bonds” to pay off the IMF",
        "reason": "The raw plain text omitted the highlighted `Volcano Bonds` phrase.",
    },
    {
        "raw": "At this rate the whole",
        "fixed": "At this rate, the whole",
        "reason": "DOCM witness includes the comma.",
    },
    {
        "raw": "big blockers",
        "fixed": "Big blockers",
        "reason": "DOCM witness capitalizes the sentence start.",
    },
    {
        "raw": "Full stop.",
        "fixed": "Full Stop.",
        "reason": "DOCM witness capitalizes both words.",
    },
    {
        "raw": "Every single one of the bitcoin wannabes- ...",
        "fixed": "EVERY SINGLE ONE OF THE BITCOIN WANNABES - ...",
        "reason": "This block is all uppercase in the scan and DOCM witness.",
    },
    {
        "raw": "It's guaranteed, mathematical certainty.",
        "fixed": "It's a guaranteed, mathematical certainty.",
        "reason": "DOCM witness includes `a`.",
    },
    {
        "raw": "bitcoin was designed",
        "fixed": "Bitcoin was designed",
        "reason": "DOCM witness capitalizes Bitcoin at this sentence position.",
    },
    {
        "raw": "gargantually wasteful",
        "fixed": "gargantuanly wasteful",
        "reason": "DOCM witness has `gargantuanly`.",
    },
    {
        "raw": "requires printing and wars",
        "fixed": "requires money printing and wars",
        "reason": "The raw plain text omitted `money`.",
    },
    {
        "raw": "cost 2 trillion fiat cuck bucks",
        "fixed": "cost $2 trillion fiat cuck-bucks",
        "reason": "DOCM witness includes the dollar sign and hyphenated `cuck-bucks`.",
    },
    {
        "raw": "Bitcoin fixes all this",
        "fixed": "BITCOIN FIXES ALL THIS",
        "reason": "This lead phrase is all uppercase in the scan and DOCM witness.",
    },
    {
        "raw": "Remove the war incentive and you remove",
        "fixed": "Remove the war incentive, and you remove",
        "reason": "DOCM witness includes the comma.",
    },
    {
        "raw": "It's fact baked",
        "fixed": "It's a fact baked",
        "reason": "DOCM witness includes `a`.",
    },
    {
        "raw": "In so doing our energy consumption",
        "fixed": "In so doing, our energy consumption",
        "reason": "DOCM witness includes the comma.",
    },
    {
        "raw": "gets monetized and for the first time in our existence",
        "fixed": "gets monetized for the first time in our existence",
        "reason": "The raw plain text inserted an extra `and`.",
    },
    {
        "raw": "smile- virtually nothing",
        "fixed": "smile - virtually nothing",
        "reason": "DOCM witness uses spaced hyphen.",
    },
]


def clean_docm_text(text: str) -> str:
    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = re.sub(r"[ \t]+", " ", line).rstrip()
        lines.append(line)
    # Collapse excessive empty lines while preserving paragraph-ish breaks.
    cleaned = "\n".join(lines).strip()
    return cleaned + "\n"


def normalized_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%']+|[.,;:!?\"“”()—-]", text)


def diff_summary(raw_text: str, fixed_text: str, limit: int = 80) -> list[str]:
    raw_words = normalized_words(raw_text)
    fixed_words = normalized_words(fixed_text)
    diff = list(difflib.unified_diff(raw_words, fixed_words, n=2, lineterm=""))
    return diff[:limit]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_text = RAW.read_text()
    docm = DOCM_TEXT.read_text()
    fixed_body = clean_docm_text(docm)
    fixed_with_signature = fixed_body.rstrip() + "\n\nMAX KEISER\n"

    FIXED_BODY.write_text(fixed_body)
    FIXED_WITH_SIGNATURE.write_text(fixed_with_signature)

    raw_lower = raw_text.lower()
    correction_records = []
    for item in MANUAL_CORRECTIONS:
        present = item["raw"].replace("\\n", "\n").lower().strip(".") in raw_lower
        correction_records.append({**item, "rawPatternPresent": present})

    report = {
        "rawSource": str(RAW),
        "docmWitness": str(DOCM_TEXT),
        "fixedBody": str(FIXED_BODY),
        "fixedWithSignature": str(FIXED_WITH_SIGNATURE),
        "manualCorrections": correction_records,
        "wordLevelDiffPreview": diff_summary(raw_text, fixed_with_signature),
        "assessment": [
            "Use the DOCM-derived fixed body as the canonical plain-text witness for article wording.",
            "`MAX KEISER` is preserved in the with-signature output because it appears visually on the scan, but it is not part of the DOCM body text.",
            "The raw plain text is useful, but contains several transcription omissions and punctuation/capitalization mismatches that can break exact selector work.",
        ],
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Plain Article Text Correction Report",
        "",
        "Scope: integrate the latest user-supplied plain text and correct it against the stronger `Article with Fonts.docm` witness. This is a text-source cleanup pass only; no key derivation was run.",
        "",
        "## Outputs",
        "",
        f"- raw user plain text: `{RAW}`",
        f"- fixed body text: `{FIXED_BODY}`",
        f"- fixed body plus visual signature: `{FIXED_WITH_SIGNATURE}`",
        f"- JSON report: `{JSON_OUT}`",
        "",
        "## Corrections Applied / Registered",
        "",
    ]
    for item in correction_records:
        mark = "found" if item["rawPatternPresent"] else "registered"
        lines.append(f"- `{item['raw']}` -> `{item['fixed']}` ({mark}): {item['reason']}")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The fixed text should replace the latest raw plain copy for exact text, word-count, and line-level selector work.",
            "- The highest-impact raw-copy omissions were `Volcano Bonds`, `money`, the `$` in `$2 trillion`, and the extra `and` in `gets monetized for the first time`.",
            "- Keep both fixed variants: body-only for DOCM-derived text experiments, and with-signature when testing scan-visible text including the page-79 `MAX KEISER` signature.",
            "- This pass does not change the current conclusion: the missing step is still a selector/registration rule, not another broad hashing branch.",
            "",
            "## Diff Preview",
            "",
        ]
    )
    for line in report["wordLevelDiffPreview"]:
        lines.append(f"`{line}`")
    REPORT.write_text("\n".join(lines) + "\n")
    print(REPORT)
    print(FIXED_WITH_SIGNATURE)


if __name__ == "__main__":
    main()
