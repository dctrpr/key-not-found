#!/usr/bin/env python3
"""Synthesize comparison/OVERDOSE layout evidence against the R1-R5 gate.

This consolidates existing comparison-article layout, OVERDOSE style,
body-highlighter grammar, comparison source-gate, capsule recurrence,
bitcoin4 witness, and priority-crop comparison reports. It does not create
selectors or key candidates; it asks whether the other Max/OVERDOSE articles
provide a current-scan R3 unit/order rule for Issue 24.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_layout_r3_gate_synthesis.json"
OUT_MD = OUT / "overdose_layout_r3_gate_synthesis.md"
SHEET = OUT / "overdose_layout_r3_gate_synthesis_sheet.jpg"

REPORTS = {
    "comparison_layout_audit": ROOT / "analysis_outputs/comparison_articles/comparison_layout_audit.json",
    "overdose_style_uniqueness": ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.json",
    "body_highlighter_grammar": ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json",
    "comparison_pdf_source_gate": ROOT / "analysis_outputs/source_audit/comparison_pdf_source_gate/comparison_pdf_source_gate.json",
    "capsule_motif_recurrence": ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.json",
    "bitcoin4_geometry_witness": ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json",
    "priority_crops_bitcoin4": ROOT / "analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

SHEET_IMAGES = [
    (
        ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness_contact_sheet.jpg",
        "OVERDOSE style comparison",
        "bitcoin4 is duplicate/witness; independent PDFs remain style controls",
    ),
    (
        ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar_sheet.jpg",
        "Body highlighter grammar",
        "Issue 24 has sustained orange/grey body highlights",
    ),
    (
        ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg",
        "Capsule motif recurrence",
        "five-point sequence recurs in Issue 24/bitcoin4, not independent comparisons",
    ),
    (
        ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness_overlay.jpg",
        "bitcoin4 geometry witness",
        "low-res witness does not repair G5/O5 registration",
    ),
    (
        ROOT / "analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison_sheet.jpg",
        "priority crop comparison",
        "future-source baseline; bitcoin4 stays lower quality",
    ),
]


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


def build_sheet() -> list[dict]:
    panels = []
    panel_w = 620
    label_h = 72
    for path, title, subtitle in SHEET_IMAGES:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((panel_w, 360))
        panel = Image.new("RGB", (panel_w, label_h + img.height), (16, 18, 22))
        draw = ImageDraw.Draw(panel)
        draw.text((0, 0), title, fill=(240, 244, 248), font=font(23))
        draw.text((0, 34), subtitle, fill=(168, 181, 194), font=font(15))
        panel.paste(img, (0, label_h))
        panels.append({"title": title, "path": rel(path), "image": panel})

    if not panels:
        return []

    cols = 2
    margin = 24
    gap = 20
    rows = (len(panels) + cols - 1) // cols
    row_heights = [
        max(p["image"].height for p in panels[r * cols : (r + 1) * cols])
        for r in range(rows)
    ]
    sheet_w = margin * 2 + panel_w * cols + gap
    sheet_h = margin * 2 + 62 + sum(row_heights) + gap * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "Comparison OVERDOSE Layout Gate", fill=(244, 247, 250), font=font(31))
    draw.text(
        (margin, margin + 38),
        "Other Max articles are style controls/provenance, not a current-scan selector.",
        fill=(172, 184, 196),
        font=font(16),
    )
    y = margin + 62
    for r in range(rows):
        x = margin
        for panel in panels[r * cols : (r + 1) * cols]:
            sheet.paste(panel["image"], (x, y))
            x += panel_w + gap
        y += row_heights[r] + gap
    sheet.save(SHEET, quality=94)
    return [{"title": p["title"], "path": p["path"]} for p in panels]


def by_key(rows: list[dict], key: str) -> dict[str, dict]:
    out = {}
    for row in rows:
        value = row.get(key)
        if value:
            out[str(value)] = row
    return out


def page_count(value) -> int | None:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return None


def body_highlight_summary(body: dict) -> dict:
    summaries = by_key(body.get("summaries", []), "source")
    return {
        source: {
            "orangeLineBands": row.get("totalOrangeLineBands"),
            "darkLineBands": row.get("totalDarkLineBands"),
            "sustainedGrammarPages": row.get("sustainedGrammarPages", []),
            "maxGrammarScore": row.get("maxGrammarScore"),
        }
        for source, row in summaries.items()
    }


def style_summary(style: dict) -> dict:
    summaries = by_key(style.get("summaries", []), "slug")
    return {
        slug: {
            "maxHighlightScore": row.get("maxHighlightScore"),
            "highlighterLikePages": row.get("highlighterLikePages", []),
            "orangeBandPages": row.get("orangeBandPages", []),
            "darkOrGreyBandPages": row.get("darkOrGreyBandPages", []),
            "smallCapsuleLikePages": row.get("smallCapsuleLikePages", []),
            "veryColorfulPages": row.get("veryColorfulPages", []),
        }
        for slug, row in summaries.items()
    }


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    layout = data["comparison_layout_audit"]
    style = data["overdose_style_uniqueness"]
    body = data["body_highlighter_grammar"]
    source_gate = data["comparison_pdf_source_gate"]
    capsule = data["capsule_motif_recurrence"]
    bitcoin4 = data["bitcoin4_geometry_witness"]
    priority = data["priority_crops_bitcoin4"]

    layout_sources = [
        {
            "slug": row.get("slug"),
            "label": row.get("label"),
            "path": rel(row.get("path")),
            "pageCount": page_count(row.get("pages")),
        }
        for row in layout.get("sources", [])
    ]
    independent_capsule_matches = capsule.get("comparisonStrongFivePointSequenceMatches", [])
    low_res_capsule_matches = capsule.get("lowResWitnessStrongFivePointSequenceMatches", [])
    promoted_geometry_count = source_gate.get("promotedForExtractionGeometry", 0)
    style_only_count = source_gate.get("styleOnlyComparisonCount", 0)
    g5_record = (
        bitcoin4.get("bitcoin4NaturalGeometry", {})
        .get("records", {})
        .get("G5", {})
    )
    o5_record = (
        bitcoin4.get("bitcoin4NaturalGeometry", {})
        .get("records", {})
        .get("O5", {})
    )

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL/PARTIAL",
            "evidence": "Independent comparison PDFs are different Max/OVERDOSE articles; bitcoin4 is a lower-resolution Issue 24 witness, not a better geometry source.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as provenance",
            "evidence": "Issue 24 body-highlighter grammar and five-capsule sequence remain distinctive against independent controls, supporting the target surface as puzzle-specific.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": "No comparison report or source gate names a word/letter/line/font/edge/fold order; comparison layouts give style/provenance only.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS as audited",
            "evidence": "Comparison PDFs are classified as style-only or low-res witness before use; Issue 24 extraction geometry remains tied to the locked high-res scan and rotate180 source-image discipline.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": f"comparison PDFs promoted for Issue 24 geometry={promoted_geometry_count}; independent strong five-point capsule sequences={len(independent_capsule_matches)}; bitcoin4 keeps O5 partial overlap but leaves G5 gap={g5_record.get('horizontalGapPx')} px.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "comparison/OVERDOSE layout synthesis against source-reopen gate; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "layoutSources": layout_sources,
        "styleSummary": style_summary(style),
        "bodyHighlighterSummary": body_highlight_summary(body),
        "sourceGate": {
            "decision": source_gate.get("decision"),
            "promotedForExtractionGeometry": promoted_geometry_count,
            "styleOnlyComparisonCount": style_only_count,
        },
        "capsuleRecurrence": {
            "assessment": capsule.get("assessment", []),
            "comparisonStrongFivePointSequenceMatches": len(independent_capsule_matches),
            "lowResWitnessStrongFivePointSequenceMatches": len(low_res_capsule_matches),
        },
        "bitcoin4Witness": {
            "decision": bitcoin4.get("decision"),
            "o5OverlapVsTarget": o5_record.get("overlapVsTarget"),
            "g5HorizontalGapPx": g5_record.get("horizontalGapPx"),
            "nextMove": bitcoin4.get("nextMove"),
        },
        "priorityCropsBitcoin4": {
            "conclusion": priority.get("conclusion"),
            "nextMove": priority.get("nextMove"),
        },
        "gateRows": gate_rows,
        "decision": "comparison_overdose_layout_closed_for_current_scan_as_r3_selector",
        "nextMove": "Keep comparison PDFs as style controls, provenance checks, and source-validation witnesses only. Reopen only if a raw clue explicitly references another issue/article/layout motif, or if a materially better source passes R1-R5 and names/supplies the extraction unit/order.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Comparison / OVERDOSE Layout R3 Gate Synthesis",
        "",
        "Scope: consolidate comparison article layout, OVERDOSE style, body-highlight grammar, source-gate, capsule recurrence, bitcoin4 witness, and priority-crop reports against the R1-R5 source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Gate Result",
        "",
        "| gate | status | evidence |",
        "|---|---|---|",
    ]
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")

    lines.extend(
        [
            "",
            "## Consolidated Findings",
            "",
            f"- Comparison PDFs promoted for Issue 24 extraction geometry: `{promoted_geometry_count}`.",
            f"- Independent comparison PDFs kept style-only by the source gate: `{style_only_count}`.",
            f"- Independent strong five-point capsule-sequence recurrences: `{len(independent_capsule_matches)}`.",
            f"- Low-res Issue 24 witness five-point recurrences in bitcoin4: `{len(low_res_capsule_matches)}`.",
            f"- bitcoin4 O5 overlap vs target: `{o5_record.get('overlapVsTarget')}`; G5 horizontal gap: `{g5_record.get('horizontalGapPx')}` px.",
            "- Issue 24 keeps the distinctive sustained body highlighter pattern; independent articles show broad OVERDOSE/graphic style but do not reproduce the same extraction-ready grammar.",
            "- bitcoin4 validates duplicate/source-fidelity behavior only; it does not repair the trusted G5/O5 registration benchmark.",
            "",
            "## Decision",
            "",
            "- Close comparison/OVERDOSE layout mechanics as a current-scan R3 selector.",
            "- Keep the comparison set as style controls, provenance evidence, and future-source validation material.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    if SHEET.exists():
        print(f"wrote {SHEET}")
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
