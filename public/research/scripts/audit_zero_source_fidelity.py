#!/usr/bin/env python3
"""Inventory zero-bearing numeric tokens across local text witnesses.

The Canva note says the browser/PDF OCR did not pick up "#0". This script does
not treat zeros as key material. It creates a source-fidelity checklist: where
zeros appear in the canonical article, which local text witnesses disagree, and
which zero-heavy tokens should be checked visually if the referenced browser or
Canva source becomes available.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/zero_source_fidelity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "zero_source_fidelity.json"
OUT_MD = OUT / "zero_source_fidelity.md"

CANONICAL_MODEL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"

TEXT_WITNESSES = {
    "canonical_body": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
    "canonical_with_signature": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_with_signature.txt",
    "user_plain_latest": ROOT / "analysis_outputs/plain_text_transcript/user_plain_article_latest.txt",
    "user_annotated_transcript": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "user_markdown_transcript": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "article_with_fonts_text": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_text.txt",
    "full_article": ROOT / "full_article.txt",
    "full_article_corrected": ROOT / "full_article_corrected.txt",
}

TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])(?:[$#]?\d[\d,]*(?:\.\d+)?%?|post-\d{4}|\d+\s*years?|\d+\s*FL\s*OZ)(?![A-Za-z0-9])", re.I)


def normalize_token(token: str) -> str:
    token = token.strip()
    token = re.sub(r"\s+", " ", token)
    return token


def zero_tokens(text: str) -> list[dict]:
    rows = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines, 1):
        for match in TOKEN_RE.finditer(line):
            token = normalize_token(match.group(0))
            if "0" not in token:
                continue
            rows.append(
                {
                    "line": line_no,
                    "token": token,
                    "digits": re.sub(r"\D", "", token),
                    "zeroCount": token.count("0"),
                    "context": line.strip(),
                }
            )
    return rows


def canonical_page_zero_rows() -> list[dict]:
    data = json.loads(CANONICAL_MODEL.read_text())
    rows = []
    for page in sorted(data["pages"].values(), key=lambda p: p["articlePage"]):
        article_page = page["articlePage"]
        for line in page["lines"]:
            text = line["text"].strip()
            for match in TOKEN_RE.finditer(text):
                token = normalize_token(match.group(0))
                if "0" not in token:
                    continue
                rows.append(
                    {
                        "articlePage": article_page,
                        "lineIndex": line["lineIndex"],
                        "token": token,
                        "digits": re.sub(r"\D", "", token),
                        "zeroCount": token.count("0"),
                        "context": text,
                    }
                )
    return rows


def witness_rows() -> dict[str, list[dict]]:
    result = {}
    for name, path in TEXT_WITNESSES.items():
        if path.exists():
            result[name] = zero_tokens(path.read_text(errors="ignore"))
    return result


def count_by_token(rows: list[dict]) -> Counter:
    return Counter(row["token"] for row in rows)


def compare_to_canonical(witnesses: dict[str, list[dict]], canonical_name: str = "canonical_body") -> list[dict]:
    base = count_by_token(witnesses.get(canonical_name, []))
    rows = []
    for name, values in witnesses.items():
        if name == canonical_name:
            continue
        current = count_by_token(values)
        missing = +(base - current)
        extra = +(current - base)
        rows.append(
            {
                "witness": name,
                "tokenCount": sum(current.values()),
                "missingVsCanonical": dict(missing),
                "extraVsCanonical": dict(extra),
                "hasDiscrepancy": bool(missing or extra),
            }
        )
    return rows


def hotspot_rows(page_rows: list[dict], comparisons: list[dict]) -> list[dict]:
    extras = Counter()
    for comp in comparisons:
        for token, count in comp["extraVsCanonical"].items():
            if "0" in token:
                extras[token] += count
    hotspots = []
    for row in page_rows:
        score = row["zeroCount"]
        if row["token"] in {"100,000", "20,000", "12,000"}:
            score += 4
        if row["token"] in {"2008", "2011", "2017", "1969"}:
            score += 2
        if any(extra.replace(",", "") in row["digits"] or row["digits"] in extra.replace(",", "") for extra in extras):
            score += 3
        if score >= 3:
            hotspots.append({**row, "priorityScore": score})
    hotspots.sort(key=lambda row: (-row["priorityScore"], row["articlePage"], row["lineIndex"], row["token"]))
    return hotspots


def main() -> None:
    page_rows = canonical_page_zero_rows()
    witnesses = witness_rows()
    comparisons = compare_to_canonical(witnesses)
    hotspots = hotspot_rows(page_rows, comparisons)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "zero/#0 source-fidelity inventory; no key derivation",
        "canonicalPageRows": page_rows,
        "witnessCounts": {name: dict(count_by_token(rows)) for name, rows in witnesses.items()},
        "comparisonsVsCanonicalBody": comparisons,
        "visualCheckHotspots": hotspots,
        "assessment": [
            "The local corrected sources agree on most zero-bearing tokens, but the user annotated transcript contains the notable extra form 1000,000.",
            "The highest-priority visual zero token is 100,000 because it is zero-heavy and has a local witness discrepancy.",
            "Other visual zero hotspots are 20,000, 12,000, 2008, 2011, 2017, and the two 10 years references.",
            "None of these zero tokens is a selector by itself; this is a source-fidelity checklist for the missing browser/Canva/original-source view.",
        ],
        "nextMove": "If the exact browser/PDF or higher-resolution Canva/original view is recovered, compare these zero hotspots visually before rerunning any selectors.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Zero / #0 Source-Fidelity Audit",
        "",
        "Scope: inventory zero-bearing numeric tokens across local text witnesses. This does not generate keys or treat zeros as key material.",
        "",
        "## Canonical Page Rows",
        "",
    ]
    for row in page_rows:
        lines.append(
            f"- p{row['articlePage']} L{row['lineIndex']}: `{row['token']}` zeros={row['zeroCount']} context `{row['context']}`"
        )
    lines.extend(["", "## Witness Differences Vs Canonical Body", ""])
    for comp in comparisons:
        status = "DIFF" if comp["hasDiscrepancy"] else "ok"
        lines.append(f"### {comp['witness']} [{status}]")
        lines.append(f"- token count: `{comp['tokenCount']}`")
        lines.append(f"- missing: `{comp['missingVsCanonical']}`")
        lines.append(f"- extra: `{comp['extraVsCanonical']}`")
        lines.append("")
    lines.extend(["## Visual Check Hotspots", ""])
    for row in hotspots:
        lines.append(
            f"- score {row['priorityScore']} p{row['articlePage']} L{row['lineIndex']} `{row['token']}`: {row['context']}"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The strongest local discrepancy is `1000,000` in the user annotated transcript versus canonical `100,000` in the corrected witnesses.",
            "- That makes `100,000` the first zero token to visually inspect if the exact browser/PDF view or higher-resolution Canva/original image is recovered.",
            "- Other high-value zero checks are `20,000`, `12,000`, the years `2008` / `2011` / `2017`, and both `10 years` references.",
            "- This closes local zero inventory as a source-fidelity checklist. It does not supply a selector or justify key generation.",
            "",
            "## Next Best Move",
            "",
            "- With a new visual source: compare these zero hotspots first, then rerun only the affected page-registration or text-mapping pass.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
