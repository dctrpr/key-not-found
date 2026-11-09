#!/usr/bin/env python3
"""
Compare the active page-76 target phrases across local text witnesses.

This is a source-authority audit only. It does not generate key material. The
goal is to keep future visual/manual extraction from using stale OCR,
investigator Markdown bold, or raw plain-text omissions around the lower
page-76 corridor.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "active_text_authority_drift"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WITNESSES = {
    "root_full_article_corrected": ROOT / "full_article_corrected.txt",
    "canonical_plain_body": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "canonical_plain_with_signature": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_with_signature.txt",
    "docm_article_with_fonts_text": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_text.txt",
    "viewer_markdown_transcript": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "viewer_annotated_notes": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "viewer_ocr_json": ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json",
}

RUNS_PATH = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
BRIDGE_PATH = ROOT / "analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge.json"
TYPEKA_BRIDGE_PATH = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.json"


TARGETS = [
    {
        "id": "O4_buying_the_dip",
        "label": "O4",
        "phrase": 'buying the dip.',
        "expectedRole": "orange/yellow highlighted active target",
    },
    {
        "id": "B4_one_billion",
        "label": "B4",
        "phrase": "$1 billion",
        "expectedRole": "black/grey highlighted active target",
    },
    {
        "id": "G5_volcano_bonds",
        "label": "G5",
        "phrase": "Volcano Bonds",
        "expectedRole": "black/grey highlighted active target",
    },
    {
        "id": "O5_shitcoiner_heart",
        "label": "O5",
        "phrase": "shitcoiner at heart.",
        "expectedRole": "orange/yellow highlighted active target",
    },
    {
        "id": "context_imf_loan",
        "label": "context",
        "phrase": "IMF loan",
        "expectedRole": "nearby context; not active color target",
    },
    {
        "id": "context_mike_novogratz",
        "label": "context",
        "phrase": "Mike Novogratz",
        "expectedRole": "nearby Typeka Mix context",
    },
    {
        "id": "context_trust_that_guy",
        "label": "context",
        "phrase": "trust that guy.",
        "expectedRole": "nearby Typeka Mix context",
    },
]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def loose(text: str) -> str:
    return re.sub(r"[^a-z0-9$%]+", "", norm(text))


def context_for(text: str, phrase: str, radius: int = 90) -> str | None:
    n_text = norm(text)
    n_phrase = norm(phrase)
    idx = n_text.find(n_phrase)
    if idx < 0:
        l_text = loose(text)
        l_phrase = loose(phrase)
        idx2 = l_text.find(l_phrase)
        if idx2 < 0:
            return None
        return "loose-normalized match; raw context not position-stable"
    start = max(0, idx - radius)
    end = min(len(n_text), idx + len(n_phrase) + radius)
    return n_text[start:end]


def parse_marked_text(input_text: str) -> list[dict[str, object]]:
    """Parse the same small markup grammar used by the 3D viewer."""
    chars: list[dict[str, object]] = []
    bold = False
    highlight: str | None = None
    i = 0
    while i < len(input_text):
        if input_text.startswith("**", i):
            bold = not bold
            i += 2
            continue
        if input_text.startswith("[[", i):
            highlight = None if highlight == "orange" else "orange"
            i += 2
            continue
        if input_text.startswith("]]", i):
            if highlight == "orange":
                highlight = None
            i += 2
            continue
        if input_text.startswith("{{", i) or input_text.startswith("~~", i):
            highlight = None if highlight == "black" else "black"
            i += 2
            continue
        if input_text.startswith("}}", i):
            if highlight == "black":
                highlight = None
            i += 2
            continue
        chars.append({"c": input_text[i], "bold": bold, "highlight": highlight})
        i += 1
    return chars


def find_marked_state(marked: str, phrase: str) -> dict[str, object]:
    parsed = parse_marked_text(marked)
    plain = "".join(item["c"] for item in parsed)
    search_variants = [
        phrase,
        phrase.strip("."),
        phrase.replace('"', "“").replace('"', "”"),
    ]
    idx = -1
    found_variant = None
    plain_lower = plain.lower()
    for variant in search_variants:
        if not variant:
            continue
        idx = plain_lower.find(variant.lower())
        if idx >= 0:
            found_variant = variant
            break
    if idx < 0:
        return {"found": False}

    segment = parsed[idx: idx + len(found_variant or phrase)]
    bold_count = sum(1 for item in segment if item["bold"] and str(item["c"]).strip())
    char_count = sum(1 for item in segment if str(item["c"]).strip())
    highlights = Counter(item["highlight"] or "none" for item in segment if str(item["c"]).strip())
    return {
        "found": True,
        "boldRatio": round(bold_count / char_count, 3) if char_count else 0,
        "highlights": dict(highlights),
    }


def docm_state_for_phrase(runs: list[dict[str, object]], phrase: str) -> dict[str, object]:
    text = "".join(str(run.get("text", "")) for run in runs)
    search_variants = [
        phrase,
        phrase.strip("."),
        phrase.replace('"', "“").replace('"', "”"),
    ]
    idx = -1
    found_variant = None
    text_lower = text.lower()
    for variant in search_variants:
        if not variant:
            continue
        idx = text_lower.find(variant.lower())
        if idx >= 0:
            found_variant = variant
            break
    if idx < 0:
        return {"found": False}

    # Reconstruct per character from original runs. Use raw text offsets because
    # active phrases are stable substrings inside the DOCM text witness.
    chars: list[dict[str, object]] = []
    for run in runs:
        font = run.get("fontAscii") or run.get("fontHAnsi") or ""
        for c in str(run.get("text", "")):
            chars.append(
                {
                    "c": c,
                    "font": font,
                    "bold": bool(run.get("bold")),
                    "highlight": run.get("highlight") or "none",
                    "runIndex": run.get("runIndex"),
                    "paragraphIndex": run.get("paragraphIndex"),
                }
            )

    segment = [item for item in chars[idx: idx + len(found_variant or phrase)] if str(item["c"]).strip()]
    if not segment:
        return {"found": True, "stateUnstable": True}

    fonts = Counter(item["font"] for item in segment)
    highlights = Counter(item["highlight"] for item in segment)
    bold_count = sum(1 for item in segment if item["bold"])
    return {
        "found": True,
        "fontCounts": dict(fonts),
        "highlightCounts": dict(highlights),
        "boldRatio": round(bold_count / len(segment), 3),
        "runIndexes": sorted({item["runIndex"] for item in segment}),
        "paragraphIndexes": sorted({item["paragraphIndex"] for item in segment}),
    }


def viewer_ocr_status(data: dict[str, object], phrase: str) -> dict[str, object]:
    hits = []
    l_phrase = loose(phrase)
    for page in data["pages"]:
        page_no = page["page"]
        page_words = " ".join(word["text"] for word in page.get("words", []))
        if l_phrase and l_phrase in loose(page_words):
            hits.append({"page": page_no, "scope": "page_words", "context": context_for(page_words, phrase, 60)})
        for word in page.get("words", []):
            if loose(phrase) == loose(word.get("text", "")):
                hits.append({"page": page_no, "scope": "word", "word": word.get("text"), "box": word.get("box")})
    return {"found": bool(hits), "hits": hits[:6]}


def main() -> None:
    witness_texts = {}
    for name, path in WITNESSES.items():
        if path.suffix == ".json":
            continue
        witness_texts[name] = path.read_text(errors="replace") if path.exists() else ""

    viewer_data = json.loads(WITNESSES["viewer_ocr_json"].read_text())
    runs = json.loads(RUNS_PATH.read_text())
    bridge = json.loads(BRIDGE_PATH.read_text())
    typeka_bridge = json.loads(TYPEKA_BRIDGE_PATH.read_text())

    rows = []
    for target in TARGETS:
        phrase = target["phrase"]
        witness_hits = {}
        for name, text in witness_texts.items():
            witness_hits[name] = {
                "found": context_for(text, phrase) is not None,
                "context": context_for(text, phrase),
            }
        markdown_state = find_marked_state(witness_texts["viewer_markdown_transcript"], phrase)
        annotated_state = {
            "found": context_for(witness_texts["viewer_annotated_notes"], phrase) is not None,
            "context": context_for(witness_texts["viewer_annotated_notes"], phrase),
        }
        docm_state = docm_state_for_phrase(runs, phrase)
        ocr_state = viewer_ocr_status(viewer_data, phrase)
        rows.append(
            {
                **target,
                "witnessHits": witness_hits,
                "markdownMarkupState": markdown_state,
                "annotatedNotesState": annotated_state,
                "docmState": docm_state,
                "viewerOcrState": ocr_state,
            }
        )

    omissions_or_drifts = []
    for row in rows:
        strong_names = ["root_full_article_corrected", "canonical_plain_body", "docm_article_with_fonts_text"]
        strong_found = [row["witnessHits"][name]["found"] for name in strong_names]
        if not all(strong_found):
            omissions_or_drifts.append(f"{row['id']}: missing from one or more strong witnesses")
        if row["id"] in {"B4_one_billion", "G5_volcano_bonds"}:
            if row["markdownMarkupState"].get("boldRatio", 0) < 0.5:
                omissions_or_drifts.append(f"{row['id']}: Markdown bold misses DOCM-bold/black-highlighted target")
        if row["id"] in {"O5_shitcoiner_heart", "O4_buying_the_dip"}:
            if row["docmState"].get("boldRatio", 0) < 0.5:
                omissions_or_drifts.append(f"{row['id']}: expected DOCM-bold active target not confirmed")
        if not row["viewerOcrState"]["found"] and row["label"] in {"B4", "G5", "O5"}:
            omissions_or_drifts.append(f"{row['id']}: absent from 3D OCR labels; use bridge/crops")

    report = {
        "scope": "active page-76 text authority drift; no key derivation",
        "targets": rows,
        "bridgeRows": bridge.get("rows", []),
        "typekaPanels": typeka_bridge.get("panels", []),
        "omissionsOrDrifts": omissions_or_drifts,
        "assessment": [
            "The corrected/root text, canonical plain body, and DOCM text agree on the active page-76 corridor after the latest plain-text corrections.",
            "The raw/user annotation layers remain useful notes, but they contain known drift such as omitted or typo-prone wording and partial-bold notation.",
            "Markdown bold is not source typography: it misses the DOCM-bold black-highlighted `$1 billion` and `Volcano Bonds` targets.",
            "DOCM states confirm the active visual sequence as yellow/orange target, black target, black target, yellow/orange target; Typeka Mix stays nearby context rather than inside the O4/B4/G5/O5 targets.",
            "3D OCR labels remain unsafe for exact active target wording, especially `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.",
        ],
        "decision": "Use corrected/DOCM/plain text for wording, high-res crop/bridge sheets for geometry, and DOCM Typeka states for typography labels. Do not use Markdown bold or 3D OCR labels as extraction authority.",
        "nextMove": "Only reopen extraction if a source/clue names which of the locked active units to read, or if a new physical/original-layout source changes one of the priority crop/wording baselines.",
    }

    (OUT_DIR / "active_text_authority_drift.json").write_text(json.dumps(report, indent=2))

    lines = [
        "# Active Text Authority Drift",
        "",
        "Scope: compare the active page-76 target phrases across corrected plain text, DOCM text/font runs, Markdown/annotated transcripts, and the 3D OCR labels. No key derivation, hashing, seed phrase, WIF, or address checks were run.",
        "",
        "## Target Summary",
        "",
        "| id | phrase | strong text witnesses | DOCM state | Markdown state | 3D OCR status |",
        "|---|---|---|---|---|---|",
    ]
    strong_names = ["root_full_article_corrected", "canonical_plain_body", "docm_article_with_fonts_text"]
    for row in rows:
        strong = ", ".join(
            f"{name.split('_')[0]}:{'yes' if row['witnessHits'][name]['found'] else 'no'}"
            for name in strong_names
        )
        docm = row["docmState"]
        if docm.get("found"):
            docm_s = f"bold={docm.get('boldRatio')} fonts={docm.get('fontCounts')} hi={docm.get('highlightCounts')}"
        else:
            docm_s = "missing"
        md = row["markdownMarkupState"]
        md_s = f"bold={md.get('boldRatio')} hi={md.get('highlights')}" if md.get("found") else "missing"
        ocr_s = "found" if row["viewerOcrState"]["found"] else "missing"
        lines.append(f"| `{row['id']}` | `{row['phrase']}` | `{strong}` | `{docm_s}` | `{md_s}` | `{ocr_s}` |")

    lines.extend(["", "## Drift / Guardrails", ""])
    lines.extend([f"- {item}" for item in omissions_or_drifts])
    lines.extend(["", "## Assessment", ""])
    lines.extend([f"- {item}" for item in report["assessment"]])
    lines.extend(["", "## Decision", "", f"- {report['decision']}", "", "## Next Move", "", f"- {report['nextMove']}"])

    (OUT_DIR / "active_text_authority_drift.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_DIR / 'active_text_authority_drift.md'}")
    print(f"Wrote {OUT_DIR / 'active_text_authority_drift.json'}")


if __name__ == "__main__":
    main()
