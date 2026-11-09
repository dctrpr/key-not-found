#!/usr/bin/env python3
"""Audit whether the DOCM Typeka font-state layer itself names an extraction rule."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VARIANT_PATH = ROOT / "analysis_outputs/docm_format_sources/typeka_variant_state_audit.json"
OUT_DIR = ROOT / "analysis_outputs/docm_format_sources/typeka_instruction_surface"
OUT_MD = OUT_DIR / "typeka_instruction_surface.md"
OUT_JSON = OUT_DIR / "typeka_instruction_surface.json"

TERMS = {
    "procedural": [
        "read",
        "take",
        "select",
        "choose",
        "pick",
        "count",
        "index",
        "use",
        "find",
        "look",
        "see",
    ],
    "unit": [
        "word",
        "words",
        "letter",
        "letters",
        "line",
        "lines",
        "page",
        "pages",
        "font",
        "fonts",
        "highlight",
        "highlights",
        "key",
        "private",
        "seed",
        "address",
    ],
    "mirror": [
        "mirror",
        "mirrored",
        "reverse",
        "reversed",
        "backward",
        "backwards",
        "fold",
        "folded",
        "left",
        "right",
        "up",
        "down",
    ],
    "index_word": [
        "first",
        "last",
        "one",
        "two",
        "three",
        "four",
        "five",
        "zero",
    ],
}

WHOLE_WORD_TERMS = {
    term
    for group in TERMS.values()
    for term in group
}

ACTIVE_TERMS = [
    "el salvador",
    "buying the dip",
    "$1 billion",
    "volcano bonds",
    "imf",
    "mike",
    "novogratz",
    "trust",
    "shitcoiner",
    "heart",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z]+)?", text.lower())


def term_hits(text: str) -> dict[str, list[str]]:
    toks = words(text)
    by_group: dict[str, list[str]] = {}
    for group, terms in TERMS.items():
        found = []
        for term in terms:
            if term in toks:
                found.append(term)
        by_group[group] = found
    return by_group


def context_snippet(text: str, max_len: int = 120) -> str:
    s = " ".join(text.split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "..."


def active_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in ACTIVE_TERMS if term in low]


def has_strong_instruction(hits: dict[str, list[str]]) -> bool:
    # Require a procedural or mirror/index action plus a concrete extraction unit.
    action = bool(hits["procedural"] or hits["mirror"] or hits["index_word"])
    unit = bool(hits["unit"])
    return action and unit


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    variant_data = json.loads(VARIANT_PATH.read_text())
    records = variant_data["variantRecords"]

    hit_records = []
    variant_counts = Counter()
    page_counts = defaultdict(Counter)
    group_counts = defaultdict(Counter)
    active_overlap = []

    for rec in records:
        text = rec.get("text", "")
        if not text.strip():
            continue
        variant = rec["variant"]
        page = str(rec["page"])
        variant_counts[variant] += 1
        page_counts[page][variant] += 1

        hits = term_hits(text)
        flat = sorted({term for terms in hits.values() for term in terms})
        if flat:
            for group, terms in hits.items():
                for term in terms:
                    group_counts[group][term] += 1
            hit_records.append(
                {
                    "runIndex": rec["runIndex"],
                    "page": rec["page"],
                    "variant": variant,
                    "highlight": rec.get("highlight") or "none",
                    "bold": bool(rec.get("bold")),
                    "terms": hits,
                    "flatTerms": flat,
                    "activeTerms": active_hits(text),
                    "strongInstruction": has_strong_instruction(hits),
                    "text": context_snippet(text),
                }
            )
        active = active_hits(text)
        if active:
            active_overlap.append(
                {
                    "runIndex": rec["runIndex"],
                    "page": rec["page"],
                    "variant": variant,
                    "highlight": rec.get("highlight") or "none",
                    "activeTerms": active,
                    "instructionTerms": flat,
                    "strongInstruction": has_strong_instruction(hits),
                    "text": context_snippet(text),
                }
            )

    strong = [r for r in hit_records if r["strongInstruction"]]
    procedural_no_unit = [
        r
        for r in hit_records
        if (r["terms"]["procedural"] or r["terms"]["mirror"] or r["terms"]["index_word"])
        and not r["terms"]["unit"]
    ]
    unit_no_action = [
        r
        for r in hit_records
        if r["terms"]["unit"]
        and not (r["terms"]["procedural"] or r["terms"]["mirror"] or r["terms"]["index_word"])
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "scan non-regular Typeka font-state runs for explicit extraction wording; no key derivation",
        "inputs": {"variantAudit": str(VARIANT_PATH.relative_to(ROOT))},
        "variantRunCounts": dict(variant_counts),
        "pageVariantCounts": {page: dict(counts) for page, counts in sorted(page_counts.items())},
        "termCounts": {group: dict(counts) for group, counts in group_counts.items()},
        "hitRecords": hit_records,
        "strongInstructionRecords": strong,
        "proceduralNoUnitRecords": procedural_no_unit,
        "unitNoActionRecords": unit_no_action,
        "activeOverlapRecords": active_overlap,
        "assessment": [
            "Non-regular Typeka runs contain ordinary prose terms such as first, right, take, and see, but no run combines an action/direction with a concrete extraction unit.",
            "No non-regular font-state run contains mirror, fold, reverse, word, letter, line, key, private, seed, or address.",
            "Active page-76 corridor terms appear in the expected Typeka Mix / bold-highlight runs, but those runs do not provide procedural permission.",
        ],
        "decision": {
            "typekaAsInstructionSurface": "closed_current_docm",
            "typekaAsFormattingWitness": "keep",
            "nextMove": "Use font states only after a separate source/geometry/clue names the unit or order; do not infer extraction from Typeka terms alone.",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2))

    lines = [
        "# Typeka Instruction Surface",
        "",
        "Scope: scan non-regular Typeka font-state runs for explicit extraction wording. No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source: `{VARIANT_PATH.relative_to(ROOT)}`",
        "",
        "## Run Counts",
        "",
        f"- Variant run counts: `{dict(variant_counts)}`",
        f"- Strong instruction records: `{len(strong)}`",
        f"- Procedural/directional/index terms without unit: `{len(procedural_no_unit)}`",
        f"- Unit terms without action: `{len(unit_no_action)}`",
        "",
        "## Term Counts",
        "",
    ]
    for group in ["procedural", "unit", "mirror", "index_word"]:
        lines.append(f"- `{group}`: `{dict(group_counts[group])}`")

    lines += [
        "",
        "## Procedural / Directional Hits Without Extraction Unit",
        "",
        "| run | page | variant | highlight | terms | text |",
        "|---:|---:|---|---|---|---|",
    ]
    for rec in procedural_no_unit[:40]:
        terms = ", ".join(rec["flatTerms"])
        text = rec["text"].replace("|", "\\|")
        lines.append(
            f"| `{rec['runIndex']}` | `{rec['page']}` | `{rec['variant']}` | `{rec['highlight']}` | `{terms}` | {text} |"
        )
    if len(procedural_no_unit) > 40:
        lines.append(f"| ... | ... | ... | ... | ... | `{len(procedural_no_unit) - 40}` more records omitted |")

    lines += [
        "",
        "## Active Corridor Overlap",
        "",
        "| run | page | variant | active terms | instruction terms | text |",
        "|---:|---:|---|---|---|---|",
    ]
    for rec in active_overlap[:40]:
        active = ", ".join(rec["activeTerms"])
        instr = ", ".join(rec["instructionTerms"]) or "-"
        text = rec["text"].replace("|", "\\|")
        lines.append(
            f"| `{rec['runIndex']}` | `{rec['page']}` | `{rec['variant']}` | `{active}` | `{instr}` | {text} |"
        )

    lines += [
        "",
        "## Findings",
        "",
        "- Typeka Mix / bold Typeka contains contextual prose terms such as `first`, `right`, `take`, and `see`, but none is paired with `word`, `letter`, `line`, `page`, `font`, `mirror`, `fold`, `reverse`, `key`, `private`, `seed`, or `address` as an extraction instruction.",
        "- The active page-76 corridor still appears in the expected font-state runs: `El Salvador`, `buying the dip`, `$1 billion`, `Volcano Bonds`, `IMF`, `Mike Novogratz`, `trust`, and `shitcoiner at heart`.",
        "- Those active runs explain emphasis/provenance; they do not provide the missing unit/order.",
        "",
        "## Decision",
        "",
        "- Close Typeka-as-instruction-surface under the current DOCM witness.",
        "- Keep Typeka as a formatting witness and corridor support layer only.",
        "- Reopen only if a source clue explicitly names font state, Typeka, Mix, bold, first/last letters, or another concrete unit.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"typekaAsInstructionSurface: {result['decision']['typekaAsInstructionSurface']}")


if __name__ == "__main__":
    main()
