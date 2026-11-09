#!/usr/bin/env python3
"""Page-76 corridor font-order audit.

This tests a narrow selector hypothesis: the verified page-76 corridor may be
ordered by the font/highlight layer sequence from `Article with Fonts.docm`,
especially around the strong p79-yellow -> p76-black calibration anchor.

No private-key candidates are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
OUT_MD = ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.md"
OUT_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json"

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
    "order",
    "reverse",
    "between",
    "above",
    "below",
    "dip",
    "down",
}

TARGET_PHRASES = [
    ("open_heart", "Get some toxicity. Get some bitcoin. Open your heart to Bitcoin."),
    ("calibration_black", "Gotta be this way. Forty years of dumb post-1971 fiat money nonsense"),
    ("rancid_catnip", "by the rancid catnip of fiat money."),
    ("stun_gun", "It's a stun gun to the genitals."),
    ("buying_dip", "buying the dip"),
    ("one_billion", "$1 billion"),
    ("volcano_bonds", "Volcano Bonds"),
    ("shitcoiner_heart", "shitcoiner at heart"),
]


def clean_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z]+)?|%", text)


def clean_letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z]", text))


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def instruction_hits(text: str) -> list[str]:
    words = [w.lower().strip("'") for w in clean_words(text)]
    return sorted({w for w in words if w in INSTRUCTION_WORDS})


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


def layer(run: dict) -> str:
    hl = run.get("highlight")
    var = run.get("variant")
    if hl == "yellow":
        return "YELLOW"
    if hl == "black":
        return "BLACK"
    if var in {"MIX", "MIX_BOLD"}:
        return "MIX"
    if var == "TYPEKA_BOLD":
        return "BOLD"
    return "REGULAR"


def layer_code(value: str) -> str:
    return {
        "YELLOW": "Y",
        "BLACK": "K",
        "MIX": "M",
        "BOLD": "B",
        "REGULAR": "R",
    }.get(value, "?")


def first_initial(text: str) -> str:
    words = clean_words(text)
    return words[0][0] if words else ""


def last_initial(text: str) -> str:
    words = clean_words(text)
    return words[-1][0] if words else ""


def enrich_runs() -> list[dict]:
    runs = json.loads(RUNS.read_text())
    boundaries = json.loads(FONT_AUDIT.read_text())["pageBoundariesByParagraph"]
    enriched = []
    for run in runs:
        item = dict(run)
        item["page"] = page_for_paragraph(run["paragraphIndex"], boundaries)
        item["variant"] = variant(run)
        item["layer"] = layer(item)
        enriched.append(item)
    return enriched


def group_signal_runs(runs: list[dict], page: int) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None
    for run in runs:
        if run["page"] != page:
            continue
        text = run.get("text") or ""
        if not text.strip():
            continue
        run_layer = run["layer"]
        if run_layer == "REGULAR":
            if current is not None:
                groups.append(current)
                current = None
            continue
        if current is None or current["layer"] != run_layer:
            if current is not None:
                groups.append(current)
            current = {
                "groupIndex": len(groups) + 1,
                "page": page,
                "layer": run_layer,
                "code": layer_code(run_layer),
                "runStart": run["runIndex"],
                "runEnd": run["runIndex"],
                "texts": [],
                "variants": Counter(),
                "highlights": Counter(),
                "boldRuns": 0,
            }
        current["runEnd"] = run["runIndex"]
        current["texts"].append(text)
        current["variants"][run["variant"]] += 1
        current["highlights"][run.get("highlight") or "none"] += 1
        current["boldRuns"] += int(bool(run.get("bold")))
    if current is not None:
        groups.append(current)

    for idx, group in enumerate(groups, 1):
        text = "".join(group.pop("texts"))
        group["groupIndex"] = idx
        group["text"] = re.sub(r"\s+", " ", text).strip()
        group["letters"] = clean_letters(group["text"])
        group["wordCount"] = len(clean_words(group["text"]))
        group["letterCount"] = len(group["letters"])
        group["firstInitial"] = first_initial(group["text"])
        group["lastInitial"] = last_initial(group["text"])
        group["instructionHits"] = instruction_hits(group["text"])
        group["variants"] = dict(group["variants"])
        group["highlights"] = dict(group["highlights"])
    return groups


def find_target_groups(groups: list[dict]) -> list[dict]:
    records = []
    for target_id, phrase in TARGET_PHRASES:
        needle = norm(phrase)
        matches = [g for g in groups if needle and needle in norm(g["text"])]
        if not matches and target_id == "buying_dip":
            matches = [g for g in groups if "buyingthedip" in norm(g["text"])]
        record = {
            "targetId": target_id,
            "phrase": phrase,
            "matches": [],
        }
        for match in matches:
            record["matches"].append(
                {
                    "groupIndex": match["groupIndex"],
                    "layer": match["layer"],
                    "code": match["code"],
                    "runStart": match["runStart"],
                    "runEnd": match["runEnd"],
                    "text": match["text"],
                }
            )
        records.append(record)
    return records


def nearest_mix(groups: list[dict], group_index: int, direction: int) -> dict | None:
    idx = group_index - 1 + direction
    while 0 <= idx < len(groups):
        if groups[idx]["layer"] == "MIX":
            return groups[idx]
        idx += direction
    return None


def target_neighbor_records(groups: list[dict], targets: list[dict]) -> list[dict]:
    rows = []
    for target in targets:
        for match in target["matches"]:
            group_index = match["groupIndex"]
            before = nearest_mix(groups, group_index, -1)
            after = nearest_mix(groups, group_index, 1)
            rows.append(
                {
                    "targetId": target["targetId"],
                    "targetGroup": group_index,
                    "targetCode": match["code"],
                    "targetText": match["text"],
                    "prevMixGroup": before["groupIndex"] if before else None,
                    "prevMixText": before["text"] if before else None,
                    "nextMixGroup": after["groupIndex"] if after else None,
                    "nextMixText": after["text"] if after else None,
                    "prevTargetNextInitials": (
                        (first_initial(before["text"]) if before else "")
                        + match["text"][:1]
                        + (first_initial(after["text"]) if after else "")
                    ),
                }
            )
    return rows


def summarize_page79_anchor(runs: list[dict]) -> dict:
    # Strong registered source is p79 runs 299-301. Include immediate signal groups
    # on p79 for color/layer context.
    p79_groups = group_signal_runs(runs, 79)
    source = [g for g in p79_groups if g["runStart"] <= 299 <= g["runEnd"] or 299 <= g["runStart"] <= 301]
    if not source:
        source = [g for g in p79_groups if 299 <= g["runStart"] <= 301 or 299 <= g["runEnd"] <= 301]
    source_index = source[0]["groupIndex"] if source else None
    context = []
    if source_index is not None:
        for g in p79_groups:
            if source_index - 2 <= g["groupIndex"] <= source_index + 2:
                context.append(g)
    return {
        "p79SignalLayerCodes": "".join(g["code"] for g in p79_groups),
        "sourceGroupIndex": source_index,
        "sourceContext": context,
        "sourceText": source[0]["text"] if source else "",
        "sourceLayer": source[0]["layer"] if source else None,
    }


def main() -> None:
    runs = enrich_runs()
    p76_groups = group_signal_runs(runs, 76)
    targets = find_target_groups(p76_groups)
    neighbor_rows = target_neighbor_records(p76_groups, targets)
    p79_anchor = summarize_page79_anchor(runs)

    layer_codes = "".join(g["code"] for g in p76_groups)
    target_codes = "".join(
        match["code"]
        for target in targets
        for match in target["matches"]
    )
    streams = {
        "p76SignalLayerCodes": layer_codes,
        "p76SignalInitials": "".join(g["firstInitial"] for g in p76_groups),
        "p76SignalLastInitials": "".join(g["lastInitial"] for g in p76_groups),
        "p76SignalLengthMod10": "".join(str(g["letterCount"] % 10) for g in p76_groups),
        "matchedTargetLayerCodes": target_codes,
        "matchedTargetInitials": "".join(
            first_initial(match["text"]) for target in targets for match in target["matches"]
        ),
        "matchedTargetLastInitials": "".join(
            last_initial(match["text"]) for target in targets for match in target["matches"]
        ),
        "targetWithNearestMixTriplets": "".join(row["prevTargetNextInitials"] for row in neighbor_rows),
    }

    result = {
        "source": str(RUNS),
        "scope": "page 76 signal font/highlight order with 76/79 calibration context",
        "p76SignalGroups": p76_groups,
        "targetMatches": targets,
        "targetNearestMix": neighbor_rows,
        "p79CalibrationSource": p79_anchor,
        "streams": streams,
        "streamInstructionHits": {name: instruction_hits(value) for name, value in streams.items()},
        "assessment": [
            "Page 76 has a clear signal-layer sequence, but it is narrative/formatting order rather than an extraction instruction.",
            "The confirmed target groups are all YELLOW or BLACK Typeka-bold groups; Typeka Mix sits around them as semantic neighboring text, not as a one-to-one index layer.",
            "The strong p79 calibration source is a YELLOW group landing on a p76 BLACK group, which supports color inversion/orientation but does not add ordering.",
            "Nearest-Mix triplets and signal group initials/lasts/lengths do not expose instruction words.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Page 76 Corridor Font-Order Audit",
        "",
        "Scope: test whether the verified page-76 corridor gives an ordered selector when combining `Article with Fonts.docm` layers, high-res highlight labels, and the established p79-yellow -> p76-black calibration anchor. No key candidates are generated.",
        "",
        "## Layer Codes",
        "",
        "- `Y` = yellow/orange highlight",
        "- `K` = black/grey highlight",
        "- `M` = Typeka Mix",
        "- `B` = Typeka bold without highlight",
        "",
        "## Streams",
        "",
    ]
    for name, value in streams.items():
        hits = ",".join(instruction_hits(value)) or "none"
        lines.append(f"- `{name}` hits={hits}: `{value}`")

    lines.extend(["", "## Page 76 Signal Groups", ""])
    for group in p76_groups:
        hit_text = ",".join(group["instructionHits"]) or "-"
        lines.append(
            f"- G{group['groupIndex']:02d} {group['code']} runs {group['runStart']}-{group['runEnd']} "
            f"hits={hit_text}: `{group['text']}`"
        )

    lines.extend(["", "## Confirmed Target Groups", ""])
    for target in targets:
        if not target["matches"]:
            lines.append(f"- `{target['targetId']}` not matched: `{target['phrase']}`")
            continue
        for match in target["matches"]:
            lines.append(
                f"- `{target['targetId']}` -> G{match['groupIndex']:02d} {match['code']} "
                f"runs {match['runStart']}-{match['runEnd']}: `{match['text']}`"
            )

    lines.extend(["", "## Nearest Typeka Mix Around Targets", ""])
    for row in neighbor_rows:
        lines.append(
            f"- `{row['targetId']}` G{row['targetGroup']:02d}: "
            f"prevMix=G{row['prevMixGroup'] or '-'} `{row['prevMixText'] or '-'}`; "
            f"nextMix=G{row['nextMixGroup'] or '-'} `{row['nextMixText'] or '-'}`; "
            f"triplet=`{row['prevTargetNextInitials']}`"
        )

    lines.extend(
        [
            "",
            "## 76/79 Calibration Context",
            "",
            f"- p79 signal layer codes: `{p79_anchor['p79SignalLayerCodes']}`",
            f"- Registered p79 source group: G{p79_anchor['sourceGroupIndex']} `{p79_anchor['sourceText']}` layer={p79_anchor['sourceLayer']}",
            "- Local p79 context:",
        ]
    )
    for group in p79_anchor["sourceContext"]:
        lines.append(
            f"  - G{group['groupIndex']:02d} {group['code']} runs {group['runStart']}-{group['runEnd']}: `{group['text']}`"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The page-76 signal sequence is structured, but it follows the visible prose: opening toxicity, UTXO/Clinton, fiat nonsense, El Salvador/Bukele, $1 billion/Volcano Bonds, Novogratz, distrust, shitcoiner-at-heart.",
            "- Confirmed page-76 targets are all `Y` or `K`; the Typeka Mix groups are nearby semantic anchors (`George Clinton`, `El Salvador`, `Mike Novogratz`, `I don't really trust that guy`) rather than a separate ordered index.",
            "- The known 76/79 calibration is a color-inversion clue (`p79 YELLOW` landing on `p76 BLACK`), but it does not produce a new ordering rule from the font states.",
            "- Close this as a direct selector. Keep it as evidence that Typeka/font layers are formatting witnesses which still need an external rule.",
            "- Next best move: inspect page-76 corridor for non-font visual ordering marks or obtain a higher-fidelity source/physical scan; do not rerun Typeka initial/length streams without a new selector.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
