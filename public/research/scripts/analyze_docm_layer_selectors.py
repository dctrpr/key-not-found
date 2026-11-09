#!/usr/bin/env python3
"""Small selector audit for DOCM font layers.

Focuses on short, human-readable streams from `Article with Fonts.docm`,
especially the cyan layer and alternate-font (`Typeka Mix`) runs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
OUT_MD = ROOT / "analysis_outputs/docm_format_sources/docm_layer_selector_audit.md"
OUT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_layer_selector_audit.json"

PAGE_BY_PARAGRAPH = [
    (75, 0, 39),
    (76, 41, 73),
    (77, 75, 108),
    (78, 110, 139),
    (79, 141, 168),
]

INSTRUCTION_WORDS = {
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "bitcoin",
    "down",
    "below",
    "above",
    "first",
    "last",
    "page",
}


def page_for_para(idx: int) -> int | None:
    for page, start, end in PAGE_BY_PARAGRAPH:
        if start <= idx <= end:
            return page
    return None


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9$]", text))


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def first_initial(text: str) -> str:
    ws = words(text)
    return ws[0][0] if ws else ""


def last_initial(text: str) -> str:
    ws = words(text)
    return ws[-1][0] if ws else ""


def word_hits(text: str) -> list[str]:
    lowered = {w.lower() for w in words(text)}
    return sorted(lowered & INSTRUCTION_WORDS)


def run_context(runs: list[dict], run_index: int, window: int = 2) -> str:
    start = max(0, run_index - window)
    end = min(len(runs), run_index + window + 1)
    parts = []
    for r in runs[start:end]:
        text = clean(r["text"])
        if not text:
            continue
        if r["runIndex"] == run_index:
            parts.append(f"[{text}]")
        else:
            parts.append(text)
    return " ".join(parts)


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text())
    for r in runs:
        r["page"] = page_for_para(r["paragraphIndex"])

    cyan = [r for r in runs if r.get("highlight") == "cyan" and clean(r["text"])]
    mix = [r for r in runs if r.get("fontAscii") == "Typeka Mix" and clean(r["text"])]

    def page_layer(layer_runs: list[dict]) -> dict[str, dict[str, str]]:
        out = {}
        for page in sorted({r["page"] for r in layer_runs if r["page"] is not None}):
            page_runs = [r for r in layer_runs if r["page"] == page]
            text = clean("".join(r["text"] for r in page_runs))
            out[str(page)] = {
                "runInitials": "".join(first_initial(r["text"]) for r in page_runs),
                "runLastInitials": "".join(last_initial(r["text"]) for r in page_runs),
                "runLengths": ",".join(str(len(letters(r["text"]))) for r in page_runs),
                "letters": "".join(letters(r["text"]) for r in page_runs),
                "text": text,
                "instructionHits": word_hits(text),
            }
        return out

    cyan_records = [
        {
            "runIndex": r["runIndex"],
            "paragraphIndex": r["paragraphIndex"],
            "page": r["page"],
            "text": r["text"],
            "letters": letters(r["text"]),
            "context": run_context(runs, r["runIndex"]),
        }
        for r in cyan
    ]

    mix_all_text = clean("".join(r["text"] for r in mix))
    streams = {
        "cyan_letters": "".join(letters(r["text"]) for r in cyan),
        "cyan_run_initials": "".join(first_initial(r["text"]) for r in cyan),
        "cyan_pages": ",".join(str(r["page"]) for r in cyan),
        "typeka_mix_run_initials": "".join(first_initial(r["text"]) for r in mix),
        "typeka_mix_run_last_initials": "".join(last_initial(r["text"]) for r in mix),
        "typeka_mix_run_lengths": ",".join(str(len(letters(r["text"]))) for r in mix),
        "typeka_mix_instruction_hits": ",".join(word_hits(mix_all_text)),
    }

    result = {
        "sourceRuns": str(RUNS_JSON),
        "streams": streams,
        "cyanRecords": cyan_records,
        "typekaMixByPage": page_layer(mix),
        "assessment": [
            "Cyan stream is MNBILLION and appears on p75/p75/p78. It is an anomaly but not an instruction.",
            "The cyan BILLION sits inside the p78 '$85 BILLION' yellow phrase, creating a semantic bridge to the p76 '$1 billion' target.",
            "Typeka Mix initials/last-initials/lengths do not form readable instruction text.",
            "Typeka Mix remains the best available alternate-font/partial-bold witness, but it needs a separate selector before it can be used for extraction.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# DOCM Layer Selector Audit",
        "",
        "Scope: test short selector-like streams from `Article with Fonts.docm` font layers. No private-key candidates are generated.",
        "",
        "## Streams",
        "",
    ]
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value}`")
    md.extend(["", "## Cyan Records", ""])
    for r in cyan_records:
        md.append(
            f"- run {r['runIndex']} p{r['page']} text=`{r['text']}` letters=`{r['letters']}` context=`{r['context']}`"
        )
    md.extend(["", "## Typeka Mix By Page", ""])
    for page, info in result["typekaMixByPage"].items():
        md.append(f"### p{page}")
        for key, value in info.items():
            preview = value[:700] + ("..." if len(value) > 700 else "") if isinstance(value, str) else value
            md.append(f"- `{key}`: `{preview}`")
    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
