#!/usr/bin/env python3
"""Audit thumbnail EXIF timestamp order from the current PDF.

This bounded pass follows the only non-structural JPEG metadata exposed by the
current PDF embedded JPEG marker gate: Canon EXIF timestamps on the tiny
`magazine.pdf` page thumbnails. It checks whether timestamp order supplies a
page/fold/OVERDOSE selector, or whether it remains scanner/PDF provenance.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_thumbnail_exif_order_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_thumbnail_exif_order_gate.json"
OUT_MD = OUT / "current_pdf_thumbnail_exif_order_gate.md"

JPEG_MARKER_GATE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_embedded_jpeg_marker_gate/"
    "current_pdf_embedded_jpeg_marker_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TS_RE = re.compile(r"(?P<stamp>\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_exif_timestamp(sample: str) -> datetime | None:
    match = TS_RE.search(sample)
    if not match:
        return None
    return datetime.strptime(match.group("stamp"), "%Y:%m:%d %H:%M:%S")


def inversion_count(values: list[int]) -> int:
    count = 0
    for index, left in enumerate(values):
        for right in values[index + 1 :]:
            if left > right:
                count += 1
    return count


def extract_thumbnail_rows(marker_gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in marker_gate.get("pdfRows", []):
        for image_row in pdf_row.get("imageRows", []):
            if image_row.get("role") != "page_thumbnail":
                continue
            exif_rows = [
                marker_row
                for marker_row in image_row.get("markerRows", [])
                if marker_row.get("role") == "exif"
            ]
            if not exif_rows:
                continue
            sample = " ".join(
                exif_rows[0].get("sample", "").replace("|", " ").split()
            )
            timestamp = parse_exif_timestamp(sample)
            if timestamp is None:
                continue
            strict_hits = sorted(
                {
                    hit
                    for marker_row in exif_rows
                    for hit in marker_row.get("strictHits", [])
                }
            )
            context_hits = sorted(
                {
                    hit
                    for marker_row in exif_rows
                    for hit in marker_row.get("contextHits", [])
                }
            )
            rows.append(
                {
                    "pdf": image_row.get("pdf"),
                    "pdfPage": image_row.get("pdfPage"),
                    "articlePage": int(image_row.get("articlePage")),
                    "xref": image_row.get("xref"),
                    "width": image_row.get("width"),
                    "height": image_row.get("height"),
                    "sample": sample,
                    "timestamp": timestamp.isoformat(sep=" "),
                    "strictHitTerms": strict_hits,
                    "contextHitTerms": context_hits,
                    "sourceInstructionCarrierSegmentCount": image_row.get(
                        "sourceInstructionCarrierSegmentCount", 0
                    ),
                    "provenanceMetadataSegmentCount": image_row.get(
                        "provenanceMetadataSegmentCount", 0
                    ),
                }
            )
    return sorted(rows, key=lambda row: row["articlePage"])


def check_candidate_orders(
    article_order: list[int], timestamp_order: list[int], ranks: dict[int, int]
) -> list[dict[str, Any]]:
    reverse_article_order = list(reversed(article_order))
    active_quartet_order = [76, 78, 79, 80]
    valid_leaf_order = [75, 76]
    checks = [
        {
            "candidate": "article/page/xref order",
            "expected": "-".join(map(str, article_order)),
            "observed": "-".join(map(str, timestamp_order)),
            "match": timestamp_order == article_order,
            "interpretation": "Would support using thumbnail timestamps as current PDF page order.",
        },
        {
            "candidate": "reverse article order",
            "expected": "-".join(map(str, reverse_article_order)),
            "observed": "-".join(map(str, timestamp_order)),
            "match": timestamp_order == reverse_article_order,
            "interpretation": "Would support a simple mirror/reverse page-order selector.",
        },
        {
            "candidate": "known valid leaf 75->76 adjacency",
            "expected": "ranks adjacent",
            "observed": f"rank75={ranks.get(75)} rank76={ranks.get(76)}",
            "match": abs(ranks.get(75, -100) - ranks.get(76, 100)) == 1,
            "interpretation": "Would support timestamp order as a physical leaf traversal clue.",
        },
        {
            "candidate": "active lower-page quartet 76-78-79-80",
            "expected": "-".join(map(str, active_quartet_order)),
            "observed": "-".join(
                str(page) for page in timestamp_order if page in active_quartet_order
            ),
            "match": [
                page for page in timestamp_order if page in active_quartet_order
            ]
            == active_quartet_order,
            "interpretation": "Would support timestamp order as a page-76/OVERDOSE traversal selector.",
        },
        {
            "candidate": "page 76 boundary role",
            "expected": "rank 1 or 8",
            "observed": f"rank76={ranks.get(76)}",
            "match": ranks.get(76) in {1, len(article_order)},
            "interpretation": "Would make the page-76 target a timestamp boundary.",
        },
    ]
    return checks


def main() -> None:
    marker_gate = load_json(JPEG_MARKER_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_summary = trigger_matrix.get("summary", {})

    thumbnail_rows = extract_thumbnail_rows(marker_gate)
    if not thumbnail_rows:
        raise SystemExit(f"No thumbnail EXIF rows found in {rel(JPEG_MARKER_GATE)}")

    article_order = [row["articlePage"] for row in thumbnail_rows]
    timestamp_sorted = sorted(thumbnail_rows, key=lambda row: row["timestamp"])
    timestamp_order = [row["articlePage"] for row in timestamp_sorted]
    ranks = {page: rank for rank, page in enumerate(timestamp_order, start=1)}
    first_stamp = datetime.fromisoformat(timestamp_sorted[0]["timestamp"])

    previous_timestamp: datetime | None = None
    enriched_rows: list[dict[str, Any]] = []
    for row in thumbnail_rows:
        stamp = datetime.fromisoformat(row["timestamp"])
        delta_from_first = int((stamp - first_stamp).total_seconds())
        article_delta: int | None = None
        if previous_timestamp is not None:
            article_delta = int((stamp - previous_timestamp).total_seconds())
        previous_timestamp = stamp
        enriched = {
            **row,
            "timestampRank": ranks[row["articlePage"]],
            "secondsFromFirstTimestamp": delta_from_first,
            "secondsFromPreviousArticlePage": article_delta,
        }
        enriched_rows.append(enriched)

    time_gap_rows: list[dict[str, Any]] = []
    for left, right in zip(timestamp_sorted, timestamp_sorted[1:]):
        left_stamp = datetime.fromisoformat(left["timestamp"])
        right_stamp = datetime.fromisoformat(right["timestamp"])
        time_gap_rows.append(
            {
                "fromArticlePage": left["articlePage"],
                "toArticlePage": right["articlePage"],
                "seconds": int((right_stamp - left_stamp).total_seconds()),
            }
        )

    rank_sequence_by_article = [ranks[page] for page in article_order]
    inversions = inversion_count(rank_sequence_by_article)
    strict_hits = sorted(
        {hit for row in thumbnail_rows for hit in row.get("strictHitTerms", [])}
    )
    context_hits = sorted(
        {hit for row in thumbnail_rows for hit in row.get("contextHitTerms", [])}
    )
    source_instruction_segments = sum(
        int(row.get("sourceInstructionCarrierSegmentCount") or 0)
        for row in thumbnail_rows
    )
    provenance_segments = sum(
        int(row.get("provenanceMetadataSegmentCount") or 0) for row in thumbnail_rows
    )
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    candidate_checks = check_candidate_orders(article_order, timestamp_order, ranks)
    selector_unlocks = sum(1 for row in candidate_checks if row["match"])
    article_monotonic = timestamp_order == article_order

    fingerprint = (
        f"rows={len(thumbnail_rows)}|pages={article_order[0]}-{article_order[-1]}"
        f"|timeOrder={'-'.join(map(str, timestamp_order))}"
        f"|articleMonotonic={int(article_monotonic)}|inversions={inversions}"
        f"|metadata={provenance_segments}|instrCarrier={source_instruction_segments}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors={selector_unlocks}"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_thumbnail_exif_order_no_selector",
        "inputs": {
            "jpegMarkerGate": rel(JPEG_MARKER_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": {
            "exifRowCount": len(thumbnail_rows),
            "articlePageOrder": article_order,
            "timestampOrder": timestamp_order,
            "timestampRankByPage": ranks,
            "articleOrderMonotonic": article_monotonic,
            "articleOrderInversionCount": inversions,
            "candidateOrderCheckCount": len(candidate_checks),
            "candidateOrderMatchCount": selector_unlocks,
            "page76Timestamp": next(
                row["timestamp"] for row in enriched_rows if row["articlePage"] == 76
            ),
            "page76TimestampRank": ranks.get(76),
            "provenanceMetadataSegmentCount": provenance_segments,
            "sourceInstructionCarrierSegmentCount": source_instruction_segments,
            "strictHitCount": len(strict_hits),
            "contextHitCount": len(context_hits),
            "strictHitTerms": strict_hits,
            "contextHitTerms": context_hits,
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": selector_unlocks,
        },
        "thumbnailRows": enriched_rows,
        "timestampGapRows": time_gap_rows,
        "candidateOrderChecks": candidate_checks,
        "fingerprint": fingerprint,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Thumbnail EXIF Order Gate",
        "",
        "Scope: checked whether the Canon EXIF timestamps in the tiny `magazine.pdf` thumbnails form a page/fold/OVERDOSE ordering selector. The EXIF rows come from the current PDF embedded JPEG marker gate, which was built from raw DCT streams in the current PDFs. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Thumbnail EXIF rows: `{len(thumbnail_rows)}`",
        f"- Article/page/xref order: `{'-'.join(map(str, article_order))}`",
        f"- Timestamp order: `{'-'.join(map(str, timestamp_order))}`",
        f"- Article-order monotonic: `{article_monotonic}`",
        f"- Article-order inversions in timestamp rank stream: `{inversions}`",
        f"- Candidate order matches / checks: `{selector_unlocks}` / `{len(candidate_checks)}`",
        f"- Page 76 timestamp / rank: `{result['summary']['page76Timestamp']}` / `{ranks.get(76)}`",
        f"- Provenance metadata / instruction carriers: `{provenance_segments}` / `{source_instruction_segments}`",
        f"- Strict/context hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Thumbnail Timestamp Rows",
        "",
        "| article page | xref | timestamp | rank | seconds from first | previous article delta | sample |",
        "|---:|---:|---|---:|---:|---:|---|",
    ]
    for row in enriched_rows:
        article_delta = (
            ""
            if row["secondsFromPreviousArticlePage"] is None
            else str(row["secondsFromPreviousArticlePage"])
        )
        lines.append(
            f"| {row['articlePage']} | {row['xref']} | `{row['timestamp']}` | {row['timestampRank']} | {row['secondsFromFirstTimestamp']} | {article_delta} | `{row['sample']}` |"
        )

    lines.extend(
        [
            "",
            "## Timestamp-Order Gaps",
            "",
            "| from page | to page | seconds |",
            "|---:|---:|---:|",
        ]
    )
    for gap in time_gap_rows:
        lines.append(
            f"| {gap['fromArticlePage']} | {gap['toArticlePage']} | {gap['seconds']} |"
        )

    lines.extend(
        [
            "",
            "## Candidate Order Checks",
            "",
            "| candidate | expected | observed | match | interpretation |",
            "|---|---|---|---:|---|",
        ]
    )
    for check in candidate_checks:
        lines.append(
            f"| {check['candidate']} | `{check['expected']}` | `{check['observed']}` | `{int(check['match'])}` | {check['interpretation']} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_thumbnail_exif_order_no_selector`",
            "- The timestamp order is `73-75-74-78-79-76-77-80`, not article/page/xref order or a simple reverse order.",
            "- Page 76 is timestamp rank 6, not a first/last boundary, and the known valid 75->76 leaf is not adjacent in timestamp order.",
            "- The EXIF rows contain no strict instruction terms, no puzzle context terms, no source-instruction carrier segment, and no source-backed R3 bridge.",
            "- Treat the Canon timestamps as scanner/PDF provenance, not as a page/fold/OVERDOSE selector.",
            "",
            "## Next Move",
            "",
            "- Continue source/original-layout validation only if a distinct physical scan, source export, or raw clue wording supplies a unit/order/transform.",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Decision: {result['decision']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
