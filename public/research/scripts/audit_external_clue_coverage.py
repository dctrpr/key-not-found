#!/usr/bin/env python3
"""Map explicit external clue items to tested/active branches.

This is a coverage audit, not a candidate-generation pass. It asks whether the
known external clues still contain an untested human operation, and distinguishes
"selector clues" from "source-fidelity acquisition" gaps.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/external_clues"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "external_clue_coverage_audit.json"
OUT_MD = OUT / "external_clue_coverage_audit.md"


def exists(path: str) -> bool:
    return (ROOT / path).exists()


CLUES = [
    {
        "clue": "Announcement: private Bitcoin key encoded in the Bitcoin Magazine piece",
        "evidence": "analysis_outputs/external_clues/original_clue_provenance.md",
        "testedBy": [
            "source lock, exact transcript, broad key-format tests, dead-branch blacklist",
        ],
        "status": "accounted_for",
        "finding": "Confirms source and target type, but gives no selector beyond the later mirror-writing clue.",
    },
    {
        "clue": "Schott paper title: mirror writing",
        "evidence": "analysis_outputs/external_clues/schott_instruction_distillation.md",
        "testedBy": [
            "hold-to-light overlays",
            "literal string reversal",
            "left/right and bimanual selectors",
            "76/79 registration",
            "page-76 self-mirror",
        ],
        "status": "accounted_for_but_incomplete",
        "finding": "Supports visual/physical mirror and left-right operations. Current tests find regions, not extraction units.",
    },
    {
        "clue": "Schott concepts: left hand, right hemisphere, bimanual movement, corpus callosum",
        "evidence": "analysis_outputs/external_clues/schott_instruction_distillation.md",
        "testedBy": [
            "78/79 two-hand selectors",
            "registered 76/79 line anchor",
            "source-page binary selectors",
        ],
        "status": "accounted_for_but_incomplete",
        "finding": "The concept fits crossing/registration, especially p79 -> p76, but does not name source layer or extraction unit.",
    },
    {
        "clue": "Announcement media sequence: Bukele, El Salvador, IMF, volcano imagery",
        "evidence": "analysis_outputs/external_clues/source_clue_inventory.md",
        "testedBy": [
            "page-76 corridor",
            "page-76 B5/O5 drilldown",
            "dose-number and p80 symptom audits",
        ],
        "status": "strongly_accounted_for",
        "finding": "Repeatedly reinforces page 76 and the Bukele/IMF/volcano/Volcano Bonds corridor.",
    },
    {
        "clue": "Announcement opener spread: OVERDOSE, five capsules, cash",
        "evidence": "analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.md",
        "testedBy": [
            "opener pill/cash inventory",
            "capsule recurrence",
            "ordered capsule projection",
            "spread model reconciliation",
        ],
        "status": "accounted_for_but_incomplete",
        "finding": "Five-capsule/order provenance is real but does not currently map onto page-76 text under the high-res digital scan.",
    },
    {
        "clue": "Canva note: pills don't line up / diff pic?",
        "evidence": "analysis_outputs/external_clues/canva_source_inspection.md",
        "testedBy": [
            "source registration gap",
            "best scan source lock",
            "capsule projection and recurrence",
        ],
        "status": "source_gap_active",
        "finding": "This is not a selector. It points to a possible source/version mismatch that only a different source image, original layout asset, or physical scan can settle.",
    },
    {
        "clue": "Canva note: OCR did not pick up the #0 in browser/PDF viewer",
        "evidence": "analysis_outputs/external_clues/canva_source_inspection.md",
        "testedBy": [
            "OCR is diagnostic only; high-res/manual text is source truth",
        ],
        "status": "source_gap_active",
        "finding": "Treat as OCR/source-fidelity warning. It does not identify which zero or which page without the referenced browser view or higher-res Canva/original visual.",
    },
    {
        "clue": "Canva note: XX / barbed wire / SHIT / FUCK ALL SHITCOINS line up after rotation/mirroring",
        "evidence": "analysis_outputs/external_clues/canva_source_inspection.md",
        "testedBy": [
            "registered Canva anchor alignment",
            "p79 pill / p76 X-dollar-wire system",
            "lower page-76 mark pointers",
        ],
        "status": "accounted_for_as_orientation",
        "finding": "Supports orientation/registration. Existing high-res tests do not make it a precise ordering or letter selector.",
    },
    {
        "clue": "Canva design thumbnail / board",
        "evidence": "analysis_outputs/external_clues/canva_thumbnail_export_audit.md",
        "testedBy": [
            "thumbnail export audit",
            "dead-branch blacklist",
        ],
        "status": "closed_as_geometry_truth",
        "finding": "Current connector only exposes a low-resolution investigator thumbnail, not original geometry truth.",
    },
]


def main() -> None:
    rows = []
    for row in CLUES:
        rows.append({**row, "evidenceExists": exists(row["evidence"])})
    active_source_gaps = [row for row in rows if row["status"] == "source_gap_active"]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "external clue coverage audit; no key derivation",
        "rows": rows,
        "summary": {
            "clueCount": len(rows),
            "activeSourceGaps": len(active_source_gaps),
            "activeSourceGapLabels": [row["clue"] for row in active_source_gaps],
        },
        "assessment": [
            "The known external clues do not contain an untested local selector operation.",
            "Mirror/left-right/bimanual clues have been tested enough to show region/corridor behavior, not final extraction units.",
            "The remaining live clue items are source-fidelity gaps: possible different source image and the unspecified OCR-missed #0.",
            "The next high-value move is source acquisition or manual inspection of the exact browser/Canva/original-layout view, not more transformations of current extracted text.",
        ],
        "nextMove": "Make a zero/#0 visual inventory only if the referenced browser/PDF view or higher-resolution Canva/original asset is available; otherwise prioritize physical/original-source acquisition.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# External Clue Coverage Audit",
        "",
        "Scope: map each known external clue to tested/active branches. This is not a key-generation pass.",
        "",
        "## Coverage",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['clue']}",
                "",
                f"- Evidence: `{row['evidence']}` exists `{row['evidenceExists']}`",
                f"- Status: `{row['status']}`",
                f"- Tested by: `{'; '.join(row['testedBy'])}`",
                f"- Finding: {row['finding']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Assessment",
            "",
            "- The local external-clue set is now mostly covered. It repeatedly points to page 76 and the Bukele/IMF/volcano corridor, but does not supply the missing word/letter extraction unit.",
            "- The only active clue items are source-fidelity gaps: `pills don't line up / diff pic?` and `OCR DIDNT PICK UP THE #0`.",
            "- Those should not be turned into more key candidates. They require a different source image, the exact browser/PDF view, higher-resolution Canva/original layout material, or physical magazine scan evidence.",
            "",
            "## Next Best Move",
            "",
            "- If a new visual source is supplied, first run a zero/#0 and pill-registration inventory against the high-res scan. Without a new source, prioritize physical/original-source acquisition over further local transformations.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
