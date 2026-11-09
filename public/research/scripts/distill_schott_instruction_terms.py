#!/usr/bin/env python3
"""Distill the linked Schott mirror-writing paper into puzzle-operation concepts.

This is a source-clue interpretation pass, not a key-generation pass. It avoids
long quotations and records only concept counts plus low-parameter implications
for the remaining selector gap.
"""

from __future__ import annotations

import json
import re
import ssl
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/external_clues"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "schott_instruction_distillation.json"
OUT_MD = OUT / "schott_instruction_distillation.md"

URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/"

CONCEPTS = {
    "literal_mirror": [
        r"\bmirror writing\b",
        r"\bmirror\b",
        r"\bopposite direction\b",
        r"\breversed\b",
        r"\breversal\b",
    ],
    "readability_with_mirror": [
        r"\bread with a mirror\b",
        r"\bviewed in a mirror\b",
        r"\bwith a mirror\b",
    ],
    "handedness_left": [
        r"\bleft hand\b",
        r"\bleft-handed\b",
        r"\bleft hander\b",
        r"\bleft-handedness\b",
    ],
    "right_hemisphere": [
        r"\bright hemisphere\b",
        r"\bright cerebral\b",
        r"\bright hemispheric\b",
    ],
    "bimanual": [
        r"\bbimanual\b",
        r"\btwo hands\b",
        r"\bboth hands\b",
        r"\bsimultaneously\b",
    ],
    "corpus_callosum": [
        r"\bcorpus callosum\b",
        r"\bcallosal\b",
    ],
    "leonardo": [
        r"\bleonardo\b",
        r"\bda vinci\b",
    ],
    "neurological": [
        r"\bbrain\b",
        r"\bneurological\b",
        r"\bstroke\b",
        r"\bhemisphere\b",
    ],
}


def fetch_text() -> tuple[str, str]:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except Exception:
        resp = urllib.request.urlopen(req, timeout=30, context=ssl._create_unverified_context())
    html = resp.read().decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find(["h1", "title"])
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{2,}", "\n", text)
    return (title.get_text(" ", strip=True) if title else ""), text


def count_concepts(text: str) -> dict:
    lowered = text.lower()
    results = {}
    for name, patterns in CONCEPTS.items():
        counts = Counter()
        total = 0
        for pat in patterns:
            found = re.findall(pat, lowered, flags=re.I)
            counts[pat] = len(found)
            total += len(found)
        results[name] = {"total": total, "patterns": dict(counts)}
    return results


def keyword_windows(text: str, terms: list[str], limit: int = 4) -> list[str]:
    """Return short non-verbatim context labels, not long quoted source text."""
    compact = re.sub(r"\s+", " ", text)
    windows = []
    for term in terms:
        for match in re.finditer(re.escape(term), compact, flags=re.I):
            start = max(0, match.start() - 45)
            end = min(len(compact), match.end() + 45)
            snippet = compact[start:end].strip()
            # Keep snippets short to avoid copying extended source text.
            words = snippet.split()
            if len(words) > 16:
                snippet = " ".join(words[:16]) + " ..."
            if snippet not in windows:
                windows.append(snippet)
            if len(windows) >= limit:
                return windows
    return windows


def main() -> None:
    title, text = fetch_text()
    counts = count_concepts(text)
    operations = [
        {
            "concept": "literal_mirror",
            "puzzleImplication": "Prefer physical/visual mirror actions and right-to-left reading before cryptographic transformations.",
            "currentStatus": "Direct prose reversal and raw hflip have been tested; they identify regions, not final letters.",
        },
        {
            "concept": "handedness_left / right_hemisphere",
            "puzzleImplication": "A left/right page or left/right side selector remains more plausible than whole-article hashing.",
            "currentStatus": "78/79 as two hands is suggestive but first/last and binary selectors failed.",
        },
        {
            "concept": "bimanual / corpus_callosum",
            "puzzleImplication": "The strongest live geometry should be treated as a crossing/communication rule between pages, not one page alone.",
            "currentStatus": "The p79-yellow -> p76-black row anchor fits this concept but lacks extraction unit/order.",
        },
        {
            "concept": "Leonardo / reversed writing",
            "puzzleImplication": "The clue supports reversing the reading direction, but only after the correct source layer and target region are known.",
            "currentStatus": "Reversing current reflected text streams produced no instruction, so the missing piece is upstream.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "sourceUrl": URL,
        "sourceTitle": title,
        "scope": "concept distillation only; no key derivation",
        "textChars": len(text),
        "conceptCounts": counts,
        "shortContextWindows": {
            "mirror": keyword_windows(text, ["mirror writing", "opposite direction", "with a mirror"]),
            "leftRight": keyword_windows(text, ["left hand", "right hemisphere", "corpus callosum"]),
            "bimanual": keyword_windows(text, ["bimanual", "both hands", "simultaneously"]),
            "leonardo": keyword_windows(text, ["Leonardo"]),
        },
        "operationMap": operations,
        "assessment": [
            "The paper supports mirror/left-right/bimanual concepts, not a named cryptographic transform.",
            "It reinforces the existing page-76 and 76/79 orientation model.",
            "It still does not specify source layer, ordering, or extraction unit.",
            "Future tests should require a fully stated human rule before generating candidates.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Schott Instruction Distillation",
        "",
        "Scope: distill the linked Schott mirror-writing paper into operational concepts for the puzzle. This is not a key-generation pass.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source: `{URL}`",
        f"- Parsed title: `{title}`",
        "",
        "## Concept Counts",
        "",
    ]
    for name, info in sorted(counts.items(), key=lambda item: (-item[1]["total"], item[0])):
        lines.append(f"- `{name}`: `{info['total']}`")

    lines.extend(["", "## Operation Map", ""])
    for op in operations:
        lines.append(f"- `{op['concept']}`: {op['puzzleImplication']} Current status: {op['currentStatus']}")

    lines.extend(["", "## Short Context Checks", ""])
    for name, snippets in result["shortContextWindows"].items():
        lines.append(f"### {name}")
        if snippets:
            for snippet in snippets:
                lines.append(f"- `{snippet}`")
        else:
            lines.append("- none")
        lines.append("")

    lines.extend(["## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "- The clue narrows the style of solution: human visual/physical selection first, cryptography only after a clean selector exists.",
            "- Best next move remains source fidelity: higher-resolution Canva/original layout/physical magazine evidence, or one explicit rule tied to the 76/79 row anchor.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
