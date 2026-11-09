#!/usr/bin/env python3
"""Reconcile C9 active-target format witnesses.

The C9/YK benchmark relies on O4/B4/G5/O5 being visually highlighted and
Typeka/bold in the source authorities. Recent line-level checks showed that
the derived bold-letter stream only preserves O4/O5 and reads G5's line-level
bold letters as IMF. This bounded pass reconciles the main witnesses so the
investigation does not mix DOCM/high-res/crop authority with Markdown markup,
annotated notes, or line-level helper streams.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FORMAT_LOCK_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
CROP_COMPLETION_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
LINE_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
C9_DENSITY_JSON = ROOT / "analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density.json"
ANNOTATED_TXT = ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt"
MARKDOWN_TXT = ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md"
CORRECTION_MD = ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.md"
OUT = ROOT / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_active_format_witness_reconciliation.json"
OUT_MD = OUT / "c9_active_format_witness_reconciliation.md"
SHEET = OUT / "c9_active_format_witness_reconciliation_sheet.jpg"


TARGETS = [
    {"id": "buying_dip", "shortId": "O4", "phrase": "buying the dip", "expectedBold": "buyingthedip"},
    {"id": "one_billion", "shortId": "B4", "phrase": "$1 billion", "expectedBold": "$1billion"},
    {"id": "volcano_bonds", "shortId": "G5", "phrase": "Volcano Bonds", "expectedBold": "VolcanoBonds"},
    {"id": "shitcoiner_heart", "shortId": "O5", "phrase": "shitcoiner at heart", "expectedBold": "shitcoineratheart"},
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def compact(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9$]+", "", text).lower()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def markdown_bold_contains(markdown: str, phrase: str) -> bool:
    phrase_compact = compact(phrase)
    for span in re.findall(r"\*\*(.*?)\*\*", markdown, flags=re.S):
        if phrase_compact and phrase_compact in compact(span):
            return True
    return False


def markdown_plain_contains(markdown: str, phrase: str) -> bool:
    return compact(phrase) in compact(markdown)


def annotated_claim_window(text: str, phrase: str) -> str:
    idx = compact(text).find(compact(phrase))
    if idx < 0:
        # Fall back to normal text find for phrases containing punctuation.
        normal = normalize(text)
        nidx = normal.find(normalize(phrase))
        if nidx < 0:
            return ""
        return normal[max(0, nidx - 180) : nidx + len(phrase) + 260]
    # Compact indexes are not source offsets; use plain phrase if possible.
    plain_idx = normalize(text).find(normalize(phrase))
    if plain_idx >= 0:
        normal = normalize(text)
        return normal[max(0, plain_idx - 180) : plain_idx + len(phrase) + 260]
    return ""


def annotated_bold_highlight_claim(text: str, phrase: str) -> dict[str, Any]:
    window = annotated_claim_window(text, phrase)
    return {
        "found": bool(window),
        "boldClaim": "bold" in window,
        "highlightClaim": "highlight" in window or "highlighted" in window,
        "orangeClaim": "orange" in window,
        "greyClaim": "grey" in window or "gray" in window,
        "window": window[:500],
    }


def correction_mentions(report: str, phrase: str) -> bool:
    return compact(phrase) in compact(report)


def line_by_target(line_data: dict[str, Any], format_lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_line = {int(row["lineIndex"]): row for row in line_data["records"]}
    out = {}
    for target in format_lock["activeTargets"]:
        out[target["id"]] = by_line.get(int(target["pageLine"]), {})
    return out


def make_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    format_lock = load_json(FORMAT_LOCK_JSON)
    crop_completion = load_json(CROP_COMPLETION_JSON)
    line_data = load_json(LINE_JSON)
    c9_density = load_json(C9_DENSITY_JSON)
    annotated = ANNOTATED_TXT.read_text(encoding="utf-8", errors="ignore")
    markdown = MARKDOWN_TXT.read_text(encoding="utf-8", errors="ignore")
    correction = CORRECTION_MD.read_text(encoding="utf-8", errors="ignore")

    format_by_id = {row["id"]: row for row in format_lock["activeTargets"]}
    crop_by_id = {row["id"]: row for row in crop_completion["targets"]}
    line_for_target = line_by_target(line_data, format_lock)
    c9_matches = {
        row["targetId"]: row
        for row in c9_density.get("summary", {}).get("activeExactBoldTargetMatches", [])
    }
    c9_mismatches = {
        row["targetId"]: row
        for row in c9_density.get("summary", {}).get("activeBoldTargetMismatches", [])
    }

    rows = []
    for target in TARGETS:
        fid = target["id"]
        fmt = format_by_id[fid]
        crop = crop_by_id.get(fid, {})
        line = line_for_target.get(fid, {})
        annotated_claim = annotated_bold_highlight_claim(annotated, target["phrase"])
        md_bold = markdown_bold_contains(markdown, target["phrase"])
        md_plain = markdown_plain_contains(markdown, target["phrase"])
        corr = correction_mentions(correction, target["phrase"])
        line_bold = line.get("boldLetters", "")
        line_exact = target["expectedBold"].lower() in compact(line_bold)
        authority_pass = (
            fmt.get("docmBoldFraction") == 1.0
            and bool(fmt.get("visualExactMatch"))
            and crop.get("phrase") == fmt.get("label")
        )
        rows.append(
            {
                "targetId": fid,
                "shortId": target["shortId"],
                "phrase": target["phrase"],
                "pageLine": fmt.get("pageLine"),
                "corridorIndex": fmt.get("corridorIndex"),
                "visualState": fmt.get("visualState"),
                "docmBoldFraction": fmt.get("docmBoldFraction"),
                "docmHighlightSummary": fmt.get("docmHighlightSummary"),
                "visualExactMatch": fmt.get("visualExactMatch"),
                "cropCompletionPhrase": crop.get("phrase"),
                "cropCompletionBox": crop.get("box"),
                "formatAuthorityPass": authority_pass,
                "lineLevelBoldLetters": line_bold,
                "lineLevelExpectedBold": target["expectedBold"],
                "lineLevelExactBoldMatch": line_exact,
                "c9DensityExactMatch": fid in c9_matches,
                "c9DensityMismatch": c9_mismatches.get(fid),
                "markdownPlainContains": md_plain,
                "markdownBoldContainsPhrase": md_bold,
                "annotatedFound": annotated_claim["found"],
                "annotatedBoldClaim": annotated_claim["boldClaim"],
                "annotatedHighlightClaim": annotated_claim["highlightClaim"],
                "annotatedOrangeClaim": annotated_claim["orangeClaim"],
                "annotatedGreyClaim": annotated_claim["greyClaim"],
                "correctionReportMentions": corr,
                "witnessConflict": authority_pass and not line_exact,
                "authorityUse": "format authority" if authority_pass else "context only",
            }
        )

    summary = {
        "formatAuthorityPassCount": sum(1 for row in rows if row["formatAuthorityPass"]),
        "lineLevelExactBoldMatchCount": sum(1 for row in rows if row["lineLevelExactBoldMatch"]),
        "markdownBoldContainsPhraseCount": sum(1 for row in rows if row["markdownBoldContainsPhrase"]),
        "annotatedBoldHighlightClaimCount": sum(1 for row in rows if row["annotatedBoldClaim"] and row["annotatedHighlightClaim"]),
        "witnessConflictCount": sum(1 for row in rows if row["witnessConflict"]),
        "correctionReportMentionCount": sum(1 for row in rows if row["correctionReportMentions"]),
        "selectorUnlocked": False,
    }
    return rows, summary


def draw_sheet(result: dict[str, Any]) -> None:
    margin = 28
    row_h = 54
    header_h = 128
    footer_h = 164
    sheet_w = 1340
    sheet_h = header_h + row_h * len(result["targetRows"]) + footer_h
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "C9 Active Format Witness Reconciliation", fill=(240, 244, 248), font=title)
    draw.text((margin, 58), "Separates DOCM/high-res/crop authority from line-level bold, Markdown markup, annotated notes, and correction witnesses.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 84), "Green means source-comparison authority; yellow means witness/context only.", fill=(178, 188, 199), font=small)

    y = header_h
    cols = [margin, 88, 254, 388, 530, 692, 846, 1006, 1160]
    headers = ["id", "phrase", "docm/high-res", "line bold", "markdown", "annotated", "correction", "conflict", "use"]
    for x, h in zip(cols, headers):
        draw.text((x, y - 24), h, fill=(178, 188, 199), font=small)
    for row in result["targetRows"]:
        bg = (16, 21, 29) if row["formatAuthorityPass"] else (28, 18, 18)
        draw.rectangle([margin - 6, y - 6, sheet_w - margin + 4, y + row_h - 10], fill=bg)
        color = "#ff9b2e" if row["visualState"] == "Y" else "#aab4c2"
        draw.text((cols[0], y), row["shortId"], fill=color, font=normal)
        draw.text((cols[1], y), row["phrase"][:22], fill="#e8eef5", font=normal)
        draw.text((cols[2], y), f"bold {row['docmBoldFraction']} / {row['docmHighlightSummary']}", fill="#72f1b8", font=mono)
        line = row["lineLevelBoldLetters"] or "-"
        line_color = "#72f1b8" if row["lineLevelExactBoldMatch"] else "#ffd166"
        draw.text((cols[3], y), line[:18], fill=line_color, font=mono)
        draw.text((cols[4], y), "bold" if row["markdownBoldContainsPhrase"] else ("plain" if row["markdownPlainContains"] else "-"), fill="#ffd166", font=mono)
        ann = "bold+hl" if row["annotatedBoldClaim"] and row["annotatedHighlightClaim"] else ("seen" if row["annotatedFound"] else "-")
        draw.text((cols[5], y), ann, fill="#ffd166", font=mono)
        draw.text((cols[6], y), "mentions" if row["correctionReportMentions"] else "-", fill="#c6d1df", font=mono)
        draw.text((cols[7], y), "yes" if row["witnessConflict"] else "no", fill="#ff8fa3" if row["witnessConflict"] else "#72f1b8", font=mono)
        draw.text((cols[8], y), row["authorityUse"], fill="#72f1b8", font=mono)
        y += row_h

    y += 16
    notes = [
        f"Format authority pass: {result['summary']['formatAuthorityPassCount']}/4.",
        f"Line-level exact bold matches: {result['summary']['lineLevelExactBoldMatchCount']}/4.",
        f"Markdown bold contains phrase: {result['summary']['markdownBoldContainsPhraseCount']}/4.",
        f"Annotated bold+highlight claims: {result['summary']['annotatedBoldHighlightClaimCount']}/4.",
        f"Witness conflicts: {result['summary']['witnessConflictCount']}/4. Result: authority is locked for source comparison only, not R3 extraction.",
    ]
    for note in notes:
        draw.text((margin, y), note, fill=(255, 219, 137), font=normal)
        y += 24
    sheet.save(SHEET, quality=94)


def main() -> None:
    rows, summary = make_rows()
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 active target format witness reconciliation; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "formatAuthorityLock": rel(FORMAT_LOCK_JSON),
            "activeCropCompletion": rel(CROP_COMPLETION_JSON),
            "page76LineLevelCorridor": rel(LINE_JSON),
            "c9BoldHighlightFormatDensity": rel(C9_DENSITY_JSON),
            "userAnnotatedTranscript": rel(ANNOTATED_TXT),
            "userMarkdownTranscript": rel(MARKDOWN_TXT),
            "plainArticleCorrectionReport": rel(CORRECTION_MD),
        },
        "targetRows": rows,
        "summary": summary,
        "assessment": [
            "DOCM/high-res/crop-pack authority agrees on all four active targets: each is Typeka, bold, highlighted, and visually matched.",
            "Line-level bold-letter helper data is not equivalent to that authority: it matches only O4/O5, omits B4, and reads G5 line-level bold letters as IMF.",
            "Markdown bold is transcript markup and matches only O4/O5 in the active quartet; it does not mark B4/G5 as bold target phrases.",
            "The annotated transcript claims all four active phrases are bold/highlighted, but it is a format witness, not exact-prose or selector authority.",
            "The correction report reinforces text authority for O4 punctuation and G5 Volcano Bonds omission, not a format-unit extraction rule.",
        ],
        "decision": {
            "c9ActiveFormatWitnessReconciliation": "authority_locked_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Use DOCM/high-res/crop-pack as active format authority for source comparison only. Do not use line-level bold, Markdown bold, annotated notes, or correction mentions as extraction permission without new R3 unit/order wording.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Active Format Witness Reconciliation",
        "",
        "Scope: reconcile DOCM/high-res/crop authority with line-level bold letters, Markdown markup, annotated transcript notes, and correction markup for O4/B4/G5/O5. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Format authority pass count: `{summary['formatAuthorityPassCount']}/4`.",
        f"- Line-level exact bold matches: `{summary['lineLevelExactBoldMatchCount']}/4`.",
        f"- Markdown bold contains active phrase: `{summary['markdownBoldContainsPhraseCount']}/4`.",
        f"- Annotated bold+highlight claims: `{summary['annotatedBoldHighlightClaimCount']}/4`.",
        f"- Witness conflicts: `{summary['witnessConflictCount']}/4`.",
        f"- Correction report mentions: `{summary['correctionReportMentionCount']}/4`.",
        "",
        "## Witness Grid",
        "",
        "| target | DOCM/high-res/crop authority | line-level bold letters | Markdown phrase bold? | annotated bold+highlight? | correction mentions? | conflict? | authority use |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        authority = f"bold `{row['docmBoldFraction']}`, `{row['docmHighlightSummary']}`, visual `{row['visualExactMatch']}`, crop `{bool(row['cropCompletionPhrase'])}`"
        annotated = row["annotatedBoldClaim"] and row["annotatedHighlightClaim"]
        lines.append(
            f"| `{row['shortId']} {row['phrase']}` | {authority} | `{row['lineLevelBoldLetters'] or '-'}` / expected `{row['lineLevelExpectedBold']}` | `{row['markdownBoldContainsPhrase']}` | `{annotated}` | `{row['correctionReportMentions']}` | `{row['witnessConflict']}` | `{row['authorityUse']}` |"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Use DOCM/high-res/crop-pack witnesses as active format authority for source comparison only.",
            "- Do not use line-level bold letters, Markdown bold, annotated notes, or correction mentions as extraction permission.",
            "- Reopen extraction only if a new source/clue supplies R3 unit/order wording tied to one of these format witnesses.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
