#!/usr/bin/env python3
"""Audit Typeka regular/mix/bold state changes as a selector hypothesis."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "analysis_outputs" / "docm_format_sources" / "article_with_fonts_runs.json"
FONT_AUDIT = ROOT / "analysis_outputs" / "docm_format_sources" / "docm_font_layer_audit.json"
OUT_DIR = ROOT / "analysis_outputs" / "docm_format_sources"
MD_OUT = OUT_DIR / "typeka_variant_state_audit.md"
JSON_OUT = OUT_DIR / "typeka_variant_state_audit.json"

INSTRUCTION_WORDS = {
    "read",
    "mirror",
    "fold",
    "take",
    "use",
    "first",
    "last",
    "left",
    "right",
    "page",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "wallet",
    "seed",
    "index",
    "order",
    "reverse",
    "dip",
    "billion",
    "volcano",
}


def clean_letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z]", text))


def clean_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z']*|\d+|[%$]", text)


def page_for_paragraph(paragraph: int, boundaries: list[dict]) -> int | None:
    for item in boundaries:
        if item["paragraphStart"] <= paragraph <= item["paragraphEnd"]:
            return item["page"]
    return None


def variant(run: dict) -> str:
    font = run.get("fontAscii") or run.get("fontHAnsi") or ""
    if font == "Typeka Mix":
        return "MIX_BOLD" if run.get("bold") else "MIX"
    if font == "Typeka":
        return "TYPEKA_BOLD" if run.get("bold") else "TYPEKA"
    if font == "Stencil":
        return "STENCIL"
    if font == "LonestarW00-Regular":
        return "LONESTAR"
    return "OTHER"


def nonblank(run: dict) -> bool:
    return bool((run.get("text") or "").strip())


def run_initial(text: str) -> str:
    letters = clean_words(text)
    if not letters:
        return ""
    return letters[0][0]


def run_last(text: str) -> str:
    letters = clean_words(text)
    if not letters:
        return ""
    return letters[-1][-1]


def stream_for(runs: list[dict], mode: str) -> str:
    if mode == "initial":
        return "".join(run_initial(run["text"]) for run in runs)
    if mode == "last":
        return "".join(run_last(run["text"]) for run in runs)
    if mode == "length_mod10":
        return "".join(str(len(clean_letters(run["text"])) % 10) for run in runs)
    if mode == "letters":
        return "".join(clean_letters(run["text"]) for run in runs)
    raise ValueError(mode)


def instruction_hits(text: str) -> list[str]:
    words = [word.lower().strip("'") for word in clean_words(text)]
    return sorted(set(word for word in words if word in INSTRUCTION_WORDS))


def main() -> None:
    runs = json.loads(RUNS.read_text())
    font_audit = json.loads(FONT_AUDIT.read_text())
    boundaries = font_audit["pageBoundariesByParagraph"]

    enriched = []
    for run in runs:
        item = dict(run)
        item["variant"] = variant(run)
        item["page"] = page_for_paragraph(run["paragraphIndex"], boundaries)
        item["letters"] = clean_letters(run["text"])
        item["letterCount"] = len(item["letters"])
        item["wordInitial"] = run_initial(run["text"])
        item["wordLast"] = run_last(run["text"])
        enriched.append(item)

    typeka_family = [
        run
        for run in enriched
        if run["variant"] in {"TYPEKA", "TYPEKA_BOLD", "MIX", "MIX_BOLD"}
    ]
    non_regular = [
        run
        for run in typeka_family
        if nonblank(run) and run["variant"] in {"TYPEKA_BOLD", "MIX", "MIX_BOLD"}
    ]
    mix_runs = [run for run in typeka_family if nonblank(run) and run["variant"].startswith("MIX")]
    typeka_bold_runs = [
        run for run in typeka_family if nonblank(run) and run["variant"] == "TYPEKA_BOLD"
    ]

    by_variant = defaultdict(list)
    by_page_variant = defaultdict(lambda: defaultdict(list))
    for run in typeka_family:
        by_variant[run["variant"]].append(run)
        if run["page"] is not None:
            by_page_variant[str(run["page"])][run["variant"]].append(run)

    state_codes = {"TYPEKA": "R", "TYPEKA_BOLD": "B", "MIX": "M", "MIX_BOLD": "X"}
    compact_states = []
    last_code = None
    for run in typeka_family:
        if not nonblank(run):
            continue
        code = state_codes.get(run["variant"], "?")
        if code != last_code:
            compact_states.append(code)
            last_code = code
    variant_records = [
        {
            "runIndex": run["runIndex"],
            "page": run["page"],
            "variant": run["variant"],
            "bold": run["bold"],
            "font": run["fontAscii"],
            "highlight": run["highlight"],
            "sizeHalfPoints": run["sizeHalfPoints"],
            "text": run["text"],
            "letters": run["letters"],
            "wordInitial": run["wordInitial"],
            "wordLast": run["wordLast"],
            "letterCount": run["letterCount"],
        }
        for run in non_regular
    ]

    streams = {
        "mixLetters": stream_for(mix_runs, "letters"),
        "mixInitials": stream_for(mix_runs, "initial"),
        "mixLasts": stream_for(mix_runs, "last"),
        "mixLengthMod10": stream_for(mix_runs, "length_mod10"),
        "typekaBoldLetters": stream_for(typeka_bold_runs, "letters"),
        "typekaBoldInitials": stream_for(typeka_bold_runs, "initial"),
        "typekaBoldLasts": stream_for(typeka_bold_runs, "last"),
        "typekaBoldLengthMod10": stream_for(typeka_bold_runs, "length_mod10"),
        "nonRegularInitials": stream_for(non_regular, "initial"),
        "nonRegularLasts": stream_for(non_regular, "last"),
        "nonRegularLengthMod10": stream_for(non_regular, "length_mod10"),
        "compactStateChanges": "".join(compact_states),
    }

    page_summary = {}
    for page, variants in sorted(by_page_variant.items(), key=lambda item: int(item[0])):
        page_summary[page] = {}
        for name, items in sorted(variants.items()):
            page_summary[page][name] = {
                "runs": len(items),
                "nonblankRuns": sum(1 for run in items if nonblank(run)),
                "chars": sum(len(run["text"]) for run in items),
                "letters": sum(run["letterCount"] for run in items),
                "text": "".join(run["text"] for run in items if nonblank(run)),
                "instructionHits": instruction_hits(" ".join(run["text"] for run in items)),
            }

    result = {
        "source": str(RUNS),
        "variantCounts": {
            name: {
                "runs": len(items),
                "nonblankRuns": sum(1 for run in items if nonblank(run)),
                "chars": sum(len(run["text"]) for run in items),
                "letters": sum(run["letterCount"] for run in items),
            }
            for name, items in sorted(by_variant.items())
        },
        "pageSummary": page_summary,
        "streams": streams,
        "streamInstructionHits": {
            key: instruction_hits(value) for key, value in streams.items()
        },
        "variantRecords": variant_records,
        "assessment": [
            "The visually weird partial-bold layer should be modeled as the Typeka Mix font layer, not as manually selected bold letters.",
            "The document metadata has Typeka and Typeka Mix fonts. Typeka-bold appears as a bold run property on Typeka, not as a separate embedded font name.",
            "Typeka Mix is substantial and phrase-like; raw initials/lasts/lengths/state changes do not reveal a readable instruction.",
            "The font-change layer remains active as a possible selector only when combined with page-76 mirror/highlight geometry.",
        ],
    }
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Typeka Variant State Audit",
        "",
        "Scope: reframe the old partial-bold branch around actual Word font states in `Article with Fonts.docm`: Typeka regular, Typeka Mix, and Typeka with bold formatting. No key derivation was run.",
        "",
        "## Variant Counts",
        "",
    ]
    for name, counts in result["variantCounts"].items():
        lines.append(
            f"- `{name}`: runs={counts['runs']}, nonblank={counts['nonblankRuns']}, chars={counts['chars']}, letters={counts['letters']}"
        )

    lines.extend(["", "## Short Streams", ""])
    for key in [
        "mixInitials",
        "mixLasts",
        "mixLengthMod10",
        "typekaBoldInitials",
        "typekaBoldLasts",
        "typekaBoldLengthMod10",
        "nonRegularInitials",
        "nonRegularLasts",
        "nonRegularLengthMod10",
        "compactStateChanges",
    ]:
        value = streams[key]
        preview = value if len(value) <= 220 else value[:220] + "..."
        hits = ", ".join(result["streamInstructionHits"][key]) or "none"
        lines.append(f"- `{key}` len={len(value)} hits={hits}: `{preview}`")

    lines.extend(["", "## Typeka Mix By Page", ""])
    for page, variants in page_summary.items():
        mix = variants.get("MIX", {"runs": 0, "letters": 0, "text": "", "instructionHits": []})
        preview = mix["text"] if len(mix["text"]) <= 420 else mix["text"][:420] + "..."
        hits = ", ".join(mix["instructionHits"]) or "none"
        lines.append(
            f"- p{page}: runs={mix['runs']}, letters={mix['letters']}, instructionHits={hits}, text=`{preview}`"
        )

    lines.extend(["", "## Non-Regular Variant Run Ledger", ""])
    for run in variant_records:
        text = re.sub(r"\s+", " ", run["text"]).strip()
        if not text:
            continue
        lines.append(
            f"- run {run['runIndex']:03d} p{run['page']} `{run['variant']}` bold={run['bold']} "
            f"hl={run['highlight']} size={run['sizeHalfPoints']} len={run['letterCount']}: `{text}`"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The user-supplied interpretation is supported: the old “weird partial bold” observation is mostly a Typeka Mix font-state observation.",
            "- `Article with Fonts.docm` does not expose a separate `Typeka Bold` font name; bold Typeka is represented as a bold formatting property on Typeka runs.",
            "- Typeka Mix by itself is phrase-like and stylistic, not a clean hidden message. Initials, last letters, run lengths, non-regular run order, and compact state changes do not produce a readable instruction.",
            "- This changes priority: stop treating the manual partial-bold stream as hand-selected key letters. Treat Typeka Mix and Typeka-bold as formatting layers that need an external selector, likely the page-76 mirror/highlight system.",
            "- The user-reported comparison that other magazine articles do not use Typeka should be treated as supporting evidence, but the local comparison PDFs are image-only so this script cannot verify font metadata from them.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n")
    print(MD_OUT)
    print(JSON_OUT)


if __name__ == "__main__":
    main()
