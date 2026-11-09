#!/usr/bin/env python3
"""Consolidate whether BOLD.docm can serve as a source witness.

This is a source/provenance gate for the two Word artifacts the user supplied:
`BOLD.docm` and `Article with Fonts.docm`. It consolidates macro provenance,
active-corridor coverage, and recovered-list status. It does not execute
macros, generate key candidates, hash prose, run BIP39, scan WIF/Base58, OCR
pages, or check addresses.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/bold_docm_source_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "bold_docm_source_gate.json"
OUT_MD = OUT / "bold_docm_source_gate.md"
SHEET = OUT / "bold_docm_source_gate_sheet.jpg"

REPORTS = {
    "macro_audit": ROOT / "analysis_outputs/docm_format_sources/bold_docm_macro_audit.json",
    "bold_vs_article": ROOT / "analysis_outputs/docm_format_sources/bold_vs_article_active_corridor/bold_vs_article_active_corridor.json",
    "target_format_authority": ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
    "typeka_font_gate": ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json",
}


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


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1640, 1160
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "BOLD.docm Source Gate", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 46),
        "BOLD.docm is checked as a generated markup artifact, not as an original page-76 source.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("BOLD active targets", result["summary"]["boldActiveTargetsPresent"]),
        ("Article active targets", result["summary"]["articleActiveTargetsPresent"]),
        ("BOLD has VBA", result["summary"]["boldHasVbaProject"]),
        ("otrobip recovered", result["summary"]["otrobipRecovered"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 370, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += 390

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 104), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Use Article with Fonts.docm as the Word formatting witness; keep BOLD.docm as generated sanity evidence.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "BOLD.docm does not contain O4/B4/G5/O5 and the macro word list is missing, so R3 remains blocked.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 135
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("document", 12), ("macros", 260), ("words", 420), ("active set", 560), ("context hits", 760), ("use", 1070)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["documentRows"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 52), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 16), row["document"], fill=(238, 243, 248), font=small)
        draw.text((margin + 260, y + 16), str(row["hasVbaProject"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 420, y + 16), str(row["wordCount"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 560, y + 16), f"{row['activePresentCount']}/4", fill=(176, 186, 198), font=mono)
        draw.text((margin + 760, y + 16), str(row["contextPresentCount"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1070, y + 16), row["authorityUse"][:42], fill=(176, 186, 198), font=small)
        y += 56

    y += 22
    draw.rectangle((margin, y, sheet_w - margin, y + 185), fill=(18, 22, 28), outline=(48, 58, 70))
    draw.text((margin + 14, y + 14), "Macro Evidence", fill=(238, 243, 248), font=normal)
    macro_lines = [
        f"macro path: {result['macroEvidence']['referencedPath']}",
        f"local matches: {result['macroEvidence']['localOtrobipMatchCount']}",
        f"routine: {result['macroEvidence']['routine']}",
    ]
    ty = y + 52
    for line in macro_lines:
        draw.text((margin + 18, ty), line[:150], fill=(176, 186, 198), font=small)
        ty += 36

    y += 215
    draw.rectangle((margin, y, sheet_w - margin, y + 215), fill=(18, 22, 28), outline=(48, 58, 70))
    draw.text((margin + 14, y + 14), "R1-R5 Result", fill=(238, 243, 248), font=normal)
    ty = y + 52
    for row in result["gateRows"]:
        draw.text((margin + 18, ty), f"{row['gate']}: {row['status']}", fill=(232, 239, 246), font=mono)
        draw.text((margin + 420, ty), row["evidence"][:108], fill=(176, 186, 198), font=small)
        ty += 34

    sheet.save(SHEET, quality=94)


def main() -> None:
    macro = load_json(REPORTS["macro_audit"])
    bold_vs_article = load_json(REPORTS["bold_vs_article"])
    target_format = load_json(REPORTS["target_format_authority"])
    typeka_gate = load_json(REPORTS["typeka_font_gate"])

    docs = bold_vs_article.get("documents", {})
    document_rows = []
    for name, doc in docs.items():
        active_present = doc.get("activePresent", [])
        context_present = doc.get("contextPresent", [])
        authority_use = (
            "trusted formatting witness"
            if name == "Article with Fonts.docm"
            else "generated/annotation sanity witness only"
        )
        document_rows.append(
            {
                "document": name,
                "hasVbaProject": doc.get("hasVbaProject"),
                "hasVbaData": doc.get("hasVbaData"),
                "paragraphCount": doc.get("paragraphCount"),
                "runCount": doc.get("runCount"),
                "wordCount": doc.get("wordCount"),
                "fontRunCounts": doc.get("fontRunCounts"),
                "highlightRunCounts": doc.get("highlightRunCounts"),
                "activePresent": active_present,
                "activePresentCount": len(active_present),
                "contextPresent": context_present,
                "contextPresentCount": len(context_present),
                "instructionTermsInFullText": doc.get("instructionTermsInFullText"),
                "authorityUse": authority_use,
            }
        )

    bold = macro.get("bold", {})
    interesting = bold.get("interestingStrings", [])
    referenced = next((item for item in interesting if "otrobip" in item.lower()), "")
    macro_evidence = {
        "hasVbaProject": bold.get("hasVbaProject"),
        "hasVbaData": bold.get("hasVbaData"),
        "containsHighlightWordsMacro": bold.get("vbaDataContainsHighlightWordsMacro"),
        "referencedPath": referenced,
        "routine": "HighlightWordsFromTextFile" if any("HighlightWordsFromTextFile" in s for s in interesting) else "",
        "localOtrobipMatchCount": len(bold.get("localOtrobipMatches", [])),
        "searchRoots": bold.get("otrobipSearchRoots"),
    }

    bold_row = next((row for row in document_rows if row["document"] == "BOLD.docm"), {})
    article_row = next((row for row in document_rows if row["document"] == "Article with Fonts.docm"), {})
    summary = {
        "boldHasVbaProject": bool(bold_row.get("hasVbaProject")),
        "boldHasVbaData": bool(bold_row.get("hasVbaData")),
        "boldActiveTargetsPresent": f"{bold_row.get('activePresentCount', 0)}/4",
        "articleActiveTargetsPresent": f"{article_row.get('activePresentCount', 0)}/4",
        "otrobipRecovered": macro_evidence["localOtrobipMatchCount"] > 0,
        "boldWordCount": bold_row.get("wordCount"),
        "articleWordCount": article_row.get("wordCount"),
        "targetFormatAuthorityDecision": target_format.get("decision"),
        "typekaGateDecision": typeka_gate.get("decision"),
        "selectorUnlocked": False,
    }

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL for BOLD",
            "evidence": "BOLD.docm has a VBA highlighting workflow and is not an original layout/font source.",
        },
        {
            "gate": "R2 target preservation",
            "status": "FAIL for BOLD",
            "evidence": "BOLD.docm contains 0/4 locked O4/B4/G5/O5 active targets; Article with Fonts contains 4/4.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": "The macro points to a missing word list and provides no page-76 word/letter/line/font order.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS as classified",
            "evidence": "BOLD is kept separate from DOCM/high-res format authority and is not used for geometry.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": "BOLD does not improve active-corridor coverage or source registration.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "BOLD.docm source/provenance gate; no macro execution, extraction, hashing, key derivation, BIP39, WIF, OCR, or address checks",
        "inputs": {name: rel(path) for name, path in REPORTS.items()},
        "summary": summary,
        "documentRows": document_rows,
        "macroEvidence": macro_evidence,
        "gateRows": gate_rows,
        "decision": "bold_docm_generated_artifact_not_source_or_selector",
        "sheet": rel(SHEET),
        "nextMove": "Use BOLD.docm only as generated-artifact sanity evidence unless the referenced `otrobip.txt` or original workflow files are recovered; keep Article with Fonts.docm as the Word formatting witness.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# BOLD.docm Source Gate",
        "",
        "Scope: consolidate whether `BOLD.docm` can serve as a source witness for the active page-76 corridor. No macros were executed, and no extraction, hashing, BIP39, WIF/Base58 scanning, OCR extraction, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- BOLD active targets present: `{summary['boldActiveTargetsPresent']}`.",
        f"- Article with Fonts active targets present: `{summary['articleActiveTargetsPresent']}`.",
        f"- BOLD has VBA project: `{summary['boldHasVbaProject']}`.",
        f"- BOLD has VBA data: `{summary['boldHasVbaData']}`.",
        f"- Referenced `otrobip.txt` recovered locally: `{summary['otrobipRecovered']}`.",
        "",
        "## Document Rows",
        "",
        "| document | VBA | words | active set | context hits | use |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in document_rows:
        lines.append(
            f"| `{row['document']}` | `{row['hasVbaProject']}` | `{row['wordCount']}` | `{row['activePresentCount']}/4` | `{row['contextPresentCount']}` | {row['authorityUse']} |"
        )
    lines.extend(
        [
            "",
            "## Macro Evidence",
            "",
            f"- Referenced path: `{macro_evidence['referencedPath']}`.",
            f"- Local `otrobip` matches recovered: `{macro_evidence['localOtrobipMatchCount']}`.",
            f"- Routine identified: `{macro_evidence['routine']}`.",
            "",
            "## Gate Result",
            "",
            "| gate | status | evidence |",
            "|---|---|---|",
        ]
    )
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- `BOLD.docm` is not an independent source for the active page-76 corridor because it is macro-enabled, references a missing external word list, and omits all four locked O4/B4/G5/O5 targets.",
            "- `Article with Fonts.docm` remains the Word-level formatting witness because it has no embedded VBA project and preserves all four active targets plus surrounding corridor terms.",
            "- The `BOLD.docm` branch should only reopen if `otrobip.txt` or original workflow files are recovered and independently pass the source-reopen gate.",
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
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
