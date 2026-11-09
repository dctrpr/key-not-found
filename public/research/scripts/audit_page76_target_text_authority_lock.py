#!/usr/bin/env python3
"""Lock the authoritative text witnesses for the page-76 target corridor.

This pass checks the exact target phrases used by the future-source packet
against the corrected canonical text, DOCM text, raw user plain text, and the
Markdown/annotated transcript witnesses. It does not run extraction, hashing,
key derivation, WIF/Base58 scans, OCR, or address checks.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_target_text_authority_lock.json"
OUT_MD = OUT / "page76_target_text_authority_lock.md"
SHEET = OUT / "page76_target_text_authority_lock_sheet.jpg"

SOURCES = {
    "canonical_plain": {
        "path": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
        "role": "corrected canonical plain text",
        "authoritative": True,
    },
    "docm_text": {
        "path": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_text.txt",
        "role": "Article with Fonts DOCM text witness",
        "authoritative": True,
    },
    "user_raw_plain": {
        "path": ROOT / "analysis_outputs/plain_text_transcript/user_plain_article_latest.txt",
        "role": "latest raw user plain-text paste",
        "authoritative": False,
    },
    "markdown_transcript": {
        "path": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
        "role": "Markdown bold/highlight transcript witness",
        "authoritative": True,
    },
    "annotated_transcript": {
        "path": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
        "role": "annotated format witness; inline notes can interrupt exact prose",
        "authoritative": False,
    },
}

JSON_INPUTS = {
    "correction_report": ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
    "active_corridor_witness": ROOT / "analysis_outputs/plain_text_transcript/active_corridor_witness_consistency/active_corridor_witness_consistency.json",
    "active_line_reconciliation": ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json",
    "source_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
}

TARGETS = [
    {"id": "buying_dip", "phrase": "buying the dip", "role": "O4 orange target"},
    {"id": "one_billion", "phrase": "$1 billion", "role": "B4 grey target"},
    {"id": "should_sell", "phrase": "should sell", "role": "p78-frame top edge phrase"},
    {"id": "future_bitcoin_earnings", "phrase": "future bitcoin earnings", "role": "source-band phrase"},
    {"id": "volcano_bonds", "phrase": "Volcano Bonds", "role": "G5 trusted target"},
    {"id": "imf_loan", "phrase": "IMF loan", "role": "G5 neighbor"},
    {"id": "tagged_mike", "phrase": "I tagged Mike", "role": "source-band phrase"},
    {"id": "novogratz", "phrase": "Novogratz", "role": "source-band phrase"},
    {"id": "trust_that_guy", "phrase": "I don't really trust that guy", "role": "nearby Typeka Mix phrase"},
    {"id": "shitcoiner_heart", "phrase": "shitcoiner at heart", "role": "O5 primary target"},
]


def load_json(path: Path) -> dict[str, Any]:
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


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def normalize(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("\\", "")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def snippet(norm_text: str, norm_phrase: str, radius: int = 86) -> str | None:
    idx = norm_text.find(norm_phrase)
    if idx < 0:
        return None
    start = max(0, idx - radius)
    end = min(len(norm_text), idx + len(norm_phrase) + radius)
    return norm_text[start:end]


def build_sheet(source_rows: list[dict[str, Any]], correction_summary: dict[str, Any]) -> None:
    sheet_w = 1420
    margin = 28
    title_h = 92
    row_h = 40
    table_h = 38 + row_h * len(source_rows)
    summary_h = 120
    sheet_h = margin * 2 + title_h + table_h + summary_h
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, margin), "Page-76 Target Text Authority Lock", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 44),
        "Checks target phrase stability across canonical/DOCM/raw/Markdown/annotated witnesses.",
        fill=(174, 184, 196),
        font=normal,
    )

    y = margin + title_h
    draw.rectangle((margin, y, sheet_w - margin, y + 32), fill=(29, 34, 42))
    headers = [("source", 12), ("authoritative", 330), ("present", 470), ("missing", 590), ("note", 720)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 8), label, fill=(236, 241, 247), font=small)
    y += 36

    for row in source_rows:
        ok = row["missingCount"] == 0
        fill = (18, 23, 28) if ok else (45, 25, 25)
        draw.rectangle((margin, y, sheet_w - margin, y + row_h - 5), fill=fill, outline=(38, 46, 56))
        draw.text((margin + 12, y + 10), row["id"], fill=(224, 232, 240), font=mono)
        draw.text((margin + 330, y + 10), str(row["authoritative"]), fill=(174, 184, 196), font=small)
        draw.text((margin + 470, y + 10), str(row["presentCount"]), fill=(113, 222, 154), font=mono)
        draw.text((margin + 590, y + 10), str(row["missingCount"]), fill=(255, 123, 123) if row["missingCount"] else (113, 222, 154), font=mono)
        note = "; ".join(row["missing"]) if row["missing"] else "all target phrases present"
        draw.text((margin + 720, y + 10), note[:82], fill=(174, 184, 196), font=small)
        y += row_h

    y += 20
    draw.rectangle((margin, y, sheet_w - margin, y + 86), fill=(37, 30, 18), outline=(90, 70, 32))
    summary = (
        f"Active-corridor corrections: {correction_summary.get('activeCorridorCorrectionCount')}; "
        f"selector-permission corrections: {correction_summary.get('selectorPermissionCorrectionCount')}; "
        "use canonical/DOCM/Markdown/annotated witnesses for page-76 target wording."
    )
    draw.text((margin + 12, y + 14), summary, fill=(255, 218, 135), font=normal)
    draw.text(
        (margin + 12, y + 46),
        "Raw user plain text is useful context, but not authoritative for G5 because it omitted Volcano Bonds.",
        fill=(255, 218, 135),
        font=normal,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    loaded_sources = {}
    for source_id, meta in SOURCES.items():
        path = meta["path"]
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        loaded_sources[source_id] = {
            **meta,
            "text": text,
            "normalized": normalize(text),
            "exists": path.exists(),
            "charCount": len(text),
        }

    source_rows = []
    target_matrix = []
    for source_id, source in loaded_sources.items():
        checks = []
        missing = []
        for target in TARGETS:
            norm_phrase = normalize(target["phrase"])
            present = norm_phrase in source["normalized"]
            if not present:
                missing.append(target["id"])
            checks.append(
                {
                    "targetId": target["id"],
                    "phrase": target["phrase"],
                    "role": target["role"],
                    "present": present,
                    "snippet": snippet(source["normalized"], norm_phrase),
                }
            )
            target_matrix.append(
                {
                    "sourceId": source_id,
                    "targetId": target["id"],
                    "present": present,
                }
            )
        source_rows.append(
            {
                "id": source_id,
                "path": rel(source["path"]),
                "role": source["role"],
                "authoritative": source["authoritative"],
                "exists": source["exists"],
                "charCount": source["charCount"],
                "presentCount": sum(1 for check in checks if check["present"]),
                "missingCount": len(missing),
                "missing": missing,
                "checks": checks,
            }
        )

    correction = load_json(JSON_INPUTS["correction_report"])
    impact = load_json(ROOT / "analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.json")
    active_line = load_json(JSON_INPUTS["active_line_reconciliation"])
    source_packet = load_json(JSON_INPUTS["source_packet"])

    active_corrections = [
        row
        for row in impact.get("rows", [])
        if row.get("affectsActiveCorridor") or row.get("activePhraseHitsFixed")
    ]
    selector_permission = [row for row in impact.get("rows", []) if row.get("addsSelectorPermission")]

    authoritative_sources = [row for row in source_rows if row["authoritative"]]
    authoritative_missing = {
        row["id"]: row["missing"] for row in authoritative_sources if row["missing"]
    }
    raw_missing = next((row["missing"] for row in source_rows if row["id"] == "user_raw_plain"), [])

    authority_lock = {
        "targetTextAuthority": "canonical_plain + docm_text + markdown_transcript",
        "rawPlainUse": "context_only_not_authority_for_G5",
        "annotatedTranscriptUse": "format/highlight witness, not exact-prose authority",
        "reason": "The latest raw plain-text paste omits the G5 `Volcano Bonds` phrase; the annotated transcript inserts notes into prose. Canonical/DOCM/Markdown witnesses preserve the exact active target wording cleanly.",
        "authoritativeMissing": authoritative_missing,
        "rawPlainMissing": raw_missing,
        "activeLineStreams": active_line.get("streams", {}),
        "packetTargetPriority": source_packet.get("targetPriority", {}),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 target text authority lock; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "sources": [
            {k: v for k, v in row.items() if k != "checks"} | {"checks": row["checks"]}
            for row in source_rows
        ],
        "targetMatrix": target_matrix,
        "correctionSummary": {
            "manualCorrectionCount": len(correction.get("manualCorrections", [])),
            "activeCorridorCorrectionCount": len(active_corrections),
            "selectorPermissionCorrectionCount": len(selector_permission),
            "activeCorridorCorrections": [
                {
                    "index": row.get("index"),
                    "raw": row.get("raw"),
                    "fixed": row.get("fixed"),
                    "activePhraseHitsFixed": row.get("activePhraseHitsFixed"),
                    "addsSelectorPermission": row.get("addsSelectorPermission"),
                }
                for row in active_corrections
            ],
        },
        "authorityLock": authority_lock,
        "sheet": rel(SHEET),
        "decision": "page76_target_text_authority_locked_to_canonical_docm_markdown_annotated",
        "nextMove": "Use canonical/DOCM/Markdown witnesses for page-76 target wording; keep annotated text as a format witness and raw plain text as context only. Continue requiring new source/clue R1-R5 before extraction.",
    }
    build_sheet(source_rows, result["correctionSummary"])
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Target Text Authority Lock",
        "",
        "Scope: verify the target phrases used by the source-acquisition packet across corrected canonical text, DOCM text, raw user plain text, Markdown transcript, and annotated transcript. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Source Phrase Coverage",
        "",
        "| source | authoritative | present | missing | note |",
        "|---|---:|---:|---:|---|",
    ]
    for row in source_rows:
        note = ", ".join(row["missing"]) if row["missing"] else "all target phrases present"
        lines.append(
            f"| `{row['id']}` | `{row['authoritative']}` | `{row['presentCount']}` | `{row['missingCount']}` | {note} |"
        )

    lines.extend(["", "## Active Corridor Corrections", ""])
    for row in result["correctionSummary"]["activeCorridorCorrections"]:
        lines.append(
            f"- Correction `{row['index']}`: `{row['raw']}` -> `{row['fixed']}`; active hits `{row['activePhraseHitsFixed']}`; selector permission `{row['addsSelectorPermission']}`"
        )

    lines.extend(
        [
            "",
            "## Authority Lock",
            "",
            f"- Target text authority: `{authority_lock['targetTextAuthority']}`",
            f"- Raw plain text use: `{authority_lock['rawPlainUse']}`",
            f"- Annotated transcript use: `{authority_lock['annotatedTranscriptUse']}`",
            f"- Reason: {authority_lock['reason']}",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("authoritativeMissing:", authoritative_missing)
    print("rawPlainMissing:", raw_missing)


if __name__ == "__main__":
    main()
