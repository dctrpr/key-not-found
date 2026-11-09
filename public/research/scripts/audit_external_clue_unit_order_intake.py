#!/usr/bin/env python3
"""Strictly score archived external clue wording for extraction unit/order.

Prior reports scanned broad external/provenance folders and found many terms,
but much of that text is our own analysis prose. This pass separates raw-ish
clue wording from derived report language and asks only whether the local
archive contains a source-backed unit/order instruction that can satisfy R3.

No article extraction, hashing, key derivation, seed/WIF checks, address checks,
or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/external_clues/external_clue_unit_order_intake"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "external_clue_unit_order_intake.json"
OUT_MD = OUT / "external_clue_unit_order_intake.md"

PATHS = {
    "original_clue": ROOT / "analysis_outputs/external_clues/original_clue_provenance.json",
    "source_inventory": ROOT / "analysis_outputs/external_clues/source_clue_inventory.json",
    "instruction_frontier": ROOT / "analysis_outputs/external_clues/external_instruction_term_frontier/external_instruction_term_frontier.json",
    "schott": ROOT / "analysis_outputs/external_clues/schott_instruction_distillation.json",
    "announcement_media_order": ROOT / "analysis_outputs/external_clues/announcement_media_order_selector/announcement_media_order_selector.json",
    "canva_live": ROOT / "analysis_outputs/external_clues/canva_live_recheck/canva_live_recheck.json",
    "canva_surface": ROOT / "analysis_outputs/source_audit/canva_live_clue_surface/canva_live_clue_surface.json",
    "public_index": ROOT / "analysis_outputs/source_audit/public_clue_index_selector/public_clue_index_selector.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

UNIT_TERMS = {
    "word",
    "words",
    "letter",
    "letters",
    "character",
    "characters",
    "line",
    "lines",
    "edge",
    "edges",
    "font",
    "fonts",
    "first",
    "last",
    "left",
    "right",
    "above",
    "below",
    "inside",
    "outside",
    "read",
    "take",
    "select",
    "count",
    "order",
    "reverse",
    "backward",
    "index",
    "indices",
}
TARGET_TERMS = {
    "page 76",
    "p76",
    "bukele",
    "el salvador",
    "volcano",
    "volcano bonds",
    "imf",
    "buying the dip",
    "$1 billion",
    "shitcoiner",
    "heart",
    "o5",
    "g5",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def html_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = re.sub(r"&mdash;|&amp;|&quot;|&#39;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def hits(text: str, terms: set[str]) -> list[str]:
    low = text.lower()
    found = []
    for term in sorted(terms, key=lambda t: (len(t.split()), len(t)), reverse=True):
        if re.search(r"(?<![a-z0-9#])" + re.escape(term.lower()) + r"(?![a-z0-9])", low):
            found.append(term)
    return found


def context_class(text: str, unit_hits: list[str], target_hits: list[str]) -> tuple[str, str]:
    low = text.lower()
    if not unit_hits:
        return "no_unit_order", "No unit/order term appears in the raw text."
    if "line" in unit_hits or "lines" in unit_hits:
        if "line up" in low or "in line with" in low or "line with" in low:
            return "orientation_not_extraction", "`line` appears in geometric/orientation language, not as a line-index instruction."
    if any(term in unit_hits for term in ["word", "words", "letter", "letters", "character", "characters", "edge", "font", "fonts"]):
        if target_hits:
            return "candidate_unit_order", "Unit term appears with target terms; would need source/raw confirmation."
        return "unit_without_target", "Unit term exists but is not tied to active page-76 target terms."
    if any(term in unit_hits for term in ["left", "right", "reverse", "backward", "read"]):
        if "mirror" in low or "mirror writing" in low:
            return "operation_family_only", "Mirror/reversal language gives operation family, not extraction unit/order."
    if target_hits:
        return "targeting_not_extraction", "The text reinforces target/corridor but does not name a unit."
    return "non_actionable_unit", "Unit-like term is not enough to extract."


def raw_records(data: dict) -> list[dict]:
    original = data["original_clue"]
    source_inventory = data["source_inventory"]
    schott = data["schott"]
    media = data["announcement_media_order"]
    canva = data["canva_live"] or data["canva_surface"]

    records: list[dict] = []

    tweets = original.get("tweets", {})
    for name, row in tweets.items():
        html = row.get("oembed", {}).get("json", {}).get("html", "")
        text = html_text(html)
        # Strip author/date tail if possible, but retain the quote text.
        text = re.sub(r"\s+Max Keiser.*$", "", text).strip()
        records.append(
            {
                "id": f"tweet_{name}",
                "sourceType": "raw_oembed_tweet",
                "text": text,
                "source": row.get("url"),
                "rawness": "raw",
            }
        )

    announcement = source_inventory.get("announcement_text")
    if announcement:
        records.append(
            {
                "id": "announcement_text_inventory",
                "sourceType": "archived_raw_announcement_text",
                "text": announcement,
                "source": rel(PATHS["source_inventory"]),
                "rawness": "raw",
            }
        )

    title = schott.get("sourceTitle")
    if title:
        records.append(
            {
                "id": "schott_title",
                "sourceType": "linked_paper_title",
                "text": title,
                "source": schott.get("sourceUrl"),
                "rawness": "raw_linked_title",
            }
        )
    for item in schott.get("operationMap", []) if isinstance(schott.get("operationMap"), list) else []:
        records.append(
            {
                "id": f"schott_operation_{item.get('concept')}",
                "sourceType": "derived_schott_distillation",
                "text": item.get("status", "") + " " + item.get("rule", "") + " " + item.get("currentStatus", ""),
                "source": rel(PATHS["schott"]),
                "rawness": "derived",
            }
        )

    canva_text = canva.get("connectorText") or canva.get("richtext")
    if canva_text:
        records.append(
            {
                "id": "canva_live_text",
                "sourceType": "live_canva_text",
                "text": canva_text,
                "source": rel(PATHS["canva_live"] if data["canva_live"] else PATHS["canva_surface"]),
                "rawness": "source_adjacent",
            }
        )

    for row in media.get("media", []):
        text = " ".join([row.get("subject", ""), " ".join(row.get("tags", [])), " ".join(row.get("matchedUnits", []))])
        records.append(
            {
                "id": f"announcement_media_{row.get('order')}",
                "sourceType": "manual_media_subject_mapping",
                "text": text,
                "source": rel(PATHS["announcement_media_order"]),
                "rawness": "derived_visual_label",
            }
        )

    return records


def main() -> None:
    data = {name: load(path) for name, path in PATHS.items()}
    records = []
    for rec in raw_records(data):
        unit = hits(rec["text"], UNIT_TERMS)
        target = hits(rec["text"], TARGET_TERMS)
        status, reason = context_class(rec["text"], unit, target)
        rec.update(
            {
                "unitHits": unit,
                "targetHits": target,
                "r3Status": "PASS" if status == "candidate_unit_order" else "FAIL",
                "classification": status,
                "reason": reason,
            }
        )
        records.append(rec)

    raw_like = [r for r in records if r["rawness"] in {"raw", "raw_linked_title", "source_adjacent"}]
    raw_pass = [r for r in raw_like if r["r3Status"] == "PASS"]
    derived_pass = [r for r in records if r["rawness"].startswith("derived") and r["r3Status"] == "PASS"]

    frontier = data["instruction_frontier"]
    contamination_note = {
        "filesScanned": frontier.get("filesScanned"),
        "rawishNonInternalCooccurrenceCount": frontier.get("rawishNonInternalCooccurrenceCount"),
        "actionableRawishCooccurrenceCount": frontier.get("actionableRawishCooccurrenceCount"),
        "reason": "Earlier co-occurrence counts include report prose. This intake treats only raw/raw-like clue text as eligible R3 evidence.",
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "strict external clue unit/order intake; no extraction or key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in PATHS.items()},
        "records": records,
        "rawLikeRecordCount": len(raw_like),
        "rawLikeR3PassCount": len(raw_pass),
        "derivedR3PassCount": len(derived_pass),
        "contaminationNote": contamination_note,
        "publicIndexSelectorAssessment": data["public_index"].get("assessment"),
        "decision": "no_archived_raw_external_clue_names_extraction_unit_order",
        "nextMove": "Keep archived clues as constraints: source piece, private Bitcoin key, mirror-writing operation family, page-76/Bukele/volcano target confirmation, and Canva source-registration gaps. Reopen only with new raw clue/provenance wording or new physical/original-layout source evidence.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# External Clue Unit/Order Intake",
        "",
        "Scope: separate raw/raw-like external clue wording from derived report prose and test whether any archived clue satisfies R3 by naming the extraction unit/order. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Raw/raw-like records: `{result['rawLikeRecordCount']}`",
        f"- Raw/raw-like R3 passes: `{result['rawLikeR3PassCount']}`",
        f"- Derived R3 passes: `{result['derivedR3PassCount']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Raw / Raw-Like Records",
        "",
        "| id | rawness | unit hits | target hits | classification | R3 | reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for rec in records:
        if rec["rawness"] not in {"raw", "raw_linked_title", "source_adjacent"}:
            continue
        lines.append(
            f"| `{rec['id']}` | `{rec['rawness']}` | `{', '.join(rec['unitHits']) or '-'}` | `{', '.join(rec['targetHits']) or '-'}` | `{rec['classification']}` | `{rec['r3Status']}` | {rec['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Derived / Manual Labels",
            "",
            "| id | rawness | unit hits | target hits | classification | use |",
            "|---|---|---|---|---|---|",
        ]
    )
    for rec in records:
        if rec["rawness"] in {"raw", "raw_linked_title", "source_adjacent"}:
            continue
        lines.append(
            f"| `{rec['id']}` | `{rec['rawness']}` | `{', '.join(rec['unitHits']) or '-'}` | `{', '.join(rec['targetHits']) or '-'}` | `{rec['classification']}` | target/provenance only |"
        )

    lines.extend(
        [
            "",
            "## Contamination Check",
            "",
            f"- Earlier external term frontier scanned `{contamination_note['filesScanned']}` files and found `{contamination_note['actionableRawishCooccurrenceCount']}` actionable raw-ish co-occurrence, but that hit was the Canva orientation/source-fidelity note rather than an extraction unit/order.",
            "- Terms like `word`, `letter`, `read`, and `select` inside our generated reports are not eligible source evidence.",
            "- The public clue index selector is already closed as a standalone selector; its direct index streams selected ordinary article words and no procedural language.",
            "",
            "## Decision",
            "",
            "- Archived raw clue text says: private Bitcoin key, encoded, this piece, Mr. President, 20 BTC.",
            "- The Schott link says mirror writing and supports mirror/reversal/left-right concepts.",
            "- The Canva note says pills/XX/barbed-wire/SHIT spills are orientation/positioning/source-fidelity clues.",
            "- None names a source-backed unit/order such as take word N, read line X, select letters, use font state, first/last, edge, or similar.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("decision:", result["decision"])
    print("rawLikeR3PassCount:", result["rawLikeR3PassCount"])


if __name__ == "__main__":
    main()
