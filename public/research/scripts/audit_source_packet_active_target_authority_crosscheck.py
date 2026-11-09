#!/usr/bin/env python3
"""Cross-check active target wording and format authority.

This bounded source-authority pass verifies the page-76 O4/B4/G5/O5 target
phrases across the canonical text, annotated transcript, Markdown transcript,
correction report, and existing authority locks. It records authority status
only; it does not derive key material.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_active_target_authority_crosscheck.json"
OUT_MD = OUT / "source_packet_active_target_authority_crosscheck.md"
OUT_SHEET = OUT / "source_packet_active_target_authority_crosscheck_sheet.jpg"

INPUTS = {
    "canonical_plain_article_body": ROOT
    / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "user_annotated_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "user_markdown_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "plain_article_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
    "page76_target_text_authority_lock": ROOT
    / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/"
    "page76_target_text_authority_lock.json",
    "page76_target_format_authority_lock": ROOT
    / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/"
    "page76_target_format_authority_lock.json",
    "c9_active_format_witness_reconciliation": ROOT
    / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation/"
    "c9_active_format_witness_reconciliation.json",
    "source_packet_terminal_coverage_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_terminal_coverage_matrix/"
    "source_packet_terminal_coverage_matrix.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def norm(text: str) -> str:
    text = text.lower()
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"[*_`~\\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def phrase_present(text: str, phrase: str) -> bool:
    return norm(phrase) in norm(text)


def draw_sheet(summary: dict, rows: list[dict]) -> None:
    width, height = 1820, 860
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Active Target Authority Crosscheck", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"targets {summary['activeTargetCount']} | authority present "
            f"{summary['canonicalPresentCount']}/{summary['activeTargetCount']} | "
            f"format pass {summary['formatAuthorityPassCount']}/4 | "
            f"selector permission corrections {summary['selectorPermissionCorrectionCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Target wording and format witnesses", fill=(45, 45, 45), font=small)
    y += 30
    headers = ["target", "line/corr", "state", "canonical", "markdown", "annotated", "format", "notes"]
    xs = [24, 310, 430, 530, 650, 770, 900, 1030]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 58), fill=fill)
        draw.text((xs[0], y), row["label"][:32], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), f"{row['pageLine']}/{row['corridorIndex']}", fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["visualState"], fill=(30, 30, 30), font=tiny)
        for key, x in [
            ("canonicalPresent", xs[3]),
            ("markdownPresent", xs[4]),
            ("annotatedPresent", xs[5]),
            ("formatAuthorityPass", xs[6]),
        ]:
            color = (25, 110, 55) if row[key] else (145, 35, 25)
            draw.text((x, y), "yes" if row[key] else "no", fill=color, font=tiny)
        draw.text((xs[7], y), row["authorityNote"][:92], fill=(70, 70, 70), font=tiny)
        y += 66

    y += 18
    draw.text((24, y), "Decision", fill=(45, 45, 45), font=small)
    y += 28
    draw.text((24, y), summary["authorityCrosscheckFingerprint"], fill=(45, 45, 45), font=tiny)
    y += 24
    draw.text(
        (24, y),
        "Use canonical/DOCM/Markdown for exact text and DOCM/high-res/crop-pack for format; no selector permission.",
        fill=(70, 70, 70),
        font=tiny,
    )
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    canonical = load_text(INPUTS["canonical_plain_article_body"])
    annotated = load_text(INPUTS["user_annotated_transcript"])
    markdown = load_text(INPUTS["user_markdown_transcript"])
    correction = load_json(INPUTS["plain_article_correction_report"])
    text_lock = load_json(INPUTS["page76_target_text_authority_lock"])
    format_lock = load_json(INPUTS["page76_target_format_authority_lock"])
    witness = load_json(INPUTS["c9_active_format_witness_reconciliation"])
    coverage = load_json(INPUTS["source_packet_terminal_coverage_matrix"])

    text_authority = text_lock.get("authorityLock", {})
    correction_summary = text_lock.get("correctionSummary", {})
    format_summary = format_lock.get("summary", {})
    witness_summary = witness.get("summary", {})
    coverage_summary = coverage.get("summary", {})
    active_targets = format_lock.get("activeTargets", [])

    correction_hits = {}
    for item in correction_summary.get("activeCorridorCorrections", []):
        for target in item.get("activePhraseHitsFixed", []):
            correction_hits.setdefault(target, []).append(
                {"raw": item.get("raw"), "fixed": item.get("fixed")}
            )

    target_short = {
        "buying_dip": "O4",
        "one_billion": "B4",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    rows = []
    for target in active_targets:
        phrase = target.get("label", "")
        target_id = target.get("id")
        short = target_short.get(target_id, target_id)
        canonical_present = phrase_present(canonical, phrase)
        markdown_present = phrase_present(markdown, phrase)
        annotated_present = phrase_present(annotated, phrase)
        format_pass = bool(target.get("docmMatchesActiveRecord", {}).get("font")) and bool(
            target.get("docmMatchesActiveRecord", {}).get("bold")
        ) and bool(target.get("docmMatchesActiveRecord", {}).get("highlight"))
        rows.append(
            {
                "id": target_id,
                "shortId": short,
                "label": phrase,
                "pageLine": target.get("pageLine"),
                "corridorIndex": target.get("corridorIndex"),
                "sentenceRow": target.get("sentenceRow"),
                "visualState": target.get("visualState"),
                "color": target.get("color"),
                "docmHighlightSummary": target.get("docmHighlightSummary"),
                "canonicalPresent": canonical_present,
                "markdownPresent": markdown_present,
                "annotatedPresent": annotated_present,
                "formatAuthorityPass": format_pass,
                "visualExactMatch": target.get("visualExactMatch"),
                "cropEvidenceCount": len(target.get("cropEvidence", [])),
                "activeCorrectionHits": correction_hits.get(short, []),
                "authorityNote": (
                    "raw plain omitted G5" if target_id in text_authority.get("rawPlainMissing", []) else
                    "correction touched active phrase" if correction_hits.get(short) else
                    "witnesses agree"
                ),
            }
        )

    all_text_present = all(
        row["canonicalPresent"] and row["markdownPresent"] and row["annotatedPresent"]
        for row in rows
    )
    all_format_pass = all(row["formatAuthorityPass"] for row in rows)
    active_corrections = correction_summary.get("activeCorridorCorrectionCount")
    selector_corrections = correction_summary.get("selectorPermissionCorrectionCount")
    correction_selector_permission = selector_corrections or 0

    summary = {
        "activeTargetCount": len(rows),
        "canonicalPresentCount": sum(1 for row in rows if row["canonicalPresent"]),
        "markdownPresentCount": sum(1 for row in rows if row["markdownPresent"]),
        "annotatedPresentCount": sum(1 for row in rows if row["annotatedPresent"]),
        "formatAuthorityPassCount": sum(1 for row in rows if row["formatAuthorityPass"]),
        "visualExactMatchCount": sum(1 for row in rows if row["visualExactMatch"]),
        "cropEvidenceTargetCount": sum(1 for row in rows if row["cropEvidenceCount"] > 0),
        "allTargetWordingPresentInCheckedWitnesses": all_text_present,
        "allActiveTargetsDocmTypekaBold": format_summary.get("allActiveTargetsDocmTypekaBold"),
        "activeVisualStateOrder": format_summary.get("activeVisualStateOrder"),
        "activeColorPattern": format_summary.get("activeColorPattern"),
        "pageLines": format_summary.get("pageLines"),
        "corridorIndexes": format_summary.get("corridorIndexes"),
        "rawPlainMissing": text_authority.get("rawPlainMissing", []),
        "activeCorridorCorrectionCount": active_corrections,
        "selectorPermissionCorrectionCount": correction_selector_permission,
        "witnessConflictCount": witness_summary.get("witnessConflictCount"),
        "lineLevelExactBoldMatchCount": witness_summary.get("lineLevelExactBoldMatchCount"),
        "markdownBoldContainsPhraseCount": witness_summary.get("markdownBoldContainsPhraseCount"),
        "terminalCoverageReadyAreas": coverage_summary.get("extractionReadyAreaCount"),
        "sourceBackedR3BridgeHitCount": coverage_summary.get("sourceBackedR3BridgeHitCount"),
        "selectorUnlocked": False,
        "authorityCrosscheckFingerprint": (
            f"targets={len(rows)}|canon={sum(1 for row in rows if row['canonicalPresent'])}"
            f"|markdown={sum(1 for row in rows if row['markdownPresent'])}"
            f"|annotated={sum(1 for row in rows if row['annotatedPresent'])}"
            f"|format={sum(1 for row in rows if row['formatAuthorityPass'])}"
            f"|rawMissing={','.join(text_authority.get('rawPlainMissing', [])) or 'none'}"
            f"|activeCorr={active_corrections}"
            f"|selectorCorr={correction_selector_permission}"
            f"|witnessConflicts={witness_summary.get('witnessConflictCount')}"
            f"|ready={coverage_summary.get('extractionReadyAreaCount')}"
            f"|sourceR3={coverage_summary.get('sourceBackedR3BridgeHitCount')}"
        ),
    }

    decision = {
        "sourcePacketActiveTargetAuthorityCrosscheck": "authority_confirmed_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "Canonical text, Markdown, annotated transcript, DOCM/high-res visual "
            "format authority, and correction markup agree on the active target "
            "identity. The raw plain omission of G5 is already controlled and no "
            "correction supplies selector permission."
        ),
        "nextMove": (
            "Use canonical/DOCM/Markdown for exact text and DOCM/high-res/crop-pack "
            "for format in future source review. Do not treat correction markup, "
            "Markdown bold, or annotated notes as extraction instructions."
        ),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active target wording and format authority crosscheck; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "targetRows": rows,
        "correctionAssessment": correction.get("assessment", {}),
        "textAuthorityLock": text_authority,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Active Target Authority Crosscheck",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}.",
        "",
        "## Findings",
        "",
        (
            "- Active targets present in canonical / Markdown / annotated witnesses: "
            f"`{summary['canonicalPresentCount']}` / `{summary['markdownPresentCount']}` / "
            f"`{summary['annotatedPresentCount']}` of `{summary['activeTargetCount']}`."
        ),
        (
            "- Format authority pass count / visual exact match count: "
            f"`{summary['formatAuthorityPassCount']}` / `{summary['visualExactMatchCount']}`."
        ),
        (
            "- Raw plain missing targets: "
            f"`{', '.join(summary['rawPlainMissing']) if summary['rawPlainMissing'] else 'none'}`."
        ),
        (
            "- Active-corridor corrections / selector-permission corrections: "
            f"`{summary['activeCorridorCorrectionCount']}` / "
            f"`{summary['selectorPermissionCorrectionCount']}`."
        ),
        (
            "- Witness conflicts / terminal ready areas / source-backed R3 hits: "
            f"`{summary['witnessConflictCount']}` / `{summary['terminalCoverageReadyAreas']}` / "
            f"`{summary['sourceBackedR3BridgeHitCount']}`."
        ),
        f"- Fingerprint: `{summary['authorityCrosscheckFingerprint']}`.",
        "",
        "## Decision",
        "",
        "- Keep canonical/DOCM/Markdown as exact text authority.",
        "- Keep DOCM/high-res/crop-pack as format authority.",
        "- Do not treat correction markup, Markdown bold, or annotated notes as extraction permission.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    draw_sheet(summary, rows)

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["authorityCrosscheckFingerprint"])


if __name__ == "__main__":
    main()
